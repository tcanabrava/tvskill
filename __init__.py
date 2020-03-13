# -*- coding: utf-8 -*-

import time
import urllib
from os.path import dirname
import pafy
import sys
import json
import requests
import timeago, datetime
import dateutil.parser
import youtube_dl
if sys.version_info[0] < 3:
    from urllib import quote
    from urllib2 import urlopen
else:
    from urllib.request import urlopen
    from urllib.parse import quote, urlencode
from adapt.intent import IntentBuilder
from bs4 import BeautifulSoup, SoupStrainer, Tag
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
from collections import deque

__author__ = 'aix'

class BitChuteSkill(MycroftSkill):
    def __init__(self):
        super(BitChuteSkill, self).__init__(name="BitChuteSkill")
        self.live_category = None
        self.recentList = deque()
        self.recentPageObject = {}
        self.nextSongList = None
        self.lastSong = None
        self.videoPageObject = {}
        self.isTitle = None
        self.newsCategoryList = {}
        self.musicCategoryList = {}
        self.techCategoryList = {}
        self.polCategoryList = {}
        self.gamingCategoryList = {}
        self.searchCategoryList = {}
        self.lastVideoDetails = {}
        
    def initialize(self):
        self.load_data_files(dirname(__file__))
        
        self.bus.on('bitchute-skill.aiix.home', self.launcherId)
        
        bitchutepause = IntentBuilder("BitChutePauseKeyword"). \
            require("BitChutePauseKeyword").build()
        self.register_intent(bitchutepause, self.bitchutepause)

        bitchuteresume = IntentBuilder("BitChuteResumeKeyword"). \
            require("BitChuteResumeKeyword").build()
        self.register_intent(bitchuteresume, self.bitchuteresume)

        #bitchutesearchpage = IntentBuilder("BitChuteSearchPageKeyword"). \
            #require("BitChuteSearchPageKeyword").build()
        #self.register_intent(bitchutesearchpage, self.bitchutesearchpage)

        bitchutelauncherId = IntentBuilder("BitChuteLauncherId"). \
            require("BitChuteLauncherIdKeyword").build()
        self.register_intent(bitchutelauncherId, self.launcherId)
        
        self.add_event('aiix.bitchute-skill.playvideo_id', self.play_event)
        
        self.gui.register_handler('BitChuteSkill.SearchLive',
                                  self.searchLive)
        
        self.gui.register_handler('BitChuteSkill.RefreshWatchList', self.refreshWatchList)
        self.gui.register_handler('BitChuteSkill.RelatedWatchList', self.bitchuterelatedpage)
        
    def launcherId(self, message):
        self.show_homepage({})
        

    def getListSearch(self, text):
        query = quote(text)
        url = "https://www.youtube.com/results?search_query=" + quote(query)
        response = urlopen(url)
        html = response.read()
        a_tag = SoupStrainer('a')
        soup = BeautifulSoup(html, 'html.parser', parse_only=a_tag)
        for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
            if "googleads" not in vid['href'] and not vid['href'].startswith(
                    u"/user") and not vid['href'].startswith(u"/channel"):
                id = vid['href'].split("v=")[1].split("&")[0]
                return id

    def moreRandomListSearch(self, text):
        LOG.info(text)
        query = quote(text)
        try:
            querySplit = text.split()
            LOG.info(querySplit)
            searchQuery = "*," + quote(querySplit[0]) + quote(querySplit[1]) + ",*"
        
        except:
            LOG.info("fail")
            searchQuery = "*," + quote(query) + ",*"

        LOG.info(searchQuery)
        return searchQuery    
    
    def searchLive(self, message):
        videoList = []
        videoList.clear()
        videoPageObject = {}
        try:
            query = message.data["Query"]
            LOG.info("I am in search Live")
            url = "https://search.bitchute.com/renderer?use=bitchute-json&name=Search&login=bcadmin&key=7ea2d72b62aa4f762cc5a348ef6642b8&query={0}".format(query)
            response = requests.get(url)
            html = response.text
            self.searchCategoryList["videoList"] = self.process_soup_additional(html)
            self.gui["searchListBlob"] = self.searchCategoryList
            self.gui["bgImage"] = quote(query)
            self.gui.show_page("HomePage.qml", override_idle=True)
        except:
            LOG.debug("error")
        
    @intent_file_handler('bitchute.intent')
    def bitchute(self, message):
        self.stop()
        self.gui.clear()
        self.enclosure.display_manager.remove_active()
        utterance = message.data['videoname'].lower()
        self.get_play_video(utterance)
    
    def bitchute_play_video(self, PlayObject):
        self.gui["status"] = str("play")
        self.gui["video"] = PlayObject['playableUrl']
        self.gui["currenturl"] = PlayObject['videoID']
        self.gui["currenttitle"] = PlayObject['videoTitle']
        self.gui["setTitle"] = PlayObject['videoTitle']
        self.gui["viewCount"] = PlayObject['videoViews']
        self.gui["publishedDate"] = PlayObject['videoUploadDate']
        self.gui["videoAuthor"] = PlayObject['videoChannel']
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["relatedVideoListBlob"] = ""
        self.gui["nextSongTitle"] = ""
        self.gui["nextSongImage"] = ""
        self.gui["nextSongID"] = ""
        self.bitchuterelatedpage(PlayObject['videoID'])
        self.gui.show_pages(["BitchutePlayer.qml", "RelatedPage.qml"], 0, override_idle=True)
        #self.recentList.appendleft({"videoID": getvid, "videoTitle": video.title, "videoImage": video.thumb})
        #self.youtubesearchpagesimple(utterance)
        #self.isTitle = video.title
        
    def bitchutepause(self, message):
        self.gui["status"] = str("pause")
        self.gui.show_page("BitchutePlayer.qml")
    
    def bitchuteresume(self, message):
        self.gui["status"] = str("play")
        self.gui.show_page("BitchutePlayer.qml")
        
    def bitchuterelatedpage(self, vidId):
        videoUrlId = vidId
        videoList = []
        videoList.clear()
        videoPageObject = {}
        videoList = self.process_related_videos(videoUrlId)
        videoPageObject['videoList'] = videoList
        self.gui["relatedVideoListBlob"] = videoPageObject
        
    def bitchutesearchpagesimple(self, query):
        LOG.info(query)
        videoList = []
        videoList.clear()
        videoPageObject = {}
        vid = self.moreRandomListSearch(query)
        url = "https://www.youtube.com/results?search_query=" + vid
        response = urlopen(url)
        html = response.read()
        videoList = self.process_soup_additional(html)        
        videoPageObject['videoList'] = videoList
        self.gui["videoListBlob"] = videoPageObject
        self.recentPageObject['recentList'] = list(self.recentList)
        self.gui["recentListBlob"] = self.recentPageObject
        
    def show_homepage(self, message):
        LOG.info("I AM IN HOME PAGE FUNCTION")
        self.gui.clear()
        self.enclosure.display_manager.remove_active()
        self.gui["loadingStatus"] = ""
        self.gui.show_page("BitchuteLogo.qml")
        self.process_home_page()

    def process_home_page(self):
        LOG.info("I AM IN HOME PROCESS PAGE FUNCTION")
        self.gui.show_page("BitchuteLogo.qml")
        self.gui["loadingStatus"] = "Fetching News"
        self.newsCategoryList['videoList'] = self.build_category_list("news")
        self.gui["loadingStatus"] = "Fetching Music"
        self.musicCategoryList['videoList'] = self.build_category_list("music")
        self.gui.clear()
        self.enclosure.display_manager.remove_active()
        self.show_search_page()
        self.techCategoryList['videoList'] = self.build_category_list("science")
        self.gui["techListBlob"] = self.techCategoryList
        self.polCategoryList['videoList'] = self.build_category_list("entertainment")
        self.gui["polListBlob"] = self.polCategoryList
        self.gamingCategoryList['videoList'] = self.build_category_list("gaming")
        self.gui["gamingListBlob"] = self.gamingCategoryList     
        LOG.info("I AM NOW IN REMOVE LOGO PAGE FUNCTION")

    def show_search_page(self):
        LOG.info("I AM NOW IN SHOW SEARCH PAGE FUNCTION")
        LOG.info(self.techCategoryList)
        self.gui["newsListBlob"] = self.newsCategoryList
        self.gui["musicListBlob"] = self.musicCategoryList
        self.gui["techListBlob"] = self.techCategoryList
        self.gui["polListBlob"] = self.polCategoryList
        self.gui["gamingListBlob"] = self.gamingCategoryList
        self.gui["searchListBlob"] = ""
        self.gui["relatedVideoListBlob"] = ""
        self.gui["previousAvailable"] = False
        self.gui["nextAvailable"] = True
        self.gui["bgImage"] = self.live_category
        self.gui.show_page("HomePage.qml", override_idle=True)
        
    def play_event(self, message):
        urlvideo = "https://www.bitchute.com/video/{0}".format(message.data['vidID'])
        self.lastSong = message.data['vidID']
        video = self.process_bitchute_video_type(urlvideo)
        LOG.info(video)
        self.speak("Playing")
        self.gui["video"] = str(video)
        self.gui["status"] = str("play")
        self.gui["currenturl"] = str(message.data['vidID'])
        self.gui["currenttitle"] = str(message.data['vidTitle'])
        self.gui["setTitle"] = str(message.data['vidTitle'])
        self.gui["viewCount"] = str(message.data['vidViews'])
        self.gui["publishedDate"] = str(message.data['vidUploadDate'])
        self.gui["videoAuthor"] = str(message.data['vidChannel'])
        if "1n" in self.gui["videoAuthor"]:
            self.gui["videoAuthor"] = self.extractVideoAuthor(message.data['vidID'])
        self.gui["relatedVideoListBlob"] = ""
        self.gui.show_pages(["BitchutePlayer.qml", "RelatedPage.qml"], 0, override_idle=True)
        self.bitchuterelatedpage(message.data['vidID'])
        self.isTitle = str(message.data['vidTitle'])

    def stop(self):
        self.enclosure.bus.emit(Message("metadata", {"type": "stop"}))
        pass

    def process_soup_additional(self, htmltype):
        videoList = []
        videoList.clear()
        soup = BeautifulSoup(htmltype)
        getVideoDetails = zip(soup.findAll(attrs={'class': 'ossfieldrdr1'}), soup.findAll('img'), soup.findAll(attrs={'class': 'ossfieldrdr4'}), soup.findAll(attrs={'class': 'ossfieldrdr6'}))
        for vid in getVideoDetails:
            videoID = vid[0].contents[1]['href'].split("/")[4]
            videoTitle = vid[0].contents[1].text
            videoImage = vid[1]['src']
            nonPUD1 = vid[2].text.strip()
            nonPUD2 = nonPUD1.rstrip()
            videoUploadDate = self.build_upload_date(nonPUD2)
            LOG.info(videoUploadDate)
            tempVideoViews = vid[3].text.replace(">", "").strip().rstrip()
            videoViews = str(tempVideoViews.lstrip('0') + " " + "views")
            videoChannel = self.getChannelName(videoID)
            if videoChannel is not None:
                videoList.append({"videoID": videoID, "videoTitle": videoTitle, "videoImage": videoImage, "videoChannel": videoChannel, "videoViews": videoViews, "videoUploadDate": videoUploadDate, "videoDuration": " "})

        return videoList
    
    def process_voice_play(self, query):
        videoUrl = None
        videoUrlList = []
        videoUrlList.clear()
        url = "https://search.bitchute.com/renderer?use=bitchute-json&name=Search&login=bcadmin&key=7ea2d72b62aa4f762cc5a348ef6642b8&query={0}".format(query)
        response = requests.get(url)
        html = response.text
        a_tag = SoupStrainer('a')
        soup = BeautifulSoup(html, 'html.parser', parse_only=a_tag)
        for vid in soup.findAll('a'):
            if not vid.has_attr('class'):
                if vid.has_attr('target'):
                    if not vid.find('img'):
                        videoUrl = vid['href']
                        videoUrlList.append(videoUrl)
        
        return videoUrlList
    
    def process_category_listing(self, htmltype):
        videoList = []
        videoList.clear()
        soup = BeautifulSoup(htmltype)
        getVideoDetails = soup.findAll(attrs={'class': 'video-card'})
        for vid in getVideoDetails:
            videoID = vid.contents[1]['href'].split("/")[2]
            videoImage = vid.contents[1].contents[1].contents[1]['data-src']
            tempVideoViews = vid.contents[1].contents[1].contents[5].contents[1]
            videoViews = str(tempVideoViews + " " + "views")
            videoTitle = vid.contents[3].contents[1].contents[0].contents[0]
            videoUploadDate = vid.contents[3].contents[5].contents[0]
            videoDuration = vid.contents[1].contents[1].contents[7].text
            tempVidChannel = vid.contents[3].contents[3].contents[0].contents[0]
            if not type(tempVidChannel) is Tag:
                videoChannel = vid.contents[3].contents[3].contents[0].contents[0]
            else:
                videoChannel = "Hidden"
            
            videoList.append({"videoID": videoID, "videoTitle": videoTitle, "videoImage": videoImage, "videoChannel": videoChannel, "videoViews": videoViews, "videoUploadDate": videoUploadDate, "videoDuration": videoDuration})
            
        return videoList
    
    def process_bitchute_video_type(self, videolink):
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        
        try:
            with ydl:
                result = ydl.extract_info(
                    videolink,
                    download=False # We just want to extract the info
                )
                if 'entries' in result:
                    video = result['entries'][0]
                else:
                    video = result
        
            video_url = video['url']
            return video_url
        
        except:
            self.gui.clear()
            self.enclosure.display_manager.remove_active()
            self.gui.show_page("BitchuteFailed.qml", override_idle=True)
            return None

    def refreshWatchList(self, message):
        try:
            self.youtubesearchpagesimple(message.data["title"])
        except:
            self.youtubesearchpagesimple(self.isTitle)
        
    @intent_file_handler('bitchute-repeat.intent')
    def bitchute_repeat_last(self):
        lastVideo = self.lastVideoDetails
        self.bitchute_play_video(lastVideo)
        
    def build_category_list(self, category):
        url = "https://www.bitchute.com/category/{0}".format(category)
        LOG.info(url)
        response = requests.get(url)
        html = response.text
        videoList = self.process_category_listing(html)
        return videoList
    
    def clear_previous_video(self):
        self.gui["setTitle"] = ""
        self.gui["video"] = ""
        self.gui["status"] = "stop"
        self.gui["currenturl"] = ""
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["relatedVideoListBlob"] = ""
        self.gui["videoThumb"] = ""
        self.gui.show_pages(["BitchutePlayer.qml", "RelatedPage.qml"], 0, override_idle=True)
    
    def set_video_thumb(self, thumb_url):
        self.gui["setTitle"] = ""
        self.gui["video"] = ""
        self.gui["status"] = "stop"
        self.gui["currenturl"] = ""
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["relatedVideoListBlob"] = ""
        self.gui["videoThumb"] = thumb_url
        self.gui.show_pages(["BitchutePlayer.qml", "RelatedPage.qml"], 0, override_idle=True)
        
    def get_play_video(self, query):
        self.clear_previous_video()
        url = "https://search.bitchute.com/renderer?use=bitchute-json&name=Search&login=bcadmin&key=7ea2d72b62aa4f762cc5a348ef6642b8&query={0}".format(query)
        response = requests.get(url)
        html = response.text
        processed_result = self.process_soup_additional(html)
        try:
            vid = processed_result[0]['videoID']
            vid_thumb = processed_result[0]['videoImage']
            self.set_video_thumb(vid_thumb)
            video_url = "https://www.bitchute.com/video/{0}".format(vid)
            playable_url = self.process_bitchute_video_type(video_url)
            if playable_url is not None:
                playableObj = {'videoID': processed_result[0]['videoID'], 'videoTitle': processed_result[0]['videoTitle'], 'videoImage': processed_result[0]['videoImage'], 'videoChannel': processed_result[0]['videoChannel'], 'videoViews': processed_result[0]['videoViews'], 'videoUploadDate': processed_result[0]['videoUploadDate'], 'playableUrl': playable_url}
                self.lastVideoDetails = playableObj
                self.bitchute_play_video(playableObj)
            else:
                self.gui.clear()
                self.enclosure.display_manager.remove_active()
                self.gui.show_page("BitchuteFailed.qml", override_idle=True)
                
        except:
            self.gui.clear()
            self.enclosure.display_manager.remove_active()
            self.gui.show_page("BitchuteFailed.qml", override_idle=True)
                    
    def getChannelName(self, videoId):
        url = "https://www.bitchute.com/video/{0}".format(videoId)
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html)
        getChannelName = soup.findAll(attrs={'class': 'video-card-channel'})
        for vid in getChannelName:
            return vid.contents[0].text
        
    def process_related_videos(self, videoUrl):
        relatedVideoList = []
        relatedVideoList.clear()
        url = "https://www.bitchute.com/video/{0}".format(videoUrl)
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html)
        getRelatedVids = soup.findAll(attrs={'class': 'video-card'})
        for vid in getRelatedVids:
            videoID = vid.contents[1]['href'].split("/")[2]
            videoImage = vid.contents[1].contents[1].contents[1]['data-src']
            videoViews = vid.contents[1].contents[1].contents[5].contents[1]
            videoTitle = vid.contents[3].contents[1].contents[0].contents[0]
            videoUploadDate = vid.contents[3].contents[3].text
            relatedVideoList.append({"videoID": videoID, "videoTitle": videoTitle, "videoImage": videoImage, "videoViews": videoViews, "videoUploadDate": videoUploadDate})

        return relatedVideoList
    
    def build_upload_date(self, update):
        yourdate = dateutil.parser.parse(update)
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds = 60 * 3.4)
        date = yourdate
        dtstring = timeago.format(date, now)
        
        return dtstring
    
    def extractVideoAuthor(self, vid):
        url = "https://www.bitchute.com/video/{0}".format(vid)
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html)
        getVideoDetails = soup.find("div", {"class":"details"})
        publisher = getVideoDetails.contents[1].text
        LOG.info(publisher)
        
        return publisher
        
def create_skill():
    return BitChuteSkill()
