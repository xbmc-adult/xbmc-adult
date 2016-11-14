#!/usr/bin/python
#Code Heavily modified from  Demo by TV DASH - by You 2008.
#
# Written by Ksosez with help from anarchintosh
# Released under GPL(v2)

import urllib, urllib2, htmllib
import re, string
import os
import sys
import xbmcplugin, xbmcaddon, xbmcgui, xbmc

#addon name
__addonname__ = 'plugin.video.fantasticc'

#get path the default.py is in.
__addonpath__ = xbmcaddon.Addon(id=__addonname__).getAddonInfo('path')

#datapath
__datapath__ = xbmc.translatePath('special://profile/addon_data/'+__addonname__)

#append lib directory
sys.path.append( os.path.join( __addonpath__, 'resources', 'lib' ) )

#import from lib directory
import weblogin
import gethtml


pluginhandle = int(sys.argv[1])

# example of how to get path to an image
default_image = os.path.join(__addonpath__, 'resources', 'images',
                             'provocative_logo.png')

# string to simplify urls
main_url = 'http://fantasti.cc/'
# fantasti.cc's ip
fip = 'http://77.247.181.97/'

# 3rd Party video Sites that are currently supported are listed below

SUPPORTEDSITES = ['deviantclip', 'empflix', 'madthumbs', 'pornhub', 'redtube',
                  'tnaflix', 'tube8', 'xhamster', 'xtube', 'xvideos',
                  'you_porn']


def get_html(url):
    return gethtml.get(url, __datapath__)


def get_avatar(lc):
    #using lowercase username, build the url to the user's avatar
    url = fip + 'avatar/' + lc[0] + '/' + lc[1] + '/' + lc[2] + '/' + lc

    #trial and error to find the correct image format
    urlist = [url + '.jpeg', url + '.jpg', url + '.png', url + '.gif']
    for surl in urlist:
        try:
            urllib2.urlopen(surl)
        except urllib2.URLError:
            pass
        else:
            return surl
    return 'http://fantasticc2.so.clients.cdn13.com/no_image_avatar.jpg'


def Notify(title, message, times, icon):
    xbmc.executebuiltin('XBMC.Notification(' + title + ', ' + message + ', ' +
                        times + ', ' + icon + ')')


def LOGIN(username, password, hidesuccess):
    uc = username[0].upper() + username[1:]
    lc = username.lower()

    logged_in = weblogin.doLogin(__datapath__, username, password)
    if logged_in == True:
        avatar = get_avatar(lc)

        if hidesuccess == 'false':
            Notify('Welcome back ' + uc, 'Fantasti.cc loves you', '4000',
                   avatar)

        addDir(uc + '\'s Videos',
               main_url + 'user/' + lc + '/videos/save_date', 1, avatar)
        addDir(uc + '\'s Collections',
               main_url + 'user/' + lc + '/collections', 2, avatar)
        addDir(uc + '\'s Favourited Collections',
               main_url + 'user/' + lc + '/collections/favorited', 2, avatar)
        addDir(uc + '\'s Rated Collections',
               main_url + 'user/' + lc + '/collections/rated', 2, avatar)

    elif logged_in == False:
        Notify('Login Failure', uc + ' could not login', '4000', default_image)


def STARTUP_ROUTINES():
    #deal with bug that happens if the datapath doesn't exist
    if not os.path.exists(__datapath__):
        os.makedirs(__datapath__)

    #check if user has enabled use-login setting
    usrsettings = xbmcaddon.Addon(id=__addonname__)
    use_account = usrsettings.getSetting('use-account')

    if use_account == 'true':
        #get username and password and do login with them
        #also get whether to hid successful login notification
        username = usrsettings.getSetting('username')
        password = usrsettings.getSetting('password')
        hidesuccess = usrsettings.getSetting('hide-successful-login-messages')

        LOGIN(username, password, hidesuccess)


