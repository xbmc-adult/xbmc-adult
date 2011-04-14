# -*- coding: UTF-8 -*-

"""
 Megavideo and Megaporn-Video Resolver v0.5
 Copyleft (Licensed under GPLv3) Anarchintosh 

 This resolver is based on work from:
 Alessio Glorioso, Ksosez, Pedro Guedes, Voinage and Coolblaze.



 -------Commands:---------

 for baseurl use either 'porn' or 'regular'.


 TO RESOLVE A URL
 - (None is a valid setting for cookiepath)
 - This returns a list for these things;
 - FLV_File,Original_File,title,description,runtime

 ====================================================
 print megavideo.resolveURL(baseurl, cookiepath, url)
 ====================================================

 

 TO CHECK IF A LINK IS STILL ONLINE (optional):
 - Returns True or False

 ====================================== 
 print megavideo.is_online(baseurl,url)
 ======================================



 TO LOG IN (GET A LOGIN COOKIE) (optional):
 - Returns 'Free' or 'Premium' if login is successful
 - Returns None if login fails

 ================================================================
 print megavideo.doLogin(baseurl, cookiepath, username, password)
 ================================================================

 
"""

import os,re
import urllib,urllib2,cookielib
import logging

#check if bin is installed (it is on python 2.5+)
#if it isn't, install it.
try: bin(1)
except:
    def bin(n):
        return bin_function(n)

def bin_function(n):
    '''convert denary integer n to binary string bStr.
    also append 0b to the beginning just like bin does'''
    bStr = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return '0b' + bStr

#global strings for valid baseurl
porn = 'http://www.megaporn.com/video/'
regular = 'http://www.megavideo.com/'

firefox_header = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

log = logging.getLogger("megavideo")


def setBaseURL(baseurl):
    # API feature to neaten up how functions are used
    if baseurl == 'regular':
       return regular
    elif baseurl == 'porn':
       return porn

def openfile(filepath):
     fh = open(filepath, 'r')
     contents=fh.read()
     fh.close()
     return contents

def check_login(source):
        #feed me some mega page source
        #returns 'free' or 'premium' if logged in
        #returns 'none' if not logged in
        
        login = re.search('Welcome', source)
        premium = re.search('flashvars.status = "premium";', source)        

        if login is not None:
             if premium is not None:
                  return 'premium'
             elif premium is None:
                  return 'free'
        else:
             return login

def doLogin(baseurl, cookiepath, username, password):

    baseurl=setBaseURL(baseurl)

    if username and password:
        #delete the old cookie
        try:
              os.remove(cookiepath)
        except:
              pass

        #build the login code, from user, pass, baseurl and cookie
        login_data = urllib.urlencode({'username' : username, 'password' : password, 'login' : 1, 'redir' : 1})   
        req = urllib2.Request(baseurl + '?c=login', login_data)
        req.add_header('User-Agent',firefox_header)
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        #do the login and get the response
        response = opener.open(req)
        source = response.read()
        response.close()

        login = check_login(source)

        if login == 'free' or login == 'premium':
            cj.save(cookiepath)

        return login
    else:
        return None

def __getPremiumUrl(baseurl, cookiepath, code, login_code):

  #this method is called from __resolveURL

  log.debug("Use premium mode")
  log.debug("cookie: '%s'" % login_code)

  req = urllib2.Request(baseurl + "xml/player_login.php?u=" + login_code + "&v=" + code)
  req.add_header('User-Agent',firefox_header)
  req.add_header('Referer', baseurl+'?v='+code)
  page = urllib2.urlopen(req);XML_FILE = page.read();page.close()

  matches = re.compile('downloadurl="([^"]+)"', re.DOTALL).findall(XML_FILE)

  if len(matches) > 0:
       return [urllib.unquote_plus(matches[0])]
  else:
       return None

  
