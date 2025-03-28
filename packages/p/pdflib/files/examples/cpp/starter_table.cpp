/* $Id: starter_table.cpp,v 1.5.2.2 2007/01/14 23:18:26 rjs Exp $
 *
 * Table starter:
 * Create table which may span multiple pages
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7
 * required data: image file (dummy text created within the program)
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

	string imagefile = "nesrin.jpg";

	int row, col, font, image, tf=-1, tbl=-1;
	int rowmax=50, colmax=5;
	PDFlib p;
	double llx= 50, lly=50, urx=550, ury=800;
	string headertext = "Table header (centered across all columns)";
	string result;
	char optlist[256];

	/* Dummy text for filling a cell with multi-line Textflow */
	string tf_text = 
"Lorem ipsum dolor sit amet, consectetur adi&shy;pi&shy;sicing elit, \
sed do eius&shy;mod tempor incidi&shy;dunt ut labore et dolore magna \
ali&shy;qua. Ut enim ad minim ve&shy;niam, quis nostrud exer&shy;citation \
ull&shy;amco la&shy;bo&shy;ris nisi ut ali&shy;quip ex ea commodo \
con&shy;sequat. Duis aute irure dolor in repre&shy;henderit in voluptate \
velit esse cillum dolore eu fugiat nulla pari&shy;atur. Excep&shy;teur \
sint occae&shy;cat cupi&shy;datat non proident, sunt in culpa qui officia \
dese&shy;runt mollit anim id est laborum. ";

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	if (p.begin_document("starter_table.pdf", "") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}
	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_table");

	/* -------------------- Add table cells -------------------- */

	/* ---------- Row 1: table header (spans all columns) */
	row = 1; col = 1;
	font = p.load_font("Times-Bold", "winansi", "");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}

	sprintf(optlist,"fittextline={position=center font=%d fontsize=14} "
			 "colspan=%d", font, colmax);

	tbl = p.add_table_cell(tbl, col, row, headertext, optlist);

	/* ---------- Row 2: various kinds of content */
	/* ----- Simple text cell */
	row++; col=1;

	sprintf(optlist, "fittextline={font=%d fontsize=10 orientate=west}", 
			 font);

	tbl = p.add_table_cell(tbl, col, row, "vertical line", optlist);
	if (tbl == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/* ----- Colorized background */
	col++;

	sprintf(optlist, "fittextline={font=%d fontsize=10} "
			 "matchbox={fillcolor={rgb 0.9 0.5 0}}", font);

	tbl = p.add_table_cell(tbl, col, row, "some color", optlist); 
	/* ----- Multi-line text with Textflow */
	col++;
	font = p.load_font("Times-Roman", "winansi", "");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}

	sprintf(optlist, 
	    "charref fontname=Times-Roman encoding=winansi fontsize=8 ");

	tf = p.add_textflow(tf, tf_text, optlist);
	if (tf == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}

	sprintf(optlist, 
	    "marginleft=2 marginright=2 margintop=2 marginbottom=2 " 
	    "textflow=%d",  tf);

	tbl = p.add_table_cell(tbl, col, row, "", optlist);
	if (tbl == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/* ----- Rotated image */
	col++;

	image = p.load_image("auto", imagefile, "");
	if (image == -1) {
	    cerr << "Couldn't load image: " << p.get_errmsg() << endl; return 2;
	}

	sprintf(optlist, "image=%d fitimage={orientate=west}", image);

	tbl = p.add_table_cell(tbl, col, row, "", optlist);
	if (tbl == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/* ----- Diagonal stamp */
	col++;

	sprintf(optlist, "fittextline={font=%d  fontsize=10 stamp=ll2ur}", 
			 font);

	tbl = p.add_table_cell(tbl, col, row, "entry void", optlist);
	if (tbl == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/* ---------- Fill row 3 and above with their numbers */
	for (row++; row <= rowmax; row++) {
	    for (col = 1; col <= colmax; col++) {
		char num[80];

		sprintf(num, "Col %d/Row %d", col, row);
		sprintf(optlist,
		    "colwidth=20%% fittextline={font=%d fontsize=10}", font);
		tbl = p.add_table_cell(tbl, col, row, num, optlist);
	    }
	}

	/* ---------- Place the table on one or more pages ---------- */

	/*
	 * Loop until all of the table is placed; create new pages
	 * as long as more table instances need to be placed.
	 */
	do {
	    p.begin_page_ext(0, 0, "width=a4.width height=a4.height");

	    /* Shade every other row; draw lines for all table cells.
	     * Add "showcells showborder" to visualize cell borders 
	     */
	    sprintf(optlist,
	    "header=1 fill={{area=rowodd fillcolor={gray 0.9}}} " 
	    "stroke={{line=other}} ");

	    /* Place the table instance */
	    result = p.fit_table(tbl, llx, lly, urx, ury, optlist);
	    if (result == "_error") {
		cerr << "Couldn't place table: " << p.get_errmsg()
		    << endl; return 2;
	    }

	    p.end_page_ext("");

	} while (result == "_boxfull");

	/* Check the result; "_stop" means all is ok. */
	if (result != "_stop") {
	    if (result == "_error") {
		cerr << "Error when placing table: " << p.get_errmsg()
		    << endl; return 2;
	    } else {
		/* Any other return value is a user exit caused by
		 * the "return" option; this requires dedicated code to
		 * deal with.
		 */
		cerr << "User return found in Textflow" << endl; return 2;
	    }
	}
	/* This will also delete Textflow handles used in the table */
	p.delete_table(tbl, "");

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
