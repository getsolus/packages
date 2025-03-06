/*---------------------------------------------------------------------------*
 |              PDFlib - A library for generating PDF on the fly             |
 +---------------------------------------------------------------------------+
 | Copyright (c) 1997-2005 Thomas Merz and PDFlib GmbH. All rights reserved. |
 +---------------------------------------------------------------------------+
 |                                                                           |
 |    This software is subject to the PDFlib license. It is NOT in the       |
 |    public domain. Extended versions and commercial licenses are           |
 |    available, please check http://www.pdflib.com.                         |
 |                                                                           |
 *---------------------------------------------------------------------------*/

// $Id: pdflib.cpp,v 1.70.2.5 2008/06/20 14:27:37 stm Exp $
//
// in sync with pdflib.h 1.232
//
// Implementation of C++ wrapper for PDFlib
//
//

#if _MSC_VER >= 1310    /* VS .NET 2003 and later */
/* pdflib.h declares some functions as deprecated, but we don't want to see
 * these warnings here */
#pragma warning(disable: 4995)
#endif

#include "pdflib.hpp"

#if defined(_MSC_VER) && defined(_MANAGED)
/*
 * For .NET managed C++ code, it is possible to use try/catch for exeption
 * handling. Enable this with the following define:
 */
// #define PDFCPP_USE_CPP_TRY_CATCH

/*
 * As it is not possible to compile the C++ wrapper truly as managed code, we
 * leave it as unmanaged code, as it is anyway only a thin layer over the
 * unmanaged PDFlib C DLL.
 * The reason that it is not possible to make it wholly managed is that even
 * with C++ try/catch the error handler will be compiled as native code, as
 * a function pointer is taken of it and passed to the PDFlib C library.
 */
#pragma unmanaged
#endif

using std::string;

#define CHAR(s) (s).c_str()
#define LEN(s)  ((int) (s).size())

#if defined(PDFCPP_USE_CPP_TRY_CATCH)

static void PDFLIB_CALL
errorhandler(PDF *p, int errortype, const char* msg)
{
  throw PDFlib::Exception(PDF_get_errmsg(p), PDF_get_errnum(p),
		  PDF_get_apiname(p), PDF_get_opaque(p));
}

#define PDFCPP_TRY try {

#define PDFCPP_CATCH } catch (PDFlib::Exception &) {\
  throw;\
}

#else

#define PDFCPP_TRY	PDF_TRY(p)

#define PDFCPP_CATCH  \
PDF_CATCH(p) {\
    throw Exception(PDF_get_errmsg(p), PDF_get_errnum(p),\
			    PDF_get_apiname(p), PDF_get_opaque(p));\
}

#endif /* PDFCPP_USE_CPP_TRY_CATCH */

PDFlib::Exception::Exception(string errmsg, int errnum, string apiname,
	void *opaque)
: m_errmsg(errmsg),
  m_errnum(errnum),
  m_apiname(apiname),
  m_opaque(opaque)
{ }

string PDFlib::Exception::get_errmsg() { return m_errmsg; }
int PDFlib::Exception::get_errnum() { return m_errnum; }
string PDFlib::Exception::get_apiname() { return m_apiname; }
const void * PDFlib::Exception::get_opaque() { return m_opaque; }

PDFlib::PDFlib(
    allocproc_t allocproc,
    reallocproc_t reallocproc,
    freeproc_t freeproc,
    void *opaque)
{
    m_PDFlib_api = ::PDF_get_api();

    if (m_PDFlib_api->sizeof_PDFlib_api != sizeof(PDFlib_api) ||
	m_PDFlib_api->major != PDFLIB_MAJORVERSION ||
	m_PDFlib_api->minor != PDFLIB_MINORVERSION) {
	throw Exception("loaded wrong version of PDFlib library", 0,
		"pdflib.cpp", opaque);
    }

#if defined(PDFCPP_USE_CPP_TRY_CATCH)
    p = m_PDFlib_api->PDF_new2(errorhandler, allocproc,
    			reallocproc, freeproc, opaque);
#else
    p = m_PDFlib_api->PDF_new2(NULL, allocproc, reallocproc, freeproc, opaque);
#endif
    
    if (p == (PDF *)0) {
	throw Exception("No memory for PDFlib object", 0, "pdflib.cpp", opaque);
    }

    PDFCPP_TRY
    {
	PDF_set_parameter(p, "binding", "C++");
        PDF_set_parameter(p, "objorient", "true");
    }
    PDFCPP_CATCH;
}

