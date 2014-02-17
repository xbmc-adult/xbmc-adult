__scriptname__ = "YouJizz.com"
__author__ = "Pillager"
__url__ = "http://code.google.com/p/xbmc-adult/"
__scriptid__ = "plugin.video.you.jizz"
__credits__ = "Pillager & anarchintosh"
__version__ = "1.0.6"

import urllib,urllib2,re
import xbmc,xbmcplugin,xbmcgui,sys

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'


def _get_keyboard(default="", heading="", hidden=False):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard(default, heading, hidden)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
                return unicode(keyboard.getText(), "utf-8")
        return default


def CATEGORIES():
        addDir('Newest','http://www.youjizz.com/newest-clips/1.html',1,'')
        addDir('Top Rated','http://www.youjizz.com/top-rated/1.html',1,'')
        addDir('Random Videos','http://www.youjizz.com/random.php',1,'')
        INDEX('http://www.youjizz.com/page/1.html')


def INDEX(url):
        addDir('Search','http://www.youjizz.com/srch.php?q=',3,'')
        addDir('Home','',None,'')
        link = getHtml(url)
        matchname = re.compile('title1">[\n]{0,1}\s*(.+?)<').findall(link)
        matchurl = re.compile('class="frame" href=\'\/videos\/.+?(\d+).html').findall(link)
        matchthumb = re.compile('data-original="([^"]+jpg)').findall(link)
        matchduration = re.compile('thumbtime\'><span.*>(\d{1,}:\d{2})').findall(link)
        for name,url,thumb,duration in zip(matchname, matchurl, matchthumb,
                                           matchduration):
                url = '/videos/embed/' + url
                addDownLink(name + ' ' + duration, url,2, thumb)
        matchpage = re.compile('pagination[\s\S]+?<span>\d{1,}<\/span>[\s\S]+?href="(.+?html)').findall(link)
        for nexturl in matchpage:
                addDir('Next Page','http://www.youjizz.com' + nexturl,1,'')


def VIDEOLINKS(url,name):
        link = getHtml('http://www.youjizz.com' + url)
        match = re.compile('so.addVariable[(]"file",[^"]+"(http[^"]+flv[^"]+)').findall(link)
        if not match:
                # Try to find a playlist instead on the page
                match = re.compile('so.addVariable\("playlist", "([^"]+)"').findall(link)
                for url in match:
                        # Download the playlist and find the last URL for the
                        # highest def video
                        link = getHtml(url)
                        match = re.compile('file="([^"]+)"').findall(link)
                        if match:
                                match = match[-1:]
                                match[0] = urllib.unquote(match[0])
        if not match:
                print "Failed to find video URL"
        for url in match:
                listitem = xbmcgui.ListItem(name)
                listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
                xbmc.Player().play(url, listitem)


def SEARCHVIDEOS(url):
        searchUrl = url
        vq = _get_keyboard(heading="Enter the query")
        # if blank or the user cancelled the keyboard, return
        if (not vq): return False, 0
        # we need to set the title to our query
        title = urllib.quote_plus(vq)
        searchUrl += title
        print "Searching URL: " + searchUrl
        INDEX(searchUrl)


def getHtml(url):
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
                cleanedparams = params.replace('?','')
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


def addDownLink(name,url,mode,iconimage):
        u = (sys.argv[0] +
             "?url=" + urllib.quote_plus(url) +
             "&mode=" + str(mode) +
             "&name=" + urllib.quote_plus(name))
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png",
                               thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                         url=u, listitem=liz, isFolder=False)
        return ok


def addDir(name,url,mode,iconimage):
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

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url)<1:
        print ""
        CATEGORIES()

elif mode == 1:
        print "" + url
        INDEX(url)

elif mode == 2:
        print "" + url
        VIDEOLINKS(url,name)

elif mode == 3:
        print mode
        SEARCHVIDEOS(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
