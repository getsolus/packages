/* $Id: starter_layer.c,v 1.1.2.6 2008/04/30 15:30:07 rjs Exp $
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

#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{

    /* This is where the data files are. Adjust as necessary. */
    const char* searchpath = "../data";
    const char* outfile = "starter_layer.pdf";

    PDF * p;
    const char* rgb = "nesrin.jpg";
    const char* gray = "nesrin_gray.jpg";

#define BUFLEN 1024
    char buf[BUFLEN];
    int font, imageRGB, imageGray, layerRGB, layerGray, layerEN, layerDE;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        PDF_set_parameter(p, "SearchPath", searchpath);

        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");


        /* Open the document with the "Layers" navigation tab visible */
        if (PDF_begin_document(p, outfile, 0, "openmode=layers") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_layer");

        /* Load the font */
        font = PDF_load_font(p, "Helvetica", 0, "winansi", "");

        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Load the Grayscale image */
        imageGray = PDF_load_image(p, "auto", gray, 0, "");
        if (imageGray == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Load the RGB image */
        imageRGB = PDF_load_image(p, "auto", rgb, 0, "");
        if (imageRGB == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /*
         * Define all layers which will be used, and their relationships.
         * This should be done before the first page if the layers are
         * used on more than one page.
         */

        /* Define the layer "RGB" */
        layerRGB = PDF_define_layer(p, "RGB", 0, "");

        /* Define the layer "Grayscale" which is hidden when opening the
         * document or printing it. */
        layerGray = PDF_define_layer(p, "Grayscale", 0,
                    "initialviewstate=false initialprintstate=false");

        /* At most one of the "Grayscale" and "RGB" layers should be visible */
        sprintf(buf, "group={%d %d}", layerGray, layerRGB);
        PDF_set_layer_dependency(p, "Radiobtn", buf);

        /* Define the layer "English" */
        layerEN = PDF_define_layer(p, "English", 0, "");

        /* Define the layer "German" which is hidden when opening the document
         * or printing it. */
        layerDE = PDF_define_layer(p, "German", 0,
                    "initialviewstate=false initialprintstate=false");

        /* At most one of the "English" and "German" layers should be visible */
        sprintf(buf, "group={%d %d}", layerEN, layerDE);
        PDF_set_layer_dependency(p, "Radiobtn", buf);

        /* Start page */
        PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");

	/* Place the RGB image on the layer "RGB" */
        PDF_begin_layer(p, layerRGB);
        PDF_fit_image(p, imageRGB, 100, 400,
                    "boxsize={400 300} fitmethod=meet");

	/* Place the Grayscale image on the layer "Grayscale" */
        PDF_begin_layer(p, layerGray);
        PDF_fit_image(p, imageGray, 100, 400,
                    "boxsize={400 300} fitmethod=meet");

	/* Place an English image caption on the layer "English" */
        PDF_begin_layer(p, layerEN);
        sprintf(buf, "font=%d fontsize=20", font);
        PDF_fit_textline(p, "This is the Nesrin image.", 0, 100, 370, buf);

	/* Place a German image caption on the layer "German".  */
        PDF_begin_layer(p, layerDE);
        sprintf(buf, "font=%d fontsize=20", font);
        PDF_fit_textline(p, "Das ist das Nesrin-Bild.", 0, 100, 370, buf);

        PDF_end_layer(p);

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