def resolveURL(baseurl, cookiepath, url):

  baseurl=setBaseURL(baseurl)

  #get the code from a url, unless only code is supplied.
  l = len(url)
  if(l > 8):
     code = url[l-8 : l]
  else:
     code = url

  #if user supplies path to cookie, get the login data from it and use it to form the xml_url.
  if cookiepath is not None:
    login_code = (re.compile('user="(.+?)"').findall(openfile(cookiepath)))[0]

    log.debug("get with cookie: '%s'" % login_code)
    xml_url = baseurl + "xml/videolink.php?u=" + login_code + "&v=" + code

  else:
    log.debug("get without cookie")
    xml_url = baseurl + "xml/videolink.php?v=" + code

  #get the XML_FILE from the url.
  req = urllib2.Request(xml_url)
  req.add_header('User-Agent',firefox_header)
  req.add_header('Referer', baseurl+'?v='+code)
  page = urllib2.urlopen(req);XML_FILE = page.read();page.close()

  #check that the link is valid
  if is_online(baseurl, XML_FILE = XML_FILE) == True:

       #try getting the Original File url. (requires premium). Returns None if you are a non-premium user.
       if cookiepath is not None: Original_File = __getPremiumUrl(baseurl, cookiepath, code, login_code)
       else: Original_File = None
       
       #Initialize the decryptor.
       decrypter = Megavideo_Decrypt(XML_FILE)

       #Create the FLV url.
       FLV_File = "http://www" + str(getServer(XML_FILE)) + baseurl[10:25] + "files/" + str(decrypter.getDecrypted()) + "/stream.flv"

       #Fix the FLV url if it is a porn url
       FLV_File = re.sub('vfiles', 'files', FLV_File)
       
       #Get some metadata from the XML_FILE
       title = getTitle(XML_FILE)
       description = getDescription(XML_FILE)
       runtime = getRuntime(XML_FILE)
  
       return FLV_File,Original_File,title,description,runtime

  else:
       return None




def is_online(baseurl,url=False,XML_FILE=False):

     baseurl=setBaseURL(baseurl)
       
     if XML_FILE == False:
          #get the code from a url, unless only code is supplied.
          l = len(url)
          if(l > 8):
              code = url[l-8 : l]
          else:
              code = url
          XML_FILE = GetURL(baseurl + "xml/videolink.php?v=" + code)
              
     try: error = re.findall('errortext="(.+?)"',XML_FILE,re.I)[0]
     except: return True
     else:
         if len(error)>0:
             print "ERROR: " + str(error)
             return False
         else:
             return True

def getServer(XML_FILE):
     try: server = re.findall('s="([0-9]+)"',XML_FILE,re.I)[0]
     except: return None
     else: return str(server)

def getTitle(XML_FILE):
     try: title = re.findall('title="(.+?)"',XML_FILE,re.I)[0]
     except: return None
     else: return str(urllib.unquote_plus(title))

def getDescription(XML_FILE):
     try: description = re.findall('description="(.+?)"',XML_FILE,re.I)[0]
     except: return None
     else: return str(urllib.unquote_plus(description))

def getRuntime(XML_FILE):
     try: runtime = re.findall('runtimehms="(.+?)"',XML_FILE,re.I)[0].replace("+"," ")
     except: return None
     else: return str(runtime)

def GetURL(url):
     req = urllib2.Request(url)
     req.add_header('User-Agent', firefox_header)       
     response = urllib2.urlopen(req)
     link=response.read()
     response.close()
     return link
     
class Megavideo_Decrypt:
	def __init__(self,XML_FILE):
		self.XML_FILE = XML_FILE
		self.setKeys()

		tobin = self.hex2bin(self.un)
		keys = []
		index = 0

		while (index < 384):
			self.k1 = ((int(self.k1) * 11) + 77213) % 81371
			self.k2 = ((int(self.k2) * 17) + 92717) % 192811
			keys.append((int(self.k1) + int(self.k2)) % 128)
			index += 1

		index = 256

		while (index >= 0):
			val1 = keys[index]
			mod  = index%128
			val2 = tobin[val1]
			tobin[val1] = tobin[mod]
			tobin[mod] = val2
			index -= 1

		index = 0
		while(index<128):
			tobin[index] = int(tobin[index]) ^ int(keys[index+256]) & 1
			index += 1

		self.decrypted = self.bin2hex(tobin)

	def setKeys(self):
		self.k1 = re.findall('k1="([0-9]+)"',self.XML_FILE,re.I)[0].replace("+"," ")
		self.k2 = re.findall('k2="([0-9]+)"',self.XML_FILE,re.I)[0].replace("+"," ")
		self.un = re.findall('un="(.+?)"',self.XML_FILE,re.I)[0].replace("+"," ")

	def getDecrypted(self):
		return str(self.decrypted)

	def hex2bin(self,val):
		bin_array = []
		string =  bin_function(int(val, 16))[2:].zfill(128)
		for value in string:
			bin_array.append(value)
		return bin_array

	def bin2hex(self,val):
		string = str("")
		for char in val:
			string+=str(char)
		return "%x" % int(string, 2)
