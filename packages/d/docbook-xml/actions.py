
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
from pisi.actionsapi.shelltools import system

import os.path

def create_catalog (targ):
    ''' Create a new catalog '''
    system ("xmlcatalog --noout --create %s" % targ)

def insert_into_catalog (type_name, dtd_name, dtd_location, catalog_file):
    ''' Insert DTD into the catalog '''
    vars_map = { 'TypeName': type_name,\
                             'DtdName': dtd_name,\
                             'DtdLocation': dtd_location,\
                             'Catalog': catalog_file }
    system ('xmlcatalog --noout --add "%(TypeName)s" "%(DtdName)s" "%(DtdLocation)s" "%(Catalog)s"' % vars_map)

def install():
    docBookRoot = "/usr/share/xml/docbook/xml-dtd-4.5"
    pisitools.dodir (docBookRoot)
    pisitools.dodir ("/etc/xml")

    for copy in ["docbook.cat", "*.dtd", "ent/", "*.mod"]:
        copy_full = os.path.join (get.workDIR(), copy)
        pisitools.insinto (docBookRoot, copy_full)

    # Now create /etc/xml/docbook
    workFile = os.path.join (get.installDIR(), "etc/xml/docbook")

    create_catalog (workFile)

    # Add all publics
    public_dtds = dict()
    public_dtds ["-//OASIS//DTD DocBook XML V4.5//EN"] = "http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd"
    public_dtds ["-//OASIS//DTD DocBook XML CALS Table Model V4.5//EN"] = "file:///usr/share/xml/docbook/xml-dtd-4.5/calstblx.dtd"
    public_dtds ["-//OASIS//DTD XML Exchange Table Model 19990315//EN"] = "file:///usr/share/xml/docbook/xml-dtd-4.5/soextblx.dtd"
    public_dtds ["-//OASIS//ELEMENTS DocBook XML Information Pool V4.5//EN"] = "file:///usr/share/xml/docbook/xml-dtd-4.5/dbpoolx.mod"
    public_dtds ["-//OASIS//ELEMENTS DocBook XML Document Hierarchy V4.5//EN"] = "file:///usr/share/xml/docbook/xml-dtd-4.5/dbhierx.mod"
    public_dtds ["-//OASIS//ELEMENTS DocBook XML HTML Tables V4.5//EN" ] = "file:///usr/share/xml/docbook/xml-dtd-4.5/htmltblx.mod"
    public_dtds ["-//OASIS//ENTITIES DocBook XML Notations V4.5//EN"] = "file:///usr/share/xml/docbook/xml-dtd-4.5/dbnotnx.mod"
    public_dtds ["-//OASIS//ENTITIES DocBook XML Character Entities V4.5//EN"] = "file:///usr/share/xml/docbook/xml-dtd-4.5/dbcentx.mod"
    public_dtds ["-//OASIS//ENTITIES DocBook XML Additional General Entities V4.5//EN"] = "-//OASIS//ENTITIES DocBook XML Additional General Entities V4.5//EN"
    for public_dtd in public_dtds:
        insert_into_catalog ("public", public_dtd, public_dtds [public_dtd], workFile)

    # Rewrites
    insert_into_catalog ("rewriteSystem", "http://www.oasis-open.org/docbook/xml/4.5", "file:///usr/share/xml/docbook/xml-dtd-4.5", workFile)
    insert_into_catalog ("rewriteURI", "http://www.oasis-open.org/docbook/xml/4.5", "file:///usr/share/xml/docbook/xml-dtd-4.5", workFile)

    ## Now we're onto the catalog itself ##
    workFile = os.path.join (get.installDIR(), "etc/xml/catalog")
    create_catalog (workFile)

    # Add the entries
    insert_into_catalog ("delegatePublic", "-//OASIS//ENTITIES DocBook XML", "file:///etc/xml/docbook", workFile)
    insert_into_catalog ("delegatePublic", "-//OASIS//DTD DocBook XML", "file:///etc/xml/docbook", workFile)
    insert_into_catalog ("delegateSystem", "http://www.oasis-open.org/docbook/", "file:///etc/xml/docbook", workFile)
    insert_into_catalog ("delegateURI", "http://www.oasis-open.org/docbook/", "file:///etc/xml/docbook", workFile)

    # Ensure all versions are available
    workFile = os.path.join (get.installDIR(), "etc/xml/docbook")
    catFile = os.path.join (get.installDIR(), "etc/xml/catalog")

    for version in ["4.1.2", "4.2", "4.3", "4.4"]:
        insert_into_catalog ("public", "-//OASIS//DTD DocBook XML V%s//EN" % version, "http://www.oasis-open.org/docbook/xml/%s/docbookx.dtd" % version, workFile)
        insert_into_catalog ("rewriteSystem", "http://www.oasis-open.org/docbook/xml/%s" % version, "file:///usr/share/xml/docbook/xml-dtd-4.5", workFile)
        insert_into_catalog ("rewriteURI", "http://www.oasis-open.org/docbook/xml/%s" % version, "file:///usr/share/xml/docbook/xml-dtd-4.5", workFile)
        insert_into_catalog ("delegateSystem", "http://www.oasis-open.org/docbook/xml/%s/" % version, "file:///etc/xml/docbook", catFile)
        insert_into_catalog ("delegateURI", "http://www.oasis-open.org/docbook/xml/%s/" % version, "file:///etc/xml/docbook", catFile)
