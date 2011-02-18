from string import *
import xbmcplugin, xbmcaddon
import sys, os.path
import urllib,urllib2, filecmp
import re, random, string, shutil
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import cookielib, htmlentitydefs
import socket, base64

addon = xbmcaddon.Addon(id='plugin.video.videodevil')
__language__ = addon.getLocalizedString
rootDir = addon.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)
settingsDir = addon.getAddonInfo('profile')
settingsDir = xbmc.translatePath(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')
#socket.setdefaulttimeout(20)

urlopen = urllib2.urlopen
cj = cookielib.LWPCookieJar()
Request = urllib2.Request

if cj != None:
    if os.path.isfile(xbmc.translatePath(os.path.join(settingsDir, 'cookies.lwp'))):
        cj.load(xbmc.translatePath(os.path.join(settingsDir, 'cookies.lwp')))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
else:
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)

if addon.getSetting('enable_debug') == 'true':
    enable_debug = True
    xbmc.output('VideoDevil debug logging enabled')
else:
    enable_debug = False

entitydefs = {
    'AElig':    u'\u00C6', # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1'
    'Aacute':   u'\u00C1', # latin capital letter A with acute, U+00C1 ISOlat1'
    'Acirc':    u'\u00C2', # latin capital letter A with circumflex, U+00C2 ISOlat1'
    'Agrave':   u'\u00C0', # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1'
    'Alpha':    u'\u0391', # greek capital letter alpha, U+0391'
    'Aring':    u'\u00C5', # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1'
    'Atilde':   u'\u00C3', # latin capital letter A with tilde, U+00C3 ISOlat1'
    'Auml':     u'\u00C4', # latin capital letter A with diaeresis, U+00C4 ISOlat1'
    'Beta':     u'\u0392', # greek capital letter beta, U+0392'
    'Ccedil':   u'\u00C7', # latin capital letter C with cedilla, U+00C7 ISOlat1'
    'Chi':      u'\u03A7', # greek capital letter chi, U+03A7'
    'Dagger':   u'\u2021', # double dagger, U+2021 ISOpub'
    'Delta':    u'\u0394', # greek capital letter delta, U+0394 ISOgrk3'
    'ETH':      u'\u00D0', # latin capital letter ETH, U+00D0 ISOlat1'
    'Eacute':   u'\u00C9', # latin capital letter E with acute, U+00C9 ISOlat1'
    'Ecirc':    u'\u00CA', # latin capital letter E with circumflex, U+00CA ISOlat1'
    'Egrave':   u'\u00C8', # latin capital letter E with grave, U+00C8 ISOlat1'
    'Epsilon':  u'\u0395', # grek capital letter epsilon, U+0395'
    'Eta':      u'\u0397', # greek capital letter eta, U+0397'
    'Euml':     u'\u00CB', # latin capital letter E with diaeresis, U+00CB ISOlat1'
    'Gamma':    u'\u0393', # greek capital letter gamma, U+0393 ISOgrk3'
    'Iacute':   u'\u00CD', # latin capital letter I with acute, U+00CD ISOlat1'
    'Icirc':    u'\u00CE', # latin capital letter I with circumflex, U+00CE ISOlat1'
    'Igrave':   u'\u00CC', # latin capital letter I with grave, U+00CC ISOlat1'
    'Iota':     u'\u0399', # greek capital letter iota, U+0399'
    'Iuml':     u'\u00CF', # latin capital letter I with diaeresis, U+00CF ISOlat1'
    'Kappa':    u'\u039A', # greek capital letter kappa, U+039A'
    'Lambda':   u'\u039B', # greek capital letter lambda, U+039B ISOgrk3'
    'Mu':       u'\u039C', # greek capital letter mu, U+039C'
    'Ntilde':   u'\u00D1', # latin capital letter N with tilde, U+00D1 ISOlat1'
    'Nu':       u'\u039D', # greek capital letter nu, U+039D'
    'OElig':    u'\u0152', # latin capital ligature OE, U+0152 ISOlat2'
    'Oacute':   u'\u00D3', # latin capital letter O with acute, U+00D3 ISOlat1'
    'Ocirc':    u'\u00D4', # latin capital letter O with circumflex, U+00D4 ISOlat1'
    'Ograve':   u'\u00D2', # latin capital letter O with grave, U+00D2 ISOlat1'
    'Omega':    u'\u03A9', # greek capital letter omega, U+03A9 ISOgrk3'
    'Omicron':  u'\u039F', # greek capital letter omicron, U+039F'
    'Oslash':   u'\u00D8', # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1'
    'Otilde':   u'\u00D5', # latin capital letter O with tilde, U+00D5 ISOlat1'
    'Ouml':     u'\u00D6', # latin capital letter O with diaeresis, U+00D6 ISOlat1'
    'Phi':      u'\u03A6', # greek capital letter phi, U+03A6 ISOgrk3'
    'Pi':       u'\u03A0', # greek capital letter pi, U+03A0 ISOgrk3'
    'Prime':    u'\u2033', # double prime = seconds = inches, U+2033 ISOtech'
    'Psi':      u'\u03A8', # greek capital letter psi, U+03A8 ISOgrk3'
    'Rho':      u'\u03A1', # greek capital letter rho, U+03A1'
    'Scaron':   u'\u0160', # latin capital letter S with caron, U+0160 ISOlat2'
    'Sigma':    u'\u03A3', # greek capital letter sigma, U+03A3 ISOgrk3'
    'THORN':    u'\u00DE', # latin capital letter THORN, U+00DE ISOlat1'
    'Tau':      u'\u03A4', # greek capital letter tau, U+03A4'
    'Theta':    u'\u0398', # greek capital letter theta, U+0398 ISOgrk3'
    'Uacute':   u'\u00DA', # latin capital letter U with acute, U+00DA ISOlat1'
    'Ucirc':    u'\u00DB', # latin capital letter U with circumflex, U+00DB ISOlat1'
    'Ugrave':   u'\u00D9', # latin capital letter U with grave, U+00D9 ISOlat1'
    'Upsilon':  u'\u03A5', # greek capital letter upsilon, U+03A5 ISOgrk3'
    'Uuml':     u'\u00DC', # latin capital letter U with diaeresis, U+00DC ISOlat1'
    'Xi':       u'\u039E', # greek capital letter xi, U+039E ISOgrk3'
    'Yacute':   u'\u00DD', # latin capital letter Y with acute, U+00DD ISOlat1'
    'Yuml':     u'\u0178', # latin capital letter Y with diaeresis, U+0178 ISOlat2'
    'Zeta':     u'\u0396', # greek capital letter zeta, U+0396'
    'aacute':   u'\u00E1', # latin small letter a with acute, U+00E1 ISOlat1'
    'acirc':    u'\u00E2', # latin small letter a with circumflex, U+00E2 ISOlat1'
    'acute':    u'\u00B4', # acute accent = spacing acute, U+00B4 ISOdia'
    'aelig':    u'\u00E6', # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1'
    'agrave':   u'\u00E0', # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1'
    'alefsym':  u'\u2135', # alef symbol = first transfinite cardinal, U+2135 NEW'
    'alpha':    u'\u03B1', # greek small letter alpha, U+03B1 ISOgrk3'
    'amp':      u'\u0026', # ampersand, U+0026 ISOnum'
    'and':      u'\u2227', # logical and = wedge, U+2227 ISOtech'
    'ang':      u'\u2220', # angle, U+2220 ISOamso'
    'aring':    u'\u00E5', # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1'
    'asymp':    u'\u2248', # almost equal to = asymptotic to, U+2248 ISOamsr'
    'atilde':   u'\u00E3', # latin small letter a with tilde, U+00E3 ISOlat1'
    'auml':     u'\u00E4', # latin small letter a with diaeresis, U+00E4 ISOlat1'
    'bdquo':    u'\u201E', # double low-9 quotation mark, U+201E NEW'
    'beta':     u'\u03B2', # greek small letter beta, U+03B2 ISOgrk3'
    'brvbar':   u'\u00A6', # broken bar = broken vertical bar, U+00A6 ISOnum'
    'bull':     u'\u2022', # bullet = black small circle, U+2022 ISOpub'
    'cap':      u'\u2229', # intersection = cap, U+2229 ISOtech'
    'ccedil':   u'\u00E7', # latin small letter c with cedilla, U+00E7 ISOlat1'
    'cedil':    u'\u00B8', # cedilla = spacing cedilla, U+00B8 ISOdia'
    'cent':     u'\u00A2', # cent sign, U+00A2 ISOnum'
    'chi':      u'\u03C7', # greek small letter chi, U+03C7 ISOgrk3'
    'circ':     u'\u02C6', # modifier letter circumflex accent, U+02C6 ISOpub'
    'clubs':    u'\u2663', # black club suit = shamrock, U+2663 ISOpub'
    'cong':     u'\u2245', # approximately equal to, U+2245 ISOtech'
    'copy':     u'\u00A9', # copyright sign, U+00A9 ISOnum'
    'crarr':    u'\u21B5', # downwards arrow with corner leftwards = carriage return, U+21B5 NEW'
    'cup':      u'\u222A', # union = cup, U+222A ISOtech'
    'curren':   u'\u00A4', # currency sign, U+00A4 ISOnum'
    'dArr':     u'\u21D3', # downwards double arrow, U+21D3 ISOamsa'
    'dagger':   u'\u2020', # dagger, U+2020 ISOpub'
    'darr':     u'\u2193', # downwards arrow, U+2193 ISOnum'
    'deg':      u'\u00B0', # degree sign, U+00B0 ISOnum'
    'delta':    u'\u03B4', # greek small letter delta, U+03B4 ISOgrk3'
    'diams':    u'\u2666', # black diamond suit, U+2666 ISOpub'
    'divide':   u'\u00F7', # division sign, U+00F7 ISOnum'
    'eacute':   u'\u00E9', # latin small letter e with acute, U+00E9 ISOlat1'
    'ecirc':    u'\u00EA', # latin small letter e with circumflex, U+00EA ISOlat1'
    'egrave':   u'\u00E8', # latin small letter e with grave, U+00E8 ISOlat1'
    'empty':    u'\u2205', # empty set = null set = diameter, U+2205 ISOamso'
    'emsp':     u'\u2003', # em space, U+2003 ISOpub'
    'ensp':     u'\u2002', # en space, U+2002 ISOpub'
    'epsilon':  u'\u03B5', # greek small letter epsilon, U+03B5 ISOgrk3'
    'equiv':    u'\u2261', # identical to, U+2261 ISOtech'
    'eta':      u'\u03B7', # greek small letter eta, U+03B7 ISOgrk3'
    'eth':      u'\u00F0', # latin small letter eth, U+00F0 ISOlat1'
    'euml':     u'\u00EB', # latin small letter e with diaeresis, U+00EB ISOlat1'
    'euro':     u'\u20AC', # euro sign, U+20AC NEW'
    'exist':    u'\u2203', # there exists, U+2203 ISOtech'
    'fnof':     u'\u0192', # latin small f with hook = function = florin, U+0192 ISOtech'
    'forall':   u'\u2200', # for all, U+2200 ISOtech'
    'frac12':   u'\u00BD', # vulgar fraction one half = fraction one half, U+00BD ISOnum'
    'frac14':   u'\u00BC', # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum'
    'frac34':   u'\u00BE', # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum'
    'frasl':    u'\u2044', # fraction slash, U+2044 NEW'
    'gamma':    u'\u03B3', # greek small letter gamma, U+03B3 ISOgrk3'
    'ge':       u'\u2265', # greater-than or equal to, U+2265 ISOtech'
    'gt':       u'\u003E', # greater-than sign, U+003E ISOnum'
    'hArr':     u'\u21D4', # left right double arrow, U+21D4 ISOamsa'
    'harr':     u'\u2194', # left right arrow, U+2194 ISOamsa'
    'hearts':   u'\u2665', # black heart suit = valentine, U+2665 ISOpub'
    'hellip':   u'\u2026', # horizontal ellipsis = three dot leader, U+2026 ISOpub'
    'iacute':   u'\u00ED', # latin small letter i with acute, U+00ED ISOlat1'
    'icirc':    u'\u00EE', # latin small letter i with circumflex, U+00EE ISOlat1'
    'iexcl':    u'\u00A1', # inverted exclamation mark, U+00A1 ISOnum'
    'igrave':   u'\u00EC', # latin small letter i with grave, U+00EC ISOlat1'
    'image':    u'\u2111', # blackletter capital I = imaginary part, U+2111 ISOamso'
    'infin':    u'\u221E', # infinity, U+221E ISOtech'
    'int':      u'\u222B', # integral, U+222B ISOtech'
    'iota':     u'\u03B9', # greek small letter iota, U+03B9 ISOgrk3'
    'iquest':   u'\u00BF', # inverted question mark = turned question mark, U+00BF ISOnum'
    'isin':     u'\u2208', # element of, U+2208 ISOtech'
    'iuml':     u'\u00EF', # latin small letter i with diaeresis, U+00EF ISOlat1'
    'kappa':    u'\u03BA', # greek small letter kappa, U+03BA ISOgrk3'
    'lArr':     u'\u21D0', # leftwards double arrow, U+21D0 ISOtech'
    'lambda':   u'\u03BB', # greek small letter lambda, U+03BB ISOgrk3'
    'lang':     u'\u2329', # left-pointing angle bracket = bra, U+2329 ISOtech'
    'laquo':    u'\u00AB', # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum'
    'larr':     u'\u2190', # leftwards arrow, U+2190 ISOnum'
    'lceil':    u'\u2308', # left ceiling = apl upstile, U+2308 ISOamsc'
    'ldquo':    u'\u201C', # left double quotation mark, U+201C ISOnum'
    'le':       u'\u2264', # less-than or equal to, U+2264 ISOtech'
    'lfloor':   u'\u230A', # left floor = apl downstile, U+230A ISOamsc'
    'lowast':   u'\u2217', # asterisk operator, U+2217 ISOtech'
    'loz':      u'\u25CA', # lozenge, U+25CA ISOpub'
    'lrm':      u'\u200E', # left-to-right mark, U+200E NEW RFC 2070'
    'lsaquo':   u'\u2039', # single left-pointing angle quotation mark, U+2039 ISO proposed'
    'lsquo':    u'\u2018', # left single quotation mark, U+2018 ISOnum'
    'lt':       u'\u003C', # less-than sign, U+003C ISOnum'
    'macr':     u'\u00AF', # macron = spacing macron = overline = APL overbar, U+00AF ISOdia'
    'mdash':    u'\u2014', # em dash, U+2014 ISOpub'
    'micro':    u'\u00B5', # micro sign, U+00B5 ISOnum'
    'middot':   u'\u00B7', # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum'
    'minus':    u'\u2212', # minus sign, U+2212 ISOtech'
    'mu':       u'\u03BC', # greek small letter mu, U+03BC ISOgrk3'
    'nabla':    u'\u2207', # nabla = backward difference, U+2207 ISOtech'
    'nbsp':     u'\u00A0', # no-break space = non-breaking space, U+00A0 ISOnum'
    'ndash':    u'\u2013', # en dash, U+2013 ISOpub'
    'ne':       u'\u2260', # not equal to, U+2260 ISOtech'
    'ni':       u'\u220B', # contains as member, U+220B ISOtech'
    'not':      u'\u00AC', # not sign, U+00AC ISOnum'
    'notin':    u'\u2209', # not an element of, U+2209 ISOtech'
    'nsub':     u'\u2284', # not a subset of, U+2284 ISOamsn'
    'ntilde':   u'\u00F1', # latin small letter n with tilde, U+00F1 ISOlat1'
    'nu':       u'\u03BD', # greek small letter nu, U+03BD ISOgrk3'
    'oacute':   u'\u00F3', # latin small letter o with acute, U+00F3 ISOlat1'
    'ocirc':    u'\u00F4', # latin small letter o with circumflex, U+00F4 ISOlat1'
    'oelig':    u'\u0153', # latin small ligature oe, U+0153 ISOlat2'
    'ograve':   u'\u00F2', # latin small letter o with grave, U+00F2 ISOlat1'
    'oline':    u'\u203E', # overline = spacing overscore, U+203E NEW'
    'omega':    u'\u03C9', # greek small letter omega, U+03C9 ISOgrk3'
    'omicron':  u'\u03BF', # greek small letter omicron, U+03BF NEW'
    'oplus':    u'\u2295', # circled plus = direct sum, U+2295 ISOamsb'
    'or':       u'\u2228', # logical or = vee, U+2228 ISOtech'
    'ordf':     u'\u00AA', # feminine ordinal indicator, U+00AA ISOnum'
    'ordm':     u'\u00BA', # masculine ordinal indicator, U+00BA ISOnum'
    'oslash':   u'\u00F8', # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1'
    'otilde':   u'\u00F5', # latin small letter o with tilde, U+00F5 ISOlat1'
    'otimes':   u'\u2297', # circled times = vector product, U+2297 ISOamsb'
    'ouml':     u'\u00F6', # latin small letter o with diaeresis, U+00F6 ISOlat1'
    'para':     u'\u00B6', # pilcrow sign = paragraph sign, U+00B6 ISOnum'
    'part':     u'\u2202', # partial differential, U+2202 ISOtech'
    'permil':   u'\u2030', # per mille sign, U+2030 ISOtech'
    'perp':     u'\u22A5', # up tack = orthogonal to = perpendicular, U+22A5 ISOtech'
    'phi':      u'\u03C6', # greek small letter phi, U+03C6 ISOgrk3'
    'pi':       u'\u03C0', # greek small letter pi, U+03C0 ISOgrk3'
    'piv':      u'\u03D6', # greek pi symbol, U+03D6 ISOgrk3'
    'plusmn':   u'\u00B1', # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum'
    'pound':    u'\u00A3', # pound sign, U+00A3 ISOnum'
    'prime':    u'\u2032', # prime = minutes = feet, U+2032 ISOtech'
    'prod':     u'\u220F', # n-ary product = product sign, U+220F ISOamsb'
    'prop':     u'\u221D', # proportional to, U+221D ISOtech'
    'psi':      u'\u03C8', # greek small letter psi, U+03C8 ISOgrk3'
    'quot':     u'\u0022', # quotation mark = APL quote, U+0022 ISOnum'
    'rArr':     u'\u21D2', # rightwards double arrow, U+21D2 ISOtech'
    'radic':    u'\u221A', # square root = radical sign, U+221A ISOtech'
    'rang':     u'\u232A', # right-pointing angle bracket = ket, U+232A ISOtech'
    'raquo':    u'\u00BB', # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum'
    'rarr':     u'\u2192', # rightwards arrow, U+2192 ISOnum'
    'rceil':    u'\u2309', # right ceiling, U+2309 ISOamsc'
    'rdquo':    u'\u201D', # right double quotation mark, U+201D ISOnum'
    'real':     u'\u211C', # blackletter capital R = real part symbol, U+211C ISOamso'
    'reg':      u'\u00AE', # registered sign = registered trade mark sign, U+00AE ISOnum'
    'rfloor':   u'\u230B', # right floor, U+230B ISOamsc'
    'rho':      u'\u03C1', # greek small letter rho, U+03C1 ISOgrk3'
    'rlm':      u'\u200F', # right-to-left mark, U+200F NEW RFC 2070'
    'rsaquo':   u'\u203A', # single right-pointing angle quotation mark, U+203A ISO proposed'
    'rsquo':    u'\u2019', # right single quotation mark, U+2019 ISOnum'
    'sbquo':    u'\u201A', # single low-9 quotation mark, U+201A NEW'
    'scaron':   u'\u0161', # latin small letter s with caron, U+0161 ISOlat2'
    'sdot':     u'\u22C5', # dot operator, U+22C5 ISOamsb'
    'sect':     u'\u00A7', # section sign, U+00A7 ISOnum'
    'shy':      u'\u00AD', # soft hyphen = discretionary hyphen, U+00AD ISOnum'
    'sigma':    u'\u03C3', # greek small letter sigma, U+03C3 ISOgrk3'
    'sigmaf':   u'\u03C2', # greek small letter final sigma, U+03C2 ISOgrk3'
    'sim':      u'\u223C', # tilde operator = varies with = similar to, U+223C ISOtech'
    'spades':   u'\u2660', # black spade suit, U+2660 ISOpub'
    'sub':      u'\u2282', # subset of, U+2282 ISOtech'
    'sube':     u'\u2286', # subset of or equal to, U+2286 ISOtech'
    'sum':      u'\u2211', # n-ary sumation, U+2211 ISOamsb'
    'sup':      u'\u2283', # superset of, U+2283 ISOtech'
    'sup1':     u'\u00B9', # superscript one = superscript digit one, U+00B9 ISOnum'
    'sup2':     u'\u00B2', # superscript two = superscript digit two = squared, U+00B2 ISOnum'
    'sup3':     u'\u00B3', # superscript three = superscript digit three = cubed, U+00B3 ISOnum'
    'supe':     u'\u2287', # superset of or equal to, U+2287 ISOtech'
    'szlig':    u'\u00DF', # latin small letter sharp s = ess-zed, U+00DF ISOlat1'
    'tau':      u'\u03C4', # greek small letter tau, U+03C4 ISOgrk3'
    'there4':   u'\u2234', # therefore, U+2234 ISOtech'
    'theta':    u'\u03B8', # greek small letter theta, U+03B8 ISOgrk3'
    'thetasym': u'\u03D1', # greek small letter theta symbol, U+03D1 NEW'
    'thinsp':   u'\u2009', # thin space, U+2009 ISOpub'
    'thorn':    u'\u00FE', # latin small letter thorn with, U+00FE ISOlat1'
    'tilde':    u'\u02DC', # small tilde, U+02DC ISOdia'
    'times':    u'\u00D7', # multiplication sign, U+00D7 ISOnum'
    'trade':    u'\u2122', # trade mark sign, U+2122 ISOnum'
    'uArr':     u'\u21D1', # upwards double arrow, U+21D1 ISOamsa'
    'uacute':   u'\u00FA', # latin small letter u with acute, U+00FA ISOlat1'
    'uarr':     u'\u2191', # upwards arrow, U+2191 ISOnum'
    'ucirc':    u'\u00FB', # latin small letter u with circumflex, U+00FB ISOlat1'
    'ugrave':   u'\u00F9', # latin small letter u with grave, U+00F9 ISOlat1'
    'uml':      u'\u00A8', # diaeresis = spacing diaeresis, U+00A8 ISOdia'
    'upsih':    u'\u03D2', # greek upsilon with hook symbol, U+03D2 NEW'
    'upsilon':  u'\u03C5', # greek small letter upsilon, U+03C5 ISOgrk3'
    'uuml':     u'\u00FC', # latin small letter u with diaeresis, U+00FC ISOlat1'
    'weierp':   u'\u2118', # script capital P = power set = Weierstrass p, U+2118 ISOamso'
    'xi':       u'\u03BE', # greek small letter xi, U+03BE ISOgrk3'
    'yacute':   u'\u00FD', # latin small letter y with acute, U+00FD ISOlat1'
    'yen':      u'\u00A5', # yen sign = yuan sign, U+00A5 ISOnum'
    'yuml':     u'\u00FF', # latin small letter y with diaeresis, U+00FF ISOlat1'
    'zeta':     u'\u03B6', # greek small letter zeta, U+03B6 ISOgrk3'
    'zwj':      u'\u200D', # zero width joiner, U+200D NEW RFC 2070'
    'zwnj':     u'\u200C'  # zero width non-joiner, U+200C NEW RFC 2070'
}

