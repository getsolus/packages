#!/usr/bin/bash
set -euo pipefail

# This configures the probability that a system is usr merged
# It should be a value from 0 to 256, with 0 being 0% chance, and 256 being 100% chance.
USR_MERGE_CHANCE="${USR_MERGE_CHANCE:=256}"

# This is where orphaned files and flag markers will be set
STATE_DIR="${STATE_DIR:=/var/solus/usr-merge}"
ORPHAN_DIR="${ORPHAN_DIR:=${STATE_DIR}/orphaned-files}"
EOPKG_FLAG_FILE="${EOPKG_FLAG_FILE:=${STATE_DIR}/eopkg-ready}"
MERGE_FLAG_FILE="${MERGE_FLAG_FILE:=${STATE_DIR}/merge-complete}"

# Time in seconds until the warning is shown
SLOW_WARNING_THRESHOLD="${SLOW_WARNING_THRESHOLD:=530}"
SLOW_WARNING_ENABLED="${SLOW_WARNING_ENABLED:=true}"

# List of dirs to be merged
MERGED_DIRS=(/bin /sbin /lib64 /lib32 /lib)

# Manually specify the path of binaries needed since we're messing with /bin and /sbin
CP="${CP:=/usr/bin/cp}"
CAT="${CAT:=/usr/bin/cat}"
DIRNAME="${DIRNAME:=/usr/bin/dirname}"
FIND="${FIND:=/usr/bin/find}"
LN="${LN:=/usr/bin/ln}"
LS="${LS:=/usr/bin/ls}"
MKDIR="${MKDIR:=/usr/bin/mkdir}"
MV="${MV:=/usr/bin/mv}"
READLINK="${READLINK:=/usr/bin/readlink}"
RM="${RM:=/usr/bin/rm}"
SHA256SUM="${SHA256SUM:=/usr/bin/sha256sum}"
STAT="${STAT:=/usr/bin/stat}"
TOUCH="${TOUCH:=/usr/bin/touch}"
DEPMOD="${DEPMOD:=/usr/sbin/depmod}"

function _flag_set() {
    local flag="$1"
    shift

    if [[ " $* " =~ [[:space:]]${flag}[[:space:]] ]]; then
        return 0
    fi

    return 1
}

if _flag_set "--please-break-my-system" "$@"; then
    USR_MERGE_CHANCE=256
fi

# Check if eopkg is ready for the usr merge
if [[ ! -f "${EOPKG_FLAG_FILE}" ]]; then
    echo "Skipping usr-merge: eopkg not ready"
    exit 0
fi

# Check if *this* system can be upgraded
# Generate a number from the last two characters of the machine ID
# and exit if it is greater or equal to the usr merge chance.
machine_id="$(cat /etc/machine-id)"
machine_num="$((16#${machine_id: -2}))"
if [[ "${machine_num}" -ge "${USR_MERGE_CHANCE}" ]]; then
    echo "Skipping usr-merge: ${machine_num} > ${USR_MERGE_CHANCE}"
    exit 0
fi

function console() {
    if [[ -e /dev/console ]]; then
        echo -ne "$@" > /dev/console 2>/dev/null || true
    fi
}

function _echo() {
    console "."
    echo "$@"
}

function _log() {
    file="$1"
    shift

    _echo "[$file]:" "$@"
}

function _checksum() {
    local file_checksum
    IFS=" " read -r -a file_checksum <<< "$($SHA256SUM "$1")"

    echo "${file_checksum[0]}"
}

# Show a warning when the script has been running for longer than required.
# The message is only shown when the migration hasn't completed yet.
function slow_warning() {
    if [ "$SLOW_WARNING_ENABLED" != true ]; then
        return
    fi

    sleep "$SLOW_WARNING_THRESHOLD"

    if [[ ! -f "$MERGE_FLAG_FILE" ]]; then
        console "\n\033[1;33mThis is taking longer than expected.\033[0m\n"
        console "Check the Solus forum or Matrix channel for guidance.\n"
    fi
}

