SolusOS Package Helper Scripts
==============================

These scripts are really simple and will help you to create PiSi packages
for SolusOS much faster.

Creating a package
------------------
    mkdir PKGNAME
    cd PKGNAME
    autopackage.py $URLOFPACKAGE

Two files should be created in the current directory, the pspec.xml and actions.py
Customise to your needs, and fill in the blanks. A good practice is to fist build
the package without the <Path> sections complete, and run "lspisi" against the .pisi
package, and then fill in the <Path>'s :) You can save time by doing:

    pisi build pspec.xml --package

Completing the dependencies
---------------------------
This one is real simple. It outputs all of the **binary** package dependencies it
can find. It will not find all! But it helps :) It will also attempt to add the
relevant -devel build-deps.

    dep_check.py name_of_installed_pisi_package

Notes
-----
You should add this Scripts directory to your path for ease-of-use :)

Feel free to report bugs on Maniphest
