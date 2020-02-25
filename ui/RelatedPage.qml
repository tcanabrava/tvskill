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

Mycroft.Delegate {
    id: root
    property var videoListModel: sessionData.relatedVideoListBlob.videoList
    skillBackgroundSource: "https://source.unsplash.com/weekly?music"
    fillWidth: true
    
    onFocusChanged: {
        if(focus){
            console.log("here in focus")
            relatedVideoListView.forceActiveFocus()
        }
    }
    
    Keys.onBackPressed: {
        parent.parent.parent.currentIndex--
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }
    
    Kirigami.Heading {
        id: rltdHeading
        anchors.top: parent.top
        anchors.topMargin: Kirigami.Units.smallSpacing
        anchors.left: parent.left
        anchors.leftMargin: Kirigami.Units.largeSpacing
        text: "Related Videos"
        level: 2
    }
    
    Kirigami.Separator {
        id: rltdSep
        anchors.top: rltdHeading.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        anchors.topMargin: Kirigami.Units.smallSpacing
    }
    
    Views.TileView {
        id: relatedVideoListView
        focus: true
        clip: true
        model: videoListModel
        anchors.top: rltdSep.bottom
        anchors.topMargin: Kirigami.Units.smallSpacing
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        property string currentVideoTitle
        property string currentVideoId
        property string currentVideoViewCount
        property string currentVideoAuthor
        property string currentVideoUploadDate
        delegate: Delegates.VideoCardRelated{}
        
        Keys.onReturnPressed: {
            busyIndicatorPop.open()
            if(focus){
                Mycroft.MycroftController.sendRequest("aiix.bitchute-skill.playvideo_id", {vidID: currentVideoId, vidTitle: currentVideoTitle, vidViewCount: currentVideoViewCount, vidUploadDate: currentVideoUploadDate, vidAuthor: currentVideoAuthor})
            }
        }
            
        onCurrentItemChanged: {
            currentVideoId = relatedVideoListView.currentItem.videoID
            currentVideoTitle = relatedVideoListView.currentItem.videoTitle
            currentVideoViewCount = relatedVideoListView.currentItem.videoViews
            currentVideoUploadDate = relatedVideoListView.currentItem.videoUploadDate
            console.log(relatedVideoListView.currentItem.videoTitle)
        }
    }
}
 
