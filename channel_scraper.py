from datetime import datetime, timedelta
from db import YouTubeVideo
from elastic import bulk_index_videos
from youtube_api import getAllVideosByChannel, getVideoInfo

class ChannelScraper:
    def __init__(self, youtube, es, channel):
        self.youtube = youtube
        self.channel = channel
        self.es = es
        self.output_folder = "output/%s/%s-%s/" % (self.channel.search_query, self.channel.title, self.channel.channel_id)

    def scrape(self):
        self.get_channel_videos()

        # Only update videos that were not updated for more than 30 days
        videosToUpdateStats = YouTubeVideo.select().where(YouTubeVideo.stats_refreshed_at < datetime.now() - timedelta(days=30))
        self.update_video_stats(videosToUpdateStats)
        self.update_elastic(videosToUpdateStats)

    def get_channel_videos(self):
        allSavedVideos = YouTubeVideo.select().where(YouTubeVideo.channel_id == self.channel.channel_id)

        isNewChannel = allSavedVideos.count() == 0
        fetchVideosMaxAge = None if isNewChannel else timedelta(days=30)
        
        print('Checking for new videos for %s from API' % self.channel.title)
        uploadPlayListItems = getAllVideosByChannel(self.youtube, self.channel, fetchVideosMaxAge)
        for i, video in enumerate(uploadPlayListItems):
            if allSavedVideos.filter(YouTubeVideo.video_id == video["contentDetails"]['videoId']).count() == 0:
                print('😀 %s: New videos found %s (index %d)' % (self.channel.title, video['snippet']['title'], i))
                YouTubeVideo.fromYouTubeAPI(video)

    def update_video_stats(self, videos):
        print('Updating stats for videos for %s from API' % self.channel.title)
        for video in videos:
            videoStats = getVideoInfo(self.youtube, video.video_id)
            video.updateStats(videoStats)
            video.save()

    def update_elastic(self, videos):
        print('Updating ES for videos for %s' % self.channel.title)
        bulk_index_videos(self.es, videos)