/* $Id: starter_pdfa.cpp,v 1.3 2006/10/01 19:18:32 rjs Exp $
 *
 * PDF/A starter:
 * Create PDF/A-compliant output
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7
 * required data: font file, image file
 */

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	/* This is where the data files are. Adjust as necessary. */
	string searchpath = "../data";

	PDFlib p;
	string imagefile = "nesrin.jpg";

	int font;
	int image;

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	if (p.begin_document("starter_pdfa.pdf", "pdfa=PDF/A-1b:2005") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/*
	 * We use sRGB as output intent since it allows the color
	 * spaces CIELab, ICC-based, grayscale, and RGB.
	 *
	 * If you need CMYK color you must use a CMYK output profile.
	 */

	p.load_iccprofile("sRGB", "usage=outputintent");

	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_pdfa");

	p.begin_page_ext(595, 842, "");

	/* Font embedding is required for PDF/A */
	font = p.load_font("LuciduxSans-Oblique", "winansi", "embedding");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}
	p.setfont(font, 24);

	p.fit_textline("PDF/A-1b:2005 starter", 50, 700, "");

	/* We can use an RGB image since we already supplied an
	 * output intent profile.
	 */
	image = p.load_image("auto", imagefile, "");

	if (image == -1){
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/* Place the image at the bottom of the page */
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
