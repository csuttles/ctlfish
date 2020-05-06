#!/usr/bin/env jython
import re

from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import IResponseInfo

from javax.swing import JMenuItem
from java.util import List, ArrayList, Arrays
from java.net import URL

from datetime import datetime
from HTMLParser import HTMLParser

class TagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []

    def handle_data(self, data):
        self.page_text.append(data)

    def handle_comment(self, data):
        self.handle_data(data)

    def strip(self, html):
        self.feed(html)
        return " ".join(self.page_text)


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
        self.hosts = set()

        # start with a common seed
        self.wordlist = set(['password'])

        # set extension metadata
        callbacks.setExtensionName('ctlfish blackhatpython wordlist generator')
        callbacks.registerContextMenuFactory(self)

        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem('Create Wordlist', actionPerformed=self.wordlist_menu))
        return menu_list

    def wordlist_menu(self, event):
        # get details of user selction in UI
        http_traffic = self.context.getSelectedMessages()

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            self.hosts.add(host)

            http_resp = traffic.getResponse()

            if http_resp:
                self.get_words(http_resp)
        self.display_wordlist()
        return

    def get_words(self, http_resp):
        # array.array has tostring() not toString()
        headers, body = http_resp.tostring().split('\r\n\r\n', 1)

        # end early to skip non-text responses (don't generate wordlists from pictures, derp)
        if headers.lower().find('content-type: text') == -1:
            return

        # if we got here, we have a text response so let's parse html and grab text
        tag_stripper = TagStripper()
        page_text = tag_stripper.strip(body)

        # make raw text into wordlist (all words between 3 and 16 chars)
        for word in re.findall(r'\w{3,}', page_text):
            if len(word) <= 16:
                self.wordlist.add(word.lower())
        return

    def mangle(self, word):
        year = datetime.now().year
        suffixes = ['', '1', '!', year]
        mangled = []

        for passwd in [word, word.capitalize()]:
            for suffix in suffixes:
                mangled.append('{}{}'.format(word, suffix))

        return mangled

    def display_wordlist(self):
        print('#!comment: ctlfish BHP wordlist for site(s) {}'.format(', '.join(self.hosts)))
        for word in sorted(self.wordlist):
            for passwd in self.mangle(word):
                print(passwd)
        return

