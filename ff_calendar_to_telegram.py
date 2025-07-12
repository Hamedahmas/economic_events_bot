import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
import pytz
import time

# توکن و آیدی کانال تلگرام
BOT_TOKEN = '8152855589:AAHJuCR3tba9uAQxJW1JBLYxNSfDb8oRf0A'
CHANNEL_ID = '-1002509441378'

# ارزهای هدف
TARGET_COUNTRIES = {
    'USD': '🇺🇸 USA',
    'EUR': '🇪🇺 EUD',
    'GBP': '🇬🇧 GBP',
    'JPY': '🇯🇵 JPY',
    'AUD': '🇦🇺 AUD',
    'CAD': '🇨🇦 CAD'
}

# کلیدواژه‌های مهم
KEYWORDS = {
    'Interest Rate': 'نرخ بهره',
    'CPI': 'تورم',
    'Inflation': 'تورم',
    'Unemployment': 'بیکاری',
    'GDP': 'تولید ناخالص داخلی',
    'Current Account': 'حساب جاری',
    'Budget': 'تراز بودجه دولت',
    'Debt': 'نسبت بدهی به تولید ناخالص داخلی'
}

def fetch_investing_calendar():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.select('table.genTbl.closedTbl.ecEventsTable tr.js-event-item')

    events = []

    for row in rows:
        try:
            country = row['data-country']
            currency = row['data-event-currency']
            event_title = row['data-event-name'].strip()
            date_time = row.select_one('.first.left.time') or row.select_one('.time')
            if not date_time:
                continue
            time_str = date_time.get_text(strip=True)

            # فیلتر کشور
            if currency not in TARGET_COUNTRIES:
                continue

            # تطبیق عنوان رویداد با کلیدواژه‌ها
            matched_key = next((k for k in KEYWORDS if k.lower() in event_title.lower()), None)
            if not matched_key:
                continue

            # ساخت datetime دقیق
            today = datetime.utcnow().date()
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
            else:
                continue
            dt_utc = datetime(today.year, today.month, today.day, hour, minute, tzinfo=pytz.UTC)
            dt_tehran = dt_utc.astimezone(pytz.timezone("Asia/Tehran"))

            events.append({
                'currency': currency,
                'event': matched_key,
                'fa_event': KEYWORDS[matched_key],
                'time': dt_tehran.strftime('%Y/%m/%d | %H:%M')
            })

        except Exception as e:
            print("⚠️ خطا:", e)
            continue

    return events

def format_message(events):
    message = "📆تاریخ و زمان انتشار :\n\n"
    for code, name in TARGET_COUNTRIES.items():
        message += f"{name}\n\n"
        for key, fa in KEYWORDS.items():
            e = next((ev for ev in events if ev['currency'] == code and ev['event'] == key), None)
            t = e['time'] if e else '—'
            message += f"{key} ({fa})\n{t}\n\n"
        message += "—————————————————-\n"
    return message.strip()

def send_to_telegram(message):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text=message)

if __name__ == "__main__":
    events = fetch_investing_calendar()
    print(f"✅ دریافت {len(events)} رویداد")
    for e in events:
        print(e)

    msg = format_message(events)
    send_to_telegram(msg)
