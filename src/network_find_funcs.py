import requests
import os
from date_range import *
# import json




start, end = get_date_range()[0], get_date_range()[1]

def is_podcast_post(post, *field_names):
    keywords = ("#armymatters", "army matters", "podcast", "#podcast")

    for field_name in field_names:
        value = str(post.get(field_name, "")).lower()
        if any(keyword in value for keyword in keywords):
            return True

    return False


def get_instagram_posts():
    posts = []

    # posts
    url = "https://app.metricool.com/api/v2/analytics/posts/instagram?blogId=5784679&userId=5193289"
    parameters = {
        "from" : start,
        "to" : end,
        "timezone" : 'America/New_York' 
    }

    response = requests.get(url=url, headers={"X-Mc-Auth" : os.environ.get("METRICOOL_KEY")}, params=parameters)

    data = []
    if response.status_code == 200:
        data = response.json().get("data")

    for post in data:
        if is_podcast_post(post, "content"):
            posts.append(post)

    # reels
    url = "https://app.metricool.com/api/v2/analytics/reels/instagram?blogId=5784679&userId=5193289"
    parameters = {
        "from" : start,
        "to" : end,
        "timezone" : 'America/New_York' 
    }

    response = requests.get(url=url, headers={"X-Mc-Auth" : os.environ.get("METRICOOL_KEY")}, params=parameters)

    data = []
    if response.status_code == 200:
        data = response.json().get("data")

    for post in data:
        if is_podcast_post(post, "content") in post.get("content"):
            posts.append(post)

    return posts


def get_facebook_posts():
    posts = []

    # posts
    url = "https://app.metricool.com/api/v2/analytics/posts/facebook?blogId=5784679&userId=5193289"
    parameters = {
        "from" : start,
        "to" : end,
        "timezone" : 'America/New_York' 
    }

    response = requests.get(url=url, headers={"X-Mc-Auth" : os.environ.get("METRICOOL_KEY")}, params=parameters)

    data = []
    if response.status_code == 200:
        data = response.json().get("data")

    for post in data:
        if is_podcast_post(post, "text"):
            posts.append(post)


    # reels
    url = "https://app.metricool.com/api/v2/analytics/reels/facebook?blogId=5784679&userId=5193289"
    parameters = {
        "from" : start,
        "to" : end,
        "timezone" : 'America/New_York' 
    }

    response = requests.get(url=url, headers={"X-Mc-Auth" : os.environ.get("METRICOOL_KEY")}, params=parameters)

    data = []
    if response.status_code == 200:
        data = response.json().get("data")

    for post in data:
        if is_podcast_post(post, "description"):
            posts.append(post)

    return posts


def get_linkedin_posts():
    url = "https://app.metricool.com/api/v2/analytics/posts/linkedin?blogId=5784679&userId=5193289"
    parameters = {
        "from" : start,
        "to" : end,
        "timezone" : 'America/New_York' 
    }
    
    response = requests.get(url=url, headers={"X-Mc-Auth" : os.environ.get("METRICOOL_KEY")}, params=parameters)

    data = []
    if response.status_code == 200:
        data = response.json().get("data")

    return [post for post in data if is_podcast_post(post, "description", "title", "comment")]


def get_shorts_in_range(posts, start: str, end: str):
    return [
        p for p in posts
        if p.get("videoType") == "SHORT"
        and start <= p["publishedAt"]["dateTime"] <= end
    ]

def get_youtube_posts():
    url = "https://app.metricool.com/api/v2/analytics/posts/youtube?blogId=5784679&userId=5193289"
    parameters = {
            "from" : start,
            "to" : end,
            "timezone" : 'America/New_York' 
        }

    response = requests.get(url=url, headers={"X-Mc-Auth" : os.environ.get("METRICOOL_KEY")}, params=parameters)

    data = []
    if response.status_code == 200:
        data = response.json().get("data")

    data = get_shorts_in_range(data, start, end)

    return [post for post in data if is_podcast_post(post, "description", "title")]
