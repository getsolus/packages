#!/usr/bin/env python3

import os
import pathlib
import hashlib
import datetime
import requests
import ruamel.yaml
import shutil
from urllib.parse import urlparse

# Define constants
YAML_FILE = "package.yml"
CACHE_DIR = "/var/lib/solbuild/sources"
DOWNLOAD_DIR = "/tmp"


def calculate_sha256(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read and update hash string in chunks
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found for hashing: {filepath}")
        return None
    except Exception as e:
        print(f"Error calculating hash for {filepath}: {e}")
        return None


def get_file_modification_time(filepath):
    """Gets the modification time of a file in the required format for If-Modified-Since."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.datetime.utcfromtimestamp(mtime).strftime('%a, %d %b %Y %H:%M:%S GMT')
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting modification time for {filepath}: {e}")
        return None


def main():
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=4, sequence=4, offset=4)
    yaml.top_level_colon_align = True

    yaml_data = None
    try:
        with open(YAML_FILE, 'r') as f:
            yaml_data = yaml.load(f)
    except FileNotFoundError:
        print(f"Error: {YAML_FILE} not found.")
        return
    except Exception as e:
        print(f"Error reading {YAML_FILE}: {e}")
        return

    # Validate data
    if not yaml_data or 'source' not in yaml_data or not isinstance(yaml_data.get('source'), list):
        print(f"Error: Invalid or missing 'source' section in {YAML_FILE}. Expected a list under 'source'.")
        return

    updated_sources_list = []
    hashes_changed = False

    for entry in yaml_data['source']:
        print(entry)
        if not isinstance(entry, dict) or len(entry) != 1:
            print(f"Warning: Skipping unexpected entry format in source: {entry}. Expected a single key-value pair (url: hash).")
            try:
                if isinstance(entry, dict) and len(entry) == 1:
                    updated_sources_list.append(entry)
            except Exception:
                pass

            continue

        url = list(entry.keys())[0]
        expected_hash = list(entry.values())[0]
        filename = pathlib.Path(urlparse(url).path).name
        hash_based_subdir = expected_hash

        old_path = pathlib.Path(CACHE_DIR) / hash_based_subdir / filename
        new_dir = pathlib.Path(DOWNLOAD_DIR) / hash_based_subdir
        new_path = new_dir / filename

        print(f"==> Processing {filename}")

        download_successful = False
        downloaded_file_path = None

        try:
            # Ensure the temporary download directory exists
            new_dir.mkdir(parents=True, exist_ok=True)

            # Check for existing cache file and attempt conditional download
            if old_path.exists():
                print("Found existing cache file, using it for time check.")
                mod_time = get_file_modification_time(old_path)
                headers = {'If-Modified-Since': mod_time} if mod_time else {}
                response = requests.get(url, headers=headers, stream=True, timeout=30)

                if response.status_code == 304:
                    print("File not modified, using cached version.")
                    download_successful = True
                    downloaded_file_path = old_path  # Hash the old file
                elif response.status_code == 200:
                    print("File modified or cache invalid, downloading fresh.")
                    with open(new_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    download_successful = True
                    downloaded_file_path = new_path  # Hash the newly downloaded file
                else:
                    print(f"Warning: Conditional download failed for {url} with status code {response.status_code}. Attempting fallback.")
                    # Attempt to use the old path if it exists, mirroring shell script fallback
                    if old_path.exists():
                        print("Falling back to using old cache file for hashing.")
                        download_successful = True
                        downloaded_file_path = old_path
                    else:
                        print("Neither new nor old path available after failed conditional download.")
                        download_successful = False

            # If no existing cache file, perform a fresh download
            else:
                print("No existing cache file, downloading fresh.")
                response = requests.get(url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(new_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    download_successful = True
                    downloaded_file_path = new_path  # Hash the newly downloaded file
                else:
                    print(f"Warning: Fresh download failed for {url} with status code {response.status_code}. Attempting fallback.")
                    if old_path.exists():
                        print("Falling back to using old cache file for hashing.")
                        download_successful = True
                        downloaded_file_path = old_path
                    else:
                        print("Neither new nor old path available after failed fresh download.")
                        download_successful = False

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}. Attempting fallback.")
            # Attempt to use the old path if it exists on request error
            if old_path.exists():
                print("Falling back to using old cache file for hashing.")
                download_successful = True
                downloaded_file_path = old_path
            else:
                print("Neither new nor old path available after download error.")
                download_successful = False

        except Exception as e:
            print(f"An unexpected error occurred during processing {url}: {e}")
            download_successful = False

        calculated_hash = None
        # Only calculate hash if download was successful and a file path is available
        if download_successful and downloaded_file_path and downloaded_file_path.exists():
             calculated_hash = calculate_sha256(downloaded_file_path)

        # Determine the final hash to use for this entry in the YAML
        final_hash_for_output = expected_hash # Default to the original hash from YAML

        if calculated_hash:
            if calculated_hash != expected_hash:
                print(f"Hash mismatch for {filename}: Expected {expected_hash}, Got {calculated_hash}. Updating hash.")
                final_hash_for_output = calculated_hash
                hashes_changed = True # Set flag because a hash has changed
            else:
                 print(f"Hash matches expected for {filename}.")
                 # Hash matches, retain the original hash from YAML which preserves comments/formatting if ruamel handled it
                 # Or explicitly use calculated_hash if you want a 'clean' update regardless of ruamel quirks with comments on values.
                 # Let's explicitly use the calculated hash for consistency if calculation was successful.
                 final_hash_for_output = calculated_hash
        else:
            # If hash calculation failed (e.g., download failed), retain the old hash.
            print(f"Could not obtain a new hash for {url}. Retaining old hash: {expected_hash}")
            final_hash_for_output = expected_hash

        # Append the updated source entry as a dictionary to the list
        updated_sources_list.append({url: final_hash_for_output})

        # Clean up temporary download directory matching shell script behavior
        if new_dir.exists():
            try:
                shutil.rmtree(new_dir)
            except Exception as e:
                print(f"Error cleaning up temporary directory {new_dir}: {e}")

    print("\n" + "="*20)
    if not hashes_changed:
        print("No changed hashes for sources found")
    else:
        print(f"Attempting to update {YAML_FILE}...")

        # --- In-place update of the YAML file ---
        try:
            # Check if any hashes were changed before updating version and release
            if hashes_changed:
                print("Hashes have changed. Updating version and incrementing release.")
                # Update the 'version' key with the current date
                yaml_data['version'] = datetime.datetime.now().strftime("%Y%m%d")

                # Increment the 'release' key if it exists and is an integer
                if 'release' in yaml_data and isinstance(yaml_data['release'], int):
                    yaml_data['release'] += 1
                else:
                    print(f"Warning: Cannot increment 'release' key. It is missing or not an integer.")

            with open(YAML_FILE, 'w') as f:
                # Update the 'source' section in the loaded data structure
                if 'source' in yaml_data and isinstance(yaml_data['source'], list):
                    yaml_data['source'] = updated_sources_list
                else:
                    print(f"Error: 'source' section not found or not a list in {YAML_FILE} during update phase.")
                    return

                # Dump the modified data structure back into the YAML file
                yaml.dump(yaml_data, f)

            print(f"{YAML_FILE} updated successfully.")

        except FileNotFoundError:
            print(f"Error: {YAML_FILE} not found during the update attempt.")
        except Exception as e:
            print(f"Error writing updated data to {YAML_FILE}: {e}")

        # --- End of In-place update ---

    print("\n" + "="*20)

    print("✅ Finished")


if __name__ == "__main__":
    main()
