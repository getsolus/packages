/* $Id: starter_image.c,v 1.1.2.4 2008/04/30 15:30:07 rjs Exp $
 * Starter image:
 * Load and place an image using various options for scaling and positioning
 *
 * Place the image it its original size.
 * Place the image with scaling and orientation to the west.
 * Fit the image into a box with clipping.
 * Fit the image into a box with proportional resizing.
 * Fit the image into a box entirely.
 *
 * Required software: PDFlib Lite/PDFlib/PDFlib+PDI/PPS 7
 * Required data: image file
 */
#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{

    /* This is where the data files are. Adjust as necessary. */
    const char* searchpath = "../data";
    const char* outfile = "starter_image.pdf";

#define BUFLEN 1024
    char buf[BUFLEN];
    PDF * p;
    const char* imagefile = "lionel.jpg";
    int font, image;
    int bw = 400, bh = 200;
    int x = 20, y = 580, yoffset = 260;


    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        PDF_set_parameter(p, "SearchPath", searchpath);

        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        if (PDF_begin_document(p, outfile, 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_image");

        /* For PDFlib Lite: change "unicode" to "winansi" */
        font = PDF_load_font(p, "Helvetica", 0, "winansi", "");
        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Load the image */
        image = PDF_load_image(p, "auto", imagefile, 0, "");
        if (image == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Start page 1 */
        PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");
        PDF_setfont(p, font, 12);


        /* ------------------------------------
         * Place the image in its original size
         * ------------------------------------
         */

        /* Position the image in its original size with its lower left corner
         * at the reference point (20, 380)
         */
        PDF_fit_image(p, image, 20, 380, "");

        /* Output some descriptive text */
        PDF_fit_textline(p,
            "The image is placed with the lower left corner in its original "
            "size at reference point (20, 380):", 0, 20, 820, "");
        PDF_fit_textline(p, "fit_image(image, 20, 380, \"\");", 0, 20, 800, "");


        /* --------------------------------------------------------
         * Place the image with scaling and orientation to the west
         * --------------------------------------------------------
         */

        /* Position the image with its lower right corner at the reference
         * point (580, 20).
         * "scale=0.5" scales the image by 0.5.
         * "orientate=west" orientates the image to the west.
         */
        PDF_fit_image(p, image, 580, 20,
            "scale=0.5 position={right bottom} orientate=west");

        /* Output some descriptive text */
        PDF_fit_textline(p,
            "The image is placed with a scaling of 0.5 and an orientation to "
            "the west with the lower right corner", 0, 580, 320,
            "position={right bottom}");
        PDF_fit_textline(p,
            " at reference point (580, 20): fit_image(image, 580, 20, "
            "\"scale=0.5 orientate=west position={right bottom}\");",
            0, 580, 300, "position={right bottom}");

        PDF_end_page_ext(p, "");

        /* Start page 2 */
        PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");
        PDF_setfont(p, font, 12);


        /* --------------------------------------
         * Fit the image into a box with clipping
         * --------------------------------------
         */

        /* The "boxsize" option defines a box with a given width and height and
         * its lower left corner located at the reference point.
         * "position={right top}" positions the image on the top right of the
         * box.
         * "fitmethod=clip" clips the image to fit it into the box.
         */
        sprintf(buf, "boxsize={%d %d} position={right top} fitmethod=clip",
            bw, bh);
        PDF_fit_image(p, image, x, y, buf);

        /* Output some descriptive text */
        PDF_fit_textline(p,
            "fit_image(image, x, y, \"boxsize={400 200} position={right top} "
            "fitmethod=clip\");", 0, 20, y+bh+10, "");


        /* ---------------------------------------------------
         * Fit the image into a box with proportional resizing
         * ---------------------------------------------------
         */

        /* The "boxsize" option defines a box with a given width and height and
         * its lower left corner located at the reference point.
         * "position={center}" positions the image in the center of the
         * box.
         * "fitmethod=meet" resizes the image proportionally until its height
         * or width completely fits into the box.
         * The "showborder" option is used to illustrate the borders of the box.
         */
        sprintf(buf,
            "boxsize={%d %d} position={center} fitmethod=meet showborder",
            bw, bh);
        PDF_fit_image(p, image, x, y-=yoffset, buf);

        /* Output some descriptive text */
        PDF_fit_textline(p,
            "fit_image(image, x, y, \"boxsize={400 200} position={center} "
            "fitmethod=meet showborder\");", 0, 20, y+bh+10, "");


        /* ---------------------------------
         * Fit the image into a box entirely
         * ---------------------------------
         */

        /* The "boxsize" option defines a box with a given width and height and
         * its lower left corner located at the reference point.
         * By default, the image is positioned in the lower left corner of the
         * box.
         * "fitmethod=entire" resizes the image proportionally until its height
         * or width completely fits into the box.
         */
        sprintf(buf, "boxsize={%d %d} fitmethod=entire", bw, bh);
        PDF_fit_image(p, image, x, y-=yoffset, buf);

        /* Output some descriptive text */
        PDF_fit_textline(p,
            "fit_image(image, x, y, \"boxsize={400 200} fitmethod=entire\");",
            0, 20, y+bh+10, "");

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
