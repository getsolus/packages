/* $Id: starter_pvf.cpp,v 1.1.2.2 2008/03/07 11:06:26 stm Exp $
 * PDFlib Virtual File system (PVF):
 * Create a PVF file which holds an image or PDF, and import the data from the
 * PVF file
 *
 * This avoids disk access and is especially useful when the same image or PDF
 * is imported multiply. For examples, images which sit in a database don't
 * have to be written and re-read from disk, but can be passed to PDFlib
 * directly in memory. A similar technique can be used for loading other data
 * such as fonts, ICC profiles, etc.
 *
 * Required software: PDFlib Lite/PDFlib/PDFlib+PDI/PPS 7
 * Required data: image file
 */
#include <iostream>
#include <cstdlib>

#include "pdflib.hpp"

using namespace std;

#define READMODE        "rb"

/*
 * Helper function to read the content of a file into a buffer
 * avoids incompatible systemcalls
 */
static void *read_file(FILE *fp, size_t *o_filelen)
{
    size_t filelen = 0, len = 0;
    char *content = NULL;

#define STARTER_READ_CHUNKSIZE 64000
    while (!feof(fp))
    {
        if (!content)
        {
            len = 0;
            filelen = STARTER_READ_CHUNKSIZE;
            content = (char *) malloc(filelen + 1);
        }
        else
        {
            len = filelen;
            filelen += STARTER_READ_CHUNKSIZE;
            content = (char *) realloc(content, filelen + 1);
        }
        len = fread(&content[len], 1, STARTER_READ_CHUNKSIZE, fp);
    }
    filelen += len - STARTER_READ_CHUNKSIZE;
    if (filelen)
    {
        content = (char *) realloc(content, filelen + 1);
    }
    else
    {
        free(content);
        content = NULL;
    }

    if (content) content[filelen] = 0;
    *o_filelen = filelen;
    return (void *) content;
} /* read_file */

int
main(void)
{
    try {

        /* This is where the data files are. Adjust as necessary. */
        string searchpath = "../data";
        string outfile = "starter_pvf.pdf";

        PDFlib p;
        FILE *fp;
        unsigned char * imagedata;
        size_t size;

        p.set_parameter("SearchPath", searchpath);

        /* This means we must check return values of load_font() etc. */
        p.set_parameter("errorpolicy", "return");

        /* Set an output path according to the name of the topic */
        if (p.begin_document(outfile, "") == -1) {
            cerr << "Error: " << p.get_errmsg() << endl; return 2;
        }

        p.set_info("Creator", "PDFlib starter sample");
        p.set_info("Title", "starter_pvf");

        /* We just read some image data from a file; to really benefit
         * from using PVF read the data from a Web site or a database instead
         */
        fp = fopen("../data/PDFlib-logo.tif", READMODE);
        if (fp == NULL) {
            cerr << "Error: Couldn't open ../data/PDFlib-logo.tif" << endl; return 2;
        }

        imagedata = (unsigned char *) read_file(fp, &size);
        if (imagedata == NULL) {
            cerr << "Error: Couldn't read ../data/PDFlib-logo.tif" << endl; return 2;
        }


        p.create_pvf("/pvf/image", imagedata, size, "");

        /* Load the image from the PVF */
        int image = p.load_image("auto", "/pvf/image", "");
        if (image == -1) {
            cerr << "Error: " << p.get_errmsg() << endl;
            if (imagedata) {
                free((void *) imagedata);
            }
            return 2;
        }

        /* Fit the image on page 1 */
        p.begin_page_ext(595, 842, "");

        p.fit_image(image, 350, 750, "");

        p.end_page_ext("");

        /* Fit the image on page 2 */
        p.begin_page_ext(595, 842, "");

        p.fit_image(image, 350, 50, "");

        p.end_page_ext("");

        /* Delete the virtual file to free the allocated memory */
        p.delete_pvf("/pvf/image");
        if (imagedata) {
            free((void *) imagedata);
        }

        p.end_document("");
    }

    catch (PDFlib::Exception &ex) {
        cerr << "PDFlib exception occurred in invoice sample: " << endl;
        cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
            << ": " << ex.get_errmsg() << endl;
        return 2;
    }

    return 0;
}
