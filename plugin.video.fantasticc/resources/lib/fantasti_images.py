import gethtml
import re
import xbmcplugin
import xml_scrapers


try:
    import utils
except:
    print 'Not running in XBMC!'

### lists of urls ###
thebase = 'http://fantasti.cc/images/'

popbase = thebase + 'popular/'


def rss_url(category1, category2):
    # rss url constructor
    return 'http://fantasti.cc/images/'+category1+'/'+category2+'/RSSFEED'

def user_xml_url(username):
    # user xml url constructor
    return 'http://fantasti.cc/album_xml.php?username='+username
            
def transform(url):
    # hack to transform thumbnail url into the full image url
    return re.sub('/thumb','',url)

def html_image_scrape(url):
    html = gethtml.get_no_unescape(url)
    scrape = re.compile('src="(.+?)" alt="(.{0,30})" ').findall(html)
    for url,info in scrape:
            url = transform(url)
    

    
print xml_scrapers.xml_image_scrape(gethtml.get_no_unescape('http://fantasti.cc/album_xml.php?username=girloftheday'))


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

def addImage():

def addDirectory():



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

if mode==None:
    print "Image folders"
    CATEGORIES()
elif mode == 1:
   print "Indexing Videos"
   INDEX(url)




xbmcplugin.endOfDirectory(int(sys.argv[1]))
