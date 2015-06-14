#!/usr/bin/python

import piksemel
import os


def updateIconThemes(filepath):
    parse = piksemel.parse(filepath)
    affected_icon_themes = []

    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if "/share/icons/" in path:
            if not path.startswith("/"):
                path = "/" + path
            theme_dir = path.split("/")[4]
            if not theme_dir in affected_icon_themes:
                affected_icon_themes.append(theme_dir)
            break
    # Update all affected icon themes
    for theme in affected_icon_themes:
        os.system("/usr/bin/gtk-update-icon-cache -ft \
            \"/usr/share/icons/%s\"" % theme)


def setupPackage(metapath, filepath):
    updateIconThemes(filepath)


def postCleanupPackage(metapath, filepath):
    updateIconThemes(filepath)
