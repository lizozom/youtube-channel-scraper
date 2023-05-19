from datetime import datetime, timedelta
from db import YouTubeVideo
from elastic import bulk_index_videos
from youtube_api import get_all_videos_by_channel, get_video_info

class ChannelScraper:
    def __init__(self, youtube, es_client, channel):
        self.youtube = youtube
        self.channel = channel
        self.es_client = es_client
        self.output_folder = f"output/{self.channel.search_query}/{self.channel.title}-{self.channel.channel_id}/"

    def scrape(self):
        self.get_channel_videos()

        # Only update videos that were not updated for more than 30 days
        
        videos_to_update_stats = YouTubeVideo.select().where(
            (YouTubeVideo.channel_title == self.channel.title) & (
                (
                    (YouTubeVideo.stats_refreshed_at.is_null()) |
                    (YouTubeVideo.stats_refreshed_at <
                     datetime.now() - timedelta(days=30))
                ))
        )

        self.update_video_stats(videos_to_update_stats)
        self.update_elastic(videos_to_update_stats)

    def get_channel_videos(self):
        all_saved_videos = YouTubeVideo.select().where(
            YouTubeVideo.channel_id == self.channel.channel_id)

        is_new_channel = all_saved_videos.count() == 0
        fetch_videos_max_age = None if is_new_channel else timedelta(days=30)

        print(f'Checking for new videos for {self.channel.title} from API')
        upload_playlist_items = get_all_videos_by_channel(
            self.youtube, self.channel, fetch_videos_max_age)
        for i, video in enumerate(upload_playlist_items):
            if all_saved_videos.filter(YouTubeVideo.video_id == video["contentDetails"]['videoId']).count() == 0:
                title = video['snippet']['title']
                print(f'😀 {self.channel.title}: New videos found {title} (index {i})')
                YouTubeVideo.from_youtube_api(video)

    def update_video_stats(self, videos):
        print(f'Updating stats for videos {len(videos)} for {self.channel.title} from API')
        for video in videos:
            video_stats = get_video_info(self.youtube, video.video_id)
            if video_stats:
                video.update_stats(video_stats)
                video.save()
            else:
                print(
                    f'😡 {self.channel.title}: Failed to update stats for video {video.video_id}')

    def update_elastic(self, videos):
        print(f'Updating ES for {len(videos)} videos for {self.channel.title}')
        bulk_index_videos(self.es_client, videos)
