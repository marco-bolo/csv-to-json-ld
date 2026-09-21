// Base URL for listing JSON Schema files (CSVW) in the repo's `remote/` folder via GitHub Contents API.
// Used by fetchSchemaFileList() to discover which sheets to build.
const GITHUB_API_URL = "https://api.github.com/repos/marco-bolo/csv-to-json-ld/contents/remote";

// Base URL for fetching raw JSON Schema files from the `main/remote/` branch path.
// Each schema file (e.g., Person.schema.json) is pulled from here.
const GITHUB_RAW_BASE = "https://raw.githubusercontent.com/marco-bolo/csv-to-json-ld/main/remote/";

// Direct raw URL to a YAML file containing slot (field) descriptions.
// These descriptions are parsed and later attached to header cells as Google Sheets "notes".
const SLOT_YAML_URL = "https://raw.githubusercontent.com/marco-bolo/csv-to-json-ld/main/remote/models/slots.yaml";

// Some CSVW schemas can reference a "synthetic" sheet that is realized by multiple concrete sheets in the UI.
// This map lets a single target sheet name (key) resolve to multiple actual sheet names for dropdown sources.
const syntheticSheetMap = {
  "person-or-organization": ["Person", "Organization"]
};

// Helpers for efficiently making updates

// Clear formatting/validation while preserving data
function clearSheetFormattingAndValidation(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();

  if (lastRow < 1 || lastCol < 1) return;

  // Get all data first to preserve it
  const dataRange = sheet.getRange(1, 1, lastRow, lastCol);
  const values = dataRange.getValues();

  // Clear formatting, validation, and notes
  dataRange.clearFormat();
  dataRange.clearDataValidations();
  dataRange.clearNote();

  // Clear conditional formatting rules
  sheet.clearConditionalFormatRules();

  // Remove any existing protections (we'll re-add them)
  const protections = sheet.getProtections(SpreadsheetApp.ProtectionType.RANGE);
  protections.forEach(protection => {
    if (protection.canEdit()) {
      protection.remove();
    }
  });

  // MORE AGGRESSIVE: Clear each column individually
  for (let col = 1; col <= lastCol; col++) {
    const colRange = sheet.getRange(1, col, sheet.getMaxRows(), 1);
    colRange.clearDataValidations();
  }

  // Restore the data
  dataRange.setValues(values);

  Logger.log(`Cleared formatting/validation for sheet: ${sheet.getName()}`);
}

function sortSheetsAlphabetically(ss) { //Visible sheets only
  const sheets = ss.getSheets();

  // Separate hidden and visible sheets
  const visible = sheets.filter(s => !s.isSheetHidden());
  const hidden = sheets.filter(s => s.isSheetHidden());

  // Sort visible sheets alphabetically
  visible.sort((a, b) => a.getName().toLowerCase().localeCompare(b.getName().toLowerCase()));

  // Reorder: visible first (sorted), then hidden
  const sorted = [...visible, ...hidden];

  sorted.forEach((sheet, index) => {
    ss.setActiveSheet(sheet);
    ss.moveActiveSheet(index + 1);
  });

  Logger.log(`Sorted ${visible.length} visible sheets alphabetically (${hidden.length} hidden sheets at end)`);
}

