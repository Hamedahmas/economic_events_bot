import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import os

# توکن و آی‌دی کانال از طریق GitHub Secrets
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

TARGET_COUNTRIES = {
    "USD": "🇺🇸 USA",
    "EUR": "🇪🇺 EUD",
    "GBP": "🇬🇧 GBP",
    "JPY": "🇯🇵 JPY",
    "AUD": "🇦🇺 AUD",
    "CAD": "🇨🇦 CAD"
}

TARGET_EVENTS = {
    "Interest Rate": "Interest Rate (نرخ بهره)",
    "CPI": "CPI یا Inflation Rate (تورم)",
    "Inflation Rate": "CPI یا Inflation Rate (تورم)",
    "Unemployment Rate": "Unemployment Rate (بیکاری)",
    "GDP": "GDP (تولید ناخالص داخلی)",
    "Current Account": "Current Account (حساب جاری)",
    "Government Budget": "Gov Budget Balance  (تراز بودجه دولت)",
    "Debt to GDP": "Debt to GDP (نسبت بدهی به تولید ناخالص داخلی)"
}

def fetch_events():
    url = "https://www.forexfactory.com/calendar.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.select('tr.calendar__row')

    data = []
    for row in rows:
        try:
            time_str = row.select_one('.calendar__time').text.strip()
            currency = row.select_one('.calendar__currency').text.strip()
            event = row.select_one('.calendar__event-title').text.strip()

            if currency not in TARGET_COUNTRIES:
                continue

            matched_key = next((k for k in TARGET_EVENTS if k.lower() in event.lower()), None)
            if not matched_key:
                continue

            date_row = row.find_previous('tr', class_='calendar__row--newday')
            date_str = date_row.select_one('.calendar__date').text.strip() if date_row else ''
            datetime_str = f"{date_str} {time_str}" if time_str != 'All Day' else f"{date_str} 00:00"
            full_time = datetime.strptime(datetime_str, "%b %d %Y %H:%M")

            tz = pytz.timezone("UTC")
            full_time = tz.localize(full_time)

            data.append({
                "currency": currency,
                "country": TARGET_COUNTRIES[currency],
                "event": TARGET_EVENTS[matched_key],
                "datetime": full_time.strftime("%Y/%m/%d    |    %H:%M")
            })
        except Exception:
            continue
    return data

def format_message(data):
    message = "📆تاریخ و زمان انتشار :

"
    for currency, country_name in TARGET_COUNTRIES.items():
        message += f"{country_name}

"
        for key in TARGET_EVENTS.values():
            entry = next((e for e in data if e['currency'] == currency and e['event'] == key), None)
            time = entry['datetime'] if entry else "----/--/--    |    --:--"
            message += f"{key}
{time}

"
        message += "—————————————————-
"
    return message.strip()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    events = fetch_events()
    msg = format_message(events)
    send_telegram_message(msg)
