import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    function nextSlide() {
        console.log("QML Component (default slideshow) Next slide");
        presentation.goToNextSlide();
    }

    Timer {
        id: advanceTimer
        interval: 30000
        running: true
        repeat: true
        onTriggered: nextSlide()
    }

    Slide {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            border.width: 0
            color: "#2f343f"

            Image {
                id: slide_community
                source: "slide-community.png"
                fillMode: Image.PreserveAspectFit
                anchors.fill: parent
            }
        }
    }

    Slide {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            border.width: 0
            color: "#2f343f"

            Image {
                id: slide_socials
                source: "slide-socials.png"
                fillMode: Image.PreserveAspectFit
                anchors.fill: parent
            }
        }
    }

    Slide {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            border.width: 0
            color: "#2f343f"

            Image {
                id: slide_helpcenter
                source: "slide-helpcenter.png"
                fillMode: Image.PreserveAspectFit
                anchors.fill: parent
            }
        }
    }

    Slide {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            border.width: 0
            color: "#2f343f"

            Image {
                id: slide_donations
                source: "slide-donations.png"
                fillMode: Image.PreserveAspectFit
                anchors.fill: parent
            }
        }
    }

    // When this slideshow is loaded as a V1 slideshow, only
    // activatedInCalamares is set, which starts the timer (see above).
    //
    // In V2, also the onActivate() and onLeave() methods are called.
    // These example functions log a message (and re-start the slides
    // from the first).
    function onActivate() {
        console.log("QML Component (default slideshow) activated");
        presentation.currentSlide = 0;
    }

    function onLeave() {
        console.log("QML Component (default slideshow) deactivated");
    }
}