function generateSheetsFromCSVW() {
  // Discover schema files and fetch current checksums
  const schemaFiles = fetchSchemaFileList().sort();
  const currentChecksums = fetchSchemaChecksums();

  // Log checksum status
  Logger.log(`Found ${Object.keys(currentChecksums).length} checksums from GitHub`);

  // Open the Google Spreadsheet by ID (replace with your own if needed).
  const ss = SpreadsheetApp.openById("1PBFK3LW3DAdvXdbk2v8bSdtTf87mBhabeeegwRjOBRg");

  // Maps "SheetName.slot" -> { targetSheet, targetColumn } for later building of data-validation dropdowns.
  const foreignKeyMap = {};

  // Tracks which foreign keys come from array-typed columns (separator set), so we can skip dropdowns for those.
  const arrayTypedFKs = {};

  // For each sheet, stores a mapping of "slot name" -> "column title shown in header".
  // Needed because CSVW columns can have localized titles that differ from the raw `name`.
  const columnTitlesBySheet = {};

  // Parse the YAML of slot descriptions once and reuse:
  // These are the human-readable tooltips we attach as header cell "notes".
  const slotDescriptions = fetchSlotDescriptions();

  // Track processing stats
  let processedCount = 0;
  let skippedCount = 0;

  // Main loop with checksum-based filtering
  schemaFiles.forEach((filename, index) => {
    const sheetName = filename.replace(".schema.json", "");

    // TESTING: Skip all sheets except these
    //if (!["Action", "Dataset", "Person", "Organization"].includes(sheetName)) return;

    // Fetch and parse the CSVW-style JSON Schema - MOVED BEFORE CHECKSUM CHECK
    const schema = JSON.parse(fetchWithRetry(GITHUB_RAW_BASE + filename));

    // Build column title mapping for ALL sheets (needed for foreign key dropdowns)
    const columns = schema.columns.filter((col) => !col.virtual);
    const nameToTitle = {};
    columns.forEach((col) => {
      const title = Array.isArray(col.titles?.en) ? col.titles.en[0] : col.name;
      nameToTitle[col.name] = title;
    });
    columnTitlesBySheet[sheetName] = nameToTitle;

    // Check if this sheet needs updating based on checksum
    if (!shouldUpdateSheet(sheetName, currentChecksums)) {
      skippedCount++;
      return; // Skip this sheet
    }

    processedCount++;
    Logger.log(`Processing sheet: ${sheetName} (${processedCount}/${schemaFiles.length - skippedCount})`);

    Logger.log(`${filename} has ${schema.foreignKeys?.length || 0} foreign keys`);

    // Create or reuse the sheet matching this schema.
    let currentSheet = ss.getSheetByName(sheetName);
    if (!currentSheet) {
      currentSheet = ss.insertSheet(sheetName);
      Logger.log(`Created new sheet: ${sheetName}`);
    } else {
      Logger.log(`Found existing sheet: ${sheetName}`);

      // *** NEW: Clear all formatting and validation before rebuilding ***
      clearSheetFormattingAndValidation(currentSheet);
    }

    // Keep the header row visible while scrolling.
    currentSheet.setFrozenRows(1); // freeze header row

    // Build headers array from the already-created nameToTitle mapping
    const headers = columns.map((col) => nameToTitle[col.name]);

    Logger.log(`Sheet: ${sheetName}`);
    Logger.log(`Slot-to-title mapping: ${JSON.stringify(nameToTitle, null, 2)}`);

    // Write header row once (row 1) with computed titles.
    const headerRange = currentSheet.getRange(1, 1, 1, headers.length);
    headerRange.setValues([headers]);

    // Protect the header row with a whitelist of allowed editors
    const protection = currentSheet.getRange(1, 1, 1, currentSheet.getMaxColumns()).protect();
    protection.setDescription(`Protect header of ${sheetName}`);
    protection.removeEditors(protection.getEditors()); // removes everyone

    // Whitelist of allowed editors
    const allowedEditors = [
      Session.getEffectiveUser().getEmail(), // script owner
      "s.formel@obis.org"
    ];

    // Add each whitelisted editor
    allowedEditors.forEach(email => {
      try {
        protection.addEditor(email);
        Logger.log(`Added editor: ${email}`);
      } catch (e) {
        Logger.log(`Failed to add editor ${email}: ${e.toString()}`);
      }
    });

    // Collect foreign key info early for validation logic
    (schema.foreignKeys || []).forEach((fk) => {
      const fromCol = fk.columnReference;
      const to = fk.reference;
      const toSheet = to.resource.replace(".csv", "").replace("../data/", "").replace("../", "").replace("out/validation/", "");

      foreignKeyMap[`${sheetName}.${fromCol}`] = {
        targetSheet: toSheet,
        targetColumn: to.columnReference
      };

      const matchingCol = schema.columns.find(col => col.name === fromCol);
      if (matchingCol && typeof matchingCol.separator === "string") {
        Logger.log(`Marking '${sheetName}.${fromCol}' as array-typed foreign key`);
        arrayTypedFKs[`${sheetName}.${fromCol}`] = true;
      }
    }); //

    // Also infer foreign keys from valueUrl patterns and LinkML range

    // Also infer foreign keys from valueUrl patterns and LinkML range
    const inferredFKs = inferForeignKeysFromValueUrl(schema, sheetName, slotDescriptions);
    Object.assign(foreignKeyMap, inferredFKs);

    // Debug: log what FKs were found for HowTo specifically
    if (sheetName === "HowTo") {
      Logger.log(`=== HowTo Foreign Keys ===`);
      Logger.log(`Explicit FKs from schema: ${JSON.stringify(schema.foreignKeys, null, 2)}`);
      Logger.log(`Inferred FKs: ${JSON.stringify(inferredFKs, null, 2)}`);

      // Log all columns to see what's there
      columns.forEach(col => {
        const slotInfo = slotDescriptions[col.name];
        Logger.log(`Column: ${col.name}, range from slot: ${slotInfo ? slotInfo.range : 'N/A'}`);
      });
    }

    // For each schema column, configure appearance, notes, and validation for the corresponding sheet column.
    columns.forEach((col, i) => {

      Logger.log(`sheet='${sheetName}', col.name='${col.name}', titles.en=${JSON.stringify(col.titles?.en)}`);

      const title = nameToTitle[col.name];

      // Find the 1-based column index by searching the header row for our title.
      const colIndex = currentSheet.getRange("1:1").getValues()[0].indexOf(title) + 1;
      if (colIndex < 1) {
        Logger.log(`Column title '${title}' not found in '${sheetName}' — skipping`);
        return;
      }

      // Convenience ranges for the header cell and the entire body of that column.
      const headerCell = currentSheet.getRange(1, colIndex);
      const colRange = currentSheet.getRange(2, colIndex, currentSheet.getMaxRows() - 1);

      // Visually emphasize required columns (bold + pale yellow background).
      if (col.required) {
        headerCell.setFontWeight("bold");
        headerCell.setBackground("#fff3cd"); // pale yellow
      }

      // Apply header notes with LinkML slot information
      const mergedNote = buildHeaderNote(col, slotDescriptions);
      if (mergedNote) headerCell.setNote(mergedNote);

      // Get LinkML slot info for this column
      const slotInfo = slotDescriptions[col.name];

      // Apply validation and formatting based on LinkML slot properties
      applySlotValidation(currentSheet, colIndex, col.name, slotInfo, foreignKeyMap, sheetName);

      // Normalize any existing values that were mangled by Sheets formatting
      normalizeSheetValues(currentSheet, colIndex, slotInfo);

      // Handle legacy CSVW regex validation (if not already handled by LinkML)
      if (col.datatype?.format && (!slotInfo || !slotInfo.pattern)) {
        const regex = col.datatype.format;
        const rule = SpreadsheetApp.newDataValidation()
          .requireFormulaSatisfied(`=REGEXMATCH(INDIRECT("RC", FALSE), "${regex}")`)
          .setAllowInvalid(true) // allow but flag invalid entries
          .build();
        colRange.setDataValidation(rule);
      }

      // Add a conditional format on the 'id' column to highlight duplicate IDs in red background.
      if (col.name === "id") {
        const colLetter = String.fromCharCode(64 + colIndex); // Convert 1->A, 2->B, ...
        const rule = SpreadsheetApp.newConditionalFormatRule()
          .whenFormulaSatisfied(`=COUNTIF(${colLetter}2:${colLetter}, INDIRECT(ADDRESS(ROW(), COLUMN()))) > 1`)
          .setBackground("#f8d7da")
          .setRanges([colRange])
          .build();
        const rules = currentSheet.getConditionalFormatRules();
        rules.push(rule);
        currentSheet.setConditionalFormatRules(rules);
      }
    });

    // After successful processing, store the current checksum
    const currentChecksum = currentChecksums[sheetName];
    if (currentChecksum) {
      storeLastProcessedChecksum(sheetName, currentChecksum);
    }

    // Gentle delay to avoid hammering Sheets/HTTP services when looping many schemas.
    Utilities.sleep(500);
  });

  // Summary logging
  Logger.log(`Schema processing complete: ${processedCount} updated, ${skippedCount} skipped`);

  // Clear force rebuild flag if it was set
  PropertiesService.getScriptProperties().deleteProperty("FORCE_REBUILD");

  // Debug logging of accumulated foreign key mappings.
  Logger.log(`Done building sheets. Total foreign keys collected: ${Object.keys(foreignKeyMap).length}`);
  Logger.log(`foreignKeyMap: ${JSON.stringify(foreignKeyMap, null, 2)}`);

  Logger.log("Starting dropdown application phase");

  // Second pass: apply data validation dropdowns for all non-array foreign-key columns.
  Object.entries(foreignKeyMap).forEach(([sourceKey, target]) => {
    const [sourceSheetName, sourceSlotName] = sourceKey.split(".");

    // Skip array-typed FK columns (see above rationale).
    if (arrayTypedFKs[sourceKey]) {
      Logger.log(`Skipping dropdown for array-typed FK: ${sourceKey}`);
      return;
    }

    const sourceSheet = ss.getSheetByName(sourceSheetName);
    if (!sourceSheet) {
      Logger.log(`Source sheet '${sourceSheetName}' not found.`);
      return;
    }

    // Translate source slot name -> displayed column title -> column index in header row.
    const sourceColName = columnTitlesBySheet[sourceSheetName]?.[sourceSlotName];
    if (!sourceColName) {
      Logger.log(`Source column '${sourceSlotName}' not mapped in '${sourceSheetName}'`);
      return;
    }

    const sourceColIndex = sourceSheet.getRange("1:1").getValues()[0].indexOf(sourceColName) + 1;
    if (sourceColIndex < 1) {
      Logger.log(`Source column '${sourceColName}' not found in header of '${sourceSheetName}'`);
      return;
    }

    // Range covering all rows under the header for this source column (data rows).
    const lastRow = Math.max(2, sourceSheet.getLastRow());
    const numRows = lastRow - 1;
    const sourceRange = sourceSheet.getRange(2, sourceColIndex, sourceSheet.getMaxRows() - 1);

    // Remove any previous validation to avoid conflicts before applying the new rule.
    sourceRange.clearDataValidations();

    // Resolve possible "synthetic" target sheets
    let targetSheetToUse = target.targetSheet;
    let mappedSheets = [target.targetSheet];

    if (syntheticSheetMap[target.targetSheet]) {
      // Create/update combined sheet for synthetic targets
      const combinedSheetName = createCombinedIdSheet(ss, target.targetSheet, syntheticSheetMap[target.targetSheet]);
      targetSheetToUse = combinedSheetName;
      mappedSheets = [combinedSheetName];

      // Manually add column mapping for the combined sheet
      if (!columnTitlesBySheet[combinedSheetName]) {
        columnTitlesBySheet[combinedSheetName] = {
          "id": "MBO Permanent Identifier*"
        };
      }

      Logger.log(`Using combined sheet ${combinedSheetName} for synthetic target ${target.targetSheet}`);
    }

    let rule = null;

    // Try to build a dropdown referencing the first valid target sheet/column encountered.
    for (const sheetName of mappedSheets) {
      const targetSheet = ss.getSheetByName(sheetName);
      if (!targetSheet) {
        Logger.log(`Target sheet '${sheetName}' not found.`);
        continue;
      }

      // Translate target slot name -> displayed column title -> target column index.
      const targetColName = columnTitlesBySheet[sheetName]?.[target.targetColumn];
      if (!targetColName) {
        Logger.log(`Target column '${target.targetColumn}' not mapped in '${sheetName}'`);
        continue;
      }

      const headerRow = targetSheet.getRange("1:1").getValues()[0];
      const targetColIndex = headerRow.indexOf(targetColName) + 1;
      if (targetColIndex < 1) {
        Logger.log(`Target column title '${targetColName}' not found in header of '${sheetName}'`);
        Logger.log(`Header row was: ${JSON.stringify(headerRow)}`);
        continue;
      }

      // Build an open-ended A2:A-style range reference for the target column values (skip header).
      const colLetter = String.fromCharCode(64 + targetColIndex);  // A, B, ...
      const rangeRef = `${colLetter}2:${colLetter}`;  // e.g. A2:A

      Logger.log(`Creating live dropdown link from '${sourceSheetName}.${sourceColName}' to '${sheetName}!${rangeRef}'`);

      // Create a data-validation rule that constrains entries to values present in the target range.
      // The second arg (true) means the user sees invalid entry warnings but cannot enter values outside the list.
      rule = SpreadsheetApp.newDataValidation()
        .requireValueInRange(targetSheet.getRange(rangeRef), true)
        .setAllowInvalid(false)
        .build();

      // Stop after the first successfully resolved target sheet/column.
      break;
    }

    // Apply the constructed validation rule to the source column's data range.
    if (rule) {
      sourceRange.setDataValidation(rule);
      Logger.log(`Dropdown applied to ${sourceSheetName}!${sourceColName}`);
    } else {
      Logger.log(`No valid dropdown range found for '${sourceSheetName}.${sourceColName}'`);
    }
  });

  // Sort all sheets alphabetically
  sortSheetsAlphabetically(ss);
}