def CATEGORIES():
    STARTUP_ROUTINES()

    mode = 1
    addDir('Popular Today',
           main_url+'videos/popular/today/', mode, default_image)
    addDir('Popular Last 7 Days',
           main_url+'videos/popular/7days/', mode, default_image)
    addDir('Popular Last Month',
           main_url+'videos/popular/31days/', mode, default_image)
    addDir('Popular All Time',
           main_url+'videos/popular/all_time/', mode, default_image)
    addDir('Upcoming', main_url+'videos/upcoming/', mode, default_image)
    addDir('Made Popular', main_url+'videos/made_popular/', mode, default_image)

    mode = 2
    addDir('Collections Upcoming',
           main_url+'videos/collections/upcoming/',
           mode, default_image)
    addDir('Collections Today - Popular',
           main_url+'videos/collections/popular/today/',
           mode, default_image)
    addDir('Collections Today - Most Viewed',
           main_url+'videos/collections/most_viewed/today/',
           mode, default_image)
    addDir('Collections Today - Most Discussed',
           main_url+'videos/collections/most_discussed/today/',
           mode, default_image)
    addDir('Collections Today - Top Favorited',
           main_url+'videos/collections/top_favorites/today/',
           mode, default_image)
    addDir('Collections Last week - Popular',
           main_url+'videos/collections/popular/7days/',
           mode, default_image)
    addDir('Collections Last week - Most Viewed',
           main_url+'videos/collections/most_viewed/7days/',
           mode, default_image)
    addDir('Collections Last week - Most Discussed',
           main_url+'videos/collections/most_discussed/7days/',
           mode, default_image)
    addDir('Collections Last week - Top Rated',
           main_url+'videos/collections/top_rated/7days/',
           mode, default_image)
    addDir('Collections Last week - Top Favorited',
           main_url+'videos/collections/top_favorites/7days/',
           mode, default_image)
    addDir('Collections Last month - Popular',
           main_url+'videos/collections/popular/31days/',
           mode, default_image)
    addDir('Collections Last month - Most Viewed',
           main_url+'videos/collections/most_viewed/31days/',
           mode, default_image)
    addDir('Collections Last month - Most Discussed',
           main_url+'videos/collections/most_discussed/31days/',
           mode, default_image)
    addDir('Collections Last month - Top Rated',
           main_url+'videos/collections/top_rated/31days/',
           mode, default_image)
    addDir('Collections Last month - Top Favorited',
           main_url+'videos/collections/top_favorites/31days/',
           mode, default_image)
    addDir('Collections All-Time - Popular',
           main_url+'videos/collections/popular/all_time/',
           mode, default_image)
    addDir('Collections All-Time - Most Viewed',
           main_url+'videos/collections/most_viewed/all_time/',
           mode, default_image)
    addDir('Collections All-Time - Most Discussed',
           main_url+'videos/collections/most_discussed/all_time/',
           mode, default_image)
    addDir('Collections All-Time - Top Rated',
           main_url+'videos/collections/top_rated/all_time/',
           mode, default_image)
    addDir('Collections All-Time - Top Favorited',
           main_url+'videos/collections/top_favorites/all_time/',
           mode, default_image)

    # didn't need to pass search a url. so i was lazy and passed it the
    # main_url as a dummy
    addDir('Search', main_url, 5, default_image)

    xbmc.log('pluginhandle %s' % pluginhandle)
    xbmcplugin.endOfDirectory(pluginhandle)