PDFlib::~PDFlib() throw()
{
    m_PDFlib_api->PDF_delete(p);
}


void
PDFlib::activate_item(int id)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_activate_item(p, id);
    PDFCPP_CATCH;
}

int
PDFlib::add_bookmark(string text, int parent, int p_open)
{
    int retval = 0;
    PDFCPP_TRY
      retval = m_PDFlib_api->PDF_add_bookmark2(p, CHAR(text), (int) LEN(text),
		    parent, p_open);
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::add_launchlink(double llx, double lly, double urx, double ury,
    string filename)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_add_launchlink(p, llx, lly, urx, ury, CHAR(filename));
    PDFCPP_CATCH;
}

void
PDFlib::add_locallink(double llx, double lly, double urx, double ury, int page,
    string optlist)
{
    PDFCPP_TRY
    m_PDFlib_api->PDF_add_locallink(p, llx, lly, urx, ury, page, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::add_nameddest(string name, string optlist)
{
    PDFCPP_TRY
    m_PDFlib_api->PDF_add_nameddest(p, CHAR(name), LEN(name), CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::add_note(double llx, double lly, double urx, double ury,
    string contents, string title, string icon, int p_open)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_add_note2(p, llx, lly, urx, ury,
	CHAR(contents), LEN(contents), CHAR(title), LEN(title), CHAR(icon),
	p_open);
    PDFCPP_CATCH;
}

void
PDFlib::add_pdflink(double llx, double lly, double urx, double ury,
    string filename, int page, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_add_pdflink(p, llx, lly, urx, ury, CHAR(filename),
			    page, CHAR(optlist));
    PDFCPP_CATCH;
}

int
PDFlib::add_table_cell(int table, int column, int row, string text, 
    string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_add_table_cell(p, table, column, row,
		    CHAR(text), (int) LEN(text), CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

int
PDFlib::add_textflow(int textflow, string text, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_add_textflow(p, textflow, CHAR(text),
		    (int) LEN(text), CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

void
PDFlib::add_thumbnail(int image)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_add_thumbnail(p, image);
    PDFCPP_CATCH;
}

void
PDFlib::add_weblink(double llx, double lly, double urx, double ury,
    string url)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_add_weblink(p, llx, lly, urx, ury, CHAR(url));
    PDFCPP_CATCH;
}

void
PDFlib::arc(double x, double y, double r, double alpha, double beta)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_arc(p, x, y, r, alpha, beta);
    PDFCPP_CATCH;
}

void
PDFlib::arcn(double x, double y, double r, double alpha, double beta)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_arcn(p, x, y, r, alpha, beta);
    PDFCPP_CATCH;
}

void
PDFlib::attach_file(double llx, double lly, double urx, double ury,
    string filename, string description, string author,
    string mimetype, string icon)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_attach_file2(p, llx, lly, urx, ury, CHAR(filename), 0,
	    CHAR(description), (int) LEN(description), CHAR(author),
	    (int) LEN(author), CHAR(mimetype), CHAR(icon));
    PDFCPP_CATCH;
}

int
PDFlib::begin_document(string filename, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_begin_document(p, CHAR(filename),
	    0, CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

void
PDFlib::begin_document_callback(writeproc_t writeproc, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_begin_document_callback(p, writeproc, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::begin_font(string fontname, double a, double b,
    double c, double d, double e, double f, string optlist)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_begin_font(p, CHAR(fontname), 0,
	a, b, c, d, e, f, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::begin_glyph(string glyphname, double wx, double llx, double lly,
    double urx, double ury)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_begin_glyph(p, CHAR(glyphname), wx, llx,
	    lly, urx, ury);
    PDFCPP_CATCH;
}

int
PDFlib::begin_item(string tag, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_begin_item(p, CHAR(tag), CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::begin_layer(int layer)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_begin_layer(p, layer);
    PDFCPP_CATCH;
}

void
PDFlib::begin_page(double width, double height)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_begin_page(p, width, height);
    PDFCPP_CATCH;
}

void
PDFlib::begin_page_ext(double width, double height, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_begin_page_ext(p, width, height, CHAR(optlist));
    PDFCPP_CATCH;
}


int
PDFlib::begin_pattern(double width, double height, double xstep, double ystep,
    int painttype)
{
    int retval = 0;

    PDFCPP_TRY

	retval = m_PDFlib_api->PDF_begin_pattern(p, width, height,
		xstep, ystep, painttype);
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::begin_template(double width, double height)
{
    int retval = 0;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_begin_template(p, width, height);
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::begin_template_ext(double width, double height, string optlist)
{
    int retval = 0;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_begin_template_ext(p, width, height,
	CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::circle(double x, double y, double r)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_circle(p, x, y, r);
    PDFCPP_CATCH;
}

void
PDFlib::clip()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_clip(p);
    PDFCPP_CATCH;
}

void
PDFlib::close()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_close(p);
    PDFCPP_CATCH;
}

void
PDFlib::close_image(int image)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_close_image(p, image);
    PDFCPP_CATCH;
}

void
PDFlib::close_pdi(int doc)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_close_pdi(p, doc);
    PDFCPP_CATCH;
}

void
PDFlib::close_pdi_document(int doc)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_close_pdi_document(p, doc);
    PDFCPP_CATCH;
}

void
PDFlib::close_pdi_page(int page)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_close_pdi_page(p, page);
    PDFCPP_CATCH;
}

void
PDFlib::closepath()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_closepath(p);
    PDFCPP_CATCH;
}

void
PDFlib::closepath_fill_stroke()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_closepath_fill_stroke(p);
    PDFCPP_CATCH;
}

void
PDFlib::closepath_stroke()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_closepath_stroke(p);
    PDFCPP_CATCH;
}

