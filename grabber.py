import tldextract, requests
import sys, os, re

def parse(file):
    global lg
    with open(file, 'r') as f:
        file = f.read()
    matches = re.findall("(lg[\.|-][a-zA-Z0-9-.]*\.[a-zA-Z0-9]*)",file, re.MULTILINE | re.DOTALL)
    if matches:
        for match in matches:
            if len(match) > 5:
                domain = tldextract.extract(match).registered_domain
                if not domain in lg: lg[domain] = []
                if not match in lg[domain]: lg[domain].append(match)

def get(url):
    try:
        request = requests.get(url,allow_redirects=False,timeout=5)
        if (request.status_code == 200):
            print(f"Got {request.status_code} keeping {url}")
            return True
        else:
            print(f"Got {request.status_code} dropping {url}")
            return False
    except Exception as e:
        print(e)
    return False

if len(sys.argv) == 1:
    print("grabber.py /data/path output.json (optional)")
    sys.exit()

if len(sys.argv) == 2:
    default = sys.argv[2]
else:
     default = "default.json"
folder = sys.argv[1]
folders = os.listdir(folder)
lg = {}

print(f"Parsing {folder}")
for element in folders:
    if element.endswith(".html"):
        parse(folder+"/"+element)
    else:
        files = os.listdir(folder+"/"+element)
        for file in files:
            if file.endswith(".html"):
                parse(folder+"/"+element+"/"+file)

print("Validating")
for domain in lg:
    for url in lg[domain]:
        response = get("https://"+url)
        if response:
            continue
        else:
            response = get("http://"+url)
            if response: continue
        lg[domain].remove(url)

print(f"Saving {default}")
with open(os.getcwd()+'/'+default, 'w') as f:
    json.dump(lg, f, indent=4)
