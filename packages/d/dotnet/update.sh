#!/bin/bash
version=$1
sdk_version=$2

if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Provide both package and sdk version, e.g. 9.0.10 9.0.111"
  exit 1
fi
if [[ ! $sdk_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Provide both package and sdk version, e.g. 9.0.10 9.0.111"
  exit 1
fi

go-task update -- $version https://github.com/dotnet/dotnet/archive/refs/tags/v$sdk_version.tar.gz --cache

curl -Lsf https://github.com/dotnet/dotnet/releases/download/v$sdk_version/release.json > files/release.json || {
  echo "Failed to download release file from https://github.com/dotnet/dotnet/releases/download/v$sdk_version/release.json"
  exit 1
}
go-task build

echo "Release notes can be found at https://github.com/dotnet/core/blob/main/release-notes"