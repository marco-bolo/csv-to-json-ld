# Google Apps Script - MARCO-BOLO Sheet Generator

## Current Setup (As of 2025)

This Google Apps Script is bound to the MARCO-BOLO csv-to-json-ld dashboard (spreadsheet) and is managed through a Google Cloud Platform (GCP) project for enhanced security and automation.

**Script ID**: `1bbb5P0gCpMq7FAhnMG5ec4ukF_C8F5H-EPKvfmK2bSbEUXwrOL8-PH8d`  
**GCP Project ID**: `mbo-wp1-csv-to-json-ld`  
**GCP Project Number**: `137568280356`  
**Owner**: steve@formeldataservices.com  
**Service Account**: github-sheets-reader@mbo-wp1-csv-to-json-ld.iam.gserviceaccount.com (viewer access)

## Current Access Model

**Script editing**: Managed through GCP IAM permissions, not standard Google Apps Script sharing
**Sheet access**: Many users can edit the spreadsheet for data entry
**Automation**: Service account provides read access for GitHub Actions to sync data

## If Primary Maintainer Becomes Unavailable

Currently this is Steve Formel (steve@formeldataservices.com)

### Option 1: Request GCP Project Access (Preferred)

If you have a Google account and need to maintain the existing script:

1. **Contact Google Cloud Support** to request project access transfer
   - Provide GCP Project ID: `mbo-wp1-csv-to-json-ld`
   - Reference the script and spreadsheet URLs
   - May require organizational verification

2. **Alternative**: If you can access the GCP project billing account, you may be able to add yourself as an owner through billing administration

### Option 2: Create New Script from Repository Code (Backup Plan)

If you cannot gain access to the existing GCP project:

1. **Clone this repository** to get the current script code
2. **Create a new Google Apps Script project**:
   - Go to https://script.google.com
   - Create new project
   - Copy code from this repository's `.gs` files

3. **Bind to the spreadsheet**:
   - In your new Apps Script project: Resources → Libraries → Add library
   - Or create as bound script: Extensions → Apps Script from the spreadsheet

4. **Update configuration**:
   - Modify URLs to point to main branch: `https://raw.githubusercontent.com/marco-bolo/csv-to-json-ld/main/remote/`
   - Update any hardcoded spreadsheet IDs if needed

5. **Set up new automation** (if needed):
   - Create new service account for GitHub Actions
   - Update repository secrets with new credentials

### Option 3: Alternative Hosting

The script functionality can be replicated outside Google Apps Script:

- **Node.js application** using Google Sheets API
- **GitHub Actions** that directly call Google Sheets API
- **Python script** with gspread library

## For Developers: Working with Current Setup

### Prerequisites
- Google account (Gmail or institutional email with Google account)
- Node.js and npm installed
- Access request to GCP project IAM

### Setup Process

1. **Request GCP project access**:
   - Contact current owner for IAM permissions
   - Need "Editor" role or custom Apps Script permissions

2. **Install and configure clasp**:
   ```bash
   npm install -g @google/clasp
   clasp login
   ```

3. **Clone the script**:
   ```bash
   clasp clone 1bbb5P0gCpMq7FAhnMG5ec4ukF_C8F5H-EPKvfmK2bSbEUXwrOL8-PH8d
   ```

### Development Workflow

1. **Make changes** in this repository directory
2. **Push to Google Apps Script**:
   ```bash
   clasp push
   ```
3. **Test** in the spreadsheet interface
4. **Commit changes** to GitHub repository

## Script Functionality

The script reads CSV-W schema files from the repository and:
- Creates or updates Google Sheets with appropriate column structures
- Applies data validation rules (dropdowns, regex patterns)
- Sets up conditional formatting for duplicate detection
- Protects header rows from accidental editing
- Adds user-friendly tooltips from LinkML slot descriptions

## Key Files in Repository

- `update-sheets-from-GitHub.js` - Main script; builds the sheet tabs from the CSV-W schemas
- `manual-validation-of-pipe-delimited-strings.js` - Validation helper for pipe-delimited columns
- `appsscript.json` - Apps Script project manifest
- `.clasp.json` - Configuration for clasp deployment (gitignored; holds the script ID)
- `README.md` - This documentation

## Script Properties

Set these in the Apps Script editor under **Project Settings -> Script Properties**. They are not
in this repository, so a fresh deployment needs them configured by hand.

| Property | Required | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | Recommended | Authenticates the one GitHub Contents API call used to list the schema files. |
| `FORCE_REBUILD` | No | Set to `"true"` to rebuild every tab regardless of checksums. The script deletes it when it finishes. |
| `last_checksum_<SheetName>` | Managed | Written by the script itself, one per sheet. Do not edit. Deleting one forces that sheet to rebuild. |

### About `GITHUB_TOKEN`

The repository is public, so the token grants **no access that anyone lacks** - it exists purely to
lift the GitHub API rate limit from 60 requests/hour to 5,000. That matters because Apps Script runs
from Google's shared egress addresses, where the unauthenticated quota is shared with every other
script on the same address.

Minimum permissions:

- **Classic token:** create it with **no scopes ticked at all**. That is sufficient to read a public
  repository and is the smallest thing that works.
- **Fine-grained token:** repository `marco-bolo/csv-to-json-ld`, permission **Contents: Read-only**.

Only `fetchSchemaFileList()` sends it. The schema and YAML fetches go to `raw.githubusercontent.com`
through `fetchWithRetry()`, which never passes it.

