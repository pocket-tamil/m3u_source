import requests

SOURCES = [
    "https://sscloud7.in/multi/tamilott.json",
    "https://as.al/raw/NyCqwJ",
    "https://livetv.ashokadigital.net/api/api.php?get_posts=&page=1&count=361&api_key=cda11bx8aITlKsXdsfafadskljasldfjoierKLrteaadfjalM",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_FILE = "local_channels.m3u"

playlist = ["#EXTM3U\n\n"]
seen = set()


def add_channel(name, logo, url):
    """Add a channel to the playlist."""

    if not url:
        return

    url = url.strip()

    if not url:
        return

    if url in seen:
        return

    seen.add(url)

    name = (name or "Unknown").strip()
    logo = (logo or "").strip()

    playlist.append(
        f'#EXTINF:-1 tvg-name="{name}" '
        f'tvg-logo="{logo}" '
        f'group-title="Local TV",{name}\n'
    )
    playlist.append(url + "\n\n")


def parse_item(item, source):
    """Parse a channel item."""

    name = (
        item.get("channelname")
        or item.get("name")
        or item.get("title")
        or item.get("channel_name")
        or item.get("content_title")
        or "Unknown"
    )

    logo = (
        item.get("logo")
        or item.get("image")
        or item.get("thumbnail")
        or item.get("poster")
        or item.get("channel_logo")
        or ""
    )

    # Ashoka Digital logos are filenames only
    if "ashokadigital.net" in source and logo:
        if not logo.startswith("http"):
            logo = f"https://livetv.ashokadigital.net/upload/logo/{logo}"

    url = (
        item.get("playbackurl")
        or item.get("stream_url")
        or item.get("url")
        or item.get("link")
        or item.get("content_url")
        or item.get("channel_url")
        or ""
    )

    add_channel(name, logo, url)


for source in SOURCES:

    print(f"Downloading: {source}")

    try:
        response = requests.get(source, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print(f"Failed: {e}")
        continue

    # Root is a list
    if isinstance(data, list):

        for item in data:

            # SSCloud7 format
            if isinstance(item, dict) and "channeldata" in item:

                for channel in item.get("channeldata", []):
                    parse_item(channel, source)

            else:
                parse_item(item, source)

    # Root is a dictionary
    elif isinstance(data, dict):

        for key in (
            "channeldata",
            "channels",
            "data",
            "results",
            "items",
            "posts",
            "list",
        ):

            if key not in data:
                continue

            value = data[key]

            if isinstance(value, list):

                for channel in value:
                    parse_item(channel, source)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(playlist)

print(f"\nDone! Generated {len(seen)} unique channels.")
print(f"Saved to {OUTPUT_FILE}")
