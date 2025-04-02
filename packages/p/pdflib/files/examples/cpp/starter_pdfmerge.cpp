/* $Id: starter_pdfmerge.cpp,v 1.3.2.1 2007/08/08 15:09:39 rp Exp $
 *
 * PDF merge starter:
 * Merge pages from multiple PDF documents; interactive elements (e.g. 
 * bookmarks) will be dropped.
 *
 * required software: PDFlib+PDI/PPS 7
 * required data: PDF documents
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
	string pdffiles[] =
	{
		"PDFlib-real-world.pdf",
		"PDFlib-datasheet.pdf",
		"TET-datasheet.pdf",
		"PLOP-datasheet.pdf",
		"pCOS-datasheet.pdf"
	};
#define FILECOUNT (sizeof(pdffiles)/sizeof(pdffiles[0]))
	int i;

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	if (p.begin_document("starter_pdfmerge.pdf", "") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}
	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_pdfmerge");

	for (i=0; i < (int)FILECOUNT; i++) {
	    int indoc, endpage, pageno, page; 

	    /* Open the input PDF */
	    indoc = p.open_pdi_document(pdffiles[i], "");
	    if (indoc == -1) {
		cerr << "Error: " << p.get_errmsg() << endl; return 2;
	    }

	    endpage = (int) p.pcos_get_number(indoc, "/Root/Pages/Count");

	    /* Loop over all pages of the input document */
	    for (pageno = 1; pageno <= endpage; pageno++)
	    {
		page = p.open_pdi_page(indoc, pageno, "");
		if (page == -1) {
		    cerr << "Error: " << p.get_errmsg() << endl;
		    continue;
		}
		/* Dummy page size; will be adjusted later */
		p.begin_page_ext(10, 10, "");

		/* Create a bookmark with the file name */
		if (pageno == 1)
		    p.create_bookmark(pdffiles[i], "");

		/* Place the imported page on the output page, and
		 * adjust the page size
		 */
		p.fit_pdi_page(page, 0, 0, "adjustpage");
		p.close_pdi_page(page);

		p.end_page_ext("");
	    }
	    p.close_pdi_document(indoc);
	}
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
