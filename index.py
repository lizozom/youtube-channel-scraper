from channel_scraper import ChannelScraper
from consts import CHANNEL_NAMES
from db.video import YouTubeChannel
from video_list import searchChannels, updateChannelStats
from youtube import init

def main():
    youtube = init()
    # youtube = initOauth()

    for query in CHANNEL_NAMES:
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
                channel,
            )
            scraper.process()


if __name__ == "__main__":
    main()



