# -*- coding: utf-8 -*-
import six
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
import sys
import os.path
import tempfile
from six.moves import urllib_request, urllib_error, urllib_parse
import re
import os
import traceback
from six.moves import http_cookiejar, html_entities, http_client, html_parser

http_client.HTTPConnection._http_vsn = 10
http_client.HTTPConnection._http_vsn_str = 'HTTP/1.1'

# python 2 and 3 compatibility defs
INFO = xbmc.LOGINFO if six.PY3 else xbmc.LOGNOTICE
TRANSLATEPATH = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath

addon = xbmcaddon.Addon(id='plugin.video.videodevil')
__language__ = addon.getLocalizedString
__addonname__ = addon.getAddonInfo('name')
__icon__ = addon.getAddonInfo('icon')
rootDir = addon.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = TRANSLATEPATH(rootDir)
settingsDir = addon.getAddonInfo('profile')
settingsDir = TRANSLATEPATH(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')
cookiePath = os.path.join(settingsDir, 'cookies.lwp')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')

urlopen = urllib_request.urlopen
cj = http_cookiejar.LWPCookieJar()
Request = urllib_request.Request
USERAGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18'

if cj:
    if os.path.isfile(TRANSLATEPATH(cookiePath)):
        try:
            cj.load(TRANSLATEPATH(cookiePath), ignore_discard=True)
        except http_cookiejar.LoadError as e:
            xbmc.log('Failed to open cookie file {}'.format(e), INFO)
    opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj))
else:
    opener = urllib_request.build_opener()

urllib_request.install_opener(opener)

if addon.getSetting('enable_debug') == 'true':
    enable_debug = True
    xbmc.log('VideoDevil debug logging enabled', INFO)
else:
    enable_debug = False

entitydefs2 = {
    '$': '%24',
    '&': '%26',
    '+': '%2B',
    ',': '%2C',
    '/': '%2F',
    ':': '%3A',
    ';': '%3B',
    '=': '%3D',
    '?': '%3F',
    '@': '%40',
    ' ': '%20',
    '"': '%22',
    '<': '%3C',
    '>': '%3E',
    '#': '%23',
    '%': '%25',
    '{': '%7B',
    '}': '%7D',
    '|': '%7C',
    '\\': '%5C',
    '^': '%5E',
    '~': '%7E',
    '[': '%5B',
    ']': '%5D',
    '`': '%60'
}


def clean1(s):  # remove &XXX;
    if not s:
        return ''
    if six.PY3:
        import html
        return html.parser.unescape(s)
    h = html_parser.HTMLParser()
    return h.unescape(s.decode('utf8')).encode('utf8')


def clean2(s):  # remove \\uXXX
    pat = re.compile(r'\\u(....)')

    def sub(mo):
        return six.unichr(int(mo.group(1), 16))
    return pat.sub(sub, smart_unicode(s))


def clean3(s):  # remove &#XXX;
    pat = re.compile(r'&#(\d+);')

    def sub(mo):
        return six.unichr(int(mo.group(1)))
    return decode(pat.sub(sub, smart_unicode(s)))


def decode(s):
    if not s:
        return ''
    try:
        dic = html_entities.name2codepoint
        for key in dic:
            entity = '&' + key + ';'
            s = s.replace(entity, six.unichr(dic[key]))
    except:
        if enable_debug:
            traceback.print_exc(file=sys.stdout)
    return s


def prefix(s):
    if not s:
        return ''
    try:
        if not s.startswith('http'):
            s = 'https:' + s
    except:
        if enable_debug:
            traceback.print_exc(file=sys.stdout)
    return s


def unquote_safe(s):  # unquote
    if not s:
        return ''
    try:
        for key, value in six.iteritems(entitydefs2):
            s = s.replace(value, key)
    except:
        if enable_debug:
            traceback.print_exc(file=sys.stdout)
    return s


def quote_safe(s):  # quote
    if not s:
        return ''
    try:
        for key, value in six.iteritems(entitydefs2):
            s = s.replace(key, value)
    except:
        if enable_debug:
            traceback.print_exc(file=sys.stdout)
    return s


def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, six.string_types):
            if hasattr(s, '__unicode__'):
                s = unicode(s) if six.PY2 else str(s)
            else:
                s = unicode(str(s), 'UTF-8') if six.PY2 else str(str(s), 'UTF-8')
        elif not isinstance(s, six.text_type):
            s = unicode(s, 'UTF-8') if six.PY2 else str(s, 'UTF-8')
    except:
        if not isinstance(s, six.string_types):
            if hasattr(s, '__unicode__'):
                s = unicode(s) if six.PY2 else str(s)
            else:
                s = unicode(str(s), 'ISO-8859-1') if six.PY2 else str(str(s), 'ISO-8859-1')
        elif not isinstance(s, six.text_type):
            s = unicode(s, 'ISO-8859-1') if six.PY2 else str(s, 'ISO-8859-1')
    return s


def clean_safe(s):
    if not s:
        return ''
    try:
        s = clean1(clean2(clean3(smart_unicode(s))))
    except:
        if enable_debug:
            traceback.print_exc(file=sys.stdout)
    return s


