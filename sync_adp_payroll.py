#!/usr/bin/env python3
"""
SST Schools - Approved FTE List vs. ADP Position Cross-Check

Compares every person on the 2026-27 Approved FTE Lists against the ADP
Workforce Now Staff Profile > Position tab (Position ID, Job Title, Location)
and flags:
  * Location mismatch   - ADP home work location is a different campus
  * Title mismatch      - ADP job code differs from the approved list job code
  * Not active in ADP   - listed as working but terminated / not found in ADP
  * Not on FTE list     - active in ADP at a campus but not on its approved list
  * Overhire            - ADP headcount for a campus + job title exceeds the
                          number of approved slots for that title

Usage:
  python3 sync_adp_payroll.py              # pull live from ADP API, then reconcile
  python3 sync_adp_payroll.py --cached     # reuse last ADP pull in adp_cache/
Then run build_webapp_ui.py to regenerate the dashboard.
"""

import os
import re
import ssl
import json
import argparse
import datetime
import unicodedata
import urllib.request
import urllib.parse
from collections import defaultdict, Counter

import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FTE_DOC_DIR = os.path.join(BASE_DIR, "FTE Planning.md", "2026-2027 Approved FTE Docs")
ADP_CACHE_PATH = os.path.join(BASE_DIR, "adp_cache", "adp_positions.json")
DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, "adp_reconciliation_report.json")
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

ADP_TOKEN_URL = "https://accounts.adp.com/auth/oauth/v2/token"
ADP_DEMOGRAPHICS_URL = "https://api.adp.com/hr/v2/worker-demographics"

# ADP home work location code -> campus. Order is the display order.
CAMPUSES = [
    # code,   campus name,                        region,           approved FTE list file (None = no list on file)
    ("SACP", "SST San Antonio College Prep",      "San Antonio",    "SST San Antonio CP 2026-27 Approved FTE List.xlsx"),
    ("ALM",  "SST Alamo",                          "San Antonio",    "SST Alamo 2026-27 Approved FTE List.xlsx"),
    ("DIS",  "SST Discovery",                      "San Antonio",    "SST Discovery 2026-27 Approved FTE List.xlsx"),
    ("HC",   "SST Hill Country Elementary",        "San Antonio",    "SST Hill Country Elem. 2026-27 Approved FTE List.xlsx"),
    ("HCCP", "SST Hill Country College Prep",      "San Antonio",    "SST Hill Country CP 2026-27 Approved FTE List.xlsx"),
    ("NW",   "SST Northwest",                      "San Antonio",    "SST Northwest 2026-27 Approved FTE List.xlsx"),
    ("SCH",  "SST Schertz Early Elementary",       "San Antonio",    "SST Schertz Early Elem. 2026-27 Approved FTE List.xlsx"),
    ("SCH2", "SST Schertz Elementary",             "San Antonio",    "SST Schertz Elem. 2026-27 Approved FTE List.xlsx"),
    ("SON",  "SST Sonterra",                       "San Antonio",    "SST Sonterra 2026-27 Approved FTE List.xlsx"),
    ("GAR",  "NF Greg Garcia",                     "San Antonio",    "New Frontiers Greg Garcia 2026-27 Approved FTE List.xlsx"),
    ("MAD",  "NF Frank L. Madla",                  "San Antonio",    "New Frontiers Madla 2026-27 Approved FTE List.xlsx"),
    ("ADV",  "SST Advancement",                    "Houston",        "SST Advancement.xlsx"),
    ("CH E", "SST Champions Elementary",           "Houston",        "SST Champions Elementary 2026-27 Approved FTE List.xlsx"),
    ("CH",   "SST Champions College Prep",         "Houston",        "SST Champions College Prep 2026-27 FTE List.xlsx"),
    ("SPR",  "SST Spring",                         "Houston",        "SST Spring 2026-27 Approved FTE List.xlsx"),
    ("SL",   "SST Sugar Land Elementary",          "Houston",        "SST Sugarland Elem. 2026-27 Approved FTE List.xlsx"),
    ("SLCP", "SST Sugar Land College Prep",        "Houston",        "SST Sugarland CP 2026-27 FTE List.xlsx"),
    ("TW",   "SST The Woodlands",                  "Houston",        "SST The Woodlands 2026-27 Approved FTE List.xlsx"),
    ("WC",   "SST Willow Creek",                   "Houston",        "SST Willow Creek 2026-27 Approved FTE List.xlsx"),
    ("BAY",  "SST Bayshore",                       "Corpus Christi", "SST Bayshore 2026-27 Approved FTE List_.xlsx"),
    ("CCEE", "SST Corpus Christi Early Elementary", "Corpus Christi", "SST CC Early Elem._.xlsx"),
    ("CCE",  "SST Corpus Christi Elementary",      "Corpus Christi", "SST Corpus Christi Elem. 2026-27 Approved FTE List_.xlsx"),
    ("CCH",  "SST Corpus Christi College Prep",    "Corpus Christi", "SST Corpus Christi CP.xlsx"),
]
NON_CAMPUS_LOCATIONS = {"CO": "Central Office", "SA": "Regional Office - San Antonio", "HOU": "Regional Office - Houston"}
CAMPUS_BY_CODE = {c[0]: c[1] for c in CAMPUSES}

