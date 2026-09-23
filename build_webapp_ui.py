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
    --focus: #2563eb;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0b1220; --surface: #111a2c; --surface-2: #0f1727; --border: #24324a;
      --ink: #e5e9f0; --ink-2: #aab4c3; --ink-3: #8592a6;
      --ok: #4ade80; --ok-bg: #12301f; --warn: #fbbf24; --warn-bg: #3a2a0a;
      --bad: #f87171; --bad-bg: #3b1414; --info: #93c5fd; --info-bg: #13274a;
      --muted-bg: #1a2438; --focus: #60a5fa;
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
  @media (max-width: 640px) { header { padding: 12px 16px; } .kpi .val { font-size: 22px; } }
</style>
</head>
<body>
<header>
  <img src="__LOGO__" alt="SST logo">
  <div>
    <h1>FTE List vs. ADP Position Cross-Check</h1>
    <p id="meta"></p>
  </div>
</header>
<main>
  <div class="kpis" id="kpis"></div>

  <h2>Campus summary</h2>
  <p class="sub">Approved slots come from each campus's 2026-27 Approved FTE List. ADP Active is the headcount whose ADP Position tab Location is that campus. Click a campus to filter everything below.</p>
  <div class="card scroll" style="max-height:none"><table id="t-campus"></table></div>

  <h2>Overhire check by job title</h2>
  <p class="sub">ADP active headcount per campus and ADP job title, compared with the number of approved slots for that title. A positive difference is an overhire.</p>
  <div class="toolbar">
    <label class="chk"><input type="checkbox" id="over-only" checked> Show overhires only</label>
    <span class="count" id="over-count"></span>
  </div>
  <div class="card scroll"><table id="t-over"></table></div>

  <h2>Person-level cross-check</h2>
  <p class="sub">Every person on an approved FTE list matched to ADP by Position ID (or name when the Position ID changed), plus active ADP staff who are on no list. Red text marks the field that differs from ADP.</p>
  <div class="toolbar">
    <input type="search" id="q" placeholder="Search name, title, Position ID…">
    <select id="f-campus"></select>
    <select id="f-status"></select>
    <button class="btn" id="export">Export CSV</button>
    <span class="count" id="p-count"></span>
  </div>
  <div class="card scroll"><table id="t-people"></table></div>
  <p class="note" id="foot"></p>
</main>

<script>
const REPORT = __REPORT__;

const STATUS = {
  MATCH:               { label: "Matches ADP",            cls: "p-ok" },
  LOCATION_MISMATCH:   { label: "Location differs",       cls: "p-warn" },
  TITLE_MISMATCH:      { label: "Title differs",          cls: "p-warn" },
  NAME_MISMATCH:       { label: "Name differs",           cls: "p-info" },
  NOT_ACTIVE_IN_ADP:   { label: "Terminated in ADP",      cls: "p-bad" },
  NOT_IN_ADP:          { label: "Not found in ADP",       cls: "p-bad" },
  NOT_ON_LIST:         { label: "Not on FTE list",        cls: "p-bad" },
  NO_FTE_LIST:         { label: "No FTE list for campus", cls: "p-muted" },
  VACANT_STILL_ACTIVE: { label: "Vacant but still active", cls: "p-info" },
  OPEN:                { label: "Open slot",              cls: "p-muted" },
};
// Filter keys: an issue filter matches any record carrying that issue
const FILTERS = [
  ["ALL", "All records"],
  ["ANY_ISSUE", "Any discrepancy"],
  ["LOCATION_MISMATCH", "Location differs"],
  ["TITLE_MISMATCH", "Title differs"],
  ["NAME_MISMATCH", "Name differs"],
  ["NOT_ACTIVE", "On list, not active in ADP"],
  ["NOT_ON_LIST", "Active in ADP, not on list"],
  ["MATCH", "Matches ADP"],
  ["OPEN", "Open slots"],
];

const state = { campus: "ALL", status: "ANY_ISSUE", q: "", sort: null, dir: 1 };
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = n => Number(n).toLocaleString();