def SEARCH(url):
    # define the keyboard
    kb = xbmc.Keyboard('', 'Search Fantasti.cc Videos', False)

    # call the keyboard
    kb.doModal()

    # if user presses enter
    if (kb.isConfirmed()):

        # get text from keyboard
        search = kb.getText()

        # if the search text is not nothing
        if search is not '':

            # encode the search phrase to put in url 
            # (ie replace ' ' with '+' etc)
            # normally you would use: search = urllib.quoteplus(search)
            # but fantasti's search urls are a bit weird
            search = re.sub(' +', '+', search)

            # create the search url
            search_url = main_url + 'search/' + search + '/tube/'
            xbmc.log('SEARCH:%s' % search_url)

            # get the source code of first page
            first_page = get_html(search_url)

            # do a search to see if no results found
            no_results_found = re.search('result-items">\s+</div>', first_page)

            # if there are results on page...
            if not no_results_found:

                # scrape to get the number of all the results pages (this is
                # listed on the first page)
                match = re.compile(
                    '([^"]+)page_(\d+)">last').findall(first_page)

                # if there weren't any multiple pages of search results
                if not match:
                    # ...directly call the results scraper for the first page
                    # to add the directories.
                    SEARCH_RESULTS(url=False, html=first_page)

                # if there were any multiple pages of search results
                if match:

                    # convert the list of strings produced by re.compile to a
                    # list of integers, so we can use them for calculations
                    xbmc.log('Number of pages:%s' % match[0][1])
                    total_pages = int(match[0][1])

                    # generate a list of numbers 1 to total_pages (eg if
                    # total_pages is 3 generate: 1, 2, 3)
                    num = 1
                    numlist = list('1')
                    while num < total_pages:
                        num = num+1
                        numlist.append(str(num))

                    # for every number in the list
                    for thenumber in numlist:

                        # transform thenumber from an integer to a string, to
                        # use in name and url strings
                        thenumber = str(thenumber)

                        # make the page name
                        name = 'Page ' + thenumber

                        search_url = main_url + match[0][0]
                        # make the page url
                        url = search_url + 'page_' + thenumber

                        # add the results page as a directory
                        addDir(name, url, 6, default_image)


def SEARCH_RESULTS(url, html=False):
    # this function scrapes the search results pages
    # accepts page source code (html) for any searches where there is only one
    # page of results
    if html is False:
        xbmc.log(url)
        html = get_html(url)
    match = re.compile('searchVideo">\s+<a href="([^"]+)">\s+<img src="([^"]+)"'
                       ).findall(html)
    for gurl, thumbnail in match:
        name = gurl.split('/')[-2]
        addSupportedLinks(gurl, name, thumbnail)


def INDEX(url):
    html = get_html(url)
    if 'collection' in url: # Collections
        match = re.compile('<i class="submitted-video-play fa fa-play-circle-o"></i>.*?<img height=".*?" width=".*?".src="(.+?)".alt="(.*?)">.*?<a href="(.*?)"', re.DOTALL).findall(html)
        for thumbnail, name, gurl in match:
            vid_id = string.split(gurl, '/')[-3]
            realurl = 'http://fantasti.cc/video.php?id=%s' % vid_id
            mode = 4
            xbmc.log('realurl %s' % realurl)
            addLink(name, realurl, mode, thumbnail)

        match = re.compile('#(\d+)').findall(url)
        if not match:
            fixedNext = url + '#2'
        else:
            page = int(match[0]) + 1
            fixedNext = url.rstrip('123456789') + str(page)

        mode = 1
        xbmc.log('fixedNext %s' % fixedNext)
        addDir('Next Page', fixedNext, mode, default_image)
    else:
        match = re.compile('<a href="([^"]+)"><img src="([^"]+)"'
                           ' alt="([^"]+)"[^>]+>.+?'
                           'style="font-size:11px;">\s+([\d:h ]+)',
                           re.DOTALL).findall(html)
        for gurl, thumbnail, name, duration in match:
            name = '%s  (%s min)' % (name, duration.rstrip())
            addSupportedLinks(gurl, name, thumbnail)
        match = re.compile('<a href="([^"]+)">next &gt;&gt;</a></span></div>'
                          ).findall(html)
        mode = 1
        fixedNext = 'http://fantasti.cc%s' % match[0]
        addDir('Next Page', fixedNext, mode, default_image)
    xbmcplugin.endOfDirectory(pluginhandle)


def addSupportedLinks(gurl, name, thumbnail):
    for each in SUPPORTEDSITES:
        if each in thumbnail:
            realurl = 'http://fantasti.cc%s' % gurl
            mode = 4
            addLink(name, realurl, mode, thumbnail)
            return
    xbmc.log('Unsupported site %s' % thumbnail)


