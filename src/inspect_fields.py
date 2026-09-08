# inspect_fields.py
#
# Run this once (locally, with METRICOOL_KEY set) to see the real shape
# of a post object for each platform. Use it to confirm/adjust
# REACH_KEYS / VIEWS_KEYS in aggregate.py.

import json
from network_find_funcs import get_instagram_posts, get_facebook_posts, get_linkedin_posts

PLATFORM_FETCHERS = [
    ("Instagram", get_instagram_posts),
    ("Facebook", get_facebook_posts),
    ("LinkedIn", get_linkedin_posts)
]

for name, fetch in PLATFORM_FETCHERS:
    posts = fetch()
    print(f"\n--- {name}: {len(posts)} podcast-tagged posts this period ---")
    if posts:
        print(json.dumps(posts, indent=2))
    else:
        print("(no posts matched the podcast filter this period)")
