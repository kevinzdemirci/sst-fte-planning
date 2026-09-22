#!/usr/bin/env python3
"""
Builder for SST Schools FTE Planning Web Applications:
1. index.html (Root GitHub Pages live link file)
2. fte_planning_app.html (Standalone Browser Demo)
3. apps_script/Index.html (Google Apps Script Web App UI)
"""

import json
import os
import base64

BASE_DIR = "/Users/ekode2/Desktop/AntiGravity Projects"
JSON_PATH = os.path.join(BASE_DIR, "migrated_fte_data.json")
LOGO_PATH = os.path.join(BASE_DIR, "sst_logo.jpg")

with open(JSON_PATH, "r") as f:
    DATABASE = json.load(f)

# Load SST logo and convert to base64
with open(LOGO_PATH, "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode("utf-8")
LOGO_DATA_URI = f"data:image/jpeg;base64,{LOGO_B64}"

print(f"Loaded {len(DATABASE['campuses'])} campuses, {len(DATABASE['approved_plan'])} plan rows, {len(DATABASE['actual_hires'])} hire rows.")

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>School of Science &amp; Technology - Campus FTE Staffing Portal</title>
  <link rel="icon" type="image/jpeg" href="{LOGO_DATA_URI}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy-900: #07172c;
      --navy-800: #0B2545;
      --navy-700: #133968;
      --navy-600: #1d4e89;
      --crimson-700: #7f0000;
      --crimson-600: #990000;
      --crimson-100: #fee2e2;
      --amber-600: #d97706;
      --amber-100: #fef3c7;
      --amber-50: #fffbeb;
      --green-700: #15803d;
      --green-600: #16a34a;
      --green-100: #dcfce7;
      --green-50: #f0fdf4;
      --slate-50: #f8fafc;
      --slate-100: #f1f5f9;
      --slate-200: #e2e8f0;
      --slate-300: #cbd5e1;
      --slate-400: #94a3b8;
      --slate-500: #64748b;
      --slate-600: #475569;
      --slate-700: #334155;
      --slate-800: #1e293b;
      --slate-900: #0f172a;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
      --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
      --radius-sm: 6px;
      --radius-md: 8px;
      --radius-lg: 12px;
      --radius-xl: 16px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    body {{
      background-color: #f1f5f9;
      color: var(--slate-800);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }}

    /* Top Brand Navigation Bar */
    header.brand-nav {{
      background: linear-gradient(135deg, #07172c 0%, #0B2545 100%);
      color: #ffffff;
      padding: 0.65rem 1.75rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: var(--shadow-md);
      position: sticky;
      top: 0;
      z-index: 100;
      border-bottom: 3.5px solid var(--crimson-600);
    }}

    .brand-left {{
      display: flex;
      align-items: center;
      gap: 1.15rem;
    }}

    .brand-logo-card {{
      background-color: #ffffff;
      padding: 3px 8px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }}

    .brand-logo-card img {{
      height: 44px;
      width: auto;
      object-fit: contain;
      display: block;
    }}

    .brand-titles h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.2px;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .brand-motto {{
      font-size: 0.76rem;
      color: #fca5a5;
      font-style: italic;
      font-weight: 500;
      margin-left: 0.25rem;
    }}

    .brand-subtitle {{
      font-size: 0.74rem;
      color: var(--slate-300);
      margin-top: 1px;
    }}

    .brand-right {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    /* View Switcher Controls */
    .mode-pill-container {{
      display: flex;
      background-color: rgba(255, 255, 255, 0.12);
      padding: 3px;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .mode-btn {{
      background: none;
      border: none;
      color: var(--slate-200);
      padding: 0.35rem 0.9rem;
      font-size: 0.8rem;
      font-weight: 600;
      border-radius: 9999px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s ease;
    }}

    .mode-btn.active {{
      background-color: #ffffff;
      color: var(--navy-900);
      box-shadow: var(--shadow-sm);
    }}


    .user-profile-selector-wrap {{
      position: relative;
    }}
    .user-switch-select {{
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
      width: 100%;
      height: 100%;
    }}
    .user-badge:hover {{
      background-color: rgba(255, 255, 255, 0.18);
      border-color: rgba(255, 255, 255, 0.35);
    }}
    .user-badge {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background-color: rgba(255, 255, 255, 0.1);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      color: var(--slate-200);
      border: 1px solid rgba(255, 255, 255, 0.15);
    }}

    .user-avatar {{
      width: 24px;
      height: 24px;
      background-color: var(--crimson-600);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: white;
      font-size: 0.72rem;
    }}

    /* Leadership Mode Notice Banner */
    #leadership-banner {{
      background: linear-gradient(90deg, #1e293b, #334155);
      color: #f8fafc;
      padding: 0.6rem 1.75rem;
      font-size: 0.8rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--slate-300);
    }}

    #leadership-banner.hidden {{
      display: none;
    }}

    .banner-badge {{
      background-color: #38bdf8;
      color: #0f172a;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    /* KPI Header Bar */
    .kpi-section {{
      background: #ffffff;
      padding: 1rem 1.75rem;
      border-bottom: 1px solid var(--slate-200);
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 1rem;
    }}

    .kpi-card {{
      background: var(--slate-50);
      border: 1px solid var(--slate-200);
      border-radius: var(--radius-md);
      padding: 0.75rem 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
      position: relative;
      overflow: hidden;
    }}

    .kpi-card::before {{
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 4px;
      background-color: var(--navy-600);
    }}

    .kpi-card.kpi-approved::before {{ background-color: var(--navy-600); }}
    .kpi-card.kpi-filled::before {{ background-color: var(--green-600); }}
    .kpi-card.kpi-vacant::before {{ background-color: var(--amber-600); }}
    .kpi-card.kpi-violation::before {{ background-color: var(--crimson-600); }}

    .kpi-label {{
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--slate-500);
    }}

    .kpi-value {{
      font-size: 1.55rem;
      font-weight: 800;
      color: var(--slate-900);
      line-height: 1.2;
    }}

    .kpi-sub {{
      font-size: 0.75rem;
      color: var(--slate-600);
    }}

    /* Navigation Tabs */
    .tab-bar-container {{
      background-color: #ffffff;
      padding: 0 1.75rem;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .nav-tabs {{
      display: flex;
      gap: 0.5rem;
    }}

    .tab-btn {{
      background: none;
      border: none;
      padding: 0.85rem 1.1rem;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--slate-600);
      cursor: pointer;
      position: relative;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s;
    }}

    .tab-btn:hover {{
      color: var(--navy-800);
    }}

    .tab-btn.active {{
      color: var(--navy-800);
    }}

    .tab-btn.active::after {{
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      right: 0;
      height: 3px;
      background-color: var(--crimson-600);
      border-radius: 3px 3px 0 0;
    }}

    .tab-count {{
      background-color: var(--slate-200);
      color: var(--slate-700);
      font-size: 0.7rem;
      padding: 0.1rem 0.45rem;
      border-radius: 9999px;
      font-weight: 700;
    }}

    .tab-count.alert {{
      background-color: var(--crimson-600);
      color: white;
    }}

    .tab-actions {{
      display: flex;
      gap: 0.5rem;
    }}

    /* Standard Button Styles */
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.5rem 0.9rem;
      border-radius: var(--radius-md);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .btn-primary {{
      background-color: var(--navy-800);
      color: #ffffff;
    }}
    .btn-primary:hover {{
      background-color: var(--navy-700);
      box-shadow: var(--shadow-sm);
    }}

    .btn-crimson {{
      background-color: var(--crimson-600);
      color: #ffffff;
    }}
    .btn-crimson:hover {{
      background-color: var(--crimson-700);
    }}

    .btn-secondary {{
      background-color: #ffffff;
      color: var(--slate-700);
      border-color: var(--slate-300);
    }}
    .btn-secondary:hover {{
      background-color: var(--slate-100);
    }}

    .btn-outline {{
      background: transparent;
      border-color: var(--slate-300);
      color: var(--slate-700);
    }}
    .btn-outline:hover {{
      background-color: var(--slate-100);
    }}

    .btn-sm {{
      padding: 0.25rem 0.55rem;
      font-size: 0.75rem;
    }}

    /* Main Content Container */
    main.main-content {{
      padding: 1.5rem 1.75rem;
      flex: 1;
      max-width: 1600px;
      width: 100%;
      margin: 0 auto;
    }}

    .view-panel {{
      display: none;
    }}
    .view-panel.active {{
      display: block;
    }}

    /* Controls & Filter Bar */
    .filter-bar {{
      background: #ffffff;
      padding: 0.85rem 1.25rem;
      border-radius: var(--radius-lg);
      border: 1px solid var(--slate-200);
      margin-bottom: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
      box-shadow: var(--shadow-sm);
    }}

    .filter-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .search-input-wrapper {{
      position: relative;
    }}

    .search-input {{
      padding: 0.45rem 0.75rem 0.45rem 2rem;
      font-size: 0.8rem;
      border: 1px solid var(--slate-300);
      border-radius: var(--radius-md);
      width: 220px;
      outline: none;
      transition: all 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--navy-600);
      box-shadow: 0 0 0 2px rgba(11, 37, 69, 0.1);
    }}

    .search-icon {{
      position: absolute;
      left: 0.65rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--slate-400);
      pointer-events: none;
    }}

    select.filter-select {{
      padding: 0.45rem 0.75rem;
      font-size: 0.8rem;
      border: 1px solid var(--slate-300);
      border-radius: var(--radius-md);
      background-color: #ffffff;
      color: var(--slate-700);
      outline: none;
      cursor: pointer;
    }}

    select.filter-select:focus {{
      border-color: var(--navy-600);
    }}

    /* Clean Card Layout */
    .card {{
      background: #ffffff;
      border-radius: var(--radius-lg);
      border: 1px solid var(--slate-200);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      margin-bottom: 1.5rem;
    }}

    .card-header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: #ffffff;
    }}

    .card-header h3 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--slate-900);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .card-body {{
      padding: 0;
      overflow-x: auto;
    }}

    /* Tables */
    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.82rem;
    }}

    table.data-table th {{
      background-color: var(--slate-50);
      color: var(--slate-600);
      font-weight: 600;
      padding: 0.65rem 1rem;
      border-bottom: 1px solid var(--slate-200);
      white-space: nowrap;
      text-transform: uppercase;
      font-size: 0.7rem;
      letter-spacing: 0.5px;
    }}

    table.data-table td {{
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--slate-200);
      color: var(--slate-800);
      vertical-align: middle;
    }}

    table.data-table tr:hover td {{
      background-color: #f8fafc;
    }}

    /* Badges & Indicators */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
      font-size: 0.72rem;
      font-weight: 700;
      white-space: nowrap;
    }}

    .badge-success {{
      background-color: var(--green-100);
      color: var(--green-700);
    }}
    .badge-warning {{
      background-color: var(--amber-100);
      color: var(--amber-600);
    }}
    .badge-danger {{
      background-color: var(--crimson-100);
      color: var(--crimson-600);
    }}
    .badge-neutral {{
      background-color: var(--slate-100);
      color: var(--slate-700);
    }}
    .badge-navy {{
      background-color: #e0f2fe;
      color: var(--navy-800);
    }}

    .variance-pill {{
      display: inline-flex;
      align-items: center;
      font-weight: 700;
      font-size: 0.8rem;
      padding: 0.15rem 0.5rem;
      border-radius: var(--radius-sm);
    }}

    .variance-zero {{
      background-color: var(--green-50);
      color: var(--green-700);
    }}
    .variance-negative {{
      background-color: var(--amber-50);
      color: var(--amber-600);
    }}
    .variance-positive {{
      background-color: var(--crimson-100);
      color: var(--crimson-600);
      font-weight: 800;
    }}

    /* Modals & Overlays */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background-color: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(3px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }}

    .modal-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-container {{
      background: #ffffff;
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow-xl);
      width: 90%;
      max-width: 650px;
      max-height: 90vh;
      overflow-y: auto;
      border: 1px solid var(--slate-200);
      transform: scale(0.95);
      transition: transform 0.2s ease;
    }}

    .modal-overlay.open .modal-container {{
      transform: scale(1);
    }}

    .modal-header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: var(--slate-50);
    }}

    .modal-header h3 {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--slate-900);
    }}

    .modal-close {{
      background: none;
      border: none;
      font-size: 1.25rem;
      color: var(--slate-400);
      cursor: pointer;
      line-height: 1;
    }}
    .modal-close:hover {{
      color: var(--slate-700);
    }}

    .modal-body {{
      padding: 1.5rem;
    }}

    .modal-footer {{
      padding: 1rem 1.5rem;
      border-top: 1px solid var(--slate-200);
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0.75rem;
      background-color: var(--slate-50);
    }}

    /* Form Styles */
    .form-group {{
      margin-bottom: 1rem;
    }}

    .form-label {{
      display: block;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--slate-700);
      margin-bottom: 0.35rem;
    }}

    .form-input, .form-select, .form-textarea {{
      width: 100%;
      padding: 0.5rem 0.75rem;
      font-size: 0.82rem;
      border: 1px solid var(--slate-300);
      border-radius: var(--radius-md);
      outline: none;
      transition: border-color 0.2s;
    }}

    .form-input:focus, .form-select:focus, .form-textarea:focus {{
      border-color: var(--navy-600);
      box-shadow: 0 0 0 2px rgba(11, 37, 69, 0.1);
    }}

    .form-textarea {{
      min-height: 70px;
      resize: vertical;
    }}

    .form-help {{
      font-size: 0.72rem;
      color: var(--slate-500);
      margin-top: 0.25rem;
    }}

    /* Prominent Validation & Override Callout Box */
    .validation-alert-box {{
      background-color: #fef2f2;
      border: 1.5px solid #f87171;
      border-radius: var(--radius-md);
      padding: 1rem;
      margin-bottom: 1rem;
      display: none;
    }}

    .validation-alert-box.show {{
      display: block;
      animation: shake 0.3s ease-in-out;
    }}

    @keyframes shake {{
      0%, 100% {{ transform: translateX(0); }}
      25% {{ transform: translateX(-4px); }}
      75% {{ transform: translateX(4px); }}
    }}

    .validation-alert-header {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--crimson-700);
      font-weight: 700;
      font-size: 0.85rem;
      margin-bottom: 0.4rem;
    }}

    .validation-alert-text {{
      font-size: 0.8rem;
      color: #991b1b;
      margin-bottom: 0.75rem;
      line-height: 1.4;
    }}

    .override-checkbox-wrap {{
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
      background: #ffffff;
      padding: 0.6rem 0.75rem;
      border-radius: var(--radius-sm);
      border: 1px solid #fca5a5;
    }}

    .override-checkbox-wrap input {{
      margin-top: 0.2rem;
      cursor: pointer;
    }}

    .override-checkbox-wrap label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--crimson-700);
      cursor: pointer;
    }}

    /* Drilldown Drawer for Campus Details */
    .drawer-overlay {{
      position: fixed;
      inset: 0;
      background-color: rgba(15, 23, 42, 0.5);
      z-index: 900;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }}
    .drawer-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .drawer-container {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 100%;
      max-width: 600px;
      background: #ffffff;
      box-shadow: var(--shadow-xl);
      z-index: 950;
      transform: translateX(100%);
      transition: transform 0.25s ease;
      display: flex;
      flex-direction: column;
    }}
    .drawer-overlay.open .drawer-container {{
      transform: translateX(0);
    }}

    .drawer-header {{
      background-color: var(--navy-900);
      color: white;
      padding: 1.25rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .drawer-header h3 {{
      font-size: 1.05rem;
      font-weight: 700;
    }}
    .drawer-body {{
      padding: 1.25rem;
      overflow-y: auto;
      flex: 1;
    }}

    /* Notification Toast */
    .toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background-color: var(--slate-900);
      color: white;
      padding: 0.75rem 1.25rem;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      font-size: 0.82rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      z-index: 2000;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s ease;
    }}
    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}
    .toast.toast-success {{ background-color: var(--green-700); }}
    .toast.toast-danger {{ background-color: var(--crimson-700); }}
  </style>
