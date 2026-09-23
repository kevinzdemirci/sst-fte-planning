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

## 📌 What this tool does

Cross-checks every person on the **2026-27 Approved FTE Lists** against the **ADP Workforce Now Staff Profile → Position tab** (Position ID, Job Title, Location) for all campuses, and flags:

| Check | Meaning |
| :--- | :--- |
| **Location differs** | ADP home work location is a different campus than the FTE list |
| **Title differs** | ADP job code (e.g. `11TEACH`) differs from the FTE list job title |
| **Name differs** | Same Position ID, different name in ADP (usually a name change) |
| **On list, not active** | On the approved list but terminated / not found in ADP (slot is really open) |
| **Not on FTE list** | Active in ADP at a campus but on no approved list |
| **Overhire** | ADP active headcount for a campus + job title exceeds its approved slots |

People are matched by ADP Position ID, falling back to name when the Position ID changed (transfer/rehire). Terminated and template rows copied from other campuses (`POSITION STATUS = T`, `STATUS = TERM/TRANSFER`) are not counted as approved slots.

## 🔄 Refreshing the data

```bash
python3 sync_adp_payroll.py            # pull live ADP positions + reconcile (needs .env + certs)
python3 sync_adp_payroll.py --cached   # re-run using the last ADP pull in adp_cache/
python3 build_webapp_ui.py             # rebuild index.html / fte_planning_app.html / apps_script/Index.html
```

To add or replace a campus list, drop the file in `FTE Planning.md/2026-2027 Approved FTE Docs/` and update its filename in the `CAMPUSES` table in `sync_adp_payroll.py`.

---

## 🚀 Deployment Instructions

### A. GitHub Pages Deployment
1. Repository is live on GitHub: `https://github.com/kevinzdemirci/sst-fte-planning`
2. Your live app is accessible at `https://kevinzdemirci.github.io/sst-fte-planning/`.

### B. Google Workspace / Apps Script Deployment
Follow the plain-language guide in [**`SETUP_GUIDE.md`**](SETUP_GUIDE.md) to upload `SST_FTE_Planning_Database.xlsx` to Google Drive and deploy the code in `apps_script/` inside your organization.
