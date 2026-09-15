REACH_KEYS = ["reach", "impressionsUnique", "organicReach", "totalReach"]
VIEWS_KEYS = ["impressions", "impressionsTotal", "views", "videoViews", "totalViews", "blueReelsPlayCount"]
AVERAGE_KEYS = ["postVideoAvgTimeWatchedSeconds", "timeWatchedForVideoViews", "averageWatchTime", "averageViewDuration"]
URL_KEYS = ["url", "link", "reelUrl", "watchUrl"]

def _first_present(d, keys):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _top_post_urls(posts, metric_keys, limit=2):
    ranked_posts = []
    for post in posts:
        metric = _first_present(post, metric_keys)
        url = _first_present(post, URL_KEYS)
        if metric is not None and url:
            ranked_posts.append((metric, url))

    ranked_posts.sort(key=lambda item: item[0], reverse=True)
    return [url for _, url in ranked_posts[:limit]]


def aggregate_platform(posts, reach_keys=REACH_KEYS, views_keys=VIEWS_KEYS, average_keys=AVERAGE_KEYS):
    """
    posts: list of raw post dicts for one platform.

    Returns:
        {
            "total_posts": int,
            "reach": int or None,       # None if the platform/API never exposed reach
                                          # (e.g. LinkedIn, or FB posts that are Reels
                                          # — matches the "NA" / "**" cells in the sheet)
            "impressions": int,
            "top_two_impression_urls": list[str],
            "top_two_reach_urls": list[str],
        }
    """
    total_posts = len(posts)
    total_views = 0
    total_reach = 0
    total_likes = 0
    total_average_watch_time = 0
    total_clicks = 0
    total_shares = 0
    total_reactions = 0
    total_comments = 0
    total_interactions = 0
    reach_seen = False
    avg_watch_time_calculable = False
    clicks_seen = False
    reactions_seen = False

    for post in posts:
        r = _first_present(post, reach_keys)
        v = _first_present(post, views_keys)
        a = _first_present(post, average_keys)

       
        if "clicks" in post and post["clicks"] is not None:
            clicks_seen = True
            total_clicks += post["clicks"]
        if "shares" in post and post["shares"] is not None:
            total_shares += post["shares"]
        if "reactions" in post and post["reactions"] is not None:
            reactions_seen = True
            total_reactions += post["reactions"]
        if "comments" in post and post["comments"] is not None:
            total_comments += post["comments"]
        if "likes" in post and post["likes"] is not None:
            total_likes += post["likes"]
        if "interactions" in post and post["interactions"] is not None:
            total_interactions += post["interactions"]
        elif "engagement" in post and "impressionsUnique" in post:
            total_interactions += post["engagement"] * post["impressionsUnique"] / 100
        elif "engagement" in post and "impressions" in post and post["engagement"] <= 1:
            total_interactions += post["engagement"] * post["impressions"] / 100
        elif "engagement" in post and "impressions" in post and post["engagement"] > 1:
            total_interactions += post["engagement"] * post["impressions"] / 100
        elif "dislikes" in post and post["dislikes"] is not None:
            total_interactions += total_comments + total_likes + total_shares + post["dislikes"]


        if r is not None:
            reach_seen = True
            total_reach += r
        if v is not None:
            total_views += v
        if a is not None:
            avg_watch_time_calculable = True
            total_average_watch_time += a



    return {
        "total_posts": total_posts,
        "reach": total_reach if reach_seen else None,
        "impressions": total_views,
        "top_two_impression_urls": _top_post_urls(posts, views_keys),
        "interactions": total_interactions,
        "likes": total_likes,
        "comments": total_comments,
        "shares": total_shares,
        "clicks": total_clicks if clicks_seen else None,
        "reactions": total_reactions if reactions_seen else None,
        "average_time_watched_for_video_views": total_average_watch_time/total_posts if avg_watch_time_calculable else 0
    }
