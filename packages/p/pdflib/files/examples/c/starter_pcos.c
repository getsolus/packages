/* $Id: starter_pcos.c,v 1.4.2.4 2007/11/15 15:09:44 rjs Exp $
 *
 * pCOS starter:
 * Dump information from an existing PDF document
 *
 * required software: PDFlib+PDI/PPS 7
 * required data: PDF input file
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{

    /* This is where the data files are. Adjust as necessary. */
    char * searchpath = "../data";

    PDF *p;
    char * pdfinput = "TET-datasheet.pdf";

    char *      docoptlist = "requiredmode=minimum";
    int count, pcosmode;
    int i, doc;
    const char *        objtype;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p)
    {
        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        PDF_set_parameter(p, "SearchPath", searchpath);

        /* We do not create any output document, so no call to
         * begin_document() is required.
         */

        /* Open the input document */
        if ((doc = PDF_open_pdi_document(p, pdfinput, 0, docoptlist)) == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* --------- general information (always available) */

        pcosmode = (int) PDF_pcos_get_number(p, doc, "pcosmode");

        printf("   File name: %s\n",
            PDF_pcos_get_string(p, doc,"filename"));

        printf(" PDF version: %.1f\n",
            PDF_pcos_get_number(p, doc, "pdfversion")/10);

        printf("  Encryption: %s\n",
            PDF_pcos_get_string(p, doc, "encrypt/description"));

        printf("   Master pw: %s\n",
            ((PDF_pcos_get_number(p, doc, "encrypt/master")!= 0) ? "yes":"no"));

        printf("     User pw: %s\n",
            ((PDF_pcos_get_number(p, doc, "encrypt/user")!= 0) ? "yes" : "no"));

        printf("Text copying: %s\n",
            ((PDF_pcos_get_number(p, doc, "encrypt/nocopy")!= 0) ? "no":"yes"));

        printf("  Linearized: %s\n",
            ((PDF_pcos_get_number(p, doc, "linearized") != 0) ? "yes" : "no"));

        printf("      Tagged: %s\n\n",
            (PDF_pcos_get_number(p, doc, "tagged") != 0) ? "yes" : "no");

        if (pcosmode == 0)
        {
            printf("Minimum mode: no more information available\n\n");
            PDF_delete(p);
            return(0);
        }

        /* --------- more details (requires at least user password) */
        printf("No. of pages: %d\n",
             (int) PDF_pcos_get_number(p, doc, "length:pages"));

        printf(" Page 1 size: width=%.3f, height=%.3f\n",
             PDF_pcos_get_number(p, doc, "pages[0]/width"),
             PDF_pcos_get_number(p, doc, "pages[0]/height"));

        count = (int) PDF_pcos_get_number(p, doc, "length:fonts");
        printf("No. of fonts: %d\n",  count);

        for (i=0; i < count; i++)
        {
            if (PDF_pcos_get_number(p, doc, "fonts[%d]/embedded", i) != 0)
                printf("embedded ");
            else
                printf("unembedded ");

            printf("%s font ",PDF_pcos_get_string(p, doc, "fonts[%d]/type", i));
            printf("%s\n", PDF_pcos_get_string(p, doc, "fonts[%d]/name", i));
        }

        printf("\n");

        if (pcosmode == 1)
        {
            printf("Restricted mode: no more information available");
            PDF_delete(p);
            return(0);
        }

        /* ----- document info keys and XMP metadata (requires master pw) */

        count = (int) PDF_pcos_get_number(p, doc, "length:/Info");

        for (i=0; i < count; i++)
        {
            objtype = PDF_pcos_get_string(p, doc, "type:/Info[%d]",i);
            printf("%12s: ", PDF_pcos_get_string(p, doc, "/Info[%d].key", i));

            /* Info entries can be stored as string or name objects */
            if (!strcmp(objtype, "name") || !strcmp(objtype, "string"))
            {
                printf("'%s'\n", PDF_pcos_get_string(p, doc, "/Info[%d]", i));
            }
            else
            {
                printf("(%s object)\n",
                    PDF_pcos_get_string(p, doc, "type:/Info[%d]", i));
            }
        }

        printf("\nXMP meta data: ");


        objtype = PDF_pcos_get_string(p, doc, "type:/Root/Metadata");
        if (!strcmp(objtype,"stream"))
        {
            const unsigned char * contents;
            int len;

            contents = PDF_pcos_get_stream(p, doc, &len, "", "/Root/Metadata");
            printf("%d bytes ", len);
            printf("\n");
        }
        else
        {
            printf("not present\n");
        }

        PDF_close_pdi_document(p, doc);

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
