#!/usr/bin/env python3
"""
Builds the SST FTE vs. ADP Position cross-check dashboard from
adp_reconciliation_report.json (produced by sync_adp_payroll.py).

Writes the same self-contained page to index.html, fte_planning_app.html
and apps_script/Index.html.
"""

import os
import json
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "adp_reconciliation_report.json")
LOGO_PATH = os.path.join(BASE_DIR, "sst_logo.jpg")
OUTPUTS = ["index.html", "fte_planning_app.html", os.path.join("apps_script", "Index.html")]

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SST FTE–ADP Cross-Check</title>
<style>
  :root {
    --navy: #0B2545; --navy-2: #133968; --crimson: #990000;
    --bg: #f4f6f9; --surface: #ffffff; --surface-2: #f8fafc; --border: #e2e8f0;
    --ink: #0f172a; --ink-2: #475569; --ink-3: #64748b;
    --ok: #15803d; --ok-bg: #dcfce7;
    --warn: #b45309; --warn-bg: #fef3c7;
    --bad: #b91c1c; --bad-bg: #fee2e2;
    --info: #1d4ed8; --info-bg: #dbeafe;
    --muted-bg: #f1f5f9;
    --focus: #2563eb; --bar: #133968;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0b1220; --surface: #111a2c; --surface-2: #0f1727; --border: #24324a;
      --ink: #e5e9f0; --ink-2: #aab4c3; --ink-3: #8592a6;
      --ok: #4ade80; --ok-bg: #12301f; --warn: #fbbf24; --warn-bg: #3a2a0a;
      --bad: #f87171; --bad-bg: #3b1414; --info: #93c5fd; --info-bg: #13274a;
      --muted-bg: #1a2438; --focus: #60a5fa; --bar: #60a5fa;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: var(--bg); color: var(--ink); font-size: 14px; line-height: 1.45; }
  header { background: var(--navy); color: #fff; padding: 14px 24px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
  header img { height: 44px; background: #fff; border-radius: 6px; padding: 3px; }
  header h1 { font-size: 18px; margin: 0; }
  header p { margin: 2px 0 0; font-size: 12px; color: #c7d2fe; }
  main { max-width: 1400px; margin: 0 auto; padding: 20px 16px 48px; }
  h2 { font-size: 15px; margin: 28px 0 4px; }
  .sub { color: var(--ink-3); font-size: 12.5px; margin: 0 0 10px; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)); gap: 10px; }
  .kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px;
         text-align: left; cursor: pointer; font: inherit; color: inherit; border-top: 3px solid var(--border); }
  .kpi:hover, .kpi.active { outline: 2px solid var(--focus); outline-offset: -1px; }
  .kpi .lbl { font-size: 11.5px; color: var(--ink-2); font-weight: 600; }
  .kpi .val { font-size: 26px; font-weight: 700; margin-top: 2px; font-variant-numeric: tabular-nums; }
  .kpi .hint { font-size: 11px; color: var(--ink-3); }
  .kpi.ok { border-top-color: var(--ok); } .kpi.warn { border-top-color: var(--warn); }
  .kpi.bad { border-top-color: var(--bad); } .kpi.info { border-top-color: var(--info); }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  .scroll { overflow-x: auto; max-height: 640px; overflow-y: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  th { position: sticky; top: 0; background: var(--surface-2); text-align: left; font-weight: 600; color: var(--ink-2);
       padding: 8px 10px; border-bottom: 1px solid var(--border); white-space: nowrap; cursor: pointer; user-select: none; z-index: 1; }
  td { padding: 7px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  tr.click { cursor: pointer; } tr.click:hover td { background: var(--muted-bg); }
  tr.sel td { background: var(--info-bg); }
  .diff { color: var(--bad); font-weight: 600; }
  .dim { color: var(--ink-3); }
  .pill { display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; white-space: nowrap; margin: 1px 2px 1px 0; }
  .p-ok { background: var(--ok-bg); color: var(--ok); } .p-warn { background: var(--warn-bg); color: var(--warn); }
  .p-bad { background: var(--bad-bg); color: var(--bad); } .p-info { background: var(--info-bg); color: var(--info); }
  .p-muted { background: var(--muted-bg); color: var(--ink-2); }
  .over { color: var(--bad); font-weight: 700; } .under { color: var(--ink-3); }
  .toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; }
  select, input[type=search], button.btn { font: inherit; font-size: 13px; padding: 6px 10px; border-radius: 7px;
       border: 1px solid var(--border); background: var(--surface); color: var(--ink); }
  input[type=search] { min-width: 220px; flex: 1 1 220px; max-width: 360px; }
  button.btn { cursor: pointer; font-weight: 600; }
  button.btn:hover { border-color: var(--focus); }
  .count { margin-left: auto; color: var(--ink-3); font-size: 12px; }
  label.chk { font-size: 12.5px; color: var(--ink-2); display: flex; gap: 5px; align-items: center; }
  .note { font-size: 12px; color: var(--ink-3); margin-top: 8px; }
  .tip { margin: 0 0 10px; font-size: 12.5px; color: var(--ink-2); }
  .htitle { flex: 1 1 280px; }
  .run { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .run #run-msg { font-size: 12px; color: #c7d2fe; }
  .run-btn { background: #fff; color: var(--navy) !important; border-color: #fff !important; }
  .run-btn.off { opacity: .75; }
  .run-btn:disabled { cursor: progress; }
  .spin { display: inline-block; width: 11px; height: 11px; border: 2px solid currentColor; border-right-color: transparent;
          border-radius: 50%; animation: sp .8s linear infinite; vertical-align: -1px; }
  @keyframes sp { to { transform: rotate(360deg); } }
  button.n { font: inherit; font-variant-numeric: tabular-nums; background: none; border: 0; padding: 1px 5px; margin: -1px -5px;
             border-radius: 5px; color: var(--info); cursor: pointer; text-decoration: underline dotted; text-underline-offset: 3px; }
  button.n:hover, button.n:focus-visible { background: var(--info-bg); outline: none; }
  button.n.over { color: var(--bad); font-weight: 700; } button.n.under { color: var(--ink-2); }
  button.link { font: inherit; background: none; border: 0; padding: 0; color: inherit; cursor: pointer; text-align: left; }
  button.link:hover b { text-decoration: underline; }
  th.sort { cursor: pointer; }
  .modal-bg { position: fixed; inset: 0; background: rgba(15, 23, 42, .55); display: flex; align-items: flex-start; justify-content: center;
              padding: 4vh 16px; z-index: 50; }
  .modal-bg[hidden] { display: none; }
  .modal { background: var(--surface); border-radius: 12px; width: min(1300px, 100%); max-height: 92vh; display: flex; flex-direction: column;
           box-shadow: 0 20px 50px rgba(0,0,0,.35); }
  .m-head { display: flex; justify-content: space-between; gap: 12px; padding: 14px 16px 10px; }
  .m-head h3 { margin: 0; font-size: 16px; }
  .m-body { overflow: auto; border-top: 1px solid var(--border); }
  .toast { position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); max-width: min(640px, calc(100% - 32px));
           padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; z-index: 60; box-shadow: 0 8px 24px rgba(0,0,0,.2); }
  .toast[hidden] { display: none; }
  .t-ok { background: var(--ok-bg); color: var(--ok); } .t-bad { background: var(--bad-bg); color: var(--bad); }
  .t-warn { background: var(--warn-bg); color: var(--warn); }
  button.kpi { width: 100%; }
  .bar { position: relative; height: 10px; min-width: 120px; background: var(--muted-bg); border-radius: 3px; }
  .bar i { position: absolute; left: 0; top: 0; bottom: 0; background: var(--bar); border-radius: 0 4px 4px 0; }
  .bar b { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--ink); }
  .mx td, .mx th { text-align: right; } .mx td:first-child, .mx th:first-child { text-align: left; position: sticky; left: 0; background: var(--surface); }
  .mx th:first-child { background: var(--surface-2); z-index: 2; }
  .mx .ap { color: var(--ink-3); font-size: 11px; }
  @media (max-width: 640px) { header { padding: 12px 16px; } .kpi .val { font-size: 22px; } }
</style>
</head>
<body>
<header>
  <img src="__LOGO__" alt="SST logo">
  <div class="htitle">
    <h1>FTE List vs. ADP Position Cross-Check</h1>
    <p id="meta"></p>
  </div>
  <div class="run">
    <button class="btn run-btn" id="run" type="button">&#x21bb; Run cross-check</button>
    <span id="run-msg"></span>
  </div>
</header>
<main>
  <p class="tip">Click any number to see the people and positions behind it.</p>
  <div class="kpis" id="kpis"></div>

  <h2>Campus summary</h2>
  <p class="sub">Approved slots come from each campus's 2026-27 Approved FTE List. ADP active is the headcount whose ADP Position tab location is that campus. Click a campus name to filter the tables below.</p>
  <div class="card scroll" style="max-height:none"><table id="t-campus"></table></div>

  <h2>Overhire check by job title</h2>
  <p class="sub">ADP active headcount per campus and ADP job title, compared with the approved slots for that title. A positive difference is an overhire.</p>
  <div class="toolbar">
    <label class="chk"><input type="checkbox" id="over-only" checked> Show overhires only</label>
    <span class="count" id="over-count"></span>
  </div>
  <div class="card scroll"><table id="t-over"></table></div>

  <h2>Staffing by job title</h2>
  <p class="sub">How many people each campus has in a job title or group: approved on the FTE list vs. active in ADP. Click any number for the names.</p>
  <div class="toolbar">
    <select id="jt-title" aria-label="Job title"></select>
    <select id="jt-region" aria-label="Region">
      <option value="ALL">All regions</option><option>San Antonio</option><option>Houston</option><option>Corpus Christi</option>
    </select>
    <select id="jt-view" aria-label="View">
      <option value="campus">Totals per campus</option>
      <option value="matrix">Campus × title matrix</option>
    </select>
    <span class="count" id="jt-count"></span>
  </div>
  <div class="card scroll" style="max-height:none"><table id="t-jt"></table></div>
  <p class="note" id="jt-legend"></p>

  <h2>Person-level cross-check</h2>
  <p class="sub">Every person on an approved FTE list matched to ADP by Position ID (or by name when the Position ID changed), plus active ADP staff who are on no list. Red text marks the field that differs from ADP.</p>
  <div class="toolbar">
    <input type="search" id="q" placeholder="Search name, title, Position ID…">
    <select id="f-campus"></select>
    <select id="f-status"></select>
    <button class="btn" id="export" type="button">Export CSV</button>
    <span class="count" id="p-count"></span>
  </div>
  <div class="card scroll"><table id="t-people"></table></div>
  <p class="note" id="foot"></p>
</main>

<div class="modal-bg" id="modal" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="m-title">
    <div class="m-head">
      <div><h3 id="m-title"></h3><p class="sub" id="m-sub" style="margin:2px 0 0"></p></div>
      <button class="btn" id="m-close" type="button" aria-label="Close">&#x2715;</button>
    </div>
    <div class="toolbar" style="padding:0 16px">
      <input type="search" id="m-q" placeholder="Search in this list…">
      <button class="btn" id="m-export" type="button">Export CSV</button>
      <span class="count" id="m-count"></span>
    </div>
    <div class="m-body"><table id="m-table"></table></div>
  </div>
</div>
<div class="toast" id="toast" hidden></div>

<script>
let REPORT = __REPORT__;

const STATUS = {
  MATCH:               { label: "Matches ADP",             cls: "p-ok" },
  LOCATION_MISMATCH:   { label: "Location differs",        cls: "p-warn" },
  TITLE_MISMATCH:      { label: "Title differs",           cls: "p-warn" },
  NAME_MISMATCH:       { label: "Name differs",            cls: "p-info" },
  NOT_ACTIVE_IN_ADP:   { label: "Terminated in ADP",       cls: "p-bad" },
  NOT_IN_ADP:          { label: "Not found in ADP",        cls: "p-bad" },
  NOT_ON_LIST:         { label: "Not on FTE list",         cls: "p-bad" },
  DUPLICATE_ON_LIST:   { label: "Listed twice",            cls: "p-warn" },
  NO_FTE_LIST:         { label: "No FTE list for campus",  cls: "p-muted" },
  VACANT_STILL_ACTIVE: { label: "Vacant but still active", cls: "p-info" },
  OPEN:                { label: "Open slot",               cls: "p-muted" },
};
const FILTERS = [
  ["ALL", "All records"],
  ["ANY_ISSUE", "Any discrepancy"],
  ["LOCATION_MISMATCH", "Location differs"],
  ["TITLE_MISMATCH", "Title differs"],
  ["NAME_MISMATCH", "Name differs"],
  ["NOT_ACTIVE", "On list, not active in ADP"],
  ["NOT_ON_LIST", "Active in ADP, not on list"],
  ["DUPLICATE_ON_LIST", "Listed twice"],
  ["MATCH", "Matches ADP"],
  ["OPEN", "Open slots"],
];

// One definition per number on the page; the Python report counts use the same rules.
const METRICS = {
  approved:          { label: "Approved slots",               test: r => r.source !== "ADP" },
  adp_active:        { label: "Active in ADP",                test: r => r.adp_status === "Active", byAdpLocation: true },
  matched:           { label: "Matches ADP",                  test: r => r.status === "MATCH" || r.status === "VACANT_STILL_ACTIVE" },
  open:              { label: "Open slots",                   test: r => r.status === "OPEN" },
  location_mismatch: { label: "Location differs from ADP",    test: r => r.issues.includes("LOCATION_MISMATCH") },
  title_mismatch:    { label: "Title differs from ADP",       test: r => r.issues.includes("TITLE_MISMATCH") },
  name_mismatch:     { label: "Name differs from ADP",        test: r => r.issues.includes("NAME_MISMATCH") },
  not_active:        { label: "On list but not active in ADP", test: r => r.status === "NOT_ACTIVE_IN_ADP" || r.status === "NOT_IN_ADP" },
  not_on_list:       { label: "Active in ADP but not on FTE list", test: r => r.status === "NOT_ON_LIST" },
  duplicate:         { label: "Same person listed twice",     test: r => r.status === "DUPLICATE_ON_LIST" },
};

const state = { campus: "ALL", status: "ANY_ISSUE", q: "", sort: null, dir: 1 };
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = n => Number(n).toLocaleString();
const campusName = code => (REPORT.campuses.find(c => c.code === code) || {}).campus || code;
const campusCodes = () => new Set(REPORT.campuses.map(c => c.code));

function matchesFilter(r, f) {
  if (f === "ALL") return true;
  if (f === "ANY_ISSUE") return r.issues.length > 0;
  if (f === "NOT_ACTIVE") return METRICS.not_active.test(r);
  if (f === "MATCH") return METRICS.matched.test(r);
  if (f === "OPEN") return METRICS.open.test(r);
  return r.issues.includes(f);
}
function inCampus(r) { return state.campus === "ALL" || r.campus_code === state.campus; }

// Records behind a metric for one campus (or ALL)
function metricRecords(metric, campus) {
  const m = METRICS[metric], codes = campusCodes();
  return REPORT.records.filter(r => {
    if (!m.test(r)) return false;
    const loc = m.byAdpLocation ? r.adp_location_code : r.campus_code;
    return campus === "ALL" ? codes.has(loc) : loc === campus;
  });
}

// A clickable number. d = detail key, see openDetail()
const num = (v, d, cls = "") => v === 0 || v === "0"
  ? `<span class="dim">0</span>`
  : `<button class="n ${cls}" type="button" data-d="${esc(d)}">${esc(v)}</button>`;

/* ---------------------------------------------------------------- page */

function renderMeta() {
  const lists = REPORT.campuses.filter(c => c.has_list).length;
  const nc = Object.entries(REPORT.non_campus_active || {}).map(([k, v]) => `${k} ${v}`).join(", ");
  $("meta").textContent = `ADP pulled ${REPORT.adp_pulled_at} · ${lists} campus FTE lists · full-time staff only (no subs / part-time) · cross-check run ${REPORT.generated_at}`;
  const ex = REPORT.excluded_sub_pt || {};
  $("foot").textContent = `Substitutes and part-time staff are excluded (${ex.fte_rows ?? 0} FTE list rows, ${ex.adp_active ?? 0} active in ADP). ` +
    `Central/regional office staff are not on campus FTE lists and are excluded from the counts (${nc}). ` +
    `Titles are compared by ADP job code (e.g. 11TEACH); the FTE list "Assignment" (grade/subject) is shown for reference only.`;
}

function renderKpis() {
  const C = state.campus;
  const camps = REPORT.campuses.filter(c => C === "ALL" || c.code === C);
  const sum = k => camps.reduce((a, c) => a + c[k], 0);
  const n = k => metricRecords(k, C).length;
  const tiles = [
    ["Approved slots", sum("approved"), "on 2026-27 FTE lists", "", `m:approved:${C}`],
    ["ADP active", sum("adp_active"), "at these campus locations", "", `m:adp_active:${C}`],
    ["Matches ADP", n("matched"), "name, location & title agree", "ok", `m:matched:${C}`],
    ["Location differs", n("location_mismatch"), "ADP campus ≠ FTE list campus", "warn", `m:location_mismatch:${C}`],
    ["Title differs", n("title_mismatch"), "ADP job title ≠ FTE list title", "warn", `m:title_mismatch:${C}`],
    ["Name differs", n("name_mismatch"), "same Position ID, different name", "info", `m:name_mismatch:${C}`],
    ["On list, not active", n("not_active"), "terminated / not found in ADP", "bad", `m:not_active:${C}`],
    ["Not on FTE list", n("not_on_list"), "active in ADP, never approved", "bad", `m:not_on_list:${C}`],
    ["Listed twice", n("duplicate"), "same ADP person on 2 list rows", "warn", `m:duplicate:${C}`],
    ["Overhire", sum("overhire"), "headcount above approved, by title", "bad", `t:over:${C}`],
  ];
  $("kpis").innerHTML = tiles.map(([l, v, h, cls, d]) =>
    `<button class="kpi ${cls}" type="button" data-d="${d}">
       <div class="lbl">${l}${C === "ALL" ? "" : ` · ${esc(campusName(C))}`}</div>
       <div class="val">${fmt(v)}</div><div class="hint">${h}</div></button>`).join("");
}

function renderCampus() {
  const heads = ["Campus", "Region", "Approved", "ADP active", "Diff", "Matched", "Open slots",
    "Location differs", "Title differs", "Name differs", "Not active in ADP", "Not on list", "Overhire"];
  const row = (c, code, label, bold) => {
    const d = c.adp_active - c.approved;
    const B = s => bold ? `<b>${s}</b>` : s;
    return `<tr class="${state.campus === code ? "sel" : ""}">
      <td>${label}</td><td>${bold ? "" : esc(c.region)}</td>
      <td class="num">${B(num(c.approved, `m:approved:${code}`))}</td>
      <td class="num">${B(num(c.adp_active, `m:adp_active:${code}`))}</td>
      <td class="num">${num((d > 0 ? "+" : "") + d, `t:all:${code}`, d > 0 ? "over" : "under")}</td>
      <td class="num">${num(c.matched, `m:matched:${code}`)}</td>
      <td class="num">${num(c.open, `m:open:${code}`)}</td>
      <td class="num">${num(c.location_mismatch, `m:location_mismatch:${code}`)}</td>
      <td class="num">${num(c.title_mismatch, `m:title_mismatch:${code}`)}</td>
      <td class="num">${num(c.name_mismatch || 0, `m:name_mismatch:${code}`)}</td>
      <td class="num">${num(c.not_active, `m:not_active:${code}`)}</td>
      <td class="num">${num(c.not_on_list, `m:not_on_list:${code}`, "over")}</td>
      <td class="num">${num(c.overhire ? "+" + c.overhire : 0, `t:over:${code}`, "over")}</td></tr>`;
  };
  const T = REPORT.campuses.reduce((a, c) => { for (const k in c) if (typeof c[k] === "number") a[k] = (a[k] || 0) + c[k]; return a; }, {});
  const rows = REPORT.campuses.map(c => row(c, c.code,
    `<button class="link" type="button" data-campus="${esc(c.code)}"><b>${esc(c.campus)}</b></button> <span class="dim">(${esc(c.code)})</span>${c.has_list ? "" : ' <span class="pill p-muted">no FTE list</span>'}`));
  rows.push(row(T, "ALL", "<b>All campuses</b>", true));
  $("t-campus").innerHTML = `<thead><tr>${heads.map((h, i) => `<th class="${i > 1 ? "num" : ""}">${h}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody>`;
}

function titleRowsHtml(rows) {
  if (!rows.length) return `<tr><td colspan="6" class="dim">Nothing to show for this selection.</td></tr>`;
  return rows.map(t => {
    const k = `${t.campus_code}|${t.job_code}`;
    return `<tr><td>${esc(t.campus)}</td><td>${esc(t.job_code)} - ${esc(t.job_title)}</td>
      <td class="num">${num(t.approved, `tc:approved:${k}`)}</td>
      <td class="num">${num(t.adp_active, `tc:adp:${k}`)}</td>
      <td class="num">${num((t.variance > 0 ? "+" : "") + t.variance, `tc:unapproved:${k}`, t.variance > 0 ? "over" : "under")}</td>
      <td>${t.unapproved.map(esc).join(", ") || '<span class="dim">—</span>'}</td></tr>`;
  }).join("");
}
const TITLE_HEAD = `<thead><tr><th>Campus</th><th>ADP job title</th><th class="num">Approved</th><th class="num">ADP active</th>
  <th class="num">Difference</th><th>In ADP under this campus &amp; title without an approved slot for it</th></tr></thead>`;

function renderOver() {
  const only = $("over-only").checked;
  const rows = REPORT.title_counts.filter(t => (state.campus === "ALL" || t.campus_code === state.campus) && (!only || t.variance > 0));
  $("over-count").textContent = `${rows.length} campus × title rows`;
  $("t-over").innerHTML = TITLE_HEAD + `<tbody>${titleRowsHtml(rows)}</tbody>`;
}

const PCOLS = [
  ["status", "Status"], ["campus", "FTE list campus"], ["fte_name", "FTE list name"], ["adp_name", "ADP name"],
  ["position_id", "Position ID"], ["fte_title", "FTE list title"], ["adp_title", "ADP job title"],
  ["adp_campus", "ADP location"], ["assignment", "Assignment"], ["list_status", "List status"], ["detail", "Notes"],
];

function personRowHtml(r, extra = false) {
  const iss = new Set(r.issues);
  const pills = (r.issues.length ? r.issues : [r.status]).map(s => `<span class="pill ${STATUS[s].cls}">${STATUS[s].label}</span>`).join("");
  const pid = r.adp_position_id && r.position_id && r.adp_position_id !== r.position_id
    ? `${esc(r.position_id)}<br><span class="dim">ADP: ${esc(r.adp_position_id)}</span>` : esc(r.position_id || r.adp_position_id);
  const dash = '<span class="dim">—</span>';
  return `<tr><td>${pills}</td><td>${esc(r.campus)}</td><td>${esc(r.fte_name)}</td>
    <td class="${iss.has("NAME_MISMATCH") ? "diff" : ""}">${esc(r.adp_name) || dash}</td>
    <td>${pid}</td><td>${esc(r.fte_title) || dash}</td>
    <td class="${iss.has("TITLE_MISMATCH") ? "diff" : ""}">${esc(r.adp_title) || dash}</td>
    <td class="${iss.has("LOCATION_MISMATCH") ? "diff" : ""}">${esc(r.adp_campus) || dash}</td>
    <td>${esc(r.assignment)}</td><td>${esc(r.list_status)}</td>
    <td>${esc(r.detail)}</td>${extra ? `<td>${esc(r.worker_type)}</td><td class="dim">${esc(r.source)}</td>` : ""}</tr>`;
}

function filteredPeople() {
  const q = state.q.toLowerCase();
  let rows = REPORT.records.filter(r => inCampus(r) && matchesFilter(r, state.status) && searchHit(r, q));
  if (state.sort) {
    const k = state.sort;
    rows = rows.slice().sort((a, b) => String(a[k] || "").localeCompare(String(b[k] || "")) * state.dir);
  }
  return rows;
}
function searchHit(r, q) {
  return !q || [r.fte_name, r.adp_name, r.fte_title, r.adp_title, r.position_id, r.adp_position_id, r.assignment, r.adp_campus, r.campus]
    .some(v => String(v || "").toLowerCase().includes(q));
}

function renderPeople() {
  const rows = filteredPeople();
  $("p-count").textContent = `${fmt(rows.length)} of ${fmt(REPORT.records.length)} records`;
  const shown = rows.slice(0, 1500);
  $("t-people").innerHTML = `<thead><tr>${PCOLS.map(([k, h]) => `<th class="sort" data-k="${k}">${h}${state.sort === k ? (state.dir > 0 ? " ▲" : " ▼") : ""}</th>`).join("")}</tr></thead>
    <tbody>${shown.map(r => personRowHtml(r)).join("") || `<tr><td colspan="${PCOLS.length}" class="dim">No records match these filters.</td></tr>`}
    ${rows.length > shown.length ? `<tr><td colspan="${PCOLS.length}" class="dim">Showing first ${shown.length}; narrow the filters or export CSV for all.</td></tr>` : ""}</tbody>`;
}


/* ---------------------------------------------------------------- staffing by job title */

const TITLE_GROUPS = [
  ["TEACHERS", "Teachers", (c, t) => /TEACH/.test(c) || /TEACHER/i.test(t)],
  ["ADMIN", "Campus administration (Principal, AP, Ops Manager)", c => ["23PRI", "23AP", "23OPS"].includes(c)],
  ["AIDES", "Educational aides", c => c === "11EA"],
  ["COORD", "Coordinators (Hub / Regional)", c => /CRD$/.test(c)],
  ["OFFICE", "Office staff (Front office, Admin asst, Registrar, Secretary)", c => ["23FRONTO", "41ADMAST", "23REGIST", "23SEC", "23ATTEND"].includes(c)],
  ["SUPPORT", "Support services (Medical, Lunch, IT, Library)", c => ["33MEDAST", "35LUNCH", "23ITSPC", "11LIBR"].includes(c)],
];

function allTitles() {
  const m = new Map();
  REPORT.title_counts.forEach(t => {
    const x = m.get(t.job_code) || { code: t.job_code, title: t.job_title, adp: 0 };
    x.adp += t.adp_active; m.set(t.job_code, x);
  });
  return [...m.values()].sort((a, b) => b.adp - a.adp || a.code.localeCompare(b.code));
}

function selectedCodes() {
  const v = $("jt-title").value, titles = allTitles();
  if (v === "ALL") return titles.map(t => t.code);
  const g = TITLE_GROUPS.find(([k]) => k === v);
  if (g) return titles.filter(t => g[2](t.code, t.title)).map(t => t.code);
  return [v];
}

function populateTitleFilter() {
  const cur = $("jt-title").value || "TEACHERS", titles = allTitles();
  const groups = TITLE_GROUPS.map(([k, l, f]) => {
    const n = titles.filter(t => f(t.code, t.title)).length;
    return n ? `<option value="${k}">${esc(l)}</option>` : "";
  }).join("");
  $("jt-title").innerHTML = `<option value="ALL">All job titles</option><optgroup label="Groups">${groups}</optgroup>` +
    `<optgroup label="Individual titles">${titles.map(t => `<option value="${esc(t.code)}">${esc(t.code)} - ${esc(t.title)}</option>`).join("")}</optgroup>`;
  $("jt-title").value = [...$("jt-title").options].some(o => o.value === cur) ? cur : "TEACHERS";
}

function renderJobTitles() {
  const codes = selectedCodes(), set = new Set(codes), region = $("jt-region").value;
  const camps = REPORT.campuses.filter(c => c.has_list && (region === "ALL" || c.region === region)
    && (state.campus === "ALL" || c.code === state.campus));
  const tc = (camp, code) => REPORT.title_counts.find(t => t.campus_code === camp && t.job_code === code);
  const sumFor = (camp, cs) => cs.reduce((a, code) => {
    const t = tc(camp, code); if (t) { a.ap += t.approved; a.adp += t.adp_active; } return a;
  }, { ap: 0, adp: 0 });
  const key = codes.join(",");
  const campKey = camps.length === REPORT.campuses.filter(c => c.has_list).length ? "ALL" : camps.map(c => c.code).join("+");

  if ($("jt-view").value === "matrix") {
    const cols = allTitles().filter(t => set.has(t.code));
    const cell = (camp, code) => {
      const t = tc(camp, code) || { approved: 0, adp_active: 0 };
      if (!t.approved && !t.adp_active) return `<td><span class="dim">·</span></td>`;
      const d = t.adp_active - t.approved;
      return `<td>${num(t.adp_active, `g:adp:${camp}:${code}`, d > 0 ? "over" : "")}<div class="ap">of ${t.approved}</div></td>`;
    };
    const tot = code => camps.reduce((a, c) => { const t = tc(c.code, code); if (t) { a.ap += t.approved; a.adp += t.adp_active; } return a; }, { ap: 0, adp: 0 });
    $("t-jt").className = "mx";
    $("t-jt").innerHTML = `<thead><tr><th>Campus</th>${cols.map(t => `<th title="${esc(t.title)}" style="white-space:normal;min-width:90px">${esc(t.code)}<div class="ap" style="font-weight:400">${esc(t.title.toLowerCase())}</div></th>`).join("")}</tr></thead><tbody>` +
      camps.map(c => `<tr><td><b>${esc(c.campus)}</b></td>${cols.map(t => cell(c.code, t.code)).join("")}</tr>`).join("") +
      `<tr><td><b>Total</b></td>${cols.map(t => { const x = tot(t.code);
        return `<td><b>${num(x.adp, `g:adp:${campKey}:${t.code}`, x.adp > x.ap ? "over" : "")}</b><div class="ap">of ${x.ap}</div></td>`; }).join("")}</tr></tbody>`;
    $("jt-count").textContent = `${camps.length} campuses × ${cols.length} titles`;
    $("jt-legend").textContent = "Each cell: active in ADP, with approved slots underneath (\u201cof N\u201d). Red = more active in ADP than approved.";
    return;
  }

  const rows = camps.map(c => ({ c, ...sumFor(c.code, codes) }));
  const max = Math.max(1, ...rows.map(r => Math.max(r.ap, r.adp)));
  const T = rows.reduce((a, r) => ({ ap: a.ap + r.ap, adp: a.adp + r.adp }), { ap: 0, adp: 0 });
  const line = (label, region, camp, ap, adp, bold) => {
    const d = adp - ap, B = x => bold ? `<b>${x}</b>` : x;
    return `<tr><td>${B(label)}</td><td>${region}</td>
      <td class="num">${B(num(ap, `g:approved:${camp}:${key}`))}</td>
      <td class="num">${B(num(adp, `g:adp:${camp}:${key}`))}</td>
      <td class="num">${num((d > 0 ? "+" : "") + d, `gt:${camp}:${key}`, d > 0 ? "over" : "under")}</td>
      <td>${bold ? "" : `<div class="bar" title="${adp} active in ADP, ${ap} approved"><i style="width:${adp / max * 100}%"></i><b style="left:calc(${ap / max * 100}% - 1px)"></b></div>`}</td></tr>`;
  };
  $("t-jt").className = "";
  $("t-jt").innerHTML = `<thead><tr><th>Campus</th><th>Region</th><th class="num">Approved</th><th class="num">ADP active</th>
      <th class="num">Difference</th><th style="width:28%">ADP active vs. approved</th></tr></thead><tbody>` +
    rows.map(r => line(`<b>${esc(r.c.campus)}</b>`, esc(r.c.region), r.c.code, r.ap, r.adp)).join("") +
    line("All shown campuses", "", campKey, T.ap, T.adp, true) + "</tbody>";
  $("jt-count").textContent = `${codes.length} job title${codes.length === 1 ? "" : "s"} · ${camps.length} campuses`;
  $("jt-legend").textContent = "Bar = active in ADP; black tick = approved slots. A bar past the tick means more staff than approved.";
}

// Detail lists for the job-title section. camp is a code, "ALL", or codes joined by "+"
function groupRecords(metric, camp, codes) {
  const cs = new Set(codes.split(",")), all = campusCodes();
  const inC = c => camp === "ALL" ? all.has(c) : camp.split("+").includes(c);
  return metric === "approved"
    ? REPORT.records.filter(r => r.source !== "ADP" && inC(r.campus_code) && cs.has(r.fte_job_code))
    : REPORT.records.filter(r => r.adp_status === "Active" && inC(r.adp_location_code) && cs.has(r.adp_job_code));
}
function groupLabel(camp, codes) {
  const where = camp === "ALL" ? "all campuses" : camp.includes("+") ? "selected campuses" : campusName(camp);
  const v = $("jt-title").value, grp = TITLE_GROUPS.find(([k]) => k === v);
  const what = codes.includes(",") ? (grp ? grp[1] : "All job titles") : codes;
  return `${what} — ${where}`;
}

/* ---------------------------------------------------------------- details panel */

const modal = { kind: null, rows: [], title: "" };

function openDetail(key) {
  const [kind, a, b] = key.split(":");
  const scope = c => c === "ALL" ? "all campuses" : campusName(c);
  if (kind === "m") {
    modal.kind = "people";
    modal.rows = metricRecords(a, b);
    modal.title = `${METRICS[a].label} — ${scope(b)}`;
    modal.sub = a === "adp_active" ? "Staff whose ADP Position tab location is this campus, with the FTE list row they matched (if any)."
      : a === "approved" ? "Every approved slot on the FTE list, with what ADP shows for the person in it." : "";
  } else if (kind === "t") {
    modal.kind = "titles";
    modal.rows = REPORT.title_counts.filter(t => (b === "ALL" || t.campus_code === b) && (a === "all" || t.variance > 0));
    modal.title = `${a === "over" ? "Overhires by job title" : "Approved vs. ADP by job title"} — ${scope(b)}`;
    modal.sub = "Click a number to see the people behind it.";
  } else if (kind === "tc") {
    const [code, job] = b.split("|");
    const t = REPORT.title_counts.find(x => x.campus_code === code && x.job_code === job) || {};
    modal.kind = "people";
    if (a === "approved") {
      modal.rows = REPORT.records.filter(r => r.source !== "ADP" && r.campus_code === code && r.fte_job_code === job);
      modal.title = `Approved ${job} slots — ${campusName(code)}`;
    } else {
      const adp = REPORT.records.filter(r => r.adp_status === "Active" && r.adp_location_code === code && r.adp_job_code === job);
      modal.rows = a === "adp" ? adp : adp.filter(r => r.campus_code !== code || r.fte_job_code !== job);
      modal.title = a === "adp" ? `Active in ADP as ${job} — ${campusName(code)}` : `${job} at ${campusName(code)} without an approved slot`;
    }
    modal.sub = `${t.job_title || ""}: ${t.approved ?? 0} approved, ${t.adp_active ?? 0} active in ADP.`;
  }
  if (kind === "g") {
    const [, metric, camp, codes] = key.split(":");
    modal.kind = "people";
    modal.rows = groupRecords(metric, camp, codes);
    modal.title = `${metric === "approved" ? "Approved slots" : "Active in ADP"}: ${groupLabel(camp, codes)}`;
    modal.sub = metric === "approved" ? "FTE list rows for these job titles, with what ADP shows for each person."
      : "Staff whose ADP Position tab has this campus and job title.";
  } else if (kind === "gt") {
    const [, camp, codes] = key.split(":");
    const cs = new Set(codes.split(",")), all = campusCodes();
    modal.kind = "titles";
    modal.rows = REPORT.title_counts.filter(t => cs.has(t.job_code) && (camp === "ALL" ? all.has(t.campus_code) : camp.split("+").includes(t.campus_code)));
    modal.title = `Approved vs. ADP by job title: ${groupLabel(camp, codes)}`;
    modal.sub = "Click a number to see the people behind it.";
  }
  $("m-q").value = "";
  renderModal();
  $("modal").hidden = false;
  document.body.style.overflow = "hidden";
  $("m-close").focus();
}

function renderModal() {
  const q = $("m-q").value.toLowerCase();
  $("m-title").textContent = modal.title;
  $("m-sub").textContent = modal.sub || "";
  if (modal.kind === "titles") {
    const rows = modal.rows.filter(t => !q || `${t.campus} ${t.job_code} ${t.job_title} ${t.unapproved.join(" ")}`.toLowerCase().includes(q));
    $("m-count").textContent = `${rows.length} rows`;
    $("m-table").innerHTML = TITLE_HEAD + `<tbody>${titleRowsHtml(rows)}</tbody>`;
  } else {
    const rows = modal.rows.filter(r => searchHit(r, q));
    $("m-count").textContent = `${fmt(rows.length)} people / positions`;
    $("m-table").innerHTML = `<thead><tr>${PCOLS.map(([, h]) => `<th>${h}</th>`).join("")}<th>Worker type</th><th>Source</th></tr></thead>
      <tbody>${rows.map(r => personRowHtml(r, true)).join("") || `<tr><td colspan="13" class="dim">No records.</td></tr>`}</tbody>`;
  }
}

function closeModal() { $("modal").hidden = true; document.body.style.overflow = ""; }

/* ---------------------------------------------------------------- export */

function downloadCsv(name, rows, cols) {
  const cell = v => `"${String(Array.isArray(v) ? v.join("; ") : v ?? "").replace(/"/g, '""')}"`;
  const csv = [cols.join(",")].concat(rows.map(r => cols.map(c => cell(r[c])).join(","))).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = name.replace(/[^\w.-]+/g, "_");
  a.click();
}
const PEOPLE_CSV = ["status", "issues", "campus", "fte_name", "adp_name", "position_id", "adp_position_id", "fte_title", "adp_title",
  "adp_campus", "adp_location", "worker_type", "assignment", "list_status", "notes", "adp_status", "detail", "source"];

