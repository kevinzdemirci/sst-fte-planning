# SST Schools — Campus FTE Staffing & Planning Web App
## Plain-Language Administrator & Leadership Setup Guide

This system replaces the previous spreadsheet-only workflow with a validated Google Workspace web application backed by a structured Google Sheets database.

---

### What Was Built & Migrated

1. **Structured Backend Database (`SST_FTE_Planning_Database.xlsx`):**
   - **`Approved_Plan`**: 576 role allocations across all 21 SST campuses + 2 partner campuses (1,359.0 total approved FTEs).
   - **`Actual_Hires`**: Complete live roster of 1,359 staff slots (1,336 active filled positions + 23 open vacancies).
   - **`Campuses`**: Rollup metrics for all campuses (Approved FTE, Live Filled, Vacancies, Variance, Violations).
   - **`Violations_Overrides`**: Dedicated watchdog tracker for unapproved roles and over-budget hiring.
   - **`Audit_Log`**: Permanent, unfalsifiable history recording user identity, exact timestamp, old value, new value, and justification notes for every change.

2. **Google Apps Script Web App (`apps_script/` folder):**
   - **`Code.gs`**: Server-side controller enforcing strict validation, override requirements, and tamper-proof audit logging.
   - **`Index.html`**: Clean, modern responsive interface with Leadership (Read-Only) and Editor (My View) modes.
   - **`Migration.gs`**: Database structure setup and sheet protection helper.
   - **`appsscript.json`**: Workspace manifest.

3. **Standalone Interactive Browser Preview (`fte_planning_app.html`):**
   - Immediate, zero-setup browser app pre-loaded with your real migrated data so you can test and demonstrate all features right now on your computer.

---

### Step 1: Immediate Local Preview & Testing

Before deploying to Google Drive, you can test and inspect the full application immediately in your browser:
1. Open the file **`fte_planning_app.html`** in Chrome, Edge, or Safari (double-click it in Finder).
2. Test switching between **Editor (My View)** and **Leadership View (Read-Only)** in the top right.
3. Try clicking **"Log New Hire"**:
   - If you select an approved role with capacity, it saves normally and updates the live variance.
   - If you select an unapproved role or attempt to hire past the approved FTE count, the app **blocks the save** with a red violation alert and requires you to check **"Grant Explicit Administrative Override"** and enter a **mandatory reason note**.
4. Test clicking **"Revise"** on any row in the **FTE Plan Matrix**: notice that casual edits are impossible; it requires an explicit approved FTE revision with a budget justification reason.
5. Click **"Unfalsifiable Audit Trail"**: observe how every single revision, override, hire, and removal is permanently logged with timestamps, previous values, new values, and reasons.

---

### Step 2: Deploying to Google Workspace (5 Minutes)

#### A. Upload the Migrated Database to Google Drive
1. Open **Google Drive** (`drive.google.com`) logged into your `@ssttx.org` account.
2. Click **New > File upload** and select `SST_FTE_Planning_Database.xlsx` from this project folder.
3. Right-click the uploaded file in Drive and choose **Open with > Google Sheets**.
4. Go to **File > Save as Google Sheets**. This will create a native Google Sheet with all 5 sheets ready.