void
PDFlib::concat(double a, double b, double c, double d, double e, double f)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_concat(p, a, b, c, d, e, f);
    PDFCPP_CATCH;
}

void
PDFlib::continue_text(string text)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_continue_text2(p, CHAR(text), (int) LEN(text));
    PDFCPP_CATCH;
}

int
PDFlib::create_3dview(string username, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_create_3dview(p, CHAR(username),
	    0, CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

int
PDFlib::create_action(string type, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_create_action(p, CHAR(type), CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

void
PDFlib::create_annotation(double llx, double lly, double urx, double ury,
    string type, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_create_annotation(p, llx, lly, urx, ury,
		CHAR(type), CHAR(optlist));
    PDFCPP_CATCH;
}

int
PDFlib::create_bookmark(string text, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_create_bookmark(p, CHAR(text), LEN(text),
	    CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

void
PDFlib::create_field(double llx, double lly, double urx, double ury,
    string name, string type, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_create_field(p, llx, lly, urx,
	    ury, CHAR(name), LEN(name), CHAR(type), CHAR(optlist));
    PDFCPP_CATCH;
}


void
PDFlib::create_fieldgroup(string name, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_create_fieldgroup(p, CHAR(name), LEN(name),
	    CHAR(optlist));
    PDFCPP_CATCH;
}

int
PDFlib::create_gstate (string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_create_gstate(p, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::create_pvf(string filename, const void *data, size_t size,
	string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_create_pvf(p, CHAR(filename), 0, data, size,
		CHAR(optlist));
    PDFCPP_CATCH;
}

int PDFlib::create_textflow(string text, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_create_textflow(p, CHAR(text), LEN(text),
	    CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}


void
PDFlib::curveto(double x1, double y1, double x2, double y2, double x3,
	double y3)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_curveto(p, x1, y1, x2, y2, x3, y3);
    PDFCPP_CATCH;
}

int
PDFlib::define_layer(string name, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_define_layer(p, CHAR(name), LEN(name),
	    CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

int
PDFlib::delete_pvf(string filename)
{
    int retval = 0;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_delete_pvf(p, CHAR(filename), 0);
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::delete_table(int table, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_delete_table(p, table, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::delete_textflow(int textflow)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_delete_textflow(p, textflow);
    PDFCPP_CATCH;
}


void
PDFlib::encoding_set_char(string encoding, int slot, string glyphname, int uv)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_encoding_set_char(p, CHAR(encoding), slot,
	CHAR(glyphname), uv);
    PDFCPP_CATCH;
}

void
PDFlib::end_document(string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_end_document(p, CHAR(optlist));
    PDFCPP_CATCH;
}


void
PDFlib::end_font()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_end_font(p);
    PDFCPP_CATCH;
}

void
PDFlib::end_glyph()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_end_glyph(p);
    PDFCPP_CATCH;
}

void
PDFlib::end_item(int id)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_end_item(p, id);
    PDFCPP_CATCH;
}

void
PDFlib::end_layer()
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_end_layer(p);
    PDFCPP_CATCH;
}

void
PDFlib::end_page()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_end_page(p);
    PDFCPP_CATCH;
}

void
PDFlib::end_page_ext(string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_end_page_ext(p, CHAR(optlist));
    PDFCPP_CATCH;
}


void
PDFlib::end_pattern()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_end_pattern(p);
    PDFCPP_CATCH;
}

void
PDFlib::end_template()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_end_template(p);
    PDFCPP_CATCH;
}

void
PDFlib::endpath()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_endpath(p);
    PDFCPP_CATCH;
}

void
PDFlib::fill()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_fill(p);
    PDFCPP_CATCH;
}

int
PDFlib::fill_imageblock(int page, string blockname, int image, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_fill_imageblock(p, page, CHAR(blockname),
				image, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::fill_pdfblock(int page, string blockname, int contents, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_fill_pdfblock(p, page, CHAR(blockname),
				contents, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::fill_textblock(int page, string blockname, string text, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_fill_textblock(p, page, CHAR(blockname),
			    CHAR(text), (int) LEN(text), CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::fill_stroke()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_fill_stroke(p);
    PDFCPP_CATCH;
}

int
PDFlib::findfont(string fontname, string encoding, int embed)
{
    int retval = 0;
    PDFCPP_TRY

	retval = m_PDFlib_api->PDF_findfont(p, CHAR(fontname),
		CHAR(encoding), embed);
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::fit_image (int image, double x, double y, string optlist)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_fit_image(p, image, x, y, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::fit_pdi_page (int page, double x, double y, string optlist)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_fit_pdi_page(p, page, x, y, CHAR(optlist));
    PDFCPP_CATCH;
}

string
PDFlib::fit_table(int table, double llx, double lly, double urx,
    double ury, string optlist)
{
    const char *retval = NULL;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_fit_table(p, table, llx, lly,
	    urx, ury, CHAR(optlist));
    PDFCPP_CATCH;

    if (retval)
	return retval;
    else
	return "";
}

string
PDFlib::fit_textflow(int textflow, double llx, double lly, double urx,
    double ury, string optlist)
{
    const char *retval = NULL;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_fit_textflow(p, textflow, llx, lly,
	    urx, ury, CHAR(optlist));
    PDFCPP_CATCH;

    if (retval)
	return retval;
    else
	return "";
}

void
PDFlib::fit_textline(string text, double x, double y, string optlist)
{
    PDFCPP_TRY
        m_PDFlib_api->PDF_fit_textline(p, CHAR(text), (int) LEN(text), x, y,
		CHAR(optlist));
    PDFCPP_CATCH;
}

string
PDFlib::get_apiname()
{
    const char *retval = NULL;

    PDFCPP_TRY
    {
	retval = m_PDFlib_api->PDF_get_apiname(p);
    }
    PDFCPP_CATCH;

    if (retval)
	return retval;
    else
	return "";
}

const char *
PDFlib::get_buffer(long *size)
{
    const char * retval = NULL;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_get_buffer(p, size);
    PDFCPP_CATCH;

    return retval;
}

string
PDFlib::get_errmsg()
{
    const char *retval = NULL;

    PDFCPP_TRY
    {
	retval = m_PDFlib_api->PDF_get_errmsg(p);
    }
    PDFCPP_CATCH;

    if (retval)
	return retval;
    else
	return "";
}

int
PDFlib::get_errnum()
{
    int retval = 0;

    PDFCPP_TRY retval = m_PDFlib_api->PDF_get_errnum(p);
    PDFCPP_CATCH;

    return retval;
}

void *
PDFlib::get_opaque()
{
    void * retval = NULL;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_get_opaque(p);
    PDFCPP_CATCH;

    return retval;
}

string
PDFlib::get_parameter(string key, double modifier)
{
    const char *retval = NULL;

    PDFCPP_TRY
    {
        retval = m_PDFlib_api->PDF_get_parameter(p, CHAR(key), modifier);
    }
    PDFCPP_CATCH;

    if (retval)
	return retval;
    else
	return "";
}

double
PDFlib::get_pdi_value(string key, int doc, int page, int reserved)
{
    double retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_get_pdi_value(p, CHAR(key), doc, page,
			reserved);
    PDFCPP_CATCH;

    return retval;
}

string
PDFlib::get_pdi_parameter(string key, int doc, int page, int reserved, int *len)
{
    const char *retval = NULL;

    PDFCPP_TRY
        retval = m_PDFlib_api->PDF_get_pdi_parameter(p, CHAR(key),
		    doc, page, reserved, len);
    PDFCPP_CATCH;

    if (retval)
	return retval;
    else
	return "";
}

double
PDFlib::get_value(string key, double modifier)
{
    double retval = 0;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_get_value(p, CHAR(key), modifier);
    PDFCPP_CATCH;

    return retval;
}

double
PDFlib::info_font(int font, string keyword, string optlist)
{
    double  retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_info_font(p, font, CHAR(keyword),
		CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

double
PDFlib::info_matchbox(string boxname, int num, string keyword)
{
    double  retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_info_matchbox(p, CHAR(boxname), 0,
		    num, CHAR(keyword));
    PDFCPP_CATCH;
    return retval;
}

double
PDFlib::info_table(int table, string keyword)
{
    double  retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_info_table(p, table, CHAR(keyword));
    PDFCPP_CATCH;
    return retval;
}

double
PDFlib::info_textflow(int textflow, string keyword)
{
    double  retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_info_textflow(p, textflow, CHAR(keyword));
    PDFCPP_CATCH;
    return retval;
}

double
PDFlib::info_textline(string text, string keyword, string optlist)
{
    double  retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_info_textline(p, CHAR(text), LEN(text),
	    CHAR(keyword), CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}


void
PDFlib::initgraphics()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_initgraphics(p);
    PDFCPP_CATCH;
}

void
PDFlib::lineto(double x, double y)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_lineto(p, x, y);
    PDFCPP_CATCH;
}

int
PDFlib::load_3ddata(string filename, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_load_3ddata(p, CHAR(filename),
	    0, CHAR(optlist));
    PDFCPP_CATCH;
    return retval;
}

int
PDFlib::load_font(string fontname, string encoding, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
       retval = m_PDFlib_api->PDF_load_font(p, CHAR(fontname), 0,
		CHAR(encoding), CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::load_iccprofile(string profilename, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_load_iccprofile(p, CHAR(profilename), 0,
		CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

/* p_image.c */

int
PDFlib::load_image (string imagetype, string filename, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_load_image(p, CHAR(imagetype),
		CHAR(filename), 0, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::makespotcolor(string spotname)
{
    int retval = 0;

    PDFCPP_TRY  retval = m_PDFlib_api->PDF_makespotcolor(p, CHAR(spotname), 0);
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::moveto(double x, double y)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_moveto(p, x, y);
    PDFCPP_CATCH;
}

int
PDFlib::open_CCITT(string filename, int width, int height, int BitReverse,
    int K, int BlackIs1)
{
    int retval = 0;

    PDFCPP_TRY
    {
	retval = m_PDFlib_api->PDF_open_CCITT(p, CHAR(filename), width, height,
				    BitReverse, K, BlackIs1);
    }
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::open_file(string filename)
{
    int retval = 0;

    PDFCPP_TRY	retval = m_PDFlib_api->PDF_open_file(p, CHAR(filename));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::open_image(string imagetype, string source, const char *data, long len,
    int width, int height, int components, int bpc, string params)
{
    int retval = 0;

    PDFCPP_TRY
    {
	retval = m_PDFlib_api->PDF_open_image(p, CHAR(imagetype), CHAR(source),
		    data, len, width, height, components, bpc, CHAR(params));
    }
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::open_image_file(string imagetype, string filename,
    string stringparam, int intparam)
{
    int retval = 0;

    PDFCPP_TRY
    {
	retval = m_PDFlib_api->PDF_open_image_file(p, CHAR(imagetype),
		    CHAR(filename), CHAR(stringparam), intparam);
    }
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::open_mem(writeproc_t writeproc)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_open_mem(p, writeproc);
    PDFCPP_CATCH;
}

int
PDFlib::open_pdi(string filename, string optlist, int reserved)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_open_pdi(p, CHAR(filename),
		CHAR(optlist), reserved);
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::open_pdi_document(string filename, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_open_pdi_document(p, CHAR(filename), 0,
		CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::open_pdi_page(int doc, int pagenumber, string optlist)
{
    int retval = 0;
    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_open_pdi_page(p, doc, pagenumber,
		    CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

double
PDFlib::pcos_get_number(int doc, string path)
{
    double retval = 0;

    PDFCPP_TRY
        retval = PDF_pcos_get_number(p, doc, "%s", CHAR(path));
    PDFCPP_CATCH;

    return retval;
}

string
PDFlib::pcos_get_string(int doc, string path)
{
    const char *cretval = NULL;
    string retval = "";

    PDFCPP_TRY
        cretval = PDF_pcos_get_string(p, doc, "%s", CHAR(path));
        if (cretval)
            retval = string(cretval);
    PDFCPP_CATCH;

    return retval;
}

const unsigned char *
PDFlib::pcos_get_stream(int doc, int *length, string optlist, string path)
{
    const unsigned char *retval = NULL;

    PDFCPP_TRY
        retval = PDF_pcos_get_stream(p, doc, length, CHAR(optlist),
                "%s", CHAR(path));
    PDFCPP_CATCH;

    return retval;
}


void
PDFlib::place_image(int image, double x, double y, double p_scale)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_place_image(p, image, x, y, p_scale);
    PDFCPP_CATCH;
}

void
PDFlib::place_pdi_page(int page, double x, double y, double sx, double sy)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_place_pdi_page(p, page, x, y, sx, sy);
    PDFCPP_CATCH;
}

int
PDFlib::process_pdi(int doc, int page, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_process_pdi(p, doc, page, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::rect(double x, double y, double width, double height)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_rect(p, x, y, width, height);
    PDFCPP_CATCH;
}

void
PDFlib::restore()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_restore(p);
    PDFCPP_CATCH;
}

void
PDFlib::resume_page(string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_resume_page(p, CHAR(optlist));
    PDFCPP_CATCH;
}


void
PDFlib::rotate(double phi)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_rotate(p, phi);
    PDFCPP_CATCH;
}

void
PDFlib::save()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_save(p);
    PDFCPP_CATCH;
}

void
PDFlib::scale(double sx, double sy)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_scale(p, sx, sy);
    PDFCPP_CATCH;
}

void
PDFlib::set_border_color(double red, double green, double blue)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_border_color(p, red, green, blue);
    PDFCPP_CATCH;
}

void
PDFlib::set_border_dash(double b, double w)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_border_dash(p, b, w);
    PDFCPP_CATCH;
}

void
PDFlib::set_border_style(string style, double width)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_border_style(p, CHAR(style), width);
    PDFCPP_CATCH;
}

void
PDFlib::setfont(int font, double fontsize)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setfont(p, font, fontsize);
    PDFCPP_CATCH;
}

void
PDFlib::set_gstate(int gstate)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_gstate(p, gstate);
    PDFCPP_CATCH;
}

void
PDFlib::set_info(string key, string value)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_set_info2(p, CHAR(key), CHAR(value),
		(int) LEN(value));
    PDFCPP_CATCH;
}

void
PDFlib::set_layer_dependency(string type, string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_set_layer_dependency(p, CHAR(type), CHAR(optlist));
    PDFCPP_CATCH;
}


void
PDFlib::set_parameter(string key, string value)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_parameter(p, CHAR(key), CHAR(value));
    PDFCPP_CATCH;
}

void
PDFlib::set_text_pos(double x, double y)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_text_pos(p, x, y);
    PDFCPP_CATCH;
}

void
PDFlib::set_value(string key, double value)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_set_value(p, CHAR(key), value);
    PDFCPP_CATCH;
}

void
PDFlib::setcolor(string fstype, string colorspace,
    double c1, double c2, double c3, double c4)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_setcolor(p, CHAR(fstype), CHAR(colorspace), c1, c2,
		c3, c4);
    PDFCPP_CATCH;
}

void
PDFlib::setdash(double b, double w)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setdash(p, b, w);
    PDFCPP_CATCH;
}

void
PDFlib::setdashpattern(string optlist)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setdashpattern(p, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::setflat(double flatness)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setflat(p, flatness);
    PDFCPP_CATCH;
}

void
PDFlib::setlinecap(int linecap)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setlinecap(p, linecap);
    PDFCPP_CATCH;
}

void
PDFlib::setlinejoin(int linejoin)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setlinejoin(p, linejoin);
    PDFCPP_CATCH;
}

void
PDFlib::setlinewidth(double width)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setlinewidth(p, width);
    PDFCPP_CATCH;
}

void
PDFlib::setmatrix( double a, double b, double c, double d, double e, double f)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setmatrix(p, a, b, c, d, e, f);
    PDFCPP_CATCH;
}

void
PDFlib::setmiterlimit(double miter)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setmiterlimit(p, miter);
    PDFCPP_CATCH;
}

void
PDFlib::setpolydash(float *darray, int length)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_setpolydash(p, darray, length);
    PDFCPP_CATCH;
}

