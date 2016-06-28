# -*- coding: utf-8 -*-
import json
import os.path as path
import re
import urllib, urllib2
from operator import itemgetter
from kodiswift import Plugin, xbmc, ListItem

plugin = Plugin()
__addondir__ = xbmc.translatePath(plugin.addon.getAddonInfo('path'))
__resdir__ = path.join(__addondir__, 'resources')
__imgsearch__ = path.join(__resdir__, 'search.png')


def makeVideoItems(itemlist):
    """
    Takes a list of dict's returned from the API and looks for the specific fields to build XBMC ListItem for each item
    :param itemlist:
    :return: List of dict(Label, Label2, Icon, Thumb, Path) items created for each dict returned from the API
    """
    litems = []
    vitem = dict()
    vid = dict()
    item = dict()
    getsrc = itemgetter('src')
    try:
        for vitem in itemlist:
            assert isinstance(vitem, dict)
            if vitem.has_key('video'):
                vid = vitem.get('video')
            else:
                vid = vitem
            if vid is not None:
                assert isinstance(vid, dict)
                thumb = ''
                length = ''
                vidid = ''
                vurl = ''
                vtitle = ''
                pubdate = ''
                if vid.has_key('url'):
                    vurl = vid.get('url')
                elif vid.has_key('embed'):
                    vurl = vid.get('embed')
                if vid.has_key('default_thumb'):
                    thumb = vid.get('default_thumb')
                elif vid.has_key('thumbnail'):
                    thumb = vid.get('thumbnail')
                elif vid.has_key('thumb'):
                    thumb = vid.get('thumb')
                if vid.has_key('duration'): length = vid.get('duration')
                if vid.has_key('id'):
                    vidid = vid.get('id')
                elif vid.has_key('video_id'):
                    vidid = vid.get('video_id')
                else:
                    vidid = vurl.rsplit('-', 1)[0]
                if vid.has_key('title'):
                    vtitle = vid.get('title').title()
                elif vitem.has_key('title'):
                    vtitle = vitem.get('title').title()
                if vid.has_key('publish_date'):
                    pubdate = vid.get('publish_date')
                elif vitem.has_key('publish_date'):
                    pubdate = vitem.get('publish_date')
                vtitle = vtitle.replace('"', '')
                vtitle = vtitle.replace("'", '')
                lbl = vtitle
                lbl2 = "{0} {1}".format(pubdate, vidid)
                if length != "00:00:00" and length != '':
                    if length.find(':') == -1:
                        lenint = 0
                        seconds = int(length)
                        m, s = divmod(seconds, 60)
                        h, m = divmod(m, 60)
                        length = "%02d:%02d" % (m, s)
                        if h > 0: length = "%d:%02d:%02d" % (h, m, s)
                    else:
                        length = length.replace("00:", "").lstrip("0")
                    lbl += '|[COLOR green]{0}[/COLOR]'.format(length)
                vpath = plugin.url_for(play, title=vtitle, video=thumb, url=vurl)
                item = dict(label=lbl, label2=lbl2, icon=thumb, thumb=thumb, path=vpath, is_playable=True)
                item.setdefault(item.keys()[0])
                xbmc.log("Item {0} - {1} - {2} - {3}\n".format(vtitle, lbl2, thumb, vpath))
                litems.append(item)
            else:
                xbmc.log("Item has no video key: {0}\n".format(repr(vitem)))
    except:
        xbmc.log("ERROR MAKINGVIDEOITEMS: {0}\n".format(repr(vitem)))
    allitems = sorted(litems, key=lambda litems: litems['label'])
    xbmc.log("\nFINISHED MakeVidItems: #{0} {1}\n".format(len(allitems), repr(allitems)))
    return allitems


def parseVideosUrl(url):
    """
    Sends request to API and returns the JSON object as a List of Dicts which is parsed into XBMC ListItems by makeVideoItems
    :param url:
    :return: List(dict())
    """
    obj = dict()
    if url.find('xtube.com') != -1: obj = []
    resp = ''
    resp = urllib2.urlopen(url).read()
    obj = json.loads(unicode(resp).decode('ascii'))
    if url.find('xtube.com') != -1: return obj
    try:
        if len(obj.keys()) == 1:
            return obj.get(obj.keys()[0])
        elif obj.has_key('videos'):
            return obj.get('videos')
        else:
            return obj
    except:
        return obj


