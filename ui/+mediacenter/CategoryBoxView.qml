/*
 *  Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.

 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.

 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.9
import QtQuick.Layouts 1.4
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.3
import org.kde.kirigami 2.8 as Kirigami
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents3
import org.kde.plasma.components 2.0 as PlasmaComponents
import Mycroft 1.0 as Mycroft
import "+mediacenter/views" as Views
import "+mediacenter/delegates" as Delegates

Item {
    property alias model: videoListView.model
    Layout.fillWidth: true
    Layout.fillHeight: true
    
    onFocusChanged: {
        if(focus){
            searchBarArea.forceActiveFocus()
        }
    }
    
    function searchBitChuteLiveResults(query){
        triggerGuiEvent("BitChuteSkill.SearchLive", {"Query": query})
        categoryLayout.currentIndex = 5
        searchQuery = query
    }
    
    function returnCategory(){
        switch(catName){
            case "News":
                return homeCatButton
                break
            case "Music":
                return musicCatButton
                break
            case "Technology":
                return techCatButton
                break
            case "Entertainment":
                return entertainmentCatButton
                break
            case "Gaming": 
                return gamingCatButton
                break
            case "Search Results":
                return searchCatButton
                break
        }
    }
    
    Rectangle {
        id: searchBarArea
        anchors.top: parent.top
        anchors.topMargin: Kirigami.Units.largeSpacing
        anchors.horizontalCenter: parent.horizontalCenter
        height: Kirigami.Units.gridUnit * 3
        width: parent.width / 3
        radius: 12
        color: searchBarArea.activeFocus ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.95) : Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.95)
                
        Keys.onReturnPressed: {
            videoQueryBox.forceActiveFocus()
        }
        
        KeyNavigation.up: returnCategory()
        KeyNavigation.down: videoListView
        
        RowLayout {
            anchors.fill: parent
            TextField {
                id: videoQueryBox
                Layout.leftMargin: Kirigami.Units.largeSpacing
                Layout.fillWidth: true
                placeholderText: "Search here..."
                Layout.fillHeight: true
                text: searchQuery.length > 0 ? searchQuery : ""
                onAccepted: {
                    searchBitChuteLiveResults(videoQueryBox.text)
                }
                KeyNavigation.down: videoListView
                KeyNavigation.right: searchVideoQuery
                
                onTextChanged: {
                    searchQuery = videoQueryBox.text
                }
            }
            
            Kirigami.Icon {
                id: searchVideoQuery
                Layout.preferredWidth: Kirigami.Units.gridUnit * 2
                Layout.fillHeight: true
                source: "search" 
                KeyNavigation.left: videoQueryBox
                KeyNavigation.down: videoListView
                
                Keys.onReturnPressed: {
                    searchBitChuteLiveResults(videoQueryBox.text)
                }
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        searchBitChuteLiveResults(videoQueryBox.text)
                    }
                }
                
                ColorOverlay {
                    anchors.fill: parent
                    source: searchVideoQuery
                    color: Kirigami.Theme.highlightColor
                    visible: searchVideoQuery.activeFocus ? 1 : 0
                }
            }
        }
    }
    
    Views.TileView {
        id: videoListView
        focus: true
        title: " "
        anchors {
            top: searchBarArea.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        delegate: Delegates.VideoCard {
            width: videoListView.cellWidth
            height: videoListView.cellHeight
        }
        cellWidth: view.width / 4
        cellHeight: cellWidth / 1.8 + Kirigami.Units.gridUnit * 5
        KeyNavigation.up: searchBarArea
    }
}
