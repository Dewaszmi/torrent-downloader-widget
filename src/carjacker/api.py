import asyncio
from pathlib import Path

import httpx
import json


async def find_jackett_torrents(search_query: str):
    JACKETT_URL = "http://localhost:9117/api/v2.0/indexers/all/results"

    # Get Jackett API key from the config file
    jackett_config_path = Path("~/.config/Jackett/ServerConfig.json").expanduser()
    with open(jackett_config_path) as f:
        json_data = json.load(f)
        api_key = json_data.get("APIKey")

    print(api_key)

    params = {
        "apikey": api_key,
        "Query": search_query,
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url=JACKETT_URL, params=params)
            r.raise_for_status()
            results = r.json()["Results"]
    except httpx.HTTPStatusError as e:
        print(f"Server returned an error: {e.response.status_code}")
        return []
    except httpx.RequestError as e:
        print(f"An error occured while requesting {e.request.url!r}: {e}")
        return []

    result_array = []
    for item in results:
        result_array.append(
            {
                "Title": item["Title"],
                "Tracker": item["Tracker"],
                "Category": item["CategoryDesc"],
                "Seeders": item["Seeders"],
                "MagnetUrl": item["MagnetUri"],
            }
        )

    return result_array


if __name__ == "__main__":
    asyncio.run(find_jackett_torrents(search_query="The Matrix"))
