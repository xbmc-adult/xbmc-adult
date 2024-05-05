import sys
import os
import singledispatch
import xbmc
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '/../', 'script.module.livestreamer', 'lib', 'livestreamer'))
#, 'resources', 'site-packages','livestreamer', 'src'))
# from script.module.livestreamer.lib import livestreamer
from urllib import unquote_plus
from livestreamer import streams as getStreams, Livestreamer
from livestreamer.stream import HTTPStream, RTMPStream
#import livestreamer
import uuid
from xbmcswift2 import Plugin
#from stream import HTTPStream, RTMPStream

plugin = Plugin()


def first_or_none(x):
    if x and len(x) > 0:
        return x[0]

def get_proxy_cache(cid=None, region='proxy-cache', ttl=5, **values):
    # cache the info for a short period of time
    # the cache will be refreshed by the proxy daemon to keep the base urls up-to-date.
    cache = plugin.get_storage(region, TTL=ttl)
    cache.update(**values)

    return cid or uuid.uuid4().hex, cache

def generate_proxy_url(cache_id):
    http_port = plugin.get_setting('listen_port', int)
    return "http://localhost:{port}/proxy/{id}".format(port=http_port, id=cache_id)

@plugin.route('/play/<url>')
def play_stream(url):
    url = unquote_plus(url)
    if url is None: url = first_or_none(plugin.request.args.get('url'))
    plugin.log.info("\n****URL TO PLAY {0}\n".format(url))
    if not url:
        plugin.notify("No URL to stream provided")
        return []

    plugin.log.info("Trying to find a stream to play on {0}".format(url))
    session = Livestreamer()
    streams = session.streams(url)
    #qual = plugin.request.args.get('q', 'best')
    #label = plugin.request.args.get('label', 'stream')
    #stream = streams.get(qual)
    label = 'mobile_480p'
    qual='best'
    stream = streams.get(qual)
    plugin.log.info("STREAM = {0}".format(str(repr(stream))))
    vidurl = ''
    if stream is None:
        qlist = ','.join(streams.keys())
        plugin.log.error("Failed to find stream with the requested quality "
                         "({0}) with URL: {1} "
                         "(qualities available: {2})".format(qual, url, qlist or "N/A"))
        plugin.notify("No streams available for this URL, Geo-Locked?")
    else:
        if isinstance(stream, (HTTPStream, )):
            vidurl = stream.url
            #plugin.set_resolved_url(stream.url)
        elif isinstance(stream, (RTMPStream,)):
            rtmp = stream.params.pop('rtmp')
            args = ["{0}={1}".format(k, v) for k, v in stream.params.items()]
            vidurl = '{0} {1}'.format(rtmp, " ".join(args))
            item = {
                'label': label,
                'path': vidurl
            }
            #plugin.play_video(item)
        else:
            cache_id, cache = get_proxy_cache(stream=stream)
            vidurl = generate_proxy_url(cache_id)
            #plugin.set_resolved_url(vidurl)
        plugin.log.info("Resolved: {0}".format(vidurl))
        if vidurl is not None and len(vidurl) > 0:
            xbmc.Player().play(vidurl)
            return plugin.finish()

if __name__ == '__main__':
    plugin.run()
