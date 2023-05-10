from datetime import datetime, timedelta
from db import YouTubeVideo
from elastic import bulk_index_videos
from youtube_api import getAllVideosByChannel, getVideoInfo


class ChannelScraper:
    def __init__(self, youtube, es, channel):
        self.youtube = youtube
        self.channel = channel
        self.es = es
        self.output_folder = f"output/{self.channel.search_query}/{self.channel.title}-{self.channel.channel_id}/"

    def scrape(self):
        self.get_channel_videos()

        # Only update videos that were not updated for more than 30 days
        videosToUpdateStats = YouTubeVideo.select().where(
            (YouTubeVideo.channel_title == self.channel.title) & (
                (
                    (YouTubeVideo.stats_refreshed_at.is_null()) |
                    (YouTubeVideo.stats_refreshed_at <
                     datetime.now() - timedelta(days=30))
                ))
        )

        self.update_video_stats(videosToUpdateStats)
        self.update_elastic(videosToUpdateStats)

    def get_channel_videos(self):
        allSavedVideos = YouTubeVideo.select().where(
            YouTubeVideo.channel_id == self.channel.channel_id)

        isNewChannel = allSavedVideos.count() == 0
        fetchVideosMaxAge = None if isNewChannel else timedelta(days=30)

        print(f'Checking for new videos for {self.channel.title} from API')
        uploadPlayListItems = getAllVideosByChannel(
            self.youtube, self.channel, fetchVideosMaxAge)
        for i, video in enumerate(uploadPlayListItems):
            if allSavedVideos.filter(YouTubeVideo.video_id == video["contentDetails"]['videoId']).count() == 0:
                print('😀 %s: New videos found %s (index %d)' %
                      (self.channel.title, video['snippet']['title'], i))
                YouTubeVideo.fromYouTubeAPI(video)

    def update_video_stats(self, videos):
        print(f'Updating stats for videos {len(videos)} for {self.channel.title} from API')
        for video in videos:
            videoStats = getVideoInfo(self.youtube, video.video_id)
            if videoStats:
                video.updateStats(videoStats)
                video.save()
            else:
                print(
                    f'😡 {self.channel.title}: Failed to update stats for video {video.video_id}')

    def update_elastic(self, videos):
        print(f'Updating ES for {len(videos)} videos for {self.channel.title}')
        bulk_index_videos(self.es, videos)
