#!/usr/bin/python
#Code Heavily modified from  Demo by TV DASH - by You 2008.
#
# Written by Ksosez with help from anarchintosh
# Released under GPL(v2)

import urllib, urllib2, htmllib
import re, string
import os
import sys
import sesame
import xbmcplugin, xbmcaddon, xbmcgui, xbmc

#addon name
__addonname__ = 'plugin.video.fantasticc'

#get path the default.py is in.
__addonpath__ = os.getcwd()

#datapath
__datapath__ = xbmc.translatePath('special://profile/addon_data/'+__addonname__)

#append lib directory
sys.path.append( os.path.join( __addonpath__, 'resources', 'lib' ) )

#import from lib directory
import weblogin
import gethtml

#import img_merge

pluginhandle = int(sys.argv[1])

# example of how to get path to an image
default_image = os.path.join(__addonpath__, 'resources', 'images',
                             'provocative_logo.png')

# string to simplify urls
main_url = 'http://fantasti.cc/'
# fantasti.cc's ip
fip = 'http://77.247.181.97/'

# 3rd Party video Sites that are currently supported are listed below

SUPPORTEDSITES = ['deviantclip', 'empflix', 'pornhub', 'redtube', 'tnaflix',
                  'tube8', 'xhamster', 'xvideos', 'you_porn']



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

    mode = 2
    addDir('Collections Popular Today',
           main_url+'videos/collections/popular/today/', mode, default_image)
    addDir('Collections Popular Last 7 Days',
           main_url+'videos/collections/popular/7days/', mode, default_image)
    addDir('Collections Popular Last Month',
           main_url+'videos/collections/popular/31days/', mode, default_image)
    addDir('Collections Popular All Time',
           main_url+'videos/collections/popular/all_time/', mode, default_image)

    # didn't need to pass search a url. so i was lazy and passed it the
    # main_url as a dummy
    addDir('Search', main_url, 5, default_image)

    print pluginhandle
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
            search = re.sub('  ', '+', search) # this one is just in case the
                                               # user accidently enters two
                                               # spaces
            search = re.sub(' ', '+', search)

            # create the search url
            search_url = main_url + 'search/' + search + '/videos/'
            print 'SEARCH:', search_url

            # get the source code of first page
            first_page = get_html(search_url)

            # do a search to see if no results found
            no_results_found = re.search('did not match any content.',
                                         first_page)

            # if there are results on page...
            if no_results_found is None:

                # scrape to get the number of all the results pages (this is
                # listed on the first page)
                match = re.compile('/videos/page_(.+?)">').findall(first_page)
                print 'Number of pages:', match

                # if there weren't any multiple pages of search results
                if not match:
                    # ...directly call the results scraper for the first page
                    # to add the directories.
                    SEARCH_RESULTS(url=False, html=first_page)

                # if there were any multiple pages of search results
                if match:

                    # convert the list of strings produced by re.compile to a
                    # list of integers, so we can use them for calculations
                    match = [int(result) for result in match]

                    # get the highest results page number, to get the total
                    # number of results pages.
                    # this gets the highest integer in the list of integers
                    total_pages = max(match)

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

                        # make the page url
                        url = search_url + 'page_' + thenumber

                        # add the results page as a directory
                        addDir(name, url, 6, default_image)



def SEARCH_RESULTS(url, html=False):
    # this function scrapes the search results pages
    # accepts page source code (html) for any searches where there is only one
    # page of results

    if html is False:
        html = get_html(url)
    match = re.compile('<a href="(.+?)" onclick="document.cookie = \'ii=1;'
                       'path=/\';"  class="xxx" target="_blank"><img '
                       'alt="(.+?)"   src="(.+?)"').findall(html)
    for gurl, name, thumbnail in match:
        for each in SUPPORTEDSITES:
            if each in gurl:
                realurl = 'http://fantasti.cc%s' % gurl
                mode = 4
                addLink(name, realurl, mode, thumbnail)
            else:
                pass