// Build column title mappings for a sheet by reading its schema
function buildColumnTitleMapping(schema) {
  const columns = schema.columns.filter((col) => !col.virtual);
  const nameToTitle = {};
  columns.forEach((col) => {
    const title = Array.isArray(col.titles?.en) ? col.titles.en[0] : col.name;
    nameToTitle[col.name] = title;
  });
  return nameToTitle;
}

// Infer foreign key relationships from valueUrl patterns or LinkML range
// Returns an object with same structure as foreignKeyMap

function inferForeignKeysFromValueUrl(schema, sheetName, slotDescriptions) {
  const inferredFKs = {};

  // Define primitive types that should NOT get dropdowns
  const primitiveTypes = ['string', 'integer', 'boolean', 'float', 'double',
                          'date', 'datetime', 'uri', 'uriorcurie', 'schemaURL'];

  schema.columns.forEach((col) => {
    // Skip if has a separator (array type)
    if (col.separator) return;

    let targetSheet = null;
    let targetColumn = "id";

    // First, check LinkML range property
    const slotInfo = slotDescriptions[col.name];
    if (slotInfo && slotInfo.range) {
      const range = slotInfo.range;

      // Skip primitive types - they should not have dropdowns
      if (primitiveTypes.includes(range)) {
        Logger.log(`Skipping primitive type range '${range}' for ${sheetName}.${col.name}`);
        return;
      }

      // Map LinkML range to target sheets
      const rangeToSheetMap = {
        "PersonOrOrganization": "person-or-organization",
        "Person": "Person",
        "Organization": "Organization",
        "Place": "Place",
        "Dataset": "Dataset",
        "PublishingStatusDefinedTerm": "PublishingStatusDefinedTerm",
        "License": "License",
        "EmbargoStatement": "EmbargoStatement",
        "Action": "Action",
        "Audience": "Audience",
        "PropertyValue": "PropertyValue",
        "Taxon": "Taxon",
        "DataDownload": "DataDownload",
        "HowTo": "HowTo",
        "HowToStep": "HowToStep",
        "HowToTip": "HowToTip",
        "Document": "Document",
        "Instrument": "Instrument",
        "Platform": "Platform"
      };

      if (rangeToSheetMap[range]) {
        targetSheet = rangeToSheetMap[range];
        Logger.log(`Inferred FK from range: ${sheetName}.${col.name} (range=${range}) -> ${targetSheet}.${targetColumn}`);
      }
    }

    // If no range match, try valueUrl pattern matching (fallback)
    if (!targetSheet && col.valueUrl) {
      const match = col.valueUrl.match(/\{\+(\w+)\}/);
      if (match && match[1] === col.name) {
        if (col.name.endsWith("MboId")) {
          const baseName = col.name.replace(/MboId$/, "");
          const sheetMap = {
            "publishingStatus": "PublishingStatusDefinedTerm",
            "license": "License",
            "embargoStatement": "EmbargoStatement",
            "spatialCoveragePlace": "Place"
          };
          targetSheet = sheetMap[baseName];
        }

        if (targetSheet) {
          Logger.log(`Inferred FK from valueUrl: ${sheetName}.${col.name} -> ${targetSheet}.${targetColumn}`);
        }
      }
    }

    if (targetSheet) {
      inferredFKs[`${sheetName}.${col.name}`] = {
        targetSheet: targetSheet,
        targetColumn: targetColumn
      };
    }
  });

  return inferredFKs;
}

