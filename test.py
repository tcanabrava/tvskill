import sys
import json
import requests
import youtube_dl
import timeago, datetime
import dateutil.parser
from bs4 import BeautifulSoup, SoupStrainer, Tag


def build_upload_date(update):
    yourdate = dateutil.parser.parse(update)
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=60 * 3.4
    )
    date = yourdate
    dtstring = timeago.format(date, now)
    return dtstring


url = "https://www.bitchute.com/video/UkKyB5VArdYC/"
response = requests.get(url)
html = response.text
print(html)
soup = BeautifulSoup(html)
videoList = []
getVideoDetails = soup.find("div", {"class": "details"})
print(getVideoDetails.contents[1].text)
