/* $Id: starter_3d.c,v 1.1.2.3 2008/04/30 15:30:07 rjs Exp $
 * 3D Starter:
 * Create a 3D model and load it into a U3D annotation.
 *
 * Define a 3D view and load some 3D data with the view defined. Then create
 * an annotation containing the loaded 3D data with the defined 3D view as the
 * initial view.
 *
 * Acrobat 7.07 or above is required for viewing PDF documents containing a
 * 3D model.
 *
 * Required software: PDFlib/PDFlib+PDI/PPS 7.0.1
 * Required data: U3D data file
 */

#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{
    /* This is where the data files are. Adjust if necessary. */
    const char* searchpath = "../data";
    const char* outfile = "starter_3d.pdf";

    /* Required minimum PDFlib version */
    double requiredversion = 701;
    char *requiredvstr = "7.0.1";

    char buf[1024];
    char *optlist;
    int font, u3dview, u3ddata;
    PDF *p;
    double major, minor, revision;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }


    PDF_TRY(p) {
        PDF_set_parameter(p, "SearchPath", searchpath);

        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        /* Check whether the required minimum PDFlib version is available */
        major = PDF_get_value(p, "major", 0);
        minor = PDF_get_value(p, "minor", 0);
        revision = PDF_get_value(p, "revision", 0);

        if (major*100 + minor*10 + revision < requiredversion) {
            printf("Error: PDFlib %s or above is required\n", requiredvstr);
            PDF_delete(p);
            return(2);
	}

        /* Start the document */
        if (PDF_begin_document(p, outfile, 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
	}

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_3d");

        font = PDF_load_font(p, "Helvetica", 0, "winansi", "");
        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
	}

        PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");

        /* Define a U3D view */
        optlist = "name=FirstView background={fillcolor={rgb 1 0.5 0.1}}";
        if ((u3dview = PDF_create_3dview(p, "First view", 0, optlist)) == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Load some U3D data with the view defined above */
	sprintf(buf, "views={%d}", u3dview);
        if ((u3ddata = PDF_load_3ddata(p, "box.u3d", 0, buf)) == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Create an annotation containing the loaded U3D data with the
         * defined 3D view as the initial view
         */
	sprintf(buf, "name=annot usercoordinates contents=U3D 3ddata= %d"
            " 3dactivate={enable=open} 3Dinitialview=%d", u3ddata, u3dview);
        PDF_create_annotation(p, 116, 400, 447, 580, "3D", buf);

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
