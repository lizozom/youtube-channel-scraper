import os
import requests
import time

# from transformers import pipeline
import numpy as np
from src.nlp.utils import get_scores_folder, get_processed_caption_folder, CHANNEL

API_URL = "https://us7916zbvnau0qxg.us-east-1.aws.endpoints.huggingface.cloud"
HEADERS = {"Authorization": "Bearer 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"}

def query_huggingface(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    return response.json()

# output = query({
#     "inputs": "Hi, I recently bought a device from your company but it is not working as advertised and I would like to get reimbursed!",
#     "parameters": {"candidate_labels": ["refund", "legal", "faq"]},
# })


# classifier = pipeline("zero-shot-classification",
#                       model="facebook/bart-large-mnli")


candidate_labels = ['cooking', 'food', 'history', 'story']
arr_titles = ['index', 'cooking_score', 'food_score', 'history_score', 'story_score']

def load_script_paragraphs(file_path) -> list[str]:
    with open(os.path.join(file_path), 'r', encoding='utf-8') as f:
        paragraphs = f.read().split('\n\n')
        print(f"Loaded {len(paragraphs)} paragraphs")
        return paragraphs

def classify_transcript_paragraphs(paragraphs: list[str]):
    results = []
    for i, par in enumerate(paragraphs):
        print(f"Processing paragraph {i}")
        # result = classifier(par, candidate_labels, multi_class=True)
        result = query_huggingface({
            "inputs": par,
            "parameters": {
                "candidate_labels":', '.join(candidate_labels),
                "multi_label": True
            },
        })
        print(result)
        scores = result["scores"]
        labels = result["labels"]
        score_map = dict(zip(labels, scores))
        results.append([i, score_map['cooking'], score_map['food'], score_map['history'], score_map['story']])
        # if i == 3:
        #     break
    return results

def process_transcripts():
    file_path = get_processed_caption_folder(CHANNEL)
    target_path = get_scores_folder(CHANNEL)
    transcript_files = os.listdir(file_path)
    for script_file in transcript_files:
        if script_file == 'par_transcript_2023-01-17T16:00:09Z_KMWrk_94L8Y.txt':
            continue
        print("Processing file: ", script_file)
        paragraphs = load_script_paragraphs(os.path.join(file_path, script_file))
        res = classify_transcript_paragraphs(paragraphs)
        print(res)
        a = np.asarray(res, dtype=object)
        target_file = os.path.join(target_path, script_file.replace('.txt', '.csv'))
        np.savetxt(target_file, a, delimiter=",", fmt=['%d', '%.5f', '%.5f', '%.5f', '%.5f'], header=','.join(arr_titles))
        time.sleep(5)

if __name__ == "__main__":
    process_transcripts()