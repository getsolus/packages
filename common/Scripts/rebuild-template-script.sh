#!/bin/bash

set -euo pipefail

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
PACKAGES="

"

# Track any troublesome packages here to deal with them manually.
MANUAL=""

# At what percentage of disk usage does delete-cache run automatically
DELETE_CACHE_THRESHOLD=80

# Colours
ERROR='\033[0;31m' # red
INFO='\033[1;34m' # blue
PROGRESS='\033[0;32m' # green
NC='\033[0m' # No Color

# Not to be ran as root
if [[ $EUID -eq 0 ]]
then
    printf "Please run as normal user.\n" >&2
    exit 1
fi

# Check requirements before starting
REQUIREMENTS="curl unxz notify-send paplay solbuild git go-task"
for i in $REQUIREMENTS; do
    if ! which $i &> /dev/null; then
        echo "Missing requirement: $i. Install it to continue."
        exit 1
    fi
done

# Count the number of packages
package_count() {
    echo -e ${PACKAGES} | wc -w
}

setup() {
    if [[ -z "$MAINPAK" ]]; then
        echo -e "> ${ERROR} MAINPAK is empty, please edit the script and set it before continuing.${NC}"
        exit 1
    fi

    echo -e "${INFO} > Switching to new git branch...${NC}"
    git switch -C ${MAINPAK}-rebuilds

    echo -e "${INFO} > Setting up custom local repo...${NC}"
    sudo mkdir -p /var/lib/solbuild/local-${MAINPAK}
    sudo mkdir -p /etc/solbuild
    cp $(git rev-parse --show-toplevel)/common/Scripts/local-unstable-MAINPAK-x86_64.profile /tmp/
    sed -i "s/MAINPAK/${MAINPAK}/g" "/tmp/local-unstable-MAINPAK-x86_64.profile"
    sudo mv -v /tmp/local-unstable-MAINPAK-x86_64.profile /etc/solbuild/local-unstable-${MAINPAK}-x86_64.profile
    echo -e "${PROGRESS} > Done! ${NC}"
    echo -e "${INFO} > Now remember to copy ${MAINPAK} .eopkg files to /var/lib/solbuild/local-${MAINPAK} before building.${NC}"
}

prechecks() {

    # FIXME: This seems shit, is there a better way?
    #if [[ $(test -d common) -ne 0 ]]; then
    #    echo -e "${ERROR} Unexpected directory structure found, are you in the right repo? ${NC}"
    #    exit 1
    #fi
    #if [[ $(test -d packages) -ne 0 ]]; then
    #    echo -e "${ERROR} Unexpected directory structure found, are you in the right repo? ${NC}"
    #    exit 1
    #fi
    #if [[ $(test -d .git) -ne 0 ]]; then
    #    echo -e "${ERROR} Unexpected directory structure found, are you in the right repo? ${NC}"
    #    exit 1
    #fi

    if [[ $(git branch --show-current) != "${MAINPAK}-rebuilds" ]]; then
        echo -e "${ERROR} Not on ${MAINPAK}-rebuilds branch. ${NC}"
        exit 1
    fi
}

bump() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    echo -e "${INFO} > Bumping the release number...${NC}"

    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}
        go-task bump
        # backup when pyyaml doesn't play ball
        # perl -i -pe 's/(release    : )(\d+)$/$1.($2+1)/e' package.yml
        popd
    done

    echo -e "${PROGRESS} > Done! ${NC}"
}

