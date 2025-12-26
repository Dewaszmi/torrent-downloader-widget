# download script utilising Ryuk-me's torrent service API (https://github.com/Ryuk-me/Torrent-Api-py)
from pathlib import Path
import requests
import json

download_dir = Path.cwd() / "torrent_dir"
download_dir.mkdir(parents=True, exist_ok=True)

# with open('test.json', 'r', encoding='utf-8') as f:
#     json_data = f.read()
#     json_data = json.loads(json_data)["data"]

r = requests.get("http://localhost:8009/api/v1/all/search?query=avengers&limit=5")
json_data = r.json()["data"]

for entry in json_data:
    torrent_url = entry.get("torrent")
    if torrent_url is None:
        continue

    name = entry["name"]
    torrent_url = entry["torrent"]
    print(f"Torrent: {torrent_url}")
    r = requests.get(torrent_url)
    if r.status_code == 200:
        save_file = download_dir / f"{name}.torrent"
        save_file.write_bytes(r.content)
