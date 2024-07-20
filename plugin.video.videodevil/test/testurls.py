import urllib.request
import re
from pathlib import Path
from urllib.request import Request, urlopen

def print_regex_matches(content: str, pattern: str) -> None:
    regex = re.compile(pattern, re.IGNORECASE + re.DOTALL + re.MULTILINE)
    matches = regex.findall(content,  re.IGNORECASE + re.DOTALL + re.MULTILINE)
    if not matches:
        # raise ValueError("No matches found for the given pattern: " + pattern)
        print("************ ERROR ************")
        print("No matches found for the given pattern: " + pattern)
    for match in matches:
        print(match)
    print("Found " + str(len(matches)) + " matches with pattern " + pattern)

def download_webpage(url: str) -> str:
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
    return urlopen(req).read().decode('utf-8')

def read_first_values(file_path, keys_to_extract):
    first_values = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            # Strip whitespace and ignore empty lines/comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Split the line into key and value parts
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Store the first occurrence of the desired keys
                if key in keys_to_extract and key not in first_values:
                    first_values[key] = value
    
    return first_values

directory = Path('../resources')
file_extension = '.cfg'

#for file_path in directory.glob(f'*{file_extension}'):
#    print("Found file " + str(file_path))
#    values = read_first_values(file_path, {'start', 'item_infos'})
#    print(values)
#    webpage = download_webpage(values['start'])
#    print_regex_matches(webpage, values['item_infos'])
#    print()

values = read_first_values('../resources/xhamster.com.cfg', {'start', 'item_infos'})
print(values)
webpage = download_webpage(values['start'])
print(webpage)
print_regex_matches(webpage, values['item_infos'])

#url = "https://www.pornoxo.com/videos/newest/"
#item_infos="<li\\s*class=\"js-pop.+?a href=\"([^\"]+).+<img\\s*src=\"([^\"])\"\\s*alt=\"([^\"])\".+?<span[^>]+>\\s*([\\d:]+)"
#item_infos="<li\\s*class=\"js-pop.+?a href=\"([^\"]+).+?<img[^>]*src=\"([^\"]+)\"[^>]*alt=\"([^\"]+)\".+?<span[^>]+>\\s*([\\d:]+)"

#url = "https://www.eporner.com/"
#item_infos="<img[^<]+src=\"([^\"]+/thumbs[^\"]+)\" data-st=\"[^\"]+\".+?<a href=\"([^\"]+)\">([^<]+)</a>.+?<span class=\"mbtim\" title=\"Duration\">([^<]+)</span>"

#url = "https://www.sunporno.com/most-recent/"
#item_infos="<span class=\"btime tm\">([\\d:]+)<.+?<img[^>]+data-src=\"([^\"]+)\".+?<a[^>]+href=\"([^\"]+)\".+?<span class=\"video-title\">([^<]+)"

#content = download_webpage(url)
#print(url)
#print(content)
#print_regex_matches(content, item_infos)
