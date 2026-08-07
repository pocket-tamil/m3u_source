import requests

SOURCES = [
    "https://sscloud7.in/multi/tamilott.json",
    "https://as.al/raw/NyCqwJ",
    "https://tavapi.inditechman.com/api/tamiltvapp.json",
    "https://livetv.ashokadigital.net/api/api.php?get_posts=&page=1&count=361&api_key=cda11bx8aITlKsXdsfafadskljasldfjoierKLrteaadfjalM<",
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

    if not url or url in seen:
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
    """Parse a channel from any supported JSON format."""

    # -----------------------
    # Channel Name
    # -----------------------
    name = (
        item.get("channel_name")          # Ashoka Digital
        or item.get("channelname")        # SSCloud7
        or item.get("name")
        or item.get("title")
        or item.get("content_title")
        or "Unknown"
    )

    # -----------------------
    # Logo
    # -----------------------
    logo = (
        item.get("channel_image")         # Ashoka Digital
        or item.get("logo")               # SSCloud7
        or item.get("channel_logo")
        or item.get("image")
        or item.get("thumbnail")
        or item.get("poster")
        or ""
    )

    # Ashoka Digital logo filenames
    if "ashokadigital.net" in source and logo:
        if not logo.startswith(("http://", "https://")):
            logo = (
                "https://livetv.ashokadigital.net/upload/logo/"
                + logo
            )

    # -----------------------
    # Stream URL
    # -----------------------
    url = (
        item.get("channel_url")           # Ashoka Digital
        or item.get("playbackurl")        # SSCloud7
        or item.get("stream_url")
        or item.get("content_url")
        or item.get("url")
        or item.get("link")
        or ""
    )

    add_channel(name, logo, url)


def parse_data(data, source):
    """Recursively parse JSON."""

    if isinstance(data, list):

        for item in data:

            if not isinstance(item, dict):
                continue

            # SSCloud7 nested format
            if "channeldata" in item:

                parse_data(item["channeldata"], source)

            else:
                parse_item(item, source)

    elif isinstance(data, dict):

        # Ashoka / Generic collections
        for key in (
            "channeldata",
            "channels",
            "data",
            "results",
            "posts",
            "items",
            "list",
        ):
            if key in data:
                parse_data(data[key], source)


for source in SOURCES:

    print(f"Downloading: {source}")

    try:
        response = requests.get(
            source,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        parse_data(data, source)

    except Exception as e:
        print(f"Error: {e}")


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(playlist)

print(f"\nGenerated {len(seen)} unique channels.")
print(f"Saved as {OUTPUT_FILE}")
