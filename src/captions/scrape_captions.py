from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_transcript(videoid):
    transcript = YouTubeTranscriptApi.get_transcript(videoid, languages=['en', 'en-US', 'en-GB'])
    formatter = TextFormatter()
    text = formatter.format_transcript(transcript).replace('\n', ' ')
    words = text.split(" ")
    return {
        "text": text,
        "wordCount": len(words),
        "duration": transcript[-1]["start"] + transcript[-1]["duration"],
    }


def scrape_video_captions(video):
    video_id = video.video_id
    print(f"Scraping captions for video: {video_id}")
    try:
        return get_transcript(video_id)
    except Exception as e:
        print(e)
        print(f"Transcript disabled for video {video_id}")
        return {"msg": "Transcript disabled"}
