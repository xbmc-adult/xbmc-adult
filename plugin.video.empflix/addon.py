# Note: Only partially working.
# Category Listing: Working
# Being Watched / Most Recent / Most Viewed / Top Rated Listings: Working
# Video Listings: Working
# Video Thumbnails: Working
# Video Playback: Not Working as requires login script / LWP cookie config

import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import cookielib
import re

settings = xbmcaddon.Addon(id='plugin.video.empflix')
cookiejar = cookielib.LWPCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookie_handler)

def CATEGORIES():
        req = urllib2.Request('http://www.empflix.com/browse.php')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('(?:<li><a href=")(?:http://www.empflix.com/channels/watched-)(.*(?=.html)).html">(.*)(?=</a>)').findall(link)
        addDir('All','http://www.empflix.com/browse.php',1,'',1)
        for channame,name in match:
                addDir(name,'http://www.empflix.com/channels/'+channame+'.html',1,'',1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def SORTMETHOD(url):
        if url == 'http://www.empflix.com/browse.php':
                addDir('Being Watched',url+'?category=bw',2,'',1)
                addDir('Most Recent',url+'?category=mr',2,'',1)
                addDir('Most Viewed',url+'?category=mv',2,'',1)
                addDir('Top Rated',url+'?category=tr',2,'',1)
        else:
                match=re.compile('(http://www.empflix.com/channels/)(.*)').findall(url)
                for start,end in match:
                        addDir('Being Watched',start+'watched-'+end,2,'',1)
                        addDir('Most Recent',start+'new-'+end,2,'',1)
                        addDir('Most Viewed',start+'popular-'+end,2,'',1)
                        addDir('Top Rated',start+'rated-'+end,2,'',1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
                       
def VIDEOLIST(url,page):
        req = urllib2.Request(url+'&page='+str(page))
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('(?:<a href=")(http://www.empflix.com/videos/.*(?=.html).html)"  title="(.*)(?=">)"><img src="/images/blank.gif" data-src="(.*)(?=" alt=)').findall(link)
        for videourl,name,thumb in match:
                addLink(name,videourl+'?',3,thumb.strip())
        if (len(match) == 24):
                addDir('Next Page',url,2,'',page+1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

# THIS SECTION IS BROKEN, REQUIRES LWP COOKIEJAR CONFIGURATION!
def PLAYVIDEO(url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<a href="(.+?)" class="downloadButton">Download FLV</a>').findall(link)
        for videourl in match:
                xbmc.Player().play(videourl)

        
        
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
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

def addLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

def addDir(name,url,mode,iconimage,page):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def main():
        
        params=get_params()
        url=None
        name=None
        mode=None
        page=1

        try:
                url=urllib.unquote_plus(params["url"])
        except:
                pass
        try:
                name=urllib.unquote_plus(params["name"])
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

        if mode==None or url==None or len(url)<1:
                CATEGORIES()
               
        elif mode==1:
                SORTMETHOD(url)
                
        elif mode==2:
                VIDEOLIST(url,page)

        elif mode==3:
                PLAYVIDEO(url)

if __name__ == "__main__":
    main()
