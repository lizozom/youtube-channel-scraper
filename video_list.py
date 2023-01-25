
def getAllVideos(youtube, playlistId):
    # Fetch videos list
    allVids = []
    vidsCount = None
    nextToken = ""
    while (vidsCount is None or len(allVids) < vidsCount):

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
    channelInfo = getChannelInfo(youtube, channel.channel_id)
    channel.updateStats(channelInfo)

def getAllVideosByChannel(youtube, channel):
    allVids = getAllVideos(youtube, channel.upload_playlist_id)
    return allVids

