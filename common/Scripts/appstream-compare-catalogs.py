import xml.etree.ElementTree as ET
import gzip
import lzma
import sys
import os

VALID_TYPES = {"desktop", "desktop-application"}


def normalize_id(id_text):
    id_text = id_text.strip()
    if id_text.endswith(".desktop"):
        id_text = id_text[:-8]  # Remove ".desktop"
    return id_text


def extract_ids_from_file(filename):
    if filename.endswith('.gz'):
        open_func = gzip.open
    elif filename.endswith('.xz'):
        open_func = lzma.open
    else:
        raise ValueError(f"Unsupported file extension for: {filename}")

    with open_func(filename, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()

        ids = []
        for component in root.findall(".//component"):
            ctype = component.attrib.get("type", "")
            if ctype in VALID_TYPES:
                id_elem = component.find("id")
                if id_elem is not None and id_elem.text:
                    ids.append(normalize_id(id_elem.text))
        return ids


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {os.path.basename(sys.argv[0])} appstream-catalog-old.xml.[gz|xz] appstream-catalog-new.[gz|xz]")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    ids1 = set(extract_ids_from_file(file1))
    ids2 = set(extract_ids_from_file(file2))

    only_in_1 = ids1 - ids2
    only_in_2 = ids2 - ids1

    print(f"\nIDs in {file1} but not in {file2}:")
    for id_ in sorted(only_in_1):
        print(f"  {id_}")

    print(f"\nIDs in {file2} but not in {file1}:")
    for id_ in sorted(only_in_2):
        print(f"  {id_}")


if __name__ == "__main__":
    main()