int
PDFlib::shading (string shtype, double x0, double y0, double x1, double y1,
    double c1, double c2, double c3, double c4, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_shading(p, CHAR(shtype), x0, y0, x1, y1,
		    c1, c2, c3, c4, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

int
PDFlib::shading_pattern (int shade, string optlist)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_shading_pattern(p, shade, CHAR(optlist));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::shfill (int shade)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_shfill(p, shade);
    PDFCPP_CATCH;
}

void
PDFlib::show(string text)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_show2(p, CHAR(text), (int) LEN(text));
    PDFCPP_CATCH;
}

int
PDFlib::show_boxed(string text, double left, double top,
    double width, double height, string hmode, string feature)
{
    int retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_show_boxed(p, CHAR(text), left, top, width,
		    height, CHAR(hmode), CHAR(feature));
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::show_xy(string text, double x, double y)
{
    PDFCPP_TRY
    	m_PDFlib_api->PDF_show_xy2(p, CHAR(text), (int) LEN(text), x, y);
    PDFCPP_CATCH;
}

void
PDFlib::skew(double alpha, double beta)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_skew(p, alpha, beta);
    PDFCPP_CATCH;
}

double
PDFlib::stringwidth(string text, int font, double fontsize)
{
    double retval = 0;

    PDFCPP_TRY
	retval = m_PDFlib_api->PDF_stringwidth2(p, CHAR(text),
		    (int) LEN(text), font, fontsize);
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::stroke()
{
    PDFCPP_TRY	m_PDFlib_api->PDF_stroke(p);
    PDFCPP_CATCH;
}

void
PDFlib::suspend_page(string optlist)
{
    PDFCPP_TRY
	m_PDFlib_api->PDF_suspend_page(p, CHAR(optlist));
    PDFCPP_CATCH;
}

void
PDFlib::translate(double tx, double ty)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_translate(p, tx, ty);
    PDFCPP_CATCH;
}

