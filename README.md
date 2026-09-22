# School of Science & Technology (SST) — Campus FTE Staffing & Planning Portal

![School of Science & Technology Logo](sst_logo.jpg)

> **"Better Education, Better Future"**  
> *A Texas charter school network with 21 campuses across San Antonio, Houston, and Corpus Christi.*

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-crimson?style=for-the-badge&logo=github)](https://kevinzdemirci.github.io/sst-fte-planning/)
[![Platform](https://img.shields.io/badge/Platform-Google%20Workspace-navy?style=for-the-badge&logo=google)](SETUP_GUIDE.md)
[![Audit](https://img.shields.io/badge/Audit-Tamper--Proof%20Logged-green?style=for-the-badge)](SETUP_GUIDE.md)

---

## 🌐 Live Web Application

- **Live GitHub Pages Link**: [https://kevinzdemirci.github.io/sst-fte-planning/](https://kevinzdemirci.github.io/sst-fte-planning/)
- **Local Browser App**: Simply open [`index.html`](index.html) or [`fte_planning_app.html`](fte_planning_app.html) directly in any web browser.

---

## 📌 Executive Overview

This portal replaces spreadsheet-only FTE (full-time-equivalent) staffing tracking across all 21 SST campuses and 2 partner campuses. It gives the FTE Planning Administrator full control to validate hiring and enforce approved headcount, while giving Superintendents, Board Members, and Regional Directors clean read-only visibility into campus staffing variances.

### The Staffing Baseline (2026–2027 SY)
- **Campuses Monitored**: 21 SST Campuses + 2 Partner Campuses (23 sites total)
- **Total Approved FTE Baseline**: **1,359.0 FTEs** across 576 role allocations
- **Active / Live Filled Headcount**: **1,336.0 FTEs** (98.3% staffing fill rate)
- **Approved Open Vacancies**: **23.0 FTEs**
- **Active Violations / Flags**: **0 Unapproved Hires**

---

## 🔑 Core Capabilities

### 1. Strict Real-Time Hiring Validation & Administrative Overrides
- When logging a hire, the system validates against the baseline budget:
  - **Catches unapproved roles**: Alerts immediately if a campus attempts to hire into a role that was never approved.
  - **Catches over-FTE violations**: Alerts immediately if adding a hire causes `Actual FTE > Approved FTE`.
- **Enforced Overrides**: The system blocks casual submissions when a violation occurs. To proceed, an explicit **Administrative Override** must be granted with a **mandatory justification reason** (e.g. emergency SPED student transfer or board amendment).

### 2. Permanent Unfalsifiable Audit Trail
- Every plan revision, new hire, status update, removed hire, or override is permanently recorded in the `Audit_Log`.
- Logs record the exact CST timestamp to the second, the user's Google email (`@ssttx.org`), previous value, new value, override status, and reason notes.
- Includes a single-click **Export Audit to CSV** for board meetings and official state reporting.

### 3. Dual Role-Based Views
- **Editor View ("My View")**: Manage approved plans, log/update live hires, resolve open violation flags, authorize new roles, and browse audit history.
- **Leadership View (Read-Only)**: Pure visibility for superintendents and board members with network KPIs, campus rollups, variance indicators, and role-by-role drilldown drawers. Can be accessed via the top-right toggle or by sharing the link with `?view=leadership`.

---

## 🗄️ Database Architecture

| Sheet Name | Description | Key Fields |
| :--- | :--- | :--- |
| **`Campuses`** | Network rollup across all 21 campuses | Campus Name, Region, Grades, Approved FTE, Actual FTE, Vacancies, Variance, Violations |
| **`Approved_Plan`** | Baseline approved FTE counts per role | Plan ID, Campus, Role Title, Category, Approved FTE, Last Revised Date/By, Revision Notes |
| **`Actual_Hires`** | Live personnel roster and approved vacancies | Hire ID, Campus, Role, Employee Name, Assignment, FTE, Status, Position ID, Override Details |
| **`Violations_Overrides`** | Watchdog log for hiring exceptions | Violation ID, Campus, Role, Type, Approved FTE, Actual FTE, Variance, Override Justification |
| **`Audit_Log`** | Tamper-proof transaction ledger | Log ID, Timestamp, User Email, Action Type, Campus, Role, Old Value, New Value, Reason |

---

## 🚀 Deployment Instructions

### A. GitHub Pages Deployment
1. Repository is live on GitHub: `https://github.com/kevinzdemirci/sst-fte-planning`
2. Your live app is accessible at `https://kevinzdemirci.github.io/sst-fte-planning/`.

### B. Google Workspace / Apps Script Deployment
Follow the plain-language guide in [**`SETUP_GUIDE.md`**](SETUP_GUIDE.md) to upload `SST_FTE_Planning_Database.xlsx` to Google Drive and deploy the code in `apps_script/` inside your organization.
