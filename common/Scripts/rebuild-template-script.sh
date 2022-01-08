#!/bin/bash

# A script to automate package rebuilds for solus.
# Can be adapted to suit the needs for different packages.

# A lot of improvements could be made here but it works well enough
# and ideally the tooling and infrastructure will be updated in the
# future to handle someof the shortcomings so scripts like these won't be neccessary.

# See Help() for usage.

# The package we are building against e.g. libicu/libboost. Should be in our custom local repo.
MAINPAK=""

# The packages to rebuild, in the order they need to be rebuilt.
# Use eopkg info and eopkg-deps to get the rev deps of the main package
# and take care to order them properly as we currently do not have
# a proper reverse dependency graph in eopkg.
# If the package list is particularly long you may wish to pass in a file instead.
# e.g. $(cat "packages.txt")
PACKAGES="foo bar xyz"

# Don't DOS the server
CONCURRENT_NETWORK_REQUESTS=8

# At what percentage of disk usage does delete-cache run automatically
DELETE_CACHE_THRESHOLD=80

# Track any troublesome packages here to deal with them manually.
MANUAL=""

# Colours
ERROR='\033[0;31m' # red
INFO='\033[1;34m' # blue
PROGRESS='\033[0;32m' # green
NC='\033[0m' # No Color

# Count the number of packages
package_count() {
    echo -e ${PACKAGES} | wc -w
}

# Setup a build repo and a custom local repo for the rebuilds
setup() {
    if [ -n "$MAINPAK" ]; then
        echo -e "${INFO} > Setting up build repo...${NC}"
        mkdir -p ~/rebuilds/${MAINPAK}
        pushd ~/rebuilds/${MAINPAK}
        git clone ssh://vcs@dev.getsol.us:2222/source/common.git --depth=1
        ln -sv common/Makefile.common .
        ln -sv common/Makefile.toplevel Makefile
        ln -sv common/Makefile.iso .
        echo -e "${INFO} > Setting up custom local repo...${NC}"
        sudo mkdir -p /var/lib/solbuild/local-${MAINPAK}
        sudo mkdir -p /etc/solbuild
        cp ~/rebuilds/${MAINPAK}/common/Scripts/local-unstable-MAINPAK-x86_64.profile /tmp/
        sed -i "s/MAINPAK/${MAINPAK}/g" "/tmp/local-unstable-MAINPAK-x86_64.profile"
        sudo mv -v /tmp/local-unstable-MAINPAK-x86_64.profile /etc/solbuild/local-unstable-${MAINPAK}-x86_64.profile
        echo -e "${PROGRESS} > Done! ${NC}"
        echo -e "${INFO} > Now remember to copy ${MAINPAK} .eopkg files to /var/lib/solbuild/local-${MAINPAK} before building.${NC}"
        set -e
        popd
    else
        echo -e "> ${ERROR} MAINPAK is empty, please edit the script and set it before continuing.${NC}"
    fi
}

# Concurrently clone repos
clone() {
    echo -e "${INFO} > Cloning packages...${NC}"
    pushd ~/rebuilds/${MAINPAK}
        make clone PKGS="${PACKAGES}" -j${CONCURRENT_NETWORK_REQUESTS}
    popd
}

# Run make bump on all packages
bump() {
    echo -e "${INFO} > Bumping the release number...${NC}"
    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
      do
        pushd ${i}
          echo -e "${INFO} > Running git pull first to see if we need to rebase...${NC}"
          git pull
          make bump
          # Backup for when pyyaml shits the bed with sources
          # perl -i -pe 's/(release    : )(\d+)$/$1.($2+1)/e' package.yml
        popd
      done
    popd
    echo -e "${PROGRESS} > Done! ${NC}"
}

