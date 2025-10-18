// $Id: chartab.cpp,v 1.17 2006/10/01 19:18:32 rjs Exp $
//
// PDFlib client: chartab example in C++
//

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    /* change these as required */
    const char *fontname = "LuciduxSans-Oblique";

    /* This is where font/image/PDF input files live. Adjust as necessary. */
    const char *searchpath = "../data";

    /* list of encodings to use */
    const char *encodings[] = { "iso8859-1", "iso8859-2", "iso8859-15" };

    /* whether or not to embed the font */
    int embed = 1;

    char buf[256];
    double x, y;
    int row, col, font, page;

    static const int ENCODINGS = 3;
    static const double FONTSIZE	= 16;
    static const double TOP		= 700;
    static const double LEFT		= 50;
    static const double YINCR		= 2*FONTSIZE;
    static const double XINCR		= 2*FONTSIZE;

    try {
	PDFlib p;

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	// This line is required to avoid problems on Japanese systems
	p.set_parameter("hypertextencoding", "host");

	if (p.begin_document("chartab.pdf",
		"destination {type fitwindow page 1}") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl;
	    return(2);
	}

	p.set_info("Creator", "chartab.c");
	p.set_info("Author", "Thomas Merz");
	p.set_info("Title", "Character table (C++)");

	/* loop over all encodings */
	for (page = 0; page < ENCODINGS; page++) {
	    p.begin_page_ext(a4_width, a4_height, "");  /* start a new page */

	    /* print the heading and generate the bookmark */

	    // Change "host" encoding to "winansi" or whatever you need!
	    font = p.load_font("Helvetica", "host", "");
	    if (font == -1) {
		cerr << "Error: " << p.get_errmsg() << endl; return(2);
	    }
	    p.setfont(font, FONTSIZE);

	    sprintf(buf, "%s (%s) %sembedded",
		fontname, encodings[page], embed ? "" : "not ");

	    p.show_xy(buf, LEFT - XINCR, TOP + 3 * YINCR);
	    p.create_bookmark(buf, "");

	    /* print the row and column captions */
	    p.setfont(font, 2 * FONTSIZE/3);

	    for (row = 0; row < 16; row++) {
		sprintf(buf, "x%X", row);
		p.show_xy(buf, LEFT + row*XINCR, TOP + YINCR);

		sprintf(buf, "%Xx", row);
		p.show_xy(buf, LEFT - XINCR, TOP - row * YINCR);
	    }

	    /* print the character table */
	    font = p.load_font(fontname, encodings[page],
		embed ? "embedding": "");
	    if (font == -1) {
		cerr << "Error: " << p.get_errmsg() << endl;
		return(2);
	    }
	    p.setfont(font, FONTSIZE);

	    y = TOP;
	    x = LEFT;

	    for (row = 0; row < 16; row++) {
		for (col = 0; col < 16; col++) {
		    sprintf(buf, "%c", 16*row + col);
		    p.show_xy(buf, x, y);
		    x += XINCR;
		}
		x = LEFT;
		y -= YINCR;
	    }

	    p.end_page_ext("");
	}
	p.end_document("");
    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred in chartab sample: " << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
