#!/usr/bin/env python3
"""
Replace Semantic IDs with UUIDs in CSV Files (including foreign keys)

This script runs after Google Sheets sync and before JSON-LD build.
It replaces semantic identifiers with UUIDs in CSV files so the rest
of the pipeline uses UUIDs.

This version replaces IDs in ALL columns, not just the primary ID column,
which handles foreign key references across CSVs.

Usage:
    python3 scripts/replace_ids_with_uuids.py --csv-dir data --registry config/uuid_mapping.json
"""

import csv
import sys
import os
import glob
from pathlib import Path

# Import the UUID registry helper
try:
    from scripts.uuid_lookup import UUIDRegistry
except ImportError:
    # If running from different directory
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.uuid_lookup import UUIDRegistry


def build_global_semantic_to_uuid_map(registry):
    """
    Build a single map of all semantic_id -> uuid across all classes.
    This allows us to replace IDs anywhere they appear, including foreign keys.
    
    Args:
        registry: UUIDRegistry instance
    
    Returns:
        Dict mapping semantic_id -> uuid
    """
    global_map = {}
    for class_name in registry.list_classes():
        class_uuids = registry.get_all_uuids(class_name)
        for semantic_id, uuid_val in class_uuids.items():
            global_map[semantic_id] = uuid_val
    return global_map


def replace_ids_in_csv(csv_path, global_map, dry_run=False):
    """
    Replace semantic IDs with UUIDs in ALL columns of a CSV file.
    This handles both primary IDs and foreign key references.
    
    Args:
        csv_path: Path to CSV file
        global_map: Dict mapping semantic_id -> uuid
        dry_run: If True, don't write changes
    
    Returns:
        Dict with statistics
    """
    rows = []
    replaced_count = 0
    replacements_by_column = {}
    fieldnames = None
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print(f"⚠️  {csv_path}: No columns found")
                return {'skipped': True, 'replaced': 0}
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                # Check every cell in every column
                for column_name in fieldnames:
                    cell_value = row.get(column_name, '').strip()
                    
                    # Skip empty cells
                    if not cell_value:
                        continue
                    
                    # Check if this value is a semantic ID we should replace
                    if cell_value in global_map:
                        uuid_val = global_map[cell_value]
                        row[column_name] = uuid_val
                        replaced_count += 1
                        
                        # Track which columns had replacements
                        if column_name not in replacements_by_column:
                            replacements_by_column[column_name] = 0
                        replacements_by_column[column_name] += 1
                
                rows.append(row)
        
        # Write back if not dry run
        if not dry_run and replaced_count > 0:
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        return {
            'skipped': False,
            'replaced': replaced_count,
            'columns': replacements_by_column
        }
    
    except Exception as e:
        print(f"  ❌ Error processing {csv_path}: {e}")
        return {'skipped': False, 'replaced': 0, 'columns': {}}


def process_csv_directory(csv_dir, registry_path, csv_pattern='*.csv', dry_run=False):
    """
    Process all CSV files in a directory, replacing semantic IDs with UUIDs.
    
    Args:
        csv_dir: Directory containing CSV files
        registry_path: Path to UUID registry file
        csv_pattern: Glob pattern for CSV files
        dry_run: If True, don't write changes
    """
    print("\n" + "="*60)
    print("Replace Semantic IDs with UUIDs (including foreign keys)")
    print("="*60 + "\n")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    # Load registry
    try:
        registry = UUIDRegistry(registry_path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nRun 'python3 scripts/sync_uuids.py' first to create the registry.")
        sys.exit(1)
    
    print(f"📂 Registry loaded from: {registry_path}")
    print(f"📊 Classes in registry: {', '.join(registry.list_classes())}\n")
    
    # Build global semantic ID -> UUID mapping
    print("🔨 Building global ID mapping...")
    global_map = build_global_semantic_to_uuid_map(registry)
    print(f"✅ Mapped {len(global_map)} semantic IDs to UUIDs\n")
    
    # Find CSV files
    csv_pattern_full = os.path.join(csv_dir, csv_pattern)
    csv_files = glob.glob(csv_pattern_full)
    
    if not csv_files:
        print(f"⚠️  No CSV files found matching: {csv_pattern_full}")
        return
    
    print(f"Found {len(csv_files)} CSV file(s)\n")
    print("-"*60 + "\n")
    
    # Process each CSV
    total_replaced = 0
    total_skipped = 0
    files_with_changes = []
    
    for csv_path in sorted(csv_files):
        csv_name = os.path.basename(csv_path)
        print(f"Processing: {csv_name}")
        
        result = replace_ids_in_csv(csv_path, global_map, dry_run)
        
        if result['skipped']:
            total_skipped += 1
        else:
            replaced = result['replaced']
            total_replaced += replaced
            
            if replaced > 0:
                files_with_changes.append(csv_name)
                print(f"  ✅ Replaced {replaced} ID(s)")
                
                # Show which columns had replacements
                columns = result.get('columns', {})
                if columns:
                    column_summary = ', '.join([f"{col} ({count})" for col, count in sorted(columns.items())])
                    print(f"     Columns: {column_summary}")
            else:
                print(f"  ⏭️  No IDs to replace")
        
        print()
    
    # Summary
    print("="*60)
    print("Summary")
    print("="*60)
    print(f"✅ Total IDs replaced: {total_replaced}")
    print(f"📝 Files modified: {len(files_with_changes)}")
    print(f"⏭️  Files skipped: {total_skipped}")
    
    if files_with_changes:
        print(f"\n📋 Files with changes:")
        for filename in files_with_changes:
            print(f"   - {filename}")
    
    print("="*60 + "\n")
    
    if dry_run:
        print("🔍 This was a dry run. Re-run without --dry-run to apply changes.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Replace semantic IDs with UUIDs in CSV files (including foreign keys)'
    )
    parser.add_argument(
        '--csv-dir',
        default='data',
        help='Directory containing CSV files (default: data)'
    )
    parser.add_argument(
        '--registry-path',
        default='config/uuid_mapping.json',
        help='Path to UUID registry file (default: config/uuid_mapping.json)'
    )
    parser.add_argument(
        '--csv-pattern',
        default='*.csv',
        help='Glob pattern for CSV files (default: *.csv)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    try:
        process_csv_directory(
            csv_dir=args.csv_dir,
            registry_path=args.registry_path,
            csv_pattern=args.csv_pattern,
            dry_run=args.dry_run
        )
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
