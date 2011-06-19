'''
login to fantasti.cc and save cookie and avatar image
'''

import weblogin
import gethtml
import utils

import urllib2
import os
import re

#main function:

def do():
        lc = utils.__lc__
        uc = utils.__uc__

        #path we will save login stuff to.
        login_path = _get_login_path()
        
        #attempt the login
        password = utils.__settings__.getSetting('password')
        hidesuccess = utils.__settings__.getSetting('hide-successful-login-messages')
        log_in = weblogin.doLogin(login_path,utils.__username__,password)
        if log_in == True:

                avatar = _get_and_save_avatar(lc, login_path)
                if hidesuccess == 'false': utils.notify('Welcome back '+uc,'Fantasti.cc loves you',avatar)

        elif log_in == False: utils.notify('Login Failure',uc+' could not login',default_image)




#supporting functions:

def _get_and_save_avatar(lc, path):
        #using lowercase username, build the url to the user's avatar
        url = utils.__ipurl__+'avatar/'+lc[0]+'/'+lc[1]+'/'+lc[2]+'/'+lc

        #trial and error to find the correct image format
        urlist = [url+'.jpeg',url+'.jpg',url+'.png',url+'.gif']
        for surl in urlist:
                try: response = urllib2.urlopen(surl)
                except urllib2.URLError, e: pass
                else:
                     #if correct url was found, save the response to avatar file and return the path
                     new_avatar_path = os.path.join(path,'avatar'+_picformat(surl))
                     _save(new_avatar_path, response.read())
                     return new_avatar_path

def _picformat(url):
        #get image format from url (ie .jpg)
        return '.'+(re.split('\.+', url))[-1]
                                       
def _save(filepath,contents):  
     fh = open(filepath, 'wb')
     fh.write(contents)  
     fh.close()
     
def _get_login_path():
        # wraps login path, so that if necessary it will make path, clear old folder contents and also pass the path
        the_path = utils.__logindata__
        if not os.path.exists(the_path): os.mkdir(the_path)
        else: _delete_folder_contents(the_path)
        return the_path

def _delete_folder_contents(folder):
    dirlist = os.listdir(folder)
    if dirlist:
        for the_file in dirlist:
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path): os.unlink(file_path)
            except Exception, e: print e



