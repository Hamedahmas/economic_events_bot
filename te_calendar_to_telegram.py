import requests
from datetime import datetime
import pytz
from telegram import Bot
import os

# 🟡 خواندن متغیرها از محیط (GitHub Secrets)
TE_API_KEY = os.environ['TE_API_KEY']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']

# کشورها و پرچم‌ها
TARGET_COUNTRIES = {
    "United States": "🇺🇸 USA",
    "Euro Area": "🇪🇺 EUD",
    "Japan": "🇯🇵 JPY",
    "United Kingdom": "🇬🇧 GBP",
    "Canada": "🇨🇦 CAD",
    "Australia": "🇦🇺 AUD"
}

# رویدادهای مهم
KEYWORDS = {
    "Interest Rate": "نرخ بهره",
    "Inflation Rate": "تورم",
    "Unemployment Rate": "بیکاری",
    "GDP": "تولید ناخالص داخلی",
    "Current Account": "حساب جاری",
    "Government Budget": "تراز بودجه دولت",
    "Debt to GDP": "نسبت بدهی به تولید ناخالص داخلی"
}

def fetch_te_events():
    url = f"https://api.tradingeconomics.com/calendar?c={TE_API_KEY}&f=json"
    res = requests.get(url)
    data = res.json()

    events = []

    for event in data:
        try:
            country = event.get("Country")
            category = event.get("Category")
            datetime_str = event.get("Date")

            if not country or country not in TARGET_COUNTRIES:
                continue

            if not category:
                continue

            matched = next((k for k in KEYWORDS if k.lower() in category.lower()), None)
            if not matched:
                continue

            dt_utc = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
            dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
            dt_tehran = dt_utc.astimezone(pytz.timezone("Asia/Tehran"))

            events.append({
                "country": country,
                "event": matched,
                "fa_event": KEYWORDS[matched],
                "time": dt_tehran.strftime('%Y/%m/%d | %H:%M')
            })
        except:
            continue

    return events

def format_message(events):
    message = "📆تاریخ و زمان انتشار:\n\n"
    for country, flag in TARGET_COUNTRIES.items():
        message += f"{flag}\n\n"
        for key, fa in KEYWORDS.items():
            match = next((e for e in events if e['country'] == country and e['event'] == key), None)
            time = match['time'] if match else "—"
            message += f"{key} ({fa})\n{time}\n\n"
        message += "—————————————————-\n"
    return message.strip()

def send_to_telegram(text):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text=text)

if __name__ == "__main__":
    events = fetch_te_events()
    msg = format_message(events)
    send_to_telegram(msg)