# Build all packages and move resulting eopkgs to local repo. Stop on error.
# Check if the eopkg already exists before attempting to build and skip if it does.
build() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    gsi=$(which gnome-session-inhibit 2>/dev/null)
    if [[ $XDG_CURRENT_DESKTOP = "GNOME" ]] && [[ ! -z ${gsi} ]]; then
      GNOME=1
    fi

    # Get sudo
    sudo -p "Enter sudo password: " printf "" || exit 1

    # Keep sudo alive without need for passwordless sudo
    while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

    # Do a naïve check that the package we are building against actually exists in the custom local repo before continuing.
    if [[ ! $(find /var/lib/solbuild/local-${MAINPAK} -type f -iname "*${MAINPAK}*") ]]; then
        echo -e "${ERROR} > No package ${MAINPAK} was found in the repo. Remember to copy it to /var/lib/solbuild/local-${MAINPAK} before starting. ${NC}"
        exit 1
    fi

    var=0
    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}

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
            if [[ $GNOME = "1" ]]; then
                gnome-session-inhibit --inhibit "logout:suspend:idle" --app-id solbuild --reason "Build in progress" \
                sudo solbuild build package.yml -p local-unstable-${MAINPAK}-x86_64
            else
                sudo solbuild build package.yml -p local-unstable-${MAINPAK}-x86_64
            fi
            sudo mv *.eopkg /var/lib/solbuild/local-${MAINPAK}/
        fi;
        popd
    done

    echo -e "${PROGRESS} > All packages built! ${NC}"
    notify-send "All rebuilds against ${MAINPAK} successfully built locally!" -t 0
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga
}

# Verify the change
verify() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    if [[ -z "${FILE}" ]]; then
        echo "FILE not set. e.g. FILE=package.yml or FILE=abi_used_libs"
    fi
    if [[ -z "${CHANGE}" ]]; then
        echo "CHANGE not set. e.g. CHANGE=libfoobar.so.8 or CHANGE=23.04.6"
    fi

    var=0

    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}

        var=$((var+1))
        echo -e "Verifying ${i}: ${var} out of" $(package_count)

        VERIFY=$(git diff -U0 --word-diff ${FILE} | grep ${CHANGE})
        if [[ $VERIFY = "" ]]; then
            echo "Package ${i} failed to rebuild against ${MAINPAK}"
            exit 1
        fi

        popd
    done
}

# All sorts of jank to install our built packages. Eopkg repos are all sorts of bork.
install() {
    sudo eopkg ar ${MAINPAK} /var/lib/solbuild/local-${MAINPAK}/eopkg-index.xml.xz
    sudo eopkg er ${MAINPAK}
    sudo eopkg dr Unstable unstable
    sudo eopkg up
    sudo eopkg er Unstable unstable
    sudo eopkg rr ${MAINPAK}
}

# Add and commit changes before publishing.
# TODO: add an excludes mechanism to allow a non-generic message for some packages.
commit() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    # Getopts for this function
    commit_usage() { echo "commit -e <pkg 1> -e <pkg 2> to use a custom commit message for these packages" 1>&2; exit; }

    local OPTIND o e
    while getopts ":e:" o; do
        case "${o}" in
            e) excludes+=("$OPTARG") ;;
            *) commit_usage ;;
        esac
    done
    shift $((OPTIND-1))

    echo -e "${INFO} > Committing changes for each package to git...${NC}"

    var=0
    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}
        echo -e "${PROGRESS} > Committing package" ${var} "out of" $(package_count) "${NC}"
        var=$((var+1))

        CUSTOM_COMMIT_MSG="0"

        for pkg in "${excludes[@]}"; do
            if [[ ${pkg} == ${i} ]]; then
                CUSTOM_COMMIT_MSG="1"
            fi
        done

        git add .

        if [ "${CUSTOM_COMMIT_MSG}" == "1" ]; then
            git commit
        else
            git commit -F- <<EOF
${i}: Rebuild against ${MAINPAK}



EOF
        fi
        popd
    done
    echo -e "${PROGRESS} > Done ${NC}"
    popd
}

