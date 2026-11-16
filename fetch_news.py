import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

VK_TOKEN = os.environ.get("VK_TOKEN") or "ВСТАВЬТЕ_СЮДА_СЕРВИСНЫЙ_КЛЮЧ_VK"

GROUPS = [
    {"domain": "raenza", "name": "Раёнза • ://vk.com"},
    {"domain": "novoperedelkinomos", "name": "Ново-Переделкино • ://vk.com"}
]

def fetch_group_posts(domain, source_name):
    params = urllib.parse.urlencode({
        "domain": domain,
        "count": 10,
        "filter": "owner",
        "access_token": VK_TOKEN,
        "v": "5.199"
    })
    url = f"https://vk.com?{params}"
    req = urllib.request.urlopen(url, timeout=15)
    data = json.loads(req.read().decode("utf-8"))
    
    posts = []
    if "response" not in data:
        print(f"Ошибка VK API для {domain}:", data)
        return posts

    for item in data["response"]["items"]:
        if item.get("marked_as_ads") == 1 or item.get("is_pinned") == 1:
            continue
        text = item.get("text", "").strip()
        if len(text) < 25:
            continue

        image_url = ""
        for att in item.get("attachments", []):
            if att.get("type") == "photo":
                sizes = att["photo"].get("sizes", [])
                if sizes:
                    image_url = sorted(sizes, key=lambda s: s["width"])[-1]["url"]
                    break

        dt = datetime.fromtimestamp(item["date"]).strftime("%d.%m %H:%M")
        owner_id = item["owner_id"]
        post_id = item["id"]

        posts.append({
            "timestamp": item["date"],
            "source": domain,
            "source_name": source_name,
            "date": dt,
            "text": text[:360] + ("..." if len(text) > 360 else ""),
            "image": image_url,
            "url": f"https://vk.com{owner_id}_{post_id}"
        })
    return posts

if __name__ == "__main__":
    all_news = []
    for g in GROUPS:
        all_news.extend(fetch_group_posts(g["domain"], g["name"]))
    
    all_news.sort(key=lambda x: x["timestamp"], reverse=True)
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(all_news[:20], f, ensure_ascii=False, indent=2)
    print(f"Успешно сохранено новостей: {len(all_news[:20])}")
