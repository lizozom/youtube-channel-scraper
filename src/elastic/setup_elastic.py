import json
import os
import re

from db.models import YouTubeVideo
from elastic import init, ELASTIC_VIDEO_INDEX_NAME, bulk_index_videos

ELASTIC_VIDEO_BACKUP_PATH = './output/backup/videos'
OUTPUT_PATH = './output'


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
        "channel_ids": {
            "terms": {
                "field": "channel_title.keyword",
                "size": 10000
            }
        }
    })

    return titles['aggregations']['channel_names']['buckets']


def backup_all_videos(es):
    channels = get_all_channel_names(es)
    for channel in channels:
        print(channel['key'])
        docs = es.search(index="youtube_videos", query={
                         "match": {"channel_title": channel['key']}}, size=10000)
        sources = [doc['_source'] for doc in docs['hits']['hits']]
        f = open(f"{ELASTIC_VIDEO_BACKUP_PATH}/{channel['key'].lower().replace(' ', '_')}.json",
                 "w", encoding='utf-8')
        f.write(json.dumps(sources, indent=4))
        f.close()


def upload_all_videos_from_backup(es):
    for (root, _, files) in os.walk(ELASTIC_VIDEO_BACKUP_PATH, topdown=True):
        for file in files:
            if file.endswith('.json'):
                print([root, file])
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    bulk_index_videos(es, data)


def download_captions(es, channel_name=None):
    channels = get_all_channel_names(es) if channel_name is None else [
        {'key': channel_name}]
    for channel in channels:
        docs = es.search(index="youtube_videos", query={
                         "match": {
                             "channel_title.keyword": channel['key']
                         },
                         }, size=10000,
                         _source_includes=["channel_id", "video_id", "video_title", "video_published_at", "video_transcript", "video_transcript_word_count"])
        sources = [doc['_source'] for doc in docs['hits']['hits']]
        
        print(f"Found {len(sources)} videos for {channel['key']}")
        # print([s["video_title"] for s in sources])
        # return
        for s in sources:
            published = s["video_published_at"]
            video_id = s["video_id"]
            video_title = s["video_title"]
            word_count = s["video_transcript_word_count"] if "video_transcript_word_count" in s else 0
            transcript = s["video_transcript"] if "video_transcript" in s else ""
            # print(transcript)
            
            file_path = f"{OUTPUT_PATH}/{channel_name}/captions/"
            os.makedirs(file_path, exist_ok=True)
            with open(os.path.join(file_path, f"transcript_{published}_{video_id}.txt"),
                      "w", encoding='utf-8') as f:
                
                print(f"Saving transcript for {video_title} with {len(transcript)} words.")
                sentences = [sentence.strip() for sentence in transcript
                             .replace("\n", " ")
                             .replace("...", ".")
                             .replace(".com", " dot com")
                             .split(".")]
                script =  ".\n".join(sentences)
                f.write(script)
                f.close()


def restore_all_videos(es):
    init_elastic(es)
    upload_all_videos_from_backup(es)


def main():
    es = init()
    download_captions(es, "Tasting History with Max Miller")
    # init_elastic(es)
    # downloadAllVideos(es)
    # restore_all_videos(es)
    print("Done setting up elasticsearch.")


if __name__ == "__main__":
    main()
