import QtQuick 2.9
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
 id: imageRoot
    property string loadingStatus: sessionData.loadingStatus
    
    onLoadingStatusChanged: {
        ldStatus.text = "Loading: " + loadingStatus
    }
    
    Image {
        anchors.fill: parent
        source: "./bitchute-logo-page.jpg"
        
        Rectangle {
            width: parent.width
            height: parent.height
            color: "transparent"
            
            Rectangle {
                width: parent.width
                height: Kirigami.Units.gridUnit * 4
                color: Kirigami.Theme.backgroundColor
                anchors.bottom: parent.bottom
                anchors.bottomMargin: Kirigami.Units.gridUnit * 2
                anchors.horizontalCenter: parent.horizontalCenter
                z: 100
                
                Kirigami.Heading {
                    id: ldStatus
                    anchors.centerIn: parent
                    font.bold: true
                    level: 2
                    text: "Error: No Results Found"
                }
            }
        }
    }
}
