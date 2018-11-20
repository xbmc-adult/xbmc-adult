# The documentation written by Voinage was used as a template for this addon
# http://wiki.xbmc.org/?title=HOW-TO_write_plugins_for_XBMC
#
# This addon is licensed with the GNU Public License, and can freely be modified
# http://www.gnu.org/licenses/gpl-2.0.html

import urllib, urllib2, re, sys, xbmcplugin, xbmcgui

def CATEGORIES():
    addDir("Most Recent", "https://lubetube.com", 1, "")
    link = read_url('https://lubetube.com/categories')
    match = re.compile('<a href="(https://lubetube.com/search/adddate/cat/[^/]+/)[^>]+>([^<]+)').findall(link)
    for url, title in match:
        url = url + "?page=1"
        addDir(title, url, 1, "")

def INDEX(url):
    # url: http://lubetube.com/search/adddate/cat/bondage/page=1
    add_next(url)
    link = read_url(url)
    match = re.compile('<a class="frame[^"]*"'
                       ' href="(https://lubetube.com/video/[^"]+)" '
                       'title="([^"]+)">.*?<img src="([^"]+)".+?Length:([^<]+)',
                       re.DOTALL).findall(link)
    for url, name, thumbnail, length in match:
        addDownLink(name + length, url, 2, thumbnail)

def VIDEOLINKS(url, name):
    link = read_url(url)
    match = re.compile('video-hd" href="([^"]+)" data').findall(link)
    for url in match:
        listitem = xbmcgui.ListItem(name)
        listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
        xbmc.Player().play(url, listitem)
        return

def add_next(url):
    match = re.compile('(\d+)$').findall(url)
    if match:
        page_number = int(match[0])
        page_number+=1 # This will 404 eventually
        category_url=url.split('=')[0]
        next_url = category_url + '=' + str(page_number)
        addDir("Next", next_url, 1, "")

def read_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB;'
                   ' rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_params():
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
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + \
        str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png",
                           thumbnailImage=iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=False)
    return ok

def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + \
        str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",
                           thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=True)
    return ok


topparams = get_params()
topurl = None
topname = None
topmode = None

try:
    topurl = urllib.unquote_plus(topparams["url"])
except:
    pass
try:
    topname = urllib.unquote_plus(topparams["name"])
except:
    pass
try:
    topmode = int(topparams["mode"])
except:
    pass

print "Mode: " + str(topmode)
print "URL: " + str(topurl)
print "Name: " + str(topname)

if topmode == None or topurl == None or len(topurl)<1:
    print ""
    CATEGORIES()

elif topmode == 1:
    print "" + topurl
    INDEX(topurl)

elif topmode == 2:
    print "" + topurl
    VIDEOLINKS(topurl, topname)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
