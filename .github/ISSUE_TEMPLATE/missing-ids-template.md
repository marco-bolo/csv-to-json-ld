---
title: "⚠️ Missing Identifiers Detected"
labels: ["uuid-sync", "needs-review"]
assignees: []
---

## Missing Identifier Report

**Generated:** {{ env.TIMESTAMP }}
**Workflow Run:** {{ env.GITHUB_SERVER_URL }}/{{ env.GITHUB_REPOSITORY }}/actions/runs/{{ env.GITHUB_RUN_ID }}

---

The following identifiers exist in the UUID registry but were **not found** in the current CSV files from Google Sheets. This typically happens when:

1. **Typo was fixed** - User corrected a misspelled identifier
2. **Identifier was renamed** - User changed the semantic meaning
3. **Record was deleted** - User intentionally removed the entry
4. **Temporary removal** - Record will be re-added later

### Action Required

For each missing identifier below, you need to manually update `config/uuid_mapping.json`:

- If **typo fix**: Update the registry to point the UUID to the corrected identifier
- If **renamed**: Update the registry to point the UUID to the new identifier  
- If **deleted**: Remove the UUID entry from the registry
- If **temporary**: No action needed, but document why

---

{{ env.MISSING_IDS_REPORT }}

---

## How to Update the Registry

### Option 1: Direct Edit

Edit `config/uuid_mapping.json` directly:

```json
{
  "PropertyValue": {
    "550e8400-e29b-41d4-a909-446655440000": "ebv_genetic_diversity",  // ← Update this value
    // or delete this line entirely
  }
}
```

### Option 2: Manual Mapping File

Create `config/id_corrections.json` to track intentional changes:

```json
{
  "PropertyValue": {
    "ebv_genetc_diversity": "ebv_genetic_diversity"  // old -> new
  }
}
```

Then run:
```bash
python scripts/apply_corrections.py
```

---

## Related Files

- **UUID Registry:** [`config/uuid_mapping.json`]({{ env.GITHUB_SERVER_URL }}/{{ env.GITHUB_REPOSITORY }}/blob/main/config/uuid_mapping.json)
- **Sync Report:** [`id_sync_report.json`]({{ env.GITHUB_SERVER_URL }}/{{ env.GITHUB_REPOSITORY }}/blob/main/id_sync_report.json)
- **Sync Script:** [`scripts/sync_uuids.py`]({{ env.GITHUB_SERVER_URL }}/{{ env.GITHUB_REPOSITORY }}/blob/main/scripts/sync_uuids.py)

---

**Note:** This issue will be automatically updated if more missing identifiers are detected in future runs.