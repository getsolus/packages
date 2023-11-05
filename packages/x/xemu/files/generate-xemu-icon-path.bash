# This function takes an icon name of the form
# xemu_(x-size)x(y-size).png and generates a proper icon path
# of the form /usr/share/icons/hicolor/(x-size)x(y-size)/apps/xemu.png
#
# Test case:
# source generate-xemu-icon-path.bash
# generate-xemu-icon-path xemu_512x512.png
# -> /usr/share/icons/hicolor/512x512/apps/xemu.png
function generate-xemu-icon-path () {
    if [[ ! -n "$1" ]]; then
        echo "no argument supplied to generate-xemu-icon-path, exiting!"
        exit 1
    fi
    local input="$1"
    # parses as "xemu"
    local name="${input:0:4}"
    # drop _ and parse the rest
    local remaining="${input:5}"
    # split up into base name and extension
    IFS="." read -r -a sizeandext <<< "$remaining"
    local extension="${sizeandext[1]}"
    local size="${sizeandext[0]}"
    # split size into xsize and ysize
    IFS="x" read -r -a xysize <<< "$size"
    local xsize="${xysize[0]}"
    local ysize="${xysize[1]}"
    # return the generated standard icon path
    echo /usr/share/icons/hicolor/"$xsize"x"$ysize"/apps/"$name"."$extension"
}

