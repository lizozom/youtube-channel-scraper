from datetime import datetime
import isodate
from peewee import CharField, ForeignKeyField, IntegerField, BooleanField, Model, SqliteDatabase, DateTimeField
from consts import DB_NAME
from utils import get_datetime

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

    def get_url(self):
        return f"https://www.youtube.com/channel/{self.channel_id}"

    @staticmethod
    def from_youtube_api(channel_snippet, search_query):
        return YouTubeChannel.get_or_create(
            channel_id=channel_snippet["channelId"],
            defaults={
                "search_query": search_query,
                "title": channel_snippet["title"],
                "description": channel_snippet["description"],
                "thumbnail": channel_snippet["thumbnails"]["default"]["url"],
                "published_at": channel_snippet["publishedAt"]
            }
        )

    def update_stats(self, channel_info):
        statistics = channel_info["statistics"]
        self.view_count = statistics["viewCount"]
        self.subscriber_count = statistics["subscriberCount"]
        self.video_count = statistics["videoCount"]
        self.stats_refreshed_at = datetime.now()

        content_details = channel_info["contentDetails"]
        self.upload_playlist_id = content_details["relatedPlaylists"]["uploads"]

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
    favorite_count = IntegerField(null=True)
    comment_count = IntegerField(null=True)

    class Meta:
        database = db

    @staticmethod
    def from_youtube_api(playlist_channel_info):
        content_details = playlist_channel_info["contentDetails"]
        status = playlist_channel_info["status"]
        snippet = playlist_channel_info["snippet"]
        return YouTubeVideo.get_or_create(
            video_id=content_details["videoId"],
            published_at=content_details["videoPublishedAt"],

            title=snippet["title"],
            description=snippet["description"],
            thumbnail=snippet["thumbnails"]["default"]["url"],
            channel=snippet["channelId"],
            channel_title=snippet["channelTitle"],
            status=status["privacyStatus"],
        )

    def to_elastic(self):
        publish_time = get_datetime(self.published_at)
        return {
            "@timestamp": datetime.now(),
            "video_id": self.video_id,
            "video_title": self.title,
            "video_description": self.description,
            "video_thumbnail": self.thumbnail,
            "video_status": self.status,
            "video_published_at": self.published_at,
            "video_published_day_of_week": publish_time.strftime("%A") if publish_time else None,
            "video_duration": self.duration,
            "video_view_count": self.view_count,
            "video_like_count": self.like_count,
            "video_favorite_count": self.favorite_count,
            "video_comment_count": self.comment_count,
            "video_tags": self.tags.split(",") if self.tags else [],
            "channel_id": self.channel_id,
            "channel_title": self.channel_title,
            "channel_description": self.channel.description,
            "channel_thumbnail": self.channel.thumbnail,
            "channel_subscriber_count": self.channel.subscriber_count,
            "channel_view_count": self.channel.view_count,
            "channel_video_count": self.channel.video_count,
            "channel_published_at": self.channel.published_at
        }

    def update_stats(self, videoInfo):
        statistics = videoInfo["statistics"]
        try:
            self.view_count = statistics["viewCount"]
        except Exception:
            pass

        try:
            self.like_count = statistics["likeCount"]
        except Exception:
            pass
        try:
            self.favorite_count = statistics["favoriteCount"]
        except Exception:
            pass
        try:
            self.comment_count = statistics["commentCount"]
        except Exception:
            pass
        status = videoInfo["status"]
        self.status = status["privacyStatus"]

        content_details = videoInfo["contentDetails"]
        self.durationStr = content_details["duration"]
        self.duration = isodate.parse_duration(
            content_details["duration"]).total_seconds()

        try:
            tags = videoInfo["snippet"]["tags"]
            self.tags = ",".join(tags)
        except Exception:
            pass

        self.stats_refreshed_at = datetime.now()
        self.save()