function matchesFilter(r, f) {
  if (f === "ALL") return true;
  if (f === "ANY_ISSUE") return r.issues.length > 0;
  if (f === "NOT_ACTIVE") return r.status === "NOT_ACTIVE_IN_ADP" || r.status === "NOT_IN_ADP";
  if (f === "MATCH") return r.status === "MATCH" || r.status === "VACANT_STILL_ACTIVE";
  if (f === "OPEN") return r.status === "OPEN";
  return r.issues.includes(f);
}

function inCampus(r) { return state.campus === "ALL" || r.campus_code === state.campus; }

function renderMeta() {
  const lists = REPORT.campuses.filter(c => c.has_list).length;
  const nc = Object.entries(REPORT.non_campus_active || {}).map(([k, v]) => `${k} ${v}`).join(", ");
  $("meta").textContent = `ADP pulled ${REPORT.adp_pulled_at} · ${lists} campus FTE lists · report built ${REPORT.generated_at}`;
  $("foot").textContent = `Central/regional office staff are not on campus FTE lists and are excluded from the counts (${nc}). ` +
    `Titles are compared by ADP job code (e.g. 11TEACH); the FTE list "Assignment" (grade/subject) is shown for reference only.`;
}

function renderKpis() {
  const recs = REPORT.records.filter(inCampus);
  const camps = REPORT.campuses.filter(c => state.campus === "ALL" || c.code === state.campus);
  const sum = k => camps.reduce((a, c) => a + c[k], 0);
  const n = f => recs.filter(r => matchesFilter(r, f)).length;
  const tiles = [
    ["Approved slots", sum("approved"), "on 2026-27 FTE lists", "", null],
    ["ADP active", sum("adp_active"), "at these campus locations", "", null],
    ["Matches ADP", n("MATCH"), "name, location & title agree", "ok", "MATCH"],
    ["Location differs", n("LOCATION_MISMATCH"), "ADP campus ≠ FTE list campus", "warn", "LOCATION_MISMATCH"],
    ["Title differs", n("TITLE_MISMATCH"), "ADP job title ≠ FTE list title", "warn", "TITLE_MISMATCH"],
    ["Name differs", n("NAME_MISMATCH"), "same Position ID, different name", "info", "NAME_MISMATCH"],
    ["On list, not active", n("NOT_ACTIVE"), "terminated / not found in ADP", "bad", "NOT_ACTIVE"],
    ["Not on FTE list", n("NOT_ON_LIST"), "active in ADP, never approved", "bad", "NOT_ON_LIST"],
    ["Overhire", sum("overhire"), "headcount above approved, by title", "bad", "OVERHIRE"],
  ];
  $("kpis").innerHTML = tiles.map(([l, v, h, cls, f]) =>
    `<button class="kpi ${cls} ${f && f === state.status ? "active" : ""}" data-f="${f || ""}">
       <div class="lbl">${l}</div><div class="val">${fmt(v)}</div><div class="hint">${h}</div></button>`).join("");
  $("kpis").querySelectorAll(".kpi").forEach(b => b.onclick = () => {
    const f = b.dataset.f;
    if (!f) return;
    if (f === "OVERHIRE") { $("over-only").checked = true; renderOver(); $("t-over").scrollIntoView({ behavior: "smooth", block: "center" }); return; }
    state.status = f; $("f-status").value = f; renderAll();
    $("t-people").scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function renderCampus() {
  const cols = [["Campus"], ["Region"], ["Approved", 1], ["ADP active", 1], ["Diff", 1], ["Matched", 1], ["Open slots", 1],
    ["Location differs", 1], ["Title differs", 1], ["Not active in ADP", 1], ["Not on list", 1], ["Overhire", 1]];
  const rows = REPORT.campuses.map(c => {
    const d = c.adp_active - c.approved;
    return `<tr class="click ${state.campus === c.code ? "sel" : ""}" data-c="${esc(c.code)}">
      <td><b>${esc(c.campus)}</b> <span class="dim">(${esc(c.code)})</span>${c.has_list ? "" : ' <span class="pill p-muted">no FTE list</span>'}</td>
      <td>${esc(c.region)}</td><td class="num">${c.approved}</td><td class="num">${c.adp_active}</td>
      <td class="num ${d > 0 ? "over" : "under"}">${d > 0 ? "+" : ""}${d}</td>
      <td class="num">${c.matched}</td><td class="num">${c.open}</td>
      <td class="num">${c.location_mismatch || '<span class="dim">0</span>'}</td>
      <td class="num">${c.title_mismatch || '<span class="dim">0</span>'}</td>
      <td class="num">${c.not_active || '<span class="dim">0</span>'}</td>
      <td class="num">${c.not_on_list ? `<span class="over">${c.not_on_list}</span>` : '<span class="dim">0</span>'}</td>
      <td class="num">${c.overhire ? `<span class="over">+${c.overhire}</span>` : '<span class="dim">0</span>'}</td></tr>`;
  });
  const T = REPORT.campuses.reduce((a, c) => { for (const k in c) if (typeof c[k] === "number") a[k] = (a[k] || 0) + c[k]; return a; }, {});
  rows.push(`<tr><td><b>All campuses</b></td><td></td><td class="num"><b>${T.approved}</b></td><td class="num"><b>${T.adp_active}</b></td>
    <td class="num"><b>${T.adp_active - T.approved > 0 ? "+" : ""}${T.adp_active - T.approved}</b></td><td class="num"><b>${T.matched}</b></td>
    <td class="num"><b>${T.open}</b></td><td class="num"><b>${T.location_mismatch}</b></td><td class="num"><b>${T.title_mismatch}</b></td>
    <td class="num"><b>${T.not_active}</b></td><td class="num"><b>${T.not_on_list}</b></td><td class="num"><b>+${T.overhire}</b></td></tr>`);
  $("t-campus").innerHTML = `<thead><tr>${cols.map(([h, n]) => `<th class="${n ? "num" : ""}">${h}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody>`;
  $("t-campus").querySelectorAll("tr[data-c]").forEach(tr => tr.onclick = () => {
    state.campus = state.campus === tr.dataset.c ? "ALL" : tr.dataset.c;
    $("f-campus").value = state.campus; renderAll();
  });
}

function renderOver() {
  const only = $("over-only").checked;
  const rows = REPORT.title_counts.filter(t => (state.campus === "ALL" || t.campus_code === state.campus) && (!only || t.variance > 0));
  $("over-count").textContent = `${rows.length} campus × title rows`;
  $("t-over").innerHTML = `<thead><tr><th>Campus</th><th>ADP job title</th><th class="num">Approved</th><th class="num">ADP active</th>
      <th class="num">Difference</th><th>In ADP under this campus &amp; title without an approved slot for it</th></tr></thead><tbody>` +
    (rows.length ? rows.map(t => `<tr><td>${esc(t.campus)}</td><td>${esc(t.job_code)} - ${esc(t.job_title)}</td>
      <td class="num">${t.approved}</td><td class="num">${t.adp_active}</td>
      <td class="num ${t.variance > 0 ? "over" : "under"}">${t.variance > 0 ? "+" : ""}${t.variance}</td>
      <td>${t.unapproved.map(esc).join(", ") || '<span class="dim">—</span>'}</td></tr>`).join("")
      : `<tr><td colspan="6" class="dim">No overhires for this selection.</td></tr>`) + "</tbody>";
}

const PCOLS = [
  ["status", "Status"], ["campus", "FTE list campus"], ["fte_name", "FTE list name"], ["adp_name", "ADP name"],
  ["position_id", "Position ID"], ["fte_title", "FTE list title"], ["adp_title", "ADP job title"],
  ["adp_campus", "ADP location"], ["assignment", "Assignment"], ["list_status", "List status"], ["detail", "Notes"],
];

function filteredPeople() {
  const q = state.q.toLowerCase();
  let rows = REPORT.records.filter(r => inCampus(r) && matchesFilter(r, state.status) &&
    (!q || [r.fte_name, r.adp_name, r.fte_title, r.adp_title, r.position_id, r.adp_position_id, r.assignment, r.adp_campus]
      .some(v => String(v || "").toLowerCase().includes(q))));
  if (state.sort) {
    const k = state.sort;
    rows = rows.slice().sort((a, b) => String(a[k] || "").localeCompare(String(b[k] || "")) * state.dir);
  }
  return rows;
}

function renderPeople() {
  const rows = filteredPeople();
  $("p-count").textContent = `${fmt(rows.length)} of ${fmt(REPORT.records.length)} records`;
  const shown = rows.slice(0, 1500);
  const body = shown.map(r => {
    const iss = new Set(r.issues);
    const pills = (r.issues.length ? r.issues : [r.status]).map(s => `<span class="pill ${STATUS[s].cls}">${STATUS[s].label}</span>`).join("");
    const pid = r.adp_position_id && r.position_id && r.adp_position_id !== r.position_id
      ? `${esc(r.position_id)}<br><span class="dim">ADP: ${esc(r.adp_position_id)}</span>` : esc(r.position_id || r.adp_position_id);
    return `<tr><td>${pills}</td><td>${esc(r.campus)}</td><td>${esc(r.fte_name)}</td>
      <td class="${iss.has("NAME_MISMATCH") ? "diff" : ""}">${esc(r.adp_name) || '<span class="dim">—</span>'}</td>
      <td>${pid}</td><td>${esc(r.fte_title)}</td>
      <td class="${iss.has("TITLE_MISMATCH") ? "diff" : ""}">${esc(r.adp_title) || '<span class="dim">—</span>'}</td>
      <td class="${iss.has("LOCATION_MISMATCH") ? "diff" : ""}">${esc(r.adp_campus) || '<span class="dim">—</span>'}</td>
      <td>${esc(r.assignment)}</td><td>${esc(r.list_status)}</td>
      <td>${esc(r.detail)}</td></tr>`;
  }).join("");
  $("t-people").innerHTML = `<thead><tr>${PCOLS.map(([k, h]) => `<th data-k="${k}">${h}${state.sort === k ? (state.dir > 0 ? " ▲" : " ▼") : ""}</th>`).join("")}</tr></thead>
    <tbody>${body || `<tr><td colspan="${PCOLS.length}" class="dim">No records match these filters.</td></tr>`}
    ${rows.length > shown.length ? `<tr><td colspan="${PCOLS.length}" class="dim">Showing first ${shown.length}; narrow the filters or export CSV for all.</td></tr>` : ""}</tbody>`;
  $("t-people").querySelectorAll("th").forEach(th => th.onclick = () => {
    const k = th.dataset.k;
    state.dir = state.sort === k ? -state.dir : 1; state.sort = k; renderPeople();
  });
}

function exportCsv() {
  const cols = ["status", "issues", "campus", "fte_name", "adp_name", "position_id", "adp_position_id", "fte_title", "adp_title",
    "adp_campus", "adp_location", "worker_type", "assignment", "list_status", "notes", "adp_status", "detail", "source"];
  const cell = v => `"${String(Array.isArray(v) ? v.join("; ") : v ?? "").replace(/"/g, '""')}"`;
  const csv = [cols.join(",")].concat(filteredPeople().map(r => cols.map(c => cell(r[c])).join(","))).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = `fte_adp_crosscheck_${state.campus}_${state.status}.csv`.replace(/\s+/g, "_");
  a.click();
}

function renderAll() { renderKpis(); renderCampus(); renderOver(); renderPeople(); }

function init() {
  $("f-campus").innerHTML = `<option value="ALL">All campuses</option>` +
    REPORT.campuses.map(c => `<option value="${esc(c.code)}">${esc(c.campus)}</option>`).join("");
  $("f-status").innerHTML = FILTERS.map(([k, l]) => `<option value="${k}">${l}</option>`).join("");
  $("f-status").value = state.status;
  $("f-campus").onchange = e => { state.campus = e.target.value; renderAll(); };
  $("f-status").onchange = e => { state.status = e.target.value; renderAll(); };
  $("q").oninput = e => { state.q = e.target.value; renderPeople(); };
  $("over-only").onchange = renderOver;
  $("export").onclick = exportCsv;
  renderMeta(); renderAll();
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
