#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, os.path, time, tempfile, threading
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import urllib, urllib2, urlparse
from urllib import quote_plus, unquote_plus, basejoin
from urllib2 import Request, urlopen

def get_file(url):
    log = xbmc.log
    clean_url = xbmc.translatePath(urllib.unquote(url)).replace("image://", "")
    if clean_url.endswith("/"):
        clean_url = clean_url[:-1]
    cached_thumb = xbmc.getCacheThumbName(clean_url)
    vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cached_thumb[0], cached_thumb)
    cache_file_jpg = os.path.join("special://profile/Thumbnails/", cached_thumb[0], cached_thumb[:-4] + ".jpg").replace(
        "\\", "/")
    cache_file_png = cache_file_jpg[:-4] + ".png"
    if xbmcvfs.exists(cache_file_jpg):
        log("cache_file_jpg Image: " + url + "-->" + cache_file_jpg)
        return xbmc.translatePath(cache_file_jpg)
    elif xbmcvfs.exists(cache_file_png):
        log("cache_file_png Image: " + url + "-->" + cache_file_png)
        return cache_file_png
    elif xbmcvfs.exists(vid_cache_file):
        log("vid_cache_file Image: " + url + "-->" + vid_cache_file)
        return vid_cache_file
    try:
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request, timeout=3)
        data = response.read()
        response.close()
        log('image downloaded: ' + url)
    except:
        log('image download failed: ' + url)
        return ""
    if not data:
        return ""
    if url.endswith(".png"):
        image = cache_file_png
    else:
        image = cache_file_jpg
    try:
        with open(xbmc.translatePath(image), "wb") as f:
            f.write(data)
        return xbmc.translatePath(image)
    except:
        log('failed to save image ' + url)
        return ""

