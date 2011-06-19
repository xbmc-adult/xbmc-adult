'''
Miscallaneous things most .py files in this addon will need
'''

import xbmc,xbmcaddon
import os

def _updir(thepath, x):
        # move up x directories on thepath
        while x > 0:
            x -= 1
            thepath = (os.path.split(thepath))[0]
        return thepath

def get_avatar_path(folder):
        # this annoying code is needed because avatar may be .gif or .jpg etc
        if os.path.exists(folder):
            dirlist = os.listdir(folder)
            if dirlist:
                    for the_file in dirlist:
                        if 'avatar' in str(the_file): return os.path.join(folder, the_file)
            elif not dirlist: return False
        else: return False


__addonpath__= os.getcwd()
__addonname__ = (os.path.split(__addonpath__))[1]
print __addonname__
__name__ = 'Fantasti.cc'
__datapath__ = xbmc.translatePath('special://profile/addon_data/'+__addonname__)
#annoying thing necessary to get over XBMC bug.
if not os.path.exists(__datapath__): os.makedirs(__datapath__)

__logindata__ = os.path.join(__datapath__,'login_data')
__settings__ = xbmcaddon.Addon(id=__addonname__)
__language__ = __settings__.getLocalizedString

__avatar__ = get_avatar_path(__logindata__)
__username__ = __settings__.getSetting('username')

__login__ = os.path.exists(os.path.join(__logindata__,'cookies.lwp'))
#uc is username with capitalised first letter
__uc__ = __username__[0].upper() + __username__[1:]
#lc is username in complete lower case
__lc__ = __username__.lower()

__ipurl__ = 'http://77.247.181.97/'
__mainurl__ = 'http://fantasti.cc/'

__images__ = os.path.join(__addonpath__,'resources','images')
__defaultimage__ = os.path.join(__images__,'provocative_logo.png')
__smallicon__ = os.path.join(__images__,'smallicon.png')

def notify(title = False, message = False, iconpath = False, times = False):
        if not title:    title = __name__
        if not message:  message = ' '
        if not times:    times = '3000'
        if not iconpath: iconpath = __smallicon__
        xbmc.executebuiltin("XBMC.Notification("+title+","+message+","+str(times)+","+iconpath+")")
 



if __name__ == "__main__":
    print "__addonpath__  =  "+__addonpath__
    print "__addonname__  =  "+__addonname__
