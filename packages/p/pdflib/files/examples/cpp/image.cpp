// $Id: image.cpp,v 1.22.2.1 2008/03/07 11:06:26 stm Exp $
//
// PDFlib client: image example in C++
//

#include <iostream>
#include <cstdlib>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	PDFlib *p;
	int image;
	char *imagefile = (char *) "nesrin.jpg";
	// This is where font/image/PDF input files live. Adjust as necessary. 
	char *searchpath = (char *) "../data";

	p = new PDFlib();

	//  This means we must check return values of load_font() etc.
	p->set_parameter("errorpolicy", "return");

	p->set_parameter("SearchPath", searchpath);

	// This line is required to avoid problems on Japanese systems
	p->set_parameter("hypertextencoding", "host");

	if (p->begin_document("image.pdf", "") == -1) {
	    cerr << "Error: " << p->get_errmsg() << endl; return 2;
	}

	p->set_info("Creator", "image.cpp");
	p->set_info("Author", "Thomas Merz");
	p->set_info("Title", "image sample (C++)!");

	image = p->load_image("auto", imagefile, "");

	if (image == -1) {
	    cerr << "Error: " << p->get_errmsg() << endl;
	    exit(3);
	}

	// dummy page size, will be adjusted by PDF_fit_image()
	p->begin_page_ext(10, 10, "");
	p->fit_image(image, 0.0, 0.0, "adjustpage");
	p->close_image(image);
	p->end_page_ext("");

	p->end_document("");
    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred in hello sample: " << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
