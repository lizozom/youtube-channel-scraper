
from datetime import datetime, timedelta

def getAllVideosByPlaylistId(youtube, playlistId):
    # Fetch videos list
    allVids = []
    vidsCount = None
    nextToken = ""
    while (vidsCount is None or len(allVids) < vidsCount):
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
        print("Got %d videos" % len(allVids))

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
    return response["items"][0]

def updateChannelStats(youtube, channel):
    # Update channel stats if they are older than 30 days
    if channel.stats_refreshed_at is not None and channel.stats_refreshed_at > datetime.now() - timedelta(days= 30):
        channelInfo = getChannelInfo(youtube, channel.channel_id)
        channel.updateStats(channelInfo)

def getAllVideosByChannel(youtube, channel):
    return getAllVideosByPlaylistId(youtube, channel.upload_playlist_id)

