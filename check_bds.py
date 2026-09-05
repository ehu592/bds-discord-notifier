import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API_URL = "https://net-secondary.web.minecraft-services.net/api/v1.0/download/links"
OFFICIAL_PAGE = "https://www.minecraft.net/en-us/download/server/bedrock"
STATE_FILE = Path("state.json")
INITIAL_VERSION = os.environ.get("INITIAL_VERSION", "1.26.45.1")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def get_latest():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)

    for link in data["result"]["links"]:
        if link.get("downloadType") == "serverBedrockLinux":
            url = link["downloadUrl"]
            m = re.search(r"bedrock-server-([0-9.]+)\.zip$", url)
            if not m:
                raise RuntimeError(f"Unexpected official BDS URL: {url}")
            return m.group(1), url

    raise RuntimeError("Official Linux BDS download link was not found")


def load_state():
    if not STATE_FILE.exists():
        return INITIAL_VERSION
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return data.get("version", INITIAL_VERSION)


def save_state(version):
    STATE_FILE.write_text(
        json.dumps({"version": version}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def version_key(v):
    return tuple(int(x) for x in v.split("."))


def notify(old, new, url):
    if not WEBHOOK_URL:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

    payload = {
        "username": "Minecraft BDS Monitor",
        "embeds": [
            {
                "title": "Minecraft Bedrock Dedicated Server 更新",
                "description": "Minecraft公式のLinux版BDSに新バージョンが公開されました。",
                "url": OFFICIAL_PAGE,
                "fields": [
                    {"name": "旧バージョン", "value": f"`{old}`", "inline": True},
                    {"name": "新バージョン", "value": f"`{new}`", "inline": True},
                    {"name": "公式BDS ZIP", "value": f"[ダウンロード]({url})", "inline": False},
                ],
            }
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "Minecraft-BDS-Monitor"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 204):
            raise RuntimeError(f"Discord webhook returned HTTP {r.status}")


def main():
    latest, url = get_latest()
    last = load_state()
    print(f"Official Linux BDS: {latest}")
    print(f"Last notified:      {last}")
    print(f"Official ZIP:       {url}")

    if version_key(latest) > version_key(last):
        print(f"New version detected: {last} -> {latest}")
        notify(last, latest, url)
        save_state(latest)
        print("Discord notification sent.")
    else:
        print("No update.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