#### B. Paste the Apps Script Code
1. In your new Google Sheet, click the top menu: **Extensions > Apps Script**.
2. Rename the project to `SST Campus FTE Planning Portal`.
3. In the left panel, replace the contents of `Code.gs` with the code from [apps_script/Code.gs](file:///Users/ekode2/Desktop/AntiGravity%20Projects/apps_script/Code.gs).
4. Click the `+` icon next to Files, select **HTML**, name it `Index`, and paste the code from [apps_script/Index.html](file:///Users/ekode2/Desktop/AntiGravity%20Projects/apps_script/Index.html).
5. Click the `+` icon next to Files, select **Script**, name it `Migration`, and paste the code from [apps_script/Migration.gs](file:///Users/ekode2/Desktop/AntiGravity%20Projects/apps_script/Migration.gs).
6. Click the Save icon (Floppy disk).
7. *(Optional)* Select the function `setupDatabaseStructure` in the toolbar and click **Run** once to ensure the `Audit_Log` sheet is locked and protected against manual tampering.

#### C. Deploy as a Web App
1. In the top-right of Apps Script, click **Deploy > New deployment**.
2. Click the gear icon next to "Select type" and choose **Web app**.
3. Configure the deployment:
   - **Description**: `SST FTE Staffing Portal v1.0`
   - **Execute as**: `User accessing the web app` (or `Me`)
   - **Who has access**: `Anyone within SST Schools` (this automatically uses your existing Google Workspace accounts).
4. Click **Deploy**.
5. Authorize access when prompted using your SST Google account.
6. Copy the **Web App URL** provided at the end of the deployment.

---

### Step 3: How Permissions & Role-Based Access Control (RBAC) Work

You do not need to create or manage any external logins or passwords. Access is controlled through Google Workspace email accounts and server-side RBAC:

#### Authorized Editors Whitelist:
The backend controller in [`apps_script/Code.gs`](file:///Users/ekode2/Desktop/AntiGravity%20Projects/apps_script/Code.gs) contains a verified whitelist:
- **Ali Dal** (`adal@ssttx.org`) — Regional Talent Acquisition
- **Hasan Kendirci** (`hkendirci@ssttx.org`) — Regional Talent Acquisition
- Central Office FTE Planning Administrator / Spreadsheet Owner

#### Granting Access in Google Drive / Google Sheets:
1. **Automated One-Click Method:** In the Apps Script toolbar, select the function **`grantTalentAcquisitionPermissions`** from the function dropdown and click **Run**. This automatically shares the spreadsheet with `adal@ssttx.org` and `hkendirci@ssttx.org` as Editors and locks the `Audit_Log` against direct spreadsheet alterations.
2. **Manual Share Dialog:** Alternatively, in Google Sheets, click the green **Share** button in the top right, enter `adal@ssttx.org` and `hkendirci@ssttx.org`, select **Editor**, and click Send.

| User / Role | Identity & Email | Capabilities Across All 21 Campuses |
| :--- | :--- | :--- |
| **Regional Talent Acquisition** | **Ali Dal** (`adal@ssttx.org`)<br>**Hasan Kendirci** (`hkendirci@ssttx.org`) | **Full Campus Editor Access**: Log new hires, update existing assignments, remove vacated records, request/approve administrative overrides with mandatory justification, revise approved FTE plans, resolve tracked violations. Every action is signed with their email and timestamped in the permanent audit trail. |
| **FTE Administrator** | `admin@ssttx.org` / Script Owner | **Full Administrator Access**: All editor capabilities, audit log export, and permission management. |
| **Executive Leadership & Board** | Superintendent, CFO, Board Members | **Read-Only Dashboard**: High-level network metrics, campus rollups across all 21 campuses, drill-down role inspections, open violation alerts. No edit buttons or inputs are displayed. (Access via `?view=leadership` or Viewer permissions). |

> [!TIP]
> **Live Web App User Switching:**
> In the live web app, click the user badge in the top right to instantly switch active profiles between **Ali Dal (Regional Talent Acquisition)**, **Hasan Kendirci (Regional Talent Acquisition)**, **FTE Planning Administrator**, and **Leadership View (Read-Only)**.

---


### Step 4: How the Audit Log Works (Tamper-Proof)

The unfalsifiable audit log was your number one requirement. Here is how it protects your data:

1. **Automatic Logging of Every Event:**
   - Whenever an Approved Plan allocation is modified, the old FTE, new FTE, user email, timestamp, and revision justification note are permanently recorded.
   - Whenever a hire is logged, updated, or removed, the previous value, new employee details, and user notes are permanently logged.
   - Whenever an unapproved role or over-FTE hire is overridden, the record is flagged as `OVERRIDDEN` with the mandatory administrative justification.
2. **Protection Against Manual Falsification:**
   - In Google Sheets, the `Audit_Log` tab is protected so only the script owner can modify its structure.
   - The web app only appends new records; it has **no functionality to delete or alter past audit rows**.
3. **Exporting for Audits & Board Reports:**
   - On the **Unfalsifiable Audit Trail** tab in the web app, click **"Export Audit to CSV"** at any time to generate an official timestamped spreadsheet report for auditors or leadership.
