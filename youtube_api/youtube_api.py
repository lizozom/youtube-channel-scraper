
from datetime import datetime, timedelta
from dateutil import parser
import pytz

from utils import getDatetime

def getAllVideosByPlaylistId(youtube, playlistId, maxAge=None):
    # Fetch videos list
    allVids = []
    vidsCount = None
    nextToken = ""
    maxAgeReached = False
    while (
        vidsCount is None or
        len(allVids) < vidsCount and
        not maxAgeReached):
        if playlistId is None:
            print("Skipping playlist (no playlist ID)")
            return []

        videosReq = youtube.playlistItems().list(
            part="contentDetails,id,snippet,status",
            playlistId=playlistId,
            pageToken=nextToken,
            maxResults=50
        )

        videosRes = videosReq.execute()
        vidsCount = videosRes["pageInfo"]["totalResults"]
        allVids.extend(videosRes["items"])
        if "nextPageToken" in videosRes:
            nextToken = videosRes["nextPageToken"]

        lastVideoDate = parser.parse(allVids[-1]["snippet"]["publishedAt"])
        if maxAge is not None and lastVideoDate < datetime.now().replace(tzinfo=pytz.UTC) - maxAge:
            maxAgeReached = True
        print("Got %d videos (latest %s)" % (len(allVids), lastVideoDate))

    return allVids

def searchChannels(youtube, channelName):
    request = youtube.search().list(
        part="snippet,id",
        q=channelName,
        type="channel",
        maxResults=1
    )

    response = request.execute()
    return response["items"]

def getChannelInfo(youtube, channel):
    request = youtube.channels().list(
        part="id,brandingSettings,contentDetails,contentOwnerDetails,localizations,snippet,statistics,status,topicDetails",
        id=channel
    )
    response = request.execute()
    return response["items"][0]

def getVideoInfo(youtube, video):
    request = youtube.videos().list(
        part="id,snippet,contentDetails,statistics,status",
        id=video
    )
    response = request.execute()
    return response["items"][0] if len(response["items"]) > 0 else None

def updateChannelStats(youtube, channel, maxAge=timedelta(days=30)):
    # Update channel stats if they are older than 30 days
    if (channel.stats_refreshed_at is not None and channel.stats_refreshed_at > datetime.now() - maxAge) or channel.upload_playlist_id is None:
        channelInfo = getChannelInfo(youtube, channel.channel_id)
        channel.updateStats(channelInfo)

def getAllVideosByChannel(youtube, channel, maxAge=None):
    return getAllVideosByPlaylistId(youtube, channel.upload_playlist_id, maxAge)
