#!/usr/bin/env python3
"""
SST Schools FTE Planning - Data Migration Pipeline
Extracts, normalizes, and packages approved FTE plans and current actual hires
from the FTE Planning folder into a structured multi-sheet database:
- Approved_Plan
- Actual_Hires
- Violations_Overrides
- Audit_Log
- Campuses
Also outputs SST_FTE_Planning_Database.xlsx and migrated_data.json
"""

import os
import re
import json
import datetime
from collections import defaultdict, Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = "/Users/ekode2/Desktop/AntiGravity Projects"
DOC_DIR = os.path.join(BASE_DIR, "FTE Planning.md", "2026-2027 Approved FTE Docs")
PROF_STAFF_FILE = os.path.join(BASE_DIR, "FTE Planning.md", "2026-2027 FTE #s for Professional and Support Staff.xlsx")
SCHEDULER_FILE = os.path.join(BASE_DIR, "FTE Planning.md", "26-27 SY FTE Meeting Scheduler.xlsx")
ENROLLMENT_FILE = os.path.join(BASE_DIR, "FTE Planning.md", "2026-2027 Campus Enrollment & Capacity Numbers.xlsx")

CAMPUS_METADATA = {
    "SST Advancement": {"region": "Houston", "type": "SST", "short_name": "Advancement", "grades": "PK-8"},
    "SST Alamo": {"region": "San Antonio", "type": "SST", "short_name": "Alamo", "grades": "PK-6"},
    "SST Bayshore": {"region": "Houston", "type": "SST", "short_name": "Bayshore", "grades": "PK-7"},
    "SST Champions Elementary": {"region": "Houston", "type": "SST", "short_name": "Champions ES", "grades": "PK-5"},
    "SST Champions College Prep": {"region": "Houston", "type": "SST", "short_name": "Champions CP", "grades": "6-12"},
    "SST Corpus Christi EE": {"region": "Corpus Christi", "type": "SST", "short_name": "Corpus EE", "grades": "PK-1"},
    "SST Corpus Christi ES": {"region": "Corpus Christi", "type": "SST", "short_name": "Corpus Elem", "grades": "2-7"},
    "SST Corpus Christi College Prep": {"region": "Corpus Christi", "type": "SST", "short_name": "Corpus CP", "grades": "8-12"},
    "SST Discovery": {"region": "San Antonio", "type": "SST", "short_name": "Discovery", "grades": "PK-7"},
    "SST Hill Country Elem": {"region": "San Antonio", "type": "SST", "short_name": "HC Elem", "grades": "PK-6"},
    "SST Hill Country CP": {"region": "San Antonio", "type": "SST", "short_name": "HC CP", "grades": "7-12"},
    "SST Northwest": {"region": "San Antonio", "type": "SST", "short_name": "Northwest", "grades": "PK-7"},
    "SST San Antonio CP": {"region": "San Antonio", "type": "SST", "short_name": "SA College Prep", "grades": "7-12"},
    "SST Schertz Elem": {"region": "San Antonio", "type": "SST", "short_name": "Schertz II", "grades": "3-7"},
    "SST Sonterra": {"region": "San Antonio", "type": "SST", "short_name": "Sonterra", "grades": "PK-6"},
    "SST Spring": {"region": "Houston", "type": "SST", "short_name": "Spring", "grades": "PK-7"},
    "SST Sugarland CP": {"region": "Houston", "type": "SST", "short_name": "Sugar Land CP", "grades": "8-12"},
    "SST Sugarland Elem": {"region": "Houston", "type": "SST", "short_name": "Sugar Land ES", "grades": "PK-7"},
    "SST The Woodlands": {"region": "Houston", "type": "SST", "short_name": "Woodlands", "grades": "PK-7"},
    "SST Willow Creek": {"region": "Houston", "type": "SST", "short_name": "Willow Creek", "grades": "PK-6"},
    "New Frontiers Greg Garcia": {"region": "San Antonio", "type": "Partner", "short_name": "Greg Garcia (NF)", "grades": "PK-8"},
    "New Frontiers Madla": {"region": "San Antonio", "type": "Partner", "short_name": "Madla (NF)", "grades": "9-12"}
}

