from xml.dom import minidom

def rss_image_scrape(url):
    pass
    #scrape = re.compile('\<title\>\<\!\[CDATA\[  By\: (.+?) \]\]\>\<\/title\>.{0,310} src="(.+?)"',re.DOTALL).findall(rss)
    #for info,url in scrape:
    #        print info,url
    xmldoc = minidom.parseString(xml)
    contents = ((xmldoc.firstChild).childNodes[1])

            
def xml_image_scrape(xml):
    
    xmldoc = minidom.parseString(xml)
    photos = xmldoc.getElementsByTagName('photo')
    for photo in photos:
        
        title = get_from_xml(photo,'title')
        url = get_from_xml(photo,'path')
        authorName = get_from_xml(photo,'authorName')
        print title,url,authorName

def get_from_xml(node,tag):
    #get node text by tag
    return read_it((node.getElementsByTagName(tag))[0].firstChild)

def read_it(node):
    #convert to text if the node is not None
    if node: node = node.toxml()
    return node
