import argparse

from dotenv import load_dotenv
from src.captions.scrape_captions import scrape_video_captions
from src.channel_scraper import ChannelScraper
from src.consts import CHANNEL_NAMES
from src.db import YouTubeChannel
from src.db.models import YouTubeVideo
from src.elastic.elastic import update_video_captions, init as init_elastic
from src.youtube_api import init, search_channels, update_channel_stats

load_dotenv()

def scrape_channel_metadata(channel_names):
    youtube = init()
    es_client = init_elastic()

    for query in channel_names:
        if YouTubeChannel \
            .select() \
                .where(YouTubeChannel.search_query == query, YouTubeChannel.relevant == True).count() == 0:
            # Load channel info from YouTube API
            channel_list = search_channels(youtube, query)
            for channel in channel_list:
                try:
                    YouTubeChannel.from_youtube_api(channel["snippet"], query)
                except Exception as e:
                    print(e)

        # Update channel stats
        saved_channels = list(YouTubeChannel
                                .select()
                                .where(YouTubeChannel.search_query == query, YouTubeChannel.relevant == True))
        print(f"Found {len(saved_channels)} channels for query {query}")
        for channel in saved_channels:
            print(f"Updating stats for channel {channel.title}")
            update_channel_stats(youtube, channel)
            scraper = ChannelScraper(
                youtube,
                es_client,
                channel,
            )
            scraper.scrape()


def scrape_channel_subtitles(channel_names, video_ids=None):
    es_client = init_elastic()

    for query in channel_names:
        channels = YouTubeChannel \
            .select() \
            .where(YouTubeChannel.title == query)
        for channel in channels:
            videos = channel.videos.order_by(YouTubeVideo.published_at.asc())
            if video_ids:
                videos = videos.where(YouTubeVideo.video_id << video_ids)
            for video in videos:
                print(video)
                captions = scrape_video_captions(video)
                if 'msg' in captions:
                    print(captions['msg'])
                    continue
                update_video_captions(es_client, video, captions)
                print(f"Updated captions for video {video.video_id}")


def main():
    parser = argparse.ArgumentParser("youtube_scraper")
    parser.add_argument("command", help="Command to run (fetch, captions)")
    parser.add_argument(
        "--channel", help="Channels to scrape", action='append')
    parser.add_argument("--video", help="Videos to scrape", action='append')
    args = parser.parse_args()

    channels = args.channel if args.channel else CHANNEL_NAMES
    video_ids = args.video if args.video else None

    print(f"Running command {args.command} for {len(channels)} channels")
    if args.command == "fetch":
        scrape_channel_metadata(channels)
    elif args.command == "captions":
        scrape_channel_subtitles(channels, video_ids)
    elif args.command == "download":
        scrape_channel_subtitles(channels, video_ids)
    else:
        print(args)
        print("Unknown command")


if __name__ == "__main__":
    main()