def INDEXCOLLECT(url):   # Index Collections Pages
    xbmc.log('URL Loading: %s' % url)
    html = get_html(url)

    match = re.compile('<a class="clnk" href="(.+?)">(.+?)</a>(.+?)<div ' +
                       'class="tag-list">', re.DOTALL).findall(html)

    for gurl, name, chtml in match:
        xbmc.log('Name [%s]' % name)
        realurl = 'http://fantasti.cc%s' % gurl
        name = unescape(name)
        mode = 1

        #scrape number of vids
        vidnumber = re.search('"videosListNumber"><b>(.*?)<',chtml)
        if vidnumber:
            num_of_vids = vidnumber.group(1)
        else:
            num_of_vids = len(re.findall('div (class="item")',chtml))

        # do some cool stuff to get the images and join them.
        icons = re.compile("background:.*?(http.*?)'").findall(chtml)

        if not icons:
          continue # some collections are empty so they don't have icons

        addDir('%s (%s vids)'%(name,num_of_vids), realurl, mode, icons[0])

    try:
        next_match = re.compile(
            '<a href="([^"]+)">next &gt;&gt;</a>').findall(html)
        mode = 2
        fixedNext = 'http://fantasti.cc%s' % next_match[0]
        xbmc.log('FixedNext: %s' % fixedNext)
        addDir('Next Page', fixedNext, mode, default_image)
    except IndexError:
        xbmc.log("IndexError skipped")
        pass

    xbmcplugin.endOfDirectory(pluginhandle)


def PLAY(url, topthumbnail):
    xbmc.log('Play URL: %s' % url)
    if 'id=' in url:
        realurl = GET_LINK(url, 1 ,topthumbnail)
    else:
        realurl = GET_LINK(url, 0 ,topthumbnail)
    xbmc.log('Real url: %s' % realurl)
    if not realurl:
        Notify('Failure', 'Try another video', '4000', default_image)

    item = xbmcgui.ListItem(path=realurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)


def GET_LINK(url, collections, url2):
# Get the real video link and feed it into XBMC
    xbmc.log('GET_LINK URL: %s' % url)
    html = get_html(url)
    if collections == 1:   # Make sure we get a url we can parse
        match = re.compile('<link rel="canonical" href="(.+?)" />'
                          ).findall(html)
        for each in match:
            url = each

    if 'xvideos' in url2:
        match = re.compile('(http://www.xvideos.com/.+?)"').findall(html)
        html = get_html(match[0])
        match = re.compile('flv_url=(.+?)&amp').findall(html)
        fetchurl = urllib.unquote(match[0])
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'pornhub' in url2:
        match = re.compile('source="([^"]+)').findall(html)
        html = get_html(match[0])
        match = re.compile('quality_[^=]+= \'([^\']+)').findall(html)
        fetchurl = urllib2.unquote(match[0])
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'empflix' in url2:
        match = re.compile('<a style="color:#BBB;" href="([^"]+)"'
                           ' target="_blank" rel="nofollow">empflix</a></span>'
                          ).findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('name="config" value="([^"]+)"').findall(html)
        for configurl in match:
            linkurl = urllib.unquote(configurl)
        html = get_html(linkurl)
        match2 = re.compile('<videoLink>([^<]+)</videoLink>').findall(html)
        fetchurl = match2[0]
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'tnaflix' in url2:
        match = re.compile('iframe src="(http://player[^"]+)').findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('flashvars\.config\s*=\s*escape\("([^"]*)"\);'
                          ).findall(html)
        for each in match:
            html = get_html('http:' + each)
            match = re.compile('<videoLink>([^<]*)').findall(html)
        for each in match:
            fetchurl = each
            xbmc.log('fetchurl: %s' % fetchurl)
    elif 'xhamster' in url2:
        match = re.compile('http://xhamster.com/movies/[^"]*').findall(html)
        html = get_html(match[0])
        match = re.compile('file: \'([^\']+)\'').findall(html)
        fetchurl = match[0]
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'hardsextube' in url2:
        match = re.compile(
            'http://www.hardsextube.com/(video/.+?)"').findall(html)
        html = get_html('http://m.hardsextube.com/%s' % match[0])
        match = re.compile('href="(.+?)" .*playVideoLink').findall(html)
        fetchurl = match[0]
        fetchurl = fetchurl.replace(' ', '+')
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'xtube' in url2:
        match = re.compile('(http://www.xtube.com/.+?)"').findall(html)
        html = get_html(match[0])
        match = re.compile('videoMp4 = "(.+?)"').findall(html)
        for each in match:
            fetchurl = each.replace('\\', '')
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'deviantclip' in url2:
        match = re.compile('<a style="color:#BBB;" href="(.+?)" target="_blank"'
                           ' rel="nofollow">deviantclip</a>').findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('"file":"(.+?)"').findall(html)
        for each in match:
            fetchurl = urllib.unquote(each)
    elif 'redtube' in url2:
        match = re.compile('(http://www.redtube.com/.+?)"').findall(html)
        html = get_html(match[0])
        match = re.compile('(http:[^"]+\.mp4[^"]+)').findall(html)
        fetchurl = urllib.unquote(match[0])
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'tube8' in url2:
        match = re.compile('source='
                           '"(http://www.tube8.com/[^"]+)"').findall(html)
        html = get_html(match[0])
        match = re.compile('page_params.videoUrlJS = "([^"]+)').findall(html)
        fetchurl = urllib2.unquote(match[0])
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'you_porn' in url2:
        match = re.compile('"(http://www.youporn.com/watch/[^"]+)"'
                          ).findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('video[^>]+src="([^"]+)').findall(html)
        for each in match:
            fetchurl = each.replace('&amp;', '&')
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'madthumbs' in url2:
        match = re.compile('href="(http://www.madthumbs.com/[^"]+)"'
                          ).findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('<source src="([^"]+mp4[^"]+)"').findall(html)
        for each in match:
            fetchurl = each.replace('&amp;', '&')
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'pornxs' in url2:
        match = re.compile('(http://pornxs.com/.+?)"').findall(html)
        html = get_html(match[0])
        match = re.compile('config-final-url="(.+?)"').findall(html)
        fetchurl = urllib.unquote(match[0])
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'xhcdn' in url2:
        match = re.compile('http://xhamster.com/movies/[^"]*').findall(html)
        html = get_html(match[0])
        match = re.compile('file: \'([^\']+)\'').findall(html)
        fetchurl = match[0]
        xbmc.log('fetchurl: %s' % fetchurl)
    elif 'spankwire' in url2:
        match = re.compile('data-origin-source="(http://www.spankwire.com/.+?)">').findall(html)
        html = get_html(match[0])
        match = re.compile('playerData.cdnPath.+?= \'(.+?)\'').findall(html)
        qualityarray = match
        # Play highest quality version
        qualityarray.reverse()
        fetchurl = urllib.unquote(qualityarray[0])
        xbmc.log('fetchurl: %s' % fetchurl)
    else:
        xbmc.log('Unknown source (%s).' % url2)
        fetchurl = None
    return fetchurl


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring)>= 2:
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