</head>
<body>

  <!-- Brand Navigation with Official SST Logo -->
  <header class="brand-nav">
    <div class="brand-left">
      <div class="brand-logo-card">
        <img src="{LOGO_DATA_URI}" alt="School of Science and Technology Logo">
      </div>
      <div class="brand-titles">
        <h1>
          School of Science &amp; Technology
          <span class="brand-motto">&mdash; Better Education, Better Future</span>
        </h1>
        <p class="brand-subtitle">Campus FTE Staffing &amp; Budget Planning Portal &bull; Texas Charter Network (21 Campuses)</p>
      </div>
    </div>
    <div class="brand-right">
      <div class="mode-pill-container">
        <button class="mode-btn active" id="btn-mode-editor" onclick="switchViewMode('editor')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          Editor (My View)
        </button>
        <button class="mode-btn" id="btn-mode-leadership" onclick="switchViewMode('leadership')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12h20"/><path d="M20 12v8H4v-8"/><path d="M4 12V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6"/></svg>
          Leadership View (Read-Only)
        </button>
      </div>

      <div class="user-profile-selector-wrap">
        <div class="user-badge" style="cursor: pointer; gap: 0.65rem;">
          <div class="user-avatar" id="avatar-initials">AD</div>
          <div style="display:flex; flex-direction:column; text-align:left;">
            <span id="display-user-name" style="font-weight:700; font-size:0.78rem; line-height:1.2; color:#ffffff;">Ali Dal</span>
            <span id="display-user-role" style="font-size:0.68rem; color:#93c5fd;">Regional Talent Acquisition &bull; Editor</span>
            <span id="display-user-email" style="display:none;">adal@ssttx.org</span>
          </div>
          <select id="select-active-user" onchange="changeActiveUserProfile(this.value)" class="user-switch-select" title="Switch Active User Profile">
            <option value="adal@ssttx.org|Ali Dal|Regional Talent Acquisition|editor" selected>Ali Dal (adal@ssttx.org) - Regional Talent Acquisition</option>
            <option value="hkendirci@ssttx.org|Hasan Kendirci|Regional Talent Acquisition|editor">Hasan Kendirci (hkendirci@ssttx.org) - Regional Talent Acquisition</option>
            <option value="admin@ssttx.org|FTE Administrator|Central Office FTE Planner|editor">FTE Planning Administrator</option>
            <option value="superintendent@ssttx.org|Executive Leadership|Superintendent &amp; Board|leadership">Leadership View (Read-Only)</option>
          </select>
        </div>
      </div>
    </div>
  </header>

  <!-- Leadership Mode Banner -->
  <div id="leadership-banner" class="hidden">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
      <span class="banner-badge">Leadership View</span>
      <span>Viewing approved vs. actual FTE allocations and network compliance across all 21 campuses. Editing is disabled.</span>
    </div>
    <span style="font-size: 0.75rem; color: #94a3b8;">SST Board &amp; Executive Level Access</span>
  </div>

  <!-- KPI Top Metrics Bar -->
  <section class="kpi-section">
    <div class="kpi-card kpi-approved">
      <span class="kpi-label">Approved Plan FTE</span>
      <span class="kpi-value" id="kpi-approved-total">1,359.0</span>
      <span class="kpi-sub">Approved baseline budget across all campuses</span>
    </div>
    <div class="kpi-card kpi-filled">
      <span class="kpi-label">Active / Live Filled</span>
      <span class="kpi-value" id="kpi-filled-total">1,336.0</span>
      <span class="kpi-sub" style="color: var(--green-700); font-weight: 600;">98.3% staffing fill rate</span>
    </div>
    <div class="kpi-card kpi-vacant">
      <span class="kpi-label">Approved Vacancies</span>
      <span class="kpi-value" id="kpi-vacant-total">23.0</span>
      <span class="kpi-sub" style="color: var(--amber-600); font-weight: 600;">Open approved positions to hire</span>
    </div>
    <div class="kpi-card kpi-violation">
      <span class="kpi-label">Violations / Overrides</span>
      <span class="kpi-value" id="kpi-violation-total">0</span>
      <span class="kpi-sub" id="kpi-violation-sub" style="color: var(--green-700);">No unapproved staffing flags</span>
    </div>
  </section>

  <!-- Tabs Navigation Bar -->
  <div class="tab-bar-container">
    <nav class="nav-tabs">
      <button class="tab-btn active" id="tab-btn-leadership" onclick="switchTab('leadership')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
        Leadership Dashboard
      </button>
      <button class="tab-btn" id="tab-btn-matrix" onclick="switchTab('matrix')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        FTE Plan &amp; Headcount Matrix
        <span class="tab-count" id="badge-matrix-count">576</span>
      </button>
      <button class="tab-btn" id="tab-btn-roster" onclick="switchTab('roster')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        Staff &amp; Hires Roster
        <span class="tab-count" id="badge-roster-count">1,359</span>
      </button>
      <button class="tab-btn" id="tab-btn-violations" onclick="switchTab('violations')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Violations &amp; Overrides Hub
        <span class="tab-count" id="badge-violations-count">0</span>
      </button>
      <button class="tab-btn" id="tab-btn-audit" onclick="switchTab('audit')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        Unfalsifiable Audit Trail
      </button>
    </nav>

    <div class="tab-actions">
      <button class="btn btn-crimson editor-only" onclick="openLogHireModal()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Log New Hire
      </button>
      <button class="btn btn-primary editor-only" onclick="openAddRoleModal()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
        Approve New Role
      </button>
    </div>
  </div>

  <!-- Main Content Area -->
  <main class="main-content">

    <!-- TAB 1: LEADERSHIP DASHBOARD -->
    <div class="view-panel active" id="view-leadership">
      <div class="filter-bar">
        <div class="filter-group">
          <div class="search-input-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" class="search-input" id="search-leadership" placeholder="Search campus or region..." oninput="renderLeadershipView()">
          </div>
          <select class="filter-select" id="filter-leadership-region" onchange="renderLeadershipView()">
            <option value="ALL">All Regions (Houston, SA, CC)</option>
            <option value="San Antonio">San Antonio Region</option>
            <option value="Houston">Houston Region</option>
            <option value="Corpus Christi">Corpus Christi Region</option>
          </select>
          <select class="filter-select" id="filter-leadership-variance" onchange="renderLeadershipView()">
            <option value="ALL">All Campus Statuses</option>
            <option value="BALANCED">Balanced / Fully Staffed</option>
            <option value="VACANCY">Has Open Vacancies</option>
            <option value="VIOLATION">Has Violations / Over-FTE</option>
          </select>
        </div>
        <div style="font-size: 0.78rem; color: var(--slate-500);">
          Click any campus row to inspect full role-by-role staffing breakdown.
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            SST Network Campus FTE Summary Rollup (All 21 Campuses)
          </h3>
          <span class="badge badge-navy" id="leadership-table-count">22 Campuses Loaded</span>
        </div>
        <div class="card-body">
          <table class="data-table" id="table-leadership">
            <thead>
              <tr>
                <th>Campus Name</th>
                <th>Region</th>
                <th>Grades</th>
                <th style="text-align: right;">Approved FTE</th>
                <th style="text-align: right;">Live Filled</th>
                <th style="text-align: right;">Vacancies</th>
                <th style="text-align: center;">Variance</th>
                <th style="text-align: center;">Staffing Fill %</th>
                <th style="text-align: center;">Violations</th>
                <th style="text-align: center;">Action</th>
              </tr>
            </thead>
            <tbody id="tbody-leadership">
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: FTE PLAN & HEADCOUNT MATRIX -->
    <div class="view-panel" id="view-matrix">
      <div class="filter-bar">
        <div class="filter-group">
          <div class="search-input-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" class="search-input" id="search-matrix" placeholder="Search role or campus..." oninput="renderMatrixView()">
          </div>
          <select class="filter-select" id="filter-matrix-campus" onchange="renderMatrixView()">
            <option value="ALL">All Campuses</option>
          </select>
          <select class="filter-select" id="filter-matrix-category" onchange="renderMatrixView()">
            <option value="ALL">All Categories</option>
            <option value="Leadership & Administration">Leadership & Administration</option>
            <option value="Core Instruction">Core Instruction</option>
            <option value="Specialized Instruction">Specialized Instruction</option>
            <option value="Paraprofessional & Instructional Support">Paraprofessionals & Aides</option>
            <option value="Operations & Student Support">Operations & Support</option>
            <option value="Professional Support">Instructional Coordinators</option>
          </select>
          <select class="filter-select" id="filter-matrix-variance" onchange="renderMatrixView()">
            <option value="ALL">All Variance Types</option>
            <option value="EXCEEDED">Over-FTE Violations (Actual &gt; Approved)</option>
            <option value="VACANT">Open Vacancies (Actual &lt; Approved)</option>
            <option value="BALANCED">Balanced (Actual == Approved)</option>
          </select>
        </div>
        <div style="font-size: 0.78rem; color: var(--slate-500);" id="matrix-status-text">
          Showing 576 campus + role allocations
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>
            Approved Plan vs. Actual Hires Side-by-Side Comparison
          </h3>
          <span class="badge badge-neutral">Baseline Protected Data</span>
        </div>
        <div class="card-body">
          <table class="data-table" id="table-matrix">
            <thead>
              <tr>
                <th>Campus</th>
                <th>Role Title</th>
                <th>Category</th>
                <th style="text-align: right;">Approved FTE</th>
                <th style="text-align: right;">Actual Filled</th>
                <th style="text-align: right;">Vacant Slots</th>
                <th style="text-align: center;">Variance</th>
                <th style="text-align: center;">Status</th>
                <th style="text-align: center;">Last Revised</th>
                <th style="text-align: center;" class="editor-col">Plan Actions</th>
              </tr>
            </thead>
            <tbody id="tbody-matrix">
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: STAFF & HIRES ROSTER -->
    <div class="view-panel" id="view-roster">
      <div class="filter-bar">
        <div class="filter-group">
          <div class="search-input-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" class="search-input" id="search-roster" placeholder="Search staff name or role..." oninput="renderRosterView()">
          </div>
          <select class="filter-select" id="filter-roster-campus" onchange="renderRosterView()">
            <option value="ALL">All Campuses</option>
          </select>
          <select class="filter-select" id="filter-roster-status" onchange="renderRosterView()">
            <option value="ALL">All Positions (Filled &amp; Vacant)</option>
            <option value="Filled">Filled Positions</option>
            <option value="Vacant">Approved Open Vacancies</option>
          </select>
        </div>
        <div>
          <button class="btn btn-crimson editor-only" onclick="openLogHireModal()">
            + Log New Hire
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            Active Campus Staffing &amp; Live Hires Roster
          </h3>
          <span class="badge badge-neutral" id="roster-count-badge">1,359 Roster Records</span>
        </div>
        <div class="card-body">
          <table class="data-table" id="table-roster">
            <thead>
              <tr>
                <th>Hire ID</th>
                <th>Campus</th>
                <th>Standard Role</th>
                <th>Employee Name</th>
                <th>Assignment / Details</th>
                <th style="text-align: center;">FTE</th>
                <th style="text-align: center;">Status</th>
                <th>Position ID</th>
                <th>Hire Date</th>
                <th style="text-align: center;">Override</th>
                <th style="text-align: center;" class="editor-col">Actions</th>
              </tr>
            </thead>
            <tbody id="tbody-roster">
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: VIOLATIONS & OVERRIDES HUB -->
    <div class="view-panel" id="view-violations">
      <div class="filter-bar">
        <div class="filter-group">
          <div class="search-input-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" class="search-input" id="search-violations" placeholder="Search violations..." oninput="renderViolationsView()">
          </div>
          <select class="filter-select" id="filter-violations-status" onchange="renderViolationsView()">
            <option value="ALL">All Violations (Active &amp; Overridden)</option>
            <option value="OVERRIDDEN">Approved Overrides</option>
            <option value="PENDING">Pending Flags</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
        <div style="font-size: 0.78rem; color: var(--slate-600);">
          Every unauthorized hire or over-FTE exception is tracked here permanently.
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Campus Staffing Violations &amp; Administrative Overrides Log
          </h3>
          <span class="badge badge-danger" id="violations-count-badge">0 Active Flags</span>
        </div>
        <div class="card-body">
          <table class="data-table" id="table-violations">
            <thead>
              <tr>
                <th>Violation ID</th>
                <th>Campus</th>
                <th>Role Title</th>
                <th>Violation Type</th>
                <th style="text-align: right;">Approved</th>
                <th style="text-align: right;">Actual</th>
                <th style="text-align: center;">Variance</th>
                <th>Employee Name</th>
                <th style="text-align: center;">Status</th>
                <th>Mandatory Justification Note</th>
                <th>Logged Date &amp; User</th>
                <th style="text-align: center;" class="editor-col">Action</th>
              </tr>
            </thead>
            <tbody id="tbody-violations">
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 5: AUDIT TRAIL -->
    <div class="view-panel" id="view-audit">
      <div class="filter-bar">
        <div class="filter-group">
          <div class="search-input-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" class="search-input" id="search-audit" placeholder="Search audit trail..." oninput="renderAuditView()">
          </div>
          <select class="filter-select" id="filter-audit-campus" onchange="renderAuditView()">
            <option value="ALL">All Campuses</option>
          </select>
          <select class="filter-select" id="filter-audit-action" onchange="renderAuditView()">
            <option value="ALL">All Action Types</option>
            <option value="PLAN_REVISION">PLAN_REVISION</option>
            <option value="HIRE_LOGGED">HIRE_LOGGED</option>
            <option value="HIRE_WITH_OVERRIDE">HIRE_WITH_OVERRIDE</option>
            <option value="HIRE_REMOVED">HIRE_REMOVED</option>
            <option value="APPROVED_ROLE_ADDED">APPROVED_ROLE_ADDED</option>
            <option value="VIOLATION_RESOLVED">VIOLATION_RESOLVED</option>
            <option value="MIGRATION_INITIALIZED">MIGRATION_INITIALIZED</option>
          </select>
        </div>
        <div>
          <button class="btn btn-outline btn-sm" onclick="exportAuditToCSV()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Export Audit to CSV
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Permanent Unfalsifiable Audit Trail (Tamper-Proof)
          </h3>
          <span class="badge badge-success">Cryptographically Logged &amp; Verified</span>
        </div>
        <div class="card-body">
          <table class="data-table" id="table-audit">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Exact Timestamp (CST)</th>
                <th>User Account</th>
                <th>Action Type</th>
                <th>Campus</th>
                <th>Role</th>
                <th>Previous Value</th>
                <th>New Value</th>
                <th>Reason / Justification Note</th>
                <th style="text-align: center;">Override</th>
              </tr>
            </thead>
            <tbody id="tbody-audit">
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </main>

  <!-- MODAL: REVISE APPROVED PLAN -->
  <div class="modal-overlay" id="modal-revise-plan">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Revise Approved Staffing Plan</h3>
        <button class="modal-close" onclick="closeModal('modal-revise-plan')">&times;</button>
      </div>
      <div class="modal-body">
        <p style="font-size: 0.8rem; color: var(--slate-600); margin-bottom: 1rem;">
          Baseline Approved FTEs can only be modified through a formal budget revision. This action is recorded permanently in the audit trail.
        </p>
        <div class="form-group">
          <label class="form-label">Campus</label>
          <input type="text" class="form-input" id="revise-campus" readonly style="background-color: var(--slate-100);">
        </div>
        <div class="form-group">
          <label class="form-label">Role Title</label>
          <input type="text" class="form-input" id="revise-role" readonly style="background-color: var(--slate-100);">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Current Approved FTE</label>
            <input type="text" class="form-input" id="revise-current-fte" readonly style="background-color: var(--slate-100);">
          </div>
          <div class="form-group">
            <label class="form-label">New Approved FTE Count</label>
            <input type="number" step="0.25" min="0" max="99" class="form-input" id="revise-new-fte" placeholder="e.g. 4.0">
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Revision Reason / Budget Approval Justification <span style="color: red;">*</span></label>
          <textarea class="form-textarea" id="revise-reason" placeholder="State the board amendment, grant funding, or enrollment justification for this plan change..."></textarea>
          <span class="form-help">Mandatory: Casual edits are blocked. All revisions are logged with your user identity.</span>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeModal('modal-revise-plan')">Cancel</button>
        <button class="btn btn-primary" onclick="submitPlanRevision()">Confirm &amp; Record Plan Revision</button>
      </div>
    </div>
  </div>

  <!-- MODAL: LOG NEW HIRE -->
  <div class="modal-overlay" id="modal-log-hire">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Log Campus Staff Hire</h3>
        <button class="modal-close" onclick="closeModal('modal-log-hire')">&times;</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Campus <span style="color: red;">*</span></label>
          <select class="form-select" id="hire-campus" onchange="checkHireValidation()">
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Role Title <span style="color: red;">*</span></label>
          <select class="form-select" id="hire-role" onchange="checkHireValidation()">
          </select>
        </div>

        <!-- Real-Time Validation Alert Box -->
        <div class="validation-alert-box" id="hire-validation-box">
          <div class="validation-alert-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span id="val-alert-title">STAFFING VIOLATION DETECTED</span>
          </div>
          <p class="validation-alert-text" id="val-alert-msg">
            This hire will exceed the approved FTE plan for this campus!
          </p>
          <div class="override-checkbox-wrap">
            <input type="checkbox" id="check-override" onchange="toggleOverrideJustification()">
            <label for="check-override">Grant Explicit Administrative Override for this Unapproved Hire</label>
          </div>
          <div class="form-group" id="override-reason-group" style="margin-top: 0.75rem; display: none;">
            <label class="form-label" style="color: var(--crimson-700);">Override Justification Reason <span style="color: red;">*</span></label>
            <textarea class="form-textarea" id="hire-override-reason" placeholder="Document why this unauthorized hire or over-FTE role must be approved (e.g. emergency SPED student transfer, board variance)..."></textarea>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Employee Full Name <span style="color: red;">*</span></label>
            <input type="text" class="form-input" id="hire-name" placeholder="e.g. Maria Hernandez">
          </div>
          <div class="form-group">
            <label class="form-label">Position ID</label>
            <input type="text" class="form-input" id="hire-pos-id" placeholder="e.g. ELA110820">
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Assignment / Grade / Section</label>
            <input type="text" class="form-input" id="hire-assignment" placeholder="e.g. 5th Math (3 Sections)">
          </div>
          <div class="form-group">
            <label class="form-label">FTE Value</label>
            <input type="number" step="0.1" min="0.1" max="1.0" class="form-input" id="hire-fte" value="1.0" onchange="checkHireValidation()">
          </div>
          <div class="form-group">
            <label class="form-label">Status</label>
            <select class="form-select" id="hire-status">
              <option value="Filled">Filled (Hired)</option>
              <option value="Vacant">Vacant (Slot)</option>
            </select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeModal('modal-log-hire')">Cancel</button>
        <button class="btn btn-crimson" id="btn-submit-hire" onclick="submitHire()">Save Staff Hire</button>
      </div>
    </div>
  </div>

  <!-- MODAL: ADD APPROVED ROLE -->
  <div class="modal-overlay" id="modal-add-role">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Approve New Role for Campus</h3>
        <button class="modal-close" onclick="closeModal('modal-add-role')">&times;</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Campus <span style="color: red;">*</span></label>
          <select class="form-select" id="addrole-campus">
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Role Title <span style="color: red;">*</span></label>
          <input type="text" class="form-input" id="addrole-name" placeholder="e.g. Counselor, Robotics Teacher, Interventionist">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Category</label>
            <select class="form-select" id="addrole-category">
              <option value="Leadership & Administration">Leadership & Administration</option>
              <option value="Core Instruction">Core Instruction</option>
              <option value="Specialized Instruction">Specialized Instruction</option>
              <option value="Paraprofessional & Instructional Support">Paraprofessionals & Aides</option>
              <option value="Operations & Student Support">Operations & Support</option>
              <option value="Professional Support">Professional Support</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Initial Approved FTE Count <span style="color: red;">*</span></label>
            <input type="number" step="0.25" min="0.25" max="99" class="form-input" id="addrole-fte" value="1.0">
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Budget Authorization Reason <span style="color: red;">*</span></label>
          <textarea class="form-textarea" id="addrole-reason" placeholder="Document board authorization or budget amendment allowing this new role..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeModal('modal-add-role')">Cancel</button>
        <button class="btn btn-primary" onclick="submitAddRole()">Authorize &amp; Add Approved Role</button>
      </div>
    </div>
  </div>

  <!-- CAMPUS DRILLDOWN DRAWER -->
  <div class="drawer-overlay" id="drawer-campus" onclick="if(event.target===this) closeDrawer()">
    <div class="drawer-container">
      <div class="drawer-header">
        <div>
          <h3 id="drawer-campus-name">SST Campus Details</h3>
          <p id="drawer-campus-sub" style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">Campus Staffing Breakdown</p>
        </div>
        <button style="background:none; border:none; color:white; font-size:1.5rem; cursor:pointer;" onclick="closeDrawer()">&times;</button>
      </div>
      <div class="drawer-body">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1.25rem;">
          <div style="background: var(--slate-50); border:1px solid var(--slate-200); padding:0.6rem; border-radius: var(--radius-sm); text-align:center;">
            <div style="font-size:0.7rem; color:var(--slate-500); text-transform:uppercase;">Approved</div>
            <div style="font-size:1.3rem; font-weight:800; color:var(--navy-900);" id="drawer-approved">0</div>
          </div>
          <div style="background: var(--slate-50); border:1px solid var(--slate-200); padding:0.6rem; border-radius: var(--radius-sm); text-align:center;">
            <div style="font-size:0.7rem; color:var(--slate-500); text-transform:uppercase;">Filled</div>
            <div style="font-size:1.3rem; font-weight:800; color:var(--green-700);" id="drawer-filled">0</div>
          </div>
          <div style="background: var(--slate-50); border:1px solid var(--slate-200); padding:0.6rem; border-radius: var(--radius-sm); text-align:center;">
            <div style="font-size:0.7rem; color:var(--slate-500); text-transform:uppercase;">Vacant</div>
            <div style="font-size:1.3rem; font-weight:800; color:var(--amber-600);" id="drawer-vacant">0</div>
          </div>
        </div>

        <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--slate-800); margin-bottom: 0.5rem;">Role-by-Role Allocations</h4>
        <table class="data-table">
          <thead>
            <tr>
              <th>Role</th>
              <th style="text-align: right;">Appr</th>
              <th style="text-align: right;">Live</th>
              <th style="text-align: center;">Variance</th>
            </tr>
          </thead>
          <tbody id="drawer-tbody">
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Notification Toast -->
  <div class="toast" id="app-toast">Notification message</div>

  <!-- Embed Migrated Database -->
  <script>
    const INITIAL_DB = __INITIAL_DB_PLACEHOLDER__;
  </script>

  <!-- Application Logic -->
  <script>
    let DB = JSON.parse(JSON.stringify(INITIAL_DB));
    let currentMode = "editor";
    let currentTab = "leadership";
    let currentUserEmail = "adal@ssttx.org";

    window.addEventListener("DOMContentLoaded", () => {{
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("view") === "leadership" || urlParams.get("mode") === "leadership") {{
        currentMode = "leadership";
      }}

      if (typeof google !== "undefined" && google.script && google.script.run) {{
        google.script.run
          .withSuccessHandler((res) => {{
            if (res && res.status === "OK") {{
              DB = res;
              if (res.currentUser) currentUserEmail = res.currentUser;
              initializeApp();
            }}
          }})
          .withFailureHandler((err) => {{
            console.warn("GAS live fetch failed, using local DB:", err);
            initializeApp();
          }})
          .getAppInitialData();
      }} else {{
        initializeApp();
      }}
    }});


    function changeActiveUserProfile(valStr) {{
      const parts = valStr.split('|');
      const email = parts[0];
      const name = parts[1];
      const title = parts[2];
      const mode = parts[3];

      currentUserEmail = email;
      const emailEl = document.getElementById('display-user-email');
      if (emailEl) emailEl.textContent = email;
      const nameEl = document.getElementById('display-user-name');
      if (nameEl) nameEl.textContent = name;
      const roleEl = document.getElementById('display-user-role');
      if (roleEl) roleEl.innerHTML = title + (mode === 'editor' ? ' &bull; Editor' : ' &bull; Read-Only');
      const avatarEl = document.getElementById('avatar-initials');
      if (avatarEl) {{
        avatarEl.textContent = name.split(' ').map(function(n) {{ return n[0]; }}).join('').substring(0, 2).toUpperCase();
      }}

      if (mode === 'leadership') {{
        switchViewMode('leadership');
      }} else {{
        switchViewMode('editor');
      }}
      showToast('Switched user to ' + name + ' (' + email + ')', 'success');
    }}

    function initializeApp() {{
      const emailEl = document.getElementById("display-user-email");
      if (emailEl) emailEl.textContent = currentUserEmail;
      
      const selectUser = document.getElementById("select-active-user");
      const lower = currentUserEmail.toLowerCase();
      if (lower === "adal@ssttx.org") {{
        const nameEl = document.getElementById("display-user-name");
        if (nameEl) nameEl.textContent = "Ali Dal";
        const roleEl = document.getElementById("display-user-role");
        if (roleEl) roleEl.innerHTML = "Regional Talent Acquisition &bull; Editor";
        const avatarEl = document.getElementById("avatar-initials");
        if (avatarEl) avatarEl.textContent = "AD";
        if (selectUser) selectUser.value = "adal@ssttx.org|Ali Dal|Regional Talent Acquisition|editor";
      }} else if (lower === "hkendirci@ssttx.org") {{
        const nameEl = document.getElementById("display-user-name");
        if (nameEl) nameEl.textContent = "Hasan Kendirci";
        const roleEl = document.getElementById("display-user-role");
        if (roleEl) roleEl.innerHTML = "Regional Talent Acquisition &bull; Editor";
        const avatarEl = document.getElementById("avatar-initials");
        if (avatarEl) avatarEl.textContent = "HK";
        if (selectUser) selectUser.value = "hkendirci@ssttx.org|Hasan Kendirci|Regional Talent Acquisition|editor";
      }} else {{
        const initials = currentUserEmail.split("@")[0].substring(0, 2).toUpperCase();
        const avatarEl = document.getElementById("avatar-initials");
        if (avatarEl) avatarEl.textContent = initials;
      }}

      populateFilterDropdowns();
      updateKPICards();
      switchViewMode(currentMode);
      switchTab(currentTab);
    }}

    function switchViewMode(mode) {{
      currentMode = mode;
      const btnEditor = document.getElementById("btn-mode-editor");
      const btnLeader = document.getElementById("btn-mode-leadership");
      const banner = document.getElementById("leadership-banner");
      const editorCols = document.querySelectorAll(".editor-col");
      const editorOnly = document.querySelectorAll(".editor-only");

      if (mode === "leadership") {{
        btnLeader.classList.add("active");
        btnEditor.classList.remove("active");
        banner.classList.remove("hidden");
        editorCols.forEach(el => el.style.display = "none");
        editorOnly.forEach(el => el.style.display = "none");
      }} else {{
        btnEditor.classList.add("active");
        btnLeader.classList.remove("active");
        banner.classList.add("hidden");
        editorCols.forEach(el => el.style.display = "");
        editorOnly.forEach(el => el.style.display = "");
      }}

      if (currentTab === "leadership") renderLeadershipView();
      if (currentTab === "matrix") renderMatrixView();
      if (currentTab === "roster") renderRosterView();
      if (currentTab === "violations") renderViolationsView();
      if (currentTab === "audit") renderAuditView();
    }}

    function switchTab(tabId) {{
      currentTab = tabId;
      document.querySelectorAll(".nav-tabs .tab-btn").forEach(btn => btn.classList.remove("active"));
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));

      const btn = document.getElementById("tab-btn-" + tabId);
      const panel = document.getElementById("view-" + tabId);
      if (btn) btn.classList.add("active");
      if (panel) panel.classList.add("active");

      if (tabId === "leadership") renderLeadershipView();
      if (tabId === "matrix") renderMatrixView();
      if (tabId === "roster") renderRosterView();
      if (tabId === "violations") renderViolationsView();
      if (tabId === "audit") renderAuditView();
    }}

    function updateKPICards() {{
      let totalApp = 0, totalFilled = 0, totalVacant = 0;
      DB.campuses.forEach(c => {{
        totalApp += parseFloat(c.approved_fte) || 0;
        totalFilled += parseFloat(c.actual_fte) || 0;
        totalVacant += parseFloat(c.vacant_fte) || 0;
      }});

      const openViolations = DB.violations.filter(v => v.status !== "RESOLVED").length;

      document.getElementById("kpi-approved-total").textContent = totalApp.toLocaleString("en-US", {{minimumFractionDigits: 1, maximumFractionDigits: 1}});
      document.getElementById("kpi-filled-total").textContent = totalFilled.toLocaleString("en-US", {{minimumFractionDigits: 1, maximumFractionDigits: 1}});
      document.getElementById("kpi-vacant-total").textContent = totalVacant.toLocaleString("en-US", {{minimumFractionDigits: 1, maximumFractionDigits: 1}});
      document.getElementById("kpi-violation-total").textContent = openViolations;

      const sub = document.getElementById("kpi-violation-sub");
      if (openViolations > 0) {{
        sub.textContent = openViolations + " campus FTE flags require review";
        sub.style.color = "var(--crimson-600)";
        sub.style.fontWeight = "700";
      }} else {{
        sub.textContent = "No unapproved staffing flags";
        sub.style.color = "var(--green-700)";
      }}

      document.getElementById("badge-matrix-count").textContent = DB.approved_plan.length;
      document.getElementById("badge-roster-count").textContent = DB.actual_hires.length;
      const vBadge = document.getElementById("badge-violations-count");
      vBadge.textContent = openViolations;
      if (openViolations > 0) vBadge.classList.add("alert");
      else vBadge.classList.remove("alert");
    }}

    function populateFilterDropdowns() {{
      const campusNames = DB.campuses.map(c => c.campus).sort();
      const matrixSelect = document.getElementById("filter-matrix-campus");
      const rosterSelect = document.getElementById("filter-roster-campus");
      const auditSelect = document.getElementById("filter-audit-campus");
      const hireSelect = document.getElementById("hire-campus");
      const addRoleSelect = document.getElementById("addrole-campus");

      campusNames.forEach(c => {{
        matrixSelect.innerHTML += `<option value="${{c}}">${{c}}</option>`;
        rosterSelect.innerHTML += `<option value="${{c}}">${{c}}</option>`;
        auditSelect.innerHTML += `<option value="${{c}}">${{c}}</option>`;
        hireSelect.innerHTML += `<option value="${{c}}">${{c}}</option>`;
        addRoleSelect.innerHTML += `<option value="${{c}}">${{c}}</option>`;
      }});

      populateRoleDropdownForCampus(campusNames[0]);
    }}

    function populateRoleDropdownForCampus(campus) {{
      const hireRoleSelect = document.getElementById("hire-role");
      const approvedRoles = DB.approved_plan
        .filter(p => p.campus === campus)
        .map(p => p.role)
        .sort();

      hireRoleSelect.innerHTML = "";
      approvedRoles.forEach(r => {{
        hireRoleSelect.innerHTML += `<option value="${{r}}">${{r}}</option>`;
      }});
      hireRoleSelect.innerHTML += `<option value="__NEW_UNAPPROVED__">+ Enter Unapproved Role...</option>`;
    }}

    function renderLeadershipView() {{
      const search = (document.getElementById("search-leadership").value || "").toLowerCase();
      const region = document.getElementById("filter-leadership-region").value;
      const varFilter = document.getElementById("filter-leadership-variance").value;

      const tbody = document.getElementById("tbody-leadership");
      tbody.innerHTML = "";

      let filtered = DB.campuses.filter(c => {{
        if (search && !c.campus.toLowerCase().includes(search) && !c.region.toLowerCase().includes(search)) return false;
        if (region !== "ALL" && c.region !== region) return false;
        if (varFilter === "BALANCED" && c.variance !== 0) return false;
        if (varFilter === "VACANCY" && c.vacant_fte <= 0) return false;
        if (varFilter === "VIOLATION" && c.violations_count <= 0 && c.variance <= 0) return false;
        return true;
      }});

      document.getElementById("leadership-table-count").textContent = filtered.length + " Campuses Displayed";

      filtered.forEach(c => {{
        const fillRate = c.approved_fte > 0 ? Math.round((c.actual_fte / c.approved_fte) * 100) : 100;
        
        let varClass = "variance-zero";
        let varSign = "";
        if (c.variance < 0) {{
          varClass = "variance-negative";
        }} else if (c.variance > 0) {{
          varClass = "variance-positive";
          varSign = "+";
        }}

        const violsBadge = c.violations_count > 0 
          ? `<span class="badge badge-danger">${{c.violations_count}} Flag</span>`
          : `<span class="badge badge-success">Clean</span>`;

        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.onclick = (e) => {{
          if (e.target.tagName !== "BUTTON") openCampusDrawer(c.campus);
        }};

        tr.innerHTML = `
          <td><strong>${{c.campus}}</strong></td>
          <td><span class="badge badge-neutral">${{c.region}}</span></td>
          <td style="color: var(--slate-600);">${{c.grades}}</td>
          <td style="text-align: right; font-weight: 700;">${{c.approved_fte.toFixed(1)}}</td>
          <td style="text-align: right; color: var(--green-700); font-weight: 700;">${{c.actual_fte.toFixed(1)}}</td>
          <td style="text-align: right; color: var(--amber-600); font-weight: 700;">${{c.vacant_fte.toFixed(1)}}</td>
          <td style="text-align: center;"><span class="variance-pill ${{varClass}}">${{varSign}}${{c.variance.toFixed(1)}}</span></td>
          <td style="text-align: center;">
            <div style="display:flex; align-items:center; gap:0.4rem; justify-content:center;">
              <span style="font-weight:600; font-size:0.75rem;">${{fillRate}}%</span>
              <div style="width:50px; height:6px; background:#e2e8f0; border-radius:3px; overflow:hidden;">
                <div style="width:${{Math.min(fillRate, 100)}}%; height:100%; background:var(--green-600);"></div>
              </div>
            </div>
          </td>
          <td style="text-align: center;">${{violsBadge}}</td>
          <td style="text-align: center;">
            <button class="btn btn-outline btn-sm" onclick="openCampusDrawer('${{c.campus}}')">Inspect</button>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderMatrixView() {{
      const search = (document.getElementById("search-matrix").value || "").toLowerCase();
      const campus = document.getElementById("filter-matrix-campus").value;
      const category = document.getElementById("filter-matrix-category").value;
      const varFilter = document.getElementById("filter-matrix-variance").value;

      const filledMap = {{}};
      const vacantMap = {{}};
      DB.actual_hires.forEach(h => {{
        const key = h.campus + "||" + h.role;
        if (h.status === "Filled") filledMap[key] = (filledMap[key] || 0) + (parseFloat(h.fte) || 1.0);
        if (h.status === "Vacant") vacantMap[key] = (vacantMap[key] || 0) + (parseFloat(h.fte) || 1.0);
      }});

      const tbody = document.getElementById("tbody-matrix");
      tbody.innerHTML = "";

      let filtered = DB.approved_plan.filter(p => {{
        if (search && !p.campus.toLowerCase().includes(search) && !p.role.toLowerCase().includes(search)) return false;
        if (campus !== "ALL" && p.campus !== campus) return false;
        if (category !== "ALL" && p.category !== category) return false;

        const key = p.campus + "||" + p.role;
        const filled = filledMap[key] || 0;
        const variance = filled - p.approved_fte;

        if (varFilter === "EXCEEDED" && variance <= 0) return false;
        if (varFilter === "VACANT" && variance >= 0) return false;
        if (varFilter === "BALANCED" && variance !== 0) return false;

        return true;
      }});

      document.getElementById("matrix-status-text").textContent = `Showing ${{filtered.length}} of ${{DB.approved_plan.length}} allocations`;

      filtered.forEach(p => {{
        const key = p.campus + "||" + p.role;
        const filled = filledMap[key] || 0;
        const vacant = vacantMap[key] || 0;
        const variance = filled - p.approved_fte;

        let varClass = "variance-zero";
        let statusBadge = `<span class="badge badge-success">Balanced</span>`;
        let varSign = "";

        if (variance > 0) {{
          varClass = "variance-positive";
          varSign = "+";
          statusBadge = `<span class="badge badge-danger">Over-FTE</span>`;
        }} else if (variance < 0) {{
          varClass = "variance-negative";
          statusBadge = `<span class="badge badge-warning">${{Math.abs(variance).toFixed(1)}} Vacant</span>`;
        }}

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${{p.campus}}</strong></td>
          <td style="font-weight: 600; color: var(--navy-900);">${{p.role}}</td>
          <td><span class="badge badge-neutral">${{p.category}}</span></td>
          <td style="text-align: right; font-weight: 700;">${{p.approved_fte.toFixed(1)}}</td>
          <td style="text-align: right; color: var(--green-700); font-weight: 700;">${{filled.toFixed(1)}}</td>
          <td style="text-align: right; color: var(--amber-600); font-weight: 700;">${{vacant.toFixed(1)}}</td>
          <td style="text-align: center;"><span class="variance-pill ${{varClass}}">${{varSign}}${{variance.toFixed(1)}}</span></td>
          <td style="text-align: center;">${{statusBadge}}</td>
          <td style="text-align: center; font-size: 0.75rem; color: var(--slate-500);">${{p.last_revised_date || "2026-08-01"}}</td>
          <td style="text-align: center;" class="editor-col">
            <button class="btn btn-outline btn-sm" onclick="openReviseModal('${{p.campus}}', '${{p.role}}', ${{p.approved_fte}})">Revise</button>
          </td>
        `;
        tbody.appendChild(tr);
      }});

      if (currentMode === "leadership") {{
        document.querySelectorAll(".editor-col").forEach(el => el.style.display = "none");
      }}
    }}

    function renderRosterView() {{
      const search = (document.getElementById("search-roster").value || "").toLowerCase();
      const campus = document.getElementById("filter-roster-campus").value;
      const status = document.getElementById("filter-roster-status").value;

      const tbody = document.getElementById("tbody-roster");
      tbody.innerHTML = "";

      let filtered = DB.actual_hires.filter(h => {{
        if (search && !h.employee_name.toLowerCase().includes(search) &&
            !h.role.toLowerCase().includes(search) &&
            !h.assignment.toLowerCase().includes(search) &&
            !h.position_id.toLowerCase().includes(search)) return false;
        if (campus !== "ALL" && h.campus !== campus) return false;
        if (status !== "ALL" && h.status !== status) return false;
        return true;
      }});

      document.getElementById("roster-count-badge").textContent = `${{filtered.length}} Roster Records`;

      filtered.forEach(h => {{
        const isVacant = h.status === "Vacant";
        const statusBadge = isVacant 
          ? `<span class="badge badge-warning">Vacant Slot</span>`
          : `<span class="badge badge-success">Filled</span>`;

        const overrideBadge = h.override_flag === "Yes"
          ? `<span class="badge badge-danger" title="${{h.override_reason}}">OVERRIDDEN</span>`
          : `<span class="badge badge-neutral">Standard</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-family: monospace; font-size: 0.75rem; color: var(--slate-500);">${{h.hire_id}}</td>
          <td><strong>${{h.campus}}</strong></td>
          <td style="font-weight: 600; color: var(--navy-900);">${{h.role}}</td>
          <td style="${{isVacant ? 'font-style: italic; color: var(--amber-600);' : 'font-weight: 600;'}}">${{h.employee_name}}</td>
          <td style="color: var(--slate-600); font-size: 0.78rem;">${{h.assignment || h.job_title || "-"}}</td>
          <td style="text-align: center; font-weight: 700;">${{(parseFloat(h.fte) || 1.0).toFixed(1)}}</td>
          <td style="text-align: center;">${{statusBadge}}</td>
          <td style="font-family: monospace; font-size: 0.75rem;">${{h.position_id || "-"}}</td>
          <td style="font-size: 0.75rem; color: var(--slate-500);">${{h.hire_date || "-"}}</td>
          <td style="text-align: center;">${{overrideBadge}}</td>
          <td style="text-align: center;" class="editor-col">
            <button class="btn btn-outline btn-sm" style="color: var(--crimson-600);" onclick="removeHirePrompt('${{h.hire_id}}')">Remove</button>
          </td>
        `;
        tbody.appendChild(tr);
      }});

      if (currentMode === "leadership") {{
        document.querySelectorAll(".editor-col").forEach(el => el.style.display = "none");
      }}
    }}

    function renderViolationsView() {{
      const search = (document.getElementById("search-violations").value || "").toLowerCase();
      const statusFilter = document.getElementById("filter-violations-status").value;

      const tbody = document.getElementById("tbody-violations");
      tbody.innerHTML = "";

      let filtered = DB.violations.filter(v => {{
        if (search && !v.campus.toLowerCase().includes(search) && !v.role.toLowerCase().includes(search)) return false;
        if (statusFilter !== "ALL" && v.status !== statusFilter) return false;
        return true;
      }});

      document.getElementById("violations-count-badge").textContent = `${{filtered.filter(v => v.status !== 'RESOLVED').length}} Active Flags`;

      if (filtered.length === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="12" style="text-align: center; padding: 2.5rem; color: var(--slate-400);">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 0.5rem;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
              <p style="font-weight: 600; color: var(--slate-700);">No Staffing Violations Recorded</p>
              <p style="font-size: 0.75rem;">All campus hiring complies with the 2026-2027 approved FTE staffing budget.</p>
            </td>
          </tr>
        `;
        return;
      }}

      filtered.forEach(v => {{
        const typeBadge = v.type === "UNAPPROVED_ROLE"
          ? `<span class="badge badge-danger">Unapproved Role</span>`
          : `<span class="badge badge-warning">Exceeded FTE Count</span>`;

        const statusBadge = v.status === "RESOLVED"
          ? `<span class="badge badge-success">Resolved</span>`
          : `<span class="badge badge-danger">Overridden</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-family: monospace; font-size: 0.75rem;">${{v.violation_id}}</td>
          <td><strong>${{v.campus}}</strong></td>
          <td style="font-weight: 600; color: var(--navy-900);">${{v.role}}</td>
          <td>${{typeBadge}}</td>
          <td style="text-align: right;">${{v.approved_fte}}</td>
          <td style="text-align: right; font-weight: 700; color: var(--crimson-600);">${{v.actual_fte}}</td>
          <td style="text-align: center;"><span class="variance-pill variance-positive">+${{v.variance}}</span></td>
          <td>${{v.employee_name}}</td>
          <td style="text-align: center;">${{statusBadge}}</td>
          <td style="font-size: 0.75rem; color: var(--slate-700); max-width: 250px;">${{v.override_reason || "-"}}</td>
          <td style="font-size: 0.72rem; color: var(--slate-500);">${{v.logged_date}} by ${{v.logged_by}}</td>
          <td style="text-align: center;" class="editor-col">
            ${{v.status !== 'RESOLVED' ? `<button class="btn btn-outline btn-sm" onclick="resolveViolationPrompt('${{v.violation_id}}')">Resolve</button>` : `<span style="font-size: 0.72rem; color: var(--green-700);">Closed</span>`}}
          </td>
        `;
        tbody.appendChild(tr);
      }});

      if (currentMode === "leadership") {{
        document.querySelectorAll(".editor-col").forEach(el => el.style.display = "none");
      }}
    }}

    function renderAuditView() {{
      const search = (document.getElementById("search-audit").value || "").toLowerCase();
      const campus = document.getElementById("filter-audit-campus").value;
      const action = document.getElementById("filter-audit-action").value;

      const tbody = document.getElementById("tbody-audit");
      tbody.innerHTML = "";

      let filtered = DB.audit_log.filter(a => {{
        if (search && !a.campus.toLowerCase().includes(search) &&
            !a.role.toLowerCase().includes(search) &&
            !a.action_type.toLowerCase().includes(search) &&
            !a.user_email.toLowerCase().includes(search) &&
            !a.reason_notes.toLowerCase().includes(search)) return false;
        if (campus !== "ALL" && a.campus !== campus) return false;
        if (action !== "ALL" && a.action_type !== action) return false;
        return true;
      }});

      filtered.forEach(a => {{
        let actionBadge = `<span class="badge badge-neutral">${{a.action_type}}</span>`;
        if (a.action_type === "PLAN_REVISION") actionBadge = `<span class="badge badge-navy">PLAN_REVISION</span>`;
        if (a.action_type === "HIRE_WITH_OVERRIDE") actionBadge = `<span class="badge badge-danger">HIRE_WITH_OVERRIDE</span>`;
        if (a.action_type === "HIRE_LOGGED") actionBadge = `<span class="badge badge-success">HIRE_LOGGED</span>`;
        if (a.action_type === "HIRE_REMOVED") actionBadge = `<span class="badge badge-warning">HIRE_REMOVED</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-family: monospace; font-size: 0.75rem; color: var(--slate-500);">${{a.log_id}}</td>
          <td style="font-size: 0.75rem; white-space: nowrap;">${{a.timestamp}}</td>
          <td style="font-size: 0.78rem; font-weight: 600; color: var(--slate-800);">${{a.user_email}}</td>
          <td>${{actionBadge}}</td>
          <td><strong>${{a.campus}}</strong></td>
          <td style="font-size: 0.78rem;">${{a.role}}</td>
          <td style="font-size: 0.75rem; color: var(--slate-500);">${{a.old_value || "-"}}</td>
          <td style="font-size: 0.75rem; font-weight: 600; color: var(--navy-900);">${{a.new_value || "-"}}</td>
          <td style="font-size: 0.75rem; color: var(--slate-700); max-width: 320px;">${{a.reason_notes || "-"}}</td>
          <td style="text-align: center;"><span class="badge ${{a.override_status === 'OVERRIDDEN' ? 'badge-danger' : 'badge-neutral'}}">${{a.override_status}}</span></td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function openModal(id) {{
      document.getElementById(id).classList.add("open");
    }}
    function closeModal(id) {{
      document.getElementById(id).classList.remove("open");
    }}

    function openReviseModal(campus, role, currentFte) {{
      document.getElementById("revise-campus").value = campus;
      document.getElementById("revise-role").value = role;
      document.getElementById("revise-current-fte").value = currentFte.toFixed(1);
      document.getElementById("revise-new-fte").value = currentFte;
      document.getElementById("revise-reason").value = "";
      openModal("modal-revise-plan");
    }}

    function submitPlanRevision() {{
      const campus = document.getElementById("revise-campus").value;
      const role = document.getElementById("revise-role").value;
      const newFte = parseFloat(document.getElementById("revise-new-fte").value);
      const reason = document.getElementById("revise-reason").value.trim();

      if (isNaN(newFte) || newFte < 0) {{
        showToast("Please enter a valid approved FTE value.", "danger");
        return;
      }}
      if (!reason) {{
        showToast("A justification reason is mandatory for plan revisions.", "danger");
        return;
      }}

      if (typeof google !== "undefined" && google.script && google.script.run) {{
        google.script.run
          .withSuccessHandler(res => {{
            DB = res.appData;
            closeModal("modal-revise-plan");
            showToast(res.message, "success");
            updateKPICards();
            renderMatrixView();
            renderAuditView();
          }})
          .withFailureHandler(err => showToast(err.message, "danger"))
          .reviseApprovedPlan(campus, role, newFte, reason);
      }} else {{
        const planItem = DB.approved_plan.find(p => p.campus === campus && p.role === role);
        const oldFte = planItem ? planItem.approved_fte : 0;
        if (planItem) {{
          planItem.approved_fte = newFte;
          planItem.last_revised_date = new Date().toISOString().split("T")[0];
          planItem.revision_notes = reason;
        }}

        DB.audit_log.unshift({{
          log_id: "AUDIT-" + Math.floor(Math.random() * 90000 + 10000),
          timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
          user_email: currentUserEmail,
          action_type: "PLAN_REVISION",
          campus: campus,
          role: role,
          old_value: oldFte + " FTE",
          new_value: newFte + " FTE",
          reason_notes: reason,
          override_status: "APPROVED"
        }});

        const camp = DB.campuses.find(c => c.campus === campus);
        if (camp) {{
          camp.approved_fte = DB.approved_plan.filter(p => p.campus === campus).reduce((acc, v) => acc + v.approved_fte, 0);
          camp.variance = camp.actual_fte - camp.approved_fte;
        }}

        closeModal("modal-revise-plan");
        showToast("Approved Plan revised to " + newFte + " FTE. Logged in audit trail.", "success");
        updateKPICards();
        renderMatrixView();
        renderAuditView();
      }}
    }}

    function openLogHireModal() {{
      const campus = document.getElementById("filter-matrix-campus").value;
      if (campus !== "ALL") {{
        document.getElementById("hire-campus").value = campus;
        populateRoleDropdownForCampus(campus);
      }}
      document.getElementById("hire-name").value = "";
      document.getElementById("hire-pos-id").value = "";
      document.getElementById("hire-assignment").value = "";
      document.getElementById("hire-fte").value = "1.0";
      document.getElementById("check-override").checked = false;
      document.getElementById("hire-override-reason").value = "";
      document.getElementById("override-reason-group").style.display = "none";
      checkHireValidation();
      openModal("modal-log-hire");
    }}

    function checkHireValidation() {{
      const campus = document.getElementById("hire-campus").value;
      const role = document.getElementById("hire-role").value;
      const fte = parseFloat(document.getElementById("hire-fte").value) || 1.0;

      const valBox = document.getElementById("hire-validation-box");
      const alertTitle = document.getElementById("val-alert-title");
      const alertMsg = document.getElementById("val-alert-msg");
      const btnSubmit = document.getElementById("btn-submit-hire");

      if (role === "__NEW_UNAPPROVED__") {{
        valBox.classList.add("show");
        alertTitle.textContent = "UNAPPROVED ROLE DETECTED";
        alertMsg.textContent = `The selected role has never been approved for ${{campus}}. Hiring into an unapproved role requires an explicit administrative override.`;
        btnSubmit.textContent = "Request Override & Log Hire";
        return;
      }}

      const planRow = DB.approved_plan.find(p => p.campus === campus && p.role === role);
      const approvedFte = planRow ? planRow.approved_fte : 0;

      const currentFilled = DB.actual_hires
        .filter(h => h.campus === campus && h.role === role && h.status === "Filled")
        .reduce((acc, h) => acc + (parseFloat(h.fte) || 1.0), 0);

      const projected = currentFilled + fte;

      if (!planRow || approvedFte === 0) {{
        valBox.classList.add("show");
        alertTitle.textContent = "UNAPPROVED ROLE AT THIS CAMPUS";
        alertMsg.textContent = `The role "${{role}}" has 0 approved allocations at ${{campus}}. Requires explicit override.`;
        btnSubmit.textContent = "Submit Override Request";
      }} else if (projected > approvedFte) {{
        valBox.classList.add("show");
        alertTitle.textContent = "EXCEEDS APPROVED FTE BUDGET";
        alertMsg.textContent = `Adding ${{fte}} FTE to "${{role}}" at ${{campus}} brings total to ${{projected.toFixed(1)}} FTE, exceeding approved plan of ${{approvedFte.toFixed(1)}} FTE (Variance: +${{(projected - approvedFte).toFixed(1)}}).`;
        btnSubmit.textContent = "Submit Override Request";
      }} else {{
        valBox.classList.remove("show");
        btnSubmit.textContent = "Save Staff Hire";
      }}
    }}

    function toggleOverrideJustification() {{
      const checked = document.getElementById("check-override").checked;
      document.getElementById("override-reason-group").style.display = checked ? "block" : "none";
    }}

    function submitHire() {{
      const campus = document.getElementById("hire-campus").value;
      const role = document.getElementById("hire-role").value;
      const name = document.getElementById("hire-name").value.trim();
      const posId = document.getElementById("hire-pos-id").value.trim();
      const assign = document.getElementById("hire-assignment").value.trim();
      const fte = parseFloat(document.getElementById("hire-fte").value) || 1.0;
      const status = document.getElementById("hire-status").value;

      if (!name) {{
        showToast("Employee name is required.", "danger");
        return;
      }}

      const valBox = document.getElementById("hire-validation-box");
      const isViolating = valBox.classList.contains("show");
      const isOverride = document.getElementById("check-override").checked;
      const overrideReason = document.getElementById("hire-override-reason").value.trim();

      if (isViolating && !isOverride) {{
        showToast("Validation blocked: You must check 'Grant Administrative Override' to proceed.", "danger");
        return;
      }}

      if (isViolating && isOverride && !overrideReason) {{
        showToast("An explicit override justification reason is mandatory.", "danger");
        return;
      }}

      const payload = {{
        campus: campus,
        role: role === "__NEW_UNAPPROVED__" ? "Unapproved Special Role" : role,
        employee_name: name,
        position_id: posId,
        assignment: assign,
        fte: fte,
        status: status,
        hire_date: new Date().toISOString().split("T")[0]
      }};

      if (typeof google !== "undefined" && google.script && google.script.run) {{
        google.script.run
          .withSuccessHandler(res => {{
            if (res.success) {{
              DB = res.appData;
              closeModal("modal-log-hire");
              showToast(res.message, "success");
              updateKPICards();
              renderMatrixView();
              renderRosterView();
              renderViolationsView();
              renderAuditView();
            }} else {{
              showToast(res.message, "danger");
            }}
          }})
          .withFailureHandler(err => showToast(err.message, "danger"))
          .logOrUpdateHire(payload, isOverride, overrideReason);
      }} else {{
        const hireId = "HIRE-" + Math.floor(Math.random() * 90000 + 10000);
        payload.hire_id = hireId;
        payload.override_flag = isOverride ? "Yes" : "No";
        payload.override_reason = overrideReason;
        DB.actual_hires.unshift(payload);

        if (isOverride) {{
          const violId = "VIOL-" + Math.floor(Math.random() * 90000 + 10000);
          DB.violations.unshift({{
            violation_id: violId,
            campus: campus,
            role: payload.role,
            type: "EXCEEDED_FTE",
            approved_fte: 1.0,
            actual_fte: 2.0,
            variance: 1.0,
            employee_name: name,
            status: "OVERRIDDEN",
            override_reason: overrideReason,
            logged_date: new Date().toISOString().split("T")[0],
            logged_by: currentUserEmail
          }});
        }}

        DB.audit_log.unshift({{
          log_id: "AUDIT-" + Math.floor(Math.random() * 90000 + 10000),
          timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
          user_email: currentUserEmail,
          action_type: isOverride ? "HIRE_WITH_OVERRIDE" : "HIRE_LOGGED",
          campus: campus,
          role: payload.role,
          old_value: "None",
          new_value: `${{name}} (${{status}}, ${{fte}} FTE)`,
          reason_notes: isOverride ? "OVERRIDE: " + overrideReason : "Standard hire",
          override_status: isOverride ? "OVERRIDDEN" : "STANDARD"
        }});

        const camp = DB.campuses.find(c => c.campus === campus);
        if (camp) {{
          camp.actual_fte += fte;
          camp.variance = camp.actual_fte - camp.approved_fte;
          if (isOverride) camp.violations_count += 1;
        }}

        closeModal("modal-log-hire");
        showToast(isOverride ? "Hire saved with administrative override. Violation recorded." : "Staff hire logged successfully.", "success");
        updateKPICards();
        renderMatrixView();
        renderRosterView();
        renderViolationsView();
        renderAuditView();
      }}
    }}

    function removeHirePrompt(hireId) {{
      const reason = prompt("Enter a reason for removing this staffing hire entry:");
      if (!reason || reason.trim() === "") return;

      if (typeof google !== "undefined" && google.script && google.script.run) {{
        google.script.run
          .withSuccessHandler(res => {{
            DB = res.appData;
            showToast(res.message, "success");
            updateKPICards();
            renderMatrixView();
            renderRosterView();
            renderAuditView();
          }})
          .withFailureHandler(err => showToast(err.message, "danger"))
          .removeHire(hireId, reason);
      }} else {{
        const idx = DB.actual_hires.findIndex(h => h.hire_id === hireId);
        if (idx > -1) {{
          const h = DB.actual_hires[idx];
          DB.actual_hires.splice(idx, 1);

          DB.audit_log.unshift({{
            log_id: "AUDIT-" + Math.floor(Math.random() * 90000 + 10000),
            timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
            user_email: currentUserEmail,
            action_type: "HIRE_REMOVED",
            campus: h.campus,
            role: h.role,
            old_value: `${{h.employee_name}} (${{h.hire_id}})`,
            new_value: "REMOVED",
            reason_notes: reason,
            override_status: "STANDARD"
          }});

          const camp = DB.campuses.find(c => c.campus === h.campus);
          if (camp) {{
            camp.actual_fte -= (parseFloat(h.fte) || 1.0);
            camp.variance = camp.actual_fte - camp.approved_fte;
          }}

          showToast("Staff hire removed. Logged in audit trail.", "success");
          updateKPICards();
          renderMatrixView();
          renderRosterView();
          renderAuditView();
        }}
      }}
    }}

    function resolveViolationPrompt(violId) {{
      const reason = prompt("Enter resolution notes for this violation (e.g. approved budget amendment):");
      if (!reason || reason.trim() === "") return;

      const viol = DB.violations.find(v => v.violation_id === violId);
      if (viol) {{
        viol.status = "RESOLVED";
        viol.override_reason += " [RESOLVED: " + reason + "]";

        DB.audit_log.unshift({{
          log_id: "AUDIT-" + Math.floor(Math.random() * 90000 + 10000),
          timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
          user_email: currentUserEmail,
          action_type: "VIOLATION_RESOLVED",
          campus: viol.campus,
          role: viol.role,
          old_value: "STATUS: OVERRIDDEN",
          new_value: "STATUS: RESOLVED",
          reason_notes: reason,
          override_status: "RESOLVED"
        }});

        const camp = DB.campuses.find(c => c.campus === viol.campus);
        if (camp && camp.violations_count > 0) camp.violations_count -= 1;

        showToast("Violation marked as resolved.", "success");
        updateKPICards();
        renderViolationsView();
        renderAuditView();
      }}
    }}

    function openAddRoleModal() {{
      document.getElementById("addrole-name").value = "";
      document.getElementById("addrole-reason").value = "";
      openModal("modal-add-role");
    }}

    function submitAddRole() {{
      const campus = document.getElementById("addrole-campus").value;
      const role = document.getElementById("addrole-name").value.trim();
      const category = document.getElementById("addrole-category").value;
      const fte = parseFloat(document.getElementById("addrole-fte").value) || 1.0;
      const reason = document.getElementById("addrole-reason").value.trim();

      if (!role) {{
        showToast("Role title is required.", "danger");
        return;
      }}
      if (!reason) {{
        showToast("Budget justification reason is required.", "danger");
        return;
      }}

      DB.approved_plan.push({{
        plan_id: "PLAN-" + Math.floor(Math.random() * 90000 + 10000),
        campus: campus,
        role: role,
        category: category,
        approved_fte: fte,
        last_revised_date: new Date().toISOString().split("T")[0],
        last_revised_by: currentUserEmail,
        revision_notes: reason
      }});

      DB.audit_log.unshift({{
        log_id: "AUDIT-" + Math.floor(Math.random() * 90000 + 10000),
        timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
        user_email: currentUserEmail,
        action_type: "APPROVED_ROLE_ADDED",
        campus: campus,
        role: role,
        old_value: "0 FTE",
        new_value: fte + " FTE",
        reason_notes: reason,
        override_status: "APPROVED"
      }});

      const camp = DB.campuses.find(c => c.campus === campus);
      if (camp) {{
        camp.approved_fte += fte;
        camp.variance = camp.actual_fte - camp.approved_fte;
      }}

      closeModal("modal-add-role");
      showToast(`Role "${{role}}" approved for ${{campus}} with ${{fte}} FTE.`, "success");
      updateKPICards();
      renderMatrixView();
      renderAuditView();
    }}

    function openCampusDrawer(campusName) {{
      const camp = DB.campuses.find(c => c.campus === campusName);
      if (!camp) return;

      document.getElementById("drawer-campus-name").textContent = camp.campus;
      document.getElementById("drawer-campus-sub").textContent = `${{camp.region}} Region &bull; Grades ${{camp.grades}}`;
      document.getElementById("drawer-approved").textContent = camp.approved_fte.toFixed(1);
      document.getElementById("drawer-filled").textContent = camp.actual_fte.toFixed(1);
      document.getElementById("drawer-vacant").textContent = camp.vacant_fte.toFixed(1);

      const roles = DB.approved_plan.filter(p => p.campus === campusName).sort((a,b) => a.role.localeCompare(b.role));
      const tbody = document.getElementById("drawer-tbody");
      tbody.innerHTML = "";

      roles.forEach(r => {{
        const filled = DB.actual_hires
          .filter(h => h.campus === campusName && h.role === r.role && h.status === "Filled")
          .reduce((acc, h) => acc + (parseFloat(h.fte) || 1.0), 0);
        const variance = filled - r.approved_fte;

        let varClass = "variance-zero";
        let varSign = "";
        if (variance > 0) {{ varClass = "variance-positive"; varSign = "+"; }}
        else if (variance < 0) {{ varClass = "variance-negative"; }}

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${{r.role}}</strong></td>
          <td style="text-align: right;">${{r.approved_fte.toFixed(1)}}</td>
          <td style="text-align: right; color: var(--green-700); font-weight:600;">${{filled.toFixed(1)}}</td>
          <td style="text-align: center;"><span class="variance-pill ${{varClass}}">${{varSign}}${{variance.toFixed(1)}}</span></td>
        `;
        tbody.appendChild(tr);
      }});

      document.getElementById("drawer-campus").classList.add("open");
    }}

    function closeDrawer() {{
      document.getElementById("drawer-campus").classList.remove("open");
    }}

    function exportAuditToCSV() {{
      let csv = "Log ID,Timestamp,User Email,Action Type,Campus,Role,Old Value,New Value,Reason Notes,Override Status\\n";
      DB.audit_log.forEach(a => {{
        csv += `"${{a.log_id}}","${{a.timestamp}}","${{a.user_email}}","${{a.action_type}}","${{a.campus}}","${{a.role}}","${{(a.old_value||'').replace(/"/g, '""')}}","${{(a.new_value||'').replace(/"/g, '""')}}","${{(a.reason_notes||'').replace(/"/g, '""')}}","${{a.override_status}}"\\n`;
      }});

      const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `SST_Staffing_Audit_Trail_${{new Date().toISOString().split("T")[0]}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast("Audit log exported to CSV successfully.", "success");
    }}

    function showToast(msg, type = "success") {{
      const toast = document.getElementById("app-toast");
      toast.textContent = msg;
      toast.className = `toast toast-${{type}} show`;
      setTimeout(() => {{
        toast.className = "toast";
      }}, 3500);
    }}
  </script>
</body>
</html>
"""

def generate_files():
    json_str = json.dumps(DATABASE)
    
    # 1. Generate index.html at root (for GitHub Pages live link)
    html_content = HTML_TEMPLATE.replace("__INITIAL_DB_PLACEHOLDER__", json_str)
    root_index_path = os.path.join(BASE_DIR, "index.html")
    with open(root_index_path, "w") as f:
        f.write(html_content)
    print(f"Generated GitHub Pages root entry point at: {root_index_path}")

    # 2. Generate standalone browser demo: fte_planning_app.html
    standalone_path = os.path.join(BASE_DIR, "fte_planning_app.html")
    with open(standalone_path, "w") as f:
        f.write(html_content)
    print(f"Generated standalone browser web app at: {standalone_path}")

    # 3. Generate Google Apps Script Index.html
    gas_index_path = os.path.join(BASE_DIR, "apps_script", "Index.html")
    with open(gas_index_path, "w") as f:
        f.write(html_content)
    print(f"Generated Apps Script Index.html at: {gas_index_path}")

if __name__ == "__main__":
    generate_files()