def INDEX(url):
    html = get_html(url)
    if 'collection' in url: # Collections
        match = re.compile('<a href=(.+?)" title="(.+?)">\s*<img src="(.+?)"'
                           ' border="0" alt="(.+?)"  width="100" height="100"'
                           ' class="collection_image" />').findall(html)
        for gurl, name, thumbnail, junk in match:
            vid_id = string.split(gurl, '=')[2][:-5]
            realurl = 'http://fantasti.cc/video.php?id=%s' % vid_id
            mode = 4
            print realurl
            addLink(name, realurl, mode, thumbnail)
        html = get_html(url)
        match = re.compile('\(\'(.+?)\', ([0-9]*),\'(.+?)\', \'(.+?)\'\)'
                           ';return false;" href="#">next').findall(html)
        if len(match) >= 1:
            fixedNext = None
            for next_match in match:
                print next_match
                mode = 1
                page = next_match[0][-1]
                vid_id = next_match[1]
                fixedNext = 'http://fantasti.cc/ajax/pager.php?page=%s&pid=%s'\
                            '&div=collection_%s&uid=14657' % \
                            (page, vid_id, vid_id)
                print fixedNext
            addDir('Next Page', fixedNext, mode, default_image)
        xbmcplugin.endOfDirectory(pluginhandle)

    else:
        match = re.compile('<a href="([^"]+)"><img src="(.+?)"'
                           ' alt="(.+?)" border="0" >').findall(html)
        for gurl, thumbnail, name in match:
            for each in SUPPORTEDSITES:
                if each in gurl:
                    realurl = 'http://fantasti.cc%s' % gurl
                    mode = 4
                    addLink(name, realurl, mode, thumbnail)
                else:
                    pass
        html = get_html(url)
        match = re.compile('<a href="(.+?)">next &gt;&gt;</a></span></div>'
                          ).findall(html)
        for next_match in match:
            mode = 1
            next_match = string.split(next_match, '"')[-1]
            fixedNext = 'http://fantasti.cc%s' % next_match
            addDir('Next Page', fixedNext, mode, default_image)
        xbmcplugin.endOfDirectory(pluginhandle)

def INDEXCOLLECT(url):   # Index Collections Pages
    print 'URL Loading: %s' % url
    html = get_html(url)
    match = re.compile('<div style="font-size:24px; line-height:30px; ">'
                       '<a href="(.+?)">(.+?)</a>(.+?)<span id="chunk.+?\>'
                       '(.+?)</div>', re.DOTALL).findall(html)
    for gurl, name, chtml, description in match:
        print name
        realurl = 'http://fantasti.cc%s' % gurl
        name = unescape(name)
        mode = 1

        #scrape number of vids
        num_of_vids = (re.compile('line-height:100\%;">(.+?) videos<br>',
                       re.DOTALL).findall(chtml))[0]
        #trim whitespace from beginning of string
        num_of_vids = re.sub('^[ \t\r\n]+', '', num_of_vids)

        # do some cool stuff to get the images and join them.
        icons = re.compile('<img src="(.+?)"').findall(chtml)

        addDir(name+' *'+num_of_vids+' vids*', realurl, mode, icons[0])

    match = re.compile('<a href="(.+?)">next &gt;&gt;</a></span></div>'
                      ).findall(html)
    for next_match in match:
        print 'Next: %s' % next_match
        mode = 2
        next_match = string.split(next_match, '"')[-1]
        fixedNext = 'http://fantasti.cc%s' % next_match
        print 'FixedNext: %s' % fixedNext
        addDir('Next Page', fixedNext, mode, default_image)

    xbmcplugin.endOfDirectory(pluginhandle)