entitydefs2 = {
    '$':    '%24',
    '&':    '%26',
    '+':    '%2B',
    ',':    '%2C',
    '/':    '%2F',
    ':':    '%3A',
    ';':    '%3B',
    '=':    '%3D',
    '?':    '%3F',
    '@':    '%40',
    ' ':    '%20',
    '"':    '%22',
    '<':    '%3C',
    '>':    '%3E',
    '#':    '%23',
    '%':    '%25',
    '{':    '%7B',
    '}':    '%7D',
    '|':    '%7C',
    '\\':   '%5C',
    '^':    '%5E',
    '~':    '%7E',
    '[':    '%5B',
    ']':    '%5D',
    '`':    '%60'
}

entitydefs3 = {
    u'¬¡¿ƒ√≈':  u'A',
    u'‚·‡‰„Â':  u'a',
    u'‘”“÷’':   u'O',
    u'ÙÛÚˆı¯': u'o',
    u'€⁄Ÿ‹':    u'U',
    u'˚˙˘¸µ':   u'u',
    u' …»À':    u'E',
    u'ÍÈËÎ':    u'e',
    u'ŒÕÃœ':    u'I',
    u'ÓÏÌÔ':    u'i',
    u'Ò':       u'n',
    u'ﬂ':       u'B',
    u'˜':       u'%',
    u'Á':       u'c',
    u'Ê':       u'ae'
}

