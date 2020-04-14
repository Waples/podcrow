#!/usr/bin/env python3
"""
Podcrow
Pythonic Podcasts!

developer: Florian B.
"""

import argparse
import shutil
import sys
import threading
import warnings

import json
import os
import re
import requests
import feedparser


PARSE = argparse.ArgumentParser()
PARSE.add_argument('-a', '--amount',
                   help='amount of pods to download.')
PARSE.add_argument('-i', '--import-pod-feed',
                   help='import_pod feed with rss-url.')
PARSE.add_argument('-l', '--list',
                   help='list available feeds.', action='store_true')
PARSE.add_argument('-s', '--short',
                   help='defines a short for the pod.')
PARSE.add_argument('-d', '--download',
                   help='download all undownloaded items.')
PARSE.add_argument('-u', '--update',
                   help='update feeds.', action='store_true')
PARSE.add_argument('-p', '--update-podcrow',
                   help='update podcrow binary.', action='store_true')
PARSE.add_argument('-v', '--version',
                   help='Show the version.', action='store_true')
ARGS = PARSE.parse_args()

BASE = f'{os.path.expanduser("~")}/media/audio/podcrow'
CGRN = '\33[92m'    # green
CRED = '\33[91m'    # red
CYEL = '\33[33m'    # yellow
VERSION = 'v1.2'

# Development settings
DEBUG = False
if not DEBUG:
    warnings.filterwarnings("ignore")   # Disable FutureWarnings.


def version():
    """until we classify, we return the version(s) with a function"""
    return VERSION


def dep_check():
    """utility function, yes i know this is bad"""
    if not os.path.exists(BASE):
        print(f'{CGRN}No base dir found, creating it for you!')
        print(f'{CYEL}Ready to import podcasts!')
        os.makedirs(BASE)
        sys.exit()
    if os.listdir(BASE) == []:
        print(f'{CYEL}No feeds yet, try importing first!')


def gen_short(url):
    """Returns a shortname based on the feed title"""
    return feedparser.parse(url)['feed']['title'].replace(' ', '_')


def update_feed_file(data, short):
    """Update the entry for the episode with data"""
    with open(find_file(short), 'r') as parsed:
        feed = json.load(parsed)
    for episode in feed['episodes']:
        if episode['title'] == data['title']:
            episode['downloaded'] = data['downloaded']
    with open(find_file(short), 'w') as parsed:
        json.dump(feed, parsed, indent=2)


def list_feeds():
    """Prints the available podcasts on the system."""
    print(CYEL + 'Available feeds:')
    for feed in os.listdir(BASE):
        print(CGRN + '\t{}'.format(feed))


def get_feeds():
    """Returns a list for all available podcast feeds."""
    feeds = []
    for feed in os.listdir(BASE):
        feeds.append(feed)
    return feeds


def find_folder(short):
    """Finds the folder on the OS for the podcast."""
    return os.path.exists(os.path.join(BASE, short))


def find_pod(short, podcast):
    """Checks if podcast allready downloaded.."""
    return os.path.exists(os.path.join(BASE, short, podcast))


def return_folder(short):
    """Returns the podcast folder."""
    return os.path.join(BASE, short)


def find_file(short):
    """Searches for the feed.json file for a podcast."""
    return os.path.join(BASE, short, 'feed.json')


def update(podcasts):
    """Update the feed.json file for a podcast."""
    for short in podcasts:
        feed = find_file(short)
        with open(feed, 'r') as files:
            opened = json.load(files)
        url = opened['url']
        import_pod(url, short)


def import_pod(url, short=''):
    """Creates a feed.json file for an RSS feed."""
    parsed = feedparser.parse(url)
    feed_title = parsed['feed']['title']
    feed_url = parsed['href']
    if not short:
        short = feed_title.replace(' ', '_')
    if not find_folder(short):
        os.makedirs(os.path.join(BASE, short))
    feed = {}
    feed['episodes'] = episodes(parsed)
    feed['title'] = feed_title
    feed['url'] = feed_url
    print(f'{CGRN}Created/Updated feed file at {find_file(short)}')
    with open(find_file(short), 'w') as dumped:
        json.dump(feed, dumped, indent=2)


def episodes(form):
    """Creates json formatted information for each episode of the podcast."""
    episode_list = []
    for entry in form.entries:
        title = entry['title'].replace(' ', '_')
        try:
            url = entry['links'][1]['href']
        except IndexError:
            print(f'{CRED}Error: {title} cannot be read from rss feed.')
        date = entry['published']
        episode = {
            'title': title,
            'url': url,
            'published': date,
            'downloaded': False,
        }
        episode_list.append(episode)
    return episode_list


def downloader(short, amount):
    """Start threaded downloads based on non-downloaded podcasts, defaults
    amount is 5 if not specified"""
    try:
        with open(find_file(short), 'r') as p__:
            feed = json.load(p__)
        for entry in feed['episodes']:
            if not entry['downloaded']:
                thr = threading.Thread(target=threaded_dl, args=(entry, short))
                thr.start()     # start a download as a thread.
                print(f"{CGRN}Started dl_thread for {entry['title']}")
                amount -= 1
                if amount == 0:
                    break
    except FileNotFoundError:
        print(f'{CRED}error: no feed file found for {short}')


def threaded_dl(entry, short):
    """basic file downloader"""
    try:
        req = requests.get(entry['url'])
        unformatted = str(entry['title'] + '.mp3')
        filename = re.sub(r"[['/()#:\!, ?]", '', unformatted)
        with open(os.path.join(return_folder(short), filename), 'wb') as media:
            for chunk in req.iter_content(chunk_size=1024**2):
                media.write(chunk)
        entry['downloaded'] = True
        update_feed_file(entry, short)
    except Exception as err:
        return err


def update_podcrow():
    """update the podcrow binary in ~/.local/bin"""
    shutil.copyfile('podcrow.py', f'{os.path.expanduser("~")}/.local/bin/podcrow')
    os.chmod(f'{os.path.expanduser("~")}/.local/bin/podcrow', 755)
    print('updated podcrow')


def podcrow():
    """Parse the user input"""
    dep_check()
    amount = 5
    if ARGS:
        if ARGS.version:
            print(f'Version:\t{VERSION}')
        if ARGS.amount:
            amount = int(ARGS.amount)
        if ARGS.list:
            list_feeds()
        if ARGS.import_pod_feed:
            url = ARGS.import_pod_feed
            if ARGS.short:
                short = ARGS.short
            else:
                short = gen_short(url)
            import_pod(url, short)
        if ARGS.download:
            downloader(ARGS.download, amount=amount)
        if ARGS.update:
            update(get_feeds())
        if ARGS.update_podcrow:
            update_podcrow()
    else:
        print(f'{CRED}[error] no arguments specified.')


if __name__ == '__main__':
    try:
        podcrow()
    except KeyboardInterrupt as _:
        print('', end='\r')
        print(f'{CYEL}Exiting')
