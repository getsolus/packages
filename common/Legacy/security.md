*Changes needed for an improved security architecture in Solus*

xattr (DONE in eopkg)
-----

eopkg must support extended filesystem attributes. Until Solus 2 arrives, we
will still be using the Pythonic eopkg.

As such, we shall extend the FileInfo class to support the following export
in the files.xml:

    <ExtendedAttributes>
        <Attribute label="some.label">value</Attribute>
    </ExtendedAttributes>


Consequently `ypkg` will introspect the paths currently provided in the
`metadata.py` module, to provide these key/value mappings.

Upon installation of the package we will then attempt restoration of the xattrs.
Note that this requires a filesystem with xattr support to be mandatory to the
use of Solus.

As such, our ISO medium should reflect this.

Employing xattr
---------------

Firstly we need to abolish the use of setuid in the distribution. A prime example
of this includes:

    - Xorg
    - mount
    - umount
    - ping (and other inetutils friends)

All setuid binaries must instead use an alternative approach, in most cases this
will be achieved with by setting the capability. i.e. for ping:

    setcap cap_net_raw=ep  $installdir/usr/bin/ping 

Potential:
----------

*SMACK*

A full-fat approach such as SELINUX is very undesirable for Solus as it is
cumbersome. An alternative such as SMACK should be employed.

Domain Separation
------------------

To suit the app/OS model required for Solus 2, we need complete domain
separation. This entails separating hardware, file and network access from the
applications into providing domains. The specifics at this point aren't strictly
important, however:

    - CAP_SYS_ADMIN binary or equivalent as a sandboxing mechanism
    - Labels on dbus paths and sockets restricting access to external D-BUS
      APIS
    - App D-BUS API for requesting permissions of the host OS from the isolated
      app instances
    - Apps will require signed bundles
    - Labels on all exported d-bus services in the base OS
    - Apps bind mounted into isolated namespace with only access out via the
      keyhole service
