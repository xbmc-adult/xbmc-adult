'''
gethtml with cookies support  v1
by anarchintosh @ xbmcforums
Copyleft = GNU GPL v3 (2011 onwards)

this function is paired with weblogin.py
and is intended to make it easier for coders wishing
to scrape source of pages, while logged in to that site.

USAGE:
!!!!!First set the compatible_urllist below!!!!!!!!!

import gethtml

to load html without cookies
source = gethtml.get(url)

to load html with cookies
source = gethtml.get(url, 'my-path-to-cookiefile')
'''

import urllib2
import cookielib
import os
import re

#!!!!!!!!!!! Please set the compatible_urllist
#set the list of URLs you want to load with cookies.
#matches bits of url, so that if you want to match www243.megaupload.com/ you
#can just put '.megaupload.com/' in the list.
compatible_urllist = ['http://fantasti.cc/', 'http://77.247.181.97/']

USER_AGENT_STRING = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

def url_for_cookies(url):
    #ascertain if the url contains any of the phrases in the list. return True
    #if a match is found.
    for compatible_url in compatible_urllist:
        if re.search(compatible_url, url):
            url_is_compatible = True
            break
        else: url_is_compatible = False
    return url_is_compatible

def get(url, cookiepath=None):
    # use cookies if cookiepath is set and if the cookiepath exists.
    if cookiepath is not None:
        #only use cookies for urls specified
        if url_for_cookies(url) == True:
            #check if user has supplied only a folder path, or a full path
            if not os.path.isfile(cookiepath):
                #if the user supplied only a folder path, append on to the end
                #of the path a common filename.
                cookiepath = os.path.join(cookiepath, 'cookies.lwp')
            #check that the cookie exists
            if os.path.exists(cookiepath):
                cj = cookielib.LWPCookieJar()
                cj.load(cookiepath)
                req = urllib2.Request(url)
                req.add_header('User-Agent', USER_AGENT_STRING)
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                response = opener.open(req)
                link = response.read()
                response.close()
                return link
            else: return _loadwithoutcookies(url)
        else: return _loadwithoutcookies(url)
    else: return _loadwithoutcookies(url)

def _loadwithoutcookies(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT_STRING)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
