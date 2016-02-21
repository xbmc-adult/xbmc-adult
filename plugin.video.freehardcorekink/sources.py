import xml.etree.ElementTree as ET
import urllib2
import xbmc

CATEGORIES = {
    'animatedkink': {
        'name': 'animatedkink',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=animatedkink&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=animatedkink&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/ANI/17032_AK_200x300.jpg'
    },
    'boundgangbangs': {
        'name': 'boundgangbangs',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=boundgangbangs&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=boundgangbangs&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/BGB/11965_BGB_315x300.jpg'
    },
    'devicebondage': {
        'name': 'devicebondage',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=devicebondage&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=devicebondage&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/DB/33381_DB_250x250.jpg'
    },
    'divinebitches': {
        'name': 'divinebitches',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=divinebitches&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=divinebitches&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/DIB/7486_DiB_250x250.jpg'
    },
    'dungeonsex': {
        'name': 'dungeonsex',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=dungeonsex&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=dungeonsex&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/DS/36007_DS_315x300.jpg'
    },
    'electrosluts': {
        'name': 'electrosluts',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=electrosluts&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=electrosluts&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/ES/35067_ES_315x300.jpg'
    },
    'everythingbutt': {
        'name': 'everythingbutt',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=everythingbutt&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=everythingbutt&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/EB/35451_B_EB_315x300.jpg'
    },
    'footworship': {
        'name': 'footworship',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=footworship&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=footworship&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/FW/29705_FW_600x250.jpg'
    },
    #Parse error XML encoding
    """
    'fuckingmachines': {
        'name': 'fuckingmachines',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=fuckingmachines&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=fuckingmachines&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/FM/6746_FM_650x600.jpg'
    },
    """
    'hardcoregangbang': {
        'name': 'hardcoregangbang',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=hardcoregangbang&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=hardcoregangbang&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/HCGB/30076_HCGB_315x300.jpg'
    },
    'hogtied': {
        'name': 'hogtied',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=hogtied&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=hogtied&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/HT/35596_HT_900x250.jpg'
    },
    'kinkarchive': {
        'name': 'kinkarchive',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=kinkarchive&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=kinkarchive&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/KA/3A3D0518_scarlett098_annaw011_KA_900x250.jpg'
    },
    'kinkuniversity': {
        'name': 'kinkuniversity',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=kinkuniversity&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=kinkuniversity&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/KU/35576_KU_315x300.jpg'
    },
    'meninpain': {
        'name': 'meninpain',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=meninpain&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=meninpain&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/MIP/4232_MIP_650x600.jpg'
    },
    'publicdisgrace': {
        'name': 'publicdisgrace',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=publicdisgrace&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=publicdisgrace&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/PD/37785_37787_PD_1152x648.jpg'
    },
    'sadisticrope': {
        'name': 'sadisticrope',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=sadisticrope&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=sadisticrope&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/SR/0474_SR_315x300.jpg'
    },
    'sexandsubmission': {
        'name': 'sexandsubmission',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=sexandsubmission&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=sexandsubmission&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/SAS/6151_SAS_650x600.jpg'
    },
    'thetrainingofo': {
        'name': 'thetrainingofo',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=thetrainingofo&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=thetrainingofo&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/TTOO/28388_TTOO_315x300.jpg'
    },
    'theupperfloor': {
        'name': 'theupperfloor',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=theupperfloor&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=theupperfloor&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/TUF/12882_TUF_315x300.jpg'
    },
    'tspussyhunters': {
        'name': 'tspussyhunters',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=tspussyhunters&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=tspussyhunters&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/TSPH/21837_TSPH_315x300.jpg'
    },
    'tsseduction': {
        'name': 'tsseduction',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=tsseduction&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=tsseduction&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/TSS/33154_TSS_315x300.jpg'
    },
    'ultimatesurrender': {
        'name': 'ultimatesurrender',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=ultimatesurrender&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=ultimatesurrender&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/US/32696_US_315x300.jpg'
    },
    #Parse error XML encoding
    """
    'waterbondage': {
        'name': 'waterbondage',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=waterbondage&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=waterbondage&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/WB/4286_WB_300x500.jpg'
    },
    'wiredpussy': {
        'name': 'wiredpussy',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=wiredpussy&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=wiredpussy&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/WP/6955_WP_650x600.jpg'
    },
    """
    'whippedass': {
        'name': 'whippedass',
        'rss': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=whippedass&type=mpg&noshoots=50',
        'info': 'http://www.kinkydollars.com/feed_helper.php?feed_type=atom&webid=padalton&program=revshare&sitename=whippedass&type=mpg&noshoots=0',
        'fanart': 'http://cdnp.kink.com/2257/banners/WA/34287_WA_315x300.jpg'
    }
}


# Fetch text content from an URL
def read(url):
    _log(url)
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()

    return data

# Write this module messages on XBMC log
def _log(message):
    xbmc.log("freehardcorekink."+message)


def dump(obj):
  for attr in dir(obj):
     print "obj.%s = %s" % (attr, getattr(obj, attr))


def get_category_list():
    cat_list = []
    for key, cat in CATEGORIES.iteritems():
        content = read(cat['info'])
        _log("get info for Category "+cat['name']+" from "+cat['info'])
        root = ET.fromstring(content)
        chan = root.find("channel")
        title = chan.find("title").text
        cat['title'] = title
        img = chan.find("image")
        image = img.find("url").text
        cat['image'] = image
        cat_list.append(cat)
    return cat_list


def get_video_list(category):
    vid_list = []
    content = read(CATEGORIES[category]['rss'])
    root = ET.fromstring(content)
    for vid in root.findall("./channel/item"):
        _log('item found '+vid.find("title").text)
        title = vid.find("title").text
        cnt = 0
        grp = vid.find(".//{http://search.yahoo.com/mrss/}group")
        for item in grp.findall(".//{http://search.yahoo.com/mrss/}content"):
            cnt+= 1
            _log('content found '+item.get('url'))
            itm = {}
            itm['title'] = title+' '+cnt.__str__()
            image = item.find("{http://search.yahoo.com/mrss/}thumbnail").get('url')
            itm['image'] = image
            url = item.get('url')
            itm['url'] = url
            itm['category'] = category
            vid_list.append(itm)
    return vid_list
