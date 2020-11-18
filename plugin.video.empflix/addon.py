import sys
import re
from six.moves import urllib_request, urllib_parse, http_cookiejar
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui


xbmcaddon.Addon(id='plugin.video.empflix')
cookiejar = http_cookiejar.LWPCookieJar()
cookie_handler = urllib_request.HTTPCookieProcessor(cookiejar)
urllib_request.build_opener(cookie_handler)


def CATEGORIES():
    link = openURL('https://www.empflix.com/categories.php')
    match = re.compile(r'/([^/]+)/\?a=1&d=" title="([^"]+)"').findall(link)
    addDir('All', 'https://www.empflix.com/', 1, '', 1)
    for channame, name in match:
        addDir(name,
               ('https://www.empflix.com/' + channame),
               2, '', 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def SORTMETHOD(url):
    if url == 'https://www.empflix.com/':
        addDir('Featured', url + 'featured', 2, '', 1)
        addDir('Most Recent', url + 'new', 2, '', 1)
        addDir('Most Viewed', url + 'popular', 2, '', 1)
        addDir('Top Rated', url + 'toprated', 2, '', 1)
    else:
        match = re.compile('(https://www.empflix.com/channels/)'
                           '(.*)').findall(url)
        for start, end in match:
            addDir('Being Watched', start + 'watched-' + end, 2, '', 1)
            addDir('Most Recent', start + 'new-' + end, 2, '', 1)
            addDir('Most Viewed', start + 'popular-' + end, 2, '', 1)
            addDir('Top Rated', start + 'rated-' + end, 2, '', 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def VIDEOLIST(url, page):
    link = openURL(url + '/?page=' + str(page))
    match = re.compile(r"data-vid='([^']+)'.+?data-name='([^']+)'.+?data-original='([^']+)'.+?'>([\d:]+)",
                       re.DOTALL).findall(link)
    for videourl, name, thumb, duration in match:
        addLink(name + ' (' + duration + ')',
                'https://player.empflix.com/video/' + videourl + '?',
                3,
                thumb.strip())
    if len(match) == 60 or len(match) == 83:
        addDir('Next Page', url, 2, '', page + 1)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def PLAYVIDEO(url):
    link = openURL(url)
    match = re.compile(r'config\s*=\s*"([^"]+)').findall(link)
    link = openURL('https:' + match[0])
    match = re.compile('<res>.+p</[^/]+([^]]+)').findall(link)
    match.reverse()
    xbmc.Player().play('https:' + match[0] + '|Referer=https://www.empflix.com/')


def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if len(splitparams) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def addLink(name, url, mode, iconimage):
    u = sys.argv[0] + '?url=' + urllib_parse.quote_plus(url) + '&mode=' + str(mode)\
        + '&name=' + urllib_parse.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage, 'icon': 'DefaultFolder.png'})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=False)
    return ok


def addDir(name, url, mode, iconimage, page):
    u = sys.argv[0] + '?url=' + urllib_parse.quote_plus(url) + '&mode=' + str(mode) +\
        '&name=' + urllib_parse.quote_plus(name) + '&page=' + str(page)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage, 'icon': 'DefaultFolder.png'})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=True)
    return ok


def openURL(url):
    xbmc.log("Opening %s" % url)
    req = urllib_request.Request(url)
    req.add_header('Referer', 'https://www.empflix.com/')
    response = urllib_request.urlopen(req)
    link = response.read().decode('utf-8')
    response.close()
    return link


def main():
    params = get_params()
    url = None
    mode = None
    page = 1

    try:
        url = urllib_parse.unquote_plus(params['url'])
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
