#!/usr/bin/env jython
import os
import re
import requests
import socket
import threading

from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

# to use this, you need to set the bing api env var
bing_api_key = os.environ.get('BING_API_KEY')
print('welcome to ctlfish blackhatpython bing BurpExtender')

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # set up extension
        self._callbacks.setExtensionName('ctlfish blackhatpython bing')
        callbacks.registerContextMenuFactory(self)
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list

    def bing_menu(self, event):
        # get details of users clicked item
        http_traffic = self.context.getSelectedMessages()
        print('{} requests highlighted'.format(len(http_traffic)))

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
            print('User selected host: {}'.format(host))
            self.bing_search(host)
        return

    def bing_search(self, host):
        # check if we have ip or hostname
        is_ip = re.match(r'((?:\d+\.){3}\d+)', host)

        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        bing_query_string = 'ip:{}'.format(ip_address)
        t = threading.Thread(target=self.bing_query, args=(bing_query_string,))
        t.daemon = True
        t.start()
        #self.bing_query(bing_query_string)

        if domain:
            bing_query_string = 'domain:{}'.format(host)
            t = threading.Thread(target=self.bing_query, args=(bing_query_string,))
            t.daemon = True
            t.start()
            #self.bing_query(bing_query_string)
        return

    def bing_query(self, bing_query_string):
        # FYI: you *must* set the lib path for python addons correctly and install requests there
        # while testing, I just pointed to the lib64 version of site-packages within my venv
        # todo: csuttles fix this to use the burp libs to send the requests
        print('Performing Bing search for: {}'.format(bing_query_string))
        bing_url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
        headers = {'user-agent': 'ctlfish/blackhatpython/0.0.1', "Ocp-Apim-Subscription-Key": bing_api_key}
        params = {"q": bing_query_string, "textDecorations": True, "textFormat": "HTML"}
        resp = requests.get(bing_url, params=params, headers=headers)
        #return resp
        try:
            rjson = resp.json()
            for page in rjson['webPages']['value']:
                print('*' * 80)
                print('page url: {}'.format(page["url"]))
                print('page id: {}'.format(page["id"]))
                print('page name: {}'.format(page["name"]))
                j_url = URL(page['url'])
                print('page in scope: {}'.format(self._callbacks.isInScope(j_url)))

                if not self._callbacks.isInScope(j_url):
                    self._callbacks.includeInScope(j_url)
                    print('added {} to Burp Scope'.format(j_url))
                else:
                    print('url {} already in Burp Scope'.format(j_url))
        except Exception as ex:
            print('caught exception {}:{}'.format(ex.__class__.__name__, ex))
            print('no results from Bing')
            pass
        return
