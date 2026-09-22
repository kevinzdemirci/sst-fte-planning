/**
 * SST Schools - Campus FTE Planning & Staffing Control Portal
 * Migration & Setup Utilities
 * 
 * Run `setupDatabaseStructure()` to initialize all 5 sheets with protective
 * permissions, formatted headers, and audit trail safeguards.
 */

function setupDatabaseStructure() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  const sheetConfigs = [
    {
      name: "Campuses",
      headers: ["Campus Name", "Short Code", "Region", "System Type", "Grades", "Approved FTE", "Actual Filled FTE", "Vacancies", "Variance", "Violations Count"],
      headerColor: "#0B2545"
    },
    {
      name: "Approved_Plan",
      headers: ["Plan ID", "Campus", "Role Title", "Category", "Approved FTE", "Last Revised Date", "Last Revised By", "Revision Notes"],
      headerColor: "#0B2545"
    },
    {
      name: "Actual_Hires",
      headers: ["Hire ID", "Campus", "Role Title", "Category", "Employee Name", "HR Job Title", "Assignment", "FTE", "Status", "Position ID", "Hire Date", "Override Flag", "Override Reason"],
      headerColor: "#0B2545"
    },
    {
      name: "Violations_Overrides",
      headers: ["Violation ID", "Campus", "Role Title", "Violation Type", "Approved FTE", "Actual FTE", "Variance", "Employee Name", "Status", "Override Reason", "Logged Date", "Logged By", "Resolved Date", "Resolved By"],
      headerColor: "#8B0000"
    },
    {
      name: "Audit_Log",
      headers: ["Log ID", "Timestamp (UTC-5)", "User Email", "Action Type", "Campus", "Role Title", "Old Value", "New Value", "Reason / Notes", "Override Status"],
      headerColor: "#0B2545",
      protect: true
    }
  ];

  sheetConfigs.forEach(function(config) {
    let sheet = ss.getSheetByName(config.name);
    if (!sheet) {
      sheet = ss.insertSheet(config.name);
    }
    
    // Setup headers if empty
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(config.headers);
      const headerRange = sheet.getRange(1, 1, 1, config.headers.length);
      headerRange.setBackground(config.headerColor);
      headerRange.setFontColor("#FFFFFF");
      headerRange.setFontWeight("bold");
      headerRange.setHorizontalAlignment("center");
      sheet.setFrozenRows(1);
    }

    // Protect Audit Log sheet so casual users or editors cannot alter logged history
    if (config.protect) {
      try {
        const protection = sheet.protect().setDescription("Unfalsifiable Audit Log - Tamper Proof");
        const me = Session.getEffectiveUser();
        protection.addEditor(me);
        protection.removeEditors(protection.getEditors().filter(function(ed) {
          return ed.getEmail() !== me.getEmail();
        }));
        if (protection.canDomainEdit()) {
          protection.setDomainEdit(false);
        }
      } catch (e) {
        Logger.log("Protection note: " + e.message);
      }
    }
  });

  Logger.log("SST Schools FTE Database structure verified and secured.");
}

/**
 * Programmatically grants Editor access to Ali Dal and Hasan Kendirci
 * on the Google Spreadsheet, and ensures sheet protections are properly assigned.
 * Run this function once from the Apps Script editor to share with Regional Talent Acquisition.
 */
function grantTalentAcquisitionPermissions() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const regionalEditors = [
    "adal@ssttx.org",        // Ali Dal - Regional Talent Acquisition
    "hkendirci@ssttx.org"    // Hasan Kendirci - Regional Talent Acquisition
  ];
  
  regionalEditors.forEach(function(email) {
    try {
      ss.addEditor(email);
      Logger.log("Granted spreadsheet editor access to: " + email);
    } catch (e) {
      Logger.log("Notice adding editor " + email + ": " + e.message);
    }
  });

  // Ensure Audit_Log sheet is locked down to preserve tamper-proof integrity
  setupDatabaseStructure();
  
  Logger.log("Regional Talent Acquisition permissions successfully configured for Ali Dal and Hasan Kendirci.");
}
