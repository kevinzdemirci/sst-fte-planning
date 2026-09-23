"""
Shared definitions for the 2027-28 FTE Planning portal (Google Sheet backend):
the ADP_Positions sheet layout, job title groups, and campus list.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sync_adp_payroll as adp  # noqa: E402

SCHOOL_YEAR = "2027-28"

# One row per ADP worker; the portal's cross-check reads these columns by name
ADP_HEADERS = [
    "worker_id", "given", "middle", "family", "preferred_given", "status", "termination_date",
    "position_id", "job_code", "job_title", "location_code", "location_name", "worker_type",
    "all_position_ids",
]

# Portal job title groups (substitutes 11SUB and part-time aides 11TA are not planned here)
JOB_GROUPS = [
    ("Teachers", lambda c, t: "TEACH" in c or "TEACHER" in t.upper()),
    ("Campus administration", lambda c, t: c in ("23PRI", "23AP", "23OPS")),
    ("Educational aides", lambda c, t: c == "11EA"),
    ("Coordinators", lambda c, t: c.endswith("CRD")),
    ("Office staff", lambda c, t: c in ("23FRONTO", "41ADMAST", "23REGIST", "23SEC", "23ATTEND")),
    ("Support services", lambda c, t: c in ("33MEDAST", "35LUNCH", "23ITSPC", "11LIBR")),
]


def job_group(code, title):
    for name, test in JOB_GROUPS:
        if test(code, title or ""):
            return name
    return "Other"


def adp_row(w):
    a = adp.current_assignment(w)
    return [
        w["worker_id"], w["given"], w["middle"], w["family"], w["preferred_given"], w["status"],
        w["termination_date"], a.get("position_id", ""), a.get("job_code", ""), a.get("job_title", ""),
        a.get("location_code", ""), a.get("location_name", ""), a.get("worker_type", ""),
        ",".join(sorted({x["position_id"] for x in w["assignments"] if x["position_id"]})),
    ]