# Publish package to the build server and wait for it to be indexed into the repo
# before publishing the next package.
publish() {
    #$(prechecks)

    pushd $(git rev-parse --show-toplevel)

    # Download initial index
    INDEX_XZ_URL="https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz"
    curl -s $INDEX_XZ_URL -o /tmp/rebuilds-unstable-index.xml.xz
    unxz /tmp/rebuilds-unstable-index.xml.xz -k -f

    var=0

    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}
        var=$((var+1))
        echo -e "${PROGRESS} > Publishing package" ${var} "out of" $(package_count) "${NC}"

        TAG=$($(git rev-parse --show-toplevel)/common/Scripts/gettag.py package.yml)

        # Update index if changed (-z)
        curl -s -z /tmp/rebuilds-unstable-index.xml.xz $INDEX_XZ_URL -o /tmp/rebuilds-unstable-index.xml.xz
        unxz /tmp/rebuilds-unstable-index.xml.xz -k -f

        # We may have had a build failure at some point which we had to sort manually and had to rerun publish
        # FIXME: Can fail if no eopkgs produced matches the tag (e.g. libreoffice)
        # FIXME: We may have had to bump the troublesome package, check for higher release than advertised.
        if [[ $(grep ${TAG} < /tmp/rebuilds-unstable-index.xml | wc -l) -eq 1 ]] ; then
            echo -e "${INFO} > ${TAG} already indexed in the repo, skipping. ${NC}"
        else
            go-task publish
            echo -e "${INFO} > Waiting for ${i} to build and be indexed... ${NC}"
            sleep 30
            DISABLE_BUILD_SUCCESS_NOTIFY=1 go-task notify-complete
        fi
        popd
    done

    echo -e "${PROGRESS} > All published packages successfully indexed into the repo! ${NC}"
    notify-send "All rebuilds against ${MAINPAK} successfully indexed into the repo!" -t 0
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga

    popd
}

NUKE() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    read -p "This will nuke all of your work, if you are sure input 'NUKE my work' to continue. " prompt
    if [[ $prompt = "NUKE my work" ]]; then
        echo -e "${INFO} > Removing rebuilds repo for ${MAINPAK} ${NC}"
        git switch main
        git branch -D ${MAINPAK}-rebuilds
        echo -e "${INFO} > Removing custom local repo for ${MAINPAK} ${NC}"
        sudo rm -frv /var/lib/solbuild/local-${MAINPAK}
        echo -e "${INFO} > Remove custom local repo configuration file ${NC}"
        sudo rm -v /etc/solbuild/local-unstable-${MAINPAK}-x86_64.profile
        echo -e "${PROGRESS} > Nuked. ${NC}"
    else
        echo -e "${ERROR} Wrong input to continue, aborting. ${NC}"
    fi

    popd
}

# If disk usage of the root parition is over a threshold then run
# solbuild dc -a to free up disk space.
checkDeleteCache() {
    DISKUSAGE=$(df -H / | awk '{ print $5 }' | cut -d'%' -f1 | sed 1d)
    if [ $DISKUSAGE -ge $DELETE_CACHE_THRESHOLD ]; then
        echo -e "${INFO} > Disk usage above ${DELETE_CACHE_THRESHOLD}%, running solbuild delete-cache --all ${NC}"
        sudo solbuild dc -a
    fi
}

# Update all kdeframeworks packages
kf_update() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    if [[ -z "${KF_VERSION}" ]]; then
        echo -e "${ERROR} Set KF_VERSION first e.g 1.108.0 ${NC}"
        exit 1
    fi

    a=( ${KF_VERSION//./ } )
    KF_VERSION_MAJOR="${a[0]}.${a[1]}"

    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}
        if yupdate ${KF_VERSION} https://cdn.download.kde.org/stable/frameworks/${KF_VERSION_MAJOR}/${i}-${KF_VERSION}.tar.xz; then
            echo "success"
        elif yupdate ${KF_VERSION} https://cdn.download.kde.org/stable/frameworks/${KF_VERSION_MAJOR}/portingAids/${i}-${KF_VERSION}.tar.xz; then
            echo "success"
        else
            echo "not found"
            exit 1
        fi
        popd
    done

    popd
}

