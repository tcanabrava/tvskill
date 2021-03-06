/*
 *  Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
 *  Copyright 2018 Marco Martin <mart@kde.org>
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

Mycroft.Delegate {
    id: delegate
    property var newsListModel: sessionData.newsListBlob.videoList
    property var musicListModel: sessionData.musicListBlob.videoList
    property var techListModel: sessionData.techListBlob.videoList
    property var polListModel: sessionData.polListBlob.videoList
    property var gamingListModel: sessionData.gamingListBlob.videoList
    property var searchListModel: sessionData.searchListBlob.videoList
    property var historyListModel: sessionData.historyListBlob.videoList
    property bool searchComplete: sessionData.searchComplete
    property bool busyIndicate: false
    property string searchQuery
    
    fillWidth: true
    
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0
    
    skillBackgroundSource: sessionData.bgImage ? "https://source.unsplash.com/weekly?" + sessionData.bgImage : "https://source.unsplash.com/weekly?music"

    Connections {
        target: Mycroft.MycroftController
        onIntentRecevied: {
            if(type == "speak") {
                busyIndicatorPop.close()
                busyIndicate = false
            }
        }
    }
    
    onNewsListModelChanged: {
        newsCatView.model = newsListModel
    }
    
    onMusicListModelChanged: {
        musicCatView.model = musicListModel
    }
    
    onTechListModelChanged: {
        techCatView.model = techListModel
    }
    
    onPolListModelChanged: {
        polCatView.model = polListModel
    }
    
    onGamingListModelChanged: {
        gamingCatView.model = gamingListModel
    }
    
    onSearchListModelChanged: {
        searchCatView.model = searchListModel
        console.log("SearchListModelChanged")
        busyIndicatorPop.close()
    }
    
    onSearchCompleteChanged: {
        busyIndicatorPop.close()
    }
    
    onFocusChanged: {
        busyIndicatorPop.close()
        busyIndicate = false
        if(delegate.focus){
            console.log("focus is here")
        }
    }
    
    Keys.onBackPressed: {
        parent.parent.parent.currentIndex++
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }
    
    ColumnLayout {
        id: colLay1
        anchors.fill: parent
        
        Rectangle {
            color: Qt.rgba(0, 0, 0, 0.8)
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 3 
            Layout.maximumHeight: Kirigami.Units.gridUnit * 4
            z: 100
            
            RowLayout {
                id: categoryRepeater
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    bottom: parent.bottom
                }
                anchors.leftMargin: Kirigami.Units.gridUnit
                anchors.rightMargin: Kirigami.Units.gridUnit
                
                TopBarTabButton {
                    id: homeCatButton
                    KeyNavigation.right: musicCatButton
                    KeyNavigation.down: categoryLayout
                    checked: categoryLayout.currentIndex == 0
                    text: "News"
                    onClicked: {
                        categoryLayout.currentIndex = 0
                    }
                }
                
                TopBarTabButton {
                    id: musicCatButton
                    KeyNavigation.right: techCatButton
                    KeyNavigation.left: newsCatButton
                    KeyNavigation.down: categoryLayout
                    checked: categoryLayout.currentIndex == 1
                    text: "Music"
                    onClicked: {
                        categoryLayout.currentIndex = 1
                    }
                }
                
                TopBarTabButton {
                    id: techCatButton
                    KeyNavigation.right: polCatButton
                    KeyNavigation.left: musicCatButton
                    KeyNavigation.down: categoryLayout
                    checked: categoryLayout.currentIndex == 2
                    text: "Technology"
                    onClicked: {
                        categoryLayout.currentIndex = 2
                    }
                }
                
                TopBarTabButton {
                    id: entertainmentCatButton
                    KeyNavigation.right: gamingCatButton
                    KeyNavigation.left: techCatButton
                    KeyNavigation.down: categoryLayout
                    checked: categoryLayout.currentIndex == 3
                    text: "Entertainment"
                    onClicked: {
                        categoryLayout.currentIndex = 3
                    }
                }
                
                TopBarTabButton {
                    id: gamingCatButton
                    KeyNavigation.left: polCatButton
                    KeyNavigation.right: searchCatButton
                    KeyNavigation.down: categoryLayout
                    checked: categoryLayout.currentIndex == 4
                    text: "Gaming"
                    onClicked: {
                        categoryLayout.currentIndex = 4
                    }
                }
                
                TopBarTabButton {
                    id: searchCatButton
                    KeyNavigation.left: gamingCatButton
                    KeyNavigation.down: categoryLayout
                    checked: categoryLayout.currentIndex == 5
                    text: "Search"
                    onClicked: {
                        categoryLayout.currentIndex = 5
                    }
                }
            }
        }
                
        StackLayout {
            id: categoryLayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.topMargin: Kirigami.Units.largeSpacing * 2
            currentIndex: 0
            
            onFocusChanged: {
                if(focus){
                    categoryLayout.itemAt(currentIndex).forceActiveFocus()
                }
            }
            
            CategoryBoxView {
                id: newsCatView
                property string catName: "News"
            }
            
            CategoryBoxView {
                id: musicCatView
                property string catName: "Music"
            }
            
            CategoryBoxView {
                id: techCatView
                property string catName: "Technology"
            }
            
            CategoryBoxView {
                id: polCatView
                property string catName: "Entertainment"
            }
            
            CategoryBoxView {
                id: gamingCatView
                property string catName: "Gaming"
            }
            
            CategoryBoxView  {
                id: searchCatView
                property string catName: "Search Results"
            }
        }
    }
    
    Popup {
        id: busyIndicatorPop
        width: parent.width
        height: parent.height
        background: Rectangle {
            anchors.fill: parent
            color: Qt.rgba(0, 0, 0, 0.5)
        }
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
        
        BusyIndicator {
            running: busyIndicate
            anchors.centerIn: parent
        }
        
        onOpened: {
            busyIndicate = true
        }
        
        onClosed: {
            busyIndicate = false
        }
    }

    Component.onCompleted: {
        categoryLayout.itemAt(categoryLayout.currentIndex).forceActiveFocus()
    }
}

