#!/usr/bin/env python3
"""
Generate an HTML/SVG diagram from a LinkML schema and configuration file.

Usage:
    python generate_diagram.py classes.yaml diagram_config.yaml output.html
"""

import yaml
import sys
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class EntityInfo:
    name: str
    slots: List[str]
    slot_titles: Dict[str, str]  # Map of slot name to title
    color: str
    group_number: int = None  # Group number for fill-out order
    in_subgraph: str = None

@dataclass
class Relationship:
    source: str
    target: str
    slot_name: str
    label: str = ""

def load_yaml(filepath: Path) -> dict:
    """Load a YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def load_slot_titles(schema_path: Path) -> Dict[str, str]:
    """Load slot definitions and extract titles."""
    # Try to find slots.yaml in the same directory as the schema
    slots_path = schema_path.parent / 'slots.yaml'
    
    if not slots_path.exists():
        # Return empty dict if slots file not found
        return {}
    
    slots_data = load_yaml(slots_path)
    slots = slots_data.get('slots', {})
    
    # Map slot names to titles
    slot_titles = {}
    for slot_name, slot_def in slots.items():
        title = slot_def.get('title', slot_name)
        slot_titles[slot_name] = title
    
    return slot_titles

def resolve_inherited_slots(class_name: str, classes: dict, visited: Set[str] = None) -> List[str]:
    """Recursively resolve slots including inherited ones from parent classes."""
    if visited is None:
        visited = set()
    
    # Prevent infinite recursion
    if class_name in visited:
        return []
    visited.add(class_name)
    
    if class_name not in classes:
        return []
    
    class_def = classes[class_name]
    
    # Start with directly defined slots
    slots = list(class_def.get('slots', []))
    
    # Add inherited slots from parent class (is_a)
    parent = class_def.get('is_a')
    if parent:
        parent_slots = resolve_inherited_slots(parent, classes, visited)
        # Add parent slots that aren't already in the list (preserve order)
        for slot in parent_slots:
            if slot not in slots:
                slots.append(slot)
    
    # Add inherited slots from mixins
    mixins = class_def.get('mixins', [])
    for mixin in mixins:
        mixin_slots = resolve_inherited_slots(mixin, classes, visited)
        for slot in mixin_slots:
            if slot not in slots:
                slots.append(slot)
    
    return slots

def parse_linkml_schema(schema_path: Path, config: dict) -> Tuple[Dict[str, EntityInfo], List[Relationship]]:
    """Parse LinkML schema and extract entities and relationships."""
    schema = load_yaml(schema_path)
    classes = schema.get('classes', {})
    
    # Load slot titles
    slot_titles = load_slot_titles(schema_path)
    
    # Get entity type classifications from config
    mandatory = set(config['entity_types']['mandatory'])
    optional = set(config['entity_types']['optional'])
    conditional = set(config['entity_types']['conditional'])
    
    # Get entity group numbers from config
    entity_group_map = {}
    if 'entity_groups' in config:
        for group_num, entity_list in config['entity_groups'].items():
            for entity_name in entity_list:
                entity_group_map[entity_name] = int(group_num)
    
    # Get subgraph memberships
    subgraph_map = {}
    for subgraph in config['subgraphs']:
        for entity in subgraph['entities']:
            subgraph_map[entity] = subgraph['name']
    
    # Extract entities
    entities = {}
    
    for class_name, class_def in classes.items():
        # Skip abstract classes
        if class_def.get('abstract', False):
            continue
        
        # Determine color
        if class_name in mandatory:
            color = config['colors']['mandatory']
        elif class_name in optional:
            color = config['colors']['optional']
        else:
            color = config['colors']['conditional']
        
        # Get slots including inherited ones
        slots = resolve_inherited_slots(class_name, classes)
        
        # Filter out excluded fields if configured
        if config['field_display']['show_all_fields']:
            exclude = set(config['field_display'].get('exclude_fields', []))
            slots = [s for s in slots if s not in exclude]
        
        entities[class_name] = EntityInfo(
            name=class_name,
            slots=slots,
            slot_titles=slot_titles,
            color=color,
            group_number=entity_group_map.get(class_name),
            in_subgraph=subgraph_map.get(class_name)
        )
    
    # Extract relationships from explicit config connections
    relationships = []
    if 'connections' in config.get('relationships', {}):
        for conn in config['relationships']['connections']:
            source = conn['source']
            target = conn['target']
            label = conn.get('label', '')
            
            # Validate that source exists (target can be a subgraph with @)
            if source in entities or source.startswith('@'):
                if target in entities or target.startswith('@'):
                    relationships.append(Relationship(
                        source=source,
                        target=target,
                        slot_name='',
                        label=label
                    ))
    
    return entities, relationships

def calculate_positions(entities: Dict[str, EntityInfo], config: dict) -> Dict[str, Tuple[int, int]]:
    """Calculate x, y positions for each entity."""
    positions = {}
    
    # Helper function to calculate entity height
    def get_entity_height(entity_name):
        if entity_name not in entities:
            return 100
        max_fields = config['field_display']['max_fields']
        fields = entities[entity_name].slots[:max_fields] if max_fields > 0 else entities[entity_name].slots
        return 25 + 10 + len(fields) * 15 + 10
    
    # Hardcoded left spine order
    left_spine_order = [
        'Action',
        '@People & Organizations Group',
        '@Place Group',
        'License',
        '@Dataset & Document Group',
        'DatasetComment'
    ]
    
    # Place left spine entities vertically
    mandatory_x = 50
    mandatory_y = 325
    entity_width = config['styling']['entity_width']
    
    for item in left_spine_order:
        if item.startswith('@'):
            # This is a subgraph - calculate its height and reserve space
            subgraph_name = item[1:]
            for subgraph in config['subgraphs']:
                if subgraph['name'] == subgraph_name:
                    # Update subgraph position to align with spine
                    subgraph['position']['x'] = mandatory_x
                    subgraph['position']['y'] = mandatory_y
                    # Reserve vertical space for the subgraph
                    mandatory_y += subgraph['position']['height'] + 50
                    break
        elif item in entities:
            positions[item] = (mandatory_x, mandatory_y)
            entity_height = get_entity_height(item)
            mandatory_y += entity_height + 50
    
    # Identify which entities are in subgraphs
    entities_in_subgraphs = set()
    for subgraph in config['subgraphs']:
        entities_in_subgraphs.update(subgraph['entities'])
    
    # Use entity_levels if defined for vertical hierarchy layout (for non-spine entities)
    left_spine_entities = set(left_spine_order)
    
    if 'entity_levels' in config:
        # Check if level_order is specified in config for custom ordering
        level_order = config.get('level_order', {})
        # Check if there's a center_align config for entities that should be x-aligned
        center_align_entities = set(config.get('center_align_entities', []))
        
        # Group entities by level, excluding spine and subgraph entities
        level_groups = {}
        for level, entity_list in config['entity_levels'].items():
            level_num = int(level)
            
            # Use custom order if specified for this level, otherwise use config order
            if str(level_num) in level_order:
                # Filter to only include entities that exist and aren't excluded
                ordered_list = [
                    e for e in level_order[str(level_num)]
                    if e in entities and e not in left_spine_entities and e not in entities_in_subgraphs
                ]
                # Add any entities from entity_list that weren't in the custom order
                for e in entity_list:
                    if e in entities and e not in left_spine_entities and e not in entities_in_subgraphs and e not in ordered_list:
                        ordered_list.append(e)
                level_groups[level_num] = ordered_list
            else:
                level_groups[level_num] = [
                    e for e in entity_list 
                    if e in entities and e not in left_spine_entities and e not in entities_in_subgraphs
                ]
        
        # Calculate center x position for aligned entities
        center_x = None
        if center_align_entities:
            # Use canvas center or a specific x coordinate
            center_x = config.get('center_align_x', config['styling']['canvas_width'] // 2)
        
        # Place entities level by level, to the right of mandatory column
        y_offset = 50
        left_margin = mandatory_x + entity_width + 150  # Start after mandatory column
        spacing_x = 50
        spacing_y = 150  # Vertical spacing between levels
        
        for level in sorted(level_groups.keys()):
            entities_in_level = level_groups[level]
            if not entities_in_level:
                continue
            
            # Calculate max height in this level
            max_height = max([get_entity_height(e) for e in entities_in_level])
            
            # Separate centered entities from normal entities
            centered_in_level = [e for e in entities_in_level if e in center_align_entities]
            normal_in_level = [e for e in entities_in_level if e not in center_align_entities]
            
            # Place centered entities first (at fixed x position)
            if centered_in_level and center_x:
                for entity_name in centered_in_level:
                    # Center the entity at the specified x coordinate
                    positions[entity_name] = (center_x - entity_width // 2, y_offset)
            
            # Place normal entities horizontally at this level in the specified order
            if normal_in_level:
                current_x = left_margin
                for entity_name in normal_in_level:
                    positions[entity_name] = (current_x, y_offset)
                    current_x += entity_width + spacing_x
            
            # Move to next level
            y_offset += max_height + spacing_y
    
    # Place entities in subgraphs (using positions from config)
    for subgraph in config['subgraphs']:
        sg_entities = [e for e in subgraph['entities'] if e in entities]
        x_start = subgraph['position']['x'] + 20
        y_start = subgraph['position']['y'] + 50
        entity_width = config['styling']['entity_width']
        
        # Calculate positions with dynamic spacing based on entity heights
        current_x = x_start
        current_y = y_start
        max_height_in_row = 0
        entities_per_row = 2  # Number of entities per row in subgraph
        
        for i, entity_name in enumerate(sg_entities):
            entity_height = get_entity_height(entity_name)
            
            # Check if we need to move to next row
            if i > 0 and i % entities_per_row == 0:
                current_x = x_start
                current_y += max_height_in_row + 20  # Add spacing between rows
                max_height_in_row = 0
            
            positions[entity_name] = (current_x, current_y)
            max_height_in_row = max(max_height_in_row, entity_height)
            
            current_x += entity_width + 20  # Add spacing between columns
    
    # Place any remaining entities not in levels or subgraphs
    remaining = [e for e in entities.keys() if e not in positions]
    if remaining:
        entity_width = config['styling']['entity_width']
        current_x = mandatory_x + entity_width + 150
        current_y = 50
        max_height_in_row = 0
        
        for i, entity_name in enumerate(remaining):
            if i > 0 and i % 6 == 0:
                current_x = mandatory_x + entity_width + 150
                current_y += max_height_in_row + 50
                max_height_in_row = 0
            
            entity_height = get_entity_height(entity_name)
            positions[entity_name] = (current_x, current_y)
            max_height_in_row = max(max_height_in_row, entity_height)
            current_x += entity_width + 50
    
    return positions

def generate_svg_entity(entity: EntityInfo, x: int, y: int, config: dict) -> str:
    """Generate SVG markup for an entity box."""
    width = config['styling']['entity_width']
    header_height = config['styling']['entity_header_height']
    field_height = config['styling']['field_height']
    
    # Calculate height based on number of fields
    max_fields = config['field_display']['max_fields']
    fields = entity.slots[:max_fields] if max_fields > 0 else entity.slots
    height = header_height + 10 + len(fields) * field_height + 10
    
    # Add group number to entity name if available
    entity_display_name = entity.name
    if entity.group_number is not None:
        entity_display_name = f"{entity.group_number}. {entity.name}"
    
    svg = f'''
    <g class="entity" transform="translate({x}, {y})">
        <rect width="{width}" height="{height}" fill="{entity.color}" 
              stroke="#333" stroke-width="2" rx="3"/>
        <text class="entity-header" x="10" y="20">{entity_display_name}</text>
        <line x1="0" y1="{header_height}" x2="{width}" y2="{header_height}" 
              stroke="#333" stroke-width="1"/>
    '''
    
    for i, field in enumerate(fields):
        y_pos = header_height + 15 + i * field_height
        # Use title if available, otherwise use the slot name
        field_display = entity.slot_titles.get(field, field)
        svg += f'    <text class="entity-field" x="10" y="{y_pos}">{field_display}</text>\n'
    
    svg += '    </g>\n'
    return svg

def generate_svg_relationship(rel: Relationship, positions: Dict[str, Tuple[int, int]], 
                              entities: Dict[str, EntityInfo], config: dict) -> str:
    """Generate SVG markup for a relationship line."""
    width = config['styling']['entity_width']
    
    # Helper to calculate entity height
    def get_entity_height(entity_name):
        if entity_name not in entities:
            return 100
        max_fields = config['field_display']['max_fields']
        fields = entities[entity_name].slots[:max_fields] if max_fields > 0 else entities[entity_name].slots
        return 25 + 10 + len(fields) * 15 + 10
    
    # Check if source or target is a subgraph (starts with @)
    is_subgraph_source = rel.source.startswith('@')
    is_subgraph_target = rel.target.startswith('@')
    
    # Get source center position
    if is_subgraph_source:
        subgraph_name = rel.source[1:]
        subgraph = None
        for sg in config['subgraphs']:
            if sg['name'] == subgraph_name:
                subgraph = sg
                break
        
        if not subgraph:
            return ''
        
        sg_pos = subgraph['position']
        src_center_x = sg_pos['x'] + sg_pos['width'] / 2
        src_center_y = sg_pos['y'] + sg_pos['height'] / 2
        src_box = {
            'left': sg_pos['x'],
            'right': sg_pos['x'] + sg_pos['width'],
            'top': sg_pos['y'],
            'bottom': sg_pos['y'] + sg_pos['height']
        }
    else:
        if rel.source not in positions:
            return ''
        
        src_x, src_y = positions[rel.source]
        src_height = get_entity_height(rel.source)
        src_center_x = src_x + width / 2
        src_center_y = src_y + src_height / 2
        src_box = {
            'left': src_x,
            'right': src_x + width,
            'top': src_y,
            'bottom': src_y + src_height
        }
    
    # Get target center position
    if is_subgraph_target:
        subgraph_name = rel.target[1:]
        subgraph = None
        for sg in config['subgraphs']:
            if sg['name'] == subgraph_name:
                subgraph = sg
                break
        
        if not subgraph:
            return ''
        
        sg_pos = subgraph['position']
        tgt_center_x = sg_pos['x'] + sg_pos['width'] / 2
        tgt_center_y = sg_pos['y'] + sg_pos['height'] / 2
        tgt_box = {
            'left': sg_pos['x'],
            'right': sg_pos['x'] + sg_pos['width'],
            'top': sg_pos['y'],
            'bottom': sg_pos['y'] + sg_pos['height']
        }
    else:
        if rel.target not in positions:
            return ''
        
        tgt_x, tgt_y = positions[rel.target]
        tgt_height = get_entity_height(rel.target)
        tgt_center_x = tgt_x + width / 2
        tgt_center_y = tgt_y + tgt_height / 2
        tgt_box = {
            'left': tgt_x,
            'right': tgt_x + width,
            'top': tgt_y,
            'bottom': tgt_y + tgt_height
        }
    
    # Calculate direction angle
    dx = tgt_center_x - src_center_x
    dy = tgt_center_y - src_center_y
    
    if dx == 0 and dy == 0:
        return ''
    
    angle = math.atan2(dy, dx)
    
    # Find exit point on source box
    def get_box_edge_point(center_x, center_y, box, angle):
        # Calculate intersection with box edges based on angle
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Check all four edges and find the one we exit through
        candidates = []
        
        # Right edge
        if cos_a > 0:
            t = (box['right'] - center_x) / cos_a
            y = center_y + t * sin_a
            if box['top'] <= y <= box['bottom']:
                candidates.append((box['right'], y, abs(t)))
        
        # Left edge
        if cos_a < 0:
            t = (box['left'] - center_x) / cos_a
            y = center_y + t * sin_a
            if box['top'] <= y <= box['bottom']:
                candidates.append((box['left'], y, abs(t)))
        
        # Bottom edge
        if sin_a > 0:
            t = (box['bottom'] - center_y) / sin_a
            x = center_x + t * cos_a
            if box['left'] <= x <= box['right']:
                candidates.append((x, box['bottom'], abs(t)))
        
        # Top edge
        if sin_a < 0:
            t = (box['top'] - center_y) / sin_a
            x = center_x + t * cos_a
            if box['left'] <= x <= box['right']:
                candidates.append((x, box['top'], abs(t)))
        
        # Return the closest intersection
        if candidates:
            return min(candidates, key=lambda c: c[2])[:2]
        return (center_x, center_y)
    
    # Get edge points
    start_x, start_y = get_box_edge_point(src_center_x, src_center_y, src_box, angle)
    end_x, end_y = get_box_edge_point(tgt_center_x, tgt_center_y, tgt_box, angle + math.pi)
    
    # Draw the line with arrowhead
    svg = f'''
    <line class="relationship-line" 
          x1="{start_x}" y1="{start_y}" 
          x2="{end_x}" y2="{end_y}"
          marker-end="url(#arrowhead)"/>
    '''
    
    # Add label if provided and not empty
    if rel.label and rel.label.strip():
        label_x = (start_x + end_x) / 2
        label_y = (start_y + end_y) / 2
        svg += f'<text class="relationship-label" x="{label_x}" y="{label_y}">{rel.label}</text>\n'
    
    return svg

def generate_svg_subgraph(subgraph: dict) -> str:
    """Generate SVG markup for a subgraph box."""
    pos = subgraph['position']
    svg = f'''
    <rect class="subgraph-box" 
          x="{pos['x']}" y="{pos['y']}" 
          width="{pos['width']}" height="{pos['height']}" rx="5"/>
    <text class="subgraph-label" x="{pos['x'] + 20}" y="{pos['y'] + 25}">{subgraph['name']}</text>
    '''
    return svg

def generate_html(entities: Dict[str, EntityInfo], relationships: List[Relationship], 
                 positions: Dict[str, Tuple[int, int]], config: dict) -> str:
    """Generate complete HTML document with SVG diagram."""
    
    svg_entities = []
    for entity_name, entity in entities.items():
        if entity_name in positions:
            x, y = positions[entity_name]
            svg_entities.append(generate_svg_entity(entity, x, y, config))
    
    svg_relationships = []
    for rel in relationships:
        svg_relationships.append(generate_svg_relationship(rel, positions, entities, config))
    
    svg_subgraphs = []
    for subgraph in config['subgraphs']:
        svg_subgraphs.append(generate_svg_subgraph(subgraph))
    
    width = config['styling']['canvas_width']
    height = config['styling']['canvas_height']
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MBO Metadata Structure Diagram</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
        }}
        
        .legend {{
            margin: 20px auto;
            max-width: 800px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .legend h3 {{
            margin-top: 0;
        }}
        
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }}
        
        .legend-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 1px solid #333;
            vertical-align: middle;
            margin-right: 5px;
        }}
        
        #diagram {{
            background: white;
            margin: 20px auto;
            display: block;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .entity {{
            cursor: pointer;
        }}
        
        .entity:hover {{
            opacity: 0.8;
        }}
        
        .entity-header {{
            font-weight: bold;
            font-size: 14px;
        }}
        
        .entity-field {{
            font-size: 11px;
            fill: #333;
        }}
        
        .relationship-line {{
            stroke: #666;
            stroke-width: 1.5;
            fill: none;
        }}
        
        .relationship-label {{
            font-size: 10px;
            fill: #666;
            text-anchor: middle;
        }}
        
        .subgraph-box {{
            fill: none;
            stroke: #999;
            stroke-width: 2;
            stroke-dasharray: 5,5;
        }}
        
        .subgraph-label {{
            font-size: 12px;
            font-weight: bold;
            fill: #666;
        }}
    </style>
</head>
<body>
    <h1>MBO Metadata Structure Diagram</h1>
    
    <div class="legend">
        <h3>Legend</h3>
        <div class="legend-item">
            <span class="legend-box" style="background: {config['colors']['mandatory']};"></span>
            <span>Mandatory Tables</span>
        </div>
        <div class="legend-item">
            <span class="legend-box" style="background: {config['colors']['conditional']};"></span>
            <span>Conditional Tables</span>
        </div>
        <div class="legend-item">
            <span class="legend-box" style="background: {config['colors']['optional']};"></span>
            <span>Optional Tables</span>
        </div>
    </div>
    
    <svg id="diagram" width="{width}" height="{height}">
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
            </marker>
        </defs>
        
        <!-- Subgraphs -->
        {''.join(svg_subgraphs)}
        
        <!-- Relationships -->
        {''.join(svg_relationships)}
        
        <!-- Entities -->
        {''.join(svg_entities)}
    </svg>
</body>
</html>'''
    
    return html

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_diagram.py <schema.yaml> <config.yaml> <output.html>")
        sys.exit(1)
    
    schema_path = Path(sys.argv[1])
    config_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    
    # Load configuration
    config = load_yaml(config_path)
    
    # Parse schema
    entities, relationships = parse_linkml_schema(schema_path, config)
    
    # Calculate positions
    positions = calculate_positions(entities, config)
    
    # Generate HTML
    html = generate_html(entities, relationships, positions, config)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"Diagram generated: {output_path}")
    print(f"  - {len(entities)} entities")
    print(f"  - {len(relationships)} relationships")

if __name__ == '__main__':
    main()