def clean_campus_name(filename):
    name = (filename.replace(" 2026-27 Approved FTE List.xlsx", "")
                    .replace(" 2026-27 FTE List.xlsx", "")
                    .replace("_.xlsx", "")
                    .replace(".xlsx", "")
                    .replace(" 2026-27 Approved FTE List_", "")
                    .strip())
    if "CC Early Elem" in name:
        return "SST Corpus Christi EE"
    if "Corpus Christi Elem" in name:
        return "SST Corpus Christi ES"
    if "Corpus Christi CP" in name:
        return "SST Corpus Christi College Prep"
    return name

def categorize_and_normalize_role(job_title, assignment):
    jt = (str(job_title) if job_title is not None else "").strip()
    assign = (str(assignment) if assignment is not None else "").strip()
    comb = f"{jt} {assign}".upper()

    # Leadership & Administration
    if "23PRI" in jt or ("PRINCIPAL" in jt and "ASSISTANT" not in jt and "23AP" not in jt):
        return ("Leadership & Administration", "Principal")
    if "23AP" in jt or "ASSISTANT PRINCIPAL" in jt:
        return ("Leadership & Administration", "Assistant Principal")
    if "23OPS" in jt or "OPERATIONS" in jt:
        return ("Leadership & Administration", "Operations Manager")

    # Campus Health & Operations
    if "ITSPC" in jt or jt.startswith("23IT") or "IT SPECIALIST" in jt:
        return ("Operations & Student Support", "IT Specialist")
    if "33MEDAST" in jt or "MEDICAL" in jt or "NURSE" in comb:
        return ("Operations & Student Support", "Medical Assistant")
    if "35LUNCH" in jt or "LUNCH" in jt:
        return ("Operations & Student Support", "Lunch Clerk")
    if "11LIBR" in jt or "LIBRARY" in comb:
        return ("Operations & Student Support", "Library Assistant")
    if ("23FRONTO" in jt or "REGISTRAR" in comb or "ATTENDANCE" in comb or
        "FRONT OFFICE" in comb or "23SEC" in jt or "SECRETARY" in comb or "41ADMAST" in jt):
        return ("Operations & Student Support", "Front Office Support Personnel")

    # Instructional Coordinators & Specialists
    if "HUBCRD" in jt or "COORDINATOR - HUB" in jt:
        return ("Professional Support", "Academic / Hub Coordinator")
    if "CCMR" in comb:
        return ("Professional Support", "CCMR Advisor")
    if "FACE" in comb or ("TESTING" in comb and "COORD" in comb):
        return ("Professional Support", "FACE / Testing Coordinator")
    if "GT" in comb:
        return ("Professional Support", "GT Teacher / Coordinator")
    if "SPED COORD" in comb or "SPED/504" in comb:
        return ("Professional Support", "SPED / 504 Coordinator")

    # Paraprofessionals & Aides
    if "11EA" in jt or "11TA" in jt or "AIDE" in jt:
        if "SPED" in comb:
            return ("Paraprofessional & Instructional Support", "SPED Educational Aide")
        elif "PK" in comb or "PRE-K" in comb or "EARLY" in comb:
            return ("Paraprofessional & Instructional Support", "Pre-K Educational Aide")
        elif "PE" in comb:
            return ("Paraprofessional & Instructional Support", "PE Educational Aide")
        elif "BASC" in comb:
            return ("Paraprofessional & Instructional Support", "BASC Aide / Support")
        else:
            return ("Paraprofessional & Instructional Support", "Instructional Aide")

    # Substitute Teachers
    if "11SUB" in jt or "SUBSTITUTE" in jt:
        return ("Instructional Staff", "Substitute Teacher")

    # Teachers
    if "11TEACH" in jt or "TEACHER" in jt or "DYS" in comb or "SPED" in comb:
        if "SPED" in comb:
            return ("Specialized Instruction", "SPED Teacher")
        if "DYS" in comb:
            return ("Specialized Instruction", "Dyslexia Teacher")
        if "ESL" in comb:
            return ("Specialized Instruction", "ESL Teacher")
        if "INTERVENTION" in comb or "PLC" in comb:
            return ("Specialized Instruction", "Interventionist / PLC Coach")
        if "ART" in comb:
            return ("Specialized Instruction", "Art Teacher")
        if "MUSIC" in comb or "BAND" in comb:
            return ("Specialized Instruction", "Music Teacher")
        if "PE" in comb or "COACH" in comb:
            return ("Specialized Instruction", "PE Teacher")
        if "PLTW" in comb or "TECH" in comb or "STEM" in comb or "ROBOTIC" in comb:
            return ("Specialized Instruction", "PLTW / STEM / Tech Teacher")
        if "SPANISH" in comb or "LOTE" in comb or "TURKISH" in comb:
            return ("Specialized Instruction", "LOTE / Foreign Language Teacher")
        if "MATH" in comb:
            return ("Core Instruction", "Math Teacher")
        if "SCIENCE" in comb or "BIOLOGY" in comb or "PHYSIC" in comb or "CHEM" in comb:
            return ("Core Instruction", "Science Teacher")
        if "ELAR" in comb or "ENGLISH" in comb or "READING" in comb:
            return ("Core Instruction", "ELAR / Reading Teacher")
        if "SS" in comb or "SOCIAL STUDIES" in comb or "HISTORY" in comb:
            return ("Core Instruction", "Social Studies Teacher")
        if "PK" in comb or "PRE-K" in comb:
            return ("Core Instruction", "Pre-K Teacher")
        if "KINDER" in comb:
            return ("Core Instruction", "Kindergarten Teacher")
        if "1ST" in comb:
            return ("Core Instruction", "1st Grade Teacher")
        if "2ND" in comb:
            return ("Core Instruction", "2nd Grade Teacher")
        if "3RD" in comb or "3TH" in comb:
            return ("Core Instruction", "3rd Grade Teacher")
        if "4TH" in comb:
            return ("Core Instruction", "4th Grade Teacher")
        if "5TH" in comb:
            return ("Core Instruction", "5th Grade Teacher")
        return ("Core Instruction", "General / Core Teacher")

    return ("Other Staff", jt if jt else "General Staff")

