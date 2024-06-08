/*---------------------------------------------------------------------------*
 |              PDFlib - A library for generating PDF on the fly             |
 +---------------------------------------------------------------------------+
 | Copyright (c) 1997-2006 Thomas Merz and PDFlib GmbH. All rights reserved. |
 +---------------------------------------------------------------------------+
 |                                                                           |
 |    This software is subject to the PDFlib license. It is NOT in the       |
 |    public domain. Extended versions and commercial licenses are           |
 |    available, please check http://www.pdflib.com.                         |
 |                                                                           |
 *---------------------------------------------------------------------------*/

// $Id: pdflib.hpp,v 1.55.2.4 2008/06/20 14:27:37 stm Exp $
//
// in sync with pdflib.h 1.151.2.22
//
// C++ wrapper for PDFlib
//
//

#ifndef PDFLIB_HPP
#define PDFLIB_HPP

#include <string>
#include "pdflib.h"

#if defined(_MSC_VER) && defined(_MANAGED)
/*
 * This definition is only here for suppressing an unnecessary warning from
 * the linker when compiling the C++ wrapper as .NET managed code. As PDF_s
 * is only used to define an opaque pointer, the .NET wrapper never needs
 * the knowledge about the actual size of PDF_s.
 */
struct PDF_s {};

/*
 * See pdflib.cpp for the reasoning why the C++ wrapper is compiled as
 * unmanaged code.
 */
#pragma unmanaged
#endif

// The C++ class wrapper for PDFlib

class PDFlib {
public:
    class Exception
    {
    public:
	Exception(std::string errmsg, int errnum, std::string apiname, 
	    void *opaque);
	std::string get_errmsg();
	int get_errnum();
	std::string get_apiname();
	const void *get_opaque();
    private:
	std::string m_errmsg;
	int m_errnum;
	std::string m_apiname;
	void * m_opaque;
    }; // Exception

    PDFlib(allocproc_t allocproc = NULL,
	reallocproc_t reallocproc = NULL,
	freeproc_t freeproc = NULL,
	void *opaque = NULL);

    ~PDFlib() throw();

