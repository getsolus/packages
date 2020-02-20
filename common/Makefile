SHELL = /bin/bash

.PHONY: help

help:
	@echo "stateless      - Update the stateless report"
	@echo "sync-licenses  - Update the SPDX license list"
	@echo "update         - Update current project list"

sync-licenses:
	@Scripts/sync_licenses.sh

update:
	go run Go/update_packages.go > packages

stateless:
	@Scripts/update_stateless.sh
