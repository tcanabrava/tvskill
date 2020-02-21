# -*- coding: utf-8 -*-

import time
import urllib
from os.path import dirname
import pafy
import sys
import json
import requests
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
        self.nextpage_url = None
        self.previouspage_url = None
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
        
    def initialize(self):
        self.load_data_files(dirname(__file__))
        
        self.bus.on('bitchute-skill.aiix.home', self.launcherId)
        
        bitchutepause = IntentBuilder("BitChutePauseKeyword"). \
            require("BitChutePauseKeyword").build()
        self.register_intent(bitchutepause, self.bitchutepause)

        bitchuteresume = IntentBuilder("BitChuteResumeKeyword"). \
            require("BitChuteResumeKeyword").build()
        self.register_intent(bitchuteresume, self.bitchuteresume)

        bitchutesearchpage = IntentBuilder("BitChuteSearchPageKeyword"). \
            require("BitChuteSearchPageKeyword").build()
        self.register_intent(bitchutesearchpage, self.bitchutesearchpage)

        bitchutelauncherId = IntentBuilder("BitChuteLauncherId"). \
            require("BitChuteLauncherIdKeyword").build()
        self.register_intent(bitchutelauncherId, self.launcherId)
        
        self.add_event('aiix.bitchute-skill.playvideo_id', self.play_event)
        
        self.gui.register_handler('BitChuteSkill.SearchLive',
                                  self.searchLive)
        
        self.gui.register_handler('BitChuteSkill.RefreshWatchList', self.refreshWatchList)
        
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
            self.searchCategoryList["videoList"] = self.build_category_list(quote(query))
            self.gui["searchListBlob"] = self.searchCategoryList
            self.gui["previousAvailable"] = False
            self.gui["nextAvailable"] = True
            self.gui["bgImage"] = quote(query)
            self.gui.show_page("BitchuteLiveSearch.qml", override_idle=True)
        except:
            LOG.debug("error")
        
    @intent_file_handler('bitchute.intent')
    def youtube(self, message):
        self.stop()
        self.gui.clear()
        self.enclosure.display_manager.remove_active()
        utterance = message.data['videoname'].lower()
        self.youtube_play_video(utterance)
    
    def youtube_play_video(self, utterance):
        self.gui["setTitle"] = ""
        self.gui["video"] = ""
        self.gui["status"] = "stop"
        self.gui["currenturl"] = ""
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["videoThumb"] = ""
        url = "https://www.youtube.com/results?search_query=" + quote(utterance)
        response = urlopen(url)
        html = response.read()
        a_tag = SoupStrainer('a')
        soup = BeautifulSoup(html, 'html.parser', parse_only=a_tag)
        self.gui["video"] = ""
        self.gui["status"] = "stop"
        self.gui["currenturl"] = ""
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["videoThumb"] = ""
        self.gui.show_pages(["YoutubePlayer.qml", "YoutubeSearch.qml"], 0, override_idle=True)
        rfind = soup.findAll(attrs={'class': 'yt-uix-tile-link'})
        try:
            vid = str(rfind[0].attrs['href'])
            veid = "https://www.youtube.com{0}".format(vid)
            LOG.info(veid)
            getvid = vid.split("v=")[1].split("&")[0]
        except:
            vid = str(rfind[1].attrs['href'])
            veid = "https://www.youtube.com{0}".format(vid)
            LOG.info(veid)
            getvid = vid.split("v=")[1].split("&")[0]
        thumb = "https://img.youtube.com/vi/{0}/maxresdefault.jpg".format(getvid)
        self.gui["videoThumb"] = thumb
        self.lastSong = veid
        video = pafy.new(veid)
        playstream = video.streams[0]
        playurl = playstream.url
        self.gui["status"] = str("play")
        self.gui["video"] = str(playurl)
        self.gui["currenturl"] = str(vid)
        self.gui["currenttitle"] = video.title
        self.gui["setTitle"] = video.title
        self.gui["viewCount"] = video.viewcount
        self.gui["publishedDate"] = video.published
        self.gui["videoAuthor"] = video.username
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["nextSongTitle"] = ""
        self.gui["nextSongImage"] = ""
        self.gui["nextSongID"] = ""
        self.gui.show_pages(["YoutubePlayer.qml", "YoutubeSearch.qml"], 0, override_idle=True)
        self.recentList.appendleft({"videoID": getvid, "videoTitle": video.title, "videoImage": video.thumb})
        self.youtubesearchpagesimple(utterance)
        self.isTitle = video.title
        
    def bitchutepause(self, message):
        self.gui["status"] = str("pause")
        self.gui.show_page("BitchutePlayer.qml")
    
    def bitchuteresume(self, message):
        self.gui["status"] = str("play")
        self.gui.show_page("BitchutePlayer.qml")
        
    def bitchutesearchpage(self, message):
        self.stop()
        videoList = []
        videoList.clear()
        videoPageObject = {}
        utterance = message.data.get('utterance').lower()
        utterance = utterance.replace(
            message.data.get('BitChuteSearchPageKeyword'), '')
        vid = self.getListSearch(utterance)
        url = "https://www.youtube.com/results?search_query=" + vid
        response = urlopen(url)
        html = response.read()
        videoList = self.process_soup_additional(html)
        videoPageObject['videoList'] = videoList
        self.recentPageObject['recentList'] = list(self.recentList)
        self.gui["videoListBlob"] = videoPageObject
        self.gui["recentListBlob"] = self.recentPageObject
        self.gui.show_page("BitchuteSearch.qml")
        
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
        self.gui["previousAvailable"] = False
        self.gui["nextAvailable"] = True
        self.gui["bgImage"] = self.live_category
        self.gui.show_page("BitchuteLiveSearch.qml", override_idle=True)
        

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
        self.gui["viewCount"] = str(message.data['vidViewCount'])
        self.gui["publishedDate"] = str(message.data['vidUploadDate'])
        self.gui["videoAuthor"] = str(message.data['vidAuthor'])
        self.gui.show_page("BitchutePlayer.qml", override_idle=True)
        self.isTitle = str(message.data['vidTitle'])

    def stop(self):
        self.enclosure.bus.emit(Message("metadata", {"type": "stop"}))
        pass

    def process_soup_additional(self, htmltype):
        videoList = []
        videoList.clear()
        a_tag = SoupStrainer('a')
        soup = BeautifulSoup(htmltype, 'html.parser', parse_only=a_tag)
        for vid in soup.findAll('a'):
            if not vid.has_attr('class'):
                if vid.has_attr('target'):
                    if not vid.find('img'):
                        videoID = vid['href'].split("/")[4]
                        videoUrl = vid['href'] 
                        videoTitle = vid.contents[0]
                    if vid.find('img'):
                        videoImage = vid.contents[1]['src']
                        videoList.append({"videoID": videoID, "videoTitle": videoTitle, "videoImage": videoImage, "videoUrl": videoUrl})               
                
        return videoList
    
    def process_voice_play(self, utterance):
        url = "https://www.bitchute.com/category/{0}".format(category)
        LOG.info(url)
        response = requests.get(url)
        a_tag = SoupStrainer('a')
        soup = BeautifulSoup(htmltype, 'html.parser', parse_only=a_tag)
        for vid in soup.findAll('a'):
            if not vid.has_attr('class'):
                if vid.has_attr('target'):
                    if not vid.find('img'):
                        videoID = vid['href'].split("/")[4]
                        videoUrl = vid['href'] 
                        videoTitle = vid.contents[0]
                    if vid.find('img'):
                        videoImage = vid.contents[1]['src']
                        #videoList.append({"videoID": videoID, "videoTitle": videoTitle, "videoImage": videoImage, "videoUrl": videoUrl})
    
    def process_category_listing(self, htmltype):
        videoList = []
        videoList.clear()
        soup = BeautifulSoup(htmltype)
        getVideoDetails = soup.findAll(attrs={'class': 'video-card'})
        for vid in getVideoDetails:
            videoID = vid.contents[1]['href'].split("/")[2]
            videoImage = vid.contents[1].contents[1].contents[1]['data-src']
            videoViews = vid.contents[1].contents[1].contents[5].contents[1]
            videoTitle = vid.contents[3].contents[1].contents[0].contents[0]
            videoUploadDate = vid.contents[3].contents[5].contents[0]
            tempVidChannel = vid.contents[3].contents[3].contents[0].contents[0]
            if not type(tempVidChannel) is Tag:
                videoChannel = vid.contents[3].contents[3].contents[0].contents[0]
            else:
                videoChannel = "Hidden"
            
            videoList.append({"videoID": videoID, "videoTitle": videoTitle, "videoImage": videoImage, "videoChannel": videoChannel, "videoViews": videoViews, "videoUploadDate": videoUploadDate})
            
        return videoList
    
    def process_bitchute_video_type(self, videolink):
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        
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

    def refreshWatchList(self, message):
        try:
            self.youtubesearchpagesimple(message.data["title"])
        except:
            self.youtubesearchpagesimple(self.isTitle)
        
    @intent_file_handler('bitchute-repeat.intent')
    def bitchute_repeat_last(self):
        video = pafy.new(self.lastSong)
        thumb = video.thumb
        playstream = video.streams[0]
        playurl = playstream.url
        self.gui["status"] = str("play")
        self.gui["video"] = str(playurl)
        self.gui["currenturl"] = ""
        self.gui["currenttitle"] = video.title
        self.gui["setTitle"] = video.title
        self.gui["viewCount"] = video.viewcount
        self.gui["publishedDate"] = video.published
        self.gui["videoAuthor"] = video.username
        self.gui["videoListBlob"] = ""
        self.gui["recentListBlob"] = ""
        self.gui["nextSongTitle"] = ""
        self.gui["nextSongImage"] = ""
        self.gui["nextSongID"] = ""
        self.gui.show_pages(["YoutubePlayer.qml", "YoutubeSearch.qml"], 0, override_idle=True)
        self.youtubesearchpagesimple(video.title)
        self.isTitle = video.title

    def build_category_list(self, category):
        url = "https://www.bitchute.com/category/{0}".format(category)
        LOG.info(url)
        response = requests.get(url)
        html = response.text
        videoList = self.process_category_listing(html)
        return videoList
        
def create_skill():
    return BitChuteSkill()
