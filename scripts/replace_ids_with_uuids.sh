#!/bin/bash
#
# Replace Semantic IDs with UUIDs in CSV Files using sed
#
# This script reads the UUID registry and generates sed commands to replace
# all semantic identifiers with their corresponding UUIDs across all CSV files.
# This handles IDs in any column, including list columns with comma-separated values.
#
# Usage:
#   bash scripts/replace_ids_with_uuids.sh <csv_dir> <registry_path>
#
# Example:
#   bash scripts/replace_ids_with_uuids.sh data config/uuid_mapping.json

set -e  # Exit on error

# Parse arguments
CSV_DIR="${1:-data}"
REGISTRY_PATH="${2:-config/uuid_mapping.json}"

echo "============================================================"
echo "Replace Semantic IDs with UUIDs (sed-based)"
echo "============================================================"
echo ""

# Check if registry exists
if [ ! -f "$REGISTRY_PATH" ]; then
    echo "❌ Registry not found at: $REGISTRY_PATH"
    echo ""
    echo "Run 'python3 scripts/sync_uuids.py' first to create the registry."
    exit 1
fi

echo "📂 Registry: $REGISTRY_PATH"
echo "📂 CSV directory: $CSV_DIR"
echo ""

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ 'jq' is required but not installed."
    echo "Install it with: apt-get install jq (Ubuntu) or brew install jq (macOS)"
    exit 1
fi

# Count CSV files
CSV_COUNT=$(find "$CSV_DIR" -name "*.csv" -type f | wc -l)
if [ "$CSV_COUNT" -eq 0 ]; then
    echo "⚠️  No CSV files found in $CSV_DIR"
    exit 0
fi

echo "Found $CSV_COUNT CSV file(s)"
echo ""

# Generate sed commands from registry
echo "🔨 Generating sed replacement commands..."

# Create temporary sed script
SED_SCRIPT=$(mktemp)

# Extract all semantic_id -> uuid mappings and generate sed commands
# The registry format is: {"ClassName": {"uuid": "semantic_id"}}
# We need to reverse this to get semantic_id -> uuid mappings
# Use word boundaries (\b) to prevent partial matches
jq -r '
  to_entries[] |
  .value |
  to_entries[] |
  "s/\\b\(.value)\\b/\(.key)/g"
' "$REGISTRY_PATH" > "$SED_SCRIPT"

# Count replacements
REPLACEMENT_COUNT=$(wc -l < "$SED_SCRIPT" | tr -d ' ')
echo "✅ Generated $REPLACEMENT_COUNT replacement rule(s)"
echo ""

if [ "$REPLACEMENT_COUNT" -eq 0 ]; then
    echo "⚠️  No replacements to perform"
    rm -f "$SED_SCRIPT"
    exit 0
fi

# Apply sed commands to all CSV files
echo "🔄 Applying replacements to CSV files..."
echo ""

MODIFIED_COUNT=0

for csv_file in "$CSV_DIR"/*.csv; do
    if [ ! -f "$csv_file" ]; then
        continue
    fi
    
    csv_name=$(basename "$csv_file")
    
    # Create backup
    cp "$csv_file" "$csv_file.backup"
    
    # Apply sed replacements
    sed -f "$SED_SCRIPT" "$csv_file.backup" > "$csv_file"
    
    # Check if file was modified
    if ! cmp -s "$csv_file" "$csv_file.backup"; then
        echo "  ✅ $csv_name (modified)"
        MODIFIED_COUNT=$((MODIFIED_COUNT + 1))
    else
        echo "  ⏭️  $csv_name (no changes)"
    fi
    
    # Remove backup
    rm -f "$csv_file.backup"
done

# Cleanup
rm -f "$SED_SCRIPT"

echo ""
echo "============================================================"
echo "Summary"
echo "============================================================"
echo "✅ Replacement rules applied: $REPLACEMENT_COUNT"
echo "📝 Files modified: $MODIFIED_COUNT"
echo "⏭️  Files unchanged: $((CSV_COUNT - MODIFIED_COUNT))"
echo "============================================================"
echo ""

if [ "$MODIFIED_COUNT" -gt 0 ]; then
    echo "✅ Successfully replaced semantic IDs with UUIDs"
else
    echo "ℹ️  No files required modification"
fi
