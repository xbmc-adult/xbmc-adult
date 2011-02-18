# -*- coding: UTF-8 -*-

"""
 Support for megavideo links.
 
 This link resolver supports the following configuration:
  - megavideouser: the user to authenticate with megavideo servers
  - megavideopassword: the password to authenticate the provided user
  - megavideopremium: if the high quality download links should be used
  
 If both username and password are set, this resolver will use the credentials
 and try to login to megavideo to get the user cookie.
 
 If the megavideopremium option is set, the resolver will return the download
 link from megavideo which links to the original file (best quality)
 
 This code is based on work from Voinage and Coolblaze.
 
 @author: Pedro Guedes guedes.emigra@gmail.com
"""
import os, re, urllib2, logging, string
#import utils.settings as settings


COOKIEFILE = os.path.join(os.getcwd(), 'cookies.lwp')

log = logging.getLogger("megavideo")
log.info("Cookiefile: %s" % COOKIEFILE)

def resolve(page):
  #mega = re.compile('<param name="movie" value="http://video.megarotic.com/v/(.+?)">').findall(page)
 # mega[0] = mega[0][0:8]
  mega = page
  megavideoUrl = __getUrl(mega)
  return megavideoUrl

def __doLogin():
  """If the megavideo username and password parameters are set, will authenticate with
  megavideo and return the user cookie that megavideo uses to track logged in users"""
 # megavideologin = settings.get("megavideouser")
 # log.debug("Authenticating on Megavideo with username: '%r'" % megavideologin)
#  megavideopassword = settings.get("megavideopassword")
#  if megavideologin and megavideopassword:
  #return __getMegavideoUserCookie(megavideologin, megavideopassword)
  
  return None

def __calcDecriptionMix(hash, keyMix):
  """Mixes the decription keys into the hash and returns the updated hash
  @param hash: the hash to merge the keys into
  @param keyMix: the array of keys to mix"""
  for i in range(128):
    hash[i] = str(int(hash[i]) ^ int(keyMix[i + 256]) & 1)
  return "".join(hash)

def __toHexDecriptionString(binaryChunks):
  """Converts an array of binary strings into a string of the corresponding hex chunks merged
  This method will first loop through the binary strings converting each one into it's correspondent
  hexadecimal string and then merge the resulting array into a string
  @param binaryChunks: an array of binary strings
  @return: a string of the corresponding hexadecimal strings, merged"""
  hexChunks = []
  for binChunk in binaryChunks:
    hexChunks.append("%x" % int(binChunk, 2))    
  return "".join(hexChunks)

def __doDecriptionChunks(binaryMergedString):
  """Break a string of 0's and 1's in pieces of 4 chars
  @param binaryMergedString: a string of 0's and 1's to break in 4-part pieces
  @return: an array of 4 character parts of the original string"""
  binaryChunks = []
  for index in range(0, len(binaryMergedString), 4):
    binaryChunk = binaryMergedString[index:index + 4]
    binaryChunks.append(binaryChunk)
  return binaryChunks

def __doDecriptionSwaps(hash, keys):
  """Swap the first 256 indices from keys on the hash with the last 128 elements from the hash
  @param hash: the hash to do swaps on
  @param keys: the generated keys to use as indices for the swaps
  @return: hash after swaps"""
  for index in range(256, 0, -1):
    key = keys[index]
    swapTarget = index % 128
    oldHashKey = hash[key]
    hash[key] = hash[swapTarget]
    hash[swapTarget] = oldHashKey
  return hash

def __computeIndices(key1, key2):
  """Generate an array of 384 indices with values 0-127
  @param key1: first seed to generate indices from
  @param key2: second seed to generate indices from
  @return: an array of 384 indices with values between 0 and 127"""
  indices = []
  for i in range(384):
    key1 = (int(key1) * 11 + 77213) % 81371
    key2 = (int(key2) * 17 + 92717) % 192811
    indices.append((int(key1) + int(key2)) % 128)
  return indices

def __explodeBin(str1):
  # explode each char in str1 into it;s binary representation
  # and collect the result into __reg1
  __reg1 = []
  __reg3 = 0
  while (__reg3 < len(str1)):
    __reg0 = str1[__reg3]
    holder = __reg0
    if (holder == "0"):
      __reg1.append("0000")
    else:
      if (__reg0 == "1"):
        __reg1.append("0001")
      else:
        if (__reg0 == "2"): 
          __reg1.append("0010")
        else: 
          if (__reg0 == "3"):
            __reg1.append("0011")
          else: 
            if (__reg0 == "4"):
              __reg1.append("0100")
            else: 
              if (__reg0 == "5"):
                __reg1.append("0101")
              else: 
                if (__reg0 == "6"):
                  __reg1.append("0110")
                else: 
                  if (__reg0 == "7"):
                    __reg1.append("0111")
                  else: 
                    if (__reg0 == "8"):
                      __reg1.append("1000")
                    else: 
                      if (__reg0 == "9"):
                        __reg1.append("1001")
                      else: 
                        if (__reg0 == "a"):
                          __reg1.append("1010")
                        else: 
                          if (__reg0 == "b"):
                            __reg1.append("1011")
                          else: 
                            if (__reg0 == "c"):
                              __reg1.append("1100")
                            else: 
                              if (__reg0 == "d"):
                                __reg1.append("1101")
                              else: 
                                if (__reg0 == "e"):
                                  __reg1.append("1110")
                                else: 
                                  if (__reg0 == "f"):
                                    __reg1.append("1111")

    __reg3 = __reg3 + 1
  return list("".join(__reg1))
    
