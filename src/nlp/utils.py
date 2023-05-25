CHANNEL = "Tasting History with Max Miller"

def get_caption_folder(channel_name):
    return f"./output/{channel_name}/captions/"

def get_processed_caption_folder(channel_name):
    return f"./output/{channel_name}/transcripts/"

def get_scores_folder(channel_name):
    return f"./output/{channel_name}/par_scores/"

def get_transcript(caption_file) -> str:
    first_file = open(caption_file, "r", encoding="utf-8")
    transcript = first_file.read()
    char_count = len(transcript)
    return transcript
    