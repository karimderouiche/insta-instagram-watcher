import requests
import re
import json
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

OUTLOOK_EMAIL = os.getenv("OUTLOOK_EMAIL")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

FREE_USER = os.getenv("FREE_USER")
FREE_KEY = os.getenv("FREE_KEY")

LAST_FILE = "last_post.json"


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = OUTLOOK_EMAIL
    msg["To"] = EMAIL_TO

    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()
    server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
    server.send_message(msg)
    server.quit()


def send_sms(message):
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
    """Scrape Instagram HTML pour extraire la première URL CDN d'image du profil."""
    url = "https://www.instagram.com/disneylandpassdlp/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "fr-FR,fr;q=0.9",
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("Erreur HTTP :", r.status_code)
        return None

    # Regex capturant toutes les URLs pointant vers le CDN Instagram
    images = re.findall(r'https://[^"]+\.cdninstagram\.com[^"]+', r.text)

    if not images:
        print("Aucune image trouvée dans le HTML.")
        return None

    # La première image = la plus récente
    return images[0]


def main():
    print("➡️ Vérification du dernier post via CDN…")

    latest_image = get_latest_image_url()
    if not latest_image:
        print("Impossible de récupérer la dernière image.")
        return

    last_saved = load_last_image()

    if last_saved == latest_image:
        print("Aucun nouveau post.")
        return

    print("🔥 NOUVEAU POST DÉTECTÉ !")

    profile_link = "https://www.instagram.com/disneylandpassdlp/"

    send_email(
        "🚨 Nouveau post Instagram !",
        f"Un nouveau post a été détecté !\n\nImage CDN : {latest_image}\nProfil : {profile_link}",
    )

    send_sms(f"Nouveau post IG ! {profile_link}")

    save_last_image(latest_image)
    print("✔ Alerte envoyée et nouvelle image sauvegardée.")


if __name__ == "__main__":
    main()
