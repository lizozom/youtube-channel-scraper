from datetime import datetime, timedelta
from db.video import YouTubeVideo
from youtube_api import getAllVideosByChannel, getVideoInfo

class ChannelScraper:
    def __init__(self, youtube, channel):
        self.youtube = youtube
        self.channel = channel
        self.output_folder = "output/%s/%s-%s/" % (self.channel.search_query, self.channel.title, self.channel.channel_id)

    def scrape(self):
        self.get_channel_videos()
        self.update_video_stats()

    def get_channel_videos(self):
        self.videos = YouTubeVideo.select().where(YouTubeVideo.channel_id == self.channel.channel_id)

        if self.videos.count() > 0:
            print('Loaded all videos for %s from DB' % self.channel.title)
            return

        print('Loading all videos for %s from API' % self.channel.title)
        uploadPlayListItems = getAllVideosByChannel(self.youtube, self.channel)
        for video in uploadPlayListItems:
            YouTubeVideo.fromYouTubeAPI(video)
        
        self.videos = YouTubeVideo.select().where(YouTubeVideo.channel_id == self.channel.channel_id)

    def update_video_stats(self):
        print('Updating stats for videos for %s from API' % self.channel.title)
        for video in self.videos:
            # Only update videos that were not updated for more than 30 days
            if video.stats_refreshed_at is not None and video.stats_refreshed_at > datetime.now() - timedelta(days= 30):
                continue
            videoStats = getVideoInfo(self.youtube, video.video_id)
            video.updateStats(videoStats)
            video.save()