# Rows on an approved list that are not approved 2026-27 slots
EXCLUDED_LIST_STATUSES = {"TERM/TRANSFER", "TERM", "TRANSFER"}

# Substitutes and part-time staff are left out of the cross-check on both sides
SUB_PT_JOB_CODES = {"11SUB", "11TA"}
SUB_PT_WORKER_TYPES = {"Part Time", "On-Call Substitute"}


def is_sub_or_pt_adp(assignment):
    return assignment.get("job_code") in SUB_PT_JOB_CODES or assignment.get("worker_type") in SUB_PT_WORKER_TYPES


def is_sub_or_pt_list(job_code, worker_category):
    cat = worker_category.upper()
    return job_code in SUB_PT_JOB_CODES or cat.startswith("P -") or cat.startswith("SUB")


# --------------------------------------------------------------------------- ADP

def create_ssl_context(cert_file, key_file):
    # python.org builds of Python ship without CA certs; fall back to the macOS system bundle
    cafile = "/etc/ssl/cert.pem" if os.path.exists("/etc/ssl/cert.pem") else None
    ctx = ssl.create_default_context(cafile=cafile)
    ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
    return ctx


def get_adp_access_token(client_id, client_secret, ctx):
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")
    req = urllib.request.Request(ADP_TOKEN_URL, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("access_token", "")


def _code(obj, *path):
    for p in path:
        obj = (obj or {}).get(p) if isinstance(obj, dict) else None
    return obj


def slim_worker(w):
    """Keep only identity + Position tab fields (no pay, contact or demographic data)."""
    person = w.get("person", {})
    legal = person.get("legalName", {})
    pref = person.get("preferredName", {})
    assignments = []
    for a in w.get("workAssignments", []) or []:
        assignments.append({
            "primary": bool(a.get("primaryIndicator")),
            "position_id": a.get("positionID") or "",
            "job_code": _code(a, "jobCode", "codeValue") or "",
            "job_title": a.get("jobTitle") or _code(a, "jobCode", "shortName") or "",
            "location_code": _code(a, "homeWorkLocation", "nameCode", "codeValue") or "",
            "location_name": _code(a, "homeWorkLocation", "nameCode", "longName")
                             or _code(a, "homeWorkLocation", "nameCode", "shortName") or "",
            "worker_type": _code(a, "workerTypeCode", "shortName") or "",
            "status": _code(a, "assignmentStatus", "statusCode", "codeValue") or "",
            "status_date": _code(a, "assignmentStatus", "effectiveDate") or "",
            "reports_to": _code((a.get("reportsTo") or [{}])[0], "reportsToWorkerName", "formattedName") or "",
        })
    return {
        "worker_id": _code(w, "workerID", "idValue") or "",
        "given": legal.get("givenName", "") or "",
        "middle": legal.get("middleName", "") or "",
        "family": legal.get("familyName1", "") or "",
        "preferred_given": pref.get("givenName", "") or "",
        "status": _code(w, "workerStatus", "statusCode", "codeValue") or "",
        "termination_date": _code(w, "workerDates", "terminationDate") or "",
        "assignments": assignments,
    }


def fetch_adp_workers():
    cert = os.getenv("ADP_CERT_PATH", "certs/kdemirci_adp_cert.pem")
    key = os.getenv("ADP_KEY_PATH", "FTE Planning.md/kdemirciFTEintegration.key")
    ctx = create_ssl_context(os.path.join(BASE_DIR, cert), os.path.join(BASE_DIR, key))
    token = get_adp_access_token(os.getenv("ADP_CLIENT_ID"), os.getenv("ADP_CLIENT_SECRET"), ctx)
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    workers, skip, top = [], 0, 100
    while True:
        req = urllib.request.Request(f"{ADP_DEMOGRAPHICS_URL}?$top={top}&$skip={skip}", headers=headers)
        with opener.open(req, timeout=60) as resp:
            raw = resp.read()
        # ADP returns 204 / empty body past the last page
        page = json.loads(raw).get("workers", []) if raw.strip() else []
        workers.extend(slim_worker(w) for w in page)
        print(f"  fetched {len(workers)} ADP worker records...")
        if len(page) < top:
            break
        skip += top
    return workers


def current_assignment(worker):
    """The assignment shown on the Position tab: primary active one, else any active, else primary."""
    A = worker["assignments"]
    if not A:
        return {}
    active = [a for a in A if a["status"] in ("A", "L")]
    for pool in (active, A):
        for a in pool:
            if a["primary"]:
                return a
        if pool:
            return pool[0]
    return {}


# --------------------------------------------------------------------------- names

def _tokens(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return [t for t in re.split(r"[^a-z]+", s) if t]


def fte_name_tokens(first, last):
    return set(_tokens(first)), set(_tokens(last))


def adp_name_tokens(w):
    return set(_tokens(w["given"]) + _tokens(w["preferred_given"]) + _tokens(w["middle"])), set(_tokens(w["family"]))


def names_match(fte_first, fte_last, w):
    f1, l1 = fte_first, fte_last
    f2, l2 = adp_name_tokens(w)
    if not l1 or not l2 or not (l1 & l2):
        # tolerate swapped first/last columns
        return bool(f1 & l2) and bool(l1 & f2)
    if not f1 or not f2:
        return False
    if f1 & f2:
        return True
    # short form (e.g. "Chris" vs "Christopher"); needs 2+ extra letters so "Juan" never matches "Juana"
    return any((a.startswith(b) or b.startswith(a)) and abs(len(a) - len(b)) >= 2
               for a in f1 for b in f2 if min(len(a), len(b)) >= 3)


def adp_display_name(w):
    return f"{w['given']} {w['family']}".strip()


# --------------------------------------------------------------------------- FTE lists

JOB_CODE_RE = re.compile(r"^\s*([0-9]{2}[A-Z]+)\s*-\s*(.+?)\s*$")


def infer_job_code(job_title, assignment):
    """Job code as ADP uses it (e.g. 11TEACH). NEW rows often lack it, so infer from text."""
    for txt in (job_title, assignment):
        m = JOB_CODE_RE.match(str(txt or "").upper())
        if m:
            return m.group(1), m.group(2).strip()
    comb = f"{job_title or ''} {assignment or ''}".upper()
    rules = [
        ("IT SPECIALIST", "23ITSPC", "IT SPECIALIST"),
        ("FRONT OFFICE", "23FRONTO", "FRONT OFFICE PERSONNEL"),
        ("SECRETARY", "23FRONTO", "FRONT OFFICE PERSONNEL"),
        ("ASSISTANT PRINCIPAL", "23AP", "ASSISTANT PRINCIPAL"),
        ("EDUCATIONAL AIDE", "11EA", "EDUCATIONAL AIDE"),
    ]
    for kw, code, title in rules:
        if kw in comb:
            return code, title
    return "11TEACH", "TEACHER"   # NEW slots described by grade/subject are teaching slots


def load_fte_lists():
    rows = []
    for code, campus, region, fname in CAMPUSES:
        if not fname:
            continue
        path = os.path.join(FTE_DOC_DIR, fname)
        ws = openpyxl.load_workbook(path, data_only=True, read_only=True).active
        it = ws.iter_rows(values_only=True)
        header = [str(c or "").strip().upper() for c in next(it)]

        def col(r, *names):
            for n in names:
                if n in header and header.index(n) < len(r):
                    return r[header.index(n)]
            return None

        for line_no, r in enumerate(it, start=2):
            if not any(r):
                continue
            first = str(col(r, "FIRST NAME", "LEGAL FIRST NAME") or "").strip()
            last = str(col(r, "LAST NAME", "LEGAL LAST NAME") or "").strip()
            job_title = str(col(r, "JOB TITLE") or "").strip()
            assignment = str(col(r, "ASSIGNMENT") or "").strip()
            list_status = str(col(r, "STATUS") or "").strip().upper()
            pos_status = str(col(r, "POSITION STATUS") or "").strip()
            pid = str(col(r, "POSITION ID") or "").strip()
            if not (first or last or job_title or assignment or pid):
                continue
            # Terminated rows (and template rows copied from other campuses) are not 2026-27 slots
            if pos_status.startswith("T") or list_status in EXCLUDED_LIST_STATUSES:
                continue
            job_code, job_name = infer_job_code(job_title, assignment)
            placeholder = (first.upper() in ("", "NEW", "VACANT") and last.upper() in ("", "NEW", "VACANT", "FTE"))
            rows.append({
                "campus_code": code,
                "campus": campus,
                "file": fname,
                "line": line_no,
                "first": first,
                "last": last,
                "name": "" if placeholder else f"{first} {last}".strip(),
                "job_code": job_code,
                "job_title": job_name,
                "assignment": assignment if assignment.upper() != job_title.upper() else "",
                "list_status": list_status if list_status not in ("NONE", "") else "",
                "notes": str(col(r, "NOTES") or "").strip(),
                "position_id": pid,
                "fte_location": str(col(r, "LOCATION") or "").strip(),
                "sub_pt": is_sub_or_pt_list(job_code, str(col(r, "WORKER CATEGORY") or "").strip()),
            })
    return rows


# --------------------------------------------------------------------------- reconcile

def reconcile(all_fte_rows, workers):
    fte_rows = [r for r in all_fte_rows if not r["sub_pt"]]
    sub_pt_rows = [r for r in all_fte_rows if r["sub_pt"]]
    by_pid = {}
    for w in workers:
        for a in w["assignments"]:
            if a["position_id"]:
                by_pid.setdefault(a["position_id"], w)
    active_workers = [w for w in workers if w["status"] == "Active"]
    # Headcount only counts full-time (non-substitute) staff
    counted_workers = [w for w in active_workers if not is_sub_or_pt_adp(current_assignment(w))]

    def find_by_name(row):
        f, l = fte_name_tokens(row["first"], row["last"])
        cands = [w for w in active_workers if names_match(f, l, w)]
        if len(cands) > 1:
            same = [w for w in cands if current_assignment(w).get("location_code") == row["campus_code"]]
            cands = same or cands
        return cands[0] if len(cands) == 1 else None

    records = []
    matched_worker_ids = set()

    for row in fte_rows:
        rec = {
            "campus": row["campus"],
            "campus_code": row["campus_code"],
            "fte_name": row["name"] or "— Open slot —",
            "fte_title": f"{row['job_code']} - {row['job_title']}",
            "fte_job_code": row["job_code"],
            "assignment": row["assignment"],
            "list_status": row["list_status"],
            "notes": row["notes"],
            "position_id": row["position_id"],
            "source": f"{row['file']} (row {row['line']})",
            "adp_name": "", "adp_position_id": "", "adp_title": "", "adp_job_code": "",
            "adp_location": "", "adp_campus": "", "worker_type": "", "adp_status": "",
            "issues": [], "detail": "",
        }
        is_vacant = row["list_status"] == "VACANT"

        if not row["name"]:
            rec["status"] = "OPEN"
            rec["detail"] = "Approved slot with no one assigned yet"
            records.append(rec)
            continue

        f, l = fte_name_tokens(row["first"], row["last"])
        w = by_pid.get(row["position_id"]) if row["position_id"] else None
        details = []
        name_note = ""
        if w and not names_match(f, l, w):
            if f & adp_name_tokens(w)[0]:
                # same Position ID and first name, different last name: usually a name change
                name_note = f"Name differs in ADP: {adp_display_name(w)}"
            else:
                details.append(f"Position ID {row['position_id']} belongs to {adp_display_name(w)} in ADP")
                w = None
        if w is None or w["status"] != "Active":
            alt = find_by_name(row)
            if alt is not None:
                if w is not None:
                    details.append(f"Old Position ID {row['position_id']} is terminated; person is active under a new position")
                w = alt

        if w is None:
            rec["status"] = "OPEN" if is_vacant else "NOT_IN_ADP"
            rec["issues"] = [] if is_vacant else ["NOT_IN_ADP"]
            rec["detail"] = "; ".join(details) or (
                "Marked VACANT on FTE list" if is_vacant else "No matching Position ID or name in ADP")
            records.append(rec)
            continue

        a = current_assignment(w)
        rec.update({
            "adp_name": adp_display_name(w),
            "adp_position_id": a.get("position_id", ""),
            "adp_title": f"{a.get('job_code', '')} - {a.get('job_title', '')}".strip(" -"),
            "adp_job_code": a.get("job_code", ""),
            "adp_location": a.get("location_name", ""),
            "adp_location_code": a.get("location_code", ""),
            "adp_campus": CAMPUS_BY_CODE.get(a.get("location_code"), NON_CAMPUS_LOCATIONS.get(a.get("location_code"), a.get("location_name", ""))),
            "worker_type": a.get("worker_type", ""),
            "adp_status": w["status"] + (f" ({w['termination_date']})" if w["status"] != "Active" and w["termination_date"] else ""),
        })

        if w["status"] != "Active":
            if is_vacant:
                rec["status"] = "OPEN"
                details.append(f"Marked VACANT; left ADP {w['termination_date'] or ''}".strip())
            else:
                rec["status"] = "NOT_ACTIVE_IN_ADP"
                rec["issues"] = ["NOT_ACTIVE_IN_ADP"]
                details.append(f"{w['status']} in ADP" + (f" since {w['termination_date']}" if w["termination_date"] else "") + " — slot is actually open")
            rec["detail"] = "; ".join(details)
            records.append(rec)
            continue

        issues = []
        if is_sub_or_pt_adp(a):
            # Approved as a full-time slot but ADP has them as part-time / substitute: not in headcount
            rec["adp_status"] = f"Active ({a.get('worker_type') or 'part-time/substitute'})"
            details.append(f"Approved as full-time, but ADP shows {a.get('worker_type') or a.get('job_code')}")
            if a.get("job_code") == row["job_code"]:
                issues.append("TITLE_MISMATCH")
        else:
            rec["_wid"] = w["worker_id"]
            rec["_pid_exact"] = a.get("position_id") == row["position_id"]
        if a.get("location_code") != row["campus_code"]:
            issues.append("LOCATION_MISMATCH")
        if a.get("job_code") and a.get("job_code") != row["job_code"]:
            issues.append("TITLE_MISMATCH")
        if name_note:
            issues.append("NAME_MISMATCH")
            details.append(name_note)
        rec["issues"] = issues
        if is_vacant:
            details.append("Marked VACANT / not returning but still active in ADP")
        if issues:
            rec["status"] = issues[0]
        else:
            rec["status"] = "VACANT_STILL_ACTIVE" if is_vacant else "MATCH"
        rec["detail"] = "; ".join(details)
        records.append(rec)

    # One ADP person fills one approved row. When several rows claim the same person, keep the row that
    # best agrees with ADP (location, title, Position ID) and flag the rest as listed twice.
    claims = defaultdict(list)
    for rec in records:
        if rec.get("_wid"):
            claims[rec["_wid"]].append(rec)
    for wid, recs in claims.items():
        matched_worker_ids.add(wid)
        if len(recs) < 2:
            continue
        recs.sort(key=lambda r: ("LOCATION_MISMATCH" in r["issues"], "TITLE_MISMATCH" in r["issues"], not r["_pid_exact"]))
        keep = recs[0]
        for dup in recs[1:]:
            dup["status"] = "DUPLICATE_ON_LIST"
            dup["issues"] = ["DUPLICATE_ON_LIST"]
            dup["adp_status"] = "Active (counted on another row)"
            dup["detail"] = f"Same ADP person is also on the {keep['campus']} list ({keep['source']}); this row is an extra slot"
    for rec in records:
        rec.pop("_wid", None)
        rec.pop("_pid_exact", None)

    def sub_pt_listing(w):
        """The part-time/substitute list row this person appears on, if any."""
        pids = {a["position_id"] for a in w["assignments"]}
        for r in sub_pt_rows:
            if (r["position_id"] and r["position_id"] in pids) or \
               (r["name"] and names_match(*fte_name_tokens(r["first"], r["last"]), w)):
                return r
        return None

    # Active ADP staff at a campus who are on no approved list
    list_codes = {c[0] for c in CAMPUSES if c[3]}
    for w in counted_workers:
        if w["worker_id"] in matched_worker_ids:
            continue
        a = current_assignment(w)
        code = a.get("location_code")
        if code not in CAMPUS_BY_CODE:
            continue  # central / regional office staff are outside campus FTE lists
        has_list = code in list_codes
        pt_row = sub_pt_listing(w) if has_list else None
        records.append({
            "campus": CAMPUS_BY_CODE[code], "campus_code": code,
            "fte_name": "— Not on FTE list —", "fte_title": "", "fte_job_code": "",
            "assignment": "", "list_status": "", "notes": "", "position_id": "",
            "source": "ADP",
            "adp_name": adp_display_name(w),
            "adp_position_id": a.get("position_id", ""),
            "adp_title": f"{a.get('job_code', '')} - {a.get('job_title', '')}".strip(" -"),
            "adp_job_code": a.get("job_code", ""),
            "adp_location": a.get("location_name", ""),
            "adp_location_code": code,
            "adp_campus": CAMPUS_BY_CODE[code],
            "worker_type": a.get("worker_type", ""),
            "adp_status": "Active",
            "status": "NOT_ON_LIST" if has_list else "NO_FTE_LIST",
            "issues": ["NOT_ON_LIST"] if has_list else ["NO_FTE_LIST"],
            "detail": (f"Full-time in ADP, but only on the {pt_row['campus']} list as part-time/substitute "
                       f"({pt_row['file']} row {pt_row['line']})") if pt_row
                      else "Active in ADP at this campus but not on its approved FTE list" if has_list
                      else "No approved FTE list on file for this campus",
        })

    # Overhire: ADP active headcount vs approved slots, per campus + job code
    approved = Counter((r["campus_code"], r["job_code"]) for r in fte_rows)
    headcount = Counter()
    titles = {}
    names_by_key = defaultdict(list)
    for w in counted_workers:
        a = current_assignment(w)
        if a.get("location_code") in list_codes:
            key = (a["location_code"], a.get("job_code", ""))
            headcount[key] += 1
            titles[key[1]] = a.get("job_title", "")
    for r in fte_rows:
        titles.setdefault(r["job_code"], r["job_title"])
    # Who drives the ADP headcount for a campus + title without an approved slot for it there
    for rec in records:
        if rec["adp_status"] != "Active" or rec["status"] == "NO_FTE_LIST":
            continue
        key = (rec["adp_location_code"], rec["adp_job_code"])
        if rec["status"] == "NOT_ON_LIST":
            names_by_key[key].append(rec["adp_name"])
        elif "LOCATION_MISMATCH" in rec["issues"]:
            names_by_key[key].append(f"{rec['adp_name']} (on {rec['campus']} list)")
        elif "TITLE_MISMATCH" in rec["issues"]:
            names_by_key[key].append(f"{rec['adp_name']} (listed as {rec['fte_job_code']})")

    title_counts = []
    for key in sorted(set(approved) | set(headcount), key=lambda k: ([c[0] for c in CAMPUSES].index(k[0]), k[1])):
        ap, hc = approved.get(key, 0), headcount.get(key, 0)
        title_counts.append({
            "campus": CAMPUS_BY_CODE[key[0]], "campus_code": key[0],
            "job_code": key[1], "job_title": titles.get(key[1], ""),
            "approved": ap, "adp_active": hc, "variance": hc - ap,
            "unapproved": sorted(names_by_key.get(key, [])),
        })

    # Campus rollup
    campuses = []
    for code, campus, region, fname in CAMPUSES:
        recs = [r for r in records if r["campus_code"] == code]
        tc = [t for t in title_counts if t["campus_code"] == code]
        campuses.append({
            "campus": campus, "code": code, "region": region, "has_list": bool(fname),
            "fte_file": fname or "",
            "approved": sum(t["approved"] for t in tc),
            "adp_active": sum(1 for w in counted_workers if current_assignment(w).get("location_code") == code),
            "matched": sum(1 for r in recs if r["status"] in ("MATCH", "VACANT_STILL_ACTIVE")),
            "open": sum(1 for r in recs if r["status"] == "OPEN"),
            "location_mismatch": sum(1 for r in recs if "LOCATION_MISMATCH" in r["issues"]),
            "title_mismatch": sum(1 for r in recs if "TITLE_MISMATCH" in r["issues"]),
            "name_mismatch": sum(1 for r in recs if "NAME_MISMATCH" in r["issues"]),
            "duplicate": sum(1 for r in recs if r["status"] == "DUPLICATE_ON_LIST"),
            "not_active": sum(1 for r in recs if r["status"] in ("NOT_ACTIVE_IN_ADP", "NOT_IN_ADP")),
            "not_on_list": sum(1 for r in recs if r["status"] == "NOT_ON_LIST"),
            "overhire": sum(max(t["variance"], 0) for t in tc),
        })

    non_campus = Counter(current_assignment(w).get("location_code") or "(none)" for w in counted_workers
                         if current_assignment(w).get("location_code") not in CAMPUS_BY_CODE)

    return {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "campuses": campuses,
        "title_counts": title_counts,
        "records": records,
        "non_campus_active": {NON_CAMPUS_LOCATIONS.get(k, k): v for k, v in non_campus.items()},
        "adp_active_total": len(counted_workers),
        "excluded_sub_pt": {"fte_rows": len(sub_pt_rows), "adp_active": len(active_workers) - len(counted_workers)},
    }


def run_crosscheck(cached=False, output=DEFAULT_OUTPUT_PATH):
    """Pull ADP (or reuse the cache), re-read the FTE lists, reconcile, and write the report."""
    if cached:
        with open(ADP_CACHE_PATH) as f:
            cache = json.load(f)
        print(f"Using cached ADP pull from {cache['pulled_at']}")
    else:
        print("Pulling ADP worker positions (live API)...")
        cache = {"pulled_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "workers": fetch_adp_workers()}
        os.makedirs(os.path.dirname(ADP_CACHE_PATH), exist_ok=True)
        with open(ADP_CACHE_PATH, "w") as f:
            json.dump(cache, f)

    fte_rows = load_fte_lists()
    report = reconcile(fte_rows, cache["workers"])
    report["adp_pulled_at"] = cache["pulled_at"]

    with open(output, "w") as f:
        json.dump(report, f, indent=1)
    return report


def main():
    parser = argparse.ArgumentParser(description="Approved FTE Lists vs. ADP Position cross-check")
    parser.add_argument("--cached", action="store_true", help="Reuse the last ADP pull in adp_cache/")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    report = run_crosscheck(args.cached, args.output)

    c = Counter(r["status"] for r in report["records"])
    over = sum(max(t["variance"], 0) for t in report["title_counts"])
    print(f"\nApproved FTE list slots:   {sum(x['approved'] for x in report['campuses'])}")
    print(f"ADP active (all):          {report['adp_active_total']}")
    for k in ("MATCH", "LOCATION_MISMATCH", "TITLE_MISMATCH", "NAME_MISMATCH", "NOT_ACTIVE_IN_ADP", "NOT_IN_ADP",
              "NOT_ON_LIST", "DUPLICATE_ON_LIST", "NO_FTE_LIST", "VACANT_STILL_ACTIVE", "OPEN"):
        print(f"  {k:<22} {c.get(k, 0)}")
    print(f"Overhire headcount (campus x title over approved): {over}")
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
