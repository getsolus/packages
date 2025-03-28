// $Id: starter_basic.cpp,v 1.3.2.1 2008/03/07 11:06:26 stm Exp $
//
// Basic starter:
// Create some simple text, vector graphics and image output
// 
// required software: PDFlib Lite/PDFlib/PDFlib+PDI/PPS 7
// required data: none

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	/*  This is where the data files are. Adjust as necessary. */
	string searchpath = "../data";

	PDFlib p;
	string imagefile = "nesrin.jpg";
	int font, image;

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	p.set_parameter("SearchPath", searchpath);

	if (p.begin_document("starter_basic.pdf", "") == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_basic");

	/*  We load the image before the first page, and use it
	    on all pages
	 */
	image = p.load_image("auto", imagefile, "");

	if (image == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return 2;
	}

	/*  Page 1 */
	p.begin_page_ext(595, 842, "");

	/*  For PDFlib Lite: change "unicode" to "winansi" */
	font = p.load_font("Helvetica-Bold", "winansi", "");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}

	p.setfont(font, 24);

	p.set_text_pos(50, 700);
	p.show("Hello world!");

	p.fit_image(image, 0.0, 0.0, "scale=0.25");

	p.end_page_ext("");

	/*  Page 2 */
	p.begin_page_ext(595, 842, "");

	/*  red rectangle */
	p.setcolor("fill", "rgb", 1.0, 0.0, 0.0, 0.0);
	p.rect(200, 200, 250, 150);
	p.fill();

	/*  blue circle */
	p.setcolor("fill", "rgb", 0.0, 0.0, 1.0, 0.0);
	p.arc(400, 600, 100, 0, 360);
	p.fill();

	/*  thick gray line */
	p.setcolor("stroke", "gray", 0.5, 0.0, 0.0, 0.0);
	p.setlinewidth(10);
	p.moveto(100, 500);
	p.lineto(300, 700);
	p.stroke();

	/*  Using the same image handle means the data will be copied
	    to the PDF only once, which saves space.
	 */	
	p.fit_image(image, 150.0, 25.0, "scale=0.25");
	p.end_page_ext("");

	/*  Page 3 */
	p.begin_page_ext(595, 842, "");

	/*  Fit the image to a box of predefined size (without distortion) */
	string optlist("boxsize={400 400} position={center} fitmethod=meet");

	p.fit_image(image, 100, 200, optlist);

	p.end_page_ext("");

	p.close_image(image);
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
