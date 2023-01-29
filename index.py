from channel_scraper import ChannelScraper
from consts import CHANNEL_NAMES
from db import YouTubeChannel
from youtube_api import init, searchChannels, updateChannelStats
from elastic import init as initElastic
from dotenv import load_dotenv

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



def main():
    scrape_channel_metadata(CHANNEL_NAMES)


if __name__ == "__main__":
    main()