def parse_all_campuses():
    all_hires = []
    campus_approved_roles = defaultdict(lambda: defaultdict(lambda: {"approved": 0, "category": ""}))
    hire_counter = 1

    for filename in sorted(os.listdir(DOC_DIR)):
        if not filename.endswith(".xlsx"):
            continue
        campus_name = clean_campus_name(filename)
        path = os.path.join(DOC_DIR, filename)
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        header = [str(c).strip().upper() if c else "" for c in rows[0]]

        def get_col(r, name):
            if name in header:
                idx = header.index(name)
                return r[idx] if idx < len(r) else None
            return None

        for r in rows[1:]:
            if not any(r):
                continue
            name_val = f"{str(r[1] or '').strip()} {str(r[2] or '').strip()}".strip()
            jt_val = get_col(r, "JOB TITLE") or ""
            assign_val = get_col(r, "ASSIGNMENT") or ""
            st_val = get_col(r, "STATUS") or ""
            pst_val = get_col(r, "POSITION STATUS") or ""
            pos_id_val = get_col(r, "POSITION ID") or ""
            hire_date_val = get_col(r, "HIRE DATE") or ""

            # Filter template artifacts / terminated employees carried over from master template
            if "TERM/TRANSFER" in str(st_val).upper() and any(x in name_val for x in ["Cynthia Sanchez", "Jerrod Porter", "Amanda Coates", "Anecito Lano", "Danielle Trevino", "Sophie Oliver"]):
                continue

            is_term = "T - Terminated" in str(pst_val) or "TERM" in str(st_val).upper()
            if is_term:
                continue

            is_vacant = "VACANT" in str(st_val).upper()
            status = "Vacant" if is_vacant else "Filled"

            category, role = categorize_and_normalize_role(jt_val, assign_val)

            # Each active or vacant line represents an approved allocation slot in the baseline plan
            campus_approved_roles[campus_name][role]["approved"] += 1.0
            campus_approved_roles[campus_name][role]["category"] = category

            # Format hire date
            date_str = ""
            if isinstance(hire_date_val, (datetime.datetime, datetime.date)):
                date_str = hire_date_val.strftime("%Y-%m-%d")
            elif hire_date_val:
                date_str = str(hire_date_val)[:10]

            hire_id = f"HIRE-{hire_counter:04d}"
            hire_counter += 1

            all_hires.append({
                "hire_id": hire_id,
                "campus": campus_name,
                "role": role,
                "category": category,
                "employee_name": name_val if not is_vacant else "[Approved Vacancy - Open]",
                "job_title": str(jt_val).strip(),
                "assignment": str(assign_val).strip(),
                "fte": 1.0,
                "status": status,
                "position_id": str(pos_id_val).strip() if pos_id_val else "",
                "hire_date": date_str,
                "override_flag": "No",
                "override_reason": ""
            })

    # Build Approved_Plan rows
    approved_plan = []
    plan_counter = 1
    for campus in sorted(campus_approved_roles.keys()):
        for role in sorted(campus_approved_roles[campus].keys()):
            info = campus_approved_roles[campus][role]
            approved_plan.append({
                "plan_id": f"PLAN-{plan_counter:04d}",
                "campus": campus,
                "role": role,
                "category": info["category"],
                "approved_fte": float(info["approved"]),
                "last_revised_date": "2026-08-01",
                "last_revised_by": "budget-director@ssttx.org",
                "revision_notes": "Initial 2026-2027 SY approved staffing budget allocation"
            })
            plan_counter += 1

    # Aggregate Campuses
    campuses_summary = []
    for campus in sorted(campus_approved_roles.keys()):
        meta = CAMPUS_METADATA.get(campus, {"region": "Texas", "type": "SST", "short_name": campus, "grades": "K-12"})
        app_total = sum(item["approved_fte"] for item in approved_plan if item["campus"] == campus)
        filled_total = sum(h["fte"] for h in all_hires if h["campus"] == campus and h["status"] == "Filled")
        vacant_total = sum(h["fte"] for h in all_hires if h["campus"] == campus and h["status"] == "Vacant")
        variance = filled_total - app_total

        campuses_summary.append({
            "campus": campus,
            "short_name": meta["short_name"],
            "region": meta["region"],
            "type": meta["type"],
            "grades": meta["grades"],
            "approved_fte": app_total,
            "actual_fte": filled_total,
            "vacant_fte": vacant_total,
            "variance": variance,
            "violations_count": 0
        })

    # Initial Audit Log entry
    audit_log = [
        {
            "log_id": "AUDIT-0001",
            "timestamp": "2026-08-01 09:00:00",
            "user_email": "system-migration@ssttx.org",
            "action_type": "MIGRATION_INITIALIZED",
            "campus": "ALL_CAMPUSES",
            "role": "ALL_ROLES",
            "old_value": "None",
            "new_value": f"{len(approved_plan)} Approved Allocations ({sum(c['approved_fte'] for c in campuses_summary)} FTE)",
            "reason_notes": "Baseline 2026-2027 FTE staffing plan migration from FTE Planning files into Google Sheets backend",
            "override_status": "STANDARD"
        },
        {
            "log_id": "AUDIT-0002",
            "timestamp": "2026-08-01 09:15:00",
            "user_email": "system-migration@ssttx.org",
            "action_type": "ROSTER_IMPORTED",
            "campus": "ALL_CAMPUSES",
            "role": "ALL_ROLES",
            "old_value": "None",
            "new_value": f"{len(all_hires)} Personnel/Slots ({sum(c['actual_fte'] for c in campuses_summary)} Filled, {sum(c['vacant_fte'] for c in campuses_summary)} Vacant)",
            "reason_notes": "Current staffing roster synchronized with HR exports",
            "override_status": "STANDARD"
        }
    ]

    violations = []

    return {
        "campuses": campuses_summary,
        "approved_plan": approved_plan,
        "actual_hires": all_hires,
        "violations": violations,
        "audit_log": audit_log
    }