// Create or update a hidden sheet with formulas that dynamically combine IDs
function createCombinedIdSheet(ss, syntheticName, sourceSheetNames) {
  const combinedSheetName = `_combined_${syntheticName}`;

  // Get or create the combined sheet
  let combinedSheet = ss.getSheetByName(combinedSheetName);
  if (!combinedSheet) {
    combinedSheet = ss.insertSheet(combinedSheetName);
    combinedSheet.hideSheet();
    Logger.log(`Created hidden combined sheet: ${combinedSheetName}`);
  } else {
    combinedSheet.clear();
  }

  // Write header
  combinedSheet.getRange(1, 1).setValue("MBO Permanent Identifier*");

  // Build a formula that combines and filters the ID columns from all source sheets
  if (sourceSheetNames.length === 2) {
    const [sheet1, sheet2] = sourceSheetNames;
    const formula = `=SORT(UNIQUE(FILTER(VSTACK(${sheet1}!A2:A, ${sheet2}!A2:A), VSTACK(${sheet1}!A2:A, ${sheet2}!A2:A)<>"")))`;
    combinedSheet.getRange(2, 1).setFormula(formula);
    Logger.log(`Set dynamic formula in ${combinedSheetName}: ${formula}`);
  } else if (sourceSheetNames.length > 2) {
    const vstackRanges = sourceSheetNames.map(name => `${name}!A2:A`).join(", ");
    const formula = `=SORT(UNIQUE(FILTER(VSTACK(${vstackRanges}), VSTACK(${vstackRanges})<>"")))`;
    combinedSheet.getRange(2, 1).setFormula(formula);
    Logger.log(`Set dynamic formula in ${combinedSheetName}: ${formula}`);
  }

  return combinedSheetName;
}