# Return 0 if the path needs to be modified, 1 if it doesn't exist or is already a correct symlink
function needs_to_be_merged () {
    local quiet=false
    if [[ "$1" == "-q" ]]; then
        shift
        quiet=true
    fi

    local to_test="$1"
    local target

    if [[ ! -e "$to_test" ]] && [[ ! -e "/usr${to_test}" ]]; then
        [[ $quiet == false ]] && _log "$to_test" "does not exist"
        return 1
    fi

    if [[ ! -L "$to_test" ]]; then
        [[ $quiet == false ]] && _log "$to_test" "not a symlink"
        return 0
    fi

    target=$($READLINK "$to_test")
    [[ $quiet == false ]] && _log "$to_test" "is a symlink to $target"

    if [[ "$target" == "usr"$to_test ]]; then
        [[ $quiet == false ]] && _log "$to_test" "is the correct symlink"
        return 1
    fi

    [[ $quiet == false ]] && _log "$to_test" "needs to be changed"
    return 0
}

# Return 0 if any given argument needs to be modified or 1 if not.
function any_needs_to_be_merged() {
    for dir in "$@"; do
        if needs_to_be_merged -q "$dir"; then
            return 0
        fi
    done

    return 1
}

# This takes a directory path and creates it and its parents recursively
function create_dir_components () {
    local dir_name="$1"
    local parent dir_stat

    # Test to see if the parent exists
    parent="$($DIRNAME "$dir_name")"
    if [[ ! -d "$parent" ]]; then
        create_dir_components "$parent"
    fi

    # Test to see if the current directory exists
    if [[ -d "$dir_name" ]]; then
        return
    fi

    # Get the non-merged path so that we can see what permissions it has
    local non_merged_path=${dir_name#"/usr"}
    dir_stat=$($STAT -c "%a" "$non_merged_path")

    # Create the directory with the defined permissions. This is allowed to fail, if it does then we orphan the file instead
    $MKDIR --mode="$dir_stat" "$dir_name" || (true && action="orphan")
}

# Create a symbolic link in the old location that points to the new file location. This uses atomic file operations but ultimately is a destructive operation
function create_compat_link () {
    local old_location="$1"
    local new_location="$2"
    local file_checksum

    # Since the new location exists we can presumably checksum it
    file_checksum="$(_checksum "$new_location")"
    local temporary_name="${old_location}.tmp.${file_checksum[0]}"

    # If the temporary file already exists then delete it (?)
    if [[ -f "$temporary_name" ]]; then
        $RM "$temporary_name"
    fi

    _log "$old_location" "creating compatibility symlink to $new_location"
    $LN --no-dereference --symbolic --relative "$new_location" "$temporary_name"
    $MV --force --no-target-directory "$temporary_name" "$old_location"
}

# Takes three arguments, the first is the source file, the second the destination, and the third the cp arguments
# If the source and the destination would be on the same file system then it will add a cp flag to create a hard link
function copy_or_hard_link () {
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

# Helper for the cp command
function copy() {
    $CP --reflink=auto "$@"
}

# Check if the given file must be migrated (regardless of checksum).
function must_migrate_file() {
    case "$1" in
    # Files regenerated by depmod
    */modules/*.current/modules.*|*/modules/*.lts/modules.*)
        return 0
        ;;
    *)
        return 1
        ;;
    esac
}

# Take a given file path and move it to the /usr location. We copy the file first
#  to a temporary file and then move it into place as an atomic operation
function move_file () {
    local file_to_move="$1"
    local destination="$2"
    local file_checksum dest_checksum

    # If the destination exists and is directory then orphan the file
    if [[ -d "$destination" ]]; then
        action="orphan"
        return 0
    fi

    # If the destination exists and is a regular file then:
    # - Copy if it is a special file
    # - Link if the checksum matches
    # - Orphan if the checksum does not match
    file_checksum="$(_checksum "$file_to_move")"
    if [[ -f "$destination" ]]; then
        if must_migrate_file "$file_to_move"; then
            _log "$file_to_move" "moving special file to $destination"
            copy "$file_to_move" "$destination" --archive
            create_compat_link "$file_to_move" "$destination"
            return 0
        fi

        dest_checksum="$(_checksum "$destination")"
        if [[ "$file_checksum" != "$dest_checksum" ]]; then
            action="orphan"
        else
            create_compat_link "$file_to_move" "$destination"
        fi
        return 0
    fi

    local temporary_name="${destination}.tmp.${file_checksum}"

    _log "$file_to_move" "moving to $destination"

    # If the temporary file already exists then delete it. We could checksum it but better to redo the copy operation
    if [[ -e "$temporary_name" ]]; then
        $RM "$temporary_name"
    fi

    copy_or_hard_link "$file_to_move" "$temporary_name" --archive

    # Check if the destination is a symbolic link, if so clobber it
    local mv_mode="--no-clobber"
    if [[ -L "$destination" ]]; then
        mv_mode="--force"
    fi

    $MV $mv_mode --no-target-directory "$temporary_name" "$destination"
    create_compat_link "$file_to_move" "$destination"
}

# Take a given file and moves it to the orphaned files directory. To reduce the risk of any errors occurring or file collisions
#  we flatten the directory path and append the file hash. An error here will halt the script
function orphan_file () {
    local file_checksum orphan_checksum
    local file_to_orphan="$1"

    if [[ ! -d "$ORPHAN_DIR" ]]; then
        $MKDIR "$ORPHAN_DIR"
    fi

    file_checksum="$(_checksum "$file_to_orphan")"
    local new_file_name="$ORPHAN_DIR/root${file_to_orphan//\//-}.$file_checksum"

    # Check if the orphaned file already exists
    if [[ -e "$new_file_name" ]]; then
        # It somehow exists, likely from a previous invocation of this script. Make sure it was a successful copy
        orphan_checksum="$(_checksum "$new_file_name")"
        if [[ "$file_checksum" == "$orphan_checksum" ]]; then
            return 0
        fi

        # The orphaned file exists but does not have the correct checksum. Assume it's an incomplete copy
        _log "$file_to_orphan" "deleting previously orphaned file $new_file_name"
        $RM "$new_file_name"
    fi

    _log "$file_to_orphan" "copying orphan to $new_file_name"
    copy_or_hard_link "$file_to_orphan" "$new_file_name" --archive

    _log "$file_to_orphan" "deleting orphaned file"
    $RM "$file_to_orphan"
}

# Detect whether or not the given directory contains only
function detect_ready_for_merge () {
    local dir_name="$1"

    local file_list=()
    while IFS=  read -r -d $'\0'; do
        file_list+=("$REPLY")
    done < <($FIND "$dir_name" -type f -print0)

    if [ ${#file_list[@]} -eq 0 ]; then
        _log "$dir_name" "ready for merge"
        return 0
    fi
    return 1
}

# Usr-merge a given directory
function usr_merge_directory () {
    local dir_name="$1"
    local usr_location="usr$dir_name"
    local temporary_name="${dir_name}.tmp-usr-merge"

    _log "$dir_name" "usr-merging to $usr_location"

    # Delete the temporary file if it already exists
    if [[ -L "$temporary_name" ]]; then
        $RM "$temporary_name"
    fi

    $LN --no-dereference --symbolic "$usr_location" "$temporary_name"
    $MV --force --exchange --no-target-directory "$temporary_name" "$dir_name"
    $RM --recursive "$temporary_name"

    _log "$dir_name" "merged"
}

function merge_dir () {
    local dir_name="$1"
    local usr_location="usr$dir_name"

    if needs_to_be_merged "$dir_name"; then
        # Create symlink immediately if it doesn't exist
        if [[ ! -e "$dir_name" ]]; then
            _log "$dir_name" "linking to $usr_location"
            $LN --no-dereference --symbolic "$usr_location" "$dir_name"
            return
        fi

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

function merge_dirs() {
    for dir in "$@"; do
        merge_dir "$dir"
    done
}

function create_merge_flag_file() {
    if [[ ! -e "${MERGE_FLAG_FILE}" ]]; then
        $MKDIR -p "${STATE_DIR}"
        $TOUCH "${MERGE_FLAG_FILE}"
    fi
}

if ! any_needs_to_be_merged "${MERGED_DIRS[@]}"; then
    echo "Skipping usr-merge: already done!"
    create_merge_flag_file
    exit 0
fi

console "Performing important system maintenance, please wait.\n"
console "This process may take up to 10 minutes to complete.\n"
console "It is safe to turn off your computer if necessary.\n"
slow_warning &

_echo "Starting merge:"
merge_dirs "${MERGED_DIRS[@]}"
create_merge_flag_file

_echo "Result:"
$LS -l "${MERGED_DIRS[@]}" 2>/dev/null || true

console " Done!\n"
