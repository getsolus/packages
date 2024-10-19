/* $Id: starter_webform.cpp,v 1.3 2006/10/01 19:18:32 rjs Exp $
 *
 * Webform starter:
 * create a linearized PDF (for fast delivery over the Web, also known
 * as "fast Web view") which is encrypted and contains some form fields.
 * A few lines of JavaScript are inserted as "page open" action to
 * automatically populate the date field with the current date.
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7
 * required data: none
 */

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	PDFlib p;
	char optlist[256];
	int font, action;
	double llx=150, lly=550, urx=350, ury=575;

	/* JavaScript for automatically filling the date into a form field */
	char js[256] =
	    "var d = util.printd(\"mm/dd/yyyy\", new Date());" 
	    "var date = this.getField(\"date\");" 
	    "date.value = d;";

	sprintf(optlist,
	    "linearize masterpassword=pdflib permissions={nomodify}");

	//  This means we must check return values of load_font() etc.
	p.set_parameter("errorpolicy", "return");

	if (p.begin_document("starter_webform.pdf", optlist) == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl;
	    return 2;
	}

	p.set_info("Creator", "PDFlib starter sample");
	p.set_info("Title", "starter_webform");

	sprintf(optlist, "script={ %s }", js);
	action = p.create_action("JavaScript", optlist);

	sprintf(optlist, "action={open=%d}", action);
	p.begin_page_ext(595, 842, optlist);

	font = p.load_font("Helvetica", "winansi", "");
	if (font == -1) {
	    cerr << "Error: " << p.get_errmsg() << endl; return(2);
	}
	p.setfont(font, 24);

	p.fit_textline("Date: ", 125, lly+5, "position={right bottom}");

	/* The tooltip will be used as rollover text for the field */
	sprintf(optlist,
	    "tooltip={Date (will be filled automatically)} "
	    "bordercolor={gray 0} font=%d", font);
	p.create_field(llx, lly, urx, ury, "date", "textfield", optlist);

	lly-=100; ury-=100;
	p.fit_textline("Name: ", 125, lly+5, "position={right bottom}");

	sprintf(optlist,
	    "tooltip={Enter your name here} " 
	    "bordercolor={gray 0} font=%d", font);
	p.create_field(llx, lly, urx, ury, "name", "textfield", optlist);

	p.end_page_ext("");

	p.end_document("");
    }

    catch (PDFlib::Exception &ex) {
	cerr << "PDFlib exception occurred: " << endl;
	cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
	    << ": " << ex.get_errmsg() << endl;
	return 2;
    }
    return 0;
}
