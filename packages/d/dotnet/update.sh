#!/bin/bash
version=$1

if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be in the format x.y.z"
  exit 1
fi

go-task update -- $version https://github.com/dotnet/dotnet/archive/refs/tags/v$version.tar.gz --cache

curl -Ls https://github.com/dotnet/dotnet/releases/download/v$version/release.json > files/release.json || {
  echo "Failed to download release file from https://github.com/dotnet/dotnet/releases/download/v$version/release.json"
  exit 1
}
go-task build
