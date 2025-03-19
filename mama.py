import sys
import subprocess
import datetime

# -- 1) Install or import necessary packages --
try:
    import requests
    from icalendar import Calendar
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "icalendar"])
    import requests
    from icalendar import Calendar

# === YOUR TELEGRAM BOT CREDENTIALS ===
TELEGRAM_BOT_TOKEN = "7868529870:AAGmCa02RDIZDNsrrrydtCiixfOUbylgWtM"
TELEGRAM_CHAT_ID = "7887131872"

# === DEFINE THE CALENDARS FOR EACH PROPERTY / PLATFORM ===
calendars = [
    {
        "property_name": "Sidi Abdellah",
        "platform": "Airbnb",
        "url": "https://www.airbnb.com/calendar/ical/1060981308110407697.ics?s=d2649e793447415c1d445c4781af698f",
    },
    {
        "property_name": "Sidi Abdellah",
        "platform": "Booking",
        "url": "https://ical.booking.com/v1/export?t=e152d86c-41dc-4f1d-9972-341d40c62034",
    },
    {
        "property_name": "Koutoubia 3eme",
        "platform": "Booking",
        "url": "https://ical.booking.com/v1/export?t=bf456c59-8ac1-4bf0-a3af-0790519d0fb4",
    },
    {
        "property_name": "Koutoubia 1er",
        "platform": "Booking",
        "url": "https://ical.booking.com/v1/export?t=9a651172-cc19-407e-a4d9-99605082d42e",
    },
    {
        "property_name": "Koutoubia 3eme",
        "platform": "Airbnb",
        "url": "https://www.airbnb.com/calendar/ical/1300954655144339364.ics?s=afec5544fb640bccc8ae62c3cea1667b",
    },
    {
        "property_name": "Koutoubia 1er",
        "platform": "Airbnb",
        "url": "https://www.airbnb.com/calendar/ical/1300952444346368409.ics?s=f0ab8f909f9c827b537f92ca8c49823e",
    },
]

def send_telegram_message(text: str):
    """Send a plain-text message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

def fetch_and_parse_ical(url: str, property_name: str, platform: str):
    """
    Fetch the iCal data from 'url' and parse into a list of reservation dicts.
    We also attach 'property_name' and 'platform' to each reservation for clarity.
    """
    reservations = []

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        ical_data = resp.text
    except Excep
