// $Id: hello.cpp,v 1.22 2006/10/01 19:55:41 rjs Exp $
//
// PDFlib client: hello example in C++
//

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	int font;
	PDFlib p;

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	// This line is required to avoid problems on Japanese systems
	p.set_parameter("hypertextencoding", "host");

	if (p.begin_document("hello.pdf", "") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl;
	    return 2;
	}

	p.set_info("Creator", "hello.cpp");
	p.set_info("Author", "Thomas Merz");
	p.set_info("Title", "Hello, world (C++)!");

	p.begin_page_ext(a4_width, a4_height, "");

	// Change "host" encoding to "winansi" or whatever you need!
	font = p.load_font("Helvetica-Bold", "host", "");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}
	p.setfont(font, 24);
	p.set_text_pos(50, 700);
	p.show("Hello, world!");
	p.continue_text("(says C++)");
	p.end_page_ext("");

	p.end_document("");
    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred in hello sample: " << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
