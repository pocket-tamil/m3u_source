import requests

SOURCES = [
    "https://sscloud7.in/multi/tamilott.json",
    "https://as.al/raw/NyCqwJ",
    "https://livetv.ashokadigital.net/api/api.php?get_posts=&page=1&count=361&api_key=cda11bx8aITlKsXdsfafadskljasldfjoierKLrteaadfjalM<",
    "https://tavapi.inditechman.com/api/tamiltvapp.json",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_FILE = "local_channels.m3u"

playlist = ["#EXTM3U\n\n"]
seen = set()


def add_channel(name, logo, url):
    """Add a channel to the M3U playlist."""

    if not url:
        return

    url = str(url).strip()

    if not url:
        return

    # Remove duplicate stream URLs
    if url in seen:
        return

    seen.add(url)

    name = str(name or "Unknown").strip()
    logo = str(logo or "").strip()

    playlist.append(
        f'#EXTINF:-1 tvg-name="{name}" '
        f'tvg-logo="{logo}" '
        f'group-title="Local TV",{name}\n'
    )

    playlist.append(url + "\n\n")


def parse_item(item, source):
    """Parse one channel object."""

    if not isinstance(item, dict):
        return

    # --------------------------------------------------
    # CHANNEL NAME
    # --------------------------------------------------

    name = (
        item.get("channel_name")       # Ashoka Digital
        or item.get("channelname")     # SSCloud7
        or item.get("name")            # TamilTVApp
        or item.get("title")
        or item.get("content_title")
        or item.get("channel")
        or "Unknown"
    )

    # --------------------------------------------------
    # CHANNEL LOGO
    # --------------------------------------------------

    logo = (
        item.get("channel_image")      # Ashoka Digital
        or item.get("logo")            # TamilTVApp / SSCloud7
        or item.get("channel_logo")
        or item.get("image")
        or item.get("thumbnail")
        or item.get("poster")
        or item.get("logo_url")
        or ""
    )

    # --------------------------------------------------
    # ASHOKA DIGITAL LOGO
    # --------------------------------------------------

    if "ashokadigital.net" in source and logo:

        if not logo.startswith(("http://", "https://")):

            logo = (
                "https://livetv.ashokadigital.net/upload/logo/"
                + logo
            )

    # --------------------------------------------------
    # STREAM URL
    # --------------------------------------------------

    url = (
        item.get("channel_url")        # Ashoka Digital
        or item.get("playbackurl")     # SSCloud7
        or item.get("stream_url")
        or item.get("content_url")
        or item.get("url")             # TamilTVApp
        or item.get("link")
        or item.get("stream")
        or item.get("play_url")
        or ""
    )

    add_channel(name, logo, url)


def parse_data(data, source):
    """Recursively parse JSON data."""

    # --------------------------------------------------
    # LIST
    # --------------------------------------------------

    if isinstance(data, list):

        for item in data:

            if not isinstance(item, dict):
                continue


            if "channeldata" in item:

                parse_data(
                    item["channeldata"],
                    source
                )


            elif "channels" in item:

                parse_data(
                    item["channels"],
                    source
                )

            else:

                parse_item(
                    item,
                    source
                )
                
    elif isinstance(data, dict):


        possible_url = (
            data.get("channel_url")
            or data.get("playbackurl")
            or data.get("stream_url")
            or data.get("content_url")
            or data.get("url")
            or data.get("link")
            or data.get("stream")
            or data.get("play_url")
        )

        if possible_url:

            parse_item(
                data,
                source
            )

        for key in (
            "channeldata",
            "channels",
            "data",
            "results",
            "posts",
            "items",
            "list",
        ):

            if key not in data:
                continue

            value = data[key]

            if isinstance(value, (list, dict)):

                parse_data(
                    value,
                    source
                )


# ======================================================
# DOWNLOAD ALL SOURCES
# ======================================================

for source in SOURCES:

    print()
    print("=" * 60)
    print(f"Downloading: {source}")
    print("=" * 60)

    try:

        response = requests.get(
            source,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        before = len(seen)

        parse_data(
            data,
            source
        )

        added = len(seen) - before

        print(f"Added: {added} channels")

    except requests.exceptions.RequestException as e:

        print(f"Request error: {e}")

    except ValueError as e:

        print(f"Invalid JSON: {e}")

    except Exception as e:

        print(f"Error: {e}")


# ======================================================
# WRITE M3U
# ======================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.writelines(
        playlist
    )


print()
print("=" * 60)
print("PLAYLIST GENERATED")
print("=" * 60)
print(f"Total unique channels : {len(seen)}")
print(f"Output file            : {OUTPUT_FILE}")
print("=" * 60)
