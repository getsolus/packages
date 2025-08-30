// $Id: quickreference.cpp,v 1.29 2006/10/01 19:18:32 rjs Exp $
//
// PDFlib+PDI client: mini imposition demo
//

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	PDFlib *p;
	int manual, page;
	int font, row, col;
	const int maxrow = 2;
	const int maxcol = 2;
	char optlist[128];
	int endpage;
	const double width = 500, height = 770;
	int pageno;
	const string infile = "reference.pdf";
	/* This is where font/image/PDF input files live. Adjust as necessary.*/
	const string searchpath = "../data";

	p = new PDFlib();

	//  This means we must check return values of load_font() etc.
	p->set_parameter("errorpolicy", "return");

	p->set_parameter("SearchPath", searchpath);

	// This line is required to avoid problems on Japanese systems
	p->set_parameter("hypertextencoding", "host");

	if (p->begin_document("quickreference.pdf", "") == -1) {
	    cerr << "Error: " << p->get_errmsg() << endl; return 2;
	}

	p->set_info("Creator", "quickreference.cpp");
	p->set_info("Author", "Thomas Merz");
	p->set_info("Title", "mini imposition demo (C++)");

	manual = p->open_pdi_document(infile, "");
	if (manual == -1) {
	    cerr << "Error: " << p->get_errmsg() << endl; return 2;
	}

	row = 0;
	col = 0;

	p->set_parameter("topdown", "true");

	endpage = (int) p->pcos_get_number(manual, "length:pages");

	for (pageno = 1; pageno <= endpage; pageno++) {
	    if (row == 0 && col == 0) {
		p->begin_page_ext(width, height, "");
		font = p->load_font("Helvetica-Bold", "host", "");
		if (font == -1) {
		    cerr << "Error: " << p->get_errmsg() << endl; return(2);
		}
		p->setfont(font, 18);
		p->set_text_pos(24, 24);
		p->show("PDFlib Quick Reference");
	    }

	    page = p->open_pdi_page(manual, pageno, "");

	    if (page == -1) {
		cerr << "Error: " << p->get_errmsg() << endl; return 2;
	    }

	    sprintf(optlist, "scale %f", 1.0/maxrow);
	    p->fit_pdi_page(page, width/maxcol*col,
			(row + 1) *  height/maxrow, optlist);
	    p->close_pdi_page(page);

	    col++;
	    if (col == maxcol) {
		col = 0;
		row++;
	    }
	    if (row == maxrow) {
		row = 0;
		p->end_page_ext("");
	    }
	}

	// finish the last partial page
	if (row != 0 || col != 0)
	    p->end_page_ext("");

	p->end_document("");
	p->close_pdi_document(manual);

    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred in quickreference sample: " << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
