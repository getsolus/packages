
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

ZoneDir = "/usr/share/zoneinfo"
TargetDir = "%s/%s" % (get.installDIR(), ZoneDir)

RightDir = "%s/right" % TargetDir
PosixDir = "%s/posix" % TargetDir

WorkDir = "."

Components = ["etcetera", "southamerica", "northamerica", "europe", "africa", "antarctica", \
              "asia", "australasia", "backward", "pacificnew", "solar87", "solar88", "solar89", \
              "systemv" ]

ExtraDist = ["zone.tab", "iso3166.tab"]

def setup():
    pisitools.dodir (ZoneDir)
    pisitools.dodir (RightDir)
    pisitools.dodir (PosixDir)


def install():
    for extra in ExtraDist:
        pisitools.insinto (ZoneDir, extra)

    for tz in Components:
        cmd = "zic -L /dev/null -d %s -y \"%s/yearistype.sh\" %s" % (TargetDir, get.workDIR(), tz)
        shelltools.system (cmd)
        part2 = "zic -L /dev/null -d %s -y \"%s/yearistype.sh\" %s" % (PosixDir, get.workDIR(), tz)
        shelltools.system (part2)
        part3 = "zic -L leapseconds -d %s -y \"%s/yearistype.sh\" %s" % (RightDir, get.workDIR(), tz)
        shelltools.system (part3)

    # Default DST
    shelltools.system ("zic -d %s -p America/New_York" % TargetDir)
