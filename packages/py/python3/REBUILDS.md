Due to currently poor tooling for dealing with python rebuilds and rebuilds in general please
follow these instructions and adjust them for your needs for python upgrades.

1. Run `make clone` in your solus directory to clone very package.
2. Run `dirname $(grep -iRl "python3" */{package.yml,abi_used_libs}) | sort | uniq` to find all packages that use python3
3. Upgrade python locally and put the resulting eopkgs in /var/lib/solbuild/local
4. Use a rebuild script to rebuild all packages against the new python version. Use the following snippet as an example.

```
#!/bin/bash
PACKAGES="$(cat "python-packages.txt")"

cd ~/solus-repo

package_count() {
    echo ${PACKAGES} | wc -w
}

bump() {
    for i in ${PACKAGES}
	do
	  pushd ${i}
        make bump
      popd
	done
}

build() {
    set -e
	for i in ${PACKAGES}
	do
	    pushd ${i}
        var=$((var+1))
	    echo "Building package" ${var} "out of" $(package_count)
        if [[ ! `ls *.eopkg` ]]; then
          make local
          sudo cp *.eopkg /var/lib/solbuild/local
        fi;
		popd
	done
}
```

In no particular order the most important packages to rebuild first are: python-six, python-configobj, pyyaml, python-pytest, pbr, 
python-requests, python-dbus, python-setuptools-scm, python-setuptools-git, flake, pyflakes, python-pytest-flake8, meson, libxml2 gobject-introspection.

These should be put at the top of the package list.

You'll need to babysit the script and cut and paste the order of packages when errors come up and disable tests in the event
of circular dependencies.