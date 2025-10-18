/* $Id: starter_block.c,v 1.3.2.7 2008/05/09 10:12:23 rjs Exp $
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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{

    /* This is where the data files are. Adjust as necessary. */
    const char * searchpath = "../data";

    PDF * p;
    double width, height;
    const char * infile = "boilerplate.pdf";
    int i, page, indoc, blockcount;
    char * optlist;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        PDF_set_parameter(p, "SearchPath", searchpath);

        if (PDF_begin_document(p, "starter_block.pdf", 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_block");

        /* Open a PDF containing blocks */
        indoc = PDF_open_pdi_document(p, infile, 0, "");
        if (indoc == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Open the first page */
        page = PDF_open_pdi_page(p, indoc, 1, "");
        if (page == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        width = PDF_pcos_get_number(p, indoc, "pages[0]/width");
        height = PDF_pcos_get_number(p, indoc, "pages[0]/height");

        PDF_begin_page_ext(p, width, height, "");

        /* Place the imported page on the output page */
        PDF_fit_pdi_page(p, page, 0, 0, "");

	/* Query the number of blocks on the first page */
        blockcount =
        (int) PDF_pcos_get_number(p, indoc, "length:pages[0]/blocks");

        if (blockcount == 0) {
            printf("Error: %s does not contain any PDFlib blocks", infile);
            PDF_delete(p);
            return(2);
        }

        /* Loop over all blocks on the page */
        for (i = 0; i <  blockcount; i++)
        {
            char buf[1024];
            const char * blockname;
            const char * blocktype;

            /* Fetch the name and type of the i-th block on the first page
             * (one of Text/Image/PDF)
             */
            sprintf(buf, "pages[0]/blocks[%d]/Name",i);
            blockname = PDF_pcos_get_string(p, indoc, buf);

            sprintf(buf, "pages[0]/blocks[%d]/Subtype",
                    i);
            blocktype = PDF_pcos_get_string(p, indoc, buf);

            /* Visualize all text blocks */
            if (!strcmp(blocktype, "Text"))
            {
                optlist =
                    "fontname=Helvetica encoding=winansi "
                    "fillcolor={rgb 1 0 0} "
                    "bordercolor={gray 0} linewidth=0.25";

                /* We simply use the blockname as content */
                if (PDF_fill_textblock(p, page, blockname,
                                    blockname, 0, optlist) == -1) {
                    printf("Warning: %s\n", PDF_get_errmsg(p));
                }
            }
        }

        PDF_end_page_ext(p, "");
        PDF_close_pdi_page(p, page);

        PDF_end_document(p, "");
        PDF_close_pdi_document(p, indoc);
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