def clean1(s): # remove &XXX;
    if not s:
        return ''
    for name, value in entitydefs.iteritems():
        if u'&' in s:
            s = s.replace(u'&' + name + u';', value)
    return s;

def clean2(s): # remove \\uXXX
    pat = re.compile(r'\\u(....)')
    def sub(mo):
        return unichr(int(mo.group(1), 16))
    return pat.sub(sub, smart_unicode(s))

def clean3(s): # remove &#XXX;
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return decode(pat.sub(sub, smart_unicode(s)))

def decode(s):
    if not s:
        return ''
    try:
        dic=htmlentitydefs.name2codepoint
        for key in dic.keys():
            entity = '&' + key + ';'
            s = s.replace(entity, unichr(dic[key]))
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def unquote_safe(s): # unquote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(value, key)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s;

def quote_safe(s): # quote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(key, value)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s;

def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def clean_safe(s):
    if not s:
        return ''
    try:
        s = clean1(clean2(clean3(smart_unicode(s))))
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def first_clean_filename(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, '')
    return s;

def second_clean_filename(s):
    if not s:
        return ''
    for key, value in entitydefs3.iteritems():
        for c in key:
            s = s.replace(c, value)
    return s;

def third_clean_filename(s):
    if not s:
        return ''
    validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
    stripped = ''.join(c for c in s if c in validchars)
    return stripped;

class CListItem:
    def __init__(self):
        self.infos_names = []
        self.infos_values = []

class CItemInfo:
    def __init__(self):
        self.name = ''
        self.src = 'url'
        self.rule = ''
        self.default = ''
        self.build = ''

class CRuleItem:
    def __init__(self):
        self.infos = ''
        self.order = ''
        self.skill = ''
        self.curr = ''
        self.info_list = []
        self.url_build = ''

class CCatcherRuleItem:
    def __init__(self):
        self.target = ''
        self.url = ''
        self.data = ''
        self.reference = ''
        self.content = ''
        self.limit = 0
        self.action = ''
        self.build = ''

