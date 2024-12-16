/* $Id: starter_pdfa.c,v 1.2.2.4 2007/11/15 15:09:44 rjs Exp $
 *
 * PDF/A starter:
 * Create PDF/A-compliant output
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7
 * required data: font file, image file
 */

#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{
    /* This is where the data files are. Adjust as necessary. */
    const char * searchpath = "../data";

    PDF *p;
    const char * imagefile = "nesrin.jpg";

    int font;
    int image;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        PDF_set_parameter(p, "SearchPath", searchpath);

        /* PDF/A-1a requires Tagged PDF */
        if (PDF_begin_document(p, "starter_pdfa.pdf", 0, "pdfa=PDF/A-1b:2005")
            == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /*
         * We use sRGB as output intent since it allows the color
         * spaces CIELab, ICC-based, grayscale, and RGB.
         *
         * If you need CMYK color you must use a CMYK output profile.
         */

        PDF_load_iccprofile(p, "sRGB", 0, "usage=outputintent");

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_pdfa");

        PDF_begin_page_ext(p, 595, 842, "");

        /* Font embedding is required for PDF/A */
        font = PDF_load_font(p, "LuciduxSans-Oblique", 0, "winansi",
                "embedding");

        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_setfont(p, font, 24);

        PDF_fit_textline(p, "PDF/A-1b:2005 starter", 0, 50, 700, "");

        /* We can use an RGB image since we already supplied an
         * output intent profile.
         */
        image = PDF_load_image(p, "auto", imagefile, 0, "");

        if (image == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Place the image at the bottom of the page */
        PDF_fit_image(p, image, (float) 0.0, (float) 0.0, "scale=0.5");

        PDF_end_page_ext(p, "");

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
