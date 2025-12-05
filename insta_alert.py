import requests
import re
import json
import os
from dotenv import load_dotenv

load_dotenv()

FREE_USER = os.getenv("FREE_USER")
FREE_KEY = os.getenv("FREE_KEY")

LAST_FILE = "last_post.json"


def send_sms(message):
    """Envoie un SMS via l'API Free Mobile."""
    url = f"https://smsapi.free-mobile.fr/sendmsg?user={FREE_USER}&pass={FREE_KEY}&msg={message}"
    requests.get(url)


def load_last_image():
    if not os.path.exists(LAST_FILE):
        return None
    with open(LAST_FILE, "r") as f:
        return json.load(f).get("image_url")


def save_last_image(url):
    with open(LAST_FILE, "w") as f:
        json.dump({"image_url": url}, f)


def get_latest_image_url():
    """Scrape Instagram HTML pour extraire la première URL CDN du compte."""
    url = "https://www.instagram.com/disneylandpassdlp/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "fr-FR,fr;q=0.9",
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("Erreur HTTP :", r.status_code)
        return None

    images = re.findall(r'https://[^"]+\.cdninstagram\.com[^"]+', r.text)

    if not images:
        print("Aucune image trouvée.")
        return None

    return images[0]


def main():
    print("➡️ Vérification du dernier post via CDN…")

    latest_image = get_latest_image_url()
    if not latest_image:
        print("Impossible de récupérer l’image.")
        return

    last_saved = load_last_image()

    if last_saved == latest_image:
        print("Aucun nouveau post.")
        return

    print("🔥 Nouveau post détecté !")

    link = "https://www.instagram.com/disneylandpassdlp/"

    send_sms(f"[IG Alert] Nouveau post détecté ! {link}")

    save_last_image(latest_image)
    print("✔ SMS envoyé et nouvelle image sauvegardée.")


if __name__ == "__main__":
    main()