The property is optional: with it absent the script sends no `Authorization` header and still works,
just against the lower rate limit. An **expired** token is worse than none, because the header is
sent and rejected - see Troubleshooting.

Tokens expire. When you create one, note the expiry somewhere you will see it.

## Service Account Details

The `github-sheets-reader` service account is used for:
- GitHub Actions to read spreadsheet data
- Automated synchronization of sheet data to repository
- Does NOT have permission to modify the script code

## Security Considerations

This setup provides good security separation:
- Sheet editors can enter data but cannot modify automation
- Script editors need explicit GCP IAM permissions
- Service account has minimal required permissions
- All code changes are version controlled

## Troubleshooting

### Cannot Access Script
- Check if you have Google account associated with your email
- Verify GCP IAM permissions
- Try accessing directly: https://script.google.com/d/1bbb5P0gCpMq7FAhnMG5ec4ukF_C8F5H-EPKvfmK2bSbEUXwrOL8-PH8d/edit

### Clasp Issues
- Ensure you're logged in: `clasp login --status`
- Check script ID matches: `cat .clasp.json`
- Verify GCP project permissions

### Script Execution Errors
- Check Apps Script execution logs
- Verify GitHub repository files are accessible
- Ensure service account credentials are valid

### `GitHub API error 401: Bad credentials`

The `GITHUB_TOKEN` script property has expired or been revoked. The script sends the header
whenever the property is set, so a stale token fails where no token at all would have succeeded.

Fix: issue a new token (see **Script Properties** above) and replace the value, or delete the
property to fall back to unauthenticated requests. Revoke the old token while you are there.

### `GitHub API error 403: rate limit exceeded`

Running unauthenticated. Apps Script shares its egress addresses, so the 60 requests/hour applies
across unrelated scripts. Set `GITHUB_TOKEN`.

### A new sheet never appears

The script skips any sheet with no entry in `remote/schema-checksums.json`:

```
No current checksum found for <SheetName> - skipping
```

That file is generated by `.github/workflows/regenerate-schemas.yaml`, which only runs on changes to
`remote/models/classes.yaml`, `slots.yaml` or `literals.yaml`. If a schema was added another way,
the checksums need regenerating before the tab can be created.

### Every sheet rebuilds when nothing visible changed

Expected when the checksum basis itself changes. The checksums cover only the columns the sheets
actually use; virtual columns are excluded, since they are CSV-W constants with no name, title or
cell and never reach a tab.

## Normal Maintenance Workflow (Primary Developer)

### Daily/Regular Operations

**Running the script to update sheets**:
1. Open the [MARCO-BOLO spreadsheet](https://docs.google.com/spreadsheets/d/1PBFK3LW3DAdvXdbk2v8bSdtTf87mBhabeeegwRjOBRg/edit)
2. Go to `Extensions` → `Apps Script`
3. Select `generateSheetsFromCSVW` function
4. Click `Run` (or set up time-based triggers for automation)
5. Monitor execution logs for any errors

**When to run**:
- After LinkML schema updates are merged to main branch
- When new entity types are added to the model
- If users report missing validation or incorrect sheet structure
- Generally not needed more than weekly unless actively developing

### Making Script Changes

**Development cycle**:
1. **Edit code** in this repository directory (not in Google Apps Script web editor)
2. **Test locally** if possible (syntax checking, etc.)
3. **Deploy to Google Apps Script**:
   ```bash
   clasp push
   ```
4. **Test in spreadsheet**:
   - Run functions in Apps Script editor
   - Verify sheet updates work correctly
   - Check that new validation rules apply properly
5. **Commit to repository**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

### Common Maintenance Tasks

**Adding support for new entity types**:
- Script automatically picks up new `.schema.json` files from repository
- No code changes needed if new entity follows standard pattern
- May need to update `syntheticSheetMap` for complex foreign key relationships

**Updating GitHub URLs** (if repository structure changes):
- Modify `GITHUB_RAW_BASE` and `SLOT_YAML_URL` constants
- Test that schema files are still accessible
- Deploy changes with `clasp push`

**Handling validation errors**:
- Check Apps Script execution logs for detailed error messages
- Common issues: 404 errors (schema files not found), JSON parsing errors
- Verify repository files are accessible at expected URLs

### Monitoring and Troubleshooting

**Check these regularly**:
- Apps Script execution logs for errors
- User feedback about sheet functionality
- GitHub repository for new schema files that need sheet creation

**Signs the script needs attention**:
- Users report missing dropdowns or validation
- New entity types appear in repository but no corresponding sheets
- 404 errors in execution logs
- Foreign key validation not working properly

### Emergency Fixes

**If script breaks production**:
1. **Identify the issue** in Apps Script execution logs
2. **Quick fix**: Revert to last working version with `clasp pull` from a backup
3. **Proper fix**: Debug in repository, test, then `clasp push`
4. **Communicate** with users about any temporary issues

**Rollback procedure**:
```bash
# If you need to revert to previous version
clasp versions  # List available versions
clasp deploy --versionNumber [previous_version]
```

## Emergency Contacts

- Original setup: steve@formeldataservices.com
- Repository maintainers: [Add current maintainer contacts]
- GCP billing account admin: [Add if different from owner]

## Migration Checklist (If Recreating)

If you need to create a new script project:

- [ ] Copy all code from repository
- [ ] Update GitHub raw URLs in script
- [ ] Test schema file fetching
- [ ] Verify sheet generation works
- [ ] Set up new service account if automation needed
- [ ] Update repository secrets for GitHub Actions
- [ ] Test end-to-end data flow
- [ ] Update documentation with new IDs