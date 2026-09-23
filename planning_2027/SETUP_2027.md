# 2027-28 FTE Planning Portal — Setup Guide

The portal replaces the per-campus FTE spreadsheets for 2027-28. Staff sign in with their
**@ssttx.org** Google account, update positions directly, and every change is logged with who, when,
the old value and the new value. The ADP cross-check runs live inside the portal.

```
Staff (@ssttx.org) ──▶ Portal (Google Apps Script web app)
                          │ reads / writes (only through the portal)
                          ▼
                 Google Sheet "2027-28 FTE Planning Database"
                 Positions · Change_Log · Editors · ADP_Positions · …
                          ▲
   "Refresh ADP data" ──▶ GitHub Action (ADP certificate in GitHub secrets) ──▶ ADP API
```

**Setup time:** Part A and Part B take about 20 minutes. Part C takes about 30 minutes, and you may need your IT admin for its first step.

---

## Part A — Create the database (Google Sheet)

1. Sign in to Google Drive with your **@ssttx.org** account.
2. Upload `planning_2027/2027-28 FTE Planning Database.xlsx`.
3. Open it and choose **File → Save as Google Sheets**. Then delete the uploaded .xlsx copy from Drive.
4. Rename the sheet to **2027-28 FTE Planning Database**.
5. **Do not share this sheet with staff.** They use the portal instead, which is what keeps the change log trustworthy.

The sheet starts out filled in from the 2026-27 approved lists, checked against ADP on 2026-09-23:

| Tab | What it holds |
|---|---|
| Positions | 1,281 planned slots. 1,031 are Returning (names and Position IDs taken from ADP). 249 are Open: some were open slots and some were held by staff who have since been terminated in ADP; the previous holder is in Notes. 1 is Not returning. |
| Change_Log | One `SEED_IMPORT` row per position, marking the starting point |
| Editors | Ali Dal and Hasan Kendirci as editors for all campuses |
| Campuses, Job_Titles | Lists used in the portal's drop-downs |
| ADP_Positions | The latest ADP snapshot, used by the cross-check |
| Settings | School year and the time ADP was last pulled |

## Part B — Put the portal online

1. In the Google Sheet, go to **Extensions → Apps Script**.
2. In the editor:
   - Replace the contents of `Code.gs` with `planning_2027/apps_script/Code.gs`.
   - Click **+ → HTML**, name the file `Portal`, and paste in `planning_2027/apps_script/Portal.html`.
   - Open **Project Settings (⚙)** and tick **Show "appsscript.json" manifest file in editor**. Then replace the contents of `appsscript.json` with `planning_2027/apps_script/appsscript.json`.
3. Click **Deploy → New deployment → Web app**:
   - **Execute as:** Me
   - **Who has access:** Anyone within School of Science and Technology (your domain)
4. Click **Deploy**, approve the permissions, and copy the **Web app URL**. That URL is the portal. Share it with Ali, Hasan and anyone else you add.
5. Open the URL. As the owner you're automatically an **admin**. Use the **Access** tab to add people:
   - **Admin** — adds and removes position slots, edits anything, and manages access.
   - **Editor** — fills slots (person, status, ADP Position ID, assignment, notes) at their campuses. Enter `ALL`, or campus codes such as `ALM, DIS`.
   - **Viewer** — read only, for example superintendents and board members.

   Anyone signed in who isn't on the list sees a "No access yet" page.

> After you change `Code.gs` or `Portal.html` later, go to **Deploy → Manage deployments → Edit → Version: New version** so the live URL picks up the change.

## Part C — Turn on "Refresh ADP data" (one time)

Until this part is done, the portal works normally but cross-checks against the ADP snapshot that came with the database.

1. **Google service account** (ask IT if Workspace policy blocks service-account keys):
   1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project, for example *SST FTE Planning*.
   2. Enable the **Google Sheets API** for that project.
   3. Under **IAM & Admin → Service accounts**, create an account called *fte-adp-refresh*. Then go to **Keys → Add key → JSON**, which downloads a key file.
   4. Share the Google Sheet with the service account's email address (…@…iam.gserviceaccount.com) as **Editor**.
2. **GitHub secrets.** In the repo, go to Settings → Secrets and variables → Actions. Add `GOOGLE_SERVICE_ACCOUNT_JSON` and paste in the whole JSON key file.
   The ADP secrets (`ADP_CLIENT_ID`, `ADP_CLIENT_SECRET`, `ADP_CERT_PEM`, `ADP_KEY_PEM`) are the same four as for the 2026-27 dashboard.
3. **Push the workflow.** `.github/workflows/adp_refresh_2027.yml` has to be pushed to GitHub. That needs a GitHub token with the `workflow` scope; see the earlier note about replacing the token.
4. **Let the portal start the workflow:**
   1. Create a GitHub **fine-grained token** limited to `sst-fte-planning`, with **Actions: Read and write** permission.
   2. In Apps Script, go to **Project Settings → Script properties** and add:
      - `GITHUB_TOKEN` — that token
      - `GITHUB_REPO` — `kevinzdemirci/sst-fte-planning`

   The token stays on Google's server, so staff never see it or need a GitHub account.
5. In the portal, click **Refresh ADP data**. After about 5 minutes the header shows the new "ADP data from…" time and the cross-check updates. The refresh is also recorded in the Change log.

---

## Using the portal through the summer

| Tab | What it's for |
|---|---|
| **Plan** | Pick a campus. Click a row to edit it. Type a name in **Find the person in ADP** to fill in the name and Position ID straight from ADP; the ADP check updates as you type. Statuses: *Returning*, *New hire*, *Not returning* (the slot opens up), *Open* (to hire). Admins also see **+ Add position**, **Copy** (another slot like this one), **Remove** (a reason is required) and **Show removed** / **Restore**. |
| **Summary** | Slots by status per campus against full-time staff active in ADP, plus the staffing-by-job-title view (teachers, campus administration and so on, as totals or a matrix). Every number can be clicked. |
| **ADP cross-check** | Location differs, Title differs, Name differs, Terminated in ADP, Not found in ADP, New hires not yet in ADP, In ADP but not in the plan, Same person twice, and Overhire by job title. Every number can be clicked, and there's a CSV export. |
| **Change log** | Every change, newest first. Filter by campus, person, action or date, and export to CSV. Each position also has a **History** button. |
| **Access** | (Admin only) Who can use the portal and what they can do. |

**Safeguards**
- If two people edit the same position, the second person is told who changed it and when, and asked to reload. Nothing is silently overwritten.
- Removing a slot is a soft delete with a required reason, and it can be restored.
- Substitutes and part-time aides are not planned here and are left out of the ADP headcount, the same as on the 2026-27 dashboard.

**Rebuilding the starting database** (only before go-live, since it resets all changes): run `python3 sync_adp_payroll.py` and then `python3 planning_2027/build_seed_2027.py`.
