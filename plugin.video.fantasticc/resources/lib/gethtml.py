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

from six.moves import urllib_request, urllib_error, http_cookiejar
import os
import re
import sys
from kodi_six import xbmc

# !!!!!!!!!!! Please set the compatible_urllist
# set the list of URLs you want to load with cookies.
# matches bits of url, so that if you want to match www243.megaupload.com/ you
# can just put '.megaupload.com/' in the list.
compatible_urllist = ['https://fantasti.cc/', 'https://www.pornhub.com']

USER_AGENT_STRING = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'


def url_for_cookies(url):
    # ascertain if the url contains any of the phrases in the list. return True
    # if a match is found.
    for compatible_url in compatible_urllist:
        if re.search(compatible_url, url):
            url_is_compatible = True
            break
        else:
            url_is_compatible = False
    return url_is_compatible


def get(url, cookiepath=None, cookie=None, user_agent=None, referer=None):
    # use cookies if cookiepath is set and if the cookiepath exists.
    if cookiepath is not None:
        # check if user has supplied only a folder path, or a full path
        if not os.path.isfile(cookiepath):
            # if the user supplied only a folder path, append on to the end
            # of the path a common filename.
            cookiepath = os.path.join(cookiepath, 'cookies.lwp')
        # check that the cookie exists
        if not os.path.exists(cookiepath):
            with open(cookiepath, 'w') as f:
                f.write('#LWP-Cookies-2.0\n')
        cj = http_cookiejar.LWPCookieJar()
        cj.load(cookiepath)
        req = urllib_request.Request(url)
        if user_agent:
            req.add_header('User-Agent', user_agent)
        else:
            req.add_header('User-Agent', USER_AGENT_STRING)
        if referer:
            req.add_header('Referer', referer)
        if cookie:
            req.add_header('Cookie', cookie)
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj))
        try:
            response = opener.open(req)
        except urllib_error.URLError as e:
            xbmc.log('%s Error opening %s' % (e, url))
            sys.exit(1)
        link = response.read()
        response.close()
        return link
    else:
        return _loadwithoutcookies(url, user_agent)


def _loadwithoutcookies(url, user_agent=None, referer=None):
    xbmc.log('Loading without cookies')
    url = url.replace('http:', 'https:')
    req = urllib_request.Request(url)
    if user_agent:
        req.add_header('User-Agent', user_agent)
    if referer:
        req.add_header('Referer', referer)
    try:
        response = urllib_request.urlopen(req)
    except urllib_error.HTTPError as e:
        xbmc.log("%s %s" % (url, e.reason), xbmc.LOGFATAL)
        sys.exit(0)
    link = response.read()
    response.close()
    return link
