# Custom local repo template profile for isolated rebuilds.
# This is to allow the standard local repo to be isolated from in-progress rebuilds
# which may take some time to complete.

image = "unstable-x86_64"

### REBUILDS ###
# rebuild-template-script.sh will take care of renaming MAINPAK.
################

# If you have a local repo providing packages that exist in the main
# repository already, you should remove the repo, and re-add it *after*
# your local repository:
remove_repos = ['Solus']
add_repos = ['MAINPAK','Local','Solus']

# Local repo for MAINPAK rebuilds
# A local repo with automatic indexing
[repo.MAINPAK]
uri = "/var/lib/solbuild/local-MAINPAK"
local = true
autoindex = true

### REBUILDS ###
# The local repo can be removed to isolate the rebuilds from the local repo if desired
################
# A local repo with automatic indexing
[repo.Local]
uri = "/var/lib/solbuild/local"
local = true
autoindex = true

# Re-add the Solus unstable repo
[repo.Solus]
uri = "https://mirrors.rit.edu/solus/packages/unstable/eopkg-index.xml.xz"