class CCatcherItem:
    def __init__(self):
        self.rule = CCatcherRuleItem()
        self.ext_rule = None
        self.match = ''
        self.info = ''
        self.extension = 'flv'
        self.quality = 'standard'

class CCurrentList:
    def __init__(self):
        self.start = ''
        self.player = ''
        self.sort = 'label'
        self.cfg = ''
        self.skill = ''
        self.reference = ''
        self.content = ''
        self.catcher = []
        self.items = []
        self.rules = []

    def getKeyboard(self, default = '', heading = '', hidden = False):
        kboard = xbmc.Keyboard(default, heading, hidden)
        kboard.doModal()
        if kboard.isConfirmed():
            return urllib.quote_plus(kboard.getText())
        return ''

    def getFileExtension(self, filename):
        ext_pos = filename.rfind('.')
        if ext_pos != -1:
            return filename[ext_pos+1:]
        else:
            return ''

    def randomFilename(self, dir = cacheDir, chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', length = 8, prefix = '', suffix = '', attempts = 10000):
        for attempt in range(attempts):
            filename = ''.join([random.choice(chars) for i in range(length)])
            filename = prefix + filename + suffix
            if not os.path.exists(os.path.join(dir, filename)):
                return filename

    def videoCount(self):
        count = 0
        for item in self.items:
            if item.infos_values[item.infos_names.index('type')] == 'video':
                count = count +1
        return count

    def getVideo(self):
        for item in self.items:
            if item.infos_values[item.infos_names.index('type')] == 'video':
                return item

    def getItemFromList(self, listname, name):
        self.loadLocal(listname, False)
        for item in self.items:
            if item.infos_values[item.infos_names.index('url')] == name:
                return item
        return None

    def itemInLocalList(self, name):
        for item in self.items:
            if item.infos_values[item.infos_names.index('url')] == name:
                return True
        return False

    def getItem(self, name):
        item = None
        for root, dirs, files in os.walk(resDir):
            for listname in files:
                if self.getFileExtension(listname) == 'list' and listname != 'catcher.list':
                    item = self.getItemFromList(listname, name)
                if item != None:
                    return item
        return None

    def addItem(self, name):
        item = self.getItem(name)
        del self.items[:]
        try:
            self.loadLocal('entry.list', False)
        except:
            del self.items[:]
        if item and not self.itemInLocalList(name):
            self.items.append(item)
            self.saveList()
        return

    def removeItem(self, name):
        item = self.getItemFromList('entry.list', name)
        if item != None:
            self.items.remove(item)
            self.saveList()
        return

    def saveList(self):
        f = open(str(os.path.join(resDir, 'entry.list')), 'w')
        f.write(smart_unicode('########################################################\n').encode('utf-8'))
        f.write(smart_unicode('#             Added sites and live streams             #\n').encode('utf-8'))
        f.write(smart_unicode('########################################################\n').encode('utf-8'))
        f.write(smart_unicode('skill=remove\n').encode('utf-8'))
        f.write(smart_unicode('########################################################\n').encode('utf-8'))
        for item in self.items:
            f.write(smart_unicode('title=' + item.infos_values[item.infos_names.index('title')] + '\n').encode('utf-8'))
            for info_name in item.infos_names:
                if info_name != 'url' and info_name != 'title':
                    f.write(smart_unicode(info_name + '=' + item.infos_values[item.infos_names.index(info_name)] + '\n').encode('utf-8'))
            f.write(smart_unicode('url=' + item.infos_values[item.infos_names.index('url')] + '\n').encode('utf-8'))
            f.write(smart_unicode('########################################################\n').encode('utf-8'))
        f.close()
        return

    def codeUrl(self, item, suffix = ''):
        url_idx = item.infos_names.index('url')
        url = ''
        info_idx = 0
        firstInfo = True
        for info_name in item.infos_names:
            if info_idx != url_idx and item.infos_names[info_idx].find('.once') == -1:
                #info_value = urllib.quote(item.infos_values[info_idx])
                info_value = item.infos_values[info_idx]
                if firstInfo:
                    firstInfo = False
                    url = smart_unicode(item.infos_names[info_idx]) + ':' + smart_unicode(info_value)
                else:
                    url = smart_unicode(url) + '&' + smart_unicode(item.infos_names[info_idx]) + ':' + smart_unicode(info_value)
            info_idx = info_idx + 1
        if firstInfo:
            url = smart_unicode(item.infos_names[url_idx]) + ':' + smart_unicode(item.infos_values[url_idx])
        else:
            url = smart_unicode(url) + '&' + smart_unicode(item.infos_names[url_idx]) + ':' + smart_unicode(urllib.quote_plus(item.infos_values[url_idx]))
        if len(suffix) > 0:
            url = url + '.' + suffix
        return url

    def decodeUrl(self, url, type = 'rss'):
        item = CListItem()
        if url.find('&') == -1:
            item.infos_names.append('url')
            item.infos_values.append(clean_safe(url))
            item.infos_names.append('type')
            item.infos_values.append(type)
            return item
        infos_names_values = url.split('&')
        for info_name_value in infos_names_values:
            sep_index = info_name_value.find(':')
            if sep_index != -1:
                item.infos_names.append(info_name_value[:sep_index])
                #item.infos_values.append(clean_safe(urllib.unquote(info_name_value[sep_index+1:])))
                item.infos_values.append(clean_safe(info_name_value[sep_index+1:]))
        try:
            type_idx = item.infos_names.index('type')
        except:
            item.infos_names.append('type')
            item.infos_values.append(type)
        return item

    def loadCatcher(self, title):
        f = open(str(os.path.join(resDir, 'catcher.list')), 'r')
        data = smart_unicode(f.read())
        data = data.replace('\r\n', '\n')
        data = data.split('\n')
        f.close()

        del self.catcher[:]
        catcher_found = False
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index])
                    value = m[index+1:]
                    if key == 'title':
                        if catcher_found:
                            return 0
                        if title == value:
                            catcher_found = True
                    elif catcher_found and key == 'target':
                        catcher_tmp = CCatcherItem()
                        catcher_tmp.rule.target = value
                    elif catcher_found and key == 'ext_target':
                        catcher_tmp.ext_rule = CCatcherRuleItem()
                        catcher_tmp.ext_rule.target = value
                    elif catcher_found and key == 'url':
                        catcher_tmp.rule.url = value
                    elif catcher_found and key == 'ext_url':
                        catcher_tmp.ext_rule.url = value
                    elif catcher_found and key == 'data':
                        catcher_tmp.rule.data = value
                    elif catcher_found and key == 'ext_data':
                        catcher_tmp.ext_rule.data = value
                    elif catcher_found and key == 'header':
                        index = value.find('|')
                        catcher_tmp.rule.reference = value[:index]
                        catcher_tmp.rule.content = value[index+1:]
                    elif catcher_found and key == 'ext_header':
                        index = value.find('|')
                        catcher_tmp.ext_rule.reference = value[:index]
                        catcher_tmp.ext_rule.content = value[index+1:]
                    elif catcher_found and key == 'build':
                        catcher_tmp.rule.build = value
                    elif catcher_found and key == 'ext_build':
                        catcher_tmp.ext_rule.build = value
                    elif catcher_found and key == 'action':
                        catcher_tmp.rule.action = value
                    elif catcher_found and key == 'ext_action':
                        catcher_tmp.ext_rule.action = value
                    elif catcher_found and key == 'limit':
                        catcher_tmp.rule.limit = int(value)
                    elif catcher_found and key == 'ext_limit':
                        catcher_tmp.ext_rule.limit = int(value)
                    elif catcher_found and key == 'extension':
                        catcher_tmp.extension = value
                    elif catcher_found and key == 'info':
                        catcher_tmp.info = value
                    elif catcher_found and key == 'quality':
                        catcher_tmp.quality = value
                        self.catcher.append(catcher_tmp)

        if catcher_found:
            return 0
        return -1

    def loadLocal(self, filename, recursive = True, lItem = None, lCatcher = False):
        if enable_debug:
            xbmc.output(str(filename))
        try:
            f = open(str(os.path.join(resDir, filename)), 'r')
            data = smart_unicode(f.read())
            data = data.replace('\r\n', '\n')
            data = data.split('\n')
            f.close()
            if enable_debug:
                xbmc.output('Local file ' + str(os.path.join(resDir, filename)) + ' opened')
        except:
            if enable_debug:
                xbmc.output('File: ' + str(os.path.join(resDir, filename)) + ' not found')
            try:
                f = open(str(os.path.join(cacheDir, filename)), 'r')
                data = smart_unicode(f.read())
                data = data.replace('\r\n', '\n')
                data = data.split('\n')
                f.close()
                if enable_debug:
                    xbmc.output('Local file ' + str(os.path.join(cacheDir, filename)) + ' opened')
            except:
                if enable_debug:
                    xbmc.output('File: ' + str(os.path.join(cacheDir, filename)) + ' not found')
                try:
                    f = open(str(filename), 'r')
                    data = smart_unicode(f.read())
                    data = data.replace('\r\n', '\n')
                    data = data.split('\n')
                    f.close()
                    if enable_debug:
                        xbmc.output('Local file ' + str(filename) + ' opened')
                except:
                    if enable_debug:
                        xbmc.output('File: ' + str(filename) + ' not found')
                        traceback.print_exc(file = sys.stdout)
                    return -1

        self.cfg = filename
        if self.getFileExtension(self.cfg) == 'cfg' and lItem != None:
            try:
                lItem.infos_values[lItem.infos_names.index(strin)] = self.cfg
            except:
                lItem.infos_names.append('cfg')
                lItem.infos_values.append(self.cfg)
        del self.items[:]
        tmp = None
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index])
                    value = m[index+1:]
                    index = value.find('|')
                    if value[:index] == 'video.devil.locale':
                        value = ' ' + __language__(int(value[index+1:])) + ' '
                    elif value[:index] == 'video.devil.image':
                        value = os.path.join(imgDir, value[index+1:])
                    if key == 'start':
                        self.start = value
                    elif key == 'player':
                        self.player = value
                    elif key == 'sort':
                        self.sort = value
                    elif key == 'skill':
                        self.skill = value
                        skill_file = filename[:filename.find('.')] + '.lnk'
                        if self.skill.find('redirect') != -1:
                            try:
                                f = open(str(os.path.join(resDir, skill_file)), 'r')
                                forward_cfg = f.read()
                                f.close()
                                if forward_cfg != self.cfg:
                                    return self.loadLocal(forward_cfg, recursive, lItem, lCatcher)
                                return 0
                            except:
                                pass
                        elif self.skill.find('store') != -1:
                            f = open(str(os.path.join(resDir, skill_file)), 'w')
                            f.write(self.cfg)
                            f.close()
                    elif key == 'catcher':
                        if lCatcher:
                            try:
                                ret = self.loadCatcher(value)
                                if ret != 0:
                                    if enable_debug:
                                        xbmc.output('Error while loading catcher')
                                    return ret
                            except:
                                if enable_debug:
                                    traceback.print_exc(file = sys.stdout)
                                return -1
                    elif key == 'header':
                        index = value.find('|')
                        self.reference = value[:index]
                        self.content = value[index+1:]
                    elif key == 'item_infos':
                        rule_tmp = CRuleItem()
                        rule_tmp.infos = value
                    elif key == 'item_order':
                        rule_tmp.order = value
                    elif key == 'item_skill':
                        rule_tmp.skill = value
                    elif key == 'item_curr':
                        rule_tmp.curr = value
                    elif key == 'item_info_name':
                        info_tmp = CItemInfo()
                        index = value.find('|')
                        if value[:index] == 'video.devil.context':
                            value = 'context.' + __language__(int(value[index+1:]))
                        info_tmp.name = value
                    elif key == 'item_info_from':
                        info_tmp.src = value
                    elif key == 'item_info':
                        info_tmp.rule = value
                    elif key == 'item_info_default':
                        info_tmp.default = value
                    elif key == 'item_info_build':
                        info_tmp.build = value
                        rule_tmp.info_list.append(info_tmp)
                    elif key == 'item_url_build':
                        rule_tmp.url_build = value
                        self.rules.append(rule_tmp)
                    elif key == 'title':
                        tmp = CListItem()
                        tmp.infos_names.append('title')
                        tmp.infos_values.append(value)
                    elif key == 'type':
                        tmp.infos_names.append('type')
                        if recursive and value == 'once':
                            value = u'rss'
                        tmp.infos_values.append(value)
                    elif key == 'url':
                        tmp.infos_names.append('url')
                        tmp.infos_values.append(value)
                        if lItem != None:
                            for info_name in lItem.infos_names:
                                try:
                                    info_idx = tmp.infos_names.index(info_name)
                                except:
                                    tmp.infos_names.append(info_name)
                                    tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                        self.items.append(tmp)
                        tmp = None
                    elif tmp != None:
                        tmp.infos_names.append(key)
                        tmp.infos_values.append(value)

        if recursive and self.start != '':
            if lItem == None:
                self.loadRemote(self.start, False)
            else:
                if self.getFileExtension(lItem.infos_values[lItem.infos_names.index('url')]) == 'cfg':
                    lItem.infos_values[lItem.infos_names.index('url')] = self.start
                    self.loadRemote(self.start, False, lItem)
                else:
                    self.loadRemote(lItem.infos_values[lItem.infos_names.index('url')], False, lItem)
        return 0

    def infoFormatter(self, info_name, info_value, cfg_file): # Site specific info handling
        info_value = info_value.replace('|', '-')
        if cfg_file == 'zdf.de.cfg':
		return clean_safe(info_value.replace('&nbsp;', ' ')).replace("\\'", "\'").replace('\\"', '\"')
        if info_name == 'title':
            try:
                info_value = clean_safe(info_value.replace('\r\n', '').replace('\n', '').replace('\t', ''))
            except:
                info_value = '...'
            if len(info_value) == 0:
                info_value = '...'
            elif cfg_file.find('youtube') != -1: # youtube
                info_value = info_value.replace('<b>', '').replace('</b>', '')
            elif cfg_file.find('xhamster') != -1:
                info_value = info_value.replace('<span style="background-color:#E9E9E9;">', '').replace('</span>', '')
            elif cfg_file.find('boysfood') != -1: # boysfood
                info_value = info_value.replace('<font style="color:#c00000;font-weight:bold;">', '').replace('</font>', '')
        elif info_name == 'icon':
            info_value = decode(unquote_safe(info_value))
            if info_value == '':
                info_value = os.path.join(imgDir, 'video.png')
        return clean_safe(info_value)

    def loadRemote(self, remote_url, recursive = True, lItem = None):
	remote_url = urllib.unquote_plus(remote_url)
        if enable_debug:
            xbmc.output(repr(remote_url))
        if lItem == None:
            lItem = self.decodeUrl(remote_url)
        try:
            curr_url = remote_url
            if recursive:
                try:
                    if self.loadLocal(lItem.infos_values[lItem.infos_names.index('cfg')], False, lItem) != 0:
                        return -1
                except:
                    pass
                try:
                    if lItem.infos_values[lItem.infos_names.index('type')] == u'search':
                        try:
                            f = open(os.path.join(cacheDir, 'search'), 'r')
                            curr_phrase = urllib.unquote_plus(f.read())
                            f.close()
                        except:
                            curr_phrase = ''
                        search_phrase = self.getKeyboard(default = curr_phrase, heading = __language__(30102))
                        if search_phrase == '':
                            return -1
                        xbmc.sleep(10)
                        f = open(os.path.join(cacheDir, 'search'), 'w')
                        f.write(search_phrase)
                        f.close()
                        curr_url = curr_url % (search_phrase)
                        lItem.infos_values[lItem.infos_names.index('url')] = curr_url
                        lItem.infos_values[lItem.infos_names.index('type')] = u'rss'
                except:
                    pass
            if self.reference == '':
                txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
            else:
                txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7', self.reference:self.content}
            if enable_debug:
                f = open(os.path.join(cacheDir, 'page.html'), 'w')
                f.write('<Titel>'+ curr_url + '</Title>\n\n')
	    curr_url = urllib.unquote_plus(curr_url)
            req = Request(curr_url, None, txheaders)
            try:
                handle = urlopen(req)
            except:
                if enable_debug:
                    traceback.print_exc(file = sys.stdout)
                return
            data = handle.read()
            #cj.save(os.path.join(resDir, 'cookies.lwp'), ignore_discard=True)
            cj.save(os.path.join(settingsDir, 'cookies.lwp'))
            if enable_debug:
                f.write(data)
                f.close()
                xbmc.output('Remote URL ' + str(curr_url) + ' opened')
        except IOError:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            return -1

        # Find list items
        reinfos = []
        lock = False
        for item_rule in self.rules:
            if item_rule.skill.find('lock') != -1 and lock:
                continue
            one_found = False
            catfilename = self.randomFilename(prefix=(self.cfg + '.dir.'), suffix = '.list')
            f = None
            if item_rule.order.find('|') != -1:
                reinfos = []
                infos_nbr = len(item_rule.order.split('|'))
                for idx in range(infos_nbr):
                    reinfos.append('')
            else:
                reinfos = ''
            revid = re.compile(item_rule.infos, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            for reinfos in revid.findall(data):
                if item_rule.skill.find('lock') != -1 and lock:
                    continue
                tmp = CListItem()
                if item_rule.order.find('|') != -1:
                    tmp.infos_names = item_rule.order.split('|')
                    tmp.infos_values = list(reinfos)
                else:
                    tmp.infos_names.append(item_rule.order)
                    tmp.infos_values.append(reinfos)
                for info in item_rule.info_list:
                    info_value = ''
                    try:
                        info_idx = tmp.infos_names.index(info.name)
                        if info.build.find('%s') != -1:
                            tmp.infos_values[info_idx] = smart_unicode(info.build % smart_unicode(tmp.infos_values[info_idx]))
                        continue
                    except:
                        pass
                    if info.rule != '':
                        info_rule = info.rule
                        if info.rule.find('%s') != -1:
                            src = tmp.infos_values[tmp.infos_names.index(info.src)]
                            info_rule = info.rule % (smart_unicode(src))
                        infosearch = re.search(info_rule, data)
                        if infosearch:
                            info_value = infosearch.group(1).lstrip().rstrip()
                            if info.build.find('%s') != -1:
                                info_value = info.build % (smart_unicode(info_value))
                        elif info.default != '':
                            info_value = info.default
                    else:
                        if info.build.find('%s') != -1:
                            src = tmp.infos_values[tmp.infos_names.index(info.src)]
                            info_value = info.build % (smart_unicode(src))
                        else:
                            info_value = info.build
                    tmp.infos_names.append(info.name)
                    tmp.infos_values.append(info_value)
                info_idx = 0
                for info_name in tmp.infos_names:
                    tmp.infos_values[info_idx] = self.infoFormatter(info_name, tmp.infos_values[info_idx], self.cfg)
                    if info_name.rfind('.append') != -1:
                        tmp.infos_values[tmp.infos_names.index(info_name[:info_name.rfind('.append')])] = smart_unicode(tmp.infos_values[tmp.infos_names.index(info_name[:info_name.rfind('.append')])]) + smart_unicode(tmp.infos_values[info_idx])
                    info_idx = info_idx + 1
                info_idx = tmp.infos_names.index('url')
                tmp.infos_values[info_idx] = smart_unicode(item_rule.url_build % (smart_unicode(tmp.infos_values[info_idx])))
                if item_rule.skill.find('append') != -1:
                    tmp.infos_values[info_idx] = curr_url + tmp.infos_values[info_idx]
                if item_rule.skill.find('space') != -1:
                    try:
                        tmp.infos_values[tmp.infos_names.index('title')] = ' ' + tmp.infos_values[tmp.infos_names.index('title')].lstrip().rstrip() + ' '
                    except:
                        pass
                for info_name in lItem.infos_names:
                    try:
                        info_idx = tmp.infos_names.index(info_name)
                    except:
                        tmp.infos_names.append(info_name)
                        tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                if item_rule.skill.find('recursive') != -1:
                    self.loadRemote(tmp.infos_values[tmp.infos_names.index('url')], False, tmp)
                    tmp = None
                else:
                    if item_rule.skill.find('directory') != -1:
                        one_found = True
                        if f == None:
                            f = open(str(os.path.join(cacheDir, catfilename)), 'w')
                            f.write(smart_unicode('########################################################\n').encode('utf-8'))
                            f.write(smart_unicode('#                    Temporary file                    #\n').encode('utf-8'))
                            f.write(smart_unicode('########################################################\n').encode('utf-8'))
                        try:
                            f.write(smart_unicode('title=' + tmp.infos_values[tmp.infos_names.index('title')] + '\n').encode('utf-8'))
                        except:
                            f.write(smart_unicode('title=...\n').encode('utf-8'))
                        for info_name in tmp.infos_names:
                            if info_name != 'url' and info_name != 'title':
                                f.write(smart_unicode(info_name + '=' + tmp.infos_values[tmp.infos_names.index(info_name)] + '\n').encode('utf-8'))
                        f.write(smart_unicode('url=' + tmp.infos_values[tmp.infos_names.index('url')] + '\n').encode('utf-8'))
                    else:
                        self.items.append(tmp)
                    if item_rule.skill.find('lock') != -1:
                        lock = True
            if item_rule.curr != '':
                revid = re.compile(item_rule.curr, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for title in revid.findall(data):
                    tmp = CListItem()
                    tmp.infos_names.append('title')
                    if item_rule.skill.find('space') != -1:
                        tmp.infos_values.append('  ' + clean_safe(title.lstrip().rstrip()) + ' (' + __language__(30106) +')  ')
                    else:
                        tmp.infos_values.append(' ' + clean_safe(title.lstrip().rstrip()) + ' (' + __language__(30106) +') ')
                    tmp.infos_names.append('url')
                    tmp.infos_values.append(curr_url)
                    for info in item_rule.info_list:
                        if info.name == 'icon':
                            tmp.infos_names.append('icon')
                            if info.default != '':
                                tmp.infos_values.append(info.default)
                            else:
                                tmp.infos_values.append(info.build)
                    for info_name in lItem.infos_names:
                        try:
                            info_idx = tmp.infos_names.index(info_name)
                        except:
                            tmp.infos_names.append(info_name)
                            tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                    if item_rule.skill.find('directory') != -1:
                        one_found = True
                        if f == None:
                            f = open(str(os.path.join(cacheDir, catfilename)), 'w')
                            f.write(smart_unicode('########################################################\n').encode('utf-8'))
                            f.write(smart_unicode('#                    Temporary file                    #\n').encode('utf-8'))
                            f.write(smart_unicode('########################################################\n').encode('utf-8'))
                        f.write(smart_unicode('title=' + tmp.infos_values[tmp.infos_names.index('title')] + '\n').encode('utf-8'))
                        for info_name in tmp.infos_names:
                            if info_name != 'url' and info_name != 'title':
                                f.write(smart_unicode(info_name + '=' + tmp.infos_values[tmp.infos_names.index(info_name)] + '\n').encode('utf-8'))
                        f.write(smart_unicode('url=' + tmp.infos_values[tmp.infos_names.index('url')] + '\n').encode('utf-8'))
                    else:
                        self.items.append(tmp)
                    if item_rule.skill.find('lock') != -1:
                        lock = True
            if one_found:
                tmp = CListItem()
                tmp.infos_names.append('url')
                tmp.infos_values.append(catfilename)
                for info in item_rule.info_list:
                    if info.name == 'title':
                        tmp.infos_names.append('title')
                        tmp.infos_values.append(' ' + info.build + ' ')
                    elif info.name == 'icon':
                        tmp.infos_names.append('icon')
                        if info.default != '':
                            tmp.infos_values.append(info.default)
                        else:
                            tmp.infos_values.append(info.build)
                for info_name in lItem.infos_names:
                    try:
                        info_idx = tmp.infos_names.index(info_name)
                    except:
                        tmp.infos_names.append(info_name)
                        tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                self.items.append(tmp)
                if item_rule.skill.find('lock') != -1:
                    lock = True
            if f != None:
                f.write(smart_unicode('########################################################\n').encode('utf-8'))
                f.close()
        return 0

class Main:
    def __init__(self):
        if enable_debug:
            xbmc.output('Initializing VideoDevil')
        self.pDialog = None
        self.curr_file = ''
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.videoExtension = '.flv'
        self.currentlist = CCurrentList()
        if enable_debug:
            xbmc.output('VideoDevil initialized')
        self.run()

    def getDirectLink(self, orig_url):
        orig_url = orig_url.replace('\r\n', '').replace('\n', '')
        self.videoExtension = '.flv'
        for source in self.currentlist.catcher:
            if len(self.urlList) > 0 and source.quality == 'fallback':
                continue
            if source.rule.url != '':
                if source.rule.data == '':
                    url = source.rule.url % orig_url
                    req = Request(url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                    if source.rule.reference != '':
                        req.add_header(source.rule.reference, source.rule.content)
                    urlfile = opener.open(req)
                    if source.rule.limit == 0:
                        fc = urlfile.read()
                    else:
                        fc = urlfile.read(source.rule.limit)
                else:
                    data = source.rule.data % orig_url
                    req = Request(source.rule.url, data)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                    if source.rule.reference != '':
                        req.add_header(source.rule.reference, source.rule.content)
                    response = urlopen(req)
                    if source.rule.limit == 0:
                        fc = response.read()
                    else:
                        fc = response.read(source.rule.limit)
                if enable_debug:
                    f = open(os.path.join(cacheDir, 'catcher.html'), 'w')
                    f.write('<Titel>'+ orig_url + '</Title>\n\n')
                    f.write(fc)
                    f.close()
            urlsearch = re.search(source.rule.target, fc)
            match = ''
            if urlsearch:
                match = urlsearch.group(1).replace('\r\n', '').replace('\n', '').lstrip().rstrip()
                if source.rule.action.find('unquote') != -1:
                    match = unquote_safe(match)
                elif source.rule.action.find('decode') != -1:
		    match = decode(match)
                if source.rule.build.find('%s') != -1:
                    match = source.rule.build % match
                if source.ext_rule != None:
                    if source.ext_rule.data == '':
                        if source.ext_rule.url.find('%s') != -1:
                            ext_url = source.ext_rule.url % match
                        else:
                            ext_url = match
                        ext_req = Request(ext_url)
                        ext_req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        if source.ext_rule.reference != '':
                            ext_req.add_header(source.ext_rule.reference, source.ext_rule.content)
                        ext_urlfile = opener.open(ext_req)
                        if source.ext_rule.limit == 0:
                            ext_fc = ext_urlfile.read()
                        else:
                            ext_fc = ext_urlfile.read(source.ext_rule.limit)
                    else:
                        ext_data = source.ext_rule.data % match
                        ext_req = Request(source.ext_rule.url, ext_data)
                        ext_req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        if source.ext_rule.reference != '':
                            ext_req.add_header(source.ext_rule.reference, source.ext_rule.content)
                        ext_response = urlopen(ext_req)
                        ext_fc = ext_response.read()
                        if source.ext_rule.limit == 0:
                            ext_fc = ext_response.read()
                        else:
                            ext_fc = ext_response.read(source.ext_rule.limit)
                    if enable_debug:
                        f = open(os.path.join(cacheDir, 'ext_catcher.html'), 'w')
                        f.write('<Titel>'+ match + '</Title>\n\n')
                        f.write(ext_fc)
                        f.close()
                    ext_urlsearch = re.search(source.ext_rule.target, ext_fc)
                    if ext_urlsearch:
                        match = ext_urlsearch.group(1).replace('\r\n', '').replace('\n', '').lstrip().rstrip()
                        if source.ext_rule.action.find('unquote') != -1:
                            match = unquote_safe(match)
                        elif source.ext_rule.action.find('decode') != -1:
			    match = decode(match)
                        if source.ext_rule.build.find('%s') != -1:
                            match = source.ext_rule.build % match
                    else:
                        match = ''
                source.match = match
                if source.match != '':
                    self.urlList.append(source.match)
                    self.extensionList.append(source.extension)
                    if source.quality == 'fallback':
                        self.videoExtension = '.' + source.extension
                        return source.match
                    elif source.quality == 'low':
                        if source.info == '':
                            self.selectionList.append(__language__(30056) + ' (' + source.extension + ')')
                        else:
                            self.selectionList.append(__language__(30056) + ' (' + source.info + ')')
                    elif source.quality == 'standard':
                        if source.info == '':
                            self.selectionList.append(__language__(30057) + ' (' + source.extension + ')')
                        else:
                            self.selectionList.append(__language__(30057) + ' (' + source.info + ')')
                    elif source.quality == 'high':
                        if source.info == '':
                            self.selectionList.append(__language__(30058) + ' (' + source.extension + ')')
                        else:
                            self.selectionList.append(__language__(30058) + ' (' + source.info + ')')

        if len(self.urlList) > 0:
            if len(self.urlList) == 1:
                self.videoExtension = '.' + self.extensionList[0]
                return self.urlList[0]
            elif int(addon.getSetting('video_type')) == 0:
                dia = xbmcgui.Dialog()
                selection = dia.select(__language__(30055), self.selectionList)
                self.videoExtension = '.' + self.extensionList[selection]
                return self.urlList[selection]
            elif int(addon.getSetting('video_type')) == 1: # low
                for source in self.currentlist.catcher:
                    if source.quality == 'low' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
                for source in self.currentlist.catcher:
                    if source.quality == 'standard' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
                for source in self.currentlist.catcher:
                    if source.quality == 'high' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
            elif int(addon.getSetting('video_type')) == 3: # high
                for source in self.currentlist.catcher:
                    if source.quality == 'high' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
                for source in self.currentlist.catcher:
                    if source.quality == 'standard' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
                for source in self.currentlist.catcher:
                    if source.quality == 'low' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
            elif int(addon.getSetting('video_type')) == 2: # standard
                for source in self.currentlist.catcher:
                    if source.quality == 'standard' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
                for source in self.currentlist.catcher:
                    if source.quality == 'low' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
                for source in self.currentlist.catcher:
                    if source.quality == 'high' and source.match != '':
                        self.videoExtension = '.' + source.extension
                        return source.match
        return ''

    def playVideo(self, videoItem):
        if videoItem == None:
            return
        if videoItem.infos_values[videoItem.infos_names.index('url')] == '':
            return
        url = videoItem.infos_values[videoItem.infos_names.index('url')]
        try:
            icon = videoItem.infos_values[videoItem.infos_names.index('icon')]
        except:
            icon = os.path.join(imgDir, 'video.png')
        try:
            title = videoItem.infos_values[videoItem.infos_names.index('title')]
        except:
            title = '...'
        try:
            urllib.urlretrieve(icon, os.path.join(cacheDir, 'thumb.tbn'))
            icon = os.path.join(cacheDir, 'thumb.tbn')
        except:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            icon = os.path.join(imgDir, 'video.png')
        url = urllib.unquote_plus(url)
        flv_file = url
        listitem = xbmcgui.ListItem(title, title, icon, icon)
        listitem.setInfo('video', {'Title':title})
        for video_info_name in videoItem.infos_names:
            try:
                listitem.setInfo(type = 'Video', infoLabels = {video_info_name: videoItem.infos_values[videoItem.infos_names.index(video_info_name)]})
            except:
                pass
        if self.currentlist.skill.find('nodownload') == -1:
            if addon.getSetting('download') == 'true':
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create('VideoDevil', __language__(30050), __language__(30051))
		flv_file = self.downloadMovie(url, title)
                self.pDialog.close()
                if flv_file == None:
                    dialog = xbmcgui.Dialog()
                    dialog.ok('VideoDevil Info', __language__(30053))
            elif addon.getSetting('download') == 'false' and addon.getSetting('download_ask') == 'true':
                dia = xbmcgui.Dialog()
                if dia.yesno('', __language__(30052)):
                    self.pDialog = xbmcgui.DialogProgress()
                    self.pDialog.create('VideoDevil', __language__(30050), __language__(30051))
                    flv_file = self.downloadMovie(url, title)
                    self.pDialog.close()
                    if flv_file == None:
                        dialog = xbmcgui.Dialog()
                        dialog.ok('VideoDevil Info', __language__(30053))
        else:
            flv_file = None

        player_type = {0:xbmc.PLAYER_CORE_AUTO, 1:xbmc.PLAYER_CORE_MPLAYER, 2:xbmc.PLAYER_CORE_DVDPLAYER}[int(addon.getSetting('player_type'))]
        if self.currentlist.player == 'auto':
            player_type = xbmc.PLAYER_CORE_AUTO
        elif self.currentlist.player == 'mplayer':
            player_type = xbmc.PLAYER_CORE_MPLAYER
        elif self.currentlist.player == 'dvdplayer':
            player_type = xbmc.PLAYER_CORE_DVDPLAYER
	
        if flv_file != None and os.path.isfile(flv_file):
            if enable_debug:
                xbmc.output('Play: ' + str(flv_file))
            xbmc.Player(player_type).play(str(flv_file), listitem)
        else:
            if enable_debug:
                xbmc.output('Play: ' + str(url))
            xbmc.Player(player_type).play(str(url), listitem)
        xbmc.sleep(200)

    def downloadMovie(self, url, title):
        if enable_debug:
            xbmc.output('Trying to download video ' + str(url))
	if addon.getSetting('download_Path') == '':
	    try:
		dl_path = xbmcgui.Dialog().browse(0, __language__(30017),'files', '', False, False)
		addon.setSetting(id='download_path', value=dl_path)
		if not os.path.exists(dl_path):
		    os.mkdir(dl_path)
	    except:pass
        file_path = xbmc.makeLegalFilename(os.path.join(addon.getSetting('download_Path'), title + self.videoExtension))
        if os.path.isfile(file_path):
            file_path = xbmc.makeLegalFilename(self.currentlist.randomFilename(prefix = file_path[:file_path.rfind('.')] + '&', suffix = self.videoExtension))
        try:
            urllib.urlretrieve(url, file_path, self.video_report_hook)
            if enable_debug:
                xbmc.output('Video ' + str(url) + ' downloaded to ' + repr(file_path))
            return file_path
        except IOError:
            title = first_clean_filename(title)
            file_path = xbmc.makeLegalFilename(os.path.join(addon.getSetting('download_Path'), title + self.videoExtension))
            if os.path.isfile(file_path):
                file_path = xbmc.makeLegalFilename(self.currentlist.randomFilename(prefix = file_path[:file_path.rfind('.')] + '&', suffix = self.videoExtension))
            try:
                urllib.urlretrieve(url, file_path, self.video_report_hook)
                if enable_debug:
                    xbmc.output('Video ' + str(url) + ' downloaded to ' + repr(file_path))
                return file_path
            except IOError:
                title = second_clean_filename(title)
                file_path = xbmc.makeLegalFilename(os.path.join(addon.getSetting('download_Path'), title + self.videoExtension))
                if os.path.isfile(file_path):
                    file_path = xbmc.makeLegalFilename(self.currentlist.randomFilename(prefix = file_path[:file_path.rfind('.')] + '&', suffix = self.videoExtension))
                try:
                    urllib.urlretrieve(url, file_path, self.video_report_hook)
                    if enable_debug:
                        xbmc.output('Video ' + str(url) + ' downloaded to ' + repr(file_path))
                    return file_path
                except IOError:
                    title = third_clean_filename(title)
                    file_path = xbmc.makeLegalFilename(os.path.join(addon.getSetting('download_Path'), title + self.videoExtension))
                    if os.path.isfile(file_path):
                        file_path = xbmc.makeLegalFilename(self.currentlist.randomFilename(dir = addon.getSetting('download_Path'), suffix = self.videoExtension))
                    try:
                        urllib.urlretrieve(url, file_path, self.video_report_hook)
                        if enable_debug:
                            xbmc.output('Video ' + str(url) + ' downloaded to ' + repr(file_path))
                        return file_path
                    except IOError:
                        title = self.currentlist.randomFilename()
                        file_path = xbmc.makeLegalFilename(os.path.join(addon.getSetting('download_Path'), title + self.videoExtension))
                        if os.path.isfile(file_path):
                            file_path = xbmc.makeLegalFilename(self.currentlist.randomFilename(prefix = file_path[:file_path.rfind('.')] + '&', suffix = self.videoExtension))
                        try:
                            urllib.urlretrieve(url, file_path, self.video_report_hook)
                            if enable_debug:
                                xbmc.output('Video ' + str(url) + ' downloaded to ' + repr(file_path))
                            return file_path
                        except:
                            pass
                    except:
                        pass
                except:
                    pass
            except:
                pass
        except:
            pass
        xbmc.sleep(500)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except:
                if enable_debug:
                    traceback.print_exc(file = sys.stdout)
        return None

    def video_report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, __language__(30050), __language__(30051))
        if self.pDialog.iscanceled():
            raise KeyboardInterrupt

    def TargetFormatter(self, url, cfg_file): # Site specific target url handling
        return url

    def parseView(self, url):
        lItem = self.currentlist.decodeUrl(url)
        url = lItem.infos_values[lItem.infos_names.index('url')]
        ext = self.currentlist.getFileExtension(url)
        if ext == 'cfg' or ext == 'list':
            result = self.currentlist.loadLocal(url, lItem = lItem)
        elif ext == 'add':
	    url = urllib.unquote_plus(url)
            self.currentlist.addItem(url[:len(url) - 4])
            return -2
        elif ext == 'remove':
            dia = xbmcgui.Dialog()
            if dia.yesno('', __language__(30054)):
		url = urllib.unquote_plus(url)
                self.currentlist.removeItem(url[:len(url) - 7])
                xbmc.executebuiltin('Container.Refresh')
            return -2
        elif ext == 'videodevil' or ext == 'dwnlddevil':
	    url = urllib.unquote_plus(url)		
            url = url[:len(url) - 11]
            lItem.infos_values[lItem.infos_names.index('url')] = url
            cfg_file = lItem.infos_values[lItem.infos_names.index('cfg')]
            if lItem.infos_values[lItem.infos_names.index('type')] == 'video':
                self.currentlist.loadLocal(cfg_file, False, lItem, True)
                lItem.infos_values[lItem.infos_names.index('url')] = self.getDirectLink(lItem.infos_values[lItem.infos_names.index('url')])
            lItem.infos_values[lItem.infos_names.index('url')] = self.TargetFormatter(lItem.infos_values[lItem.infos_names.index('url')], cfg_file)
            try:
                self.videoExtension = '.' + lItem.infos_values[lItem.infos_names.index('extension')]
            except:
                pass
            if ext == 'videodevil':
                result = self.playVideo(lItem)
            else:
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create('VideoDevil', __language__(30050), __language__(30051))
                self.downloadMovie(lItem.infos_values[lItem.infos_names.index('url')], lItem.infos_values[lItem.infos_names.index('title')])
                self.pDialog.close()
            return -2
        else:
            result = self.currentlist.loadRemote(lItem.infos_values[lItem.infos_names.index('url')], lItem = lItem)

        xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)
        if self.currentlist.sort.find('label') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)
        if self.currentlist.sort.find('size') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_SIZE)
        if self.currentlist.sort.find('duration') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DURATION)
        if self.currentlist.sort.find('genre') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_GENRE)
        if self.currentlist.sort.find('rating') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if self.currentlist.sort.find('date') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DATE)

        if self.currentlist.skill.find('play') != -1 and self.currentlist.videoCount() == 1:
            url = self.currentlist.codeUrl(self.currentlist.getVideo(), 'videodevil')
            result = self.parseView(url)
        else:
            for m in self.currentlist.items:
                m_url = m.infos_values[m.infos_names.index('url')]
                try:
                    m_type = m.infos_values[m.infos_names.index('type')]
                except:
                    m_type = 'rss'
                m_icon = m.infos_values[m.infos_names.index('icon')]
                m_title = clean_safe(m.infos_values[m.infos_names.index('title')])
                if m_type == 'rss' or m_type == 'search':
                    self.addListItem(m_title, self.currentlist.codeUrl(m), m_icon, len(self.currentlist.items), m)
                elif m_type.find('video') != -1:
                    self.addListItem(m_title, self.currentlist.codeUrl(m, 'videodevil'), m_icon, len(self.currentlist.items), m)
        return result

    def addListItem(self, title, url, icon, totalItems, lItem):
        u = sys.argv[0] + '?url=' + url
        liz = xbmcgui.ListItem(title, title, icon, icon)
        if self.currentlist.getFileExtension(url) == 'videodevil' and self.currentlist.skill.find('nodownload') == -1:
	    action = 'XBMC.RunPlugin(%s.dwnlddevil)' % u[:len(u)-11]
            try:
                liz.addContextMenuItems([(__language__(30007), action)])
            except:
                pass
        if self.currentlist.skill.find('add') != -1:
            action = 'XBMC.RunPlugin(%s.add)' % u
            try:
                liz.addContextMenuItems([(__language__(30010), action)])
            except:
                pass
        if self.currentlist.skill.find('remove') != -1:
            action = 'XBMC.RunPlugin(%s.remove)' % u
            try:
                liz.addContextMenuItems([(__language__(30011), action)])
            except:
                pass
        for video_info_name in lItem.infos_names:
            if video_info_name.find('context.') != -1:
                try:
                    cItem = lItem
                    cItem.infos_values[lItem.infos_names.index('url')] = lItem.infos_values[lItem.infos_names.index(video_info_name)]
                    cItem.infos_values[lItem.infos_names.index('type')] = 'rss'
                    action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?url=' + self.currentlist.codeUrl(cItem))
                    liz.addContextMenuItems([(video_info_name[video_info_name.find('.') + 1:], action)])
                except:
                    pass
            if video_info_name.find('.append') == -1 and video_info_name != 'url' and video_info_name != 'title' and video_info_name != 'icon' and video_info_name != 'type' and video_info_name != 'extension' and video_info_name.find('.tmp') == -1 and video_info_name.find('.append') == -1 and video_info_name.find('context.') == -1:
                try:
                    if video_info_name.find('.int') != -1:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name[:video_info_name.find('.int')]): int(lItem.infos_values[lItem.infos_names.index(video_info_name)])})
                    elif video_info_name.find('.once') != -1:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name[:video_info_name.find('.once')]): lItem.infos_values[lItem.infos_names.index(video_info_name)]})
                    else:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name): lItem.infos_values[lItem.infos_names.index(video_info_name)]})
                except:
                    pass
        xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True, totalItems = totalItems)

    def purgeCache(self):
        for root, dirs, files in os.walk(cacheDir , topdown = False):
            for name in files:
                os.remove(os.path.join(root, name))

    def run(self):
        if enable_debug:
            xbmc.output('VideoDevil running')
        try:
            self.handle = int(sys.argv[1])
            paramstring = sys.argv[2]
            if len(paramstring) <= 2:
                if addon.getSetting('hide_warning') == 'false':
                    dialog = xbmcgui.Dialog()
                    if not dialog.yesno(__language__(30061), __language__(30062), __language__(30063), __language__(30064), __language__(30065), __language__(30066)):
                        return
                if enable_debug:
                    xbmc.output('Settings directory: ' + str(settingsDir))
                    xbmc.output('Cache directory: ' + str(cacheDir))
                    xbmc.output('Resource directory: ' + str(resDir))
                    xbmc.output('Image directory: ' + str(imgDir))
                if not os.path.exists(cacheDir):
                    if enable_debug:
                        xbmc.output('Creating cache directory ' + str(cacheDir))
                    os.mkdir(settingsDir)
                    os.mkdir(cacheDir)
                    if enable_debug:
                        xbmc.output('Cache directory created')
                if enable_debug:
                    xbmc.output('Purging cache directory')
                self.purgeCache()
                if enable_debug:
                    xbmc.output('Cache directory purged')
                self.parseView('sites.list')
                del self.currentlist.items[:]
                if enable_debug:
                    xbmc.output('End of directory')
                xbmcplugin.endOfDirectory(handle = int(sys.argv[1]))
            else:
                params = sys.argv[2]
                currentView = params[5:]
                if enable_debug:
                    xbmc.output(repr(currentView))
                if self.parseView(currentView) == 0:
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    if enable_debug:
                        xbmc.output('End of directory')
        except Exception, e:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            dialog = xbmcgui.Dialog()
            dialog.ok('VideoDevil Error', 'Error running VideoDevil.\n\nReason:\n' + str(e))
