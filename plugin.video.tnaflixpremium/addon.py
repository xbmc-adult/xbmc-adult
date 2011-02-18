import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import re

Addon = xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) )

def CATEGORIES():
        req = urllib2.Request('http://premium.tnaflix.com/')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        categoryblock = re.compile('<h2>Categories</h2>(.+?)</div>',re.S).findall(link)
        match=re.compile('<li><a href="(.+?)" title=".+?">(.+?)</a></li>').findall(categoryblock[0])
        for url,name in match:
                addDir(name,url,1,'',1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def SORTMETHOD(url):
        addDir('Being Watched',url+'/being-watched/',2,'',1)
        addDir('Most Recent',url+'/most-recent/',2,'',1)
        addDir('Most Viewed',url+'/most-viewed/',2,'',1)
        addDir('Top Rated',url+'/top-rated/',2,'',1)
        addDir('Most Pop',url+'/most-popular/',2,'',1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
                       
def VIDEOLIST(url,page):
        req = urllib2.Request(url+str(page))
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<a href=".+?" class="videoThumb" title="(.+?)"> <img onmouseout=".+?" onmouseover=".+?http://pr-static-edge.tnaflix.com/previews(.+?)-thmb.+?"  src="(.+?)" id=".+?" width=".+?" height=".+?" /></a>').findall(link)
        for name,videourl,thumb in match:
                addLink(name,"http://pr-cdn-edge.tnaflix.com/videos" + videourl + "-hq.flv",thumb,len(match))
        if (len(match) == 24):
            addDir('Next Page',url,2,'',page+1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
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

def addLink(name,url,iconimage,totalitems):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"MPAA" : "XXX" } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,totalItems=totalitems)
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
