#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin, xbmcgui, sys, urllib, urllib2, re, xbmcaddon, socket, HTMLParser

socket.setdefaulttimeout(30)
thisPlugin = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.video.xhamstergay')
userAgentString = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16'
htmlp = HTMLParser.HTMLParser()


def index():
    addDir('Latest Videos', 'http://xhamster.com/channels/new-gays-1.html', 2)
    addDir('Search', '',3)
    xbmcplugin.endOfDirectory(thisPlugin)


def listVideos(url):
    req = urllib2.Request(url)
    req.add_header('Cookie', 'videoFilters=%7B%22sort%22%3A%22da%22%2C%22channels%22%3A%22%3B1%22%7D; path=/; domain=xhamster.com')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    ##link3=re.sub("<div class=\"vDate\">Promoted Videos.*?<div class='vDate'>",'',link,re.MULTILINE|re.DOTALL)
    
    match=re.compile("<a href='([^']+)'  class='hRotator' ><img src='([^']+)' width='160' height='120' class='thumb' alt=\"([^\"]+)\"/>",re.MULTILINE|re.DOTALL).findall(link)
    for url2,thumbnail,name in match:
        addLink(htmlp.unescape(name), htmlp.unescape(url2), 1, htmlp.unescape(thumbnail))        
    match=re.compile("<a href='([^']+)'>\d+</a><a href='([^']+)' class='last colR'><div class='icon iconPagerNextHover'></div>Next</a>",re.MULTILINE|re.DOTALL).findall(link)        
    for url_last,url_next in match:
        addDir('Load More Videos ...', 'http://xhamster.com/' + htmlp.unescape(url_next),2)
        ##addDir('LAST', 'http://xhamster.com' + url_last,2)
    match=re.compile("<a href='([^']+)'>\d+</a><a href='([^']+)' class='last' overicon='iconPagerNextHover'>",re.MULTILINE|re.DOTALL).findall(link)        
    for url_last,url_next in match:
        addDir('Load More Videos ...', 'http://xhamster.com/' + htmlp.unescape(url_next),2)
        ##addDir('LAST', 'http://xhamster.com' + url_last,2)
    match=re.compile("<a href='([^']+)' class='first' overicon='iconPagerPrevHover'><div class='icon iconPagerPrev'></div>Prev</a>",re.MULTILINE|re.DOTALL).findall(link)
    ##for url_prev in match:
        ##addDir('PREV', 'http://xhamster.com' + url_prev,2)
    xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode(500)")


def playVideo(url):
    match=re.compile('/(\d+)/(.*)\.html',re.MULTILINE|re.DOTALL).findall(url)        
    for cod,t in match:
        reqlink='http://youdownload.newdigest.com/capture.php?cod='+cod+'&t='+t
    req = urllib2.Request(reqlink)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    listitem = xbmcgui.ListItem(path=link)
    return xbmcplugin.setResolvedUrl(thisPlugin, True, listitem)


def search():
    keyboard = xbmc.Keyboard('', 'Search')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText()
        url="http://xhamster.com/search.php?qcat=video&page=1&q="+urllib.quote_plus(search_string)
        listVideos(url)


def addLink(name, url, mode=1, iconimage='', description='', isVideo=True):
    u    = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
    ok   = True
    icon = 'DefaultVideo.png'
    if (not isVideo):
        icon = 'DefaultAudio.png'
    liz  = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ 'Title': name } )
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
    playVideo(url)
elif mode == "2":
    listVideos(url)
elif mode == "3":
    search()
else:
    index()