# Update all plasma packages
plasma_update() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    if [[ -z "${PLASMA_VERSION}" ]]; then
        echo -e "${ERROR} Set PLASMA_VERSION first e.g 5.25.4 ${NC}"
        exit 1
    fi

    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}

        if [[ ${i} = "breeze-gtk-theme" ]]; then
            yupdate ${PLASMA_VERSION} https://cdn.download.kde.org/stable/plasma/${PLASMA_VERSION}/breeze-gtk-${PLASMA_VERSION}.tar.xz
        elif [[ ${i} = "polkit-kde-agent" ]]; then
            yupdate ${PLASMA_VERSION} https://cdn.download.kde.org/stable/plasma/${PLASMA_VERSION}/${i}-1-${PLASMA_VERSION}.tar.xz
        else
            yupdate ${PLASMA_VERSION} https://cdn.download.kde.org/stable/plasma/${PLASMA_VERSION}/${i}-${PLASMA_VERSION}.tar.xz
        fi
        if [[ $? -ne 0 ]]; then
            echo "not found"
            exit 1
        fi

        popd
    done

    popd
}

kdegear_update() {
    $(prechecks)

    pushd $(git rev-parse --show-toplevel)

    if [[ -z "${KDEGEAR_VERSION}" ]]; then
        echo -e "${ERROR} Set KDEGEAR_VERSION first e.g 23.04.2 ${NC}"
        exit 1
    fi

    for i in ${PACKAGES}; do
        pushd $(git rev-parse --show-toplevel)/packages/*/${i}

        if [[ ${i} = "kdeconnect" ]]; then
            yupdate ${KDEGEAR_VERSION} https://cdn.download.kde.org/stable/release-service/${KDEGEAR_VERSION}/src/kdeconnect-kde-${KDEGEAR_VERSION}.tar.xz
        else
            yupdate ${KDEGEAR_VERSION} https://cdn.download.kde.org/stable/release-service/${KDEGEAR_VERSION}/src/${i}-${KDEGEAR_VERSION}.tar.xz
        fi
        if [[ $? -ne 0 ]]; then
            echo "not found"
            exit 1
        fi

        popd
    done

    popd
}

# Display Help
help() {
cat << EOF
   Rebuild template script for rebuilding packages on Solus.

   Please read and edit the script with the appriate parameters before starting.
   Generally only the MAINPAK and PACKAGES variables will need to be set where MAINPAK
   is the package you are rebuilding against and PACKAGES are the packages that need to
   be rebuilt against it. You'll also want to copy and rename it appropriately before using.

   Usage: ./rebuild-package.sh {setup,bump,build,verify,commit,publish,NUKE}

   Explaination of commands:

   setup   : Creates a build repo for the rebuilds in as well as a custom local repo to place the resulting
           : eopkgs in. A custom local repo is used to isolate the standard local repo from the ongoing rebuilds.
           : The custom repo configuration can be found in /etc/solbuild/ after running setup.
           : If desired the custom repo can be edited to isolate it from the local repo in addition.
   bump    : Increments the release number in the package.yml file on all packages in the build repo (make bump)
   build   : Iteratively builds all packages in PACKAGES. If the package already exists in the local
           : repo it will skip to the next package.
   verify  : Can choose a common diff to verify all packages rebuilt properly e.g. FILE=abi_used_libs CHANGE=libfoobar.so.8
   commit  : Git commit the changes with a generic commit message.
   publish : Iteratively runs makes publish to push the package to the build server,
           : waits for the package to be indexed into the repo before pushing the next.
           : You may wish to use autopush instead.

   NUKE    : This will nuke all of your work and cleanup any created files or directories.
           : This should only be done when all work has been indexed into the repo. Use with caution!"

   --------------------------------------------------------------------------------------------------------------------------

   Miscellaneous Options:

   package_count   : Count the total number of packages that are marked to be rebuilt.
   checkDeleteCache: If disk usage of the root partition is above 80%, then solbuild delete-cache --all will be run to free up disk space.
                     This is checked periodically during build.

EOF
}

# This little guy allows to call functions as arguments.
"$@"

if [[ $# -eq 0 ]]; then
    help
fi