// --- Helpers for building header notes from CSVW + slots.yaml (+ optional hints) ---

// Pull dc:description (or description) from a CSVW column safely.
// Supports string, language map, array of strings/maps (robust to varied CSVW encodings).
function extractCsvwDescription(col) {
  // Guard: if the caller passed nothing, be graceful.
  if (!col || typeof col !== "object") return null;

  // Some CSVW encoders put description as an array; normalize to first item if so.
  let v = col["dc:description"] ?? col["description"];
  if (!v) return null;

  if (Array.isArray(v)) {
    // e.g., ["Some text"] or [{en: "Some text"}]
    if (v.length === 0) return null;
    v = v[0];
  }

  if (typeof v === "string") return v.trim();

  if (typeof v === "object") {
    // Language map: prefer 'en', then first available key.
    if (Array.isArray(v.en)) return String(v.en[0]).trim();
    if (typeof v.en === "string") return v.en.trim();
    const keys = Object.keys(v);
    if (!keys.length) return null;
    const firstVal = v[keys[0]];
    return Array.isArray(firstVal) ? String(firstVal[0]).trim() : String(firstVal).trim();
  }

  return null;
}

// Merge CSVW dc:description/description with slots.yaml description.
// CSVW text first, then a blank line, then the slots.yaml fields in order:
// description, required, multivalued, range, pattern.
function buildHeaderNote(col, slotInfoByName) {
  const fromCsvw = extractCsvwDescription(col);

  const slotKey = col?.name;
  const slotInfo = slotKey && slotInfoByName[slotKey] ? slotInfoByName[slotKey] : null;

  const lines = [];

  if (fromCsvw) {
    lines.push(fromCsvw);
  }

  if (slotInfo) {
    if (fromCsvw) lines.push(""); // blank line between CSVW text and slots.yaml block
    // Header line to make it obvious where the following fields come from.
    lines.push("from slots.yaml:");

    // Only add fields that are present; keep the requested order.
    if (slotInfo.description != null && String(slotInfo.description).trim() !== "") {
      lines.push(`description: ${String(slotInfo.description).trim()}`);
    }
    if (typeof slotInfo.required !== "undefined") {
      lines.push(`required: ${slotInfo.required}`);
    }
    if (typeof slotInfo.multivalued !== "undefined") {
      lines.push(`multivalued: ${slotInfo.multivalued}`);
    }
    if (slotInfo.range != null && String(slotInfo.range).trim() !== "") {
      lines.push(`range: ${String(slotInfo.range).trim()}`);
    }
    if (slotInfo.pattern != null && String(slotInfo.pattern).trim() !== "") {
      lines.push(`pattern: ${String(slotInfo.pattern).trim()}`);
    }
  }

  const note = lines.join("\n").trim();
  return note || null;
}

