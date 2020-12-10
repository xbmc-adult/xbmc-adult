# -*- coding: UTF-8 -*-

"""
 weblogin
 by Anarchintosh @ xbmcforums
 Copyleft (GNU GPL v3) 2011 onwards

 this example is configured for Fantasti.cc login
 See for the full guide please visit:
 http://forum.xbmc.org/showthread.php?p=772597#post772597


 USAGE:
 in your default.py put:

 import weblogin
 logged_in = weblogin.doLogin('a-path-to-save-the-cookie-to',
                              'the-username', 'the-password')

 logged_in will then be either True or False depending on whether the login was
 successful.
"""


import os
from six.moves import urllib_request, urllib_parse, urllib_error, http_cookiejar
import json

# TESTING SETTINGS (will only be used when running this file independent of
# your addon)
# Remember to clear these after you are finished testing,
# so that your sensitive details are not in your source code.
# These are only used in the:  if __name__ == "__main__"   thing at the bottom
# of this script.
myusername = ''
mypassword = ''
# note, the cookie will be saved to the same directory as weblogin.py when testing


def check_login(source, username):
    js_data = json.loads(source)
    # search for the string in the reply, without caring about upper or lower case
    if js_data.get('status') == 'ok' and \
       js_data.get('data').get('userName').lower() == username.lower():
        return (True, js_data.get('data').get('avatar'))
    return (False, None)


def doLogin(cookiepath, username, password):

    # check if user has supplied only a folder path, or a full path
    if not os.path.isfile(cookiepath):
        # if the user supplied only a folder path, append on to the end of the
        # path a filename.
        cookiepath = os.path.join(cookiepath, 'cookies.lwp')

    # delete any old version of the cookie file
    try:
        os.remove(cookiepath)
    except:
        pass

    if username and password:

        # the url you will request to.
        login_url = 'https://fantasti.cc/signin.php'

        # the header used to pretend you are a browser
        header_string = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

        # build the form data necessary for the login
        login_data = urllib_parse.urlencode({'user': username,
                                             'pass': password,
                                             'memento': 1,
                                             'x': 0,
                                             'y': 0,
                                             'do': 'login',
                                             'SSO': ''
                                             })

        # build the request we will make
        req = urllib_request.Request(login_url)
        req.add_header('User-Agent', header_string)

        # initiate the cookielib class
        cj = http_cookiejar.LWPCookieJar()

        # Setup no redirects
        class NoRedirection(urllib_request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        # install cookielib into the url opener, so that cookies are handled
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj), NoRedirection())
        urllib_request.install_opener(opener)
        # do the login and get the response

        try:
            source = urllib_request.urlopen(req, login_data.encode()).read()
        except urllib_error.HTTPError as e:
            source = e.read()

        # check the received html for a string that will tell us if the user is
        # logged in
        # pass the username, which can be used to do this.
        login, avatar = check_login(source, username)

        # if login suceeded, save the cookiejar to disk
        if login:
            cj.save(cookiepath)

        # return whether we are logged in or not
        return (login, avatar)

    else:
        return (False, False)


# code to enable running the .py independent of addon for testing
if __name__ == "__main__":
    if myusername == '' or mypassword == '':
        print('YOU HAVE NOT SET THE USERNAME OR PASSWORD!')
    else:
        logged_in = doLogin(os.getcwd(), myusername, mypassword)
        print('LOGGED IN:', logged_in)
