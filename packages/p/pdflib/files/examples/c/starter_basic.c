/* $Id: starter_basic.c,v 1.3.2.4 2007/11/15 15:09:44 rjs Exp $
 *
 * Basic starter:
 * Create some simple text, vector graphics and image output
 *
 * required software: PDFlib Lite/PDFlib/PDFlib+PDI/PPS 7
 * required data: none
 */

#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{

    /* This is where the data files are. Adjust as necessary. */
    const char* searchpath = "../data";

    PDF * p;
    const char* imagefile = "nesrin.jpg";
    char* optlist;
    int font, image;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        PDF_set_parameter(p, "SearchPath", searchpath);

        if (PDF_begin_document(p, "starter_basic.pdf", 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_basic");

        /* We load the image before the first page, and use it
         * on all pages
         */
        image = PDF_load_image(p, "auto", imagefile, 0, "");

        if (image == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Page 1 */
        PDF_begin_page_ext(p, 595, 842, "");

        font = PDF_load_font(p, "Helvetica-Bold", 0, "winansi", "");

        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_setfont(p, font, 24);

        PDF_set_text_pos(p, 50, 700);
        PDF_show(p, "Hello world!");

        PDF_fit_image(p, image, (float) 0.0, (float) 0.0, "scale=0.25");

        PDF_end_page_ext(p, "");

        /* Page 2 */
        PDF_begin_page_ext(p, 595, 842, "");

        /* red rectangle */
        PDF_setcolor(p, "fill", "rgb", 1.0, 0.0, 0.0, 0.0);
        PDF_rect(p, 200, 200, 250, 150);
        PDF_fill(p);

        /* blue circle */
        PDF_setcolor(p, "fill", "rgb", 0.0, 0.0, 1.0, 0.0);
        PDF_arc(p, 400, 600, 100, 0, 360);
        PDF_fill(p);

        /* thick gray line */
        PDF_setcolor(p, "stroke", "gray", 0.5, 0.0, 0.0, 0.0);
        PDF_setlinewidth(p, 10);
        PDF_moveto(p, 100, 500);
        PDF_lineto(p, 300, 700);
        PDF_stroke(p);

        /* Using the same image handle means the data will be copied
         * to the PDF only once, which saves space.
         */
        PDF_fit_image(p, image, 150.0, 25.0, "scale=0.25");
        PDF_end_page_ext(p, "");

        /* Page 3 */
        PDF_begin_page_ext(p, 595, 842, "");

        /* Fit the image to a box of predefined size (without distortion) */
        optlist =
        "boxsize={400 400} position={center} fitmethod=meet";

        PDF_fit_image(p, image, 100, 200, optlist);

        PDF_end_page_ext(p, "");

        PDF_close_image(p, image);
        PDF_end_document(p, "");
    }

    PDF_CATCH(p) {
        printf("PDFlib exception occurred:\n");
        printf("[%d] %s: %s\n",
            PDF_get_errnum(p), PDF_get_apiname(p), PDF_get_errmsg(p));
        PDF_delete(p);
        return(2);
    }

    PDF_delete(p);

    return 0;
}
