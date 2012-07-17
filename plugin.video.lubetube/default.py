# The documentation written by Voinage was used as a template for this addon
# http://wiki.xbmc.org/?title=HOW-TO_write_plugins_for_XBMC
#
# This addon is licensed with the GNU Public License, and can freely be modified
# http://www.gnu.org/licenses/gpl-2.0.html

import urllib,urllib2,re,xbmcplugin,xbmcgui

def CATEGORIES():
	addDir("Most Recent", "http://lubetube.com", 1, "")
	addDir("Amateur", "http://lubetube.com/search/cat/amateur", 1, "")
	addDir("Anal", "http://lubetube.com/search/cat/anal", 1, "")
	addDir("Asian", "http://lubetube.com/search/cat/asian", 1, "")
	addDir("Ass", "http://lubetube.com/search/cat/asslicking", 1, "")
	addDir("BBW", "http://lubetube.com/search/cat/bbw", 1, "")
	addDir("Big Butt", "http://lubetube.com/search/cat/bigbutt", 1, "")
	addDir("Big Cock", "http://lubetube.com/search/cat/bigcock", 1, "")
	addDir("Big Tits", "http://lubetube.com/search/cat/bigtits", 1, "")
	addDir("Blonde", "http://lubetube.com/search/cat/blonde", 1, "")
	addDir("Blowjob", "http://lubetube.com/search/cat/blowjob", 1, "")
	addDir("Bondage", "http://lubetube.com/search/cat/bondage", 1, "")
	addDir("Creampie", "http://lubetube.com/search/cat/creampie", 1, "")
	addDir("Cumshot", "http://lubetube.com/search/cat/cumshot", 1, "")
	addDir("Cum Swapping", "http://lubetube.com/search/cat/cumswapping", 1, "")
	addDir("Double Penetration", "http://lubetube.com/search/cat/doublepenetration", 1, "")
	addDir("Ebony", "http://lubetube.com/search/cat/ebony", 1, "")
	addDir("Facial", "http://lubetube.com/search/cat/facial", 1, "")
	addDir("Fetish", "http://lubetube.com/search/cat/fetish", 1, "")
	addDir("Fingering", "http://lubetube.com/search/cat/fingering", 1, "")
	addDir("Fisting", "http://lubetube.com/search/cat/fisting", 1, "")
	addDir("Foot Fetish", "http://lubetube.com/search/cat/footfetish", 1, "")
	addDir("Footjob", "http://lubetube.com/search/cat/footjob", 1, "")
	addDir("Fucking Machine", "http://lubetube.com/search/cat/fuckingmachine", 1, "")
	addDir("Gagging", "http://lubetube.com/search/cat/gagging", 1, "")
	addDir("Gangbang", "http://lubetube.com/search/cat/gangbang", 1, "")
	addDir("Group Sex", "http://lubetube.com/search/cat/groupsex", 1, "")
	addDir("Handjob", "http://lubetube.com/search/cat/handjob", 1, "")
	addDir("Hardcore", "http://lubetube.com/search/cat/hardcore", 1, "")
	addDir("Insertion", "http://lubetube.com/search/cat/insertion", 1, "")
	addDir("Interracial", "http://lubetube.com/search/cat/interracial", 1, "")
	addDir("Latex", "http://lubetube.com/search/cat/latex", 1, "")
	addDir("Latina", "http://lubetube.com/search/cat/latina", 1, "")
	addDir("Lesbian", "http://lubetube.com/search/cat/lesbian", 1, "")
	addDir("Masturbation", "http://lubetube.com/search/cat/masturbation", 1, "")
	addDir("MILF", "http://lubetube.com/search/cat/milf", 1, "")
	addDir("Party", "http://lubetube.com/search/cat/party", 1, "")
	addDir("Pornstar", "http://lubetube.com/search/cat/pornstar", 1, "")
	addDir("POV", "http://lubetube.com/search/cat/pov", 1, "")
	addDir("Public", "http://lubetube.com/search/cat/public", 1, "")
	addDir("Reality", "http://lubetube.com/search/cat/reality", 1, "")
	addDir("Redhead", "http://lubetube.com/search/cat/redhead", 1, "")
	addDir("Solo", "http://lubetube.com/search/cat/solo", 1, "")
	addDir("Spanking", "http://lubetube.com/search/cat/spanking", 1, "")
	addDir("Squirting", "http://lubetube.com/search/cat/squirting", 1, "")
	addDir("Striptease", "http://lubetube.com/search/cat/striptease", 1, "")
	addDir("Teen", "http://lubetube.com/search/cat/teen", 1, "")
	addDir("Threesome", "http://lubetube.com/search/cat/threesome", 1, "")
	addDir("Toys", "http://lubetube.com/search/cat/toys", 1, "")
	addDir("Tranny", "http://lubetube.com/search/cat/tranny", 1, "")
	addDir("Voyeur", "http://lubetube.com/search/cat/voyeur", 1, "")


def INDEX(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<a class="frame[^"]*" href="(http://lubetube.com/video/[^"]+)" title="([^"]+)">.*?<img src="([^"]+)".+?Length:([^<]+)', re.DOTALL).findall(link)
        for url,name,thumbnail,length in match:
		addDownLink(name+length,url,2,thumbnail)


def VIDEOLINKS(url,name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('playlist_flow_player_flv.php\?vid\=[0-9]*').findall(link)
        for url in match:
		req = urllib2.Request('http://lubetube.com/' + url)
	        response = urllib2.urlopen(req)
	        link=response.read()
        	response.close()
	        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		match=re.compile('url="(.*)" type').findall(link)
		for url in match:
                        listitem = xbmcgui.ListItem(name)
                        listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
                        url = url.replace('&amp;', '&')
                        xbmc.Player().play(url, listitem)
        



                
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




def addDownLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
              
params=get_params()
url=None
name=None
mode=None

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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
       
elif mode==1:
        print ""+url
        INDEX(url)
        
elif mode==2:
        print ""+url
        VIDEOLINKS(url,name)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