def clean_filename(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    return s.strip(badchars)


def smart_read_file(directory, filename):
    f = open(str(os.path.join(directory, filename)), 'r')
    data = smart_unicode(f.read())
    data = data.replace('\r\n', '\n')
    data = data.split('\n')
    f.close()
    return data


class CListItem(object):
    def __init__(self):
        self.infos_dict = {}


class CItemInfo(object):
    def __init__(self):
        self.name = ''
        self.src = 'url'
        self.rule = ''
        self.default = ''
        self.build = ''


class CRuleItem(object):
    def __init__(self):
        self.infos = ''
        self.order = ''
        self.skill = ''
        self.curr = ''
        self.info_list = []
        self.url_build = ''


class CCatcherRuleItem(object):
    def __init__(self):
        self.target = ''
        self.url = ''
        self.data = ''
        self.reference = ''
        self.content = ''
        self.limit = 0
        self.action = ''
        self.build = ''


class CCatcherItem(object):
    def __init__(self):
        self.rule = CCatcherRuleItem()
        self.ext_rule = None
        self.match = ''
        self.info = ''
        self.extension = 'flv'
        self.quality = 'standard'


class CCurrentList(object):
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

    def getKeyboard(self, default='', heading='', hidden=False):
        kboard = xbmc.Keyboard(default, heading, hidden)
        kboard.doModal()
        if kboard.isConfirmed():
            return urllib_parse.quote_plus(kboard.getText())
        return ''

    def getFileExtension(self, filename):
        ext_pos = filename.rfind('.')
        if ext_pos != -1:
            return filename[ext_pos + 1:]
        else:
            return ''

    def videoCount(self):
        count = 0
        for item in self.items:
            if item.infos_dict['type'] == 'video':
                count = count + 1
        return count

    def getVideo(self):
        for item in self.items:
            if item.infos_dict['type'] == 'video':
                return item

    def getItemFromList(self, listname, name):
        self.loadLocal(listname, False)
        for item in self.items:
            if item.infos_dict['url'] == name:
                return item
        return None

    def itemInLocalList(self, name):
        for item in self.items:
            if item.infos_dict['url'] == name:
                return True
        return False

    def getItem(self, name):
        item = None
        for root, dirs, files in os.walk(resDir):
            for listname in files:
                if self.getFileExtension(listname) == 'list' \
                        and listname != 'catcher.list':
                    item = self.getItemFromList(listname, name)
                if item is not None:
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
        if item is not None:
            self.items.remove(item)
            self.saveList()
        return

    def saveList(self):
        f = open(str(os.path.join(resDir, 'entry.list')), 'w')
        f.write(smart_unicode('########################################################\n'))
        f.write(smart_unicode('#             Added sites and live streams             #\n'))
        f.write(smart_unicode('########################################################\n'))
        f.write(smart_unicode('skill=remove\n'))
        f.write(smart_unicode('########################################################\n'))
        for item in self.items:
            f.write(smart_unicode('title=' + item.infos_dict['title'] + '\n'))
            for info_name, info_value in item.infos_dict.items():
                if info_name != 'url' and info_name != 'title':
                    f.write(smart_unicode(info_name + '=' + info_value + '\n'))
            f.write(smart_unicode('url=' + item.infos_dict['url'] + '\n'))
            f.write(smart_unicode('########################################################\n'))
        f.close()
        return

    def codeUrl(self, item, suffix=''):
        url = ''
        firstInfo = True
        # this is added for handling the stupid &nbsp;
        item.infos_dict['url'] = item.infos_dict['url'].replace(u'\xa0', ' ')
        for info_name, info_value in item.infos_dict.items():
            if info_name != 'url' and info_name.find('.once') == -1:
                # info_value = urllib.quote(info_value)
                if firstInfo:
                    firstInfo = False
                    url = smart_unicode(info_name) \
                        + ':' \
                        + smart_unicode(info_value)
                else:
                    url = smart_unicode(url) \
                        + '&' + smart_unicode(info_name) \
                        + ':' + smart_unicode(info_value)
        if firstInfo:
            url = 'url:' + smart_unicode(item.infos_dict['url'])
        else:
            try:
                url = smart_unicode(url) \
                    + '&' \
                    + smart_unicode('url:') \
                    + smart_unicode(urllib_parse.quote_plus(item.infos_dict['url']))
            except KeyError:
                xbmc.log('Skipping %s probably has unicode'
                         % item.infos_dict['url'], INFO)
        if len(suffix) > 0:
            url = url + '.' + suffix
        return url

    def decodeUrl(self, url, url_type='rss'):
        item = CListItem()
        if url.find('&') == -1:
            item.infos_dict['url'] = clean_safe(url)
            item.infos_dict['type'] = url_type
            return item
        infos_names_values = url.split('&')
        for info_name_value in infos_names_values:
            sep_index = info_name_value.find(':')
            if sep_index != -1:
                item.infos_dict[info_name_value[:sep_index]] = clean_safe(
                    info_name_value[sep_index + 1:])
        if 'type' not in item.infos_dict:
            item.infos_dict['type'] = url_type
        return item

    def loadCatcher(self, title):
        data = smart_read_file(resDir, 'catcher.list')
        del self.catcher[:]
        catcher_found = False
        for m in data:
            if not m:
                continue
            if m[0] == '#':
                continue
            index = m.find('=')
            if index == -1:
                continue
            key = (m[:index]).lower()
            value = m[index + 1:]
            if key == 'title':
                if catcher_found:
                    return 0
                if title == value:
                    catcher_found = True
            elif catcher_found:
                if key == 'target':
                    catcher_tmp = CCatcherItem()
                    catcher_tmp.rule.target = value
                if key == 'ext_target':
                    catcher_tmp.ext_rule = CCatcherRuleItem()
                    catcher_tmp.ext_rule.target = value
                if key == 'url':
                    catcher_tmp.rule.url = value
                if key == 'ext_url':
                    catcher_tmp.ext_rule.url = value
                if key == 'data':
                    catcher_tmp.rule.data = value
                if key == 'ext_data':
                    catcher_tmp.ext_rule.data = value
                if key == 'header':
                    index = value.find('|')
                    catcher_tmp.rule.reference = value[:index]
                    catcher_tmp.rule.content = value[index + 1:]
                if key == 'ext_header':
                    index = value.find('|')
                    catcher_tmp.ext_rule.reference = value[:index]
                    catcher_tmp.ext_rule.content = value[index + 1:]
                if key == 'build':
                    catcher_tmp.rule.build = value
                if key == 'ext_build':
                    catcher_tmp.ext_rule.build = value
                if key == 'action':
                    catcher_tmp.rule.action = value
                if key == 'ext_action':
                    catcher_tmp.ext_rule.action = value
                if key == 'limit':
                    catcher_tmp.rule.limit = int(value)
                if key == 'ext_limit':
                    catcher_tmp.ext_rule.limit = int(value)
                if key == 'extension':
                    catcher_tmp.extension = value
                if key == 'info':
                    catcher_tmp.info = value
                if key == 'quality':
                    catcher_tmp.quality = value
                    self.catcher.append(catcher_tmp)

        if catcher_found:
            return 0
        return -1

    def loadLocal(self, filename, recursive=True, lItem=None,
                  lCatcher=False):
        if enable_debug:
            xbmc.log('loadLocal: ' + str(filename), INFO)
        for local_path in [resDir, cacheDir, '']:
            try:
                data = smart_read_file(local_path, filename)
                if enable_debug:
                    xbmc.log('Local file '
                             + str(os.path.join(local_path, filename))
                             + ' opened', INFO)
                break
            except Exception as e:
                if enable_debug:
                    xbmc.log('File: '
                             + str(os.path.join(local_path, filename))
                             + ' error: ' + e.__str__(), INFO)
                    if local_path == '':
                        traceback.print_exc(file=sys.stdout)
                if local_path == '':
                    return -1

        self.cfg = filename
        if self.getFileExtension(self.cfg) == 'cfg' and lItem is not None:
            lItem.infos_dict['cfg'] = self.cfg
        del self.items[:]
        tmp = None
        for m in data:
            if not m:
                continue
            if m[0] == '#':
                continue
            index = m.find('=')
            if index == -1:
                continue
            key = (m[:index]).lower()
            value = m[index + 1:]
            index = value.find('|')
            if value[:index] == 'video.devil.locale':
                value = ' ' + __language__(int(value[index + 1:])) + ' '
            elif value[:index] == 'video.devil.image':
                value = os.path.join(imgDir, value[index + 1:])
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
                        f = open(str(os.path.join(resDir, skill_file)),
                                 'r')
                        forward_cfg = f.read()
                        f.close()
                        if forward_cfg != self.cfg:
                            return self.loadLocal(forward_cfg,
                                                  recursive, lItem,
                                                  lCatcher)
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
                                xbmc.log('Error while loading catcher', INFO)
                            return ret
                    except:
                        if enable_debug:
                            traceback.print_exc(file=sys.stdout)
                        return -1
            elif key == 'header':
                index = value.find('|')
                self.reference = value[:index]
                self.content = value[index + 1:]
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
                    value = 'context.' \
                            + __language__(int(value[index + 1:]))
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
                tmp.infos_dict['title'] = value
            elif key == 'type':
                if recursive and value == 'once':
                    value = u'rss'
                tmp.infos_dict['type'] = value
            elif key == 'url':
                tmp.infos_dict['url'] = value
                if lItem is not None:
                    for info_name, info_value \
                            in lItem.infos_dict.items():
                        if info_name not in tmp.infos_dict:
                            tmp.infos_dict[info_name] = info_value
                self.items.append(tmp)
                tmp = None
            elif tmp is not None:
                tmp.infos_dict[key] = value

        if recursive and self.start != '':
            if lItem is None:
                self.loadRemote(self.start, False)
            else:
                if self.getFileExtension(lItem.infos_dict['url']) == 'cfg':
                    lItem.infos_dict['url'] = self.start
                    self.loadRemote(self.start, False, lItem)
                else:
                    self.loadRemote(lItem.infos_dict['url'], False, lItem)
        return 0

    def infoFormatter(self, info_name, info_value, cfg_file):
        # Site specific info handling
        info_value = info_value.replace('|', '-')
        if cfg_file == 'zdf.de.cfg':
            return clean_safe(info_value.replace('&nbsp;', ' ')
                              ).replace("\\'", "\'"
                                        ).replace('\\"', '\"')
        if info_name == 'title':
            try:
                info_value = clean_safe(info_value.strip())
            except:
                info_value = '...'
            if len(info_value) == 0:
                info_value = '...'
            elif cfg_file.find('xhamster') != -1:
                info_value = info_value.replace('<span style="background-color:#E9E9E9;">', '').replace('</span>', '')
        elif info_name == 'icon':
            info_value = decode(unquote_safe(info_value))
            if info_value == '':
                info_value = os.path.join(imgDir, 'video.png')
        return clean_safe(info_value)

    def loadRemote(self, remote_url, recursive=True, lItem=None):
        remote_url = urllib_parse.unquote_plus(remote_url)
        if enable_debug:
            xbmc.log('loadRemote: ' + repr(remote_url), INFO)
        if lItem is None:
            lItem = self.decodeUrl(remote_url)
        try:
            curr_url = remote_url
            if recursive:
                try:
                    if self.loadLocal(lItem.infos_dict['cfg'],
                                      False, lItem) != 0:
                        return -1
                except:
                    pass
                try:
                    if lItem.infos_dict['type'] == u'search':
                        try:
                            curr_phrase = urllib_parse.unquote_plus(addon.getSetting('curr_search'))
                        except:
                            addon.setSetting('curr_search', '')
                        search_phrase = self.getKeyboard(default=curr_phrase,
                                                         heading=__language__(30102))
                        if search_phrase == '':
                            return -1
                        addon.setSetting('curr_search', search_phrase)
                        xbmc.sleep(10)
                        curr_url = curr_url.replace('%s',
                                                    urllib_parse.quote_plus(search_phrase))
                        lItem.infos_dict['url'] = curr_url
                        lItem.infos_dict['type'] = u'rss'
                except:
                    traceback.print_exc(file=sys.stdout)
            if self.reference == '':
                txheaders = {'User-Agent': USERAGENT,
                             'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
            else:
                txheaders = {'User-Agent': USERAGENT,
                             'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                             self.reference: self.content}
            if enable_debug:
                if six.PY2:
                    f = open(os.path.join(cacheDir, 'page.html'), 'w')
                else:
                    f = open(os.path.join(cacheDir, 'page.html'), 'w', encoding='utf-8')
                f.write('<Title>' + curr_url + '</Title>\n\n')

            curr_url = urllib_parse.unquote(curr_url).replace('\\/', '/')
            req = Request(curr_url, None, txheaders)
            try:
                cj.load(TRANSLATEPATH(cookiePath), ignore_discard=True)
                opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj))
                urllib_request.install_opener(opener)
                handle = urlopen(req)
                cj.save(TRANSLATEPATH(cookiePath), ignore_discard=True)
            except:
                if enable_debug:
                    traceback.print_exc(file=sys.stdout)
                return
            undecoded = handle.read()

            encoding = None
            content_type = handle.headers.get('content-type', '')
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1]

            if encoding is None:
                epattern = r'<meta\s+http-equiv="Content-Type"\s+content="(?:.+?);\s+charset=(.+?)"'
                r = re.search(six.b(epattern), undecoded, re.IGNORECASE)
                if r:
                    encoding = r.group(1).decode('latin-1') if six.PY3 else r.group(1)

            data = undecoded.decode(encoding.lower(), errors='ignore') if encoding else undecoded.decode('latin-1', errors='ignore')
            current_url_page = curr_url
            if enable_debug:
                f.write(data.encode('utf-8') if six.PY2 else data)
                f.close()
                xbmc.log('Remote URL ' + str(curr_url) + ' opened', INFO)
        except IOError:
            if enable_debug:
                traceback.print_exc(file=sys.stdout)
            return -1

        # Find list items
        lock = False
        for item_rule in self.rules:
            if item_rule.skill.find('lock') != -1 and lock:
                continue
            one_found = False
            catfilename = tempfile.mktemp(suffix='.list',
                                          prefix=(self.cfg + '.dir.'),
                                          dir='')
            f = None
            revid = re.compile(item_rule.infos,
                               re.IGNORECASE + re.DOTALL + re.MULTILINE)
            for reinfo in revid.findall(data):
                if item_rule.skill.find('lock') != -1 and lock:
                    continue
                tmp = CListItem()
                if item_rule.order.find('|') != -1:
                    infos_names = item_rule.order.split('|')
                    infos_values = list(reinfo)
                    tmp.infos_dict = dict(list(zip(infos_names, infos_values)))
                else:
                    tmp.infos_dict[item_rule.order] = reinfo
                for info in item_rule.info_list:
                    info_value = ''
                    if info.name in tmp.infos_dict:
                        if info.build.find('%s') != -1:
                            tmp.infos_dict[info.name] = smart_unicode(info.build
                                                                      % smart_unicode(tmp.infos_dict[info.name]))
                        continue
                    if info.rule != '':
                        info_rule = info.rule
                        if info.rule.find('%s') != -1:
                            src = tmp.infos_dict[info.src]
                            info_rule = info.rule % (smart_unicode(src))
                        infosearch = re.search(info_rule, data)
                        if infosearch:
                            info_value = infosearch.group(1).strip()
                            if info.build.find('%s') != -1:
                                info_value = (info.build
                                              % (smart_unicode(info_value)))
                        elif info.default != '':
                            info_value = info.default
                    else:
                        if info.build.find('%s') != -1:
                            src = tmp.infos_dict[info.src]
                            info_value = info.build % (smart_unicode(src))
                        else:
                            info_value = info.build
                    tmp.infos_dict[info.name] = info_value
                for info_name, info_value in tmp.infos_dict.items():
                    tmp.infos_dict[info_name] = self.infoFormatter(info_name,
                                                                   info_value,
                                                                   self.cfg)
                    if info_name + '.append' in tmp.infos_dict:
                        tmp.infos_dict[info_name] = smart_unicode(
                            smart_unicode(info_value) + tmp.infos_dict[info_name + '.append'])
                tmp.infos_dict['url'] = smart_unicode(item_rule.url_build % (smart_unicode(tmp.infos_dict['url'])))
                if item_rule.skill.find('append') != -1:
                    tmp.infos_dict['url'] = curr_url + tmp.infos_dict['url']
                if item_rule.skill.find('striptoslash') != -1:
                    curr_match = re.search(r'(.+?/)[^/]+$', current_url_page)
                    if curr_match:
                        if curr_match.group(1) == 'http://' or curr_match.group(1) == 'https://':
                            tmp.infos_dict['url'] = curr_url + '/' + tmp.infos_dict['url']
                        else:
                            if '/' in tmp.infos_dict['url']:
                                tmp.infos_dict['url'] = re.search(r'(?:.+/)?(.+)', tmp.infos_dict['url']).group(1)
                            tmp.infos_dict['url'] = curr_match.group(1) + tmp.infos_dict['url']
                if item_rule.skill.find('space') != -1:
                    try:
                        tmp.infos_dict['title'] = ' ' + tmp.infos_dict['title'].strip() + ' '
                    except:
                        pass
                for info_name, info_value in lItem.infos_dict.items():
                    if info_name not in tmp.infos_dict:
                        tmp.infos_dict[info_name] = info_value
                if item_rule.skill.find('recursive') != -1:
                    self.loadRemote(tmp.infos_dict['url'], False, tmp)
                    tmp = None
                else:
                    if item_rule.skill.find('directory') != -1:
                        one_found = True
                        if f is None:
                            f = open(str(os.path.join(cacheDir, catfilename)), 'w')
                            f.write(smart_unicode('########################################################\n'))
                            f.write(smart_unicode('#                    Temporary file                    #\n'))
                            f.write(smart_unicode('########################################################\n'))
                        try:
                            f.write(smart_unicode('title=' + tmp.infos_dict['title'] + '\n'))
                        except:
                            f.write(smart_unicode('title=...\n'))
                        for info_name, info_value in tmp.infos_dict.items():
                            if info_name != 'url' and info_name != 'title':
                                f.write(smart_unicode(info_name + '=' + info_value + '\n'))
                        f.write(smart_unicode('url=' + tmp.infos_dict['url'] + '\n'))
                    else:
                        self.items.append(tmp)
                    if item_rule.skill.find('lock') != -1:
                        lock = True
            if item_rule.curr != '':
                revid = re.compile(item_rule.curr, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for title in revid.findall(data):
                    tmp = CListItem()
                    if item_rule.skill.find('space') != -1:
                        tmp.infos_dict['title'] = '  ' + clean_safe(title.strip()) + ' (' + __language__(30106) + ')  '
                    else:
                        tmp.infos_dict['title'] = ' ' + clean_safe(title.strip()) + ' (' + __language__(30106) + ') '
                    tmp.infos_dict['url'] = curr_url
                    for info in item_rule.info_list:
                        if info.name == 'icon':
                            if info.default != '':
                                tmp.infos_dict['icon'] = info.default
                            else:
                                tmp.infos_dict['icon'] = info.build
                    for info_name, info_value in lItem.infos_dict.items():
                        if info_name not in tmp.infos_dict:
                            tmp.infos_dict[info_name] = info_value
                    if item_rule.skill.find('directory') != -1:
                        one_found = True
                        if f is None:
                            f = open(str(os.path.join(cacheDir, catfilename)), 'w')
                            f.write(smart_unicode('########################################################\n'))
                            f.write(smart_unicode('#                    Temporary file                    #\n'))
                            f.write(smart_unicode('########################################################\n'))
                        f.write(smart_unicode('title=' + tmp.infos_dict['title'] + '\n'))
                        for info_name, info_value in tmp.infos_dict.items():
                            if info_name != 'url' and info_name != 'title':
                                f.write(smart_unicode(info_name + '=' + info_value + '\n'))
                        f.write(smart_unicode('url=' + tmp.infos_dict['url'] + '\n'))
                    else:
                        self.items.append(tmp)
                    if item_rule.skill.find('lock') != -1:
                        lock = True
            if one_found:
                tmp = CListItem()
                tmp.infos_dict['url'] = catfilename
                for info in item_rule.info_list:
                    if info.name == 'title':
                        tmp.infos_dict['title'] = ' ' + info.build + ' '
                    elif info.name == 'icon':
                        if info.default != '':
                            tmp.infos_dict['icon'] = info.default
                        else:
                            tmp.infos_dict['icon'] = info.build
                for info_name, info_value in lItem.infos_dict.items():
                    if info_name not in tmp.infos_dict:
                        tmp.infos_dict[info_name] = info_value
                self.items.append(tmp)
                if item_rule.skill.find('lock') != -1:
                    lock = True
            if f is not None:
                f.write(smart_unicode('########################################################\n'))
                f.close()
        return 0


class PreferredQuality(object):
    ASK = 0
    LOW = 1
    STANDARD = 2
    HIGH = 3

    @staticmethod
    def getSortedQualities(preference):
        sorted_qualities_by_preference = {
            PreferredQuality.LOW: ('low', 'standard', 'high'),
            PreferredQuality.STANDARD: ('standard', 'low', 'high'),
            PreferredQuality.HIGH: ('high', 'standard', 'low')
        }
        return sorted_qualities_by_preference.get(preference, PreferredQuality.ASK)

    @staticmethod
    def translate(quality):
        quality_labels = {
            'low': 30056,
            'standard': 30057,
            'high': 30058
        }
        label_code = quality_labels.get(quality, 30057)
        return __language__(label_code)


class ContentFetcher(object):
    def __init__(self):
        self.lastFetchedUri = None
        self.lastFetchedContents = None

    def request(self, name, rule, url):
        request = self.buildRequest(rule, url)

        if self.isCached(request):
            return self.lastFetchedContents
        else:
            contents = self.sendRequest(name, rule, url, request)
            self.lastFetchedUri = self.getUriKey(request)
            self.lastFetchedContents = contents

        if enable_debug:
            self.dumpRequest(name, rule, url, request, contents)
        return contents

    def buildRequest(self, rule, original_url):
        if rule.data == '':
            url = rule.url % original_url
            data = None
        else:
            url = rule.url
            data = (rule.data % original_url).encode('utf8')

        req = Request(url.replace('\\/', '/'), data)
        req.add_header('User-Agent', USERAGENT)
        if rule.reference != '':
            req.add_header(
                rule.reference,
                rule.content)
        return req

    def sendRequest(self, name, rule, url, request):
        if enable_debug:
            xbmc.log('Sending HTTP-Request %s (%s)' %
                     (request.get_full_url(), name), INFO)
        try:
            cj.load(TRANSLATEPATH(cookiePath), ignore_discard=True)
            opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj))
            urllib_request.install_opener(opener)
            response = opener.open(request)
            cj.save(TRANSLATEPATH(cookiePath), ignore_discard=True)
        except urllib_error.HTTPError as e:
            xbmc.log('HTTP-Request failed %s %s' %
                     (e, request.get_full_url()), INFO)
            self.dumpRequest(name, rule, url, request, str(e))
            raise

        encoding = None
        content_type = response.headers.get('content-type', '')
        if 'charset=' in content_type:
            encoding = content_type.split('charset=')[-1]

        contents = response.read() if rule.limit == 0 else response.read(rule.limit)

        if encoding is None:
            epattern = r'<meta\s+http-equiv="Content-Type"\s+content="(?:.+?);\s+charset=(.+?)"'
            r = re.search(six.b(epattern), contents, re.IGNORECASE)
            if r:
                encoding = r.group(1).decode('latin-1') if six.PY3 else r.group(1)

        contents = contents.decode(encoding, errors='ignore') if encoding else contents.decode('latin-1', errors='ignore')
        return contents

    def isCached(self, request):
        uri = self.getUriKey(request)
        return self.lastFetchedUri == uri

    def getUriKey(self, request):
        return str(request.get_full_url()) + str(request.data)

    def dumpRequest(self, name, rule, url, request, contents):
        if six.PY2:
            f = open(os.path.join(cacheDir, name + '.html'), 'w')
        else:
            f = open(os.path.join(cacheDir, name + '.html'), 'w', encoding='utf-8')
        f.write('<Rule>\n')
        f.write('   <Url>' + rule.url + '</Url>\n')
        f.write('   <Data>' + rule.data + '</Data>\n')
        f.write('   <Reference>' + rule.reference + '</Reference>\n')
        f.write('</Rule>\n')

        f.write('<Request>\n')
        f.write('   <Url>' + str(request.get_full_url()) + '</Url>\n')
        f.write('   <Method>' + str(request.get_method()) + '</Method>\n')
        f.write('   <Data>' + str(request.data) + '</Data>\n')
        f.write('   <Headers>\n')
        for header_item in request.header_items():
            f.write('   <Header>%s: %s</Header>\n' %
                    (header_item[0], header_item[1]))
        f.write('   </Headers>\n')
        f.write('</Request>\n')

        f.write('<Response>\n')
        f.write(contents.encode('utf-8') if six.PY2 else contents)
        f.write('</Response>\n')
        f.close()


