import sys
import subprocess

# -- 1) Install or import necessary packages --
try:
    import requests
    from icalendar import Calendar
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "icalendar"])
    import requests
    from icalendar import Calendar

import datetime

# === YOUR TELEGRAM BOT CREDENTIALS ===
TELEGRAM_BOT_TOKEN = "7868529870:AAGmCa02RDIZDNsrrrydtCiixfOUbylgWtM"
TELEGRAM_CHAT_ID = "7749183977"

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
    except Exception as e:
        # Return an empty list or you can raise an error. We'll do empty list & send error to Telegram.
        send_telegram_message(f"Failed to fetch iCal for {property_name} ({platform}): {e}")
        return reservations

    # Parse the iCal
    try:
        calendar = Calendar.from_ical(ical_data)
        for component in calendar.walk():
            if component.name == "VEVENT":
                dtstart = component.get("DTSTART").dt
                dtend   = component.get("DTEND").dt

                summary = component.get("SUMMARY", "")
                description = component.get("DESCRIPTION", "")

                guest_name = "Unknown"
                phone_number = "Unknown"

                # If it's from Booking.com, they often have "Closed - Not Available" for booked dates
                # We'll unify that as "Reserved"
                if summary.strip().lower() == "closed - not available":
                    guest_name = "Reserved"
                    phone_number = "N/A"
                else:
                    # Try a basic parse if "Name:" or "Phone:" appear
                    if "Name:" in summary:
                        parts = summary.split(',')
                        for part in parts:
                            part = part.strip()
                            if "Name:" in part:
                                guest_name = part.split("Name:")[1].strip()
                            if "Phone:" in part:
                                phone_number = part.split("Phone:")[1].strip()
                    else:
                        # For Airbnb, often the summary might show "Reserved: John Doe"
                        # or "John Doe (2 guests)" or some variant. We'll store it directly as fallback:
                        guest_name = summary

                reservations.append({
                    "property_name": property_name,
                    "platform": platform,
                    "checkin": dtstart,
                    "checkout": dtend,
                    "guest_name": guest_name,
                    "phone": phone_number,
                    "raw_summary": summary,
                    "raw_description": description,
                })
    except Exception as e:
        send_telegram_message(f"Failed to parse iCal for {property_name} ({platform}): {e}")
        # Return what was parsed so far or an empty list
        return reservations

    return reservations

def main():
    all_reservations = []

    # 1) Fetch & parse each iCal
    for cal in calendars:
        prop = cal["property_name"]
        platform = cal["platform"]
        url = cal["url"]

        these_reservations = fetch_and_parse_ical(url, prop, platform)
        all_reservations.extend(these_reservations)

    # 2) Filter for check-ins or check-outs that occur "today"
    today = datetime.date.today()
    todays_events = []

    for r in all_reservations:
        checkin_date = r["checkin"].date() if hasattr(r["checkin"], 'date') else r["checkin"]
        checkout_date = r["checkout"].date() if hasattr(r["checkout"], 'date') else r["checkout"]

        if checkin_date == today or checkout_date == today:
            todays_events.append(r)

    # 3) Format the message
    if not todays_events:
        message = "No check-ins/check-outs today for any property."
    else:
        lines = []
        for evt in todays_events:
            lines.append(
                f"Property: {evt['property_name']}\n"
                f"Platform: {evt['platform']}\n"
                f"Guest: {evt['guest_name']}\n"
                f"Phone: {evt['phone']}\n"
                f"Check-in: {evt['checkin']}\n"
                f"Check-out: {evt['checkout']}\n"
                "------------------------"
            )
        message = "\n".join(lines)

    # 4) Send single Telegram message
    send_telegram_message(message)

if __name__ == "__main__":
    main()