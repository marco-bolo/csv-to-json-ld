#!/usr/bin/env python3
"""
Generate sitemap.xml for csv-to-json-ld repository
Only includes .html and .json files from the out/ directory
"""

import os
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration
BASE_URL = "https://lab.marcobolo-project.eu/csv-to-json-ld"
OUTPUT_DIR = "remote/models/site"  # MkDocs output directory
SITEMAP_FILE = "remote/models/site/sitemap.xml"
INCLUDED_EXTENSIONS = [".html", ".json"]

def get_file_modified_time(filepath):
    """Get the last modified time of a file in W3C format"""
    timestamp = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d")

def should_include_file(filepath):
    """Check if file should be included in sitemap"""
    return any(filepath.suffix == ext for ext in INCLUDED_EXTENSIONS)

def generate_sitemap():
    """Generate sitemap.xml from files in OUTPUT_DIR"""
    
    # Create root element
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Get all files recursively from OUTPUT_DIR
    output_path = Path(OUTPUT_DIR)
    
    if not output_path.exists():
        print(f"Error: {OUTPUT_DIR} directory does not exist")
        return
    
    files_added = 0
    
    # Walk through all files in output directory
    for filepath in sorted(output_path.rglob("*")):
        if filepath.is_file() and should_include_file(filepath):
            # Get relative path from output directory
            rel_path = filepath.relative_to(output_path)
            
            # Create URL (convert Windows paths to forward slashes)
            url_path = str(rel_path).replace("\\", "/")
            full_url = f"{BASE_URL}/{url_path}"
            
            # Create URL entry
            url_elem = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_elem, "loc")
            loc.text = full_url
            
            # Add last modified date
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = get_file_modified_time(filepath)
            
            files_added += 1
    
    # Pretty print XML
    xml_str = ET.tostring(urlset, encoding="unicode")
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Remove extra blank lines
    pretty_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])
    
    # Write to file
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    print(f"✓ Generated {SITEMAP_FILE} with {files_added} URLs")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Source directory: {OUTPUT_DIR}")
    print(f"  Included extensions: {', '.join(INCLUDED_EXTENSIONS)}")

if __name__ == "__main__":
    generate_sitemap()
