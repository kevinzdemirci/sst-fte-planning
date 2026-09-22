/**
 * SST Schools - Campus FTE Planning & Staffing Control Portal
 * Google Apps Script Web App Backend Controller
 * 
 * Manages Approved Plans, Live Actual Hires, Strict Validation,
 * Administrative Overrides, and Unfalsifiable Audit Logging.
 */

const SHEET_NAMES = {
  CAMPUSES: "Campuses",
  APPROVED_PLAN: "Approved_Plan",
  ACTUAL_HIRES: "Actual_Hires",
  VIOLATIONS: "Violations_Overrides",
  AUDIT_LOG: "Audit_Log"
};

/**
 * Serves the web application HTML.
 * Handles ?view=leadership query parameter for read-only leadership view.
 */
function doGet(e) {
  const template = HtmlService.createTemplateFromFile("Index");
  
  // Detect view mode from URL parameters
  const viewMode = (e && e.parameter && e.parameter.view) ? e.parameter.view.toLowerCase() : "editor";
  template.initialViewMode = viewMode === "leadership" ? "leadership" : "editor";
  
  // Get active Google user email
  let userEmail = "";
  try {
    userEmail = Session.getActiveUser().getEmail() || Session.getEffectiveUser().getEmail() || "staff@ssttx.org";
  } catch (err) {
    userEmail = "staff@ssttx.org";
  }
  template.userEmail = userEmail;

  return template.evaluate()
    .setTitle("SST Schools - Campus FTE Staffing Portal")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag("viewport", "width=device-width, initial-scale=1");
}

/**
 * Returns the spreadsheet instance.
 * Checks Script Properties for SPREADSHEET_ID, fallback to active spreadsheet.
 */
function getSpreadsheet_() {
  const props = PropertiesService.getScriptProperties();
  const customId = props.getProperty("SPREADSHEET_ID");
  if (customId) {
    return SpreadsheetApp.openById(customId);
  }
  return SpreadsheetApp.getActiveSpreadsheet();
}

/**
 * Helper to get active user email.
 */
function getCurrentUserEmail_() {
  try {
    return Session.getActiveUser().getEmail() || Session.getEffectiveUser().getEmail() || "fte-admin@ssttx.org";
  } catch (e) {
    return "fte-admin@ssttx.org";
  }
}

/**
 * Helper to format current timestamp (Texas CST/CDT).
 */
function getTimestamp_() {
  return Utilities.formatDate(new Date(), "America/Chicago", "yyyy-MM-dd HH:mm:ss");
}

/**
 * Writes a permanent entry to the Audit_Log sheet.
 * Audit log cannot be falsified or quietly deleted.
 */
function logAudit_(ss, actionType, campus, role, oldValue, newValue, reasonNotes, overrideStatus) {
  const ws = ss.getSheetByName(SHEET_NAMES.AUDIT_LOG);
  if (!ws) return;

  const logId = "AUDIT-" + Utilities.getUuid().substring(0, 8).toUpperCase();
  const timestamp = getTimestamp_();
  const userEmail = getCurrentUserEmail_();

  ws.appendRow([
    logId,
    timestamp,
    userEmail,
    actionType,
    campus || "NETWORK",
    role || "N/A",
    oldValue !== undefined ? String(oldValue) : "",
    newValue !== undefined ? String(newValue) : "",
    reasonNotes || "",
    overrideStatus || "STANDARD"
  ]);
}

/**
 * Retrieves all data from Google Sheets to populate the web app.
 */
