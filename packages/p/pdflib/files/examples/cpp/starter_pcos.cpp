/* $Id: starter_pcos.cpp,v 1.3.2.2 2007/02/16 09:51:58 stm Exp $
 *
 * pCOS starter:
 * Dump information from an existing PDF document
 *
 * required software: PDFlib+PDI/PPS 7
 * required data: PDF input file
 */


#include <iostream>
#include <iomanip>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	/* This is where the data files are. Adjust as necessary. */
	string searchpath = "../data";

	PDFlib p;
	string pdfinput = "TET-datasheet.pdf";

	string	docoptlist = "requiredmode=minimum";
	int	count, pcosmode;
	int	i, doc;
	string	objtype;

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	/* We do not create any output document, so no call to
	 * begin_document() is required.
	 */

	/* Open the input document */
	if ((doc = p.open_pdi_document(pdfinput, docoptlist)) == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl;
	    return 2;
	}

	/* --------- general information (always available) */

	pcosmode = (int) p.pcos_get_number(doc, "pcosmode");

	cout << "   File name: " <<
	    p.pcos_get_string(doc,"filename") << endl;

	cout << " PDF version: " <<
	    p.pcos_get_number(doc, "pdfversion")/10 << endl;

	cout << "  Encryption: " <<
	    p.pcos_get_string(doc, "encrypt/description") << endl;

	cout << "   Master pw: " <<
	    ((p.pcos_get_number(doc, "encrypt/master") != 0)
	    ? "yes":"no") << endl;

	cout << "     User pw: " <<
	    ((p.pcos_get_number(doc, "encrypt/user") != 0)
	    ? "yes" : "no") << endl;

	cout << "Text copying: " <<
	    ((p.pcos_get_number(doc, "encrypt/nocopy") != 0)
	    ? "no":"yes") << endl;

	cout << "  Linearized: " <<
	    ((p.pcos_get_number(doc, "linearized") != 0)
	    ? "yes" : "no") << endl;

	cout << "      Tagged: " <<
	    ((p.pcos_get_number(doc, "tagged") != 0) ? "yes" : "no") << endl;

	if (pcosmode == 0) {
	    cout << "Minimum mode: no more information available" << endl;
	    return(0);
	}
	cout << endl;

	/* --------- more details (requires at least user password) */
	cout << "No. of pages: " <<
	    (int) p.pcos_get_number(doc, "length:pages") << endl;

	cout << " Page 1 size: width=" << fixed << setprecision(3) <<
	     p.pcos_get_number(doc, "pages[0]/width") << ", height=" <<
	     p.pcos_get_number(doc, "pages[0]/height") << endl;
	/* reset formatting to default */
	cout << resetiosflags(ios::floatfield) << setprecision(6);

	count = (int) p.pcos_get_number(doc, "length:fonts");
	cout << "No. of fonts: " <<  count << endl;

	for (i=0; i < count; i++) {
	    char fonts[256];

	    sprintf(fonts, "fonts[%d]/embedded", i);
	    if (p.pcos_get_number(doc, fonts) != 0)
		cout << "embedded ";
	    else
		cout << "unembedded ";

	    sprintf(fonts, "fonts[%d]/type", i);
	    cout << p.pcos_get_string(doc, fonts) << " font ";
	    sprintf(fonts, "fonts[%d]/name", i);
	    cout << p.pcos_get_string(doc, fonts) << endl;
	}

	cout << "" << endl;

	if (pcosmode == 1) {
	    cout << "Restricted mode: no more information available" << endl;
	    return(0);
	}

	/* ----- document info keys and XMP metadata (requires master pw) */

	count = (int) p.pcos_get_number(doc, "length:/Info");

	for (i=0; i < count; i++) {
	    char info[256];
	    string key;

	    sprintf(info, "type:/Info[%d]", i);
	    objtype = p.pcos_get_string(doc, info);

	    sprintf(info, "/Info[%d].key", i);
	    key = p.pcos_get_string(doc, info);
	    cout.width(12);
	    cout << key << ": ";

	    /* Info entries can be stored as string or name objects */
	    if (objtype == "name" || objtype == "string") {
		sprintf(info, "/Info[%d]", i);
		cout << "'" + p.pcos_get_string(doc, info) << "'" << endl;
	    } else {
		sprintf(info, "type:/Info[%d]", i);
		cout << "(" + p.pcos_get_string(doc,info) << " object)" << endl;
	    }
	}
	cout << endl << "XMP meta data: ";

	objtype = p.pcos_get_string(doc, "type:/Root/Metadata");
	if (objtype == "stream") {
	    const unsigned char *contents;
	    int len;

	    contents = p.pcos_get_stream(doc, &len, "", "/Root/Metadata");
	    cout << len << " bytes ";
	    cout << "";
	} else {
	    cout << "not present";
	}
	cout << endl;

	p.close_pdi_document(doc);

    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred: " << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
