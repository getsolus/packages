#!/usr/bin/python

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def setup():
    # Will disable perlinterp until we have that :)
    autotools.configure('--with-features=huge \
                         --prefix=/usr \
                         --exec-prefix=/usr \
                         --localstatedir=/var/lib/vim \
                         --enable-gui=no\
                         --enable-multibyte\
                         --enable-pythoninterp \
                         --enable-rubyinterp \
                         --disable-netbeans \
                         --disable-perlinterp \
                         --with-compiledby=\'Solus\' \
                         --with-modified-by=\'Solus\'')
def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Should be needed
    pisitools.dosym('/etc/vim/vimrc','/usr/share/vim/vimrc')
    pisitools.dosym('/etc/vim/vimrc.tiny','/usr/share/vim/vimrc.tiny')
    pisitools.dosym('/usr/bin/vim','/usr/bin/vi')