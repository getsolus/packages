/* $Id: hellodl.c,v 1.10 2004/04/16 20:01:35 tm Exp $
 *
 * PDFlib client: hello example in C with dynamic DLL loading
 */

#include <stdio.h>
#include <stdlib.h>

#include "pdflibdl.h"

int
main(void)
{
    PDF *p;
    int font;
    PDFlib_api *PDFlib;

    /* load the PDFlib dynamic library and create a new PDFlib object*/
    if ((PDFlib = PDF_new_dl(&p)) == (PDFlib_api *) NULL)
    {
        printf("Couldn't create PDFlib object (DLL not found?)\n");
        return(2);
    }

    PDF_TRY_DL(PDFlib, p) {
	if (PDFlib->PDF_begin_document(p, "hellodl.pdf", 0, "") == -1) {
	    printf("Error: %s\n", PDFlib->PDF_get_errmsg(p));
	    return(2);
	}

	/* This line is required to avoid problems on Japanese systems */
	PDFlib->PDF_set_parameter(p, "hypertextencoding", "host");

	PDFlib->PDF_set_info(p, "Creator", "hello.c");
	PDFlib->PDF_set_info(p, "Author", "Thomas Merz");
	PDFlib->PDF_set_info(p, "Title", "Hello, world (C DLL)!");

	PDFlib->PDF_begin_page_ext(p, a4_width, a4_height, "");

	/* Change "host" encoding to "winansi" or whatever you need! */
	font = PDFlib->PDF_load_font(p, "Helvetica-Bold", 0, "host", "");

	PDFlib->PDF_setfont(p, font, 24);
	PDFlib->PDF_set_text_pos(p, 50, 700);
	PDFlib->PDF_show(p, "Hello, world!");
	PDFlib->PDF_continue_text(p, "(says C DLL)");
	PDFlib->PDF_end_page_ext(p, "");

	PDFlib->PDF_end_document(p, "");
    }

    PDF_CATCH_DL(PDFlib, p) {
        printf("PDFlib exception occurred in hellodl sample:\n");
        printf("[%d] %s: %s\n",
	PDFlib->PDF_get_errnum(p), PDFlib->PDF_get_apiname(p),
	PDFlib->PDF_get_errmsg(p));
	PDF_delete_dl(PDFlib, p);
        return(2);
    }

    /* delete the PDFlib object and unload the library */
    PDF_delete_dl(PDFlib, p);

    return 0;
}
