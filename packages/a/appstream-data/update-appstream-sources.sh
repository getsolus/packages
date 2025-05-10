#!/bin/bash
set -euo pipefail

YAML_FILE="package.yml"
CACHE_DIR="/var/lib/solbuild/sources"
DOWNLOAD_DIR="/tmp"

# List to store changes
changes=()

# Read all urls and hashes
mapfile -t entries < <(yq -o=json '.source[]' "$YAML_FILE" | jq -r 'to_entries[] | "\(.key) \(.value)"')

# Loop through the entries
for entry in "${entries[@]}"; do
    url="${entry%% *}"
    hash="${entry##* }"
    filename="$(basename "$url")"
    oldpath="$CACHE_DIR/$hash/$filename"
    newpath="$DOWNLOAD_DIR/$hash/$filename"

    mkdir -p "$(dirname "$newpath")"

    echo "==> Processing $filename"

    if [[ -f "$oldpath" ]]; then
        echo "Found existing cache file, using it for time check."
        curl -fsSL -z "$oldpath" -o "$newpath" "$url"
    else
        echo "No existing cache file, downloading fresh."
        mkdir -p $DOWNLOAD_DIR/$hash
        curl -fsSL -o "$newpath" "$url"
    fi

    if [[ ! -f "$newpath" ]]; then
        new_hash=$(sha256sum "$oldpath" | awk '{print $1}')
    else
        new_hash=$(sha256sum "$newpath" | awk '{print $1}')
    fi

    if [[ "$new_hash" != "$hash" ]]; then
        changes+=("  - $url : $new_hash")
    else
        # Collect the unchanged sources as well
        changes+=("  - $url : $hash")
    fi

    if [[ -f "$newpath" ]]; then
        rm -fr $DOWNLOAD_DIR/$hash
    fi
done

# Print out everything for copy pasta into yaml file
echo "All Sources:"
printf "%s\n" "${changes[@]}"

echo "✅ Finished"