// Apply column formatting and validation based on LinkML slot properties
function applySlotValidation(sheet, colIndex, colName, slotInfo, foreignKeyMap, sheetName) {
  const colRange = sheet.getRange(2, colIndex, sheet.getMaxRows() - 1);

  // Check if this column is a foreign key
  const fkKey = `${sheetName}.${colName}`;
  const isForeignKey = foreignKeyMap.hasOwnProperty(fkKey);

  if (isForeignKey) {
    // Foreign keys get dropdown validation - handled later in the main loop
    Logger.log(`Column ${colName} is a foreign key - dropdown will be applied later`);
    return;
  }

  if (slotInfo) {
    // Format columns with string range and pattern as text to prevent number conversion
    if (slotInfo.range === 'string' && slotInfo.pattern) {
      colRange.setNumberFormat('@'); // Force text formatting

      // Apply regex validation using the LinkML pattern
      const regex = slotInfo.pattern;
      const rule = SpreadsheetApp.newDataValidation()
        .requireFormulaSatisfied(`=REGEXMATCH(INDIRECT("RC", FALSE), "${regex}")`)
        .setAllowInvalid(true)
        .build();
      colRange.setDataValidation(rule);
      Logger.log(`Applied pattern validation '${regex}' to column ${colName}`);

    } else if (slotInfo.range === 'date') {
      // Format date columns appropriately
      colRange.setNumberFormat('yyyy-mm-dd');
      Logger.log(`Applied date formatting to column ${colName}`);
    }
  }
}