class StopDownloading(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class GetFileThread(threading.Thread):
    def __init__(self, url):
        self.url = url
        threading.Thread.__init__(self)

    def run(self):
        self.file = get_file(self.url)

class FunctionThread(threading.Thread):
    def __init__(self, function=None, param=None):
        # super(FunctionThread, self).__init__(self)
        threading.Thread.__init__(self, target=self.function, name=self.function.__name__)
        self.function = function
        self.param = param
        self.setName(self.function.__name__)
        xbmc.log("init " + self.function.__name__)

    def run(self):
        self.listitems = self.function(self.param)
        return True

class xbmcUtils(object):
    def __init__(self, addonid='plugin.video.motherless', pluginhandle=None, urlposter=''):
        self.PHost = urlposter
        self.BHost = str(self.PHost.replace('http', '').lstrip('s').replace('://', '').split('/', 1)[0])
        if pluginhandle is None:
            self.handle = int(sys.argv[1])
        else:
            self.handle = pluginhandle
        self.std_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',}
        self.req = Request(url=self.BHost, headers=self.std_headers)
        if addonid != 'plugin.video.':
            self.addon = xbmcaddon.Addon(id=str(addonid))
            self.addonid = str(addonid)
        else:
            self.addon = xbmcaddon.Addon()
            self.addonid = str(self.addon.getAddonInfo('id'))
        self.plugDir = xbmc.translatePath(self.addon.getAddonInfo('path').decode('utf-8'))
        self.resDir = os.path.join(xbmc.translatePath(self.addon.getAddonInfo('path').decode('utf-8')), "resources/")
        self.imgDir = os.path.join(self.resDir, "images/")
        self.profile = xbmc.translatePath(self.addon.getAddonInfo('profile').decode('utf-8'))

    def url_quote(self, input_string):
        """
        get url-quoted string
        """
        try:
            return urllib.quote_plus(input_string.encode('utf8', 'ignore'))
        except:
            return urllib.quote_plus(unicode(input_string, "utf-8").encode("utf-8"))

    def getUrl(self, url):
        assert isinstance(self.req, Request)
        self.req.url = url #urllib2.toBytes(url)
        response = urlopen(self.req)
        link = response.read()
        response.close()
        return self.removeNonAscii(link)

    def removeNonAscii(self, s):
        return "".join(filter(lambda x: ord(x) < 128, s))

    def addLink(self, videourl, name, iconimage='DefaultVideo.png', fanart=None, plot='', genre='', duration='',
                mode='5', returnItem=False):
        try:
            name = name.encode('utf-8')
        except:
            pass
        namesafe = quote_plus(name)
        parameters = dict(url=videourl, mode=str(mode), name=namesafe)
        pathurl = sys.argv[0] + '?' + urllib.urlencode(parameters)
        # '.format(self.addonid, videourl, str(mode), namesafe)
        infolbl = {"Title": name, "Plot": plot, "Genre": genre, "Duration": duration}
        liz = xbmcgui.ListItem(label=name, label2=plot, iconImage=iconimage, thumbnailImage=iconimage, path=pathurl)
        ctxdl = "XBMC.RunPlugin('plugin://{0}/?url={1}&name={2}&mode=download')".format(self.addonid, videourl,
                                                                                        namesafe)
        ctx = [(('[COLOR red]Download[/COLOR] {0}'.format(namesafe)), (ctxdl))]  # ,('Download and Play', dlaction2))]
        liz.addContextMenuItems(items=ctx, replaceItems=False)
        returl = pathurl
        notVid = True
        if str(videourl).find(".mp4") != -1:
            liz.setMimeType("video/mp4")
            liz.setProperty('IsPlayable', 'true')
            liz.setPath(videourl)
            returl = videourl
            notVid = False
        liz.setInfo(type="Video", infoLabels=infolbl)
        if fanart is not None: liz.setArt(dict(fanart=fanart))
        if returnItem:
            return liz
        else:
            return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=pathurl, listitem=liz, isFolder=notVid)

    def addListItem(self, liz, pathurl):
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=pathurl, listitem=liz, totalItems=1)

    def createListitems(self, data=None, preload_images=0):
        INT_INFOLABELS = ["year", "episode", "season", "top250", "tracknumber", "playcount", "overlay"]
        FLOAT_INFOLABELS = ["rating"]
        STRING_INFOLABELS = ["genre", "director", "mpaa", "plot", "plotoutline", "title", "originaltitle",
                             "sorttitle", "duration", "studio", "tagline", "writer", "tvshowtitle", "premiered",
                             "status", "code", "aired", "credits", "lastplayed", "album", "votes", "trailer",
                             "dateadded"]
        if not data:
            return []
        itemlist = []
        threads = []
        image_requests = []
        for (count, result) in enumerate(data):
            listitem = xbmcgui.ListItem('%s' % (str(count)))
            for (key, value) in result.iteritems():
                if not value:
                    continue
                value = unicode(value)
                if count < preload_images:
                    if value.startswith("http://") and (value.endswith(".jpg") or value.endswith(".png")):
                        if value not in image_requests:
                            thread = GetFileThread(value)
                            threads += [thread]
                            thread.start()
                            image_requests.append(value)
                if key.lower() in ["name", "label"]:
                    listitem.setLabel(value)
                elif key.lower() in ["label2"]:
                    listitem.setLabel2(value)
                elif key.lower() in ["title"]:
                    listitem.setLabel(value)
                    listitem.setInfo('video', {key.lower(): value})
                elif key.lower() in ["thumb"]:
                    listitem.setThumbnailImage(value)
                    listitem.setArt({key.lower(): value})
                elif key.lower() in ["icon"]:
                    listitem.setIconImage(value)
                    listitem.setArt({key.lower(): value})
                elif key.lower() in ["path"]:
                    listitem.setPath(path=value)
                elif key.lower() in ["link"]:
                    listitem.setPath(path=value)
                    strid = str(value.rpartition('/')[2])
                    listitem.setThumbnailImage(self.PHost.format(strid))
                    listitem.setIconImage(self.PHost.format(strid))
                elif key.lower() in ["poster", "banner", "fanart", "clearart", "clearlogo", "landscape",
                                     "discart", "characterart", "tvshow.fanart", "tvshow.poster",
                                     "tvshow.banner", "tvshow.clearart", "tvshow.characterart"]:
                    listitem.setArt({key.lower(): value})
                elif key.lower() in INT_INFOLABELS:
                    try:
                        listitem.setInfo('video', {key.lower(): int(value)})
                    except:
                        pass
                elif key.lower() in STRING_INFOLABELS:
                    listitem.setInfo('video', {key.lower(): value})
                elif key.lower() in FLOAT_INFOLABELS:
                    try:
                        listitem.setInfo('video', {key.lower(): "%1.1f" % float(value)})
                    except:
                        pass
                # else:
                listitem.setProperty('%s' % (key), value)
            listitem.setProperty("index", str(count))
            itemlist.append(listitem)
        for x in threads:
            x.join()
        return itemlist

    def downloadVid(self, url, name):
        ok = False
        if url is not None:
            if name is not None:
                filename = str(name)
            else:
                filename = xbmc.makeLegalFilename(str(url).rpartition('/')[2])
            ok = self.downloadVideo(url, filename)
        else:
            ok = False
        return ok

    def select(self, title, menuItems):
        select = xbmcgui.Dialog().select(title, menuItems)
        if select == -1:
            return None
        else:
            return menuItems[select]

    def getKeyboard(self, default='', heading='', hidden=False):
        kboard = xbmc.Keyboard(default, heading, hidden)
        kboard.doModal()
        if kboard.isConfirmed():
            return str(kboard.getText())
        return ""

    def setView(self, viewMode=500, endofdir=True):
        # xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        self.setSortMethodsForCurrentXBMCList(sortKeys=['name', 'date', 'file', 'duration', 'none'])
        if not endofdir:
            ok = xbmc.executebuiltin("Container.SetViewMode({0})".format(viewMode))
        else:
            ok = xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=True,
                                           cacheToDisc=True)
            xbmc.executebuiltin("Container.SetViewMode({0})".format(viewMode))
        return ok

    def getImage(self, title):
        dialog = xbmcgui.Dialog()
        image = dialog.browse(1, title, 'pictures', '.jpg|.png', True)
        return image

    def showMessage(self, msg):
        xbmc.executebuiltin('Notification(Motherless,' + str(msg.encode('utf-8', 'ignore')) + ')')

    def showBusyAnimation(self):
        xbmc.executebuiltin('ActivateWindow(busydialog)')

    def hideBusyAnimation(self):
        xbmc.executebuiltin('Dialog.Close(busydialog,true)')

    def closeAllDialogs(self):
        xbmc.executebuiltin('Dialog.Close(all, true)')

    def log(self, msg):
        try:
            xbmc.log(msg)
        except:
            xbmc.log(msg.encode('utf-8'))

    def addSortMethod(self, method):
        xbmcplugin.addSortMethod(handle=self.handle, sortMethod=method)

    def setSortMethodsForCurrentXBMCList(self, sortKeys):
        if not sortKeys or sortKeys == []:
            self.addSortMethod(xbmcplugin.SORT_METHOD_UNSORTED)
        else:
            if 'name' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_LABEL)
            if 'size' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_SIZE)
            if 'duration' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_DURATION)
            if 'genre' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_GENRE)
            if 'rating' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_VIDEO_RATING)
            if 'date' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_DATE)
            if 'file' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_FILE)
            if 'none' in sortKeys:
                self.addSortMethod(xbmcplugin.SORT_METHOD_UNSORTED)

    def getContainerFolderPath(self):
        return xbmc.getInfoLabel('Container.FolderPath')

    def getListItemPath(self):
        return xbmc.getInfoLabel('ListItem.Path')

    def getCurrentWindow(self):
        return xbmc.getInfoLabel('System.CurrentWindow')

    def getCurrentControl(self):
        return xbmc.getInfoLabel('System.CurrentControl')

    def getCurrentWindowXmlFile(self):
        return xbmc.getInfoLabel('Window.Property(xmlfile)')


    def downloadVideo(self, url, name):

        def _pbhook(self, numblocks, blocksize, filesize, url=None, dp=None):
            try:
                percent = min((numblocks * blocksize * 100) / filesize, 100)
                currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
                kbps_speed = int((numblocks * blocksize) / (time.clock() - start))
                if kbps_speed > 0:
                    eta = (filesize - numblocks * blocksize) / kbps_speed
                else:
                    eta = 0
                kbps_speed = kbps_speed / 1024
                total = float(filesize) / (1024 * 1024)
                mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
                e = 'Speed: %.02f Kb/s ' % kbps_speed
                e += 'ETA: %02d:%02d' % divmod(eta, 60)
                dp.update(percent, '', mbs, e)
            except:
                percent = 100
                dp.update(percent)
            if dp.iscanceled():
                dp.close()
                raise StopDownloading('Stopped Downloading')

        def clean_filename(self, s):
            if not s:
                return ''
            badchars = '\\/:*?\"<>|\''
            for c in badchars:
                s = s.replace(c, '')
            return s
            # return s;

        download_path = self.addon.getSetting('download_path')
        if download_path == '':
            try:
                download_path = xbmcgui.Dialog().browse(0, "Download Path", 'myprograms', '', False, False)
                self.addon.setSetting(id='download_path', value=download_path)
                if not xbmcvfs.exists(download_path):
                    xbmcvfs.mkdir(download_path)
            except:
                pass
        if download_path != '':
            dp = xbmcgui.DialogProgress()
            name = name.split("[")[0]
            dp.create("{0}  Download".format(str(self.addonid).rpartition('.')[2]), name[:50])
            tmp_file = tempfile.mktemp(dir=download_path, suffix=".mp4")
            tmp_file = xbmc.makeLegalFilename(tmp_file)
            start = time.clock()
            try:
                urllib.urlretrieve(url, tmp_file, lambda nb, bs, fs, url=url: _pbhook(nb, bs, fs, url, dp))
                vidfile = xbmc.makeLegalFilename(download_path + clean_filename(name) + ".mp4")
                try:
                    xbmcvfs.rename(tmp_file, vidfile)
                    return vidfile
                except:
                    return tmp_file
            except:
                while os.path.exists(tmp_file):
                    try:
                        os.remove(tmp_file)
                        break
                    except:
                        pass

