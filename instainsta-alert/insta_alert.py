import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIGURATION EMAIL OUTLOOK
# -----------------------------
OUTLOOK_EMAIL = os.getenv("OUTLOOK_EMAIL")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# -----------------------------
# CONFIGURATION FREE MOBILE SMS
# -----------------------------
FREE_USER = os.getenv("FREE_USER")
FREE_KEY = os.getenv("FREE_KEY")

# -----------------------------
# INSTAGRAM ACCOUNT
# -----------------------------
INSTAGRAM_URL = "https://www.instagram.com/disneylandpassdlp/?__a=1&__d=dis"
LAST_POST_FILE = "last_post.json"


def send_email(subject, message):
    """Envoie un email via Outlook SMTP."""
    msg = MIMEMultipart()
    msg["From"] = OUTLOOK_EMAIL
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
        server.send_message(msg)


def send_sms(message):
    """Envoie un SMS via l'API Free Mobile."""
    url = f"https://smsapi.free-mobile.fr/sendmsg?user={FREE_USER}&pass={FREE_KEY}&msg={message}"
    requests.get(url)


def get_last_post_shortcode():
    """Récupère le shortcode du dernier post Instagram."""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(INSTAGRAM_URL, headers=headers)
    
    if response.status_code != 200:
        print("Erreur de récupération Instagram :", response.text)
        return None

    data = response.json()

    try:
        shortcode = data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["shortcode"]
        return shortcode
    except KeyError:
        print("Erreur : structure JSON inattendue.")
        return None


def load_last_saved_shortcode():
    """Charge le dernier post sauvegardé."""
    if not os.path.exists(LAST_POST_FILE):
        return None
    
    with open(LAST_POST_FILE, "r") as f:
        return json.load(f).get("shortcode")


def save_shortcode(shortcode):
    """Sauvegarde le dernier shortcode."""
    with open(LAST_POST_FILE, "w") as f:
        json.dump({"shortcode": shortcode}, f)


def main():
    print("➡️ Vérification du dernier post Instagram…")

    latest_shortcode = get_last_post_shortcode()
    if not latest_shortcode:
        print("Impossible de récupérer le dernier post.")
        return

    last_saved = load_last_saved_shortcode()

    if last_saved == latest_shortcode:
        print("Aucun nouveau post 📭")
        return

    # Nouveau post !
    print("🔥 Nouveau post détecté !")

    post_url = f"https://www.instagram.com/p/{latest_shortcode}/"

    # EMAIL
    try:
        send_email(
            "🚨 Nouveau post Instagram !",
            f"@disneylandpassdlp a publié un nouveau post !\n\nLien : {post_url}"
        )
        print("📩 Email envoyé !")
    except Exception as e:
        print("Erreur envoi email :", e)

    # SMS
    try:
        send_sms(f"Nouveau post IG ! {post_url}")
        print("📱 SMS envoyé !")
    except:
        print("Erreur envoi SMS.")

    # Sauvegarde du shortcode
    save_shortcode(latest_shortcode)
    print("💾 Shortcode sauvegardé.")


if __name__ == "__main__":
    main()
