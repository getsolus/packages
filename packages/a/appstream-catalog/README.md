# AppStream Data Package
## Purpose
This package contains Solus' AppStream metadata, which powers software lists in GNOME Software and Discover. This package should track the latest tag on github.com/getsolus/solus-appstream-data, ensuring that the data used by software centers reflects the actual state of the repository.

The package folder also contains a specialized Taskfile.yml which augments the main one to add appstream-specific update automation.

## Update Procedure
1. Ensure that your clone of the packages repository is up to date, and that you're on the `main` branch.
2. Go to this package: `gotopkg appstream-catalog`.
3. Run `go-task infra:generate-appstream` . You must have `infrastructure-tooling`, ssh access to teaparty and be part of the ferryd group on teaparty for this to succeed.
   - NOTE: As the generated tarballs are behind a CDN it may take a few minutes to propagate.
4. Run `update-appstream-sources.py`
5. Run `git diff`, if the shasums of the sources are different run `go-task build`.
6. Install the resulting `.eopkg` and make sure GNOME Software or Discover recognize packages (ideally, search for something which you know was added in the most recent sync).
7. Commit and push to a branch on github using this package's Taskfile: `go-task appstream-commit-and-push`. You can also do this manually if you're more comfortable that way.
8. Create a pull request from your new branch on github. If you used the Taskfile or manually created a branch called `appstream-catalog-update`, you can click this helpful link: https://github.com/getsolus/packages/pull/new/appstream-catalog-update.
8. Follow standard PR approval procedure and get updated appstream-catalog into the repository before the weekly sync.
