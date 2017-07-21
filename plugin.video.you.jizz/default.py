__scriptname__ = "YouJizz.com"
__author__ = "Pillager"
__url__ = "http://code.google.com/p/xbmc-adult/"
__scriptid__ = "plugin.video.you.jizz"
__credits__ = "Pillager & anarchintosh"
__version__ = "1.0.6"

import urllib, urllib2, re, HTMLParser, json
import xbmc, xbmcplugin, xbmcgui, sys

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
BASE_URL = 'https://www.youjizz.com'

def _get_keyboard(default="", heading="", hidden=False):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard(default, heading, hidden)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
                return unicode(keyboard.getText(), "utf-8")
        return default


def CATEGORIES():
        addDir('Newest', BASE_URL + '/newest-clips/1.html', 1, '')
        addDir('Top Rated', BASE_URL + '/top-rated/1.html', 1, '')
        addDir('Random Videos', BASE_URL + '/random.php', 1, '')
        INDEX(BASE_URL + '/most-popular' + '/1.html')


def INDEX(url):
        addDir('Search', BASE_URL + '/search/%s-1.html', 3, '')
        addDir('Home', '', None, '')
        link = getHtml(url)
        link = re.compile('content">[\s\S]+<div class="desktop-only">([.\s\S]+)<div class="mobile-only').findall(link)[0]
        matchname = re.compile('title">[^>]+>([^<]+)').findall(link)
        matchurl = re.compile('class="frame" href="(/videos/.+?\d+.html)').findall(link)
        matchthumb = re.compile('data-original="([^"]+jpg)').findall(link)
        matchduration = re.compile('time">(\d{1,}:\d{2}:?\d{0,2})').findall(link)
        for name, url, thumb, duration in zip(matchname, matchurl, matchthumb, matchduration):
                addDownLink(name + ' ' + '(' + duration + ')', url, 2, "https:" + thumb)
        matchpage = re.compile('pagination".+?active.+?<li><a href="([^"]+html)').findall(link)
        if matchpage:
                addDir('Next Page', BASE_URL + '' + matchpage[0], 1, '')


def VIDEOLINKS(url, name):
        h = HTMLParser.HTMLParser()
        link = getHtml(BASE_URL + '' + url)
        encodings = re.compile('var encodings = (\[[.\s\S]+?\]);').findall(link)

        if not encodings:
                xbmc.log("Failed to find video URL")
        else:
                encodings = json.loads(encodings[0])

                for encoding in encodings:
                        if "_hls" not in encoding['filename']:
                                url = h.unescape(encoding['filename'])
                                listitem = xbmcgui.ListItem(name)
                                listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
                                xbmc.Player().play('https:' + url, listitem)


def SEARCHVIDEOS(url):
        searchUrl = url
        vq = _get_keyboard(heading="Enter the query")
        # if blank or the user cancelled the keyboard, return
        if (not vq): return False, 0
        # we need to set the title to our query
        title = re.sub('[^0-9a-zA-Z]+', '-', vq)
        searchUrl = searchUrl % title
        xbmc.log("Searching URL: " + searchUrl)
        INDEX(searchUrl)


def getHtml(url):
        xbmc.log("getHtml: " + url)
        req = urllib2.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data


def getParams():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params)-1] == '/'):
                        params = params[0:len(params)-2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]

        return param


def addDownLink(name, url, mode, iconimage):
        u = (sys.argv[0] +
             "?url=" + urllib.quote_plus(url) +
             "&mode=" + str(mode) +
             "&name=" + urllib.quote_plus(name))
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png",
                               thumbnailImage=iconimage)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                         url=u, listitem=liz, isFolder=False)
        return ok


def addDir(name, url, mode, iconimage):
        u = (sys.argv[0] +
             "?url=" + urllib.quote_plus(url) +
             "&mode=" + str(mode) +
             "&name=" + urllib.quote_plus(name))
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",
                               thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                         url=u, listitem=liz, isFolder=True)
        return ok


params = getParams()
url = None
name = None
mode = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass

xbmc.log("Mode: " + str(mode))
xbmc.log("URL: " + str(url))
xbmc.log("Name: " + str(name))

if mode == None or url == None or len(url)<1:
        CATEGORIES()

elif mode == 1:
        INDEX(url)

elif mode == 2:
        VIDEOLINKS(url, name)

elif mode == 3:
        SEARCHVIDEOS(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
