#!/usr/bin/bash
set -euo pipefail

# Temp: Exit if I_UNDERSTAND_THAT_THIS_SCRIPT_CAN_BREAK_MY_SYSTEM is not set
# This will be removed once we are ready to enable this by default
if [ -z "${I_UNDERSTAND_THAT_THIS_SCRIPT_CAN_BREAK_MY_SYSTEM+set}" ]; then
    exit 0
fi

# This is where orphaned files will be moved to
ORPHAN_DIR="${ORPHAN_DIR:=/var/usr-merge-orphaned-files}"

# Manually specify the path of binaries needed since we're messing with /bin and /sbin
CP="${CP:=/usr/bin/cp}"
DIRNAME="${DIRNAME:=/usr/bin/dirname}"
FIND="${FIND:=/usr/bin/find}"
MKDIR="${MKDIR:=/usr/bin/mkdir}"
READLINK="${READLINK:=/usr/bin/readlink}"
RM="${RM:=/usr/bin/rm}"
SHA256SUM="${SHA256SUM:=/usr/bin/sha256sum}"
STAT="${STAT:=/usr/bin/stat}"
TOUCH="${TOUCH:=/usr/bin/touch}"

# Return 0 if the path needs to be modified, 1 if it doesn't exist or is already a correct symlink
needs_to_be_merged () {
    local to_test="$1"

    if ! test -e $to_test; then
        printf "$to_test does not exist\n"
        return 1
    fi

    if ! test -L $to_test; then
        printf "$to_test is not a symlink\n"
        return 0
    fi
    local target=$($READLINK $to_test)
    printf "$to_test is a symlink to $target\n"

    if [[ "$target" == "usr"$to_test ]]; then
        printf "$to_test is the correct symlink\n"
        return 1
    fi

    printf "$to_test needs to be changed\n"
    return 0
}

# This takes a directory path and creates it and it's parents recursively
create_dir_components () {
    local dir_name="$1"

    # Test to see if the parent exists
    local parent=$($DIRNAME "$dir_name")
    if ! test -e "$parent"; then
        create_dir_components "$parent"
    fi

    # Test to see if the current directory exists
    if test -e "$dir_name"; then
        return
    fi

    # Get the non-merged path so that we can see what permissions it has
    local non_merged_path=${dir_name#"/usr"}
    local dir_stat=$($STAT -c "%a" "$non_merged_path")

    printf "Creating $dir_name with $dir_stat permissions\n"
    # Create the directory with the defined permissions. This is allowed to fail, if it does then we orphan the file instead
    $MKDIR --mode="$dir_stat" $dir_name || true && action="orphan"
}

# This script takes a given file and moves it to the orphaned files directory
# To reduce the risk of any errors occurring or file collisions we flatten the directory path and append the file hash
orphan_file () {
    if ! test -d "$ORPHAN_DIR"; then
        $MKDIR "$ORPHAN_DIR"
    fi

    local file_to_orphan="$1"
    local file_checksum=($($SHA256SUM "$file_to_orphan"))
    local new_file_name="$ORPHAN_DIR/root${file_to_orphan//\//-}.$file_checksum"

    # Check if the orphaned file already exists
    if test -e "$new_file_name"; then
        # It somehow exists, likely from a previous invocation of this script. Make sure it was a successful copy
        local orphan_checksum=($($SHA256SUM "$new_file_name"))
        if [[ "$file_checksum" == "$orphan_checksum" ]]; then
            return 0
        fi

        # The orphaned file exists but does not have the correct checksum. Assume it's an incomplete copy
        printf "Deleting previously orphaned file $new_file_name\n"
        $RM -v "$new_file_name"
    fi

    printf "Copying file $file_to_orphan to $new_file_name\n"
    $CP -av "$file_to_orphan" "$new_file_name"
}

merge_dir () {
    if needs_to_be_merged $1; then
        echo ""

        # Get list of files that are not symlinks
        file_list=()
        while IFS=  read -r -d $'\0'; do
            file_list+=("$REPLY")
        done < <($FIND $1 -type f -print0)

        for old_location in "${file_list[@]}"
        do
            # What we should do with the file, either move it or orphan it
            local new_location="/usr$old_location"
            action="move"
            create_dir_components $($DIRNAME "$new_location")

            # This is where I'm stopped currently, we need to correctly handle the logic of moving files here
            orphan_file "$old_location"
        done
    fi
}

merge_dir /bin
merge_dir /sbin
merge_dir /lib64
merge_dir /lib32
merge_dir /lib

# Have a separate variable so we can test the eopkg epoch separately from the usr-merge
if [ -z "${I_WANT_TO_TEST_THE_EPOCH_TRANSITION_WORKS+set}" ]; then
    exit 0
fi

$TOUCH /run/eopkg-epoch-transition
