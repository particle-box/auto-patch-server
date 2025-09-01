import requests, sys

def get_core_and_snapenhance():
    url = "https://api.github.com/repos/particle-box/SnapEnhance/releases"
    r = requests.get(url)
    r.raise_for_status()
    for rel in r.json():
        if not rel.get('prerelease', False):
            continue
        for asset in rel.get('assets', []):
            if asset['name'].lower() == "core.apk":
                print(f"Downloading {asset['name']} ...")
                core = requests.get(asset['browser_download_url'])
                with open("core.apk", "wb") as f:
                    f.write(core.content)
    print("done.")

if __name__ == '__main__':
    get_core_and_snapenhance()
