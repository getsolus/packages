TOPLVL = $(abspath ".")

SHELL = /bin/bash

.PHONY: help

PKGS = $(shell cat ${TOPLVL}/common/packages)
pull_PKGS = $(addsuffix .pull,$(PKGS))
clone_PKGS = $(addsuffix .clone,$(PKGS))
clean_PKGS = $(addsuffix .clean,$(PKGS))
up_PKGS = $(addsuffix .upcheck,$(PKGS))

help:
	@echo "clone     - Clone all repos"
	@echo "cvecheck  - Check all packages for CVEs"
	@echo "pull      - Pull all repos"

clone: $(clone_PKGS)

clean: $(clean_PKGS)

pull: $(pull_PKGS)

upcheck: $(up_PKGS)

%.upcheck:
	@[ ! -d "$(subst .upcheck,,$@)" ] || ( \
		git_repo=$(subst .upcheck,,$@); \
		ypkg-update-checker q "./$$git_repo/package.yml" || exit 0; \
	)

%.pull:
	@[ ! -d "$(subst .pull,,$@)" ] || ( \
		echo "Pulling $(subst .pull,,$@)..."; \
		git_repo=$(subst .pull,,$@); \
		git -C "$(subst .pull,,$@)" remote set-url origin "https://dev.getsol.us/source/$${git_repo}.git" || exit 0; \
		git -C "$(subst .pull,,$@)" remote set-url --push origin "ssh://vcs@dev.getsol.us:2222/source/$${git_repo}.git" || exit 0; \
		git -C "$(subst .pull,,$@)" pull || exit 0; \
	)

%.clone:
	@[ -d "$(subst .clone,,$@)" ] || ( \
		git_repo=$(subst .clone,,$@); \
		git clone "https://dev.getsol.us/source/$${git_repo}.git" || exit 0; \
		cd $${git_repo}; \
		git remote set-url origin "https://dev.getsol.us/source/$${git_repo}.git"; \
		git remote set-url --push origin "ssh://vcs@dev.getsol.us:2222/source/$${git_repo}.git"; \
	)

%.clean:
	@[ -d "$(subst .clean,,$@)" ] || ( \
		git_repo=$(subst .clone,,$@); \
		cd $${git_repo}; \
		make clean; \
	)

cvecheck:
	cve-check-tool -n $(TOPLVL)/common/packages -M $(TOPLVL)/common/mapping -o report.html; \
