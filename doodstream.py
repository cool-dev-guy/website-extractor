## Doodstream
- Extractor:
```py
import requests
import re
from bs4 import BeautifulSoup
dood_url = "https://d000d.com/e/8va6oxwxwutw/" #/e/ for streams and /d/ for download.but /d/ has g-recaptcha ,hard and ime consuming and /e/ is turnstile and easy.
print(dood_url)

resp = requests.get(dood_url)
pattern = r"/pass_md5/[\w-]+/[\w-]+"

# Find the text using regex
match = re.search(pattern, resp.text)

# Check if a match is found
if match:
    text = match.group()
    print("PASS:", text)
else:
    print("No match found.")
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'd0000d.com',
    'Referer': 'https://d0000d.com/'+dood_url.replace("https://dood.yt/",''),# this redirects [TODO:add a proper solution]
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
# get auth stuff.
pattern = r'return a \+ "(\?token=[^"]+&expiry=)"'
match = re.search(pattern, resp.text)
resp = requests.get("https://d0000d.com"+text,headers=headers)
import time
import random
import string
if match:
    extracted_text = match.group(1)
    print("Extracted url:", resp.text + ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + extracted_text + str(int(time.time() * 1000)))
else:
    print("No match found.")
```

- Downloading:
```shell
curl 'EXTRACTED_LINK' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: en-GB,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://d000d.com/' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: cross-site' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36' \
  --compressed \
  --output output.mp4
```