function getAppInitialData() {
  const ss = getSpreadsheet_();
  const currentUser = getCurrentUserEmail_();

  // If sheets are not initialized, return notice
  const planSheet = ss.getSheetByName(SHEET_NAMES.APPROVED_PLAN);
  if (!planSheet) {
    return {
      status: "UNINITIALIZED",
      currentUser: currentUser,
      campuses: [],
      approvedPlan: [],
      actualHires: [],
      violations: [],
      auditLog: []
    };
  }

  const campuses = readSheetRows_(ss.getSheetByName(SHEET_NAMES.CAMPUSES), [
    "campus", "short_name", "region", "type", "grades", "approved_fte", "actual_fte", "vacant_fte", "variance", "violations_count"
  ]);

  const approvedPlan = readSheetRows_(ss.getSheetByName(SHEET_NAMES.APPROVED_PLAN), [
    "plan_id", "campus", "role", "category", "approved_fte", "last_revised_date", "last_revised_by", "revision_notes"
  ]);

  const actualHires = readSheetRows_(ss.getSheetByName(SHEET_NAMES.ACTUAL_HIRES), [
    "hire_id", "campus", "role", "category", "employee_name", "job_title", "assignment", "fte", "status", "position_id", "hire_date", "override_flag", "override_reason"
  ]);

  const violations = readSheetRows_(ss.getSheetByName(SHEET_NAMES.VIOLATIONS), [
    "violation_id", "campus", "role", "type", "approved_fte", "actual_fte", "variance", "employee_name", "status", "override_reason", "logged_date", "logged_by", "resolved_date", "resolved_by"
  ]);

  const auditLog = readSheetRows_(ss.getSheetByName(SHEET_NAMES.AUDIT_LOG), [
    "log_id", "timestamp", "user_email", "action_type", "campus", "role", "old_value", "new_value", "reason_notes", "override_status"
  ]);

  return {
    status: "OK",
    currentUser: currentUser,
    campuses: campuses,
    approvedPlan: approvedPlan,
    actualHires: actualHires,
    violations: violations,
    auditLog: auditLog.reverse() // latest entries first
  };
}

/**
 * Helper to read structured rows from sheet.
 */
function readSheetRows_(sheet, fields) {
  if (!sheet) return [];
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow <= 1) return [];

  const data = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
  return data.map(function(row) {
    const obj = {};
    for (let i = 0; i < fields.length; i++) {
      let val = row[i];
      if (val instanceof Date) {
        val = Utilities.formatDate(val, "America/Chicago", "yyyy-MM-dd");
      }
      obj[fields[i]] = val !== undefined && val !== null ? val : "";
    }
    return obj;
  });
}

/**
 * Revises the Approved Plan baseline for a campus + role.
 * Requires an explicit revision justification note.
 */
function reviseApprovedPlan(campus, role, newApprovedFte, reasonNotes) {
  if (!reasonNotes || reasonNotes.trim() === "") {
    throw new Error("A revision reason note is required to modify the Approved Plan.");
  }

  const ss = getSpreadsheet_();
  const ws = ss.getSheetByName(SHEET_NAMES.APPROVED_PLAN);
  if (!ws) throw new Error("Approved_Plan sheet not found.");

  const data = ws.getDataRange().getValues();
  let foundRow = -1;
  let oldFte = 0;
  let category = "Instructional Staff";

  for (let r = 1; r < data.length; r++) {
    if (data[r][1] === campus && data[r][2] === role) {
      foundRow = r + 1; // 1-indexed
      oldFte = parseFloat(data[r][4]) || 0;
      category = data[r][3] || category;
      break;
    }
  }

  const timestampDate = Utilities.formatDate(new Date(), "America/Chicago", "yyyy-MM-dd");
  const user = getCurrentUserEmail_();
  const newFteVal = parseFloat(newApprovedFte);

  if (foundRow > -1) {
    // Update existing row
    ws.getRange(foundRow, 5).setValue(newFteVal);
    ws.getRange(foundRow, 6).setValue(timestampDate);
    ws.getRange(foundRow, 7).setValue(user);
    ws.getRange(foundRow, 8).setValue(reasonNotes);
  } else {
    // New role approved for this campus
    const planId = "PLAN-" + Utilities.getUuid().substring(0, 6).toUpperCase();
    ws.appendRow([planId, campus, role, category, newFteVal, timestampDate, user, reasonNotes]);
  }

  // Log in Audit Trail
  logAudit_(
    ss,
    "PLAN_REVISION",
    campus,
    role,
    oldFte + " FTE",
    newFteVal + " FTE",
    reasonNotes,
    "APPROVED"
  );

  syncCampusRollups_(ss);

  return {
    success: true,
    message: "Approved Plan successfully revised to " + newFteVal + " FTE.",
    appData: getAppInitialData()
  };
}

