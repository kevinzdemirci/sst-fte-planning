/**
 * SST 2027-28 FTE Planning Portal - Google Apps Script backend
 *
 * The Google Sheet is the database. Staff never edit the sheet directly (it is not
 * shared with them); every change goes through this script, which checks the user's
 * role and writes one Change_Log row per changed field.
 *
 * Roles (Editors sheet; the script owner is always admin):
 *   admin  - add / remove position slots, edit anything, manage access
 *   editor - fill slots (people, status, Position ID, notes) at their campuses
 *   viewer - read only
 *
 * Script properties (Project Settings > Script properties) for "Refresh ADP data":
 *   GITHUB_TOKEN     fine-grained token, Actions: Read and write on the repo
 *   GITHUB_REPO      e.g. kevinzdemirci/sst-fte-planning
 *   GITHUB_WORKFLOW  adp_refresh_2027.yml  (optional, this is the default)
 */

const SHEETS = {
  POSITIONS: "Positions", LOG: "Change_Log", EDITORS: "Editors", CAMPUSES: "Campuses",
  TITLES: "Job_Titles", ADP: "ADP_Positions", SETTINGS: "Settings",
};
const STATUSES = ["Returning", "New hire", "Not returning", "Open"];
const NAMED_STATUSES = ["Returning", "New hire", "Not returning"];
const EDITOR_FIELDS = ["assignment", "first_name", "last_name", "adp_position_id", "status", "notes"];
const ADMIN_FIELDS = ["campus_code", "job_code"];
const ROLES = ["admin", "editor", "viewer"];
const ROLE_RANK = { viewer: 1, editor: 2, admin: 3 };
const TZ = "America/Chicago";

/* ------------------------------------------------------------------ web app */

function doGet() {
  const user = currentUser_();
  if (!user) {
    return HtmlService.createHtmlOutput(
      '<div style="font-family:sans-serif;max-width:520px;margin:15vh auto;line-height:1.5">' +
      "<h2>No access yet</h2><p>You are signed in as <b>" + escapeHtml_(activeEmail_() || "an unknown account") +
      "</b>, which is not on the 2027-28 FTE Planning access list.</p>" +
      "<p>Ask the FTE Planning administrator to add you.</p></div>"
    ).setTitle("SST FTE Planning");
  }
  return HtmlService.createHtmlOutputFromFile("Portal")
    .setTitle("SST " + setting_("school_year") + " FTE Planning")
    .addMetaTag("viewport", "width=device-width, initial-scale=1");
}

/* ------------------------------------------------------------------ users */

function activeEmail_() {
  try { return (Session.getActiveUser().getEmail() || "").toLowerCase().trim(); } catch (e) { return ""; }
}

function currentUser_() {
  const email = activeEmail_();
  if (!email) return null;
  let owner = "";
  try { owner = (Session.getEffectiveUser().getEmail() || "").toLowerCase().trim(); } catch (e) {}
  if (email === owner) return { email: email, name: "FTE Planning Administrator", role: "admin", campuses: ["ALL"], owner: true };
  const row = readTable_(SHEETS.EDITORS).rows.find(function (r) { return String(r.email).toLowerCase().trim() === email; });
  if (!row || ROLES.indexOf(row.role) < 0) return null;
  return { email: email, name: row.name || email, role: row.role, campuses: parseCampuses_(row.campuses), owner: false };
}

function requireUser_(minRole) {
  const u = currentUser_();
  if (!u) throw new Error("You do not have access to the FTE Planning portal.");
  if (ROLE_RANK[u.role] < ROLE_RANK[minRole]) throw new Error("Your role (" + u.role + ") cannot do this.");
  return u;
}

function parseCampuses_(v) {
  const list = String(v || "").split(/[,;\s]+/).map(function (s) { return s.trim(); }).filter(String);
  return list.length ? list : ["ALL"];
}

function canEditCampus_(u, code) {
  if (u.role === "admin") return true;
  return u.role === "editor" && (u.campuses.indexOf("ALL") >= 0 || u.campuses.indexOf(code) >= 0);
}

/* ------------------------------------------------------------------ sheet helpers */