class ContentMatcher(object):
    def search(self, rule, contents):
        matches = re.search(rule.target, contents)
        if not matches:
            return ''

        match = matches.group(1).strip()
        if enable_debug:
            xbmc.log('pre-action target is %s' % match, INFO)
        if rule.action.find('unquote') != -1:
            match = unquote_safe(match)
        elif rule.action.find('decode') != -1:
            match = decode(match)
        elif rule.action.find('quote') != -1:
            match = quote_safe(match)
        elif rule.action.find('clean') != -1:
            match = clean2(match)
        elif rule.action.find('prefix') != -1:
            match = prefix(match)
        if rule.build.find('%s') != -1:
            match = rule.build % match
        if enable_debug:
            xbmc.log('target is %s' % match, INFO)

        return match


class Main(object):
    def __init__(self):
        if enable_debug:
            xbmc.log('Initializing VideoDevil', INFO)
        self.pDialog = None
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.videoExtension = '.flv'
        self.handle = 0
        self.currentlist = CCurrentList()
        self.fetcher = ContentFetcher()
        self.extFetcher = ContentFetcher()
        self.matcher = ContentMatcher()
        if enable_debug:
            xbmc.log('VideoDevil initialized', INFO)
        self.run()

    def showErrorNotification(self, errorCode):
        message = __language__(errorCode)
        xbmc.log('an error occured [%d]: %s' % (errorCode, message), INFO)
        xbmcgui.Dialog().notification(
            __addonname__, message, xbmcgui.NOTIFICATION_ERROR, sound=False)

    def getDirectLink(self, original_url):
        if enable_debug:
            xbmc.log('getting direct link (%s)' % original_url, INFO)
        original_url = original_url.strip()

        for source in self.currentlist.catcher:
            self.matchDirectLink(source, original_url)

        return self.determinePreferredLink()

    def matchDirectLink(self, source, original_url):
        if len(self.urlList) > 0 and source.quality == 'fallback':
            return

        contents = self.fetcher.request("catcher", source.rule, original_url)
        match = self.matcher.search(source.rule, contents)
        if match == '':
            return

        if source.ext_rule is not None:
            if source.ext_rule.url.find('%s') != -1:
                ext_url = source.ext_rule.url % match
            else:
                ext_url = match

            contents = self.extFetcher.request(
                "ext_catcher", source.ext_rule, ext_url)
            match = self.matcher.search(source.ext_rule, contents)
            if match == '':
                return

        hdrs = {'User-Agent': USERAGENT,
                'Referer': original_url}
        cj.load(TRANSLATEPATH(cookiePath), ignore_discard=True)
        cookies = {c.name: c.value for c in cj}
        if cookies:
            cookies = "; ".join("=".join(pair) for pair in cookies.items())
            hdrs.update({'Cookie': cookies})
        match += '|{0}'.format('&'.join(['{0}={1}'.format(key, urllib_parse.quote_plus(hdrs[key])) for key in hdrs]))
        source.match = match
        self.urlList.append(source.match)
        self.extensionList.append(source.extension)

        selection_label = PreferredQuality.translate(source.quality)
        selection_info = source.extension if source.info == '' else source.info
        self.selectionList.append(
            "%s (%s)" % (selection_label, selection_info))

    def determinePreferredLink(self):
        preference = int(addon.getSetting('video_type'))
        if enable_debug:
            xbmc.log('found %d urls, prefered video type: %d'
                     % (len(self.urlList), preference), INFO)
        if len(self.urlList) == 0:
            self.showErrorNotification(30067)
            return ''
        if len(self.urlList) == 1:
            self.videoExtension = '.' + self.extensionList[0]
            return self.urlList[0]

        sorted_qualities = PreferredQuality.getSortedQualities(preference)

        if sorted_qualities == PreferredQuality.ASK:
            selection = xbmcgui.Dialog().select(__language__(30055),
                                                self.selectionList)
            self.videoExtension = '.' + self.extensionList[selection]
            return self.urlList[selection]

        for quality in sorted_qualities:
            for source in self.currentlist.catcher:
                if source.match != '' and source.quality == quality:
                    self.videoExtension = '.' + source.extension
                    return source.match

    def playVideo(self, videoItem):
        if videoItem is None:
            return
        if videoItem.infos_dict['url'] == '':
            return
        url = videoItem.infos_dict['url']
        try:
            icon = videoItem.infos_dict['icon']
        except:
            icon = os.path.join(imgDir, 'video.png')
        try:
            title = videoItem.infos_dict['title']
        except:
            title = '...'
        try:
            urllib_request.urlretrieve(icon, os.path.join(cacheDir, 'thumb.tbn'))
            icon = os.path.join(cacheDir, 'thumb.tbn')
        except:
            if enable_debug:
                traceback.print_exc(file=sys.stdout)
            icon = os.path.join(imgDir, 'video.png')
        url = url.replace(' ', '%20')
        flv_file = url
        listitem = xbmcgui.ListItem(title)
        listitem.setArt({'thumb': icon,
                         'icon': icon})
        listitem.setInfo('video', {'Title': title})
        for info_name, info_value in videoItem.infos_dict.items():
            try:
                listitem.setInfo(type='Video',
                                 infoLabels={info_name: info_value})
            except:
                pass
        if self.currentlist.skill.find('nodownload') == -1:
            if addon.getSetting('download') == 'true':
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create('VideoDevil',
                                    '{0}[CR]{1}'.format(
                                        __language__(30050),
                                        __language__(30051))
                                    )
                flv_file = self.downloadMovie(url, title)
                self.pDialog.close()
            elif addon.getSetting('download') == 'false' and addon.getSetting('download_ask') == 'true':
                if xbmcgui.Dialog().yesno('', __language__(30052)):
                    self.pDialog = xbmcgui.DialogProgress()
                    self.pDialog.create('VideoDevil',
                                        '{0}[CR]{1}'.format(
                                            __language__(30050),
                                            __language__(30051))
                                        )
                    flv_file = self.downloadMovie(url, title)
                    self.pDialog.close()
                    if flv_file is None:
                        xbmcgui.Dialog().ok('VideoDevil Info',
                                            __language__(30053))
        else:
            flv_file = None

        if flv_file is not None and os.path.isfile(flv_file):
            if enable_debug:
                xbmc.log('Play: ' + str(flv_file), INFO)
            xbmc.Player().play(str(flv_file), listitem)
        else:
            if enable_debug:
                xbmc.log('Play: ' + str(url), INFO)
            xbmc.Player().play(str(url), listitem)
        xbmc.sleep(200)

    def downloadMovie(self, url, title):
        url = url.split('|')[0]
        if enable_debug:
            xbmc.log('Trying to download video ' + str(url), INFO)
        download_path = addon.getSetting('download_path')
        if download_path == '':
            try:
                download_path = xbmcgui.Dialog().browse(0,
                                                        __language__(30017),
                                                        'files',
                                                        '',
                                                        False,
                                                        False)
                addon.setSetting(id='download_path', value=download_path)
                if not os.path.exists(download_path):
                    os.mkdir(download_path)
            except:
                pass
        tmp_file = tempfile.mktemp(dir=download_path,
                                   suffix=self.videoExtension)
        if six.PY2:
            tmp_file = xbmc.makeLegalFilename(tmp_file)
        else:
            tmp_file = xbmcvfs.makeLegalFilename(tmp_file)
        url = urllib_parse.unquote(url)
        url = url.replace(' ', '%20')
        urllib_request.urlretrieve(url,
                                   tmp_file,
                                   self.video_report_hook)
        if six.PY2:
            vidfile = xbmc.makeLegalFilename(
                download_path + clean_filename(title) + self.videoExtension)
        else:
            vidfile = xbmcvfs.makeLegalFilename(
                download_path + clean_filename(title) + self.videoExtension)
        try:
            os.rename(tmp_file, vidfile)
            return vidfile
        except:
            return tmp_file

    def video_report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, "{0}[CR]{1}".format(__language__(30050), __language__(30051)))
        if self.pDialog.iscanceled():
            raise KeyboardInterrupt

    def TargetFormatter(self, url):  # Site specific target url handling
        if 'tukif' in url:
            url = url + '|Referer=http://www.tukif.com'
        if r':\/\/' in url:
            url = url.replace(r'\/', '/')
        return url

    def parseView(self, url):
        url = urllib_parse.unquote(url)
        lItem = self.currentlist.decodeUrl(url)
        url = lItem.infos_dict['url']
        ext = self.currentlist.getFileExtension(url)
        if ext == 'cfg' or ext == 'list':
            result = self.currentlist.loadLocal(url, lItem=lItem)
        elif ext == 'add':
            url = urllib_parse.unquote_plus(url)
            self.currentlist.addItem(url[:len(url) - 4])
            return -2
        elif ext == 'remove':
            if xbmcgui.Dialog().yesno('', __language__(30054)):
                url = urllib_parse.unquote_plus(url)
                self.currentlist.removeItem(url[:len(url) - 7])
                xbmc.executebuiltin('Container.Refresh')
            return -2
        elif ext == 'videodevil' or ext == 'dwnlddevil':
            url = urllib_parse.unquote_plus(url)
            url = url[:len(url) - 11]
            cfg_file = lItem.infos_dict['cfg']
            if lItem.infos_dict['type'] == 'video':
                self.currentlist.loadLocal(cfg_file, False, lItem, True)
                url = self.getDirectLink(url)

            url = self.TargetFormatter(url)
            lItem.infos_dict['url'] = url

            if 'extension' in lItem.infos_dict:
                self.videoExtension = '.' + lItem.infos_dict['extension']
            if ext == 'videodevil':
                result = self.playVideo(lItem)
            else:
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create('VideoDevil',
                                    "{0}[CR]{1}".format(
                                        __language__(30050),
                                        __language__(30051))
                                    )
                self.downloadMovie(lItem.infos_dict['url'],
                                   lItem.infos_dict['title'])
                self.pDialog.close()
            return -2
        else:
            result = self.currentlist.loadRemote(lItem.infos_dict['url'],
                                                 lItem=lItem)

        xbmcplugin.addSortMethod(handle=self.handle,
                                 sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setContent(self.handle, 'movies')
        if self.currentlist.sort.find('label') != -1:
            xbmcplugin.addSortMethod(handle=self.handle,
                                     sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        if self.currentlist.sort.find('size') != -1:
            xbmcplugin.addSortMethod(handle=self.handle,
                                     sortMethod=xbmcplugin.SORT_METHOD_SIZE)
        if self.currentlist.sort.find('duration') != -1:
            xbmcplugin.addSortMethod(handle=self.handle,
                                     sortMethod=xbmcplugin.SORT_METHOD_DURATION)
        if self.currentlist.sort.find('genre') != -1:
            xbmcplugin.addSortMethod(handle=self.handle,
                                     sortMethod=xbmcplugin.SORT_METHOD_GENRE)
        if self.currentlist.sort.find('rating') != -1:
            xbmcplugin.addSortMethod(handle=self.handle,
                                     sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if self.currentlist.sort.find('date') != -1:
            xbmcplugin.addSortMethod(handle=self.handle,
                                     sortMethod=xbmcplugin.SORT_METHOD_DATE)

        if self.currentlist.skill.find('play') != -1 \
           and self.currentlist.videoCount() == 1:
            url = self.currentlist.codeUrl(self.currentlist.getVideo(),
                                           'videodevil')
            result = self.parseView(url)
        else:
            if url == 'sites.list':
                self.currentlist.items = [item for item in self.currentlist.items if addon.getSetting(item.infos_dict['title']) == 'true']
            for m in self.currentlist.items:
                try:
                    m_type = m.infos_dict['type']
                except:
                    m_type = 'rss'
                m_icon = m.infos_dict['icon']
                m_title = clean_safe(m.infos_dict['title'])
                if m_type == 'rss' or m_type == 'search':
                    self.addListItem(m_title,
                                     self.currentlist.codeUrl(m),
                                     m_icon,
                                     len(self.currentlist.items),
                                     m)
                elif m_type.find('video') != -1:
                    self.addListItem(m_title,
                                     self.currentlist.codeUrl(m, 'videodevil'),
                                     m_icon,
                                     len(self.currentlist.items),
                                     m)
        return result

    def addListItem(self, title, url, icon, totalItems, lItem):
        # Remove \ in json urls
        url = url.replace(r'\/', '/')
        url = url.replace('%5C%2F', '%2F')
        icon = icon.replace(r'\/', '/')
        # in Frodo url parameters need to be encoded
        # ignore characters that can't be converted to ascii
        url = url.encode('utf-8', errors='ignore') if six.PY2 else url
        quoted_url = urllib_parse.quote(url)
        u = sys.argv[0] + '?url=' + quoted_url

        if ' ' in icon:  # Some sites such as hentaigasm have space character in thumbnail
            icon = urllib_parse.quote(icon, safe=':/')
        if '$HEADERS$' in icon:
            icon = icon.replace('$HEADERS$', '|')
        if 'http' in icon and 'User-Agent' not in icon:  # Some sites such as vmasala reject Kodi User-Agent
            icon += '|User-Agent=%s' % USERAGENT if '|' not in icon else '&User-Agent=%s' % USERAGENT

        liz = xbmcgui.ListItem(title)
        liz.setArt({'thumb': icon,
                    'icon': icon})
        if self.currentlist.getFileExtension(url) == 'videodevil' \
           and self.currentlist.skill.find('nodownload') == -1:
            action = 'RunPlugin(%s.dwnlddevil)' % u[:len(u) - 11]
            try:
                liz.addContextMenuItems([(__language__(30007), action)])
            except:
                pass
        if self.currentlist.skill.find('add') != -1:
            action = 'RunPlugin(%s.add)' % u
            try:
                liz.addContextMenuItems([(__language__(30010), action)])
            except:
                pass
        if self.currentlist.skill.find('remove') != -1:
            action = 'RunPlugin(%s.remove)' % u
            try:
                liz.addContextMenuItems([(__language__(30011), action)])
            except:
                pass
        for info_name, info_value in lItem.infos_dict.items():
            if info_name.find('context.') != -1:
                try:
                    cItem = lItem
                    cItem.infos_dict['url'] = info_value
                    cItem.infos_dict['type'] = 'rss'
                    action = 'RunPlugin(%s)' % (sys.argv[0] + '?url=' + self.currentlist.codeUrl(cItem))
                    liz.addContextMenuItems(
                        [(info_name[info_name.find('.') + 1:], action)])
                except:
                    pass
            if info_name.find('.append') == -1 \
               and info_name != 'url' \
               and info_name != 'title' \
               and info_name != 'icon' \
               and info_name != 'type' \
               and info_name != 'extension' \
               and info_name.find('.tmp') == -1 \
               and info_name.find('.append') == -1 \
               and info_name.find('context.') == -1:
                try:
                    if info_name.find('.int') != -1:
                        liz.setInfo('Video',
                                    infoLabels={(info_name[:info_name.find('.int')]).capitalize(): int(info_value)})
                    elif info_name.find('.once') != -1:
                        liz.setInfo('Video',
                                    infoLabels={(info_name[:info_name.find('.once')]).capitalize(): info_value})
                    else:
                        liz.setInfo('Video',
                                    infoLabels={(info_name).capitalize(): info_value})
                except:
                    pass

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=u,
                                    listitem=liz,
                                    isFolder=True,
                                    totalItems=totalItems)

    def purgeCache(self):
        for root, dirs, files in os.walk(cacheDir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

    def run(self):
        if enable_debug:
            xbmc.log('VideoDevil running', INFO)
        try:
            self.handle = int(sys.argv[1])
            paramstring = sys.argv[2]
            if len(paramstring) <= 2:
                if addon.getSetting('hide_warning') == 'false':
                    if six.PY2:
                        msg = "{0} {1} {2}".format(__language__(30062).encode('utf8'),
                                                   __language__(30063).encode('utf8'),
                                                   __language__(30064).encode('utf8'))
                        nolabel = __language__(30065).encode('utf8')
                        yeslabel = __language__(30066).encode('utf8')
                        heading = __language__(30061).encode('utf8')
                    else:
                        msg = "{0} {1} {2}".format(__language__(30062),
                                                   __language__(30063),
                                                   __language__(30064))
                        nolabel = __language__(30065)
                        yeslabel = __language__(30066)
                        heading = __language__(30061)
                    if not xbmcgui.Dialog().yesno(heading,
                                                  msg,
                                                  nolabel=nolabel,
                                                  yeslabel=yeslabel):
                        return
                if enable_debug:
                    xbmc.log('Settings directory: ' + str(settingsDir), INFO)
                    xbmc.log('Cache directory: ' + str(cacheDir), INFO)
                    xbmc.log('Resource directory: ' + str(resDir), INFO)
                    xbmc.log('Image directory: ' + str(imgDir), INFO)
                if not os.path.exists(settingsDir):
                    if enable_debug:
                        xbmc.log('Creating settings directory ' + str(settingsDir), INFO)
                    os.mkdir(settingsDir)
                    if enable_debug:
                        xbmc.log('Settings directory created', INFO)
                if not os.path.exists(cacheDir):
                    if enable_debug:
                        xbmc.log('Creating cache directory ' + str(cacheDir), INFO)
                    os.mkdir(cacheDir)
                    if enable_debug:
                        xbmc.log('Cache directory created', INFO)
                if enable_debug:
                    xbmc.log('Purging cache directory', INFO)
                self.purgeCache()
                cj.clear()
                cj.save(TRANSLATEPATH(cookiePath))
                if enable_debug:
                    xbmc.log('Cache directory purged', INFO)
                self.parseView('sites.list')
                del self.currentlist.items[:]
                if enable_debug:
                    xbmc.log('End of directory', INFO)
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
            else:
                currentView = paramstring[5:]
                if enable_debug:
                    # unquote twice otherwise url is not unquoted
                    unquoted_currentView = urllib_parse.unquote(currentView)
                    unquoted_currentView = urllib_parse.unquote(unquoted_currentView)
                    xbmc.log(
                        'currentView: ' + unquoted_currentView.replace('&', '\n'), INFO)
                if self.parseView(currentView) == 0:
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    if enable_debug:
                        xbmc.log('End of directory', INFO)
        except Exception as e:
            if enable_debug:
                traceback.print_exc(file=sys.stdout)
            xbmcgui.Dialog().ok('VideoDevil Error',
                                'Error running VideoDevil.\n\nReason:\n' + str(e))
