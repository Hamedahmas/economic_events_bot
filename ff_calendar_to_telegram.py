import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from telegram import Bot

# توکن ربات و آی‌دی کانال
TELEGRAM_BOT_TOKEN = '8152855589:AAHJuCR3tba9uAQxJW1JBLYxNSfDb8oRf0A'
TELEGRAM_CHANNEL_ID = '-1002509441378'

# رویدادهای مورد نظر
TARGET_EVENTS = {
    'Interest Rate',
    'CPI',
    'Inflation Rate',
    'Unemployment Rate',
    'GDP',
    'Current Account',
    'Government Budget',
    'Debt to GDP'
}

# کشورها و معادل نمادها
COUNTRIES = {
    'USD': '🇺🇸 USA',
    'EUR': '🇪🇺 EUD',
    'GBP': '🇬🇧 GBP',
    'JPY': '🇯🇵 JPY',
    'AUD': '🇦🇺 AUD',
    'CAD': '🇨🇦 CAD'
}

def fetch_forex_factory_events():
    url = 'https://www.forexfactory.com/calendar.php'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    rows = soup.select('tr.calendar__row')
    events = []

    for row in rows:
        try:
            time_str = row.select_one('.calendar__time').text.strip()
            currency = row.select_one('.calendar__currency').text.strip()
            title = row.select_one('.calendar__event-title').text.strip()

            if currency not in COUNTRIES:
                continue

            matched_event = next((e for e in TARGET_EVENTS if e.lower() in title.lower()), None)
            if not matched_event:
                continue

            date_str = row.get('data-event-datetime')
            if not date_str:
                continue

            utc_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            tehran_time = utc_time.astimezone(pytz.timezone('Asia/Tehran'))

            events.append({
                'currency': currency,
                'title': matched_event,
                'time': tehran_time.strftime('%Y/%m/%d | %H:%M')
            })

        except Exception as e:
            print(f"خطا: {e}")
            continue

    return events

def format_message(events):
    message = """📆تاریخ و زمان انتشار :

"""
    for code, name in COUNTRIES.items():
        message += f'{name}\n\n'
        for target in TARGET_EVENTS:
            match = next((e for e in events if e['currency'] == code and target.lower() in e['title'].lower()), None)
            time_str = match['time'] if match else '—'
            fa_name = translate_event_name(target)
            message += f'{target} ({fa_name})\n{time_str}\n\n'
        message += '—————————————————-\n'

    return message

def translate_event_name(name):
    mapping = {
        'Interest Rate': 'نرخ بهره',
        'CPI': 'تورم',
        'Inflation Rate': 'تورم',
        'Unemployment Rate': 'بیکاری',
        'GDP': 'تولید ناخالص داخلی',
        'Current Account': 'حساب جاری',
        'Government Budget': 'تراز بودجه دولت',
        'Debt to GDP': 'نسبت بدهی به تولید ناخالص داخلی',
    }
    return mapping.get(name, '')

def send_to_telegram(text):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=text)

if __name__ == "__main__":
    events = fetch_forex_factory_events()
    msg = format_message(events)
    send_to_telegram(msg)
