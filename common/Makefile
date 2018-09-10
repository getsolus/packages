SHELL = /bin/bash

.PHONY: help


help:
	@echo "update  - Update current project list"


update:
	@curl https://build.getsol.us/projects.list | grep -E "^packages/" | cut -d '/' -f 2 | sed -e 's/\.git$$//g' | sort > packages