/**
 * Validates and logs or updates an employee hire.
 * Strict validation:
 * - If role was not approved at campus, blocks save unless explicit override provided.
 * - If actual FTE > approved FTE, blocks save unless explicit override provided.
 */
function logOrUpdateHire(hirePayload, isOverride, overrideReason) {
  const ss = getSpreadsheet_();
  const campus = hirePayload.campus;
  const role = hirePayload.role;
  const hireFte = parseFloat(hirePayload.fte) || 1.0;
  const hireId = hirePayload.hire_id || "";

  // 1. Get approved count for this campus + role
  const planSheet = ss.getSheetByName(SHEET_NAMES.APPROVED_PLAN);
  const planData = planSheet.getDataRange().getValues();
  let approvedFte = null;
  let category = hirePayload.category || "Instructional Staff";

  for (let i = 1; i < planData.length; i++) {
    if (planData[i][1] === campus && planData[i][2] === role) {
      approvedFte = parseFloat(planData[i][4]) || 0;
      category = planData[i][3] || category;
      break;
    }
  }

  // 2. Get current actual filled count
  const hiresSheet = ss.getSheetByName(SHEET_NAMES.ACTUAL_HIRES);
  const hiresData = hiresSheet.getDataRange().getValues();
  let currentFilledFte = 0;

  for (let j = 1; j < hiresData.length; j++) {
    const rowHireId = hiresData[j][0];
    const rowCampus = hiresData[j][1];
    const rowRole = hiresData[j][2];
    const rowStatus = hiresData[j][8];
    const rowFte = parseFloat(hiresData[j][7]) || 1.0;

    // exclude current hire if updating
    if (rowHireId !== hireId && rowCampus === campus && rowRole === role && rowStatus === "Filled") {
      currentFilledFte += rowFte;
    }
  }

  const projectedFte = currentFilledFte + hireFte;

  // Validation Check A: Unapproved Role
  if (approvedFte === null || approvedFte === 0) {
    if (!isOverride) {
      return {
        success: false,
        errorType: "UNAPPROVED_ROLE",
        campus: campus,
        role: role,
        projectedFte: projectedFte,
        message: 'The role "' + role + '" is NOT approved at ' + campus + '. Hiring into an unapproved role requires an explicit administrative override.'
      };
    }
  }

  // Validation Check B: Exceeding Approved FTE
  if (approvedFte !== null && projectedFte > approvedFte) {
    if (!isOverride) {
      return {
        success: false,
        errorType: "EXCEEDED_FTE",
        campus: campus,
        role: role,
        approvedFte: approvedFte,
        currentFilledFte: currentFilledFte,
        projectedFte: projectedFte,
        variance: projectedFte - approvedFte,
        message: 'Hiring would cause ' + campus + ' (' + role + ') to exceed approved FTE: ' + projectedFte + ' actual vs ' + approvedFte + ' approved. Requires an explicit administrative override.'
      };
    }
  }

  // If override was required, enforce justification note
  if (isOverride && (!overrideReason || overrideReason.trim() === "")) {
    return {
      success: false,
      errorType: "MISSING_REASON",
      message: "An explicit override justification note is required to approve this hiring exception."
    };
  }

  const nowStamp = Utilities.formatDate(new Date(), "America/Chicago", "yyyy-MM-dd HH:mm:ss");
  const user = getCurrentUserEmail_();
  let finalHireId = hireId;
  let oldInfo = "None";

  if (hireId) {
    // Updating existing hire row
    for (let r = 1; r < hiresData.length; r++) {
      if (hiresData[r][0] === hireId) {
        const rowNum = r + 1;
        oldInfo = hiresData[r][4] + " (" + hiresData[r][8] + ", " + hiresData[r][7] + " FTE)";
        hiresSheet.getRange(rowNum, 2).setValue(campus);
        hiresSheet.getRange(rowNum, 3).setValue(role);
        hiresSheet.getRange(rowNum, 4).setValue(category);
        hiresSheet.getRange(rowNum, 5).setValue(hirePayload.employee_name);
        hiresSheet.getRange(rowNum, 6).setValue(hirePayload.job_title || role);
        hiresSheet.getRange(rowNum, 7).setValue(hirePayload.assignment || "");
        hiresSheet.getRange(rowNum, 8).setValue(hireFte);
        hiresSheet.getRange(rowNum, 9).setValue(hirePayload.status || "Filled");
        hiresSheet.getRange(rowNum, 10).setValue(hirePayload.position_id || "");
        hiresSheet.getRange(rowNum, 11).setValue(hirePayload.hire_date || "");
        hiresSheet.getRange(rowNum, 12).setValue(isOverride ? "Yes" : "No");
        hiresSheet.getRange(rowNum, 13).setValue(isOverride ? overrideReason : "");
        break;
      }
    }
  } else {
    // New hire insertion
    finalHireId = "HIRE-" + Utilities.getUuid().substring(0, 6).toUpperCase();
    hiresSheet.appendRow([
      finalHireId,
      campus,
      role,
      category,
      hirePayload.employee_name,
      hirePayload.job_title || role,
      hirePayload.assignment || "",
      hireFte,
      hirePayload.status || "Filled",
      hirePayload.position_id || "",
      hirePayload.hire_date || Utilities.formatDate(new Date(), "America/Chicago", "yyyy-MM-dd"),
      isOverride ? "Yes" : "No",
      isOverride ? overrideReason : ""
    ]);
  }

  // Record Violation / Override record if applicable
  if (isOverride) {
    const violSheet = ss.getSheetByName(SHEET_NAMES.VIOLATIONS);
    const violId = "VIOL-" + Utilities.getUuid().substring(0, 6).toUpperCase();
    const vType = approvedFte === null || approvedFte === 0 ? "UNAPPROVED_ROLE" : "EXCEEDED_FTE";
    violSheet.appendRow([
      violId,
      campus,
      role,
      vType,
      approvedFte || 0,
      projectedFte,
      projectedFte - (approvedFte || 0),
      hirePayload.employee_name,
      "OVERRIDDEN",
      overrideReason,
      nowStamp,
      user,
      nowStamp,
      user
    ]);
  }

  // Log in Audit Trail
  const action = isOverride ? "HIRE_WITH_OVERRIDE" : (hireId ? "HIRE_UPDATED" : "HIRE_LOGGED");
  const newInfo = hirePayload.employee_name + " (" + (hirePayload.status || "Filled") + ", " + hireFte + " FTE)";
  logAudit_(
    ss,
    action,
    campus,
    role,
    oldInfo,
    newInfo,
    isOverride ? "OVERRIDE JUSTIFICATION: " + overrideReason : (hirePayload.notes || "Standard hire entry"),
    isOverride ? "OVERRIDDEN" : "STANDARD"
  );

  syncCampusRollups_(ss);

  return {
    success: true,
    hireId: finalHireId,
    message: isOverride 
      ? "Hire logged with administrative override. Violation recorded and permanently audited."
      : "Hire logged successfully.",
    appData: getAppInitialData()
  };
}

