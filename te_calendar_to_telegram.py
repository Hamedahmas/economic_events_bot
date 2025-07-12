import tradingeconomics as te
from datetime import datetime
import pytz
from telegram import Bot

# 🟡 API KEY - شما باید آن را از سایت TradingEconomics دریافت و جایگزین کنید
TE_API_KEY = 'guest:6fdc38bb-abcd-1234-9aaa-78e92bdcf4fe'  # ← حتماً جایگزین شود

# 🔹 تلگرام
BOT_TOKEN = '8152855589:AAHJuCR3tba9uAQxJW1JBLYxNSfDb8oRf0A'
CHANNEL_ID = '-1002509441378'

# لاگین به TE API
te.login(TE_API_KEY)

# کشورها / پرچم
TARGET_COUNTRIES = {
    "United States": "🇺🇸 USA",
    "Euro Area": "🇪🇺 EUD",
    "United Kingdom": "🇬🇧 GBP",
    "Japan": "🇯🇵 JPY",
    "Canada": "🇨🇦 CAD",
    "Australia": "🇦🇺 AUD"
}

# رویدادهای هدف
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
    data = te.getCalendarData(output_type='dict')
    events = []

    for ev in data:
        country = ev.get('Country')
        category = ev.get('Category')
        date_str = ev.get('Date')

        if not country or country not in TARGET_COUNTRIES:
            continue

        matched = next((k for k in KEYWORDS if k.lower() in (category or '').lower()), None)
        if not matched:
            continue

        dt_utc = datetime.fromisoformat(date_str)
        dt_tehran = dt_utc.astimezone(pytz.timezone('Asia/Tehran'))

        events.append({
            'country': country,
            'event': matched,
            'fa_event': KEYWORDS[matched],
            'time': dt_tehran.strftime('%Y/%m/%d | %H:%M')
        })

    return events

def format_message(events):
    message = "📆 تاریخ و زمان انتشار:\n\n"
    for country, flag in TARGET_COUNTRIES.items():
        message += f"{flag}\n\n"
        for key, fa in KEYWORDS.items():
            e = next((ev for ev in events if ev['country'] == country and ev['event'] == key), None)
            t = e['time'] if e else "—"
            message += f"{key} ({fa})\n{t}\n\n"
        message += "—————————————————-\n"
    return message.strip()

def send_to_telegram(text):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text=text)

if __name__ == "__main__":
    events = fetch_te_events()
    msg = format_message(events)
    send_to_telegram(msg)
