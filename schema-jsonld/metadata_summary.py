#!/usr/bin/env python3
"""
JSON-LD Metadata Summary Generator for MARCO-BOLO Catalog

This script generates human-readable summaries from JSON-LD schema.org metadata files.
It builds a graph of all resources and traverses relationships to create comprehensive reports.

Usage:
    python generate_summary.py <identifier> [--json-dir <directory>]
    
Example:
    python generate_summary.py mbo_wp2_d2
    python generate_summary.py https://w3id.org/marco-bolo/mbo_wp2_d2
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from datetime import datetime


class MetadataGraph:
    """A simple graph structure for JSON-LD metadata."""
    
    def __init__(self):
        """Initialize the graph."""
        self.nodes = {}  # Maps @id -> JSON data
        self.id_to_file = {}  # Maps @id -> filename for debugging
        
    def load_directory(self, json_dir: Path):
        """
        Load all JSON-LD files from a directory.
        
        Args:
            json_dir: Directory containing JSON-LD files
        """
        json_dir = Path(json_dir)
        
        for json_file in json_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if '@id' in data:
                    node_id = data['@id']
                    self.nodes[node_id] = data
                    self.id_to_file[node_id] = json_file.name
                    
            except Exception as e:
                print(f"Warning: Error loading {json_file}: {e}")
    
    def get_node(self, ref: Any) -> Optional[Dict]:
        """
        Get a node by reference (either string URL or dict with @id).
        
        Args:
            ref: Either a string URL or dict with @id key
            
        Returns:
            Node data or None
        """
        if isinstance(ref, str):
            return self.nodes.get(ref)
        elif isinstance(ref, dict) and '@id' in ref:
            return self.nodes.get(ref['@id'])
        return None
    
    def get_id(self, ref: Any) -> Optional[str]:
        """Extract @id from a reference."""
        if isinstance(ref, str):
            return ref
        elif isinstance(ref, dict) and '@id' in ref:
            return ref['@id']
        return None
    
    def extract_identifier(self, w3id_url: str) -> str:
        """Extract short identifier from w3id URL."""
        return w3id_url.rstrip('/').split('/')[-1]
    
    def find_related(self, node_id: str, visited: Optional[Set[str]] = None) -> Dict[str, List[Dict]]:
        """
        Find all resources related to a node by traversing relationships.
        
        Args:
            node_id: The @id to start from
            visited: Set of already visited nodes (to prevent cycles)
            
        Returns:
            Dict organizing related resources by relationship type
        """
        if visited is None:
            visited = set()
        
        if node_id in visited:
            return {}
        
        visited.add(node_id)
        
        node = self.nodes.get(node_id)
        if not node:
            return {}
        
        related = {
            'results': [],  # Things this action resulted in
            'inputs': [],   # Things that went into creating this
            'about': [],    # What this is about
            'distributions': [],  # Different formats/versions
            'people': [],   # Agents, creators, maintainers, participants
            'other': []     # Other relationships
        }
        
        # CRITICAL: Find all nodes that point TO this node via @reverse.result
        # These are metadata nodes that describe outputs of this action
        for other_id, other_node in self.nodes.items():
            if other_id in visited:
                continue
                
            if '@reverse' in other_node:
                reverse = other_node['@reverse']
                if 'result' in reverse:
                    result_ref = reverse['result']
                    refs = [result_ref] if not isinstance(result_ref, list) else result_ref
                    
                    for ref in refs:
                        ref_id = self.get_id(ref)
                        if ref_id == node_id:
                            # This node points back to us via @reverse.result
                            # Now check what it's 'about' - that's the actual output
                            if 'about' in other_node:
                                about_ref = other_node['about']
                                about_info = self._get_node_info(about_ref)
                                if about_info:
                                    related['results'].append(about_info)
                                    
                                    # Also recursively explore the output
                                    about_id = self.get_id(about_ref)
                                    if about_id:
                                        sub_related = self.find_related(about_id, visited)
                                        for key, values in sub_related.items():
                                            if key not in ['results']:  # Avoid duplication
                                                related[key].extend(values)
        
        # Process @reverse relationships (things pointing TO this node)
        if '@reverse' in node:
            reverse = node['@reverse']
            
            # Check for "result" - things that this is a result of
            if 'result' in reverse:
                result_ref = reverse['result']
                if isinstance(result_ref, list):
                    for ref in result_ref:
                        related['inputs'].append(self._get_node_info(ref))
                else:
                    related['inputs'].append(self._get_node_info(result_ref))
        
        # Process forward relationships (things this node points TO)
        
        # Results - what this action produced
        if 'result' in node:
            result = node['result']
            if isinstance(result, list):
                for item in result:
                    info = self._get_node_info(item)
                    if info:
                        related['results'].append(info)
                        # Recursively explore results
                        item_id = self.get_id(item)
                        if item_id:
                            sub_related = self.find_related(item_id, visited)
                            # Merge sub-results
                            for key, values in sub_related.items():
                                related[key].extend(values)
            else:
                info = self._get_node_info(result)
                if info:
                    related['results'].append(info)
        
        # About - what this resource describes
        if 'about' in node:
            about = node['about']
            info = self._get_node_info(about)
            if info:
                related['about'].append(info)
                # Recursively explore what it's about
                about_id = self.get_id(about)
                if about_id and about_id not in visited:
                    sub_related = self.find_related(about_id, visited)
                    for key, values in sub_related.items():
                        if key not in ['about']:  # Avoid infinite loops
                            related[key].extend(values)
        
        # Distributions
        if 'distribution' in node:
            dist = node['distribution']
            if isinstance(dist, list):
                for item in dist:
                    info = self._get_node_info(item)
                    if info:
                        related['distributions'].append(info)
            else:
                info = self._get_node_info(dist)
                if info:
                    related['distributions'].append(info)
        
        # People and organizations
        for prop in ['agent', 'participant', 'creator', 'maintainer', 'contributor']:
            if prop in node:
                person = node[prop]
                if isinstance(person, list):
                    for p in person:
                        info = self._get_node_info(p)
                        if info:
                            info['role'] = prop
                            related['people'].append(info)
                else:
                    info = self._get_node_info(person)
                    if info:
                        info['role'] = prop
                        related['people'].append(info)
        
        # Remove duplicates while preserving order
        for key in related:
            seen = set()
            unique = []
            for item in related[key]:
                item_id = item.get('id')
                if item_id not in seen:
                    seen.add(item_id)
                    unique.append(item)
            related[key] = unique
        
        return related
    
    def _get_node_info(self, ref: Any) -> Optional[Dict]:
        """
        Get summary information about a node.
        
        Args:
            ref: Reference to the node
            
        Returns:
            Dict with node summary info
        """
        node = self.get_node(ref)
        if not node:
            # Even if we don't have the node, return the ID
            node_id = self.get_id(ref)
            if node_id:
                return {
                    'id': node_id,
                    'identifier': self.extract_identifier(node_id),
                    'type': 'Unknown',
                    'data': {}
                }
            return None
        
        node_id = node.get('@id', '')
        
        # Try to get a human-readable name
        name = node.get('name', '')
        if not name:
            # Try alternative name fields
            name = node.get('givenName', '') + ' ' + node.get('familyName', '')
            name = name.strip()
        
        return {
            'id': node_id,
            'identifier': self.extract_identifier(node_id),
            'type': node.get('@type', 'Unknown'),
            'name': name,
            'description': node.get('description', ''),
            'abstract': node.get('abstract', ''),
            'data': node  # Keep full data for detailed access
        }


class JSONLDSummarizer:
    """Generates human-readable summaries from JSON-LD metadata catalogs."""
    
    def __init__(self, json_dir: Path):
        """
        Initialize the summarizer.
        
        Args:
            json_dir: Directory containing JSON-LD files
        """
        self.graph = MetadataGraph()
        print(f"Loading JSON-LD files from {json_dir}...")
        self.graph.load_directory(json_dir)
        print(f"Loaded {len(self.graph.nodes)} resources")
    
    def find_id_by_identifier(self, identifier: str) -> Optional[str]:
        """
        Find full @id URL by short identifier.
        
        Args:
            identifier: Short identifier (e.g., 'mbo_wp2_d2')
            
        Returns:
            Full @id URL or None
        """
        # First check if it's already a full URL
        if identifier in self.graph.nodes:
            return identifier
        
        # Search for matching identifier
        for node_id in self.graph.nodes:
            if self.graph.extract_identifier(node_id) == identifier:
                return node_id
        
        return None
    
    def format_value(self, value: Any) -> str:
        """Format a value for display."""
        if isinstance(value, dict):
            if '@value' in value:
                return str(value['@value'])
            elif '@id' in value:
                return self.graph.extract_identifier(value['@id'])
        return str(value)
    
    def generate_summary(self, identifier: str) -> str:
        """
        Generate a human-readable summary for an identifier.
        
        Args:
            identifier: The identifier or @id URL to summarize
            
        Returns:
            Formatted summary string
        """
        # Find the full @id
        node_id = self.find_id_by_identifier(identifier)
        
        if not node_id:
            return f"Error: Could not find resource with identifier '{identifier}'"
        
        node = self.graph.nodes[node_id]
        short_id = self.graph.extract_identifier(node_id)
        
        summary = []
        summary.append("=" * 80)
        summary.append(f"SUMMARY: {short_id}")
        summary.append("=" * 80)
        summary.append("")
        
        # Basic Information
        summary.append("### BASIC INFORMATION")
        summary.append("")
        
        type_info = node.get('@type', 'Unknown')
        summary.append(f"**Type:** {type_info}")
        
        if 'name' in node:
            summary.append(f"**Name:** {node['name']}")
        
        summary.append(f"**ID:** {node_id}")
        summary.append("")
        
        # Description/Abstract
        if 'abstract' in node:
            summary.append("### ABSTRACT")
            summary.append("")
            summary.append(self._wrap_text(node['abstract']))
            summary.append("")
        
        if 'description' in node and 'abstract' not in node:
            summary.append("### DESCRIPTION")
            summary.append("")
            summary.append(self._wrap_text(node['description']))
            summary.append("")
        
        # Key Properties (excluding relationships we'll handle separately)
        summary.append("### PROPERTIES")
        summary.append("")
        
        skip_props = ['@context', '@id', '@type', '@reverse', 'name', 'description', 
                     'abstract', 'result', 'about', 'distribution', 'agent', 
                     'participant', 'creator', 'maintainer', 'contributor']
        
        for key, value in node.items():
            if key in skip_props:
                continue
            
            # Handle custom namespace properties
            if key.startswith('https://'):
                prop_name = key.split('/')[-1]
            else:
                prop_name = key
            
            formatted = self.format_value(value)
            prop_name = prop_name.replace('_', ' ').title()
            summary.append(f"- **{prop_name}:** {formatted}")
        
        summary.append("")
        
        # Find all related resources
        print(f"Finding related resources for {short_id}...")
        related = self.graph.find_related(node_id)
        
        # People/Organizations
        if related['people']:
            summary.append("### PEOPLE & ORGANIZATIONS")
            summary.append("")
            
            # Group by role
            by_role = defaultdict(list)
            for person in related['people']:
                role = person.get('role', 'related').title()
                by_role[role].append(person)
            
            for role in sorted(by_role.keys()):
                summary.append(f"#### {role}")
                for person in by_role[role]:
                    person_id = person['identifier']
                    person_name = person.get('name', '')
                    
                    # Show name if available, otherwise just identifier
                    if person_name:
                        summary.append(f"- **{person_name}** ({person_id})")
                    else:
                        summary.append(f"- {person_id}")
                    
                    # Add any additional person info if available
                    person_data = person['data']
                    details = []
                    if 'email' in person_data:
                        details.append(f"Email: {person_data['email']}")
                    if 'affiliation' in person_data:
                        aff = self.format_value(person_data['affiliation'])
                        details.append(f"Affiliation: {aff}")
                    if details:
                        summary.append(f"  {' | '.join(details)}")
                
                summary.append("")
            
            # Remove the extra blank line at the end
            if summary[-1] == "":
                summary.pop()
            summary.append("")
        
        # Results - what this action produced
        if related['results']:
            summary.append("### OUTPUTS")
            summary.append("")
            summary.append("This action resulted in the following resources:")
            summary.append("")
            
            # Group by type
            by_type = defaultdict(list)
            for result in related['results']:
                by_type[result['type']].append(result)
            
            for res_type in sorted(by_type.keys()):
                summary.append(f"#### {res_type}")
                summary.append("")
                for result in by_type[res_type]:
                    self._add_resource_detail(summary, result)
                summary.append("")
        
        # About - what describes this
        if related['about']:
            summary.append("### DESCRIBED BY")
            summary.append("")
            for about in related['about']:
                self._add_resource_detail(summary, about)
            summary.append("")
        
        # Distributions
        if related['distributions']:
            summary.append("### AVAILABLE FORMATS")
            summary.append("")
            for dist in related['distributions']:
                dist_data = dist['data']
                fmt = dist_data.get('encodingFormat', 'unknown')
                summary.append(f"- **{fmt}**")
                
                if 'schema:contentUrl' in dist_data or 'contentUrl' in dist_data:
                    url_data = dist_data.get('schema:contentUrl') or dist_data.get('contentUrl')
                    url = self.format_value(url_data)
                    summary.append(f"  URL: {url}")
                
                if 'dateModified' in dist_data:
                    date = dist_data['dateModified']
                    summary.append(f"  Modified: {date}")
            summary.append("")
        
        summary.append("=" * 80)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Total resources in graph: {len(self.graph.nodes)}")
        summary.append("=" * 80)
        
        return "\n".join(summary)
    
    def _add_resource_detail(self, summary: List[str], resource: Dict, indent: int = 0):
        """Add detailed information about a resource."""
        prefix = "  " * indent
        
        name = resource.get('name') or resource['identifier']
        res_type = resource['type']
        identifier = resource['identifier']
        
        # For Person types, show simplified format without type label
        if res_type == 'Person':
            if resource.get('name'):
                summary.append(f"{prefix}{name}")
            else:
                summary.append(f"{prefix}{identifier}")
            
            # Add person details if available
            data = resource['data']
            details = []
            if 'givenName' in data or 'familyName' in data:
                full_name = f"{data.get('givenName', '')} {data.get('familyName', '')}".strip()
                if full_name and full_name != name:
                    details.append(f"Name: {full_name}")
            if 'email' in data:
                details.append(f"Email: {data['email']}")
            if 'affiliation' in data:
                aff = self.format_value(data['affiliation'])
                details.append(f"Affiliation: {aff}")
            
            if details:
                summary.append(f"{prefix}{' | '.join(details)}")
            return
        
        summary.append(f"{prefix}**{name}** ({identifier})")
        
        # Description - show both abstract and description with labels
        abstract = resource.get('abstract', '')
        desc = resource.get('description', '')
        
        if abstract:
            summary.append(f"{prefix}Abstract: {abstract}")
            if desc and desc != abstract:
                summary.append(f"{prefix}Description: {desc}")
        elif desc:
            summary.append(f"{prefix}Description: {desc}")
        
        # Status and dates
        data = resource['data']
        status_parts = []
        
        if 'creativeWorkStatus' in data:
            status = self.format_value(data['creativeWorkStatus'])
            status_parts.append(f"Status: {status}")
        
        # Check for dates
        for date_key in ['datePublished', 'dateModified', 'dateCreated', 'inProgressDate']:
            if date_key in data:
                date_val = self.format_value(data[date_key])
                label = date_key.replace('Date', '').replace('inProgress', 'Expected')
                status_parts.append(f"{label}: {date_val}")
            
            # Check custom namespace
            custom_key = f"https://w3id.org/marco-bolo/{date_key}"
            if custom_key in data:
                date_val = self.format_value(data[custom_key])
                label = date_key.replace('Date', '').replace('inProgress', 'Expected')
                status_parts.append(f"{label}: {date_val}")
        
        if status_parts:
            summary.append(f"{prefix}[{' | '.join(status_parts)}]")
        
        # URLs
        for url_key in ['url', 'schema:url']:
            if url_key in data:
                url = self.format_value(data[url_key])
                summary.append(f"{prefix}🔗 {url}")
        
        summary.append("")
    
    def _wrap_text(self, text: str, width: int = 80, indent: int = 0) -> str:
        """Simple text wrapping with optional indentation."""
        words = text.split()
        lines = []
        current_line = []
        indent_str = ' ' * indent
        effective_width = width - indent
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > effective_width:
                lines.append(indent_str + ' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(indent_str + ' '.join(current_line))
        
        return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate human-readable summaries from JSON-LD metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_summary.py mbo_wp2_d2
  python generate_summary.py mbo_wp2_d2 --json-dir ./metadata/
  python generate_summary.py mbo_wp2_d2 --output report.txt
  python generate_summary.py https://w3id.org/marco-bolo/mbo_wp2_d2
        """
    )
    
    parser.add_argument('identifier', 
                       help='The identifier to summarize (short form or full @id URL)')
    parser.add_argument('--json-dir', 
                       default='.',
                       help='Directory containing JSON-LD files (default: current directory)')
    parser.add_argument('--output', '-o',
                       help='Output file (default: print to stdout)')
    
    args = parser.parse_args()
    
    # Create summarizer (loads all files)
    summarizer = JSONLDSummarizer(args.json_dir)
    
    # Generate summary
    summary = summarizer.generate_summary(args.identifier)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"\nSummary written to {args.output}")
    else:
        print(summary)


if __name__ == '__main__':
    main()