def readjson():
    dictallcats = dict()
    try:
        txt = file(path.join(__addondir__, 'spankwire.json'), 'r').read()
        dictallcats = json.loads(txt)  # dictallcats = json.JSONDecoder().decode(txt)
        if len(dictallcats.keys) == 1:
            return dictallcats.get(dictallcats.get(dictallcats.keys[0]))
        else:
            return dictallcats
    except:
        return []

def savejson(obj, filename):
    try:
        f = file(filename, 'w')
        txt = json.dump(obj, f)
        f.close()
    except:
        pass

def make_catitems(dictallcats):
    # SPANKWIRE specific code first version that created category listing for gay spankwire site.
    urlbase = "http://www.spankwire.com/api/HubTrafficApiCall?"
    caturl = urlbase + "data=getCategoriesList&output=json&segment=gay"
    catvidsurl = urlbase + "data=searchVideos&output=json&thumbsize=small&count=100&segment=gay&search=&tags=&category={0}"
    searchurl = urlbase + "data=searchVideos&output=json&thumbsize=small&count=100&segment=gay&search={0}&tags=&category="
    thumbcaturl = "http://cdn2.static.spankwire.com/images/category/Gay/{0}.jpg"
    listofcats = dictallcats.get(dictallcats.keys()[0])
    catvidslistitems = []
    for cat in listofcats:
        catname = cat.get('category')
        caturl = catvidsurl.format(catname)
        thumb = thumbcaturl.format(catname.replace(' ', '').replace('/', '').replace('&', ''))
        viditem = dict(label=catname, icon=thumb, thumb=thumb,
                       path=plugin.url_for(category, catname=catname, url=caturl))
        viditem.setdefault(viditem.keys()[0])
        catvidslistitems.append(viditem)
    return catvidslistitems

