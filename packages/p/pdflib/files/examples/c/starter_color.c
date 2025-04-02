/* $Id: starter_color.c,v 1.1.2.4 2008/04/30 15:30:07 rjs Exp $
 * Starter color:
 * Demonstrate the basic use of supported color spaces
 *
 * Apply the following color spaces to text and vector graphics:
 * - gray
 * - rgb
 * - cmyk
 * - iccbasedgray/rgb/cmyk
 * - spot
 * - lab
 * - pattern
 * - shadings
 *
 * Required software: PDFlib/PDFlib+PDI/PPS 7
 * Required data: none
 */

#include <stdio.h>
#include <stdlib.h>

#include "pdflib.h"


int
main(void)
{
    /* This is where the data files are. Adjust as necessary. */
    const char* searchpath = "../data";
    const char* outfile = "starter_color.pdf";

#define BUFLEN 1024
    char buf[BUFLEN];
    PDF * p;
    int font, spot;
    int y = 800, x = 50, xoffset1=80, xoffset2 = 100, yoffset = 70, r = 30;
    double icchandle;

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
        PDF_set_info(p, "Title", "starter_color");

        /* Load the font */
        font = PDF_load_font(p, "Helvetica", 0, "winansi", "");

        if (font == -1) {
            printf("Error: %s\n", PDF_get_errmsg(p));
            PDF_delete(p);
            return(2);
        }

        /* Start the page */
        PDF_begin_page_ext(p, 0, 0, "width=a4.width height=a4.height");

        PDF_setfont(p, font, 14);


        /* -------------------------------------------------------------------
         * Use default colors
         *
         * If no special color is set the default values will be used. The
         * default values are restored at the beginning of the page.
         * 0=black in the Gray color space is the default fill and stroke
         * color in many cases, as shown in our sample.
         * -------------------------------------------------------------------
         */

        /* Fill a circle with the default black fill color */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        /* Output text with default black fill color */
        PDF_fit_textline(p,
                "Circle and text filled with default color {gray 0}", 0,
                x+xoffset2, y, "");

        PDF_fit_textline(p, "1.", 0,  x+xoffset1, y, "");

        /* -------------------------------------------------------------------
         * Use the Gray color space
         *
         * Gray color is defined by Gray values between 0=black and 1=white.
         * -------------------------------------------------------------------
         */

        /* Using setcolor(), set the current fill color to a light gray
         * represented by (0.5, 0, 0, 0) which defines 50% gray. Since gray
         * colors are defined by only one value, the last three function
         * parameters must be set to 0.
         */
        PDF_setcolor(p, "fill", "gray", 0.5, 0, 0, 0);

        /* Fill a circle with the current fill color defined above */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        /* Output text with the current fill color */
        PDF_fit_textline(p, "Circle and text filled with {gray 0.5}", 0,
                x+xoffset2, y, "");

        /* Alternatively, you can set the fill color in the call to
         * fit_textline() using the "fillcolor" option. This case applies the
         * fill color just the single function call. The current fill color
         * won't be affected.
         */
        PDF_fit_textline(p, "2.", 0, x+xoffset1, y, "fillcolor={gray 0.5}");


        /* --------------------------------------------------------------------
         * Use the RGB color space
         *
         * RGB color is defined by RGB triples, i.e. three values between 0 and
         * 1 specifying the percentage of red, green, and blue.
         * (0, 0, 0) is black and (1, 1, 1) is white. The commonly used RGB
         * color values in the range 0–255 must be divided by 255 in order to
         * scale them to the range 0–1 as required by PDFlib.
         * --------------------------------------------------------------------
         */

        /* Use setcolor() to set the fill color to a grass-green
         * represented by (0.1, 0.95, 0.3, 0) which defines 10% red, 95% green,
         * 30% blue. Since RGB colors are defined by only three values, the last
         * function parameter must be set to 0.
         */
        PDF_setcolor(p, "fill", "rgb", 0.1, 0.95, 0.3, 0);

        /* Draw a circle with the current fill color defined above */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        /* Output a text line with the RGB fill color defined above */
        PDF_fit_textline(p, "Circle and text filled with {rgb 0.1 0.95 0.3}",
                0, x+xoffset2, y, "");

        /* Alternatively, you can set the fill color in the call to
         * fit_textline() using the "fillcolor" option. This case applies the
         * fill color just the single function call. The current fill color
         * won't be affected.
         */
        PDF_fit_textline(p, "3.", 0, x+xoffset1, y,
                "fillcolor={rgb 0.1 0.95 0.3}");


        /* --------------------------------------------------------------------
         * Use the CMYK color space
         *
         * CMYK color is defined by four CMYK values between 0 = no color and
         * 1 = full color representing cyan, magenta, yellow, and black values;
         * (0, 0, 0, 0) is white and (0, 0, 0, 1) is black.
         * --------------------------------------------------------------------
         */

        /* Use setcolor() to set the current fill color to a pale
         * orange, represented by (0.1, 0.7, 0.7, 0.1) which defines 10% Cyan,
         * 70% Magenta, 70% Yellow, and 10% Black.
         */
        PDF_setcolor(p, "fill", "cmyk", 0.1, 0.7, 0.7, 0.1);

        /* Fill a circle with the current fill color defined above */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        /* Output a text line with the CMYK fill color defined above */
        PDF_fit_textline(p,
                "Circle and text filled with {cmyk 0.1 0.7 0.7 0.1}", 0,
                x+xoffset2, y, "");

        /* Alternatively, you can set the fill color in the call to
         * fit_textline() using the "fillcolor" option. This case applies the
         * fill color just the single function call. The current fill color
         * won't be affected.
         */
        PDF_fit_textline(p, "4.", 0, x+xoffset1, y,
                "fillcolor={cmyk 0.1 0.7 0.7 0.1}");


        /* --------------------------------------------------------------------
         * Use a Lab color
         *
         * Device-independent color in the CIE L*a*b* color space is specified
         * by a luminance value in the range 0-100 and two color values in the
         * range -127 to 128. The first value contains the green-red axis,
         * while the second value contains the blue-yellow axis.
         * --------------------------------------------------------------------
         */

        /* Set the current fill color to a loud blue, represented by
         * (100, -127, -127, 0). Since Lab colors are defined by only three
         * values, the last function parameter must be set to 0.
         */
        PDF_setcolor(p, "fill", "lab", 100, -127, -127, 0);

        /* Fill a circle with the fill color defined above */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        /* Output a text line with the Lab fill color defined above */
        PDF_fit_textline(p, "Circle and text filled with {lab 100 -127 -127}",
                0, x+xoffset2, y, "");

        /* Alternatively, you can set the fill color in the call to
         * fit_textline() using the "fillcolor" option. This case applies the
         * fill color just the single function call. The current fill color
         * won't be affected.
         */
        PDF_fit_textline(p, "5.", 0, x+xoffset1, y,
                "fillcolor={lab 100 -127 -127}");


        /* ---------------------------------------------------------------
         * Use an ICC based color
         *
         * ICC-based colors are specified with the help of an ICC profile.
         * ---------------------------------------------------------------
         */

        /* Load the sRGB profile. sRGB is guaranteed to be always available */
        icchandle = PDF_load_iccprofile(p, "sRGB", 0, "usage=iccbased");

        /* Set the sRGB profile. (Accordingly, you can use
         * "setcolor:iccprofilergb" or "setcolor:iccprofilegray" with an
         * appropriate profile)
         */
        PDF_set_value(p, "setcolor:iccprofilergb", icchandle);

        /* Use setcolor() with the "iccbasedrgb" color space to set the current
         * fill and stroke color to a grass-green, represented
         * by the RGB color values (0.1 0.95 0.3 0) which define 10% Red,
         * 95% Green, and 30% Blue. Since iccbasedrgb colors are defined by only
         * three values, the last function parameter must be set to 0.
         */
        PDF_setcolor(p, "fill", "iccbasedrgb", 0.1, 0.95, 0.3, 0);

        /* Fill a circle with the ICC based RGB fill color defined above */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        /* Output a text line with the ICC based RGB fill color defined above */
        PDF_fit_textline(p,
                "Circle and text filled with {iccbasedrgb 0.1 0.95 0.3}", 0,
                x+xoffset2, y, "");

        /* Alternatively, you can set the fill color in the call to
         * fit_textline() using the "fillcolor" option. This case applies the
         * fill color just the single function call. The current fill color
         * won't be affected.
         */
        PDF_fit_textline(p, "6.", 0, x+xoffset1, y,
                "fillcolor={iccbasedrgb 0.1 0.95 0.3}");


        /* --------------------------------------------------------------------
         * Use a spot color
         *
         * Spot color (separation color space) is a predefined or arbitrarily
         * named custom color with an alternate representation in one of the
         * other color spaces above; this is generally used for preparing
         * documents which are intended to be printed on an offset printing
         * machine with one or more custom colors. The tint value (percentage)
         * ranges from 0 = no color to 1 = maximum intensity of the spot color.
         * --------------------------------------------------------------------
         */

        /* Define the spot color "PANTONE 281 U" from the builtin color
         * library PANTONE
         */
        spot = PDF_makespotcolor(p, "PANTONE 281 U", 0);

        /* Set the spot color "PANTONE 281 U" with a tint value of 1 (=100%)
         * and output some text. Since spot colors are defined by only two
         * values, the last two function parameters must be set to 0.
         */
        PDF_setcolor(p, "fill", "spot", spot, 1.0, 0, 0);

        /* Fill a circle with the ICC based RGB fill color defined above */
        PDF_circle(p, x, y-=yoffset, r);
        PDF_fill(p);

        PDF_fit_textline(p,
                "Circle and text filled with {spotname {PANTONE 281 U} 1}",
                0, x+xoffset2, y, "");

        /* Alternatively, you can set the fill color in the call to
         * fit_textline() using the "fillcolor" option. This case applies the
         * fill color just the single function call. The current fill color
         * won't be affected.
         */
        PDF_fit_textline(p, "7.", 0, x+xoffset1, y,
            "fillcolor={spotname {PANTONE 281 U} 1}");

        /* or */
        sprintf(buf, "fillcolor={spot %d 1}", spot);
        PDF_fit_textline(p, "7.", 0, x+xoffset1, y, buf);


        /* ----------------------------------------------------------
         * For using the Pattern color space, see the Cookbook topics
         * graphics/fill_pattern and images/background_pattern.
         * ----------------------------------------------------------
         */

        /* ---------------------------------------------------------
         * For using the Shading color space, see the Cookbook topic
         * color/color_gradient.
         * ---------------------------------------------------------
         */

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
