#!/usr/bin/env python3
"""
UUID Registry Sync Script

This script manages the mapping between UUIDs and user-generated semantic identifiers.
It should be run BEFORE the JSON-LD build process.

Workflow:
1. Read all semantic IDs from CSV files
2. Check UUID registry for each ID
3. Generate UUIDs for NEW semantic IDs
4. Detect MISSING semantic IDs (in registry but not in current CSVs)
5. Update registry file
6. Create report for GitHub Actions
"""

import json
import uuid
import glob
import csv
import os
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


def load_registry(path='config/uuid_mapping.json'):
    """Load the UUID registry from JSON file."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Registry not found at {path}, creating new registry")
        return {}


def save_registry(registry, path='config/uuid_mapping.json'):
    """Save the UUID registry to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(registry, f, indent=2, sort_keys=True)
    print(f"✅ Registry saved to {path}")


def generate_uuid():
    """Generate a new UUID v4 with mbo_ prefix."""
    return f"mbo_{uuid.uuid4()}"


def find_similar(target, candidates, threshold=0.75):
    """
    Find similar strings using fuzzy matching.
    
    Args:
        target: The string to match against
        candidates: List of strings to search through
        threshold: Minimum similarity ratio (0-1)
    
    Returns:
        List of (candidate, ratio) tuples sorted by similarity
    """
    matches = []
    for candidate in candidates:
        ratio = SequenceMatcher(None, target.lower(), candidate.lower()).ratio()
        if ratio >= threshold:
            matches.append((candidate, ratio))
    return sorted(matches, key=lambda x: x[1], reverse=True)


def read_csv_identifiers(csv_pattern='out/*.csv', id_column='id'):
    """
    Read semantic identifiers from CSV files.
    
    Args:
        csv_pattern: Glob pattern to match CSV files
        id_column: Name of the column containing identifiers
    
    Returns:
        Dict mapping class_name -> list of semantic IDs
    """
    current_ids = {}
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"⚠️  No CSV files found matching pattern: {csv_pattern}")
        return current_ids
    
    for csv_file in csv_files:
        # Extract class name from filename (e.g., 'PropertyValue.csv' -> 'PropertyValue')
        class_name = Path(csv_file).stem
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if id_column not in reader.fieldnames:
                    print(f"⚠️  Column '{id_column}' not found in {csv_file}")
                    continue
                
                ids = [row[id_column] for row in reader if row.get(id_column, '').strip()]
                current_ids[class_name] = ids
                print(f"📄 Read {len(ids)} identifiers from {class_name}")
        
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {e}")
            continue
    
    return current_ids


def create_reverse_mapping(registry):
    """
    Create a reverse mapping from semantic_id -> uuid for quick lookups.
    
    Args:
        registry: The UUID registry (class -> uuid -> semantic_id)
    
    Returns:
        Dict mapping class_name -> semantic_id -> uuid
    """
    reverse_registry = {}
    for class_name, uuid_map in registry.items():
        reverse_registry[class_name] = {v: k for k, v in uuid_map.items()}
    return reverse_registry


def sync_uuids(csv_pattern='out/*.csv', registry_path='config/uuid_mapping.json', id_column='id'):
    """
    Main sync function that manages UUID registry.
    
    Returns:
        Dict containing sync report with new_ids and missing_ids
    """
    print("\n" + "="*60)
    print("UUID Registry Sync")
    print("="*60 + "\n")
    
    # Load existing registry
    registry = load_registry(registry_path)
    
    # Read current semantic IDs from CSVs
    current_ids = read_csv_identifiers(csv_pattern, id_column)
    
    if not current_ids:
        print("\n⚠️  No identifiers found in CSV files. Exiting.")
        return {'new_ids': [], 'missing_ids': [], 'timestamp': datetime.utcnow().isoformat()}
    
    # Create reverse mapping for efficient lookups
    reverse_registry = create_reverse_mapping(registry)
    
    # Track changes
    new_ids = []
    missing_ids = []
    
    print("\n" + "-"*60)
    print("Processing Changes")
    print("-"*60 + "\n")
    
    # Process each class
    for class_name, semantic_ids in current_ids.items():
        if class_name not in registry:
            registry[class_name] = {}
            print(f"🆕 New class detected: {class_name}")
        
        # Check for new IDs
        for semantic_id in semantic_ids:
            if semantic_id not in reverse_registry.get(class_name, {}):
                # New ID - generate UUID
                new_uuid = generate_uuid()
                registry[class_name][new_uuid] = semantic_id
                new_ids.append({
                    'class': class_name,
                    'uuid': new_uuid,
                    'semantic_id': semantic_id
                })
                print(f"  ✨ NEW: {class_name}/{semantic_id} -> {new_uuid}")
    
    # Check for missing IDs (in registry but not in current CSVs)
    for class_name, uuid_map in registry.items():
        current_class_ids = current_ids.get(class_name, [])
        
        for uuid_val, semantic_id in uuid_map.items():
            if semantic_id not in current_class_ids:
                # Find similar IDs that might be typo fixes
                similar = find_similar(semantic_id, current_class_ids)
                missing_ids.append({
                    'class': class_name,
                    'uuid': uuid_val,
                    'semantic_id': semantic_id,
                    'similar': similar[:3]  # Top 3 matches
                })
                print(f"  ⚠️  MISSING: {class_name}/{semantic_id} (UUID: {uuid_val})")
                if similar:
                    print(f"      Possible match: {similar[0][0]} ({similar[0][1]:.0%} similar)")
    
    # Save updated registry
    print("\n" + "-"*60)
    save_registry(registry, registry_path)
    
    # Generate report
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'new_ids': new_ids,
        'missing_ids': missing_ids
    }
    
    with open('id_sync_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("📊 Report saved to id_sync_report.json")
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"✅ New IDs added: {len(new_ids)}")
    print(f"⚠️  Missing IDs detected: {len(missing_ids)}")
    print("="*60 + "\n")
    
    # Set outputs for GitHub Actions
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"new_count={len(new_ids)}\n")
            f.write(f"missing_count={len(missing_ids)}\n")
            f.write(f"has_missing={str(len(missing_ids) > 0).lower()}\n")
            f.write(f"has_new={str(len(new_ids) > 0).lower()}\n")
    
    return report


if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync UUID registry with semantic identifiers')
    parser.add_argument('--csv-pattern', default='out/*.csv', 
                        help='Glob pattern for CSV files (default: out/*.csv)')
    parser.add_argument('--registry-path', default='config/uuid_mapping.json',
                        help='Path to UUID registry file (default: config/uuid_mapping.json)')
    parser.add_argument('--id-column', default='id',
                        help='Name of ID column in CSVs (default: id)')
    
    args = parser.parse_args()
    
    try:
        report = sync_uuids(
            csv_pattern=args.csv_pattern,
            registry_path=args.registry_path,
            id_column=args.id_column
        )
        
        # Exit with error code if there are missing IDs (to trigger manual review)
        if report['missing_ids']:
            print("⚠️  Missing IDs detected. Manual review required.")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