def catlist_tube8(isGay=True):
    urlapi = "http://api.tube8.com/api.php?action=getcategorieslist&output=json"
    turl = getAPIURLS('tube8').replace('search=&', 'search={0}&')
    turl = turl.replace('search=gay&', 'search={0}+gay&')
    resp = ''
    litems = []
    allitems = []
    catlist = []
    resp = urllib2.urlopen(urlapi).read()
    obj = json.loads(unicode(resp).decode('ascii'))
    try:
        if isGay:
            catlist = obj.get("gay")
        else:
            catlist = obj.get("straight")
        for catname in catlist:
            cname = catname.title()
            cimg = 'DefaultFolder.png'
            curl = turl.format(catname)
            cpath = plugin.url_for(site, sitename='tube8', section='index', url=curl)
            citem = dict(label=cname, icon=cimg, thumb=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return litems


def catlist_gaytube():
    # urlhtml = "http://www.gaytube.com/c/abc?m=azl"
    # html = urllib2.urlopen(urlhtml).read()
    # Above is to try and scrape category pictures so defaultfolder doesn't have to be used but can't get a Regex to work

    urlapi = "http://www.gaytube.com/api/webmasters/categories/"
    gturl = getAPIURLS('gaytube')
    resp = ''
    html = ''
    catlist = []
    litems = []
    allitems = []
    resp = urllib2.urlopen(urlapi).read()
    obj = json.loads(unicode(resp).decode('ascii'))
    catlist = obj.get('categories')
    try:
        for catname in catlist:
            assert isinstance(catname, dict)
            cname = catname.get('category')
            cimg = 'DefaultFolder.png'
            curl = gturl + urllib.quote_plus(cname)
            cpath = plugin.url_for(site, sitename='gaytube', section='index', url=curl)
            citem = dict(label=cname.title(), icon=cimg, thumb=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return litems

def rootItems():
    # Moved this code into the main plugin route '/' which originally had more code in it so I wanted to clean it up
    #  but in changing the plugin less code was left in the index '/' route so moved this code directly there
    litems = []
    igay = __imgsearch__.replace('search.', 'fgaytube.')
    iph = __imgsearch__.replace('search.', 'fpornhub.')
    irt = __imgsearch__.replace('search.', 'fredtube.')
    isw = __imgsearch__.replace('search.', 'fspankwire.')
    it8 = __imgsearch__.replace('search.', 'ftube8.')
    ixt = __imgsearch__.replace('search.', 'fxtube.')
    iyp = __imgsearch__.replace('search.', 'fyouporn.')
    pgay = plugin.url_for(siteroot, sitename="gaytube")
    pph = plugin.url_for(siteroot, sitename="pornhub")
    prt = plugin.url_for(siteroot, sitename="redtube")
    psw = plugin.url_for(siteroot, sitename="spankwire")
    pt8 = plugin.url_for(siteroot, sitename="tube8")
    pxt = plugin.url_for(siteroot, sitename="xtube")
    pyp = plugin.url_for(siteroot, sitename="youporn")
    if plugin.get_setting('dostr8'):
        # IF the STR8 Setting is turned on no point in including the GAYTUBE site as it's gay specific content only
        item = {'label': 'Gaytube', 'icon': igay, "thumb": igay, 'path': pgay}
        litems.append(item)
    item = {'label': 'Pornhub', 'icon': iph, "thumb": iph, 'path': pph}
    litems.append(item)
    item = {'label': 'Redtube', 'icon': irt, "thumb": irt, 'path': prt}
    litems.append(item)
    item = {'label': 'Spankwire', 'icon': isw, "thumb": isw, 'path': psw}
    litems.append(item)
    item = {'label': 'Tube8', 'icon': it8, "thumb": it8, 'path': pt8}
    litems.append(item)
    item = {'label': 'xtube', 'icon': ixt, "thumb": ixt, 'path': pxt}
    litems.append(item)
    item = {'label': 'YouPorn', 'icon': iyp, "thumb": iyp, 'path': pyp}
    litems.append(item)
    allitems = []
    for li in litems:
        li.setdefault(li.keys()[0])
        allitems.append(li)
    return sorted(allitems, key=lambda allitems: allitems['label'])


def getAPIURLS(sitename=None):
    """
    If a sitename is passes then just the URL to that sites API is returned if nothing is passed then a dictionary of Key=Sitename, Value=API URL is returned
    This function handles looking at the Plugin Settings to determine the Sorting/Ordering which defaults to NEWEST
    bugs still exist on ordering as dif API's use a dif word for other sortings but NEWEST works on all
    STR8 setting is checked and if it is enabled then the correct URL's are selected which doesn't specify segment=gay or gay in tags/search
    :param sitename:
    :return: URL of API for sitename specified or DICT(sitename: URL, sitename2: URL)
    """
    b = "http://www."
    siteapis = dict(gaytube=b+"gaytube.com/api/webmasters/search/?ordering=newest&period=alltime&thumbsize=preview&count=200&page=1&search=&tags[]=&category=",
        pornhub=b+"pornhub.com/webmasters/search?id=44bc40f3bc04f65b7a35&category=gay&ordering=newest&tags[]=&search=&page=1&thumbsize=medium",
        redtube="http://api.redtube.com/?data=redtube.Videos.searchVideos&output=json&thumbsize=medium&ordering=newest&page=1&search=&tags[]=gay",
        spankwire=b+"spankwire.com/api/HubTrafficApiCall?data=searchVideos&output=json&ordering=newest&page=1&segment=gay&count=100&search=&tags=gay&thumbsize=medium",
        tube8="http://api.tube8.com/api.php?action=searchVideos&output=json&ordering=newest&search=gay&thumbsize=all&page=1&orientation=gay",
        xtube=b+"xtube.com/webmaster/api.php?action=getVideosBySearchParams&tags=&ordering=newest&thumbsize=400x300&fields=title,tags,duration,thumbnail,url,embed,categories&search=gay&page=1&count=100",
        youporn=b+"youporn.com/api/webmasters/search?search=&page=1&ordering=newest&tags[]=gay&thumbsize=medium")
    urls_straight = dict(gaytube=b+"gaytube.com/api/webmasters/search/?ordering=newest&period=alltime&thumbsize=all&count=100&page=1&search=&tags[]=",
        pornhub=b+"pornhub.com/webmasters/search?id=44bc40f3bc04f65b7a35&category=&ordering=newest&tags[]=&search=&page=1&thumbsize=medium",
        redtube="http://api.redtube.com/?data=redtube.Videos.searchVideos&output=json&thumbsize=medium&ordering=newest&page=1&search=&tags[]=",
        spankwire=b +"spankwire.com/api/HubTrafficApiCall?data=searchVideos&output=json&ordering=newest&page=1&segment=straight&count=100&search=&tags=&thumbsize=all",
        tube8="http://api.tube8.com/api.php?action=searchVideos&output=json&ordering=newest&search=&thumbsize=big&page=1&orientation=straight",
        xtube=b+"xtube.com/webmaster/api.php?action=getVideosBySearchParams&tags=&ordering=newest&thumbsize=400x300&fields=title,tags,duration,thumbnail,url,embed,categories&search=&page=1&count=100",
        youporn=b+"youporn.com/api/webmasters/search?search=&page=1&ordering=newest&tags[]=&thumbsize=medium")
    DOSTR8 = plugin.get_setting(key='dostr8')
    ORDERBY = plugin.get_setting(key='sortby')

    if DOSTR8 == True or DOSTR8 == 'true':
        siteapis = urls_straight
    if ORDERBY != 'newest':
        urlstemp = siteapis
        tempdict = dict()
        for k, v in urlstemp.iteritems():
            url = v.replace('ordering=newest', 'ordering={0}'.format(ORDERBY))
            tempdict.update(k=url)
        siteapis = tempdict

    if sitename is None:
        return siteapis
    else:
        if siteapis.has_key(sitename):
            return siteapis.get(sitename)
        else:
            return siteapis


@plugin.route('/')
def index():
    """
    Index for plugin this just builds the main items for the site's linked to the SITEROOT destination
    :return: List of ListItems for Index of all sites
    """
    litems = []
    # litems = rootItems()
    igay = __imgsearch__.replace('search.', 'fgaytube.')
    iph = __imgsearch__.replace('search.', 'fpornhub.')
    irt = __imgsearch__.replace('search.', 'fredtube.')
    isw = __imgsearch__.replace('search.', 'fspankwire.')
    it8 = __imgsearch__.replace('search.', 'ftube8.')
    ixt = __imgsearch__.replace('search.', 'fxtube.')
    iyp = __imgsearch__.replace('search.', 'fyouporn.')
    pgay = plugin.url_for(siteroot, sitename="gaytube")
    pph = plugin.url_for(siteroot, sitename="pornhub")
    prt = plugin.url_for(siteroot, sitename="redtube")
    psw = plugin.url_for(siteroot, sitename="spankwire")
    pt8 = plugin.url_for(siteroot, sitename="tube8")
    pxt = plugin.url_for(siteroot, sitename="xtube")
    pyp = plugin.url_for(siteroot, sitename="youporn")

    DOSTR8 = plugin.get_setting(key='dostr8')
    if not (DOSTR8 == True or DOSTR8 == 'true'):
        # IF the STR8 Setting is turned on no point in including the GAYTUBE site as it's gay specific content only
        item = {'label': 'Gaytube', 'icon': igay, 'thumb': igay, 'path': pgay}
        litems.append(item)
    item = {'label': 'Pornhub', 'icon': iph,'thumb': iph, 'path': pph}
    litems.append(item)
    item = {'label': 'Redtube', 'icon': irt,'thumb': irt, 'path': prt}
    litems.append(item)
    item = {'label': 'Spankwire', 'icon': isw, 'thumb': isw, 'path': psw}
    litems.append(item)
    item = {'label': 'Tube8', 'icon': it8, 'thumb': it8, 'path': pt8}
    litems.append(item)
    item = {'label': 'Xtube', 'icon': ixt, 'thumb': ixt, 'path': pxt}
    litems.append(item)
    item = {'label': 'YouPorn', 'icon': iyp, 'thumb': iyp, 'path': pyp}
    litems.append(item)
    allitems = []
    for li in litems:
        li.setdefault(li.keys()[0])
        allitems.append(li)
    litems = sorted(allitems, key=lambda allitems: allitems['label'])
    return litems


@plugin.route('/siteroot/<sitename>/')
def siteroot(sitename):
    """
    Calls the site() function but helps by figuring out base URL to pass one special instance exists with site Spankwire
    I have setup category and thumbnails but it's the only site and only on the GAY segment. I hope to expand
    the functionality to add a category section to the sites and bring up the sites category list for GAY/STR8 as well
    as including a global attempt at category similar to the global search where a category will run the API's search
    using the tags=Category where possible or just search=Category if a tags criteria is not in the API. Until then
    I have this static category listing for GAY content on spankwire which I saved as a JSON file. The API exposes
    Category's for most sites but doesn't include Thumbnails and sometimes doesn't expose dif category's for GAY/STR8
    so to make Thumbnails for Gay content I scraped the webpage and just found it easier to statically set these up.
    :param sitename:
    :return: ListItems for the Index of the site specified
    """
    litems = []
    siteurl = getAPIURLS(sitename=sitename)
    DOSTR8 = plugin.get_setting(key='dostr8')
    if sitename.lower() == "spankwire" and not (DOSTR8 == True or DOSTR8 == 'true'):
        isw = __imgsearch__.replace('search.', 'fspankwire.')
        item = {'label': 'Spankwire Gay Categories',
                'path': plugin.url_for(site, sitename='spankwire', section='category', url=siteurl), 'icon': isw,
                'thumb': isw}
        item.setdefault(item.keys()[0])
        litems = [item]
        litems.extend(site(sitename, 'index', siteurl))
    elif sitename.lower() == "gaytube":
        igt = __imgsearch__.replace('search.', 'fgaytube.')
        item = {'label': 'GayTube Categories',
                'path': plugin.url_for(site, sitename='gaytube', section='category', url=siteurl), 'icon': igt,
                'thumb': igt}
        item.setdefault(item.keys()[0])
        litems = [item]
        litems.extend(site(sitename, 'index', siteurl))
    elif sitename.lower() == "tube8":
        igt = __imgsearch__.replace('search.', 'ftube8.')
        item = {'label': 'Tube8 Categories',
                'path': plugin.url_for(site, sitename='tube8', section='category', url=siteurl), 'icon': igt,
                'thumb': igt}
        item.setdefault(item.keys()[0])
        litems = [item]
        litems.extend(site(sitename, 'index', siteurl))
    else:
        litems = site(sitename, 'index', siteurl)
    return litems


@plugin.route('/site/<sitename>/<section>/<url>/')
def site(sitename, section, url):
    """
    Main working function for the addon and handles Site specific calls to Search a site, Next Page, and Index.
    Index and Search sections call back into this section for Next Page support
    A shortcut helper SITEROOT simply calls this function for each site but looks up the correct URL to pass to section=Index
    :param sitename: Name of site to perform section actions on
    :param section: Index, Search, Next
    :param url: API URL for the section
    :return: Listitems for results plus a Search Site Item and Next Page Item
    """
    # siteapiurls = getAPIURLS()
    # siteurl = siteapiurls.get(sitename)
    litems = []
    itemslist = []
    DOSTR8 = plugin.get_setting(key='dostr8')
    __imgnext__ = __imgsearch__.replace('search.png', 'next.png')
    siteurl = getAPIURLS(sitename=sitename)
    if siteurl.find('search=gay&') != -1:
        surl = siteurl.replace('search=gay&', 'search={0}+gay&')
    else:
        surl = siteurl.replace('search=', 'search={0}')
    itemsearch = {'label': 'Search {0}'.format(sitename.title()),
                  'path': plugin.url_for(site, sitename=sitename, section='search', url=surl), 'icon': __imgsearch__,
                  'thumb': __imgsearch__}
    itemsearch.setdefault(itemsearch.keys()[0])
    pagenum = 2
    if url.find('page=') != -1:
        pagestr = str(url.split('page=', 1)[1]).split('&', 1)[0]
        if pagestr is not None:
            pagenum = int(pagestr) + 1
        else:
            pagenum = 2
    pagenumcur = pagenum - 1
    if url.find('page=1') != -1:
        nurl = url.replace('page=1&', 'page=2&')
    elif url.find('page=') != -1:
        nurl = url.replace('page={0}&'.format(pagenumcur), 'page={0}&'.format(pagenum))
    else:
        nurl = url + '&page={0}'.format(pagenum)
    itemnext = {'label': 'Next --> {0}'.format(pagenum),
                'path': plugin.url_for(site, sitename=sitename, section='next', url=nurl), 'icon': __imgnext__,
                'thumb': __imgnext__}
    itemnext.setdefault(itemnext.keys()[0])

    if section.lower() == "index":
        # Index was called so get the first page of a specific site and return items with a Search and Next added
        vitems = list()
        itemslist = parseVideosUrl(url)
        litems = makeVideoItems(itemslist)
        try:
            itemslist = sorted(litems, key=lambda litems: litems['label'])
        except:
            xbmc.log('\nERROR SORTING ITEMS #{0}'.format(len(litems)))
            itemslist = litems
        itemslist.insert(0, itemsearch)
        itemslist.append(itemnext)
        litems = itemslist
    elif section.lower() == "next":
        # Provides support for viewing Next set of results/page and accessed from the itemnext ListItem added to Index/Search
        vitems = list()
        itemslist = parseVideosUrl(url)
        litems = makeVideoItems(itemslist)
        try:
            itemslist = sorted(litems, key=lambda litems: litems['label'])
        except:
            xbmc.log('\nERROR SORTING ITEMS #{0}'.format(len(litems)))
            itemslist = litems
        itemslist.insert(0, itemsearch)
        itemslist.append(itemnext)
        litems = itemslist
    elif section.lower() == "category":
        if sitename.lower() == 'spankwire':
            txt = file(path.join(__addondir__, 'spankwire.json')).read()
            allitems = json.loads(txt)
            itemlist = allitems.get(allitems.keys()[0])
            allitems = sorted(itemlist, key=lambda itemlist: itemlist['label'])
            for li in allitems:
                assert isinstance(li, dict)
                # catpath = plugin.url_for(category, catname=li.get('label'), url=li.get('path'))
                catpath = plugin.url_for(site, sitename='spankwire', section='index', url=li.get('path'))
                li.update(path=catpath)
                li.setdefault(li.keys()[0])
                litems.append(li)
        elif sitename.lower() == 'gaytube':
            litems = catlist_gaytube()
        elif sitename.lower() == 'tube8':
            if not (DOSTR8 == True or DOSTR8 == 'true'):
                litems = catlist_tube8(isGay=True)
            else:
                litems = catlist_tube8(isGay=False)
    elif section.lower() == "search":
        # Perform a search of the specific site and return results and a next page item - NOT a global multisite search
        searchtxt = ''
        try:
            searchtxt = plugin.get_setting('lastsearch')
        except:
            searchtxt = ''
        searchtxt = plugin.keyboard(searchtxt, 'Search {0}'.format(sitename.title()), False)
        searchquery = searchtxt.replace(' ', '+')
        plugin.set_setting(key='lastsearch', val=searchtxt)
        surl = surl.format(searchquery)
        itemslist = parseVideosUrl(surl)
        litems = makeVideoItems(itemslist)
        try:
            itemslist = sorted(litems, key=lambda litems: litems['label'])
        except:
            xbmc.log('\nERROR SORTING ITEMS #{0}'.format(len(litems)))
            itemslist = litems
        itemslist.insert(0, itemsearch)
        nurl = surl.replace('page=1&', 'page=2&')
        itemnext = {'label': 'Next {0} --> {1}'.format(searchtxt, pagenum), 'path': plugin.url_for(site, sitename=sitename, section='next', url=nurl),
                    'icon': __imgnext__, 'thumb': __imgnext__}
        itemnext.setdefault(itemnext.keys()[0])
        itemslist.append(itemnext)
        litems = itemslist
    else:
        itemslist = parseVideosUrl(url)
        litems = makeVideoItems(itemslist)
        litems.append(itemnext)
    return litems


@plugin.route('/play/<title>/<video>/<url>/')
def play(title, video, url):
    """
    Play attempts to scrape the video's page and find the actual video file to play. This is still buggy but seems to work on
    a lot of the sites but not all the time so any help on this function working better would be appreciated. I pass in the
    title of the movie and the video tags the Thumbnail which I use to create a proper ListItem with the scrapped MP4 url
    :param title: Video Title to play passed to XBMC in a new ListItem object with resolved URL of video scraped from url
    :param video: Thumbnail URL of the video used as the icon and thumbnail for ListItem to play
    :param url: URL of the embed/video page to scrape for the real playable video file
    :return: ListItem of video with path = scraped url of the MP4/Video file hopefully
    """
    resolved = None
    mediaurl = None
    vidhtml = urllib2.urlopen(url).read()
    vidurl = ''
    vli = None
    try:
        matches = re.compile('(http://[^"<]+?.mp4[^"<]+?)"', re.I + re.M + re.S + re.U).findall(vidhtml)[0]
        if matches is not None:
            vidurl = matches
            xbmc.log("MATCH MP4 = {0}".format(vidurl))
            vli = ListItem(label=title, label2=url, icon=video, thumbnail=video, path=vidurl)
            vli.playable = True
        else:
            matches = re.compile('(http://[^"<]+?.flv[^"<]+?)"', re.I + re.M + re.S + re.U).findall(vidhtml)[0]
            if matches is not None:
                vidurl = matches
                xbmc.log("MATCH FLV = {0}".format(vidurl))
                vli = ListItem(label=title, label2=url, icon=video, thumbnail=video, path=vidurl)
                vli.playable = True
    except:
        pass
    try:
        if vli is not None:
            plugin.set_resolved_url(vli)
            plugin.play_video(vli)
            # return plugin.play_video(vli)
    except:
        pass


@plugin.route('/category/<catname>/<url>/')
def category(catname, url):
    """
    Old Category handler only specific to Spankwire Gay at this time as Category's are not supported for all sites yet
    :param catname:
    :param url:
    :return:
    """
    caturl = "http://www.spankwire.com/api/HubTrafficApiCall?data=getCategoriesList&output=json&segment=gay"
    thumbcaturl = "http://cdn2.static.spankwire.com/images/category/Gay/{0}.jpg"
    if url is None: url = caturl.format(catname)
    itemslist = parseVideosUrl(url)
    litems = makeVideoItems(itemslist)
    return litems

@plugin.route('/search/')
def search():
    """
    Search currently searches just spankwire but want to expand this search over the search performed in site() to run each
    of those searches for every site and return all results in this one section for now i have removed the route to this
    search until I can finish the global search.
    """
    urlbase = "http://www.spankwire.com/api/HubTrafficApiCall?"
    caturl = urlbase + "data=getCategoriesList&output=json&segment=gay"
    catvidsurl = urlbase + "data=searchVideos&output=json&thumbsize=small&count=100&segment=gay&search=&tags=&category={0}"
    searchurl = urlbase + "data=searchVideos&output=json&thumbsize=small&count=100&segment=gay&search={0}&tags=&category="
    thumbcaturl = "http://cdn2.static.spankwire.com/images/category/Gay/{0}.jpg"
    searchtxt = ''
    searchtxt = plugin.get_setting('lastsearch')
    searchtxt = plugin.keyboard(searchtxt, 'Search Spankwire', False)
    searchquery = searchtxt.replace(' ', '+')
    plugin.set_setting(key='lastsearch', val=searchtxt)
    url = searchurl.format(searchquery)
    itemslist = parseVideosUrl(url)
    viditems = makeVideoItems(itemslist)
    return viditems


if __name__ == '__main__':
    plugin.run()
    viewmode = int(plugin.get_setting('viewmode'))
    if viewmode is None: viewmode = 500
    plugin.set_view_mode(viewmode)
