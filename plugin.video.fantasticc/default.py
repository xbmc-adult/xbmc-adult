# FANTASTI.CC XBMC ADDON
# See addon.xml for version number

# Written by Ksosez and anarchintosh
# Released under GPL(v2)
# Supports Pictures and Videos

import os
import sys
import urllib
import xbmcgui,xbmcaddon,xbmcplugin

# annoyingly, utils can't be imported until this is done
__addonpath__= os.getcwd()
__addonname__ = (os.path.split(__addonpath__))[1] 
sys.path.append(os.path.join( __addonpath__, 'resources', 'lib' ))

import utils

def LOGIN():
 #do login if settings say we should
    import fantasti_login
    
    if utils.__settings__.getSetting('use-account') == 'true':
        print 'DOING FANTASTI.CC LOGIN'
        fantasti_login.do()
    else:
        #delete old cookie/ avatar image
        fantasti_login._get_login_path()
    

##### present two folder choices; videos or images. ####

def addDir(name, the_type, iconimage=''):
    u = "%s?type=%s" % ( sys.argv[0], the_type )
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type= the_type, infoLabels={ "Title": name } )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

if not sys.argv[2]:
        LOGIN()
        addDir('Videos','video','')
        addDir('Image support coming soon...','image','')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

if 'video' in sys.argv[2]:
        import fantasti_videos

#elif 'image' in sys.argv[2]:
#        import fantasti_images
