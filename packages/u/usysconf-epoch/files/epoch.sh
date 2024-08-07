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
LN="${LN:=/usr/bin/ln}"
MKDIR="${MKDIR:=/usr/bin/mkdir}"
MV="${MV:=/usr/bin/mv}"
READLINK="${READLINK:=/usr/bin/readlink}"
RM="${RM:=/usr/bin/rm}"
SHA256SUM="${SHA256SUM:=/usr/bin/sha256sum}"
STAT="${STAT:=/usr/bin/stat}"
TOUCH="${TOUCH:=/usr/bin/touch}"

_checksum() {
    local file_checksum
    IFS=" " read -r -a file_checksum <<< "$($SHA256SUM "$1")"

    echo "${file_checksum[0]}"
}

# Return 0 if the path needs to be modified, 1 if it doesn't exist or is already a correct symlink
needs_to_be_merged () {
    local to_test="$1"
    local target

    if ! test -e "$to_test"; then
        echo "$to_test does not exist"
        return 1
    fi

    if ! test -L "$to_test"; then
        echo "$to_test is not a symlink"
        return 0
    fi

    target=$($READLINK "$to_test")
    echo "$to_test is a symlink to $target"

    if [[ "$target" == "usr"$to_test ]]; then
        echo "$to_test is the correct symlink"
        return 1
    fi

    echo "$to_test needs to be changed"
    return 0
}

