from datetime import datetime

from network_find_funcs import (
    get_instagram_posts,
    get_facebook_posts,
    get_linkedin_posts,
    get_youtube_posts,
)

from date_range import get_date_range

from aggregate import aggregate_platform
from sheets_sync import write_summary, get_client_adc  

SPREADSHEET_ID = "10_pz7I2u27s-eTKsatJDAbuZ6QnEpJTF9ZPAq2vk_EA"
WORKSHEET_NAME = "Monthly Review"


def month_label():
    start, _end = get_date_range()
    return datetime.fromisoformat(start).strftime("%B %Y")


def main():
    instagram_posts = get_instagram_posts()
    facebook_posts = get_facebook_posts()
    linkedin_posts = get_linkedin_posts()
    youtube_shorts = get_youtube_posts()

    platform_rows = [
        {"platform": "LinkedIn", **aggregate_platform(linkedin_posts)},
        {"platform": "Facebook", **aggregate_platform(facebook_posts)},
        {"platform": "Instagram", **aggregate_platform(instagram_posts)},
        {"platform": "Youtube Shorts", **aggregate_platform(youtube_shorts)}
    ]

    client = get_client_adc()
    write_summary(SPREADSHEET_ID, WORKSHEET_NAME, month_label(), platform_rows, client, youtube_shorts)

    print(f"Synced {month_label()} summary to '{WORKSHEET_NAME}':")
    for row in platform_rows:
        print(f"  {row}")


if __name__ == "__main__":
    main()
