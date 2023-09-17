#!/bin/sh

if [ -n "GTK_MODULES" ]; then
	GTK_MODULES="${GTK_MODULES}:appmenu-gtk-module"
else
	GTK_MODULES="appmenu-gtk-module"
fi

export GTK_MODULES
