/* $Id: starter_pdfx.cpp,v 1.5 2006/10/01 19:18:32 rjs Exp $
 *
 * PDF/X starter:
 * Create PDF/X-compliant output
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7
 * required data: font file, image file, ICC profile
 *                (see www.pdflib.com for ICC profiles)
 */


#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	/* This is where the data files are. Adjust as necessary.*/
	string searchpath = "../data";

	PDFlib p;
	string imagefile = "nesrin.jpg";
	int font, image, spot, icc;
	char optlist[256];

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	if (p.begin_document("starter_pdfx.pdf", "pdfx=PDF/X-3:2002") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_pdfx");

	/*
	 * You can use one of the Standard output intents (e.g. for SWOP
	 * printing) which do not require an ICC profile:

	p.load_iccprofile("CGATS TR 001", "usage=outputintent");

	 * However, if you use ICC or Lab color you must load an ICC
	 * profile as output intent:
	 */
	if (p.load_iccprofile("ISOcoated.icc", "usage=outputintent") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl;
	    cerr << "Please install the ICC profile package from " <<
		"www.pdflib.com to run the PDF/X starter sample." << endl;
	    return(2);
	}

	p.begin_page_ext(595, 842, "");

	/* Font embedding is required for PDF/X */
	font = p.load_font("LuciduxSans-Oblique", "winansi", "embedding");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}
	p.setfont(font, 24);

	spot = p.makespotcolor("PANTONE 123 C");
	p.setcolor("fill", "spot", spot, 1.0, 0.0, 0.0);
	p.fit_textline("PDF/X-3:2002 starter", 50, 700, "");

	/* The RGB image below needs an ICC profile; we use sRGB. */
	icc = p.load_iccprofile("sRGB", "");
	sprintf(optlist, "iccprofile=%d", icc);
	image = p.load_image("auto", imagefile, optlist);

	if (image == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	p.fit_image(image, 0.0, 0.0, "scale=0.5");
	p.end_page_ext("");
	p.end_document("");
    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred:" << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
