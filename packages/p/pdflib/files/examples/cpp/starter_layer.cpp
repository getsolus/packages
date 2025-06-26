/* $Id: starter_layer.cpp,v 1.1.2.2 2008/02/11 20:10:27 rjs Exp $
 * Starter layer:
 * Define several layers, output images and text to them and define
 * particular layers to be visible when opening the document
 *
 * Define two layers for RGB or Grayscale images and two layers for English or
 * German image captions. Output images and text on the various layers and
 * open the document with the RGB images and English captions visible.
 *
 * Required software: PDFlib/PDFlib+PDI/PPS 7
 * Required data: grayscale and RGB images
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
        string outfile = "starter_layer.pdf";

        PDFlib p;
        string rgb = "nesrin.jpg";
        string gray = "nesrin_gray.jpg";

#define BUFLEN 1024
        char buf[BUFLEN];
        int font, imageRGB, imageGray, layerRGB, layerGray, layerEN, layerDE;

        /* This means we must check return values of load_font() etc. */
        p.set_parameter("errorpolicy", "return");

        p.set_parameter("SearchPath", searchpath);


        /* Open the document with the "Layers" navigation tab visible */
        if (p.begin_document(outfile, "openmode=layers") == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        p.set_info("Creator", "PDFlib starter sample");
        p.set_info("Title", "starter_layer");


        /* Load the font */
        font = p.load_font("Helvetica", "winansi", "");

        if (font == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        /* Load the Grayscale image */
        imageGray = p.load_image("auto", gray, "");
        if (imageGray == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        /* Load the RGB image */
        imageRGB = p.load_image("auto", rgb, "");
        if (imageRGB == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

	/*
	 * Define all layers which will be used, and their relationships.
         * This should be done before the first page if the layers are
	 * used on more than one page.
	 */

        /* Define the layer "RGB" */
        layerRGB = p.define_layer("RGB", "");

        /* Define the layer "Grayscale" which is hidden when opening the
         * document or printing it.
         */
        layerGray = p.define_layer("Grayscale",
                    "initialviewstate=false initialprintstate=false");

        /* At most one of the "Grayscale" and "RGB" layers should be visible */
        sprintf(buf, "group={%d %d}", layerGray, layerRGB);
        p.set_layer_dependency("Radiobtn", buf);

        /* Define the layer "English" */
        layerEN = p.define_layer("English", "");

        /* Define the layer "German" which is hidden when opening the document
         * or printing it.
         */
        layerDE = p.define_layer("German",
                    "initialviewstate=false initialprintstate=false");

        /* At most one of the "English" and "German" layers should be visible */
        sprintf(buf, "group={%d %d}", layerEN, layerDE);
        p.set_layer_dependency("Radiobtn", buf);

        /* Start page */
        p.begin_page_ext(0, 0, "width=a4.width height=a4.height");

	/* Place the RGB image on the layer "RGB" */
        p.begin_layer(layerRGB);
        p.fit_image(imageRGB, 100, 400,
                    "boxsize={400 300} fitmethod=meet");

	/* Place the Grayscale image on the layer "Grayscale" */
        p.begin_layer(layerGray);
        p.fit_image(imageGray, 100, 400,
                    "boxsize={400 300} fitmethod=meet");

	/* Place an English image caption on the layer "English" */
        p.begin_layer(layerEN);
        sprintf(buf, "font=%d fontsize=20", font);
        p.fit_textline("This is the Nesrin image.", 100, 370, buf);

	/* Place a German image caption on the layer "German".  */
        p.begin_layer(layerDE);
        sprintf(buf, "font=%d fontsize=20", font);
        p.fit_textline("Das ist das Nesrin-Bild.", 100, 370, buf);

        p.end_layer();

        p.end_page_ext("");

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
