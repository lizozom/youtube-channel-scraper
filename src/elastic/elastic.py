import configparser
from elasticsearch import Elasticsearch

config = configparser.ConfigParser()
config.read('auth/elastic.ini')

ELASTIC_VIDEO_INDEX_NAME = 'youtube_videos'

def init():
    es = Elasticsearch(
        cloud_id=config['ELASTIC']['cloud_id'],
        http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
    )

    print(es.info())

    return es

def update_video_captions(es, video, captions):
    es.update(index=ELASTIC_VIDEO_INDEX_NAME, id=video.video_id, body={
        "doc": {
            "video_transcript": captions['text'],
            "video_transcript_word_count": captions['duration'],
            "video_transcript_duration": captions['wordCount'],
        },
    })

def bulk_index_videos(es, videos):
    bulk_data = []
    for i, video in enumerate(videos):
        if isinstance(video, dict):
            bulk_data.append({
                "index": {
                    "_id": video["video_id"],
                }
            })
            bulk_data.append(video)
        else:
            bulk_data.append({
                "index": {
                    "_id": video.video_id,
                }
            })
            bulk_data.append(video.to_elastic())

        if len(bulk_data) == 200 or i == len(videos) - 1:
            res = es.bulk(index=ELASTIC_VIDEO_INDEX_NAME, operations=bulk_data)
            bulk_data = []
            print(i, "Errors" if res['errors'] else "OK")