def addLink(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) \
        + "&name=" + urllib.quote_plus(name) + "&name=" + "&iconimage=" \
        + urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage='DefaultVideo.png',
                           thumbnailImage=iconimage)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) \
        + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",
                           thumbnailImage=iconimage)
    liz.setInfo( type='Video', infoLabels={ 'Title': name } )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                     listitem=liz, isFolder=True)
    return ok


def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()


topparams = get_params()
topurl = None
topname = None
topmode = None
cookie = None
topthumbnail = None

try:
    topurl = urllib.unquote_plus(topparams['url'])
except:
    pass
try:
    topname = urllib.unquote_plus(topparams['name'])
except:
    pass
try:
    topmode = int(topparams['mode'])
except:
    pass

try:
    topthumbnail = urllib.unquote_plus(topparams['iconimage'])
except:
    pass

xbmc.log('Mode: ' + str(topmode))
xbmc.log('URL: ' + str(topurl))
xbmc.log('Name: ' + str(topname))

if topmode == None:
    xbmc.log('Generate Main Menu')
    CATEGORIES()
elif topmode == 1:
    xbmc.log('Indexing Videos')
    INDEX(topurl)
elif topmode == 2:
    xbmc.log('Indexing Collections')
    INDEXCOLLECT(topurl)
elif topmode == 4:
    xbmc.log('Play Video')
    PLAY(topurl,topthumbnail)
elif topmode == 5:
    xbmc.log('Category: Search')
    SEARCH(topurl)
elif topmode == 6:
    xbmc.log('Category: SEARCH_RESULTS')
    SEARCH_RESULTS(topurl)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
