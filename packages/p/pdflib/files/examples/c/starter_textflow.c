/* $Id: starter_textflow.c,v 1.4.2.5 2007/11/15 15:09:44 rjs Exp $
 *
 * Textflow starter:
 * Create multi-column text output which may span multiple pages
 *
 * required software: PDFlib/PDFlib+PDI/PPS 7 or above
 * required data: none
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{
    PDF * p;

    int i, tf = -1;
    const char * result;
    double llx1= 50, lly1=50, urx1=250, ury1=800;
    double llx2=300, lly2=50, urx2=500, ury2=800;

    /* Repeat the dummy text to produce more contents */
    int count = 50;

    const char * optlist1 =
        "fontname=Helvetica fontsize=10.5 encoding=winansi "
        "fillcolor={gray 0} alignment=justify";

    const char * optlist2 =
        "fontname=Helvetica-Bold fontsize=14 encoding=winansi "
        "fillcolor={rgb 1 0 0} charref";

    /* Dummy text for filling the columns. Soft hyphens are marked with
     * the character reference "&shy;" (character references are
     * enabled by the charref option).
     */
    const char * text=
"Lorem ipsum dolor sit amet, consectetur adi&shy;pi&shy;sicing elit, \
sed do eius&shy;mod tempor incidi&shy;dunt ut labore et dolore magna \
ali&shy;qua. Ut enim ad minim ve&shy;niam, quis nostrud exer&shy;citation \
ull&shy;amco la&shy;bo&shy;ris nisi ut ali&shy;quip ex ea commodo \
con&shy;sequat. \
Duis aute irure dolor in repre&shy;henderit in voluptate velit esse cillum \
dolore \
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

        if (PDF_begin_document(p, "starter_textflow.pdf", 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_textflow");

        /* Create some amount of dummy text and feed it to a Textflow
         * object with alternating options.
         */
        for (i=1; i<=count; i++)
        {
            char num[1024];

            sprintf(num, "%d ", i);
            tf = PDF_add_textflow(p, tf, num, 0, optlist2);
            if (tf == -1) {
                printf("Error: %s\n", PDF_get_errmsg(p));
                PDF_delete(p);
                return(2);
            }

            tf = PDF_add_textflow(p, tf, text, 0, optlist1);
            if (tf == -1) {
                printf("Error: %s\n", PDF_get_errmsg(p));
                PDF_delete(p);
                return(2);
            }
        }

        /* Loop until all of the text is placed; create new pages
         * as long as more text needs to be placed. Two columns will
         * be created on all pages.
         */
        do
        {
            char optlist[1024];
            /* Add "showborder to visualize the fitbox borders */
            sprintf(optlist, "verticalalign=justify linespreadlimit=120%% ");

            PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");

            /* Fill the first column */
            result = PDF_fit_textflow(p, tf, llx1, lly1, urx1, ury1, optlist);

            /* Fill the second column if we have more text*/
            if (strcmp(result, "_stop"))
                result = PDF_fit_textflow(p, tf, llx2, lly2, urx2,ury2,optlist);

            PDF_end_page_ext(p, "");

            /* "_boxfull" means we must continue because there is more text;
             * "_nextpage" is interpreted as "start new column"
             */
        } while (!strcmp(result, "_boxfull") || !strcmp(result, "_nextpage"));

        /* Check for errors */
        if (strcmp(result, "_stop"))
        {
            /* "_boxempty" happens if the box is very small and doesn't
             * hold any text at all.
             */
            if (!strcmp(result, "_boxempty")) {
                printf("Error: Textflow box too small");
                PDF_delete(p);
                return(2);
            }
            else
            {
                /* Any other return value is a user exit caused by
                 * the "return" option; this requires dedicated code to
                 * deal with.
                 */
                printf("User return '%s' found in Textflow", result);
                PDF_delete(p);
                return(2);
            }
        }

        PDF_delete_textflow(p, tf);

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
