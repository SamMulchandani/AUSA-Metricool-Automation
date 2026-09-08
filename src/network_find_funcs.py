import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
# import json


def get_date_range():
    today = datetime.now(ZoneInfo("America/New_York")).date()
    current_month_start = today.replace(day=1)
    previous_month = current_month_start.month - 1 or 12
    previous_year = current_month_start.year if current_month_start.month > 1 else current_month_start.year - 1
    previous_month_start = current_month_start.replace(
        year=previous_year,
        month=previous_month,
    )
    # return f"{previous_month_start}T00:00:00", f"{current_month_start}T00:00:00"
    return f"{previous_month_start}T00:00:00", f"{current_month_start}T00:00:00"

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
        if is_podcast_post(post, "content"):
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

# instagram_posts = get_instagram_posts('2026-07-01T00:00:00', '2026-07-31T00:00:00')
# print(len(instagram_posts))
# print(instagram_posts)

# facebook_posts = get_facebook_posts('2026-07-01T00:00:00', '2026-07-31T00:00:00')
# print(len(facebook_posts))
# print(facebook_posts)

# linkedin_posts = get_linkedin_posts(get_date_range()[0], get_date_range()[1])
# print(len(linkedin_posts))
# print(linkedin_posts)

