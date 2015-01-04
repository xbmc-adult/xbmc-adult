import sesame
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import socket
import re

NB_ITEM_PAGE = 28
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

def log(msg):
    xbmc.log((u"### [%s] - %s" % (__name__, msg,)).encode('utf-8'),
             level=xbmc.LOGDEBUG)

def openUrl(url, postData=None):
    try:
        useragent = {'User-Agent': USER_AGENT}
        req = urllib2.Request(url, headers=useragent)
        if postData:
            data = urllib.urlencode(postData)
            website = urllib2.urlopen(req, data)
        else:
            website = urllib2.urlopen(req)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            log('We failed to reach a server.')
            log('Reason: %s' % e.reason)
            return False
        elif hasattr(e, 'code'):
            log('The server couldn\'t fulfill the request.')
            log('Error code: %s' % e.code)
            return False
    except socket.timeout as e:
        # catched
        log(type(e))
        return False
    else:
        # read html code
        html = website.read()
        website.close()
        return html

def _get_keyboard( default="", heading="", hidden=False ):
	""" shows a keyboard and returns a value """
	keyboard = xbmc.Keyboard( default, heading, hidden )
	keyboard.doModal()
	if ( keyboard.isConfirmed() ):
		return unicode( keyboard.getText(), "utf-8" )
	return default

def showRoot(localpath, handle):
	ri=[
		("Latest", "http://www.tube8.com/latest/"),
		("Most Viewed", "http://www.tube8.com/most-viewed/"),
		("Top Rated", "http://www.tube8.com/top/"),
		("Most Favorited", "http://www.tube8.com/most-favorited/"),
		("Most Discussed", "http://www.tube8.com/most-discussed/"),
		("Most Voted", "http://www.tube8.com/most-voted/"),
		("Longest", "http://www.tube8.com/longest/"),
		]

	li=xbmcgui.ListItem("Search")
	u=localpath + "?mode=4"
	xbmcplugin.addDirectoryItem(handle, u, li, True)

	li=xbmcgui.ListItem("Categories")
	u=localpath + "?mode=1"
	xbmcplugin.addDirectoryItem(handle, u, li, True)

	for name, url in ri:
		li=xbmcgui.ListItem(name)
		u=localpath + "?mode=2&name=" + urllib.quote_plus(name) + \
      "&url=" + urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(handle, u, li, True, NB_ITEM_PAGE)

	xbmcplugin.endOfDirectory(handle)

def showCategories(localpath, handle):
	url="http://www.tube8.com/categories.html"
	htmlContent = openUrl(url)

	catPattern = '<li><a href="(http:\/\/www\.tube8\.com\/cat\/.+?)">(.+?)<\/a>'
	catRE = re.compile(catPattern)
	match = catRE.findall(htmlContent)
	categories = []
	for url, name in match:
		if name not in categories:
			categories.append(name)
			li=xbmcgui.ListItem(name)
			u=localpath + "?mode=2&name=" + urllib.quote_plus(name) + \
      "&url=" + urllib.quote_plus(url)
			xbmcplugin.addDirectoryItem(handle, u, li, True, NB_ITEM_PAGE)
	xbmcplugin.endOfDirectory(handle)

def showSearchList(localpath, handle, url, page):
	pageUrl = url + "&page=" + str(int(page))
	showListCommon(localpath, handle, pageUrl)
	name = "Next Page " + str(int(page) + 1)
	li=xbmcgui.ListItem(name)
	u=localpath + "?mode=5&name=" + urllib.quote_plus(name) + \
    "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1)
	xbmcplugin.addDirectoryItem(handle, u, li, True, NB_ITEM_PAGE)
	xbmcplugin.endOfDirectory(handle)

def showCatList(localpath, handle, url, page):
	pageUrl = url + "page/" + str(int(page)) + "/"
	showListCommon(localpath, handle, pageUrl)
	name = "Next Page " + str(int(page) + 1)
	li=xbmcgui.ListItem(name)
	u=localpath + "?mode=2&name=" + urllib.quote_plus(name) + \
    "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1)
	xbmcplugin.addDirectoryItem(handle, u, li, True, NB_ITEM_PAGE)
	xbmcplugin.endOfDirectory(handle)

