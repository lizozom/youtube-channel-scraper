from captions.scrape_captions import setup_driver, scrape_video_captions
from channel_scraper import ChannelScraper
from consts import CHANNEL_NAMES
from db import YouTubeChannel
from db.models import YouTubeVideo
from elastic.elastic import update_video_captions
from youtube_api import init, searchChannels, updateChannelStats
from elastic import init as initElastic
from dotenv import load_dotenv
import argparse

load_dotenv()

def scrape_channel_metadata(channel_names):
    youtube = init()
    es = initElastic()

    for query in channel_names:
        if  YouTubeChannel \
            .select() \
            .where(YouTubeChannel.search_query == query, YouTubeChannel.relevant == True).count() == 0:
            # Load channel info from YouTube API
            channelList = searchChannels(youtube, query)
            for channel in channelList:
                YouTubeChannel.fromYouTubeAPI(channel["snippet"], query)
        
        savedChannelList = list(YouTubeChannel \
            .select() \
            .where(YouTubeChannel.search_query == query, YouTubeChannel.relevant == True))

        for channel in savedChannelList:
            updateChannelStats(youtube, channel)
            scraper = ChannelScraper(
                youtube, 
                es,
                channel,
            )
            scraper.scrape()


def scrape_channel_subtitles(channel_names):
    driver = setup_driver()
    es = initElastic()

    for query in channel_names:
        channels = YouTubeChannel \
            .select() \
            .where(YouTubeChannel.search_query == query, YouTubeChannel.relevant == True)
        for channel in channels:
            videos = channel.videos.order_by(YouTubeVideo.published_at.asc())
            for video in videos:
                print(video)
                captions = scrape_video_captions(driver, video)
                print(captions)
                if ('msg' in captions):
                    print(captions['msg'])
                    continue
                update_video_captions(es, video, captions)
                print("Updated captions for video %s" % video.video_id)

def main():
    parser = argparse.ArgumentParser("youtube_scraper")
    parser.add_argument("command", help="Command to run (fetch, captions)")
    parser.add_argument("--channels", help="Channels to scrape", action='append')
    args = parser.parse_args()

    channels = args.channels if args.channels else CHANNEL_NAMES

    if args.command == "fetch":
        scrape_channel_metadata(channels)
    elif args.command == "captions":
        scrape_channel_subtitles(channels)
    else:
        print(args)
        print("Unknown command")


if __name__ == "__main__":
    main()