# Build all packages and move resulting eopkgs to local repo. Stop on error.
# Check if the eopkg already exists before attempting to build and skip if it does.
build() {
    set -e
    # Do a naïve check that the package we are building against actually exists in the custom local repo before continuing.
    if ( ls /var/lib/solbuild/local-${MAINPAK} | grep -q ${MAINPAK}); then
        pushd ~/rebuilds/${MAINPAK}
        for i in ${PACKAGES}
        do
        pushd ${i}

            var=$((var+1))

            # See if we need to free up some disk space before continuing.
            $(checkDeleteCache)

            # Figure out the eopkg string.
            PKGNAME=$(grep ^name < package.yml | awk '{ print $3 }' | tr -d "'")
            RELEASE=$(grep ^release < package.yml | awk '{ print $3 }' | tr -d "'")
            VERSION=$(grep ^version < package.yml | awk '{ print $3 }' | tr -d "'")
            EOPKG="${PKGNAME}-${VERSION}-${RELEASE}-1-x86_64.eopkg"

            echo -e "${PROGRESS} > Building package" ${var} "out of" $(package_count) "${NC}"

            # Check if the eopkg already exists before building.
            if [[ ! $(ls /var/lib/solbuild/local-${MAINPAK}/${EOPKG}) ]]; then
                echo -e "${INFO} Package doesn't exist, building: ${i} ${NC}"
                sudo solbuild build package.yml -p local-unstable-${MAINPAK}-x86_64;
                sudo mv *.eopkg /var/lib/solbuild/local-${MAINPAK}/
            fi;
        popd
        done
        echo -e "${PROGRESS} > All packages built! ${NC}"
        popd
    else
        echo -e "${ERROR} > No package ${MAINPAK} was found in the repo. Remember to copy it to /var/lib/solbuild/local-${MAINPAK} before starting. ${NC}"
    fi
}

# Generate a "clean" abireport for most packages
# Until ypkg3 where yabi/abi-wizard gets run inside the chroot this will have to do
# Can fail with subpackages
# NOT TESTED
cleanabireport() {
    # Get the most recent eopkg history point
    eopkg_history_point = $(eopkg history | grep -m 1 "" | egrep -o '[[:digit:]]*')

    $(moveLocaltoRepo)

    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
    do
      pushd ${i}

        # Figure out eopkg string.
        PKGNAME=$(grep ^name < package.yml | awk '{ print $3 }' | tr -d "'")
        RELEASE=$(grep ^release < package.yml | awk '{ print $3 }' | tr -d "'")
        VERSION=$(grep ^version < package.yml | awk '{ print $3 }' | tr -d "'")
        EOPKG="${PKGNAME}-${VERSION}-${RELEASE}-1-x86_64.eopkg"

        sudo eopkg it $EOPKG -y

        make abireport
      popd
    done
    popd

    $(moveRepotoLocal)

    sudo eopkg history -t $eopkg_history_point -y

}

# Use tool of choice here to verify changes e.g. git diff, meld, etc.
verify() {
    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
    do
      pushd ${i}
        var=$((var+1))
        echo -e "Verifying package" ${var} "out of" $(package_count)
        git difftool --tool=gvimdiff3
      popd
    done
    popd
}

# Add and commit changes before publishing.
# TODO: add an excludes mechanism to allow a non-generic message for some packages.
commit() {
    set -e
    pushd ~/rebuilds/${MAINPAK}

    echo -e "${INFO} > Committing changes for each package to git...${NC}"

    for i in ${PACKAGES}
    do
      pushd ${i}
        echo -e "${INFO} > Committing package ${var} out of $(package_count) ${NC}"
        var=$((var+1))
        echo -e "${INFO} > Running git pull first to see if we need to rebase...${NC}"
        git pull
        make clean
        git add *
        git commit -m "Rebuild against ${MAINPAK}"
      popd
    done
    popd
    echo -e "${PROGRESS} > Done! ${NC}"
}

