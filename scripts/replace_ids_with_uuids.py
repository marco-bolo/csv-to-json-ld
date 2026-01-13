#!/usr/bin/env python3
"""
Replace Semantic IDs with UUIDs in CSV Files

This script runs after Google Sheets sync and before JSON-LD build.
It replaces semantic identifiers with UUIDs in CSV files so the rest
of the pipeline uses UUIDs.

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


def get_class_name_from_csv_path(csv_path):
    """
    Extract class name from CSV file path.
    
    Examples:
        'data/PropertyValue.csv' -> 'PropertyValue'
        'remote/Action.csv' -> 'Action'
    """
    return Path(csv_path).stem


def replace_ids_in_csv(csv_path, registry, id_column='id', dry_run=False):
    """
    Replace semantic IDs with UUIDs in a CSV file.
    
    Args:
        csv_path: Path to CSV file
        registry: UUIDRegistry instance
        id_column: Name of the ID column (default: 'id')
        dry_run: If True, don't write changes
    
    Returns:
        Dict with statistics
    """
    class_name = get_class_name_from_csv_path(csv_path)
    
    # Check if this class exists in registry
    if not registry.has_class(class_name):
        print(f"⏭️  Skipping {csv_path}: {class_name} not in registry")
        return {'skipped': True, 'replaced': 0, 'errors': 0}
    
    rows = []
    replaced_count = 0
    error_count = 0
    fieldnames = None
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print(f"⚠️  {csv_path}: No columns found")
                return {'skipped': True, 'replaced': 0, 'errors': 0}
            
            if id_column not in fieldnames:
                print(f"⏭️  Skipping {csv_path}: No '{id_column}' column")
                return {'skipped': True, 'replaced': 0, 'errors': 0}
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                semantic_id = row.get(id_column, '').strip()
                
                # Skip empty rows
                if not semantic_id:
                    rows.append(row)
                    continue
                
                # Look up UUID for this semantic ID
                try:
                    uuid = registry.get_uuid(class_name, semantic_id, required=True)
                    
                    # Replace semantic ID with UUID
                    row[id_column] = uuid
                    replaced_count += 1
                    
                except ValueError as e:
                    print(f"  ❌ Row {row_num}: {e}")
                    error_count += 1
                    # Keep original semantic ID if UUID lookup fails
                
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
            'errors': error_count
        }
    
    except Exception as e:
        print(f"  ❌ Error processing {csv_path}: {e}")
        return {'skipped': False, 'replaced': 0, 'errors': 1}


def process_csv_directory(csv_dir, registry_path, id_column='id', csv_pattern='*.csv', dry_run=False):
    """
    Process all CSV files in a directory.
    
    Args:
        csv_dir: Directory containing CSV files
        registry_path: Path to UUID registry file
        id_column: Name of ID column
        csv_pattern: Glob pattern for CSV files
        dry_run: If True, don't write changes
    """
    print("\n" + "="*60)
    print("Replace Semantic IDs with UUIDs")
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
    total_errors = 0
    total_skipped = 0
    
    for csv_path in sorted(csv_files):
        print(f"Processing: {csv_path}")
        
        result = replace_ids_in_csv(csv_path, registry, id_column, dry_run)
        
        if result['skipped']:
            total_skipped += 1
        else:
            total_replaced += result['replaced']
            total_errors += result['errors']
            
            if result['replaced'] > 0:
                print(f"  ✅ Replaced {result['replaced']} semantic ID(s) with UUID(s)")
            if result['errors'] > 0:
                print(f"  ⚠️  {result['errors']} error(s)")
        
        print()
    
    # Summary
    print("="*60)
    print("Summary")
    print("="*60)
    print(f"✅ Total IDs replaced: {total_replaced}")
    print(f"⏭️  Files skipped: {total_skipped}")
    print(f"❌ Total errors: {total_errors}")
    print("="*60 + "\n")
    
    if total_errors > 0:
        print("⚠️  Some IDs could not be replaced. Check errors above.")
        sys.exit(1)
    
    if dry_run:
        print("🔍 This was a dry run. Re-run without --dry-run to apply changes.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Replace semantic IDs with UUIDs in CSV files'
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
        '--id-column',
        default='id',
        help='Name of ID column in CSVs (default: id)'
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
            id_column=args.id_column,
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