#!/usr/bin/python3
import argparse
import os
import sys
import pathlib
from xml.etree import ElementTree

APPLICATIONS_DIRS = [
    pathlib.Path("/usr/share/applications"),
]

APPSTREAM_DATA_DIRS = [
    pathlib.Path("/usr/share/metainfo"),
    pathlib.Path("/usr/share/appdata"),
]

IGNORE_LIST_PATH = pathlib.Path.joinpath(
    pathlib.Path(__file__).parent, "appstream_ignored_packages.txt"
)


def main():
    parser = argparse.ArgumentParser(
        prog="check_appstream_progress",
        description="Scan either the whole Solus packages repo or a single pspec.xml "
        "to check for .desktop files and appstream metadata."
        "Place the names of packages to be ignored (such as internal pieces of desktop environments,"
        " for example) in a file called 'appstream_ignored_packages.txt' next to this script.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--package-names-only",
        action="store_true",
        dest="package_names_only",
        default=False,
        help="Output only the names of packages which need appstream metainfo added to them, suppressing info messages",
    )
    parser.add_argument(
        "--no-ignorelist",
        action="store_true",
        dest="no_ignorelist",
        default=False,
        help="Report all packages, even if they are present in appstream_ignored_packages.txt",
    )
    parser.add_argument(
        "packages_or_pspec_path",
        action="store",
        help="""Path to the Solus packages repo or pspec.xml file.\n
If a directory is provided, it will be scanned for pspec.xml files, and a report will be generated of the """
        """appstream data status of all discovered packages.\n
If a file is provided, it will be scanned as though it is a pspec.xml file, and the program will:
If the package would ship a .desktop file and no appstream metainfo, exit 1.
If the package would ship a .desktop file with correct metainfo, exit 0.
If the package would ship no .desktop file, exit 0.
Text explaining these results is also printed to stdout.""",
        type=pathlib.Path,
    )
    args = parser.parse_args()
    if args.packages_or_pspec_path.exists():
        if os.path.isdir(args.packages_or_pspec_path):
            if not args.package_names_only:
                print("Directory detected, scanning whole repository...")
            repo_info = check_whole_repo(pathlib.Path(sys.argv[1]))
            if not args.no_ignorelist:
                if os.path.isfile(IGNORE_LIST_PATH):
                    with open(IGNORE_LIST_PATH, "r") as ignore_file:
                        if not args.package_names_only:
                            print(f"Ignoring packages in {IGNORE_LIST_PATH}")
                        ignore_list = [
                            package
                            for package in ignore_file.read().splitlines()
                            if not package.startswith("#")
                        ]
                        repo_info["problematic_packages"] = [
                            package
                            for package in repo_info["problematic_packages"]
                            if package not in ignore_list
                        ]
                else:
                    if not args.package_names_only:
                        print(
                            f"WARNING: No ignore list file detected at {IGNORE_LIST_PATH}"
                        )
            if not args.package_names_only:
                print(
                    f'Count of packages shipping .desktop file: {len(repo_info["packages_with_desktop_file"])}'
                )
                print(
                    f'Count of packages shipping appstream metadata: {len(repo_info["packages_with_appstream_file"])}'
                )
                print(
                    f'Count of packages which need appstream metadata: {len(repo_info["problematic_packages"])}'
                )
                print("Problematic Packages:")
            for package in repo_info["problematic_packages"]:
                print(f"{package}")
        else:
            print("File detected, parsing single pspec.xml...")
            if args.package_names_only:
                print(
                    "Warning: option --package-names-only has no effect when scanning a single pspec.xml file."
                )
            result = check_single_pspec(args.packages_or_pspec_path)
            if not result:
                print("Package has a .desktop file and no appstream metainfo.")
                exit(1)
            else:
                print(
                    "If the package ships a .desktop file, it also ships appstream metadata. Good work!"
                )
                exit(0)
    else:
        print("Specified path does not exist.")
        exit(1)


def _has_desktop_file(pspec_root: ElementTree.Element) -> bool:
    """
    Checks for a .desktop file in one of the specified directories.

    param pspec_root: The root element of a tree representing a pspec.xml file.
    """
    has_desktop_file = False
    for package in pspec_root.findall("Package"):
        for path in package.find("Files").findall("Path"):
            if path.text.endswith(
                ".desktop"
            ):  # It's a .desktop file, but is it in the right place?
                desktop_path = pathlib.Path(path.text)
                if desktop_path.parent in APPLICATIONS_DIRS:
                    has_desktop_file = True
                    break  # We found a .desktop file, stop iterating
        if has_desktop_file:
            break  # We found a .desktop file, stop iterating
    return has_desktop_file


def _has_appstream_file(pspec_root: ElementTree.Element) -> bool:
    """
    Checks for an appstream metadata file in one of the specified directories.

    param pspec_root: The root element of a tree representing a pspec.xml file.
    """
    has_appstream_file = False
    for package in pspec_root.findall("Package"):
        for path in package.find("Files").findall("Path"):
            if path.text.endswith("metainfo.xml") or path.text.endswith("appdata.xml"):
                appstream_path = pathlib.Path(path.text)
                if appstream_path.parent in APPSTREAM_DATA_DIRS:
                    has_appstream_file = True
                    break  # We found appstream metainfo, stop iterating
        if has_appstream_file:
            break  # We found appstream metainfo, stop iterating
    return has_appstream_file


def _get_info_from_pspec(pspec_path: pathlib.Path) -> dict:
    """
    Parses a pspec.xml file and returns a dictionary containing information about it.
    Specifically, this function checks for appstream metadata files and .desktop files.

    param pspec_path: A path to a pspec.xml file.
    """
    out = {
        "has_desktop_file": False,
        "has_appstream_file": False,
    }
    pspec_file = open(pspec_path, "r")
    pspec_tree = ElementTree.parse(pspec_file)
    pspec_root = pspec_tree.getroot()
    out["has_desktop_file"] = _has_desktop_file(pspec_root)
    out["has_appstream_file"] = _has_appstream_file(pspec_root)
    return out


def check_single_pspec(pspec_path: pathlib.Path) -> bool:
    """
    Checks a pspec.xml file to make sure that if the package ships a GUI app, it also ships appstream metainfo.

    param pspec_path: Path to a pspec.xml file
    """
    correct = None
    pspec_info = _get_info_from_pspec(pspec_path)
    if pspec_info["has_desktop_file"]:
        correct = False  # Yer on thin ice, buddy
    if pspec_info["has_appstream_file"]:
        correct = True
    return correct


def check_whole_repo(packages_path: pathlib.Path) -> dict:
    """
    Checks the entire Solus packages repository worth of pspec.xml files for .desktop files and appstream metadata.
    Returns a dictionary containing appstream status information for the whole repository.
    """
    out = {
        "packages_with_desktop_file": [],
        "packages_with_appstream_file": [],
        "problematic_packages": [],
    }
    for directory in os.walk(packages_path):
        leaf_files = directory[-1]
        for file in leaf_files:
            if file.startswith("pspec"):
                current_path = pathlib.Path(directory[0])
                package_name = current_path.name
                pspec_info = _get_info_from_pspec(
                    pathlib.Path.joinpath(current_path, file)
                )
                if pspec_info["has_desktop_file"]:
                    out["packages_with_desktop_file"].append(package_name)
                if pspec_info["has_appstream_file"]:
                    out["packages_with_appstream_file"].append(package_name)
                if (
                    pspec_info["has_desktop_file"]
                    and not pspec_info["has_appstream_file"]
                ):
                    out["problematic_packages"].append(package_name)
    return out


if __name__ == "__main__":
    main()