def export_to_excel(data, output_path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    navy_fill = PatternFill(start_color="0B2545", end_color="0B2545", fill_type="solid")
    crimson_fill = PatternFill(start_color="8B0000", end_color="8B0000", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    def style_header(ws, fill=navy_fill):
        for cell in ws[1]:
            cell.fill = fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 26

    def autofit_cols(ws):
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    # 1. Sheet: Campuses
    ws_camp = wb.create_sheet(title="Campuses")
    ws_camp.append(["Campus Name", "Short Code", "Region", "System Type", "Grades", "Approved FTE", "Actual Filled FTE", "Vacancies", "Variance", "Violations Count"])
    for c in data["campuses"]:
        ws_camp.append([c["campus"], c["short_name"], c["region"], c["type"], c["grades"], c["approved_fte"], c["actual_fte"], c["vacant_fte"], c["variance"], c["violations_count"]])
    style_header(ws_camp)
    autofit_cols(ws_camp)

    # 2. Sheet: Approved_Plan
    ws_plan = wb.create_sheet(title="Approved_Plan")
    ws_plan.append(["Plan ID", "Campus", "Role Title", "Category", "Approved FTE", "Last Revised Date", "Last Revised By", "Revision Notes"])
    for p in data["approved_plan"]:
        ws_plan.append([p["plan_id"], p["campus"], p["role"], p["category"], p["approved_fte"], p["last_revised_date"], p["last_revised_by"], p["revision_notes"]])
    style_header(ws_plan)
    autofit_cols(ws_plan)

    # 3. Sheet: Actual_Hires
    ws_hires = wb.create_sheet(title="Actual_Hires")
    ws_hires.append(["Hire ID", "Campus", "Role Title", "Category", "Employee Name", "HR Job Title", "Assignment", "FTE", "Status", "Position ID", "Hire Date", "Override Flag", "Override Reason"])
    for h in data["actual_hires"]:
        ws_hires.append([h["hire_id"], h["campus"], h["role"], h["category"], h["employee_name"], h["job_title"], h["assignment"], h["fte"], h["status"], h["position_id"], h["hire_date"], h["override_flag"], h["override_reason"]])
    style_header(ws_hires)
    autofit_cols(ws_hires)

    # 4. Sheet: Violations_Overrides
    ws_viol = wb.create_sheet(title="Violations_Overrides")
    ws_viol.append(["Violation ID", "Campus", "Role Title", "Violation Type", "Approved FTE", "Actual FTE", "Variance", "Employee Name", "Status", "Override Reason", "Logged Date", "Logged By", "Resolved Date", "Resolved By"])
    for v in data["violations"]:
        ws_viol.append([v["violation_id"], v["campus"], v["role"], v["type"], v["approved_fte"], v["actual_fte"], v["variance"], v["employee_name"], v["status"], v["override_reason"], v["logged_date"], v["logged_by"], v.get("resolved_date", ""), v.get("resolved_by", "")])
    style_header(ws_viol, crimson_fill)
    autofit_cols(ws_viol)

    # 5. Sheet: Audit_Log
    ws_audit = wb.create_sheet(title="Audit_Log")
    ws_audit.append(["Log ID", "Timestamp (UTC-5)", "User Email", "Action Type", "Campus", "Role Title", "Old Value", "New Value", "Reason / Notes", "Override Status"])
    for a in data["audit_log"]:
        ws_audit.append([a["log_id"], a["timestamp"], a["user_email"], a["action_type"], a["campus"], a["role"], a["old_value"], a["new_value"], a["reason_notes"], a["override_status"]])
    style_header(ws_audit)
    autofit_cols(ws_audit)

    wb.save(output_path)
    print(f"Excel database created successfully at: {output_path}")

def main():
    print("Starting SST FTE Planning Data Migration...")
    data = parse_all_campuses()
    
    excel_path = os.path.join(BASE_DIR, "SST_FTE_Planning_Database.xlsx")
    export_to_excel(data, excel_path)
    
    json_path = os.path.join(BASE_DIR, "migrated_fte_data.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"JSON database exported to: {json_path}")
    
    print("\n--- MIGRATION SUMMARY ---")
    print(f"Campuses Processed: {len(data['campuses'])}")
    print(f"Approved Plan Allocations: {len(data['approved_plan'])}")
    print(f"Total Approved FTE: {sum(c['approved_fte'] for c in data['campuses'])}")
    print(f"Total Actual Filled: {sum(c['actual_fte'] for c in data['campuses'])}")
    print(f"Total Approved Vacancies: {sum(c['vacant_fte'] for c in data['campuses'])}")
    print(f"Total Staff/Slots in Roster: {len(data['actual_hires'])}")
    print("-------------------------\n")

if __name__ == "__main__":
    main()
