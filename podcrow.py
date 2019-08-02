#!/usr/bin/env python3

'''
Podcrow
Pythonic Podcasts!

codeauthor: gn0mish@protonmail.com
v0.1
'''

import argparse
import json
import os
import re
import requests
import feedparser

PARSE = argparse.ArgumentParser()
PARSE.add_argument('-i', '--import_pod_feed',
                   help='import_pod feed with rss-url.')
PARSE.add_argument('-l', '--list',
                   help='list available feeds.', action='store_true')
PARSE.add_argument('-s', '--shortname',
                   help='defines a shortname for the pod.')
PARSE.add_argument('-d', '--download',
                   help='download all undownloaded items.')
PARSE.add_argument('-u', '--update',
                   help='update feeds.', action='store_true')
ARGS = PARSE.parse_args()

HOME = os.path.expanduser('~')
BASE = HOME + '/media/audio/podcrow'
CGRN = '\33[92m'
CRED = '\33[91m'
CYEL = '\33[33m'
CRST = '\33[0m'


def find_folder(shortname):
    '''
    Finds the folder on the OS for the podcast.
    '''
    return os.path.exists(os.path.join(BASE, shortname))


def find_pod(shortname, podcast):
    '''
    Checks if podcast allready downloaded..
    '''
    return os.path.exists(os.path.join(BASE, shortname, podcast))


def return_folder(shortname):
    '''
    Returns the podcast folder
    '''
    return os.path.join(BASE, shortname)


def find_file(shortname):
    '''
    Searches for the feed.json file for a podcast.
    '''
    return os.path.join(BASE, shortname, 'feed.json')


def update(podcasts):
    '''
    Update the feed.json file for a podcast.
    '''
    for shortname in podcasts:
        feed = find_file(shortname)
        with open(feed, 'r') as files:
            opened = json.load(files)
        url = opened['url']
        import_pod(url, shortname)


def import_pod(url, shortname=''):
    '''
    Creates a feed.json file for an RSS feed.
    '''
    if not find_folder(BASE):
        os.makedirs(BASE)
    parsed = feedparser.parse(url)
    feed_title = parsed['feed']['title']
    feed_url = parsed['href']
    if not shortname:
        shortname = feed_title.replace(' ', '_')
    if not find_folder(shortname):
        os.makedirs(os.path.join(BASE, shortname))
    feed = {}
    feed['episodes'] = episodes(parsed)
    feed['title'] = feed_title
    feed['url'] = feed_url
    feed_file = find_file(shortname)
    print(CGRN + 'Created feed file at "' + feed_file + '"' + CRST)
    with open(feed_file, 'w') as dumped:
        json.dump(feed, dumped, indent=2)


def episodes(form):
    '''
    Creates json formatted information for each episode of the podcast.
    '''
    episodes = []
    for entry in form.entries:
        title = entry['title'].replace(' ', '_')
        try:
            url = entry['links'][1]['href']
        except IndexError:
            print(CRED + 'Error: ' + title +
                  ' cannot be read from rss feed.' + CRST)
        date = entry['published']
        download = False
        episode = {
            'title': title,
            'url': url,
            'published': date
        }
        episodes.append(episode)
    return episodes


def get_feeds():
    '''
    Returns a list for all available podcast feeds.
    '''
    feeds = []
    available = os.listdir(BASE)
    for feed in available:
        feeds.append(feed)
    return feeds


def download(shortname):
    '''
    Downloads each episode if not allready on OS.
    '''
    try:
        with open(find_file(shortname), 'r') as parsed:
            feed = json.load(parsed)
        title = feed['title']
        line = '\n-------------------------------------------------------------'
        print(CYEL + 'Podcast:\t' + title + line + CRST)
        episodes = feed['episodes']
        for entry in episodes:
            filename = str(entry['title'] + '.mp3')
            filename = re.sub(r"[['/()#:\!, ?]", '', filename)
            url = entry['url']
            if not find_pod(shortname, filename):
                print(CGRN + 'Downloading:\t' + filename + CRST)
                req = requests.get(url)
                with open(os.path.join(return_folder(shortname), filename), 'wb') as media:
                    for chunk in req.iter_content(chunk_size=1024**2):
                        media.write(chunk)
    except FileNotFoundError:
        print('error: no feed file found for ' + shortname)


def download_all(podcasts):
    '''
    Just a simple loop
    '''
    for shortname in podcasts:
        download(shortname)

def list_feeds():
    '''
    Prints the available podcasts on the system.
    '''
    available = os.listdir(BASE)
    print(CYEL + 'Available feeds:')
    for feed in available:
        print(CGRN + '\t{}'.format(feed))


def main():
    '''
    Parse the user input
    '''
    if ARGS:
        if ARGS.list:
            list_feeds()
        if ARGS.import_pod_feed:
            url = ARGS.import_pod_feed
            if ARGS.shortname:
                shortname = ARGS.shortname
            import_pod(url, shortname)
        if ARGS.download:
            shortname = ARGS.download
            if shortname == 'all':
                update(get_feeds())
                download_all(get_feeds())
            download(shortname)
        if ARGS.update:
            shortname = get_feeds()
            update(shortname)
    else:
        print('[error] no arguments specified.')


if __name__ == '__main__':
    main()
