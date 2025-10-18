/* $Id: pdfclock.c,v 1.21 2006/10/01 10:27:02 rjs Exp $
 *
 * A little PDFlib application to draw an analog clock.
 */

#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#include "pdflib.h"

#define RADIUS		200.0
#define MARGIN		20.0

int
main(void)
{
    PDF		*p;
    double	alpha;
    time_t	timer;
    struct tm	ltime;

    /* create a new PDFlib object */
    if ((p = PDF_new()) == (PDF *) 0)
    {
        printf("Couldn't create PDFlib object (out of memory)!\n");
        return(2);
    }

    PDF_TRY(p) {
	/* This means we must check return values of load_font() etc. */
	PDF_set_parameter(p, "errorpolicy", "return");

	if (PDF_begin_document(p, "pdfclock.pdf", 0, "") == -1) {
	    printf("Error: %s\n", PDF_get_errmsg(p));
	    return(2);
	}

	/* This line is required to avoid problems on Japanese systems */
	PDF_set_parameter(p, "hypertextencoding", "host");

	PDF_set_info(p, "Creator", "pdfclock.c");
	PDF_set_info(p, "Author", "Thomas Merz");
	PDF_set_info(p, "Title", "PDF clock (C)");

	PDF_begin_page_ext(p, 2 * (RADIUS + MARGIN), 2 * (RADIUS + MARGIN), "");
	
	PDF_translate(p, RADIUS + MARGIN, RADIUS + MARGIN);
	PDF_setcolor(p, "fillstroke", "rgb", 0, 0, 1, 0);
	PDF_save(p);

	/* minute strokes */
	PDF_setlinewidth(p, 2);
	for (alpha = 0; alpha < 360; alpha += 6)
	{
	    PDF_rotate(p, 6);
	    PDF_moveto(p, RADIUS, 0);
	    PDF_lineto(p, RADIUS - MARGIN/3, 0);
	    PDF_stroke(p);
	}

	PDF_restore(p);
	PDF_save(p);

	/* 5 minute strokes */
	PDF_setlinewidth(p, 3);
	for (alpha = 0; alpha < 360; alpha += 30)
	{
	    PDF_rotate(p, 30);
	    PDF_moveto(p, RADIUS, 0);
	    PDF_lineto(p, RADIUS-MARGIN, 0);
	    PDF_stroke(p);
	}

	time(&timer);
	ltime = *localtime(&timer);

	/* draw hour hand */
	PDF_save(p);
	PDF_rotate(p, -((ltime.tm_min/60.0) + ltime.tm_hour - 3.0) * 30.0);
	PDF_moveto(p, -RADIUS/10, -RADIUS/20);
	PDF_lineto(p, RADIUS/2, 0);
	PDF_lineto(p, -RADIUS/10, RADIUS/20);
	PDF_closepath(p);
	PDF_fill(p);
	PDF_restore(p);

	/* draw minute hand */
	PDF_save(p);
	PDF_rotate(p, -((ltime.tm_sec/60.0) + ltime.tm_min - 15.0) * 6.0);
	PDF_moveto(p, -RADIUS/10, -RADIUS/20);
	PDF_lineto(p, RADIUS * 0.8, 0);
	PDF_lineto(p, -RADIUS/10, RADIUS/20);
	PDF_closepath(p);
	PDF_fill(p);
	PDF_restore(p);

	/* draw second hand */
	PDF_setcolor(p, "fillstroke", "rgb", 1, 0, 0, 0);
	PDF_setlinewidth(p, 2);
	PDF_save(p);
	PDF_rotate(p, -((ltime.tm_sec - 15.0) * 6.0));
	PDF_moveto(p, -RADIUS/5, 0);
	PDF_lineto(p, RADIUS, 0);
	PDF_stroke(p);
	PDF_restore(p);

	/* draw little circle at center */
	PDF_circle(p, 0, 0, RADIUS/30);
	PDF_fill(p);

	PDF_restore(p);

	PDF_end_page_ext(p, "");
	PDF_end_document(p, "");
    }

    PDF_CATCH(p) {
        printf("PDFlib exception occurred in pdfclock sample:\n");
        printf("[%d] %s: %s\n",
	    PDF_get_errnum(p), PDF_get_apiname(p), PDF_get_errmsg(p));
        PDF_delete(p);
        return(2);
    }

    PDF_delete(p);

    return 0;
}
