import xbmcaddon

__plugin__ = 'VideoDevil'
__author__ = 'sfaxman'
__credits__ = 'bootsy'

addon = xbmcaddon.Addon(id='plugin.video.videodevil')
rootDir = addon.getAddonInfo('path')
if rootDir.endswith(';'):
    rootDir = rootDir[:-1]

class Main:
    def __init__(self):
        self.pDialog = None
        self.run()

    def run(self):
        import videodevil
        videodevil.Main()

Main()
