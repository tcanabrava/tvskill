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
            console.log("here in focus")
            videoListView.forceActiveFocus()
        }
    }
    
    Views.TileView {
        id: videoListView
        focus: true
        clip: true
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        property string currentVideoTitle
        property string currentVideoId
        property string currentVideoViewCount
        property string currentVideoAuthor
        property string currentVideoUploadDate
        delegate: Delegates.VideoCard{}
        
        KeyNavigation.up: videoQueryBox
        KeyNavigation.down: controlBarItem
                
        Keys.onReturnPressed: {
            busyIndicatorPop.open()
            if(focus){
                Mycroft.MycroftController.sendRequest("aiix.bitchute-skill.playvideo_id", {vidID: currentVideoId, vidTitle: currentVideoTitle, vidViewCount: currentVideoViewCount, vidUploadDate: currentVideoUploadDate, vidAuthor: currentVideoAuthor})
            }
        }
            
        onCurrentItemChanged: {
            currentVideoId = videoListView.currentItem.videoID
            currentVideoTitle = videoListView.currentItem.videoTitle
            currentVideoAuthor = videoListView.currentItem.videoChannel
            currentVideoViewCount = videoListView.currentItem.videoViews
            currentVideoUploadDate = videoListView.currentItem.videoUploadDate
            console.log(videoListView.currentItem.videoTitle)
        }
    }
}