/* ---------------------------------------------------------------- re-run */

let API = false;
async function detectApi() {
  try {
    const r = await fetch("/api/status", { cache: "no-store" });
    API = r.ok && (await r.json()).ok === true;
  } catch (e) { API = false; }
  $("run").title = API ? "Pull ADP live, re-read the FTE list files and redo the cross-check"
    : "Re-running needs the local app (ADP credentials stay on your computer). Double-click “Run FTE Cross-Check.command” in the project folder.";
  $("run").classList.toggle("off", !API);
}

async function runCrosscheck() {
  if (!API) { toast($("run").title, "warn"); return; }
  const btn = $("run");
  btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Running…';
  $("run-msg").textContent = "Pulling ADP and re-reading FTE lists (takes 3–4 minutes)…";
  const before = REPORT.campuses.reduce((a, c) => a + c.overhire, 0);
  try {
    const r = await fetch("/api/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || r.statusText);
    REPORT = data;
    renderMeta(); populateCampusFilter(); populateTitleFilter(); renderAll();
    const after = REPORT.campuses.reduce((a, c) => a + c.overhire, 0);
    toast(`Cross-check complete — ADP pulled ${REPORT.adp_pulled_at}. Overhire ${before} → ${after}.`, "ok");
    $("run-msg").textContent = "";
  } catch (e) {
    toast("Cross-check failed: " + e.message, "bad");
    $("run-msg").textContent = "";
  } finally {
    btn.disabled = false; btn.innerHTML = "&#x21bb; Run cross-check";
  }
}

function toast(msg, kind) {
  const t = $("toast");
  t.textContent = msg; t.className = `toast t-${kind}`; t.hidden = false;
  clearTimeout(toast.h); toast.h = setTimeout(() => t.hidden = true, 7000);
}

/* ---------------------------------------------------------------- wiring */

function renderAll() { renderKpis(); renderCampus(); renderOver(); renderJobTitles(); renderPeople(); }

function populateCampusFilter() {
  $("f-campus").innerHTML = `<option value="ALL">All campuses</option>` +
    REPORT.campuses.map(c => `<option value="${esc(c.code)}">${esc(c.campus)}</option>`).join("");
  $("f-campus").value = state.campus;
}

function init() {
  populateCampusFilter();
  $("f-status").innerHTML = FILTERS.map(([k, l]) => `<option value="${k}">${l}</option>`).join("");
  $("f-status").value = state.status;
  $("f-campus").onchange = e => { state.campus = e.target.value; renderAll(); };
  $("f-status").onchange = e => { state.status = e.target.value; renderAll(); };
  $("q").oninput = e => { state.q = e.target.value; renderPeople(); };
  $("over-only").onchange = renderOver;
  populateTitleFilter();
  ["jt-title", "jt-region", "jt-view"].forEach(id => $(id).onchange = renderJobTitles);
  $("export").onclick = () => downloadCsv(`fte_adp_crosscheck_${state.campus}_${state.status}.csv`, filteredPeople(), PEOPLE_CSV);
  $("m-q").oninput = renderModal;
  $("m-close").onclick = closeModal;
  $("modal").onclick = e => { if (e.target.id === "modal") closeModal(); };
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !$("modal").hidden) closeModal(); });
  $("m-export").onclick = () => modal.kind === "titles"
    ? downloadCsv(`${modal.title}.csv`, modal.rows, ["campus", "job_code", "job_title", "approved", "adp_active", "variance", "unapproved"])
    : downloadCsv(`${modal.title}.csv`, modal.rows, PEOPLE_CSV);
  $("run").onclick = runCrosscheck;
  // One delegated handler for every clickable number, campus name and sortable header
  document.addEventListener("click", e => {
    const d = e.target.closest("[data-d]");
    if (d) { openDetail(d.dataset.d); return; }
    const c = e.target.closest("[data-campus]");
    if (c) { state.campus = state.campus === c.dataset.campus ? "ALL" : c.dataset.campus; $("f-campus").value = state.campus; renderAll(); return; }
    const th = e.target.closest("th.sort");
    if (th) { const k = th.dataset.k; state.dir = state.sort === k ? -state.dir : 1; state.sort = k; renderPeople(); }
  });
  renderMeta(); renderAll(); detectApi();
}
init();
</script>
</body>
</html>
"""


def generate_files():
    with open(REPORT_PATH) as f:
        report = json.load(f)
    with open(LOGO_PATH, "rb") as f:
        logo = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    # "</" and "<?" would break the inline <script> / Apps Script templating
    report_js = json.dumps(report, separators=(",", ":")).replace("</", "<\\/").replace("<?", "<\\?")
    html = HTML_TEMPLATE.replace("__LOGO__", logo).replace("__REPORT__", report_js)
    for rel in OUTPUTS:
        with open(os.path.join(BASE_DIR, rel), "w") as f:
            f.write(html)
        print(f"Wrote {rel} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    generate_files()
