================================================
PDFlib - A library for generating PDF on the fly
================================================

Portable C library for dynamically generating PDF ("Adobe Acrobat") files,
with support for many other programming languages.

The PDFlib distribution is available from www.pdflib.com

PDFlib is a library for generating PDF files. It offers an API with
support for text, vector graphics, raster image, and hypertext. Call PDFlib
routines from within your client program and voila: dynamic PDF files!

PDFlib is available on a wide variety of operating system platforms,
and supports many programming languages and development environments:

- C
- C++
- Cobol
- COM (Visual Basic, ASP, Windows Script Host, Delphi, and many others)
- Java via the JNI, including servlets and JSP (but not EJB)
- .NET framework (VB.NET, ASP.NET, C# and others).
- Perl
- PHP Hypertext Processor
- Python
- REALbasic
- RPG
- Ruby
- Tcl

An overview of PDFlib features can be found in the PDFlib tutorial and
the PDFlib reference manual. Separate Windows editions of these manuals
cover the COM, .NET, and REALbasic bindings.


PDFlib flavors
==============
The PDFlib software is available in different flavors (see the PDFlib
tutorial for a detailed comparison):

- PDFlib Lite
  Open-source edition for basic PDF generation, free for personal use.
  PDFlib Lite does not support all languages, and is not available on
  EBCDIC platforms.
  Important note: PDFlib Lite supports only a subset of PDFlib features.
  The differences are detailed in the PDFlib tutorial.

- PDFlib
  The commercial edition adds various features for advanced PDF generation.

- PDFlib+PDI
  Includes PDFlib plus the PDF Import library PDI which can be used to
  integrate pages from existing PDF documents in the generated output

- PDFlib Personalization Server (PPS)
  Includes PDFlib+PDI, plus advanced block processing functions for
  easily personalizing PDF documents. PPS also includes the Block
  plugin for Adobe Acrobat which can be used to create PDFlib blocks
  interactively.


Binary Packages
===============
PDFlib, PDFlib+PDI, and PPS are available in binary form, and require
a commercial license. All of these products are available in a single
library, and can be evaluated without any restrictions without any
license. However, unless a valid license key is applied a demo stamp
will be generated across all pages.
The binary packages support C plus various other language bindings.
Instructions for using these packages can be found in doc/readme-binary.txt.


PDFlib Lite Source Packages
===========================
PDFlib Lite is available in source form, and can be used for free under
certain conditions. Source code is also available for selected language
wrappers. If you are working with a source code package you need an ANSI C
compiler. Detailed instructions for building PDFlib from source code
can be found in doc/readme-source-*.txt


Documentation and Samples
=========================
We provide the following material to assist you in using PDFlib successfully:

- The mini samples (hello, image, pdfclock, etc.) are available in all
  packages and for all supported language bindings. They provide minimalistic
  sample code for text output, images, and vector graphics. The mini samples
  are mainly useful for testing your PDFlib installation, and for getting a
  very quick overview of writing PDFlib applications.

  The hello, pdfclock, chartab, and image examples work with PDFlib or
  PDFlib Lite.

  The invoice and quickreference examples require PDFlib+PDI, and demonstrate
  how to deal with existing PDF documents.

  The businesscard example requires the PDFlib Personalization Server (PPS),
  and contains a simple personalization example.

- The starter samples are contained in all packages and are available for a
  variety of language bindings. They provide a useful generic starting point
  for important topics, and cover simple text and image output, Textflow and
  table formatting, PDF/A and PDF/X creation and other topics. The starter
  samples demonstrate the basic techniques for achieving a particular goal
  with PDFlib products. It is strongly recommended to take a look at the
  starter samples.

- The PDFlib Tutorial, which is contained in all packages as a single PDF
  document, explains important programming concepts in more detail, using
  explanations, tables, and small or large pieces of sample code. If you
  start extending your code beyond the starter samples you should read up on
  relevant topics in the PDFlib Tutorial.

- The PDFlib Reference, which is contained in all packages as a single PDF
  document, contains a concise description of all functions, parameters, and
  options which together comprise the PDFlib application programming interface
  (API). The PDFlib Reference is the definitive source for looking up parameter
  details, supported options, input conditions, and other programming rules
  which must be observed. Note that some versions of the PDFlib reference are
  incomplete, e.g. the Javadoc API listing for PDFlib and the PDFlib function
  listing on php.net. Make sure to always use the full PDFlib Reference when
  working with PDFlib.

- The PDFlib Cookbook is a growing collection of PDFlib coding fragments for
  solving specific problems. Most Cookbook examples are written in the Java
  language, but can easily be adjusted to other programming languages since
  the PDFlib API is almost identical for all supported language bindings. The
  PDFlib Cookbook is maintained as a growing collection of sample programs.
  It is available on the Web at the following URL:

  www.pdflib.com/developer/cookbook


Other PDFlib resources
======================
In addition to the PDFlib reference manual the following resources
are available:

- The PDFlib FAQ collects information about known bugs, patches,
  and workarounds: www.pdflib.com

- The PDFlib mailing list discusses PDFlib deployment in a variety of
  environments. You can access the mailing list archives over the Web,
  and don't need to subscribe in order to use it:
  groups.yahoo.com/group/pdflib

- Commercial PDFlib licensees are eligible to standard product
  support from PDFlib GmbH. Please send your inquiry along with your
  PDFlib license number to support@pdflib.com.

- Customers with a valid support contract can benefit from additional
  advantages, including short response times and free minor and major
  updates; see our Web site for details.


Submitting Bug Reports
======================
In case of trouble you should always check the PDFlib Web site in order
to see whether your problem is already known, or a patch exists.  If not
so, please observe the following:

If you have trouble with running PDFlib, please send the following
information to support@pdflib.com

- a description of your problem
- the platform in use
- the PDFlib version number you are using
- the language binding you are using, along with relevant version numbers
- relevant code snippets for reproducing the problem, or a small PDF file
  exhibiting the problem if you can't construct a code snippet easily
- sample data files if necessary (image files, for example)
- details of the PDF viewer (if relevant) where the problem occurs

If you have trouble compiling the PDFlib Lite source code, please send the
following information to support@pdflib.com:

- a description of your problem and the platform in use
- the PDFlib version number you are using
- the output of "./libtool --config" (Unix systems only)
- most welcome: suggested patches or solutions, other helpful information


Licensing and Copyright
=======================
THIS IS NOT PUBLIC DOMAIN OR FREEWARE SOFTWARE!

PDFlib Lite can freely be used for non-profit personal use.
The license text can be found in the file PDFlib-Lite-license.pdf.

PDFlib, PDFlib+PDI, and PPS can only be used under the terms of
a commercial license, and always require a license fee. Details
of the license can be found in the file PDFlib-license.pdf.
Licensing information is available in the file PDFlib-purchase-order.pdf,
and on our Web site www.pdflib.com.



Please contact us if you are interested in obtaining a commercial
PDFlib license:

PDFlib GmbH
Licensing Department
Franziska-Bilek-Weg 9, 80339 Munich, Germany
fax +49/89/452 33 84-99

License inquiries: sales@pdflib.com

Support for PDFlib licensees: support@pdflib.com


Technical inquiries if you have not licensed PDFlib:
mailing list and archives at groups.yahoo.com/group/pdflib

Copyright (c) 1997-2010 PDFlib GmbH and Thomas Merz.  All rights reserved.
PDFlib and the PDFlib logo are registered trademarks of PDFlib GmbH.
