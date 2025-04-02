/* $Id: starter_table.c,v 1.4.2.5 2007/11/15 15:09:44 rjs Exp $
 *
 * Table starter:
 * Create table which may span multiple pages
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7
 * required data: image file (dummy text created within the program)
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

    const char * imagefile = "nesrin.jpg";

    int row, col, font, image, tf=-1, tbl=-1;
    int rowmax=50, colmax=5;

    double llx= 50, lly=50, urx=550, ury=800;
    const char * headertext = "Table header (centered across all columns)";
    const char * result;
    char optlist[1024];

    /* Dummy text for filling a cell with multi-line Textflow */
    const char * tf_text =
"Lorem ipsum dolor sit amet, consectetur adi&shy;pi&shy;sicing elit, \
sed do eius&shy;mod tempor incidi&shy;dunt ut labore et dolore magna \
ali&shy;qua. Ut enim ad minim ve&shy;niam, quis nostrud exer&shy;citation \
ull&shy;amco la&shy;bo&shy;ris nisi ut ali&shy;quip ex ea commodo \
con&shy;sequat. \
Duis aute irure dolor in repre&shy;henderit in voluptate velit esse \
cillum dolore \
eu fugiat nulla pari&shy;atur. Excep&shy;teur sint occae&shy;cat \
cupi&shy;datat \
non proident, sunt in culpa qui officia dese&shy;runt mollit anim id est \
laborum. ";

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        PDF_set_parameter(p, "SearchPath", searchpath);

        if (PDF_begin_document(p, "starter_table.pdf", 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_table");

        /* -------------------- Add table cells -------------------- */

        /* ---------- Row 1: table header (spans all columns) */
        row = 1; col = 1;
        font = PDF_load_font(p, "Times-Bold", 0, "winansi", "");

        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        sprintf(optlist,
            "fittextline={position=center font=%d fontsize=14} colspan=%d",
            font, colmax);

        tbl = PDF_add_table_cell(p, tbl, col, row, headertext, 0, optlist);

        if (tbl == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* ---------- Row 2: various kinds of content */
        /* ----- Simple text cell */
        row++; col=1;

        sprintf(optlist, "fittextline={font=%d fontsize=10 orientate=west}",
                font);

        tbl = PDF_add_table_cell(p, tbl, col, row, "vertical line", 0, optlist);

        if (tbl == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }
        /* ----- Colorized background */
        col++;

        sprintf(optlist, "fittextline={font=%d fontsize=10} "
            "matchbox={fillcolor={rgb 0.9 0.5 0}}", font);

        tbl = PDF_add_table_cell(p, tbl, col, row, "some color", 0, optlist);

        if (tbl == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }
        /* ----- Multi-line text with Textflow */
        col++;
        font = PDF_load_font(p, "Times-Roman", 0, "winansi", "");

        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        sprintf(optlist,
            "charref fontname=Times-Roman encoding=winansi fontsize=8");

        tf = PDF_add_textflow(p, tf, tf_text, 0, optlist);
        if (tf == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        sprintf(optlist, "margin=2 textflow=%d", tf);

        tbl = PDF_add_table_cell(p, tbl, col, row, "", 0, optlist);

        if (tbl == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }
        /* ----- Rotated image */
        col++;

        image = PDF_load_image(p, "auto", imagefile, 0, "");

        if (image == -1) {
            printf("Couldn't load image: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        sprintf(optlist, "image=%d fitimage={orientate=west}", image);

        tbl = PDF_add_table_cell(p, tbl, col, row, "", 0, optlist);

        if (tbl == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }
        /* ----- Diagonal stamp */
        col++;

        sprintf(optlist,
            "fittextline={font=%d fontsize=10 stamp=ll2ur}", font);

        tbl = PDF_add_table_cell(p, tbl, col, row, "entry void", 0, optlist);

        if (tbl == -1) {
            printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }
        /* ---------- Fill row 3 and above with their numbers */
        for (row++; row <= rowmax; row++)
        {
            for (col = 1; col <= colmax; col++)
            {
                char num[1024];

                sprintf(num, "Col %d/Row %d", col, row);
                sprintf(optlist,
                    "colwidth=20%% fittextline={font=%d fontsize=10}", font);
                tbl = PDF_add_table_cell(p, tbl, col, row, num, 0, optlist);

                if (tbl == -1) {
                    printf("Error: adding cell: %s\n", PDF_get_errmsg(p));
                    PDF_delete(p);
                    return(2);
                }
            }
        }

        /* ---------- Place the table on one or more pages ---------- */

        /*
         * Loop until all of the table is placed; create new pages
         * as long as more table instances need to be placed.
         */
        do {
            PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");

            /* Shade every other row; draw lines for all table cells.
             * Add "showcells showborder" to visualize cell borders
             */
            sprintf(optlist, "header=1 fill={{area=rowodd "
                "fillcolor={gray 0.9}}} stroke={{line=other}} ");

            /* Place the table instance */
            result = PDF_fit_table(p, tbl, llx, lly, urx, ury, optlist);

            if (!strcmp(result, "_error"))
            {
                printf("Could't place table: %s\n", PDF_get_errmsg(p));
                PDF_delete(p);
                return(2);
            }

            PDF_end_page_ext(p, "");

        } while (!strcmp(result, "_boxfull"));

        /* Check the result; "_stop" means all is ok. */
        if (strcmp(result, "_stop"))
        {
            if (!strcmp(result, "_error"))
            {
                printf("Error when placing table: %s\n", PDF_get_errmsg(p));
                PDF_delete(p);
                return(2);
            }
            else
            {
                /* Any other return value is a user exit caused by
                 * the "return" option; this requires dedicated code to
                 * deal with.
                 */
                printf("User return found in Textflow\n");
                PDF_delete(p);
                return(2);
            }
        }

        /* This will also delete Textflow handles used in the table */
        PDF_delete_table(p, tbl, "");

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
