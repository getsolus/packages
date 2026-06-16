# Contribution 1: Add monitoring.yml to all packages that are still without it

**Contribution Number:** 1  
**Student:** Cabdifataax Maxamuud  
**Issue:** [getsolus/packages #4121](https://github.com/getsolus/packages/issues/4121)  
**Status:** Phase II – Implementation In Progress

---

## Why I Chose This Issue

This issue is a great entry point into open source contribution because it is well-scoped and beginner-friendly. Each sub-task (adding a `monitoring.yml` to a single package) is small and self-contained, which makes it easy to make incremental progress and get familiar with the project's structure and contribution workflow without needing deep knowledge of the codebase.

I also wanted to learn more about how Linux package management ecosystems handle security monitoring and release tracking. Working through this issue gives hands-on experience with tools like Anitya (release-monitoring.org), CPE naming conventions from the National Vulnerability Database, and the Solus packaging workflow — all of which are broadly useful skills for systems-level open source work.

---

## Understanding the Issue

### Problem Description

The Solus packages repository uses a `monitoring.yml` file in each package's directory to enable automated scanning for new upstream releases and security advisories (CVEs). A large number of packages were missing this file, meaning they were not being automatically monitored for updates or vulnerabilities. As of June 2026, approximately 16 packages remain without a `monitoring.yml` file.

### Expected Behavior

Every package directory should contain a `monitoring.yml` file alongside `package.yml`, `pspec*.xml`, and `MAINTAINERS.md`. The file should include a valid Anitya project ID for release tracking and either a CPE name for CVE tracking or a dated comment confirming that no CPE exists.

A typical `monitoring.yml` looks like this:

```yaml
releases:
  id: 8335
  rss: https://example.com/tags?format=atom
# No known CPE, checked 2025-06-23
security:
  cpe: ~
```

Or, when there is no RSS feed:

```yaml
releases:
  id: 372091
  rss: ~
# No known CPE, checked 2025-01-09
security:
  cpe: ~
```

### Current Behavior

Running the provided `find` command in the local packages repo returns a list of package directories that are missing a `monitoring.yml` file. Only ~16 packages remain unaddressed at this stage of the issue.

As of June 2026, the confirmed remaining packages (from [malfisya's gist](https://gist.github.com/malfisya/696f92c7555e043bfc0499c26aad8f58)) are:

| Package | Category |
| --- | --- |
| `hunspell-fr` | Spell checker dictionary (French) |
| `hunspell-it` | Spell checker dictionary (Italian) |
| `hunspell-pt-br` | Spell checker dictionary (Portuguese/BR) |
| `hunspell-ru` | Spell checker dictionary (Russian) |
| `hunspell-sl` | Spell checker dictionary (Slovenian) |
| `hyphen-de` | Hyphenation rules (German) |
| `hyphen-fr` | Hyphenation rules (French) |
| `iscan-data` | Epson scanner firmware data |
| `iscan` | Epson Image Scan! utility |
| `msodbcsql` | Microsoft ODBC Driver for SQL Server |
| `python-sip-4` | Legacy SIP C++/Python binding tool |
| `python-sphinx-rtd-theme` | Sphinx Read the Docs theme |
| `python-sphinx-lv2-theme` | Sphinx LV2 documentation theme |
| `python2-cairo` | Python 2 Cairo bindings (may be removed) |
| `python2-setuptools` | Python 2 setuptools (legacy) |
| `sqlheavy` | SQLite GObject wrapper (may be removed) |

> **Note:** `python2-cairo` and `sqlheavy` do not appear in the local fork's `packages/` tree, suggesting they may have already been removed or dropped upstream between the gist being written and now.

### Affected Components

- Individual package directories across the entire `getsolus/packages` repository
- The automated release monitoring and security advisory pipeline used by Solus maintainers

---

## Reproduction Process

### Environment Setup

- **OS:** Any Linux system (or WSL on Windows) with `git` and `bash` available
- **Required tools:** `go-task` (the Solus task runner — install via `go install github.com/go-task/task/v3/cmd/task@latest` or your distro's package manager)
- **Optional:** `yamllint` to validate generated YAML before committing

### Steps to Reproduce

Follow these steps exactly to confirm which packages are still missing `monitoring.yml`:

1. Fork the upstream repository on GitHub: go to [getsolus/packages](https://github.com/getsolus/packages) and click **Fork**.

2. Clone your fork locally:

   ```bash
   git clone https://github.com/<your-username>/packages.git
   cd packages
   ```

3. Run the following `find` command from the repo root to list every package directory that has no `monitoring.yml` file:

   ```bash
   find . -maxdepth 3 -mindepth 3 -name "package.yml" \
     | sed 's|/package\.yml||' \
     | while read d; do [ ! -f "$d/monitoring.yml" ] && echo "$d"; done \
     | sort
   ```

   > **What this does:** walks every `packages/<letter>/<name>/` directory, checks for the presence of `monitoring.yml`, and prints only those directories where the file is absent.

4. Compare the output against the [reference gist](https://gist.github.com/malfisya/696f92c7555e043bfc0499c26aad8f58). As of June 2026 you should see roughly 14 packages (the same list in the table above — `python2-cairo` and `sqlheavy` are no longer in the tree).

5. Navigate into one of the listed package directories and scaffold the template:

   ```bash
   cd packages/h/hunspell-fr
   go-task add-monitoring
   cat monitoring.yml        # inspect the generated skeleton
   ```

   You will see a YAML file with placeholder `id`, `rss`, and `cpe` fields that must be filled in before committing.

### Reproduction Evidence

- **Reproduction command output:** confirms ~14 actionable packages still missing the file (see table in Current Behavior above)
- **Full list of originally affected packages:** [malfisya's gist](https://gist.github.com/malfisya/696f92c7555e043bfc0499c26aad8f58)
- **Working branch in fork:** [Abdifatah2023/packages — add-monitoring-yml-batch1](https://github.com/Abdifatah2023/packages/tree/add-monitoring-yml-batch1)

---

## Solution Approach

### Analysis

The root cause is simply that `monitoring.yml` is a relatively new requirement and was not retroactively added to existing packages when it was introduced. There is no bug in any single package — this is a coverage gap that is being filled incrementally by contributors. The bulk of the work has already been done by the community; only ~16 packages remain.

### Proposed Solution

Pick a batch of 5–10 packages from the remaining list, and for each one:

1. Run `go-task add-monitoring` inside the package directory to scaffold the template
2. Look up the package on release-monitoring.org to find its Anitya ID
3. Add the correct `id` (and `rss` feed if one exists, otherwise `rss: ~`) under the `releases` section
4. Search for a CPE name using the `cpe-guesser` API or `cpesearch` helper
5. Fill in the `cpe` field, or add a `# No known CPE, checked YYYY-MM-DD` comment and set `cpe: ~`
6. Commit per package and open one PR at a time (5–10 packages per PR per maintainer guidance)

### Implementation Plan

My approach is to add `monitoring.yml` files in three small batches, one PR per batch, so each PR stays within the 5–10 package limit set by maintainers:

- **Batch 1 (PR #1):** the seven `hunspell-*` / `hyphen-*` dictionary packages — these share a similar upstream pattern (language-specific projects), so the Anitya lookups are predictable and CPEs are unlikely, making them a fast, low-risk first batch.
- **Batch 2 (PR #2):** four Python packages (`python-sip-4`, `python-sphinx-rtd-theme`, `python-sphinx-lv2-theme`, `python2-setuptools`) — well-known upstream projects that are almost certainly already tracked on Anitya.
- **Batch 3 (PR #3):** three proprietary/vendor packages (`iscan-data`, `iscan`, `msodbcsql`) — these require extra CPE research (Epson and Microsoft vendor namespaces) so they are handled last once the workflow is proven.

For each package: scaffold with `go-task add-monitoring` → look up the Anitya project ID → check NVD for a CPE → fill in the file → commit with message `<package>: Add monitoring.yml` → open PR referencing #4121.

---

Using UMPIRE framework (adapted):

**Understand:** Packages are missing `monitoring.yml` files that link them to upstream release tracking and CVE databases. Each file must be individually researched and filled out. Only ~16 remain.

**Match:** Existing `monitoring.yml` files in the repo (e.g., `hatari/monitoring.yml`, `passt/monitoring.yml`) serve as reference examples for correct formatting and field usage.

**Plan:**

1. ~~Run the `find` command to confirm the current list of remaining packages~~ ✓ Confirmed: 14 actionable packages remain (`python2-cairo` and `sqlheavy` are gone from the repo)
2. **First batch (PR #1):** `hunspell-fr`, `hunspell-it`, `hunspell-pt-br`, `hunspell-ru`, `hunspell-sl`, `hyphen-de`, `hyphen-fr` — all dictionary packages, likely no CPE, all need Anitya lookup
3. **Second batch (PR #2):** `python-sip-4`, `python-sphinx-rtd-theme`, `python-sphinx-lv2-theme`, `python2-setuptools` — Python packages, likely Anitya-tracked
4. **Third batch (PR #3):** `iscan-data`, `iscan`, `msodbcsql` — proprietary/vendor packages requiring extra CPE research
5. For each package: run `go-task add-monitoring`, look up the Anitya ID on release-monitoring.org, check for a CPE, fill in the file
6. Commit each package as its own commit for clean history
7. Open one PR referencing issue #4121; wait for review before opening the next

**Implement:** [Branch/commit links — to be added as work progresses]

**Review:** Verify each file matches the schema at the [Solus monitoring.yml docs](https://help.getsol.us/docs/packaging/monitoring.yml/), ensure no `null` values are left unfilled, confirm the Anitya ID resolves at `https://release-monitoring.org/project/<id>/`, and follow contribution guidelines.

**Evaluate:** After merging, confirm the packages no longer appear in the `find` command output.

---

## Testing Strategy

### Unit Tests

- [ ] Verify each `monitoring.yml` is valid YAML (no syntax errors)
- [ ] Confirm `id` field is an integer matching an actual Anitya project URL
- [ ] Confirm `cpe` field is either a valid vendor/product pair or explicitly set to `~` with a dated comment
- [ ] Confirm `rss` is either a valid feed URL or `~` (not left blank or `null`)

### Integration Tests

- [ ] Run the `find` command after changes and confirm affected packages no longer appear
- [ ] Verify the Anitya ID resolves correctly at `https://release-monitoring.org/project/<id>/`

### Manual Testing

Manually cross-check each package by visiting release-monitoring.org and the NVD CPE browser to confirm the IDs and CPE names are accurate before submitting the PR.

---

## Implementation Notes

### Week 1 Progress

Posted an introductory comment on issue #4121 explaining my background (CITE student at TCU / CodePath AI Open-Source program) and planned workflow. Received a reply from project member `davidjharder` with specific guidance on batch sizes and PR workflow. Currently selecting the first batch of packages from the remaining ~16 and preparing to open a first PR.

### Week 2 Progress — Repository Exploration

Cloned the upstream `getsolus/packages` repository locally and explored the structure to prepare for implementation.

**Reference `monitoring.yml` files confirmed in the repo:**

Three files currently exist and serve as ground-truth examples:

- `packages/h/hatari/monitoring.yml` — uses Anitya ID 8335, includes an RSS atom feed, no CPE (checked 2025-06-23)
- `packages/p/passt/monitoring.yml` — uses Anitya ID 372091, RSS set to `~` (no feed), no CPE (checked 2025-01-09)
- `packages/s/scd2html/monitoring.yml` — uses Anitya ID 316146, includes an RSS feed from sourcehut, no CPE (checked 2025-04-30)

These confirm the schema shown in the "Understanding the Issue" section above is accurate.

**Key observations on the 16 remaining packages:**

- The `hunspell-*` and `hyphen-*` packages are dictionary/hyphenation data files — their upstream sources are language-specific projects (e.g., grammalecte.net for French). Anitya IDs will need individual lookup; CPEs are unlikely.
- `iscan` sources from Epson's Linux scanner package hosting (`epson.net`). Proprietary distribution; CPE may exist under `epson` vendor.
- `msodbcsql` sources from `packages.microsoft.com` (Microsoft ODBC Driver v17). Anitya is unlikely to track this; CPE likely exists under `microsoft` vendor.
- `python-sip-4` sources from `riverbankcomputing.com` — very likely tracked on Anitya (well-known Python/C++ binding tool).
- `python2-cairo` and `sqlheavy` are **not present** in the local clone's package tree, suggesting they were dropped from the Solus repo before a monitoring file was ever needed. They can be skipped.

### Code Changes

- **Files to be modified:** `<package-name>/monitoring.yml` (new file) for each package in the batch
- **Key commits:** [To be added]
- **Approach decisions:** Following maintainer guidance — one PR at a time, 5–10 packages per PR, each package as its own commit. Starting with `python-sip-4` and the `hunspell-*` / `hyphen-*` dictionaries as the first batch, since their upstream sources are well-documented and Anitya lookups should be straightforward.

---

## Pull Request

**PR Link:** [To be added when submitted]

**PR Description:** Adds `monitoring.yml` to [N] packages that were missing it, enabling automatic release and CVE monitoring. Each file includes a verified Anitya ID and either a CPE name or a dated note confirming no CPE was found. Closes part of #4121.

**My Comment on the Issue (2026-06-11):**

> Hi! I am a CITE student at TCU and currently part of the CodePath AI Open-Source program. I'd like to contribute to this issue. I'm planning to add `monitoring.yml` files to a batch of packages from the list in the gist.
>
> I'll start with a small set to make sure I've got the workflow right (finding the correct Anitya ID on release-monitoring.org, checking for CPE names, and using `go-task add-monitoring`), then expand from there. I'll open a PR once I have a first batch ready for review.
>
> Let me know if there are any packages I should prioritize or avoid, or if there's a preferred batch size for PRs. Thanks!

**Maintainer Response — davidjharder (2026-06-11):**

> Hi Abdifatah, you are welcome to try a few batches. but there is not much left to do on this particular task.
> For easier review, please work on one PR at a time and limit PRs to 5-10 packages.
> We (the Solus project) have not hammered out AI guidelines yet, but all contributions must be fully understood by the PR author.

**Key takeaways from maintainer feedback:**

- Only ~16 packages remain — the task is nearly complete
- Submit one PR at a time, 5–10 packages per PR
- Every contribution must be personally understood by the author, regardless of tooling used

**Status:** Ready to implement first batch

---

## Learnings & Reflections

### Technical Skills Gained

- Understanding of how Linux distributions track upstream releases and security advisories
- Familiarity with Anitya / release-monitoring.org and the CPE naming standard
- Experience navigating a large monorepo and contributing at scale
- Understanding of the `monitoring.yml` schema used by Solus (releases ID, rss feed, security CPE)

### Challenges Overcome

- Learning the correct `monitoring.yml` format by reading existing files in the repo (e.g., `hatari/monitoring.yml`, `passt/monitoring.yml`) rather than relying solely on documentation
- Understanding that the file extension in the repo is `.yml` (not `.yaml` as referenced in the issue title)
- Scoping effort correctly given that only ~16 packages remain rather than the original ~3,000+

### What I'd Do Differently Next Time

[To be filled in after completion]

---

## Resources Used

- [Solus monitoring.yml documentation](https://help.getsol.us/docs/packaging/monitoring.yml/)
- [GitHub Issue #4121](https://github.com/getsolus/packages/issues/4121)
- [Gist: packages missing monitoring.yml](https://gist.github.com/malfisya/696f92c7555e043bfc0499c26aad8f58)
- [release-monitoring.org (Anitya)](https://release-monitoring.org/)
- [CPE Guesser API](https://cpe-guesser.cve-search.org/search)
- [National Vulnerability Database CPE Search](https://nvd.nist.gov/products/cpe/search)
