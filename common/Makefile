SHELL = /bin/bash

.PHONY: help

help:
	@echo "stateless      - Update the stateless report"
	@echo "update         - Update current project list"

update:
	go run Go/update_packages.go > packages

stateless:
	@Scripts/update_stateless.sh
