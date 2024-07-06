import json
import random
from time import sleep

from src.db.utils import user_to_dict, expand_and_parse_tweets, expand_and_parse_tweets_for_api
from src.lib.app_manager import AppManager

users = [
    'MollyIsDegening',
    "shamrock",
    "100xShaman",
    "FleecyFn",
    "0xAttelii",
    "thatdude_rudy",
    'winfinitysol'
    'TheCryptoGuy210',
    'Lyquids',
    '8ballsol',
    'AltcoinsCuzzin',
    'cryptzen93',
    'drich26_onX',
    'quamfywhale',
    'fundedstackz',
    'carsontrades17',
    'Crypto_Cowboys9',
    '__KiWi__KiD__',
    'flashyn_',
    'web3chicha',
    'glorysclub',
    'unknwn0x',
    'Joshd3412',
    'onlytradingLs',
    'solamibobby',
    'supplydogg',
    'SKREIDZ',
    'astrotheprotege',
    'lilclearpill'
    'PetrMorales24',
    '1Rangsey',
]


def get_following(app_manager):
    all_users = {}

    for user in users:
        app = app_manager.get_next()
        with open('following.json', 'r') as f:
            all_users = json.load(f)
            if user not in all_users:
                try:
                    following = app.get_user_followings(user, pages='20')
                    user_names = [user_to_dict(user) for user in following.users]
                    all_users[user] = user_names
                    print(following.users)
                except Exception as e:
                    print(e)
                    continue

                with open('following.json', 'w') as f:
                    json.dump(all_users, f)
                    print(f"Saved {len(all_users)} users to following.json")
                print(f"Sleeping for 4 seconds")
                sleep(4)
            else:
                print(f"{user} already in following.json")
    return all_users


def get_unique():
    with open('following.json', 'r') as f:
        all_users_map = json.load(f)
        all_users = {}
        all_keys = all_users_map.keys()
        unique_users = set()
        for key in all_keys:
            this_set = all_users_map[key]
            for user in this_set:
                unique_users.add(user['username'])
                all_users[user['username']] = user
        return all_users, unique_users


# get_following(app_manager)

# def follow_unique(app_manager):
# all_users, unique_users = get_unique()
# keys = all_users.keys()
# users_here = all_users['unknwn0x']
# print(f"Unique users: {len(users)}")
# for user in users_here:
#     print(user)
# app = app_manager.get_next()
# try:
#     app.follow_user(user['twitter_id'])
#     print(f"Followed {user}")
#     random_sleep = random.uniform(1, 5)
#     print(f"Sleeping for {random_sleep} seconds")
#     sleep(random_sleep)
# except Exception as e:
#     print(e)
#     continue


def follow_users_users(user_name, app_manager):
    with open('following.json', 'r') as f:
        following = json.load(f)
        users = following[user_name]
        index = 0
        # reverse array to follow the most recent users first
        users.reverse()
        for user in users:
            app = app_manager.get_next()
            print(user['username'])
            try:
                app.follow_user(user['twitter_id'])
                print(f"Followed {user['username']}")
                if index % 10 == 0 and index != 0:
                    random_sleep = random.uniform(50, 100)
                else:    
                    random_sleep = random.uniform(3, 5)
                print(f"Sleeping for {random_sleep} seconds")
                sleep(random_sleep)
            except Exception as e:
                print(e)
                continue
            index += 1


def follow_all(app_manager):
    all_users, unique_users = get_unique()
    keys = all_users.keys()
    index = 0
    for key in keys:
        user_details = all_users[key]
        user_id = user_details['twitter_id']
        app = app_manager.get_next()
        try:
            app.follow_user(user_id)
            print(f"Followed {user_details['username']}")
            if index % 500 == 0 and index != 0:
                random_sleep = random.uniform(300, 600)
            elif index % 100 == 0 and index != 0:
                random_sleep = random.uniform(100, 300)
            elif index % 10 == 0 and index != 0:
                random_sleep = random.uniform(50, 100)
            else:
                random_sleep = random.uniform(3, 6)
            print(f"Sleeping for {random_sleep} seconds")
            sleep(random_sleep)
        except Exception as e:
            print(e)
            continue
    print("Done following all users")
