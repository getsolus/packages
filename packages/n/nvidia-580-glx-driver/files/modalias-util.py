#!/usr/bin/env python
"""
Script to write modaliases into an AppStream metainfo XML file.
Usage: echo $MODALIASES | python3 as-metainfo-write-modaliases path/to/appstream.metainfo.xml
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_modaliases(input_text):
    """Parse modaliases from input text, splitting by space or newline."""
    # Split by both spaces and newlines, filter out empty strings
    modaliases = []
    for line in input_text.strip().split('\n'):
        for alias in line.split():
            alias = alias.strip()
            if alias:
                modaliases.append(alias)
    return modaliases


def update_metainfo(xml_path, modaliases):
    """Update the metainfo XML file with the provided modaliases."""
    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find or create the <provides> element
    provides = root.find('provides')
    if provides is None:
        provides = ET.SubElement(root, 'provides')

    # Remove existing modalias elements
    for modalias in provides.findall('modalias'):
        provides.remove(modalias)

    # Add new modalias elements
    for alias in modaliases:
        modalias_elem = ET.SubElement(provides, 'modalias')
        modalias_elem.text = alias

    # Write back to file with proper formatting
    ET.indent(tree, space='  ')
    tree.write(xml_path, encoding='UTF-8', xml_declaration=True)


def main():
    # Check if the file path is provided
    if len(sys.argv) != 2:
        print("Usage: echo $MODALIASES | python3 as-metainfo-write-modaliases path/to/appstream.metainfo.xml", file=sys.stderr)
        sys.exit(1)

    xml_path = Path(sys.argv[1])

    # Check if file exists
    if not xml_path.exists():
        print(f"Error: File '{xml_path}' not found", file=sys.stderr)
        sys.exit(1)

    # Read modaliases from stdin
    input_text = sys.stdin.read()

    if not input_text.strip():
        print("Error: No input provided via stdin", file=sys.stderr)
        sys.exit(1)

    # Parse modaliases
    modaliases = parse_modaliases(input_text)

    if not modaliases:
        print("Error: No valid modaliases found in input", file=sys.stderr)
        sys.exit(1)

    # Update the XML file
    try:
        update_metainfo(xml_path, modaliases)
        print(f"Successfully updated {xml_path} with {len(modaliases)} modalias(es)")
    except ET.ParseError as e:
        print(f"Error: Invalid XML file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

