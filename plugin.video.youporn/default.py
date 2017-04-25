#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin, xbmcgui, sys, urllib, urllib2, re, xbmcaddon, socket, HTMLParser

socket.setdefaulttimeout(300)
thisPlugin = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.video.youporn11')
userAgentString = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'
htmlp = HTMLParser.HTMLParser()


def index():
    addDir('Latest Videos (RSS)', 'http://www.youporn.com/rss/')
    addDir('Latest Videos', 'http://www.youporn.com/',3)
    addDir('Top Rated', 'http://www.youporn.com/top_rated/',3)
    addDir('Most Viewed', 'http://www.youporn.com/most_viewed/',3)
    addDir('Most Favorited', 'http://www.youporn.com/most_favorited/',3)
    addDir('Most Discussed', 'http://www.youporn.com/most_discussed/',3)
    addDir('Search', 'lol',4)
    xbmcplugin.endOfDirectory(thisPlugin)


def listVideosRss(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<item>\s*<title>(.*?)</title>\s*<link>(.*?)</link>\s*<description>.*?IMG border="1" src="(.*?)".*?Length: (\d+:\d+).*?</item>',re.MULTILINE|re.DOTALL).findall(link)
    for name,url,thumbnail,length in match:
	addLink(htmlp.unescape(name), url, 2, htmlp.unescape(thumbnail),'',True,length)
    xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode(500)")


def listVideos(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<a href="([^"]+)">\s*<img src="([^"]+)" alt="([^"]+)" class="flipbook" data-max="[^"]+" data-video-id="[^"]+" data-thumbnail="[^"]+" data-path="[^"]+">\s*<p class="videoTitle" title="[^"]+">[^<]+</p>\s*<span class="duration">[^<]+</span>\s*<span class="rating up"><i>[^<]+</i>\s*</span>\s*</a>',re.MULTILINE|re.DOTALL).findall(link)
    for url2,thumbnail,name in match:
        addLink(htmlp.unescape(name), 'http://www.youporn.com' + url2, 2, htmlp.unescape(thumbnail))
    xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode(500)")


def playVideo(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<a href="([^"]+)">\s*MP4 - For Windows 7, Mac and iPad\s*</a>',re.MULTILINE|re.DOTALL).findall(link)
    for url in match:
		listitem = xbmcgui.ListItem(path=htmlp.unescape(url))
    return xbmcplugin.setResolvedUrl(thisPlugin, True, listitem)


def search(url):
    keyboard = xbmc.Keyboard('', 'Search')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText()
        url="http://www.youporn.com/search/?query="+urllib.quote_plus(search_string)
        listVideos(url)


def addLink(name, url, mode=1, iconimage='', description='', isVideo=True, duration=''):
    u    = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
    ok   = True
    icon = 'DefaultVideo.png'
    if (not isVideo):
        icon = 'DefaultAudio.png'
    liz  = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ 'Title': name,'Duration':duration } )
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode=1, iconimage=''):
    u   = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
    ok  = True
    liz = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ 'Title': name })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def parameters_string_to_dict(parameters):
    """Convert parameters encoded in a URL to a dict."""
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split('&')
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)
if mode == "1":
    listVideosRss(url)
elif mode == "2":
    playVideo(url)
elif mode == "3":
    listVideos(url)
elif mode == "4":
    search(url)
else:
    index()
