#!/usr/bin/env bash

if [ ! -f "package.yml" ]; then
    echo "Cannot find package.yml, run from the root of the package directory."
    exit 1
fi

cleanup() {
  echo "Cleaning up before exiting..."
  rm -fr ./*.eopkg metadata.xml files.xml install/
}

trap cleanup EXIT

name=$(yq .name package.yml)

eopkg fetch "${name}"

uneopkg ./*.eopkg

FILES=$(find install/usr/share/fonts -type f)

fonts=()

for i in ${FILES}; do
    fullname=$(fc-query --format='%{fullname[0]}' "${i}")
    if [[ -n $fullname ]]; then
        mapfile -t temp <<< "$fullname"
        fonts+=("${temp[@]}")
    else
        family_style=$(fc-query --format='%{family[0]} %{style[0]}\n' "${i}")
        if [[ -n $family_style ]]; then
            mapfile -t temp <<< "$family_style"
            fonts+=("${temp[@]}")
        else
            echo "Error: Failed to get font info for '${i}'" >&2
        fi
    fi
done

echo "  <provides>"
for i in "${fonts[@]}"; do
    echo "    <font>${i}</font>"
done
echo "  </provides>"


