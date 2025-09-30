import requests
import json
import tweepy
import time
from requests_oauthlib import OAuth1

# ==== Twitter Auth ====
ACCESS_TOKEN = "2892387153-5Aimf62oCuD9xBF24czASHun48wJ1b7ebxZeg0N"
ACCESS_TOKEN_SECRET = "0FsCnPJBtxC4QGWxtmxhHcaqa8ePZh1tuZhwtUJBLGrcZ"
CLIENT_SECRET = "gYthuAZDkeG1RYknab7IadKE01DDtZBPMUetYdxxBFvSynXMrA"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAAf74QEAAAAAzlg9Xui%2BxQhXLpn7XtxfspNiAAA%3DvOWmYcOdICwExgPmB4zaD42NtCo7PNprCkgQ9aEpQEVMe1jFsb"
CONSUMER_KEY = "qy2q95IFNY8X3pNseiG5QdTPe"
CONSUMER_SECRET = "vEWM8QBF7eOPWxljDuy1uAJM2FdRRT2cgBe5qty32pFPJC3M14"

# ==== NSE Announcements API ====
NSE_URL = "https://www.nseindia.com/api/corporate-announcements?index=equities"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

seen_ids = set()  # memory store, replace with DB/file for persistence

def fetch_announcements():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get("https://www.nseindia.com", timeout=10)  # warmup
    resp = session.get(NSE_URL, timeout=10)
    resp.raise_for_status()
    print(resp.json())
    return resp.json()

def post_to_twitter(tweet_text):
    url = "https://api.x.com/2/tweets"
    
    # Set up OAuth1 authentication
    auth = OAuth1(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET,
        signature_method='HMAC-SHA1'
    )

    payload = {
        "text": tweet_text
    }

    response = requests.post(url, json=payload, auth=auth)
    if response.status_code in [200, 201]:
        print("Tweet posted successfully!")
        print(response.json())
    else:
        print(f"Failed to post tweet: {response.status_code}")
        print(response.text)

def format_tweet(ann):
    """
    Formats a corporate announcement into a tweet-friendly string.
    
    ann: dict containing NSE announcement data.
    """
    company = ann.get("sm_name") or ann.get("symbol")
    desc = ann.get("desc", "")
    text = ann.get("attchmntText", "")
    url = ann.get("attchmntFile", "")
    time = ann.get("an_dt", "")

    # Include announcement date at the top
    header = f"{company} - {desc} ({time})"

    # Reserve space for URL and newline
    reserved_chars = len(url) + 2  # newline + spacing
    available_text_len = 280 - len(header) - reserved_chars - 1  # 1 extra newline

    # Truncate text if too long
    if len(text) > available_text_len:
        text = text[:available_text_len - 3] + "..."  # ellipsis

    # Compose tweet
    tweet = f"{header}\n{text}\n{url}"

    return tweet


if __name__ == "__main__":
    try:
        data = fetch_announcements()   # <-- returns a list
        for ann in data:               # <-- iterate directly
            ann_id = ann.get("seq_id") or ann.get("srNo")
            if ann_id and ann_id not in seen_ids:
                seen_ids.add(ann_id)
                tweet = format_tweet(ann)
                print(tweet)
                post_to_twitter(tweet)
                break
       # time.sleep(60)  # check every 1 min
    except Exception as e:
        print("Error:", e)
        #time.sleep(120)