# Publish package to the build server and wait for it to be indexed into the repo
# before publishing the next package. Lower or increase sleep time depending on the size
# of packages being built.
publish() {
    set -e
    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
    do
      pushd ${i}
        var=$((var+1))

        echo -e "${PROGRESS} > Publishing package" ${var} "out of" $(package_count) "${NC}"
        make publish
        
        # Figure out eopkg string.
        PKGNAME=$(grep ^name < package.yml | awk '{ print $3 }' | tr -d "'")
        RELEASE=$(grep ^release < package.yml | awk '{ print $3 }' | tr -d "'")
        VERSION=$(grep ^version < package.yml | awk '{ print $3 }' | tr -d "'")
        EOPKG="${PKGNAME}-${VERSION}-${RELEASE}-1-x86_64.eopkg"

        # The buildname of the package listed on the buildserver queue.
        BUILDNAME="${PKGNAME}-${VERSION}-${RELEASE}"

        # Take care: your unstable repo can be called anything.
        # TODO: It could be quicker to check if the build has completed on the buildserver first
        #       then update the index and look for it
        # FIXME:If subpackaging is used and the "main" package doesn't exist this check will fail e.g. libreoffice.
        while [[ $(grep ${EOPKG} < /var/lib/eopkg/index/Unstable/eopkg-index.xml | wc -l) -lt 1 ]] ; do

          echo -e "${INFO} > Waiting for ${i} to build and be indexed... ${NC}"
          sleep 30

          echo -e "${INFO} > Checking that ${i} has not failed on the buildserver... ${NC}"
          # Add a sanity check in case the build has failed on the buildserver for whatever reason.
          if [[ -n $(curl https://build.getsol.us | grep -A 3 ${BUILDNAME} | grep build-failed) ]]; then
            echo -e "${ERROR} > ${i} failed on the build server, aborting. ${NC}"
            exit 1
          fi

          echo -e "${INFO} > Updating repo to see if ${i} has been indexed... ${NC}"
          sudo eopkg ur
        done
        echo -e "${PROGRESS} > ${i} has been indexed into the repo ${NC}"
      popd
    done
    popd
    echo -e "${PROGRESS} > Finished publishing packages! ${NC}"
}

NUKE() {
    read -p "This will nuke all of your work, if you are sure input NUKE my work to continue. " prompt
    if [[ $prompt = "NUKE my work" ]]; then
        echo -e "${INFO} >  Removing rebuilds repo for ${MAINPAK} ${NC}"
        rm -fr ~/rebuilds/${MAINPAK}
        echo -e "${INFO} > Removing custom local repo for ${MAINPAK} ${NC}"
        sudo rm -frv /var/lib/solbuild/local-${MAINPAK}
        echo -e "${INFO} > Remove custom local repo configuration file ${NC}"
        sudo rm -v /etc/solbuild/local-unstable-${MAINPAK}-x86_64.profile
        echo -e "${PROGRESS} > Nuked. ${NC}"
    else
        echo -e "${ERROR} Wrong input to continue, aborting. ${NC}"
    fi
}

# Move tracked packages in the local repo to the build repo
# If patterns are used to create a completely different subpackage name
# e.g. gpgme provides a python-gpg subpackage, it won't be moved.
# So check the local repo after it has finished.
moveLocaltoRepo() {
    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
    do
      pushd ${i}
        var=$((var+1))

        # Figure out the eopkg string.
        PKGNAME=$(grep ^name < package.yml | awk '{ print $3 }' | tr -d "'")
        RELEASE=$(grep ^release < package.yml | awk '{ print $3 }' | tr -d "'")
        VERSION=$(grep ^version < package.yml | awk '{ print $3 }' | tr -d "'")
        EOPKG="${PKGNAME}-${VERSION}-${RELEASE}-1-x86_64.eopkg"

        echo -e "Moving package" ${var} "out of" $(package_count) "to build repo"
        if [[ $(ls /var/lib/solbuild/local-${MAINPAK}/${EOPKG}) ]]; then
          echo -e ${i}
          sudo mv /var/lib/solbuild/local-${MAINPAK}/${PKGNAME}-*${VERSION}-${RELEASE}-1-x86_64.eopkg .
        fi;
      popd
    done
    popd
}

# Move packages from the build repo to the local repo
moveRepotoLocal() {
    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
    do
      pushd ${i}
        var=$((var+1))

        echo -e "Moving package" ${var} "out of" $(package_count) "to local repo"
        if [[ $(ls *.eopkg) ]]; then
          echo -e ${i}
          sudo mv *.eopkg /var/lib/solbuild/local-${MAINPAK}/
        fi;
      popd
    done
    popd
}

# make clean doesn't work with just a subset of the repo cloned.
# TODO: make clean PKGS=$PACKAGES probably works
cleanLocal(){
    pushd ~/rebuilds/${MAINPAK}
    for i in ${PACKAGES}
    do
      pushd ${i}
        var=$((var+1))
        echo -e "${INFO} > Cleaning package(s)" ${var} "out of" $(package_count) "${NC}"
        make clean
      popd
    done
    popd
    echo -e "${PROGRESS} > Finished cleaning packages(s)! ${NC}"
}

# If disk usage of the root parition is over a threshold then run
# solbuild dc -a to free up disk space.
checkDeleteCache() {
    DISKUSAGE=$(df -H / | awk '{ print $5 }' | cut -d'%' -f1 | sed 1d)
    if [ $DISKUSAGE -ge $DELETE_CACHE_THRESHOLD ]; then
        echo -e "${INFO} > Disk usage above ${DELETE_CACHE_THRESHOLD}%, running solbuild delete-cache --all...${NC}"
        sudo solbuild dc -a
    fi
}

# Display Help
Help() {
cat << EOF
   Rebuild template script for rebuilding packages on Solus.

   Please read and edit the script with the appriate parameters before starting.
   Generally only the MAINPAK and PACKAGES variables will need to be set where MAINPAK
   is the package you are rebuilding against and PACKAGES are the packages that need to
   be rebuilt against it. You'll also want to copy and rename it appropriately before using.
   To run unattended passwordless sudo needs to be enabled. Use at your own risk.

   Usage: ./rebuild-package.sh {setup,clone,bump,build,verify,commit,publish,NUKE}

   Explaination of commands:

   setup   : Creates a build repo for the rebuilds in as well as a custom local repo to place the resulting
           : eopkgs in. A custom local repo is used to isolate the standard local repo from the ongoing rebuilds.
           : The custom repo configuration can be found in /etc/solbuild/ after running setup.
           : If desired the custom repo can be edited to isolate it from the local repo in addition.
   clone   : Clones all the packages in PACKAGES to the build repo (make package.clone).
   bump    : Increments the release number in the package.yml file on all packages in the build repo (make bump)
   build   : Iteratively builds all packages in PACKAGES. If the package already exists in the local
           : repo it will skip to the next package. Passwordless sudo is recommended here so it can run unattended.
   verify  : Uses a git diff tool of choice to verify the rebuilds e.g. to verify abi_used_libs has changed in all packages.
   commit  : Git commit the changes with a generic commit message.
   publish : Iteratively runs makes publish to push the package to the build server,
           : waits for the package to be indexed into the repo before pushing the next.
           : You may wish to use autopush instead.

   NUKE    : This will nuke all of your work and cleanup any created files or directories.
           : This should only be done when all work has been indexed into the repo. Use with caution!"

   --------------------------------------------------------------------------------------------------------------------------

   Miscellaneous Options:

   moveLocaltoRepo : Move all the packages in the custom local repo (/var/lib/solbuild/local/MAINPAK/*.eopkg) back to their
                     build repos from where they originated. If patterns are used to create a completely different subpackage name
                     this may fail for those packages. This option can be useful for updating abi reports.
   moveRepotoLocal : Move all the packages from their build repo of origin to the custom local repo (/var/lib/solbuild/local/MAINPAK/).
   package_count   : Count the total number of packages that are marked to be rebuilt.
   checkDeleteCache: If disk usage of the root partition is above 80%, then solbuild delete-cache --all will be run to free up disk space.
                     This is checked periodically during build.

EOF
}

while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
   esac
done

# This little guy allows to call functions as arguments.
"$@"

echo -e "Rerun with -h to display help."
