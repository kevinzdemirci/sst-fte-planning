#!/usr/bin/env python3
"""
Pulls ADP Position data and writes it to the ADP_Positions tab of the 2027-28
FTE Planning Google Sheet. Run by .github/workflows/adp_refresh_2027.yml when
someone clicks "Refresh ADP data" in the portal.

Environment:
  SHEET_ID                     Google Sheet ID (passed by the portal)
  GOOGLE_SERVICE_ACCOUNT_JSON  service account key; the sheet must be shared with it (Editor)
  ADP_CLIENT_ID / ADP_CLIENT_SECRET / ADP_CERT_PATH / ADP_KEY_PATH  (see sync_adp_payroll.py)
Only counts are printed - the workflow log is public.
"""

import os
import json
import datetime
from zoneinfo import ZoneInfo

import gspread

from adp_rows import adp, ADP_HEADERS, adp_row

CENTRAL = ZoneInfo("America/Chicago")


def main():
    workers = adp.fetch_adp_workers()
    pulled_at = datetime.datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M")
    values = [ADP_HEADERS] + [adp_row(w) for w in workers]

    gc = gspread.service_account_from_dict(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]))
    sh = gc.open_by_key(os.environ["SHEET_ID"])

    ws = sh.worksheet("ADP_Positions")
    ws.clear()
    ws.resize(rows=len(values), cols=len(ADP_HEADERS))
    ws.update(values=values, range_name="A1", value_input_option="RAW")

    settings = sh.worksheet("Settings")
    keys = settings.col_values(1)
    if "adp_pulled_at" in keys:
        settings.update_cell(keys.index("adp_pulled_at") + 1, 2, pulled_at)
    else:
        settings.append_row(["adp_pulled_at", pulled_at], value_input_option="RAW")

    log = sh.worksheet("Change_Log")
    headers = log.row_values(1)
    entry = {"timestamp": datetime.datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
             "user": "adp-refresh (GitHub Actions)", "action": "ADP_REFRESHED",
             "note": f"{len(workers)} ADP worker records, {sum(w['status'] == 'Active' for w in workers)} active"}
    log.append_row([entry.get(h, "") for h in headers], value_input_option="RAW")

    print(f"Wrote {len(workers)} ADP worker records to ADP_Positions (pulled {pulled_at})")


if __name__ == "__main__":
    main()