    void activate_item(int id);
    int add_bookmark(std::string text, int parent, int p_open);
    void add_launchlink(double llx, double lly, double urx, double ury,
	std::string filename);
    void add_locallink(double llx, double lly, double urx, double ury, int page,
	std::string optlist);
    void add_nameddest(std::string name, std::string optlist);
    void add_note(double llx, double lly, double urx, double ury,
    	std::string contents,
	std::string title, std::string icon, int p_open);
    void add_pdflink(double llx, double lly, double urx, double ury,
	std::string filename, int page, std::string optlist);
    int add_table_cell(int table, int column, int row, std::string text,
	std::string optlist);
    int add_textflow(int textflow, std::string text, std::string optlist);
    void add_thumbnail(int image);
    void add_weblink(double llx, double lly, double urx, double ury,
	std::string url);
    void arc(double x, double y, double r, double alpha, double beta);
    void arcn(double x, double y, double r, double alpha, double beta);
    void attach_file(double llx, double lly, double urx, double ury,
	std::string filename, std::string description, std::string author,
	std::string mimetype, std::string icon);
    int begin_document(std::string filename, std::string optlist);
    void begin_document_callback(writeproc_t writeproc, std::string optlist);
    void begin_font(std::string fontname, double a, double b,
	double c, double d, double e, double f, std::string optlist);
    void begin_glyph(std::string glyphname, double wx, double llx, double lly,
	double urx, double ury);
    int begin_item(std::string tag, std::string optlist);
    void begin_layer(int layer);
    void begin_page(double width, double height);
    void begin_page_ext(double width, double height, std::string optlist);
    int begin_pattern(double width, double height, double xstep, double ystep,
	int painttype);
    int begin_template(double width, double height);
    int begin_template_ext(double width, double height, std::string optlist);
    void circle(double x, double y, double r);
    void clip();
    void close();
    void close_image(int image);
    void close_pdi(int doc);
    void close_pdi_document(int doc);
    void close_pdi_page(int page);
    void closepath();
    void closepath_fill_stroke();
    void closepath_stroke();
    void concat(double a, double b, double c, double d, double e, double f);
    void continue_text(std::string text);
    int create_3dview(std::string username, std::string optlist);
    int create_action(std::string type, std::string optlist);
    void create_annotation(double llx, double lly, double urx, double ury,
	std::string type, std::string optlist);
    int create_bookmark(std::string text, std::string optlist);
    void create_field(double llx, double lly, double urx, double ury,
	std::string name, std::string type, std::string optlist);
    void create_fieldgroup(std::string name, std::string optlist);
    int create_gstate (std::string optlist);
    void create_pvf(std::string filename, const void *data, size_t size,
    	std::string optlist);
    int create_textflow(std::string text, std::string optlist);
    void curveto(double x1, double y1, double x2, double y2, double x3,
    	double y3);
    int define_layer(std::string name, std::string optlist);
    int delete_pvf(std::string filename);
    void delete_table(int table, std::string optlist);
    void delete_textflow(int textflow);
    void encoding_set_char(std::string encoding, int slot,
	std::string glyphname, int uv);
    void end_document(std::string optlist);
    void end_font();
    void end_glyph();
    void end_item(int id);
    void end_layer();
    void end_page();
    void end_page_ext(std::string optlist);
    void end_pattern();
    void end_template();
    void endpath();
    void fill();
    int fill_imageblock(int page, std::string blockname, int image,
	std::string optlist);
    int fill_pdfblock(int page, std::string blockname, int contents,
	std::string optlist);
    int fill_textblock(int page, std::string blockname, std::string text,
	std::string optlist);
    void fill_stroke();
    int findfont(std::string fontname, std::string encoding, int embed);
    void fit_image (int image, double x, double y, std::string optlist);
    void fit_pdi_page (int page, double x, double y, std::string optlist);
    std::string fit_table(int table, double llx, double lly, double urx,
	double ury, std::string optlist);
    std::string fit_textflow(int textflow, double llx, double lly, double urx,
	double ury, std::string optlist);
    void fit_textline(std::string text, double x, double y, std::string optlist);
    std::string get_apiname();
    const char * get_buffer(long *size);
    std::string get_errmsg();
    int get_errnum();
    void * get_opaque();
    std::string get_parameter(std::string key, double modifier);
    double get_pdi_value(std::string key, int doc, int page, int reserved);
    std::string get_pdi_parameter(std::string key, int doc, int page,
	int reserved, int *len = NULL);
    double get_value(std::string key, double modifier);
    double info_font(int font, std::string keyword, std::string optlist);
    double info_matchbox(std::string boxname, int num, std::string keyword);
    double info_table(int table, std::string keyword);
    double info_textflow(int textflow, std::string keyword);
    double info_textline(std::string text, std::string keyword,
	std::string optlist);
    void initgraphics();
    void lineto(double x, double y);
    int load_3ddata(std::string filename, std::string optlist);
    int load_font(std::string fontname, std::string encoding,
	std::string optlist);
    int load_iccprofile(std::string profilename, std::string optlist);
    int load_image (std::string imagetype, std::string filename,
	std::string optlist);
    int makespotcolor(std::string spotname);
    void moveto(double x, double y);
    int open_CCITT(std::string filename, int width, int height, int BitReverse,
	int K, int BlackIs1);
    int open_file(std::string filename);
    int open_image(std::string imagetype, std::string source, const char *data,
	long len, int width, int height, int components, int bpc,
	std::string params);
    int open_image_file(std::string imagetype, std::string filename,
	std::string stringparam, int intparam);
    void open_mem(writeproc_t writeproc);
    int open_pdi(std::string filename, std::string optlist, int reserved);
    int open_pdi_document(std::string filename, std::string optlist);
    int open_pdi_page(int doc, int pagenumber, std::string optlist);
    double pcos_get_number(int doc, std::string path);
    std::string pcos_get_string(int doc, std::string path);
    const unsigned char * pcos_get_stream(int doc, int *length,
	std::string optlist, std::string path);
    void place_image(int image, double x, double y, double p_scale);
    void place_pdi_page(int page, double x, double y, double sx, double sy);
    int process_pdi(int doc, int page, std::string optlist);
    void rect(double x, double y, double width, double height);
    void restore();
    void resume_page(std::string optlist);
    void rotate(double phi);
    void save();
    void scale(double sx, double sy);
    void set_border_color(double red, double green, double blue);
    void set_border_dash(double b, double w);
    void set_border_style(std::string style, double width);
    void setfont(int font, double fontsize);
    void set_gstate(int gstate);
    void set_info(std::string key, std::string value);
    void set_layer_dependency(std::string type, std::string optlist);
    void set_parameter(std::string key, std::string value);
    void set_text_pos(double x, double y);
    void set_value(std::string key, double value);
    void setcolor(std::string fstype, std::string colorspace,
	double c1, double c2, double c3, double c4);
    void setdash(double b, double w);
    void setdashpattern(std::string optlist);
    void setflat(double flatness);
    void setlinecap(int linecap);
    void setlinejoin(int linejoin);
    void setlinewidth(double width);
    void setmatrix( double a, double b, double c, double d, double e, double f);
    void setmiterlimit(double miter);
    void setpolydash(float *darray, int length);
    int shading (std::string shtype, double x0, double y0, double x1, double y1,
	double c1, double c2, double c3, double c4, std::string optlist);
    int shading_pattern (int shade, std::string optlist);
    void shfill (int shade);
    void show(std::string text);
    int show_boxed(std::string text, double left, double top,
	double width, double height, std::string hmode, std::string feature);
    void show_xy(std::string text, double x, double y);
    void skew(double alpha, double beta);
    double stringwidth(std::string text, int font, double fontsize);
    void stroke();
    void suspend_page(std::string optlist);
    void translate(double tx, double ty);
    std::string utf16_to_utf8(std::string utf16string);
    std::string utf8_to_utf16(std::string utf8string, std::string format);
    std::string utf32_to_utf16(std::string utf32string, std::string ordering);

    void xshow(std::string text, const double *xadvancelist);

private:
    PDF *p;
    const PDFlib_api *m_PDFlib_api;
};

#if defined(_MSC_VER) && defined(_MANAGED)
#pragma managed
#endif

#endif	// PDFLIB_HPP