def showListCommon(localpath, handle, pageUrl):
	log('Opening page: %s' % pageUrl)
	htmlContent = openUrl(pageUrl)

	#thumbRE = '<img .+? class="videoThumbs" .+? src="(.+?)".+?>'
	#videosRE = 'sh2"><a href="(.+?)" title="(.+?)">.+?</a>'
	lenghtRE = '<div class="video-right-text float-right"><strong>(([0-9]{2}:)?[0-9]{2}:[0-9]{2})</strong></div>'

	if 'tube8.com/top/' in pageUrl:
		thumbRE = '<img .+? class="videoThumbs" .+? src="(.+?)".+?>'
	else:
		thumbRE = 'class="videoThumbs"[\s\w]+?id=".+"[\s\w]+?category=".+"[\s\w]+?src="([^"]+)"'
	videosRE = 'sh2">\s*?<a href="(.+)" title="(.+?)">'
	lenghtRE = '<div class="video-right-text float-right"><strong>(([0-9]{2}:)?[0-9]{2}:[0-9]{2})</strong></div>'

	thumbPattern, videoPattern, lenghtPattern = re.compile(thumbRE), re.compile(videosRE), re.compile(lenghtRE)

	matchThumb=thumbPattern.findall(htmlContent)
	matchVid=videoPattern.findall(htmlContent)
	matchlengh=lenghtPattern.findall(htmlContent)

	log('Duration: %s' % matchlengh)
	log('Video: %s' % matchVid)
	log('Thumb: %s' % matchThumb)

	totalLen = len(matchVid)
	n = 0
	for url, name in matchVid:
		thumb, duration = matchThumb[n], matchlengh[n][0]
		li=xbmcgui.ListItem(name, name, thumb, thumb)
		li.setInfo( type="Video", infoLabels={ "Title": name, "Duration": duration } )
		u=localpath + "?mode=3&name=" + urllib.quote_plus(name) + \
      "&url=" + urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(handle, u, li, False, totalLen)
		n = n + 1

def playVideo(localpath, handle, url):
	f=urllib2.urlopen(url)
	a=f.read()
	f.close()

	p=re.compile('"video_url":"([^"]+)')
	match=p.findall(a)
	eurl=match[0].replace('\/', '/')

	p2=re.compile('"video_title":"([^"]+)')
	iv=p2.findall(a)[0]

	video=sesame.decrypt(eurl, iv, 256)
	print "Playing: " + video
	xbmc.Player().play(video)

def get_params(args):
	param=[]
	print "Parsing arguments: " + str(args)
	paramstring=args[2]
	if len(paramstring)>=2:
		params=args[2]
		cleanedparams=params.replace('?', '')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
		return param

def search_videos(localpath, handle):
	searchUrl = "http://www.tube8.com/search.html?q="
	vq = _get_keyboard( heading="Enter the query" )
	# if blank or the user cancelled the keyboard, return
	if ( not vq ): return False, 0
	# we need to set the title to our query
	title = urllib.quote_plus(vq)
	searchUrl += title
	print "Searching URL: " + searchUrl
	showSearchList(localpath, handle, searchUrl, 1)

def main():
	params=get_params(sys.argv)
	mode=None
	url=None
	page=1
	try:
		url=urllib.unquote_plus(params["url"])
	except:
		pass
	try:
		mode=int(params["mode"])
	except:
		pass
	try:
		page=int(params["page"])
	except:
		pass

	if mode==None:
		showRoot(sys.argv[0], int(sys.argv[1]))
	elif mode==1:
		showCategories(sys.argv[0], int(sys.argv[1]))
	elif mode==2:
		showCatList(sys.argv[0], int(sys.argv[1]), url, page)
	elif mode==5:
		showSearchList(sys.argv[0], int(sys.argv[1]), url, page)
	elif mode==3:
		playVideo(sys.argv[0], int(sys.argv[1]), url)
	elif mode==4:
		search_videos(sys.argv[0], int(sys.argv[1]))

if __name__ == "__main__":
	main()