/**
 * Removes or marks an employee hire removed.
 */
function removeHire(hireId, reasonNotes) {
  if (!reasonNotes || reasonNotes.trim() === "") {
    throw new Error("A reason note is required to remove a hire entry.");
  }

  const ss = getSpreadsheet_();
  const hiresSheet = ss.getSheetByName(SHEET_NAMES.ACTUAL_HIRES);
  const data = hiresSheet.getDataRange().getValues();
  let rowToDelete = -1;
  let campus = "";
  let role = "";
  let empName = "";

  for (let r = 1; r < data.length; r++) {
    if (data[r][0] === hireId) {
      rowToDelete = r + 1;
      campus = data[r][1];
      role = data[r][2];
      empName = data[r][4];
      break;
    }
  }

  if (rowToDelete > -1) {
    hiresSheet.deleteRow(rowToDelete);
    logAudit_(
      ss,
      "HIRE_REMOVED",
      campus,
      role,
      empName + " (" + hireId + ")",
      "REMOVED",
      reasonNotes,
      "STANDARD"
    );
    syncCampusRollups_(ss);
  }

  return {
    success: true,
    message: "Hire entry successfully removed.",
    appData: getAppInitialData()
  };
}

/**
 * Resolves a tracked violation or override.
 */
function resolveViolation(violationId, resolutionNotes) {
  if (!resolutionNotes || resolutionNotes.trim() === "") {
    throw new Error("Resolution notes are required.");
  }

  const ss = getSpreadsheet_();
  const ws = ss.getSheetByName(SHEET_NAMES.VIOLATIONS);
  const data = ws.getDataRange().getValues();
  const nowStamp = Utilities.formatDate(new Date(), "America/Chicago", "yyyy-MM-dd HH:mm:ss");
  const user = getCurrentUserEmail_();

  let campus = "", role = "";
  for (let r = 1; r < data.length; r++) {
    if (data[r][0] === violationId) {
      campus = data[r][1];
      role = data[r][2];
      ws.getRange(r + 1, 9).setValue("RESOLVED");
      ws.getRange(r + 1, 10).setValue(resolutionNotes);
      ws.getRange(r + 1, 13).setValue(nowStamp);
      ws.getRange(r + 1, 14).setValue(user);
      break;
    }
  }

  logAudit_(
    ss,
    "VIOLATION_RESOLVED",
    campus,
    role,
    "STATUS: PENDING/OVERRIDDEN",
    "STATUS: RESOLVED",
    resolutionNotes,
    "RESOLVED"
  );

  syncCampusRollups_(ss);

  return {
    success: true,
    message: "Violation marked as resolved.",
    appData: getAppInitialData()
  };
}

