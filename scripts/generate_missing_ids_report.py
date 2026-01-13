#!/usr/bin/env python3
"""
Generate Missing IDs Report

Reads the sync report and generates formatted markdown for the GitHub issue.
"""

import json
import sys


def format_missing_ids_report(report_path='id_sync_report.json'):
    """
    Generate formatted markdown report from sync report.
    
    Args:
        report_path: Path to the JSON sync report
    
    Returns:
        Formatted markdown string
    """
    try:
        with open(report_path) as f:
            report = json.load(f)
    except FileNotFoundError:
        return "⚠️ No sync report found. Run `sync_uuids.py` first."
    
    missing_ids = report.get('missing_ids', [])
    
    if not missing_ids:
        return "✅ No missing identifiers detected. All identifiers in the registry are present in current CSV files."
    
    # Group by class
    by_class = {}
    for item in missing_ids:
        class_name = item['class']
        if class_name not in by_class:
            by_class[class_name] = []
        by_class[class_name].append(item)
    
    # Generate markdown
    lines = []
    lines.append(f"### Summary\n")
    lines.append(f"**Total missing identifiers:** {len(missing_ids)}\n")
    lines.append(f"**Classes affected:** {len(by_class)}\n")
    
    for class_name, items in sorted(by_class.items()):
        lines.append(f"\n### Class: `{class_name}`\n")
        lines.append(f"**Missing count:** {len(items)}\n")
        
        for item in items:
            lines.append(f"\n#### `{item['semantic_id']}`\n")
            lines.append(f"- **UUID:** `{item['uuid']}`")
            
            # Show similar matches if any
            if item.get('similar'):
                lines.append(f"- **Possible matches in current sheets:**")
                for candidate, ratio in item['similar']:
                    lines.append(f"  - `{candidate}` ({ratio:.0%} similar)")
            else:
                lines.append(f"- **No similar identifiers found**")
            
            lines.append(f"\n**Action checklist:**")
            lines.append(f"- [ ] Reviewed and decided on action")
            lines.append(f"- [ ] Updated `config/uuid_mapping.json` if needed")
            lines.append(f"- [ ] Documented reason for change")
            lines.append("")
    
    return "\n".join(lines)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate missing IDs report')
    parser.add_argument('--report-path', default='id_sync_report.json',
                        help='Path to sync report JSON')
    parser.add_argument('--output', default='missing_ids_report.md',
                        help='Output markdown file')
    
    args = parser.parse_args()
    
    report_content = format_missing_ids_report(args.report_path)
    
    # Write to file
    with open(args.output, 'w') as f:
        f.write(report_content)
    
    print(f"✅ Report written to {args.output}")
    
    # Also print to stdout for GitHub Actions
    print("\n" + "="*60)
    print(report_content)
    print("="*60)