def __calculateFileHash(str1, key1, key2):
  # explode hex to bin strings, collapse to a string and return char array
  hash = __explodeBin(str1)
  # based on the keys, generate an array of 384 (256 + 128) values
  decriptIndices = __computeIndices(key1, key2)
  # from 256 to 0, swap hash[decriptIndices[x]] with hash[__reg3 % 128]
  hash = __doDecriptionSwaps(hash, decriptIndices)
  # replace the first 128 chars in hash with the formula:
  #  hash[x] = hash[x] * decriptIndices[x+256] & 1
  hash = __calcDecriptionMix(hash, decriptIndices)
  # split __reg12 in chunks of 4 chars
  chunks = __doDecriptionChunks(hash)  
  # convert each binary chunk to a hex string for the final hash
  return __toHexDecriptionString(chunks)

def __getUrl(mega):
  megavideocookie = __doLogin()
#  if settings.isSet("megavideopremium"):
#    return __getPremiumUrl(mega, megavideocookie)
#  else:
  mega = string.split(mega, "v=")[1]
  return __getPublicUrl(mega, megavideocookie)
  
def __getPremiumUrl(code, megavideocookie):
  log.debug("Use premium mode")
  log.debug("Megavideo cookie: '%s'" % megavideocookie)
  req = urllib2.Request("http://www.megavideo.com/xml/player_login.php?u=" + megavideocookie + "&v=" + code)
  req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
  patronvideos = 'downloadurl="([^"]+)"'
  matches = re.compile(patronvideos, re.DOTALL).findall(urllib2.urlopen(req).read())
  return matches[0].replace("%3A", ":").replace("%2F", "/").replace("%20", " ")
  
def __getPublicUrl(code, megavideocookie):
  log.debug("Use normal mode")
  url = "http://www.megaporn.com/video/xml/videolink.php?v=" + code
#  print url
  if megavideocookie:
    print "Megavideo cookie: '%s'" % megavideocookie
    url = "http://www.megaporn.com/video/xml/videolink.php?u="+megavideocookie+"&v=" + code
    print url
  req = urllib2.Request(url)
  req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
  req.add_header('Referer', 'http://www.megavideo.com/')
  page = urllib2.urlopen(req);response = page.read();page.close()
  errort = re.compile(' errortext="(.+?)"').findall(response)
#  print "testing"
  if len(errort) <= 0:
    s = re.compile(' s="(.+?)"').findall(response)
    k1 = re.compile(' k1="(.+?)"').findall(response)
    k2 = re.compile(' k2="(.+?)"').findall(response)
    un = re.compile(' un="(.+?)"').findall(response)
    return "http://www" + s[0] + ".megaporn.com/files/" + __calculateFileHash(un[0], k1[0], k2[0]) + "/"
  
def __getMegavideoUserCookie(login, password):
  log.debug("getMegavideoUserCookie")
  ficherocookies = COOKIEFILE
  cj = None
  ClientCookie = None
  cookielib = None

  try:
    import cookielib
  except ImportError:
    try:
      import ClientCookie
    except ImportError:
      urlopen = urllib2.urlopen
      Request = urllib2.Request
    else:
      urlopen = ClientCookie.urlopen
      Request = ClientCookie.Request
      cj = ClientCookie.LWPCookieJar()
  else:
    urlopen = urllib2.urlopen
    Request = urllib2.Request
    cj = cookielib.LWPCookieJar()

  if cj is not None:
    if os.path.isfile(ficherocookies):
      cj.load(ficherocookies)

    if cookielib is not None:
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      urllib2.install_opener(opener)

    else:
      opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
      ClientCookie.install_opener(opener)

  url = "http://www.megavideo.com/?s=signup"
  theurl = url
  # an example url that sets a cookie,
  # try different urls here and see the cookie collection you can make !
  txdata = "action=login&cnext=&snext=&touser=&user=&nickname=" + login + "&password=" + password
  txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
          'Referer':'http://www.megavideo.com/?s=signup'}
  req = Request(theurl, txdata, txheaders)
  handle = urlopen(req)
  cj.save(ficherocookies)                     # save the cookies again    

  handle.read()
  data = handle.read()
  log.debug("----------------------")
  log.debug("Respuesta de getUrl")
  log.debug("----------------------")
  log.debug(data)
  log.debug("----------------------")
  handle.close()

  cookiedatafile = open(ficherocookies, 'r')
  cookiedata = cookiedatafile.read()
  cookiedatafile.close();

  log.debug("----------------------")
  log.debug("Cookies despues")
  log.debug("----------------------")
  log.debug(cookiedata)
  log.debug("----------------------")

  patronvideos = 'user="([^"]+)"'
  matches = re.compile(patronvideos, re.DOTALL).findall(cookiedata)
  if len(matches) == 0:
    patronvideos = 'user=([^\;]+);'
    matches = re.compile(patronvideos, re.DOTALL).findall(cookiedata)
    
  return matches[0]