def PLAY(url):
    print 'Play URL:%s' % url
    if 'id=' in url:
        realurl = GET_LINK(url, 1)
    else:
        realurl = GET_LINK(url, 0)
    print 'Real url:%s' % realurl
    if not realurl:
        Notify('Failure', 'Try another video', '4000', default_image)

    item = xbmcgui.ListItem(path=realurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def GET_LINK(url, collections):
# Get the real video link and feed it into XBMC
    print 'GET_LINK URL: %s' % url
    html = get_html(url)
    if collections == 1:   # Make sure we get a url we can parse
        match = re.compile('<link rel="canonical" href="(.+?)" />'
                          ).findall(html)
        for each in match:
            url = each

    if 'xvideos' in url:
        match = re.compile('(http://www.xvideos.com/.+?)"').findall(html)
        html = get_html(match[0])
        match = re.compile('flv_url=(.+?)&amp').findall(html)
        fetchurl = urllib.unquote(match[0])
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'pornhub' in url:
        match = re.compile('href="([^"]+viewkey[^"]+)"').findall(html)
        html = get_html(match[0])
        match = re.compile('"video_url":"([^"]+)"').findall(html)
        fetchurl = urllib2.unquote(match[0])
        match = re.compile('"video_title":"([^"]+)"').findall(html)
        title = urllib.unquote_plus(match[0])
        fetchurl = sesame.decrypt(fetchurl, title, 256)
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'empflix' in url:
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
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'tnaflix' in url:
        match = re.compile('<param name="FlashVars" value="(.+?)"/>'
                          ).findall(html)
        for gurl in match:
            print 'gurl %s' % gurl
            purl = string.split(gurl, '?')[1]
            print purl
            urlget2 = 'http://www.tnaflix.com/embedding_player/' \
                      'embedding_feed.php?' + purl
            print urlget2
        html = get_html(urlget2)
        match = re.compile('<file>(.+?)</file>').findall(html)
        for each in match:
            fetchurl = each
            print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'xhamster' in url:
        match = re.compile('xhamster.com/movies/(.+?)/').findall(html)
        html = get_html('http://xhamster.com/xembed.php?video=%s' % match[0])
        match = re.compile('srv=(.+?)&image').findall(html)
        fetchurl = match[0].replace('&file', '/key')
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'deviantclip' in url:
        match = re.compile('<a style="color:#BBB;" href="(.+?)" target="_blank"'
                           ' rel="nofollow">deviantclip</a>').findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('"file":"(.+?)"').findall(html)
        for each in match:
            fetchurl = urllib.unquote(each)
        return fetchurl
    elif 'redtube' in url:
        match = re.compile('(http://www.redtube.com/.+?)"').findall(html)
        html = get_html(match[0])
        match = re.compile('flv_h264_url=(.+?)"').findall(html)
        fetchurl = urllib.unquote(match[0])
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'tube8' in url:
        match = re.compile('href="(http://www.tube8.com/[^"]+)"').findall(html)
        html = get_html(match[0])
        match = re.compile('"video_url":"([^"]+)"').findall(html)
        fetchurl = urllib2.unquote(match[0])
        match = re.compile('"video_title":"([^"]+)"').findall(html)
        title = urllib2.unquote(match[0])
        fetchurl = sesame.decrypt(fetchurl, title, 256)
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    elif 'you_porn' in url:
        match = re.compile('href="(http://www.youporn.com/watch/[^"]+)"'
                          ).findall(html)
        for gurl in match:
            urlget2 = gurl
        html = get_html(urlget2)
        match = re.compile('</span><a href="(.+?mp4.+?)">.+?iPad').findall(html)
        for each in match:
            fetchurl = each.replace('&amp;', '&')
        print 'fetchurl: %s' % fetchurl
        return fetchurl
    else:
        #Clipnabber
        #get the name of the resource
        r = re.compile('permalink/(.*?)/').findall(url)[0]
        print 'Unknown source (%s). Trying clipnabber' % r

        #get the link
        try:
            gurl = re.compile('<a[^>]+href="(.*?)"[^>]*>%s</a>' % r
                             ).findall(html)[0]
            kid = re.compile('id="Math">(\d+)'
                            ).findall(get_html('http://clipnabber.com/mini.php'))[0]
            html = get_html('http://clipnabber.com/gethint.php?mode=1&sid=%s&url=%s'
                            % (kid, urllib.quote(gurl)))
            fetchurl = re.compile("<a href='(.*?)'").findall(html)[0]
            print 'Fetchurl: %s' % fetchurl
        except:
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
        + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage='DefaultVideo.png',
                           thumbnailImage=iconimage)
    liz.setInfo( type='Video', infoLabels={ 'Title': name } )
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

print 'Mode: '+str(topmode)
print 'URL: '+str(topurl)
print 'Name: '+str(topname)

if topmode == None:
    print 'Generate Main Menu'
    CATEGORIES()
elif topmode == 1:
    print 'Indexing Videos'
    INDEX(topurl)
elif topmode == 2:
    print 'Indexing Collections'
    INDEXCOLLECT(topurl)
elif topmode == 4:
    print 'Play Video'
    PLAY(topurl)
elif topmode == 5:
    print 'Category: Search'
    SEARCH(topurl)

elif topmode == 6:
    print 'Category: SEARCH_RESULTS'
    SEARCH_RESULTS(topurl)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