string
PDFlib::utf16_to_utf8(string utf16string)
{
    const char *retval = NULL;

    PDFCPP_TRY
    {
        retval = m_PDFlib_api->PDF_utf16_to_utf8(p, CHAR(utf16string),
                        (int) LEN(utf16string), NULL);
    }
    PDFCPP_CATCH;

    if (retval)
        return retval;
    else
        return "";
}

string
PDFlib::utf32_to_utf16(string utf32string, string ordering)
{
    const char *buf;
    int size;
    string retval = "";

    PDFCPP_TRY
    {
        buf = m_PDFlib_api->PDF_utf32_to_utf16(p, CHAR(utf32string),
		    LEN(utf32string), CHAR(ordering), &size);
        if (buf)
                retval = string(buf, (unsigned int) size);
    }
    PDFCPP_CATCH;

    return retval;
}

string
PDFlib::utf8_to_utf16(string utf8string, string format)
{
    const char *buf;
    int size;
    string retval = "";

    PDFCPP_TRY
    {
        buf = m_PDFlib_api->PDF_utf8_to_utf16(p, CHAR(utf8string),
                                                 CHAR(format), &size);
        if (buf)
                retval = string(buf, (unsigned int) size);
    }
    PDFCPP_CATCH;

    return retval;
}

void
PDFlib::xshow(string text, const double *xadvancelist)
{
    PDFCPP_TRY	m_PDFlib_api->PDF_xshow(p, CHAR(text), (int) LEN(text),
                                                xadvancelist);
    PDFCPP_CATCH;
}
