#!/bin/bash

###STEP 1: Generate data for Phab
cap=4500
r=1
rm /tmp/phab-input.txt
while [ $r -le $cap ]; do
    echo R${r} >> /tmp/phab-input.txt
    r=$(( $r + 1 ))
done
xdg-open /tmp/phab-input.txt > /dev/null 2>&1 &
xdg-open https://dev.solus-project.com/maniphest/task/edit/form/1/ > /dev/null 2>&1 &
touch /tmp/phab-output.txt
xdg-open /tmp/phab-output.txt > /dev/null 2>&1 &

echo "
STEP 2: Paste contents from phab-input in Task, Inspect description preview, Edit as HTML. Copy paste HTML into /tmp/phab-output.txt"
read -rsp $'Press any key to continue...\n' -n1 key

###STEP 3: Generate readable names
cat /tmp/phab-output.txt | grep href | sed 's:^<a href=\"/source/::' | cut -d / -f 1 | sort -d -f > /tmp/Temp.txt


# These repositories aren't packages
NONPKGS="mirror-clr-boot-manager
arc-tr
infrastructure-tooling
common
solus-image-budgie
solus-image-mate
solus-image-gnome
solus-image-i3
solus-appstream-data
solus-site
solus-site-styling
solus-webplatform-js
mirror-budgie-desktop
solus-site-backend
solus-image-plasma"

# These packages are not used within Solus
ARCHIVEDPKGS="amdgpu-pro
antiword
arc-firefox-theme
captiva-icon-theme
catalyst
catalyst-glx-driver
ceti2-gtk-theme
cgames
cgoban1
colordiff
cscope
D1671
dkms
docbook-xsl
dropbear
encodings
esetroot
evoassist
evolve-sc
gtk3-engine-unico
faac
faenza-icon-theme
fglrx
font-adobe-utopia-100dpi
font-adobe-utopia-75dpi
font-adobe-utopia-type1
font-alias
font-arabic-misc
font-bh-100dpi
font-bh-75dpi
font-bh-lucidatypewriter-100dpi
font-bh-lucidatypewriter-75dpi
font-bh-ttf
font-bh-type1
font-bitstream-100dpi
font-bitstream-75dpi
font-bitstream-type1
font-cronyx-cyrillic
font-cursor-misc
font-daewoo-misc
font-dec-misc
font-ibm-type1
font-isas-misc
font-jis-misc
font-micro-misc
font-misc-cyrillic
font-misc-ethiopic
font-misc-meltho
font-misc-misc
font-mutt-misc
font-schumacher-misc
font-screen-cyrillic
font-sony-misc
font-sun-misc
font-winitzki-cyrillic
font-xfree86-type1
foomatic-filters
fs-uae-arcade
geeqie
gl-driver-switch
glamor-egl
gnome-initial-setup
gnome-js-common
gnome-packagekit
gnome-shell-extension-caffeine
gnome-themes-mediterranean
gnonlin
gnucash
grc
greed
iceauth
jmtpfs
journal
kdevplatform
kernel
kodi-addon-inputstream-adaptive
la
lapack
libgames-support
libirclient
libsdl
libuuid
libwnck-1
libzeitgeist
lightzone
mate-notification-theme-solus
mlocate
mozjs17
notification-daemon
notify-osd
nxcomp
nxproxy
pacifica-icon-theme
perl-net-bdus
plexhometheater
python3-colorama
python3-decorator
python3-xlib
python-django
python-polkit
python-pyflakes
python-pylint
qt5-everywhere
qt5-x11patterns
qtcreator
quirky
rethinkdb
roboto-ttf
sane
sessreg
setuptools_scm
smproxy
software-update-icon
solus-migration
spidermonkey
sylpheed
wocky
x11perf
xcmsdb
xdriinfo
xf86-input-cmt
xkbevd
xkbutils
xlsatoms
xlsclients
xmlindent
xorg-driver-video-modesetting
xpr
xrefresh
xterm
xvinfo
xwud"

# Can probably delete repos: libuuid qtcreator la libgames-support qt5-x11patterns

# STEP 4: Remove repos that aren't packages or are no longer used
for i in $NONPKGS $ARCHIVEDPKGS; do
    sed -i "/^${i}$/d" /tmp/Temp.txt
done

cat /tmp/Temp.txt > ~/git/Solus/common/packages

# Cleanup
rm /tmp/Temp.txt /tmp/phab-input.txt /tmp/phab-output.txt
