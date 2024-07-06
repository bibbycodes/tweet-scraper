from time import sleep
from tweety.types import HOME_TIMELINE_TYPE_FOLLOWING
from src.api.dgen_galore import DgenGlore
from src.db.utils import expand_and_parse_tweets_for_api
from src.lib.app_manager import AppManager
from random import uniform


def get_time_line(app, dgen_galore=DgenGlore('http://localhost:4000')):
    timeline = app.get_home_timeline(timeline_type=HOME_TIMELINE_TYPE_FOLLOWING, pages=2)
    print(timeline)
    tweets = expand_and_parse_tweets_for_api(timeline)
    print(tweets)
    dgen_galore.post_mentions({"mentions": tweets})


def start():
    app_manager = AppManager()
    app_manager.initialise_apps()
    dgen_galore = DgenGlore('http://localhost:4000')
    apps = app_manager.get_apps()
    i = 0
    while True:
        try:
            for app in apps:
                get_time_line(app, dgen_galore)
            i += 1
            print(f"Ran {i} times")
            if i % 20 == 0 and i != 0:
                random_sleep_time = uniform(60, 80)
            elif i % 10 == 0 and i != 0:
                random_sleep_time = uniform(40, 70)
            elif i % 5 == 0 and i != 0:
                random_sleep_time = uniform(30, 60)
            else:
                random_sleep_time = uniform(15, 45)
            print(f"Sleeping for {random_sleep_time} seconds")
            sleep(random_sleep_time)
        except Exception as e:
            print(f"Error occurred: {e}")
            sleep(200)
            continue


start()
