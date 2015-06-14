
#!/usr/bin/python


from pisi.actionsapi import pisitools, shelltools, get

WorkDir = "bash_completion"

def setup():
    pass

def build():
    pass

def install():
    pisitools.insinto ("/etc/profile.d", "bash_completion.sh", "70-bash_completion.sh")
    pisitools.insinto ("/etc/", "bash_completion")
    pisitools.dodir ("/etc/bash_completion.d")
    pisitools.dodir ("/usr/share/bash-completion")
    pisitools.insinto ("/etc/bash_completion.d/", "contrib/*")

    pisitools.dodoc ("README")
