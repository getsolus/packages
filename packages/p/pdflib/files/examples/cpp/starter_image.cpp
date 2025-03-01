/* $Id: starter_image.cpp,v 1.1.2.2 2007/12/20 16:30:38 kurt Exp $
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
#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {

        /* This is where the data files are. Adjust as necessary. */
        string searchpath = "../data";
        string outfile = "starter_image.pdf";

#define BUFLEN 1024
        char buf[BUFLEN];
        PDFlib p;
        string imagefile = "lionel.jpg";
        int font, image;
        int bw = 400, bh = 200;
        int x = 20, y = 580, yoffset = 260;

        p.set_parameter("SearchPath", searchpath);

        /* This means we must check return values of load_font() etc. */
        p.set_parameter("errorpolicy", "return");

        if (p.begin_document(outfile, "") == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        p.set_info("Creator", "PDFlib starter sample");
        p.set_info("Title", "starter_image");

        /* For PDFlib Lite: change "unicode" to "winansi" */
        font = p.load_font("Helvetica", "winansi", "");
        if (font == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        /* Load the image */
        image = p.load_image("auto", imagefile, "");
        if (image == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        /* Start page 1 */
        p.begin_page_ext(0, 0, "width=a4.width height=a4.height");
        p.setfont(font, 12);


        /* ------------------------------------
         * Place the image in its original size
         * ------------------------------------
         */

        /* Position the image in its original size with its lower left corner
         * at the reference point (20, 380)
         */
        p.fit_image(image, 20, 380, "");

        /* Output some descriptive text */
        p.fit_textline(
            "The image is placed with the lower left corner in its original "
            "size at reference point (20, 380):", 20, 820, "");
        p.fit_textline("fit_image(image, 20, 380, \"\");", 20, 800, "");


        /* --------------------------------------------------------
         * Place the image with scaling and orientation to the west
         * --------------------------------------------------------
         */

        /* Position the image with its lower right corner at the reference
         * point (580, 20).
         * "scale=0.5" scales the image by 0.5.
         * "orientate=west" orientates the image to the west.
         */
        p.fit_image(image, 580, 20,
            "scale=0.5 position={right bottom} orientate=west");

        /* Output some descriptive text */
        p.fit_textline(
            "The image is placed with a scaling of 0.5 and an orientation to "
            "the west with the lower right corner", 580, 320,
            "position={right bottom}");
        p.fit_textline(
            " at reference point (580, 20): fit_image(image, 580, 20, "
            "\"scale=0.5 orientate=west position={right bottom}\");",
            580, 300, "position={right bottom}");

        p.end_page_ext("");

        /* Start page 2 */
        p.begin_page_ext(0, 0, "width=a4.width height=a4.height");
        p.setfont(font, 12);


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
        p.fit_image(image, x, y, buf);

        /* Output some descriptive text */
        p.fit_textline(
            "fit_image(image, x, y, \"boxsize={400 200} position={right top} "
            "fitmethod=clip\");", 20, y+bh+10, "");


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
        p.fit_image(image, x, y-=yoffset, buf);

        /* Output some descriptive text */
        p.fit_textline(
            "fit_image(image, x, y, \"boxsize={400 200} position={center} "
            "fitmethod=meet showborder\");", 20, y+bh+10, "");


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
        p.fit_image(image, x, y-=yoffset, buf);

        /* Output some descriptive text */
        p.fit_textline(
            "fit_image(image, x, y, \"boxsize={400 200} fitmethod=entire\");",
            20, y+bh+10, "");

        p.end_page_ext("");

        p.close_image(image);

        p.end_document("");

    }

    catch (PDFlib::Exception &ex) {
        cerr << "PDFlib exception occurred:" << endl;
        cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
            << ": " << ex.get_errmsg() << endl;
        return 2;
    }

    return 0;
}
