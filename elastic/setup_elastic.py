import json
import os

from db.models import YouTubeVideo
from elastic import init, ELASTIC_VIDEO_INDEX_NAME, bulk_index_videos

ELASTIC_VIDEO_BACKUP_PATH = './elastic/backup/videos'


def init_elastic(es):
    with open('elastic/mapping.json', encoding='utf-8') as mapping_file:
        file_contents = mapping_file.read()
        mappings = json.loads(file_contents)
        if not es.indices.exists(index=ELASTIC_VIDEO_INDEX_NAME):
            es.indices.create(index=ELASTIC_VIDEO_INDEX_NAME,
                              mappings=mappings)
        else:
            res = es.indices.put_mapping(
                index=ELASTIC_VIDEO_INDEX_NAME, properties=mappings["properties"])
            print(res)


def index_videos_from_db(es):
    allVideos = YouTubeVideo.select()
    bulk_index_videos(es, allVideos)


def get_all_channel_names(es):
    titles = es.search(index="youtube_videos", size=0, aggs={
        "channel_names": {
            "terms": {
                "field": "channel_title.keyword",
                "size": 10000
            }
        }
    })

    return titles['aggregations']['channel_names']['buckets']


def backupAllVideos(es):
    channels = getAllChannelNames(es)
    for channel in channels:
        print(channel['key'])
        docs = es.search(index="youtube_videos", query={
                         "match": {"channel_title": channel['key']}}, size=10000)
        sources = [doc['_source'] for doc in docs['hits']['hits']]
        f = open(f"{ELASTIC_VIDEO_BACKUP_PATH}/{channel['key'].lower().replace(' ', '_')}.json",
                 "w", encoding='utf-8')
        f.write(json.dumps(sources, indent=4))
        f.close()


def uploadAllVideosFromBackup(es):
    for (root, _, files) in os.walk(ELASTIC_VIDEO_BACKUP_PATH, topdown=True):
        for file in files:
            if file.endswith('.json'):
                print([root, file])
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    bulk_index_videos(es, data)

def downloadCaptions(es, channel_name):
    channels = getAllChannelNames(es)
    for channel in channels:
        print(channel['key'])
        docs = es.search(index="youtube_videos", query={
                         "match": {"channel_title": channel['key']}}, size=10000)
        sources = [doc['_source'] for doc in docs['hits']['hits']]
        f = open(f"{ELASTIC_VIDEO_BACKUP_PATH}/{channel['key'].lower().replace(' ', '_')}.json",
                 "w", encoding='utf-8')
        f.write(json.dumps(sources, indent=4))
        f.close()


def restoreAllVideos(es):
    init_elastic(es)
    uploadAllVideosFromBackup(es)


def main():
    es = init()
    # init_elastic(es)
    # downloadAllVideos(es)
    # restoreAllVideos(es)
    print("Done setting up elasticsearch.")


if __name__ == "__main__":
    main()
