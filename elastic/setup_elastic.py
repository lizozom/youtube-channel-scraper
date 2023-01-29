import json
from db.models import YouTubeVideo

from elastic import init, ELASTIC_VIDEO_INDEX_NAME, bulk_index_videos

def initElastic(es):
    with open('elastic/mapping.json') as mapping_file:
        file_contents = mapping_file.read()
        mappings = json.loads(file_contents)
        if (not es.indices.exists(index=ELASTIC_VIDEO_INDEX_NAME)):
            es.indices.create(index=ELASTIC_VIDEO_INDEX_NAME, mappings=mappings)
        else: 
            res = es.indices.put_mapping(index=ELASTIC_VIDEO_INDEX_NAME, properties=mappings["properties"])
            print(res)


def indexVideos(es):
    allVideos = YouTubeVideo.select()
    bulk_index_videos(es, allVideos)

def main():
    es = init()
    initElastic(es)
    indexVideos(es)
    print("Done setting up elasticsearch.")

if __name__ == "__main__":
    main()
    