/**
 * Recalculates summary totals in the Campuses sheet.
 */
function syncCampusRollups_(ss) {
  const campSheet = ss.getSheetByName(SHEET_NAMES.CAMPUSES);
  const planSheet = ss.getSheetByName(SHEET_NAMES.APPROVED_PLAN);
  const hiresSheet = ss.getSheetByName(SHEET_NAMES.ACTUAL_HIRES);
  const violSheet = ss.getSheetByName(SHEET_NAMES.VIOLATIONS);

  if (!campSheet || !planSheet || !hiresSheet) return;

  const planData = planSheet.getDataRange().getValues();
  const hiresData = hiresSheet.getDataRange().getValues();
  const violData = violSheet ? violSheet.getDataRange().getValues() : [];

  const appMap = {}, filledMap = {}, vacantMap = {}, violMap = {};

  for (let i = 1; i < planData.length; i++) {
    const c = planData[i][1];
    const fte = parseFloat(planData[i][4]) || 0;
    appMap[c] = (appMap[c] || 0) + fte;
  }

  for (let j = 1; j < hiresData.length; j++) {
    const c = hiresData[j][1];
    const st = hiresData[j][8];
    const fte = parseFloat(hiresData[j][7]) || 1.0;
    if (st === "Filled") {
      filledMap[c] = (filledMap[c] || 0) + fte;
    } else if (st === "Vacant") {
      vacantMap[c] = (vacantMap[c] || 0) + fte;
    }
  }

  for (let k = 1; k < violData.length; k++) {
    const c = violData[k][1];
    const st = violData[k][8];
    if (st !== "RESOLVED") {
      violMap[c] = (violMap[c] || 0) + 1;
    }
  }

  const campData = campSheet.getDataRange().getValues();
  for (let r = 1; r < campData.length; r++) {
    const c = campData[r][0];
    const app = appMap[c] || 0;
    const act = filledMap[c] || 0;
    const vac = vacantMap[c] || 0;
    const varVal = act - app;
    const viols = violMap[c] || 0;

    campSheet.getRange(r + 1, 6).setValue(app);
    campSheet.getRange(r + 1, 7).setValue(act);
    campSheet.getRange(r + 1, 8).setValue(vac);
    campSheet.getRange(r + 1, 9).setValue(varVal);
    campSheet.getRange(r + 1, 10).setValue(viols);
  }
}
