/* $Id: starter_block.cpp,v 1.3.2.2 2008/05/09 10:11:52 rjs Exp $
 *
 * Block starter:
 * Import a PDF page containing, and process all blocks. The blocks are
 * retrieved via pCOS, and the block filling functions are used to
 * visualize the blocks on the output page. A real-world application would
 * of course fill the blocks with data retrieved from some external data
 * source.
 *
 * required software: PPS 7 or above
 * required data: input PDF
 */

#include <iostream>
#include <cstring>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	/* This is where the data files are. Adjust as necessary. */
	string searchpath = "../data";

	PDFlib p;
	double width, height;
	string infile = "boilerplate.pdf";
	int i, page, indoc, blockcount;
	char optlist[256];

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	if (p.begin_document("starter_block.pdf", "") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_block");

	/* Open a PDF containing blocks */
	indoc = p.open_pdi_document(infile, "");
	if (indoc == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/* Open the first page */
	page = p.open_pdi_page(indoc, 1, "");
	if (page == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	width = p.pcos_get_number(indoc, "pages[0]/width");
	height = p.pcos_get_number(indoc, "pages[0]/height");

	p.begin_page_ext(width, height, "");

	/* Place the imported page on the output page */
	p.fit_pdi_page(page, 0, 0, "");

	/* Query the number of blocks on the first page */
	blockcount = (int) p.pcos_get_number(indoc,
	    "length:pages[0]/blocks");

	if (blockcount == 0) {
	    cerr << "Error: " << infile << "does not contain any PDFlib blocks";
	    return 2;
	}

	/* Loop over all blocks on the page */
	for (i = 0; i <  blockcount; i++) {
	    string blockname;
	    string blocktype;

	    /* Fetch the name and type of the i-th block on the first page
	     * (one of Text/Image/PDF)
	     */
	    sprintf(optlist, "pages[0]/blocks[%d]/Name", i);
	    blockname = p.pcos_get_string(indoc, optlist);

	    sprintf(optlist, "pages[0]/blocks[%d]/Subtype", i);
	    blocktype = p.pcos_get_string(indoc, optlist);

	    /* Visualize all text blocks */
	    if (blocktype == "Text") {
		strcpy(optlist, "fontname=Helvetica encoding=winansi "
		   "fillcolor={rgb 1 0 0} bordercolor={gray 0} linewidth=0.25");

		/* We simply use the blockname as content */
		if (p.fill_textblock(page, blockname, blockname, optlist) == -1)
		    cerr << "Warning: " << p.get_errmsg() << endl;
	    }
	}

	p.end_page_ext("");
	p.close_pdi_page(page);

	p.end_document("");
	p.close_pdi_document(indoc);
    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred:" << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }

    return 0;
}
