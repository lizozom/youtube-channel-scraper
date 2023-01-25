import isodate
from datetime import datetime
from peewee import *
from consts import DB_NAME

db = SqliteDatabase(DB_NAME)

class YouTubeChannel(Model):
    channel_id = CharField(primary_key=True)
    search_query = CharField()
    title = CharField()
    description = CharField()
    thumbnail = CharField()
    created_at = DateTimeField(default=datetime.now)
    stats_refreshed_at = DateTimeField(null=True)
    published_at = DateTimeField()
    view_count = IntegerField(null=True)
    subscriber_count = IntegerField(null=True)
    video_count = IntegerField(null=True)
    relevant = BooleanField(default=True, null=True)
    upload_playlist_id = CharField(null=True)

    class Meta:
        database = db

    def getUrl(self):
        return "https://www.youtube.com/channel/%s" % self.channel_id

    @staticmethod
    def fromYouTubeAPI(channelSnippet, searchQuery):
        return YouTubeChannel.get_or_create(
            search_query=searchQuery,
            channel_id=channelSnippet["channelId"],
            title=channelSnippet["title"],
            description=channelSnippet["description"],
            thumbnail=channelSnippet["thumbnails"]["default"]["url"],
            published_at=channelSnippet["publishedAt"],
        )

    def updateStats(self, channelInfo):
        statistics = channelInfo["statistics"]
        self.view_count = statistics["viewCount"]
        self.subscriber_count = statistics["subscriberCount"]
        self.video_count = statistics["videoCount"]
        self.stats_refreshed_at = datetime.now()

        contentDetails = channelInfo["contentDetails"]
        self.upload_playlist_id = contentDetails["relatedPlaylists"]["uploads"]

        self.save()
        

class YouTubeVideo(Model):
    video_id = CharField(primary_key=True)
    title = CharField()
    status = CharField(null=True)
    tags = CharField(null=True)
    description = CharField()
    thumbnail = CharField()
    published_at = DateTimeField()
    created_at = DateTimeField(default=datetime.now)
    stats_refreshed_at = DateTimeField(null=True)
    channel = ForeignKeyField(YouTubeChannel, backref='videos')
    channel_title = CharField()
    durationStr = CharField(null=True)
    duration = IntegerField(null=True)
    view_count = IntegerField(null=True)
    like_count = IntegerField(null=True)
    dislike_count = IntegerField(null=True)
    favorite_count = IntegerField(null=True)
    comment_count = IntegerField(null=True)

    class Meta:
        database = db

    @staticmethod
    def fromYouTubeAPI(playlistChannelInfo):
        contentDetails = playlistChannelInfo["contentDetails"]
        status = playlistChannelInfo["status"]
        snippet = playlistChannelInfo["snippet"]
        return YouTubeVideo.get_or_create(
            video_id=contentDetails["videoId"],
            published_at=contentDetails["videoPublishedAt"],

            title=snippet["title"],
            description=snippet["description"],
            thumbnail=snippet["thumbnails"]["default"]["url"],
            channel=snippet["channelId"],
            channel_title=snippet["channelTitle"],
            status=status["privacyStatus"],
        )

    def updateStats(self, videoInfo):
        statistics = videoInfo["statistics"]
        try:
            self.view_count = statistics["viewCount"]
        except:
            pass
        
        try:
            self.like_count = statistics["likeCount"]
        except:
            pass

        # Not supported by API
        # self.dislike_count = statistics["dislikeCount"]
        try:
            self.favorite_count = statistics["favoriteCount"]
        except:
            pass    

        try:
            self.comment_count = statistics["commentCount"]
        except:    
            pass

        status = videoInfo["status"]
        self.status = status["privacyStatus"]

        contentDetails = videoInfo["contentDetails"]
        self.durationStr = contentDetails["duration"]
        self.duration = isodate.parse_duration(contentDetails["duration"]).total_seconds()

        try:
            tags = videoInfo["snippet"]["tags"]
            self.tags = ",".join(tags)
        except:
            pass

        self.stats_refreshed_at = datetime.now()
        self.save()
        