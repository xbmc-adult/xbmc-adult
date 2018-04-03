import sys
import urllib
import urllib2
import cookielib
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

xbmcaddon.Addon(id='plugin.video.empflix')
cookiejar = cookielib.LWPCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
urllib2.build_opener(cookie_handler)


def CATEGORIES():
    link = openURL('http://www.empflix.com/categories.php')
    match = re.compile('/([^/]+)/\?a=1&d=" title="([^"]+)"').findall(link)
    addDir('All', 'http://www.empflix.com/browse.php', 1, '', 1)
    for channame, name in match:
        addDir(name,
               ('http://www.empflix.com/' + channame),
               2, '', 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def SORTMETHOD(url):
    if url == 'http://www.empflix.com/browse.php':
        addDir('Being Watched', url + '?category=bw', 2, '', 1)
        addDir('Most Recent', url + '?category=mr', 2, '', 1)
        addDir('Most Viewed', url + '?category=mv', 2, '', 1)
        addDir('Top Rated', url + '?category=tr', 2, '', 1)
    else:
        match = re.compile('(http://www.empflix.com/channels/)'
                           '(.*)').findall(url)
        for start, end in match:
            addDir('Being Watched', start + 'watched-' + end, 2, '', 1)
            addDir('Most Recent', start + 'new-' + end, 2, '', 1)
            addDir('Most Viewed', start + 'popular-' + end, 2, '', 1)
            addDir('Top Rated', start + 'rated-' + end, 2, '', 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def VIDEOLIST(url, page):
    link = openURL(url + '/?page=' + str(page))
    match = re.compile(r"data-vid.+?data-name='([^']+)'.+?href='([^']+).+?data-original='([^']+)'.+?'>([\d:]+)",
                       re.DOTALL).findall(link)
    for name, videourl, thumb, duration in match:
        addLink(name + ' (' + duration + ')',
                'http://www.empflix.com' + videourl + '?',
                3,
                thumb.strip())
    if len(match) == 24:
        addDir('Next Page', url, 2, '', page + 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def PLAYVIDEO(url):
    link = openURL(url)
    match = re.compile('contentUrl" content="([^"]+)').findall(link)
    xbmc.Player().play(match[0])


def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if len(splitparams) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def addLink(name, url, mode, iconimage):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)\
        + '&name=' + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage='DefaultFolder.png',
                           thumbnailImage=iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=False)
    return ok


def addDir(name, url, mode, iconimage, page):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) +\
        '&name=' + urllib.quote_plus(name) + '&page=' + str(page)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage='DefaultFolder.png',
                           thumbnailImage=iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=True)
    return ok


def openURL(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def main():
    params = get_params()
    url = None
    mode = None
    page = 1

    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    try:
        mode = int(params['mode'])
    except:
        pass
    try:
        page = int(params['page'])
    except:
        pass

    if mode is None or url is None or len(url) < 1:
        CATEGORIES()

    elif mode == 1:
        xbmc.log('SORTMETHOD ' + url)
        SORTMETHOD(url)

    elif mode == 2:
        xbmc.log('VIDEOLIST ' + url)
        xbmc.log('VIDEOLIST ' + str(page))
        VIDEOLIST(url, page)

    elif mode == 3:
        xbmc.log('PLAYVIDEO ' + url)
        PLAYVIDEO(url)


if __name__ == '__main__':
    main()
