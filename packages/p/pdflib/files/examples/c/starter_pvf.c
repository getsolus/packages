/* $Id: starter_pvf.c,v 1.1.2.6 2008/04/30 15:30:07 rjs Exp $
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
#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"

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

    /* This is where the data files are. Adjust as necessary. */
    const char* searchpath = "../data";
    const char* outfile = "starter_pvf.pdf";

    PDF * p;
    FILE *fp;
    unsigned char * imagedata;
    int image;
    size_t size;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0) {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
        PDF_set_parameter(p, "SearchPath", searchpath);

        /* This means we must check return values of load_font() etc. */
        PDF_set_parameter(p, "errorpolicy", "return");

        /* Set an output path according to the name of the topic */
        if (PDF_begin_document(p, outfile, 0, "") == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        PDF_set_info(p, "Creator", "PDFlib starter sample");
        PDF_set_info(p, "Title", "starter_pvf");

        /* We just read some image data from a file; to really benefit
         * from using PVF read the data from a Web site or a database instead
         */
        fp = fopen("../data/PDFlib-logo.tif", READMODE);
        if (fp == NULL) {
            printf("Error: Couldn't open ../data/PDFlib-logo.tif\n");
            PDF_delete(p);
            return(2);
        }

        imagedata = read_file(fp, &size);
        if (imagedata == NULL) {
            printf("Error: Couldn't read ../data/PDFlib-logo.tif\n");
            PDF_delete(p);
            return(2);
        }


        PDF_create_pvf(p, "/pvf/image", 0, imagedata, size, "");

        /* Load the image from the PVF */
        image = PDF_load_image(p, "auto", "/pvf/image", 0, "");
        if (image == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            if (imagedata) {
                free((void *) imagedata);
            }
            return(2);
        }

        /* Fit the image on page 1 */
        PDF_begin_page_ext(p, 595, 842, "");

        PDF_fit_image(p, image, 350, 750, "");

        PDF_end_page_ext(p, "");

        /* Fit the image on page 2 */
        PDF_begin_page_ext(p, 595, 842, "");

        PDF_fit_image(p, image, 350, 50, "");

        PDF_end_page_ext(p, "");

        /* Delete the virtual file to free the allocated memory */
        PDF_delete_pvf(p, "/pvf/image", 0);
        if (imagedata) {
            free((void *) imagedata);
        }

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