// Normalize values that Google Sheets may have converted incorrectly
function normalizeSheetValues(sheet, colIndex, slotInfo) {
  if (!slotInfo || slotInfo.range !== 'string' || !slotInfo.pattern) return;

  const colRange = sheet.getRange(2, colIndex, sheet.getMaxRows() - 1);
  const values = colRange.getValues();
  let changed = false;

  for (let i = 0; i < values.length; i++) {
    let cellValue = values[i][0];

    if (cellValue === '' || cellValue == null) continue;

    let originalValue = cellValue;
    cellValue = String(cellValue).trim();

    // Fix floating point numbers that should be integers (like 2026.0 -> 2026)
    if (/^\d+\.0+$/.test(cellValue)) {
      cellValue = cellValue.replace(/\.0+$/, '');
      values[i][0] = cellValue;
      changed = true;
      Logger.log(`Normalized ${originalValue} to ${cellValue} in row ${i + 2}`);
    }
  }

  if (changed) {
    colRange.setValues(values);
  }
}

// --- Checksum optimization functions ---

// Fetch current checksums from GitHub
function fetchSchemaChecksums() {
  const checksumUrl = GITHUB_RAW_BASE + "schema-checksums.json";
  try {
    const response = fetchWithRetry(checksumUrl);
    return JSON.parse(response);
  } catch (e) {
    Logger.log(`Could not fetch checksums from GitHub: ${e}`);
    return {};
  }
}

// Get the last processed checksum for a sheet (stored in Script Properties)
function getLastProcessedChecksum(sheetName) {
  try {
    const properties = PropertiesService.getScriptProperties();
    return properties.getProperty(`last_checksum_${sheetName}`);
  } catch (e) {
    Logger.log(`Could not retrieve last checksum for ${sheetName}: ${e}`);
    return null;
  }
}

// Store the checksum after successfully processing a sheet
function storeLastProcessedChecksum(sheetName, checksum) {
  try {
    const properties = PropertiesService.getScriptProperties();
    properties.setProperty(`last_checksum_${sheetName}`, checksum);
    Logger.log(`Stored checksum for ${sheetName}: ${checksum}`);
  } catch (e) {
    Logger.log(`Could not store checksum for ${sheetName}: ${e}`);
  }
}

// Check if a sheet needs updating based on checksum comparison
function shouldUpdateSheet(sheetName, currentChecksums) {
  const currentChecksum = currentChecksums[sheetName];
  const lastProcessedChecksum = getLastProcessedChecksum(sheetName);

  // Update if:
  // 1. No current checksum (schema doesn't exist) - skip
  // 2. No last processed checksum (never processed before) - update
  // 3. Checksums are different - update
  // 4. Force rebuild flag is set - update

  if (!currentChecksum) {
    Logger.log(`No current checksum found for ${sheetName} - skipping`);
    return false;
  }

  const forceRebuild = PropertiesService.getScriptProperties().getProperty("FORCE_REBUILD") === "true";

  if (forceRebuild) {
    Logger.log(`Force rebuild enabled - updating ${sheetName}`);
    return true;
  }

  if (!lastProcessedChecksum) {
    Logger.log(`No previous checksum for ${sheetName} - updating (first time)`);
    return true;
  }

  if (currentChecksum !== lastProcessedChecksum) {
    Logger.log(`Checksum changed for ${sheetName}: ${lastProcessedChecksum} -> ${currentChecksum}`);
    return true;
  }

  Logger.log(`No changes for ${sheetName} (checksum: ${currentChecksum}) - skipping`);
  return false;
}

// Queries the GitHub Contents API for available *.schema.json files under `remote/`,
// filters out blacklisted schemas, and returns the file names.
function fetchSchemaFileList() {
  const blacklist = ["unioned-identifiers.schema.json"];

  // Optional GitHub token to increase rate limits / access private forks; read from script properties.
  const token = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  const headers = token ? { Authorization: "Bearer " + token } : {};

  // Call the Contents API endpoint.
  const response = UrlFetchApp.fetch(GITHUB_API_URL, { headers, muteHttpExceptions: true });

  // Fail fast if non-200.
  if (response.getResponseCode() !== 200) {
    throw new Error(`GitHub API error ${response.getResponseCode()}: ${response.getContentText()}`);
  }

  // Keep only *.schema.json and not blacklisted, return names as strings.
  return JSON.parse(response.getContentText())
    .filter(f => f.name.endsWith(".schema.json"))
    .filter(f => !blacklist.includes(f.name))
    .map(f => f.name);
}

