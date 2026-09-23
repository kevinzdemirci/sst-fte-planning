#!/usr/bin/env python3
"""
SST Schools - Campus FTE Staffing & Planning Portal
ADP Workforce Now Live API & CSV Cross-Check Automation Engine

Features:
1. Connects to ADP Workforce Now REST API via OAuth 2.0 + Mutual TLS (mTLS).
2. Uses the live /hr/v2/worker-demographics endpoint.
3. Automatically maps ADP campus cost centers/locations to the 21 SST campuses.
4. Flexible name matching ("First Last" vs "Last, First").
5. Produces comprehensive reconciliation reports (JSON & CSV).
"""

import os
import sys
import json
import csv
import ssl
import urllib.request
import urllib.parse
import argparse
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "migrated_fte_data.json")
DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, "adp_reconciliation_report.json")
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Load .env if present
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

ADP_TOKEN_URL = "https://accounts.adp.com/auth/oauth/v2/token"
ADP_DEMOGRAPHICS_URL = "https://api.adp.com/hr/v2/worker-demographics"

def create_ssl_context(cert_file: str, key_file: str) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
    return ctx

def get_adp_access_token(client_id: str, client_secret: str, cert_file: str, key_file: str) -> str:
    """Authenticates with ADP accounts service using Client Credentials and mTLS."""
    ctx = create_ssl_context(cert_file, key_file)
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }).encode("utf-8")

    req = urllib.request.Request(
        ADP_TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    with opener.open(req, timeout=30) as resp:
        token_data = json.loads(resp.read().decode("utf-8"))
        return token_data.get("access_token", "")


def normalize_campus(adp_loc: str, known_campuses: List[str]) -> str:
    if not adp_loc:
        return "Unknown Campus"
    low = adp_loc.lower()
    if "central office" in low or "444444" in low or "district" in low:
        return "Central Office"
    if "regional office" in low or "555555" in low:
        return "Regional Office"

    # Match against known SST campuses
    best_match = None
    max_len = 0
    for c in known_campuses:
        # Extract campus keywords (e.g., "Alamo", "Advancement", "Champions", "Bayshore", "Hill Country")
        cleaned = c.lower().replace("sst", "").replace("college prep", "").replace("elem.", "").replace("elementary", "").strip()
        words = [w for w in cleaned.split() if len(w) > 2]
        if words and all(w in low for w in words):
            if len(c) > max_len:
                max_len = len(c)
                best_match = c

    return best_match or adp_loc.strip()


def fetch_adp_worker_demographics(access_token: str, cert_file: str, key_file: str, known_campuses: List[str]) -> List[Dict[str, Any]]:
    """Pulls employee demographic and work assignment records from ADP API."""
    ctx = create_ssl_context(cert_file, key_file)
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    adp_records = []
    # Production ADP API pagination
    top = 100
    skip = 0
    total_fetched = 0

    while True:
        url = f"{ADP_DEMOGRAPHICS_URL}?$top={top}&$skip={skip}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with opener.open(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"Notice during pagination: {e}")
            break

        workers = data.get("workers", [])
        if not workers:
            break

        for w in workers:
            person = w.get("person", {})
            legal = person.get("legalName", {})
            given = legal.get("givenName", "").strip()
            family = legal.get("familyName1", "").strip()
            formatted = legal.get("formattedName", "").strip()

            if given and family:
                full_name = f"{given} {family}"
            elif formatted:
                full_name = formatted
            else:
                full_name = f"{given} {family}".strip()

            if not full_name:
                continue

            status_obj = w.get("workerStatus", {}).get("statusCode", {})
            status_val = status_obj.get("codeValue") or status_obj.get("shortName") or "Active"

            asgns = w.get("workAssignments", [{}])
            asgn = asgns[0] if asgns else {}

            loc_obj = asgn.get("homeWorkLocation", {}).get("nameCode", {})
            raw_loc = loc_obj.get("longName") or loc_obj.get("shortName") or loc_obj.get("codeValue") or ""
            campus = normalize_campus(raw_loc, known_campuses)

            job_title = asgn.get("jobTitle") or "Staff Member"
            
            # Standard hours
            hours_obj = asgn.get("standardPayPeriodHours", {})
            std_hours = hours_obj.get("hoursQuantity") or 40.0
            try:
                fte = round(float(std_hours) / 40.0, 2)
            except (ValueError, TypeError):
                fte = 1.0

            worker_id = w.get("workerID", {}).get("idValue") or asgn.get("positionID") or ""

            adp_records.append({
                "worker_id": worker_id,
                "name": full_name,
                "raw_location": raw_loc,
                "campus": campus,
                "role": job_title,
                "adp_fte": fte,
                "status": status_val.upper()
            })

        total_fetched += len(workers)
        print(f"Fetched {total_fetched} ADP records so far...")
        if len(workers) < top:
            break
        skip += top

    return adp_records


def parse_adp_csv(file_path: str, known_campuses: List[str]) -> List[Dict[str, Any]]:
    """Parses exported ADP Payroll CSV/Excel files."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    records = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = row.get("First Name", "").strip()
            last = row.get("Last Name", "").strip()
            name = row.get("Employee Name") or f"{first} {last}".strip()
            if not name:
                continue

            loc = row.get("Location") or row.get("Home Work Location") or row.get("Campus") or row.get("Department", "")
            campus = normalize_campus(loc, known_campuses)
            role = row.get("Job Title") or row.get("Position Title") or row.get("Role", "Staff Member")
            hours = row.get("Hours Scheduled") or row.get("Standard Hours") or 40.0
            try:
                fte = round(float(hours) / 40.0, 2)
            except (ValueError, TypeError):
                fte = 1.0

            status = row.get("Status", "Active").upper()
            records.append({
                "worker_id": row.get("Employee Identification Number") or row.get("Employee ID", ""),
                "name": name,
                "campus": campus,
                "role": role,
                "adp_fte": fte,
                "status": status
            })
    return records


def names_match(name1: str, name2: str) -> bool:
    """Flexible name comparison ignoring commas, middle initials, and casing."""
    n1 = name1.lower().replace(",", " ").replace(".", " ").split()
    n2 = name2.lower().replace(",", " ").replace(".", " ").split()
    if not n1 or not n2:
        return False
    # If same words
    s1, s2 = set(n1), set(n2)
    if s1 == s2 or s1.issubset(s2) or s2.issubset(s1):
        return True
    # If first and last match
    if len(n1) >= 2 and len(n2) >= 2:
        if (n1[0] == n2[0] and n1[-1] == n2[-1]) or (n1[0] == n2[-1] and n1[-1] == n2[0]):
            return True
    return False


def cross_check_records(fte_db: Dict[str, Any], adp_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Cross-checks ADP payroll records against the SST FTE Planning database."""
    actual_hires = fte_db.get("actual_hires", [])
    campuses = [c["campus"] for c in fte_db.get("campuses", [])]

    # Index FTE hires
    matched_fte_ids = set()
    reconciled_rows = []

    # 1. Evaluate ADP records
    for adp in adp_records:
        adp_name = adp["name"]
        adp_status = adp.get("status", "ACTIVE")
        
        # Only active workers represent live payroll headcount
        is_adp_active = "ACTIVE" in adp_status or "PAID" in adp_status or "LEAVE" in adp_status

        # Find match in FTE hires
        fte_match = None
        for h in actual_hires:
            h_name = h.get("employee_name") or h.get("name") or ""
            if h_name and h_name.lower() != "vacant" and names_match(adp_name, h_name):
                fte_match = h
                break

        if not fte_match:
            if is_adp_active:
                reconciled_rows.append({
                    "name": adp_name,
                    "worker_id": adp.get("worker_id", ""),
                    "adp_campus": adp["campus"],
                    "fte_campus": "— Not in Plan —",
                    "adp_role": adp["role"],
                    "fte_role": "— Not in Plan —",
                    "adp_fte": adp["adp_fte"],
                    "fte_fte": 0.0,
                    "discrepancy_type": "GHOST_PAYROLL",
                    "status_badge": "Missing in FTE Portal",
                    "severity": "CRITICAL",
                    "action_needed": "Validate if hire was approved by Central Office"
                })
        else:
            matched_fte_ids.add(fte_match.get("hire_id"))
            fte_campus = fte_match.get("campus", "")
            adp_campus = adp["campus"]

            campus_mismatch = (fte_campus.lower().strip() != adp_campus.lower().strip())
            fte_diff = round(adp["adp_fte"] - float(fte_match.get("fte", 1.0)), 2)

            if not is_adp_active:
                reconciled_rows.append({
                    "name": adp_name,
                    "worker_id": adp.get("worker_id", ""),
                    "adp_campus": adp_campus,
                    "fte_campus": fte_campus,
                    "adp_role": adp["role"],
                    "fte_role": fte_match.get("role", ""),
                    "adp_fte": adp["adp_fte"],
                    "fte_fte": float(fte_match.get("fte", 1.0)),
                    "discrepancy_type": "MISSING_IN_ADP",
                    "status_badge": f"Terminated in ADP ({adp_status})",
                    "severity": "CRITICAL",
                    "action_needed": "Update FTE portal to VACANT (Employee terminated)"
                })
            elif campus_mismatch:
                reconciled_rows.append({
                    "name": adp_name,
                    "worker_id": adp.get("worker_id", ""),
                    "adp_campus": adp_campus,
                    "fte_campus": fte_campus,
                    "adp_role": adp["role"],
                    "fte_role": fte_match.get("role", ""),
                    "adp_fte": adp["adp_fte"],
                    "fte_fte": float(fte_match.get("fte", 1.0)),
                    "discrepancy_type": "CAMPUS_MISMATCH",
                    "status_badge": "Campus Mismatch",
                    "severity": "WARNING",
                    "action_needed": "Realign home location in ADP or process campus transfer"
                })
            elif abs(fte_diff) > 0.05:
                reconciled_rows.append({
                    "name": adp_name,
                    "worker_id": adp.get("worker_id", ""),
                    "adp_campus": adp_campus,
                    "fte_campus": fte_campus,
                    "adp_role": adp["role"],
                    "fte_role": fte_match.get("role", ""),
                    "adp_fte": adp["adp_fte"],
                    "fte_fte": float(fte_match.get("fte", 1.0)),
                    "discrepancy_type": "FTE_VARIANCE",
                    "status_badge": f"FTE Diff ({'+' if fte_diff>0 else ''}{fte_diff})",
                    "severity": "INFO",
                    "action_needed": "Verify standard scheduled hours vs approved FTE"
                })
            else:
                reconciled_rows.append({
                    "name": adp_name,
                    "worker_id": adp.get("worker_id", ""),
                    "adp_campus": adp_campus,
                    "fte_campus": fte_campus,
                    "adp_role": adp["role"],
                    "fte_role": fte_match.get("role", ""),
                    "adp_fte": adp["adp_fte"],
                    "fte_fte": float(fte_match.get("fte", 1.0)),
                    "discrepancy_type": "MATCHED",
                    "status_badge": "Reconciled OK",
                    "severity": "SUCCESS",
                    "action_needed": "In alignment"
                })

    # 2. Check for hires recorded in FTE portal that are missing in ADP
    for fte_hire in actual_hires:
        h_id = fte_hire.get("hire_id")
        h_name = fte_hire.get("employee_name") or fte_hire.get("name") or ""
        h_status = str(fte_hire.get("status", "")).upper()

        if h_id not in matched_fte_ids and h_name and h_name.lower() != "vacant" and h_status in ["FILLED", "ACTIVE"]:
            reconciled_rows.append({
                "name": h_name,
                "worker_id": fte_hire.get("position_id", ""),
                "adp_campus": "— Not in ADP —",
                "fte_campus": fte_hire.get("campus", ""),
                "adp_role": "— Not in ADP —",
                "fte_role": fte_hire.get("role", ""),
                "adp_fte": 0.0,
                "fte_fte": float(fte_hire.get("fte", 1.0)),
                "discrepancy_type": "MISSING_IN_ADP",
                "status_badge": "Missing in ADP Payroll",
                "severity": "CRITICAL",
                "action_needed": "Confirm onboarding paperwork or process departure"
            })

    total_eval = len(reconciled_rows)
    matched_cnt = sum(1 for r in reconciled_rows if r["discrepancy_type"] == "MATCHED")
    mismatch_cnt = sum(1 for r in reconciled_rows if r["discrepancy_type"] == "CAMPUS_MISMATCH")
    fte_var_cnt = sum(1 for r in reconciled_rows if r["discrepancy_type"] == "FTE_VARIANCE")
    ghost_cnt = sum(1 for r in reconciled_rows if r["discrepancy_type"] == "GHOST_PAYROLL")
    missing_cnt = sum(1 for r in reconciled_rows if r["discrepancy_type"] == "MISSING_IN_ADP")

    return {
        "summary": {
            "total_evaluated": total_eval,
            "matched_ok": matched_cnt,
            "campus_mismatches": mismatch_cnt,
            "fte_variances": fte_var_cnt,
            "ghost_payroll": ghost_cnt,
            "missing_in_adp": missing_cnt,
            "total_discrepancies": total_eval - matched_cnt
        },
        "records": reconciled_rows
    }


def main():
    parser = argparse.ArgumentParser(description="Live ADP Payroll vs SST Campus FTE Cross-Check Engine")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to database json")
    parser.add_argument("--csv", help="Path to ADP CSV file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, help="Output JSON path")
    args = parser.parse_args()

    print("================================================================")
    print("SST Public Schools — Live ADP Workforce Now Reconciliation Engine")
    print("================================================================")

    with open(args.db, "r") as f:
        fte_db = json.load(f)

    known_campuses = [c["campus"] for c in fte_db.get("campuses", [])]

    if args.csv:
        print(f"Ingesting ADP Payroll CSV: {args.csv}")
        adp_records = parse_adp_csv(args.csv, known_campuses)
    else:
        client_id = os.getenv("ADP_CLIENT_ID")
        client_secret = os.getenv("ADP_CLIENT_SECRET")
        cert_path = os.getenv("ADP_CERT_PATH", "certs/kdemirci_adp_cert.pem")
        key_path = os.getenv("ADP_KEY_PATH", "FTE Planning.md/kdemirciFTEintegration.key")

        print("Authenticating with ADP Workforce Now API via mTLS...")
        token = get_adp_access_token(client_id, client_secret, cert_path, key_path)
        print("Authenticated successfully! Fetching live worker demographics...")
        adp_records = fetch_adp_worker_demographics(token, cert_path, key_path, known_campuses)

    print(f"\nProcessing {len(adp_records)} ADP employee records against 21 SST campuses...")
    results = cross_check_records(fte_db, adp_records)

    summary = results["summary"]
    print("\n--- LIVE ADP RECONCILIATION SUMMARY ---")
    print(f"Total Evaluated:        {summary['total_evaluated']}")
    print(f"Verified & Reconciled:  {summary['matched_ok']} ✅")
    print(f"Campus Mismatches:      {summary['campus_mismatches']} ⚠️")
    print(f"FTE Hours Variances:    {summary['fte_variances']} ⚖️")
    print(f"Ghost Payroll (No FTE): {summary['ghost_payroll']} 🚨")
    print(f"Missing in ADP Payroll: {summary['missing_in_adp']} ❌")
    print(f"Total Discrepancies:    {summary['total_discrepancies']}")

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote full audit results to: {args.output}")

if __name__ == "__main__":
    main()
