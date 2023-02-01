from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
import configparser

config = configparser.ConfigParser()
config.read('elastic.ini')

ELASTIC_VIDEO_INDEX_NAME = 'youtube_videos'

def init():
    es = Elasticsearch(
        cloud_id=config['ELASTIC']['cloud_id'],
        http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
    )

    print(es.info())

    return es

def bulk_index_videos(es, videos):
    bulk_data = []
    for i, video in enumerate(videos):
        bulk_data.append({
            "index": {
                "_id": video.video_id,
            }
        })
        bulk_data.append(video.toElastic())

        if len(bulk_data) == 200 or i == len(videos) - 1:
            res = es.bulk(index=ELASTIC_VIDEO_INDEX_NAME, operations=bulk_data)
            bulk_data = []
            print(i, "Errors" if res['errors'] else "OK")