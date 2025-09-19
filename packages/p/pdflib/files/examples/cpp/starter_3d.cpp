// $Id: starter_3d.cpp,v 1.1.2.1 2008/02/20 21:47:01 rjs Exp $
// 3D Starter:
// Create a 3D model and load it into a U3D annotation.
//
// Define a 3D view and load some 3D data with the view defined. Then create
// an annotation containing the loaded 3D data with the defined 3D view as the
// initial view.
//
// Acrobat 7.07 or above is required for viewing PDF documents containing a
// 3D model.
//
// Required software: PDFlib/PDFlib+PDI/PPS 7.0.1
// Required data: U3D data file
//

#include <iostream>

#include "pdflib.hpp"

using namespace std;

int
main(void)
{
    try {
	// This is where the data files are. Adjust if necessary.
	string searchpath = "../data";
	string outfile = "starter_3d.pdf";

	// Required minimum PDFlib version
	double requiredversion = 701;
	string requiredvstr = "7.0.1";

	char buf[1024];
	char *optlist;
	int font, u3dview, u3ddata;
	PDFlib p;

        p.set_parameter("SearchPath", searchpath);

        // This means we must check return values of load_font() etc.
        p.set_parameter("errorpolicy", "return");

        // Check whether the required minimum PDFlib version is available
        double major = p.get_value("major", 0);
        double minor = p.get_value("minor", 0);
        double revision = p.get_value("revision", 0);

        if (major*100 + minor*10 + revision < requiredversion) {
            cerr << "Error: PDFlib " << requiredvstr
		<< " or above is required" << endl;
            return 2;
        }

        // Start the document
        if (p.begin_document(outfile, "") == -1) {
            cerr << "Error: " << p.get_errmsg() << endl;
            return 2;
        }

        p.set_info("Creator", "PDFlib Cookbook");
        p.set_info("Title", "starter_3d");

        font = p.load_font("Helvetica", "winansi", "");
        if (font == -1) {
            cerr << "Error: " << p.get_errmsg() << endl;
            return 2;
        }

        p.begin_page_ext(0, 0, "width=a4.width height=a4.height");

        // Define a U3D view
        optlist = "name=FirstView background={fillcolor={rgb 1 0.5 0.1}}";
        if ((u3dview = p.create_3dview("First view", optlist)) == -1) {
            cerr << "Error: " << p.get_errmsg() << endl;
            return 2;
        }

        // Load some U3D data with the view defined above
	sprintf(buf, "views={%d}", u3dview);
        if ((u3ddata = p.load_3ddata("box.u3d", buf)) == -1) {
            cerr << "Error: " << p.get_errmsg() << endl;
            return 2;
        }

        // Create an annotation containing the loaded U3D data with the
        // defined 3D view as the initial view
        //
	sprintf(buf, "name=annot usercoordinates contents=U3D 3ddata= %d"
            " 3dactivate={enable=open} 3Dinitialview=%d", u3ddata, u3dview);
        p.create_annotation(116, 400, 447, 580, "3D", buf);

        p.end_page_ext("");

        p.end_document("");

    }

    catch (PDFlib::Exception &ex) {
        cerr << "PDFlib exception occurred in hello sample: " << endl;
        cerr << "[" << ex.get_errnum() << "] " << ex.get_apiname()
            << ": " << ex.get_errmsg() << endl;
        return 2;
    }



    return 0;
}