// Fetches and parses the YAML file that holds slot descriptions.
// The parser is intentionally lightweight: it walks lines, tracks the current slot,
// and captures `description:` fields (including block scalars using `|`).
// Returns an object: { slotName: "description text", ... } used by headerCell.setNote(desc).
// Fetches and parses the YAML that holds slot metadata.
// Returns an object keyed by slot name:
// { slotName: { description, required, multivalued, range, pattern }, ... }
function fetchSlotDescriptions() {
  const yaml = fetchWithRetry(SLOT_YAML_URL);
  const result = {};

  const lines = yaml.split("\n");

  // Parsing state
  let currentSlot = null;
  let captureMultilineDesc = false;
  let multilineBuffer = [];
  let baseIndentForBlock = 0;

  // Helper to flush a pending block description into the slot record
  function flushBlockDesc() {
    if (currentSlot && captureMultilineDesc) {
      const desc = multilineBuffer.join("\n").replace(/\s+$/g, "").trim();
      result[currentSlot] = result[currentSlot] || {};
      result[currentSlot].description = desc;
      captureMultilineDesc = false;
      multilineBuffer = [];
      baseIndentForBlock = 0;
    }
  }

  // Simple, indentation-tolerant matchers
  const slotHeaderRe = /^(\s*)([A-Za-z0-9_]+):\s*$/;
  const keyValRe = /^\s*([A-Za-z0-9_]+):\s*(.*)$/;

  function parseBoolOrString(raw) {
    const v = raw.trim().replace(/^['"]|['"]$/g, "");
    const lower = v.toLowerCase();
    if (lower === "true") return true;
    if (lower === "false") return false;
    if (lower === "yes") return true;
    if (lower === "no") return false;
    // leave numbers/regex/other strings intact
    return v;
  }

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    const trimmed = line.trim();
    if (trimmed === "" || trimmed.startsWith("#")) {
      // Comments/blank lines: if we are capturing a block, keep them as content
      if (captureMultilineDesc && currentSlot) {
        // Preserve blank/comment lines inside block scalars by adding raw content (minus base indent)
        multilineBuffer.push(line.slice(baseIndentForBlock));
      }
      continue;
    }

    // If we hit a new slot header, finish any pending block description
    let m = line.match(slotHeaderRe);
    if (m) {
      flushBlockDesc();
      currentSlot = m[2];
      result[currentSlot] = result[currentSlot] || {};
      continue;
    }

    // If we're inside a description block, keep collecting lines as long as they stay indented
    if (captureMultilineDesc && currentSlot) {
      // A block scalar continues while indentation > baseIndentForBlock
      const currentIndent = line.match(/^\s*/)[0].length;
      if (currentIndent >= baseIndentForBlock) {
        multilineBuffer.push(line.slice(baseIndentForBlock));
        continue;
      } else {
        // indentation dropped: block ends, process this line in normal flow
        flushBlockDesc();
        // fall through to normal parsing of this line
      }
    }

    // Key/value lines
    m = line.match(keyValRe);
    if (!m || !currentSlot) {
      // Not a key/value under a slot; ignore
      continue;
    }

    const key = m[1];
    let val = m[2];

    // Handle description specially (inline scalar vs block scalar)
    if (key === "description") {
      if (val.trim() === "|" || val.trim() === ">|") {
        // Start block scalar; remember the indent for subsequent lines
        captureMultilineDesc = true;
        multilineBuffer = [];
        baseIndentForBlock = (lines[i + 1] || "").match(/^\s*/)[0].length; // next line's indent as baseline
      } else {
        // Inline description
        result[currentSlot] = result[currentSlot] || {};
        result[currentSlot].description = val.trim().replace(/^['"]|['"]$/g, "");
      }
      continue;
    }

    // Regular scalar values for other fields we care about
    if (["required", "multivalued", "range", "pattern"].includes(key)) {
      result[currentSlot] = result[currentSlot] || {};
      result[currentSlot][key] = parseBoolOrString(val);
      continue;
    }

    // Ignore other keys
  }

  // If the file ended while capturing a block, flush it.
  flushBlockDesc();

  return result;
}

// Fetch a URL with simple retry/backoff to tolerate transient network hiccups.
// Used for both YAML and JSON schema fetches.
function fetchWithRetry(url, retries = 5, delayMs = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      return UrlFetchApp.fetch(url).getContentText();
    } catch (e) {
      if (i === retries - 1) throw e;
      Utilities.sleep(delayMs + Math.floor(Math.random() * 500));
    }
  }
}


function forceRebuildDocument() {
  // Delete the stored checksum for Document
  PropertiesService.getScriptProperties().setProperty("FORCE_REBUILD", "true");

  // Now run the main function
  generateSheetsFromCSVW();
}
