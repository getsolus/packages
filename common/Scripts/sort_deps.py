#!/usr/bin/env python2

import ruamel.yaml

try:
    with open("package.yml", "r") as file:
        lines = file.readlines()
        file.seek(0)
        data = ruamel.yaml.round_trip_load(file)
        builddeps = data.get("builddeps")
        maxwidth = len(max(lines, key=len))

    x = sorted(filter(lambda entry: entry.startswith("pkgconfig("), builddeps))
    y = sorted(filter(lambda entry: not entry.startswith("pkgconfig("), builddeps))
    sorted_builddeps = x + y

    if builddeps != sorted_builddeps:
        print "builddeps were not in the correct order.\n", builddeps
        print "\nWriting correct builddeps order to package.yml...\n", sorted_builddeps
        data["builddeps"] = sorted_builddeps
        with open("package.yml", "w") as file:
            ruamel.yaml.round_trip_dump(
                data,
                file,
                indent=4,
                block_seq_indent=4,
                width=maxwidth,
                top_level_colon_align=True,
                prefix_colon=" ",
            )
    else:
        print "builddep's are in the correct order."

except TypeError:
    print "builddeps key does not exist in this package.yml"

except IOError as e:
    print e
