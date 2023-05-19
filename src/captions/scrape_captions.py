from time import sleep
import json
import random
import os
import os.path

from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

WAIT_TIME = 15                                # seconds browser waits before giving up
SLEEP_TIME = [5, 15]                          # random seconds range before loading next video id
HEADLESS = False                              # select True if you want the browser window to be invisible (but not inaudible)
MUTE = True                                   # select True if you want the browser window to be muted
adblock_path = os.environ.get("ADBLOCK_PATH")

def process_captions(captions_str):
    captions_json = json.loads(captions_str)
    duration = captions_json["events"][0]["dDurationMs"]
    texts = []
    for event in captions_json["events"]:
        if "segs" in event:
            for segment in event["segs"]:
                text = segment["utf8"]
                if text != "\n":
                    texts.append(text.strip())
    summary = {
        "text": " ".join(texts),
        "wordCount": len(texts),
        "duration": duration
    }
    return summary

def get_transcript(driver, videoid):
    captions = ""
    # navigate to video
    driver.get("https://www.youtube.com/watch?v=%s&vq=small" % videoid)

    try:
        element = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "ytp-subtitles-button")))
    except Exception:
        return {
            "msg": 'could not find subtitles button'
        }

    if "unavailable" in element.get_attribute("title"):
        return {
            "msg": 'video has no captions'
        }

    try:
        # Press if captions are disabled
        if element.get_attribute("aria-pressed") == "false":
            element.click()
    except Exception:
        return {
            "msg": 'could not click'
        }

    try:
        request = driver.wait_for_request('/timedtext', timeout=15)
        captions_resp = request.response
        if captions_resp:
            print("FOUND")
            if captions_resp.status_code >= 200 and captions_resp.status_code < 300:
                content = decode(captions_resp.body, captions_resp.headers.get('Content-Encoding', 'identity'))
                captions = json.dumps(json.loads(content), sort_keys=True, indent=4)
            else:
                print("Returned with error")
    except Exception:
        return {
            "msg": 'no captions'
        }

    # cool down
    sleep(random.uniform(SLEEP_TIME[0], SLEEP_TIME[1]))
    del driver.requests

    return process_captions(captions)

def setup_driver():
    # create driver
    options = Options()
    print(adblock_path)
    if adblock_path:
        options.add_argument('load-extension=' + adblock_path)
    if MUTE:
        options.add_argument("--mute-audio")

    if HEADLESS:
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.scopes = [
        '.*youtube.*',
    ]

    # let adblock installation finish
    sleep(7)

    driver.switch_to.window(driver.window_handles[0])
    return driver

def scrape_video_captions(driver, video):
    video_id = video.video_id
    print(f"Scraping captions for video: {video_id}")
    return get_transcript(driver, video_id)
