#!/usr/bin/env python3
"""
UUID Lookup Helper

This module provides functions to look up UUIDs from the registry during JSON-LD build.
Import this in your JSON-LD generation code.

Usage:
    from scripts.uuid_lookup import UUIDRegistry
    
    registry = UUIDRegistry()
    uuid = registry.get_uuid('PropertyValue', 'ebv_genetic_diversity')
"""

import json
import sys
from pathlib import Path


class UUIDRegistry:
    """Helper class for looking up UUIDs from the registry."""
    
    def __init__(self, registry_path='config/uuid_mapping.json'):
        """
        Initialize the UUID registry.
        
        Args:
            registry_path: Path to the UUID mapping JSON file
        """
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.reverse_mapping = self._create_reverse_mapping()
    
    def _load_registry(self):
        """Load the UUID registry from file."""
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"UUID registry not found at {self.registry_path}. "
                "Run scripts/sync_uuids.py first."
            )
        
        with open(self.registry_path) as f:
            return json.load(f)
    
    def _create_reverse_mapping(self):
        """Create reverse mapping: class -> semantic_id -> uuid."""
        reverse = {}
        for class_name, uuid_map in self.registry.items():
            reverse[class_name] = {semantic_id: uuid_val 
                                   for uuid_val, semantic_id in uuid_map.items()}
        return reverse
    
    def get_uuid(self, class_name, semantic_id, required=True):
        """
        Get UUID for a semantic identifier.
        
        Args:
            class_name: The class/table name (e.g., 'PropertyValue')
            semantic_id: The semantic identifier (e.g., 'ebv_genetic_diversity')
            required: If True, raise error when UUID not found. If False, return None.
        
        Returns:
            UUID string, or None if not found and required=False
        
        Raises:
            ValueError: If UUID not found and required=True
        """
        uuid_val = self.reverse_mapping.get(class_name, {}).get(semantic_id)
        
        if uuid_val is None and required:
            raise ValueError(
                f"No UUID found for {class_name}/{semantic_id}. "
                "This identifier may not exist in the registry. "
                "Run scripts/sync_uuids.py to generate UUIDs for new identifiers."
            )
        
        return uuid_val
    
    def get_semantic_id(self, class_name, uuid_val):
        """
        Get semantic identifier for a UUID (reverse lookup).
        
        Args:
            class_name: The class/table name
            uuid_val: The UUID
        
        Returns:
            Semantic identifier string, or None if not found
        """
        return self.registry.get(class_name, {}).get(uuid_val)
    
    def get_all_uuids(self, class_name):
        """
        Get all UUIDs for a given class.
        
        Args:
            class_name: The class/table name
        
        Returns:
            Dict mapping semantic_id -> uuid
        """
        return self.reverse_mapping.get(class_name, {})
    
    def has_class(self, class_name):
        """Check if a class exists in the registry."""
        return class_name in self.registry
    
    def list_classes(self):
        """Get list of all classes in the registry."""
        return list(self.registry.keys())


def main():
    """Command-line interface for UUID lookup."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Look up UUIDs from registry')
    parser.add_argument('class_name', help='Class name (e.g., PropertyValue)')
    parser.add_argument('semantic_id', help='Semantic identifier to look up')
    parser.add_argument('--registry-path', default='config/uuid_mapping.json',
                        help='Path to UUID registry file')
    
    args = parser.parse_args()
    
    try:
        registry = UUIDRegistry(args.registry_path)
        uuid_val = registry.get_uuid(args.class_name, args.semantic_id)
        print(uuid_val)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()