# This takes a directory path and creates it and it's parents recursively
create_dir_components () {
    local dir_name="$1"
    local parent dir_stat

    # Test to see if the parent exists
    parent="$($DIRNAME "$dir_name")"
    if ! test -e "$parent"; then
        create_dir_components "$parent"
    fi

    # Test to see if the current directory exists
    if test -e "$dir_name"; then
        return
    fi

    # Get the non-merged path so that we can see what permissions it has
    local non_merged_path=${dir_name#"/usr"}
    dir_stat=$($STAT -c "%a" "$non_merged_path")

    echo "Creating $dir_name with $dir_stat permissions"
    # Create the directory with the defined permissions. This is allowed to fail, if it does then we orphan the file instead
    $MKDIR --verbose --mode="$dir_stat" "$dir_name" || (true && action="orphan")
}

# Create a symbolic link in the old location that points to the new file location. This uses atomic file operations but ultimately is a destructive operation
create_compat_link () {
    local old_location="$1"
    local new_location="$2"
    local file_checksum

    # Since the new location exists we can presumably checksum it
    file_checksum="$(_checksum "$new_location")"
    local temporary_name="${old_location}.tmp.${file_checksum[0]}"

    # If the temporary file already exists then delete it (?)
    if test -e "$temporary_name"; then
        $RM --verbose "$temporary_name"
    fi

    echo "Creating symlink $old_location to $new_location"
    $LN --no-dereference --symbolic --verbose --relative "$new_location" "$temporary_name"
    $MV --force --no-target-directory --verbose "$temporary_name" "$old_location"
}

# Takes three arguments, the first is the source file, the second the destination, and the third the cp arguments
# If the source and the destination would be on the same file system then it will add a cp flag to create a hard link
copy_or_hard_link () {
    local file_to_move="$1"
    local destination="$2"
    shift 2
    local cp_args=("$@")
    local dest_parent source_device dest_device

    dest_parent=$($DIRNAME "$destination")
    source_device=$($STAT -c "%D" "$file_to_move")
    dest_device=$($STAT -c "%D" "$dest_parent")

    if [[ "$source_device" == "$dest_device" ]]; then
        cp_args+=("--link")
    fi

    $CP "${cp_args[@]}" "$file_to_move" "$destination"
}

# Take a given file path and move it to the /usr location. We copy the file first
#  to a temporary file and then move it into place as an atomic operation
move_file () {
    local file_to_move="$1"
    local destination="$2"
    local file_checksum dest_checksum

    # If the destination exists and is directory then orphan the file
    if test -d "$destination"; then
        action="orphan"
        return 0
    fi

    # If the destination exists and is a regular file then check the checksum of it, if they're the same then we orphan the file.
    # If they are the same we can just skip the file
    file_checksum="$(_checksum "$file_to_move")"
    if test -f "$destination"; then
        dest_checksum="$(_checksum "$destination")"
        if [[ "$file_checksum" != "$dest_checksum" ]]; then
            action="orphan"
        else
            create_compat_link "$file_to_move" "$destination"
        fi
        return 0
    fi

    local temporary_name="${destination}.tmp.${file_checksum}"

    # If the temporary file already exists then delete it. We could checksum it but better to redo the copy operation
    if test -e "$temporary_name"; then
        echo "$temporary_name already exists, deleting it"
        $RM --verbose "$temporary_name"
    fi

    echo "Copying file $file_to_move to $temporary_name"
    copy_or_hard_link "$file_to_move" "$temporary_name" --archive --verbose

    # Check if the destination is a symbolic link, if so clobber it
    local mv_mode="--no-clobber"
    if test -L "$destination"; then
        mv_mode="--force"
    fi

    $MV $mv_mode --no-target-directory --verbose "$temporary_name" "$destination"
    create_compat_link "$file_to_move" "$destination"
}

# Take a given file and moves it to the orphaned files directory. To reduce the risk of any errors occurring or file collisions
#  we flatten the directory path and append the file hash. An error here will halt the script
orphan_file () {
    local file_checksum, orphan_checksum

    if ! test -d "$ORPHAN_DIR"; then
        $MKDIR --verbose "$ORPHAN_DIR"
    fi

    local file_to_orphan="$1"
    file_checksum="$(_checksum "$file_to_orphan")"
    local new_file_name="$ORPHAN_DIR/root${file_to_orphan//\//-}.$file_checksum"

    # Check if the orphaned file already exists
    if test -e "$new_file_name"; then
        # It somehow exists, likely from a previous invocation of this script. Make sure it was a successful copy
        orphan_checksum="$(_checksum "$new_file_name")"
        if [[ "$file_checksum" == "$orphan_checksum" ]]; then
            return 0
        fi

        # The orphaned file exists but does not have the correct checksum. Assume it's an incomplete copy
        echo "Deleting previously orphaned file $new_file_name"
        $RM --verbose "$new_file_name"
    fi

    echo "Copying file $file_to_orphan to $new_file_name"
    copy_or_hard_link "$file_to_orphan" "$new_file_name" --archive --verbose

    # TODO: For now we're not deleting orphaned files since we want the script to fail so we can find any edge cases
}

# Detect whether or not the given directory contains only
detect_ready_for_merge () {
    local dir_name="$1"

    local file_list=()
    while IFS=  read -r -d $'\0'; do
        file_list+=("$REPLY")
    done < <($FIND "$dir_name" -type f -print0)

    if [ ${#file_list[@]} -eq 0 ]; then
        echo "$dir_name is ready for merge"
        return 0
    fi
    return 1
}

# Usr-merge a given directory
usr_merge_directory () {
    local dir_name="$1"
    local usr_location="usr$dir_name"
    local temporary_name="${dir_name}.tmp-usr-merge"

    # Delete the temporary file if it already exists
    if test -L "$temporary_name"; then
        $RM --verbose "$temporary_name"
    fi

    echo "Usr-merging $dir_name to $usr_location"
    $LN --no-dereference --symbolic --verbose "$usr_location" "$temporary_name"
    $MV --force --exchange --no-target-directory --verbose "$temporary_name" "$dir_name"
    $RM --verbose --recursive "$temporary_name"
}

merge_dir () {
    local dir_name="$1"
    if needs_to_be_merged "$dir_name"; then
        # Get list of files that are not symlinks
        file_list=()
        while IFS=  read -r -d $'\0'; do
            file_list+=("$REPLY")
        done < <($FIND "$dir_name" -type f -print0)

        for old_location in "${file_list[@]}"
        do
            # What we should do with the file, either move it or orphan it
            local new_location="/usr$old_location"
            action="move"
            create_dir_components "$($DIRNAME "$new_location")"

            if [[ "$action" == "move" ]]; then
                move_file "$old_location" "$new_location"
            fi

            if [[ "$action" == "orphan" ]]; then
                orphan_file "$old_location"
            fi
        done

        if detect_ready_for_merge "$dir_name"; then
            usr_merge_directory "$dir_name"
        fi
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