function ss_() {
  const id = PropertiesService.getScriptProperties().getProperty("SPREADSHEET_ID");
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function sheet_(name) {
  const sh = ss_().getSheetByName(name);
  if (!sh) throw new Error('Missing sheet "' + name + '". Was the planning database imported?');
  return sh;
}

// Display values keep IDs, dates and codes exactly as shown in the sheet (and avoid Date objects).
function readTable_(name) {
  const sh = sheet_(name);
  const values = sh.getDataRange().getDisplayValues();
  const headers = values.shift() || [];
  const rows = values.map(function (v, i) {
    const o = { _row: i + 2 };
    headers.forEach(function (h, j) { o[h] = v[j]; });
    return o;
  });
  return { sheet: sh, headers: headers, rows: rows };
}

function writeRow_(table, rowNumber, obj) {
  const values = [table.headers.map(function (h) { return obj[h] === undefined || obj[h] === null ? "" : String(obj[h]); })];
  // Plain-text format so Sheets never turns IDs or timestamps into numbers / dates
  table.sheet.getRange(rowNumber, 1, 1, table.headers.length).setNumberFormat("@").setValues(values);
}

function appendRows_(name, headers, objs) {
  if (!objs.length) return;
  const sh = sheet_(name);
  const values = objs.map(function (o) { return headers.map(function (h) { return o[h] === undefined ? "" : String(o[h]); }); });
  sh.getRange(sh.getLastRow() + 1, 1, values.length, headers.length).setNumberFormat("@").setValues(values);
}

function now_() { return Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd HH:mm:ss"); }

function setting_(key) {
  const row = readTable_(SHEETS.SETTINGS).rows.find(function (r) { return r.key === key; });
  return row ? row.value : "";
}

function log_(user, entries) {
  const headers = readTable_(SHEETS.LOG).headers;
  const ts = now_();
  appendRows_(SHEETS.LOG, headers, entries.map(function (e) {
    return Object.assign({ timestamp: ts, user: user.email }, e);
  }));
}

function withLock_(fn) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error("The portal is busy saving another change. Please try again.");
  try { return fn(); } finally { lock.releaseLock(); }
}

function escapeHtml_(s) {
  return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
}

function clean_(obj) {
  const o = {};
  Object.keys(obj).forEach(function (k) { if (k !== "_row") o[k] = obj[k]; });
  return o;
}

/* ------------------------------------------------------------------ read API */

function getBootstrap() {
  const u = requireUser_("viewer");
  const adp = readTable_(SHEETS.ADP);
  return {
    user: { email: u.email, name: u.name, role: u.role, campuses: u.campuses },
    schoolYear: setting_("school_year"),
    campuses: readTable_(SHEETS.CAMPUSES).rows.map(clean_),
    jobTitles: readTable_(SHEETS.TITLES).rows.map(clean_),
    positions: readTable_(SHEETS.POSITIONS).rows.map(clean_),
    adp: { pulledAt: setting_("adp_pulled_at"), headers: adp.headers,
           rows: adp.rows.map(function (r) { return adp.headers.map(function (h) { return r[h]; }); }) },
    editors: u.role === "admin" ? readTable_(SHEETS.EDITORS).rows.map(clean_) : [],
    githubConfigured: !!PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN"),
    serverTime: now_(),
  };
}

function getChangeLog(filter) {
  requireUser_("viewer");
  filter = filter || {};
  let rows = readTable_(SHEETS.LOG).rows.map(clean_);
  if (filter.position_key) rows = rows.filter(function (r) { return r.position_key === filter.position_key; });
  rows.reverse();
  return rows.slice(0, filter.limit || 5000);
}

/* ------------------------------------------------------------------ write API: positions */

function savePosition(input) {
  return withLock_(function () {
    const u = requireUser_("editor");
    const t = readTable_(SHEETS.POSITIONS);
    const p = normalizePosition_(input);
    validatePosition_(p);
    const ts = now_();

    if (!input.position_key) {
      if (u.role !== "admin") throw new Error("Only an admin can add position slots.");
      const next = t.rows.reduce(function (m, r) { return Math.max(m, parseInt(String(r.position_key).replace(/\D/g, ""), 10) || 0); }, 0) + 1;
      const rec = Object.assign(p, {
        position_key: "P-" + ("0000" + next).slice(-5), school_year: setting_("school_year"),
        created_at: ts, created_by: u.email, updated_at: ts, updated_by: u.email, deleted: "",
      });
      writeRow_(t, t.sheet.getLastRow() + 1, rec);
      log_(u, [{ action: "ADD_POSITION", position_key: rec.position_key, campus_code: rec.campus_code, job_code: rec.job_code,
                 new_value: summary_(rec), note: input.change_note || "" }]);
      return rec;
    }

    const cur = t.rows.find(function (r) { return r.position_key === input.position_key; });
    if (!cur) throw new Error("Position " + input.position_key + " no longer exists. Reload the portal.");
    if (cur.deleted) throw new Error("Position " + input.position_key + " was removed. Reload the portal.");
    if (input.expected_updated_at !== cur.updated_at) {
      throw new Error("This position was changed by " + cur.updated_by + " at " + cur.updated_at +
                      " after you opened it. Reload to see the latest, then make your change again.");
    }
    if (!canEditCampus_(u, cur.campus_code)) throw new Error("You can only edit positions at your assigned campuses.");

    const fields = EDITOR_FIELDS.concat(ADMIN_FIELDS);
    const changed = fields.filter(function (f) { return String(cur[f] || "") !== String(p[f] || ""); });
    if (!changed.length) return clean_(cur);
    const forbidden = changed.filter(function (f) { return ADMIN_FIELDS.indexOf(f) >= 0; });
    if (forbidden.length && u.role !== "admin") throw new Error("Only an admin can change a position's campus or job title.");
    if (!canEditCampus_(u, p.campus_code)) throw new Error("You cannot move a position to that campus.");

    const rec = Object.assign(clean_(cur), p, { updated_at: ts, updated_by: u.email });
    writeRow_(t, cur._row, rec);
    log_(u, changed.map(function (f) {
      return { action: "UPDATE", position_key: rec.position_key, campus_code: rec.campus_code, job_code: rec.job_code,
               field: f, old_value: cur[f] || "", new_value: rec[f] || "", note: input.change_note || "" };
    }));
    return rec;
  });
}

function deletePosition(key, expectedUpdatedAt, note) {
  return withLock_(function () {
    const u = requireUser_("admin");
    if (!String(note || "").trim()) throw new Error("A reason is required to remove a position.");
    const t = readTable_(SHEETS.POSITIONS);
    const cur = t.rows.find(function (r) { return r.position_key === key; });
    if (!cur || cur.deleted) throw new Error("Position " + key + " is not active. Reload the portal.");
    if (expectedUpdatedAt !== cur.updated_at) throw new Error("This position was changed by " + cur.updated_by + " at " + cur.updated_at + ". Reload first.");
    const rec = Object.assign(clean_(cur), { deleted: "yes", updated_at: now_(), updated_by: u.email });
    writeRow_(t, cur._row, rec);
    log_(u, [{ action: "REMOVE_POSITION", position_key: key, campus_code: cur.campus_code, job_code: cur.job_code,
               old_value: summary_(cur), note: note }]);
    return rec;
  });
}

function restorePosition(key, note) {
  return withLock_(function () {
    const u = requireUser_("admin");
    const t = readTable_(SHEETS.POSITIONS);
    const cur = t.rows.find(function (r) { return r.position_key === key; });
    if (!cur || !cur.deleted) throw new Error("Position " + key + " is not removed.");
    const rec = Object.assign(clean_(cur), { deleted: "", updated_at: now_(), updated_by: u.email });
    writeRow_(t, cur._row, rec);
    log_(u, [{ action: "RESTORE_POSITION", position_key: key, campus_code: cur.campus_code, job_code: cur.job_code,
               new_value: summary_(rec), note: note || "" }]);
    return rec;
  });
}

function normalizePosition_(i) {
  const s = function (v, max) { return String(v === undefined || v === null ? "" : v).replace(/\s+/g, " ").trim().slice(0, max || 120); };
  const p = {
    campus_code: s(i.campus_code, 10), job_code: s(i.job_code, 20).toUpperCase(), assignment: s(i.assignment, 200),
    first_name: s(i.first_name, 60), last_name: s(i.last_name, 60), adp_position_id: s(i.adp_position_id, 20).toUpperCase(),
    status: s(i.status, 20), notes: s(i.notes, 1000),
  };
  if (p.status === "Open") { p.first_name = ""; p.last_name = ""; p.adp_position_id = ""; }
  return p;
}

function validatePosition_(p) {
  if (STATUSES.indexOf(p.status) < 0) throw new Error("Choose a status.");
  if (!readTable_(SHEETS.CAMPUSES).rows.some(function (r) { return r.code === p.campus_code; })) throw new Error("Unknown campus.");
  if (!readTable_(SHEETS.TITLES).rows.some(function (r) { return r.job_code === p.job_code; })) throw new Error("Unknown job title.");
  if (NAMED_STATUSES.indexOf(p.status) >= 0 && (!p.first_name || !p.last_name)) {
    throw new Error('Status "' + p.status + '" needs the person\'s first and last name.');
  }
  if (p.adp_position_id && !/^[A-Z0-9]{3,20}$/.test(p.adp_position_id)) throw new Error("ADP Position ID should look like ELA110850.");
}

function summary_(p) {
  const who = [p.first_name, p.last_name].join(" ").trim();
  return [p.campus_code, p.job_code, p.assignment, who || "(open)", p.status].filter(String).join(" | ");
}

/* ------------------------------------------------------------------ write API: access */

function saveEditor(input) {
  return withLock_(function () {
    const u = requireUser_("admin");
    const email = String(input.email || "").toLowerCase().trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error("Enter a valid email address.");
    if (ROLES.indexOf(input.role) < 0) throw new Error("Choose a role.");
    const codes = readTable_(SHEETS.CAMPUSES).rows.map(function (r) { return r.code; });
    const campuses = parseCampuses_(input.campuses);
    if (campuses.indexOf("ALL") < 0 && campuses.some(function (c) { return codes.indexOf(c) < 0; })) throw new Error("Unknown campus code.");
    const t = readTable_(SHEETS.EDITORS);
    const cur = t.rows.find(function (r) { return String(r.email).toLowerCase().trim() === email; });
    const rec = { email: email, name: String(input.name || "").trim().slice(0, 80), role: input.role,
                  campuses: campuses.join(","), added_at: cur ? cur.added_at : now_(), added_by: cur ? cur.added_by : u.email };
    writeRow_(t, cur ? cur._row : t.sheet.getLastRow() + 1, rec);
    log_(u, [{ action: cur ? "ACCESS_CHANGED" : "ACCESS_GRANTED", field: email,
               old_value: cur ? cur.role + " @ " + cur.campuses : "", new_value: rec.role + " @ " + rec.campuses }]);
    return rec;
  });
}

function removeEditor(email) {
  return withLock_(function () {
    const u = requireUser_("admin");
    const t = readTable_(SHEETS.EDITORS);
    const cur = t.rows.find(function (r) { return String(r.email).toLowerCase().trim() === String(email).toLowerCase().trim(); });
    if (!cur) throw new Error("That person is not on the access list.");
    t.sheet.deleteRow(cur._row);
    log_(u, [{ action: "ACCESS_REMOVED", field: cur.email, old_value: cur.role + " @ " + cur.campuses }]);
    return true;
  });
}

/* ------------------------------------------------------------------ ADP refresh via GitHub Actions */

function github_(method, path, body) {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty("GITHUB_TOKEN"), repo = props.getProperty("GITHUB_REPO");
  if (!token || !repo) throw new Error("ADP refresh is not set up yet (GITHUB_TOKEN / GITHUB_REPO script properties).");
  const res = UrlFetchApp.fetch("https://api.github.com/repos/" + repo + path, {
    method: method, muteHttpExceptions: true, contentType: "application/json",
    headers: { Authorization: "Bearer " + token, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
    payload: body ? JSON.stringify(body) : undefined,
  });
  const code = res.getResponseCode();
  if (code >= 300) throw new Error("GitHub returned " + code + ". Check the GITHUB_TOKEN permissions and GITHUB_REPO.");
  return code === 204 ? null : JSON.parse(res.getContentText());
}

function workflow_() {
  return PropertiesService.getScriptProperties().getProperty("GITHUB_WORKFLOW") || "adp_refresh_2027.yml";
}

function latestRun_() {
  const d = github_("get", "/actions/workflows/" + workflow_() + "/runs?event=workflow_dispatch&per_page=1");
  const r = (d.workflow_runs || [])[0];
  return r ? { id: r.id, status: r.status, conclusion: r.conclusion, url: r.html_url, created_at: r.created_at } : null;
}

function startAdpRefresh() {
  return withLock_(function () {
    const u = requireUser_("editor");
    const last = latestRun_();
    if (last && last.status !== "completed") return { alreadyRunning: true, run: last };
    github_("post", "/actions/workflows/" + workflow_() + "/dispatches", { ref: "main", inputs: { sheet_id: ss_().getId() } });
    log_(u, [{ action: "ADP_REFRESH_REQUESTED", note: "Pull of ADP Position data requested" }]);
    return { alreadyRunning: false, requestedAt: new Date().toISOString() };
  });
}

function getAdpRefreshStatus() {
  requireUser_("viewer");
  return { run: latestRun_(), pulledAt: setting_("adp_pulled_at") };
}
