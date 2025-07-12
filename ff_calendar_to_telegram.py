import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from telegram import Bot

# اطلاعات تلگرام
TELEGRAM_BOT_TOKEN = '8152855589:AAHJuCR3tba9uAQxJW1JBLYxNSfDb8oRf0A'
TELEGRAM_CHANNEL_ID = '-1002509441378'

# کشورها و معادل پرچم و اسم
COUNTRIES = {
    'USD': '🇺🇸 USA',
    'EUR': '🇪🇺 EUD',
    'GBP': '🇬🇧 GBP',
    'JPY': '🇯🇵 JPY',
    'AUD': '🇦🇺 AUD',
    'CAD': '🇨🇦 CAD'
}

# رویدادهای مهم هدف
TARGET_EVENTS = {
    'Interest Rate': 'نرخ بهره',
    'CPI': 'تورم',
    'Inflation Rate': 'تورم',
    'Unemployment Rate': 'بیکاری',
    'GDP': 'تولید ناخالص داخلی',
    'Current Account': 'حساب جاری',
    'Government Budget': 'تراز بودجه دولت',
    'Debt to GDP': 'نسبت بدهی به تولید ناخالص داخلی'
}

def fetch_forex_factory_events():
    url = 'https://www.forexfactory.com/calendar.php'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    rows = soup.select('table.calendar__table tr.calendar__row')
    events = []

    for row in rows:
        try:
            time_cell = row.select_one('td.calendar__time')
            currency_cell = row.select_one('td.calendar__currency')
            title_cell = row.select_one('td.calendar__event-title')

            if not (time_cell and currency_cell and title_cell):
                continue

            currency = currency_cell.text.strip()
            title = title_cell.text.strip()
            time_text = time_cell.text.strip()

            if currency not in COUNTRIES:
                continue

            matched_event = next((e for e in TARGET_EVENTS if e.lower() in title.lower()), None)
            if not matched_event:
                continue

            # بررسی و ساخت زمان از time_text
            if 'am' in time_text.lower() or 'pm' in time_text.lower():
                time_obj = datetime.strptime(time_text, '%I:%M%p')
            elif ':' in time_text:
                time_obj = datetime.strptime(time_text, '%H:%M')
            else:
                continue  # زمان‌های نامشخص

            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            final_time = today.replace(hour=time_obj.hour, minute=time_obj.minute)
            tehran_time = final_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Tehran'))

            events.append({
                'currency': currency,
                'title': matched_event,
                'time': tehran_time.strftime('%Y/%m/%d | %H:%M')
            })

        except Exception as e:
            print(f'⚠️ خطا در ردیف: {e}')
            continue

    return events

def format_message(events):
    message = "📆تاریخ و زمان انتشار :\n\n"
    for code, name in COUNTRIES.items():
        message += f"{name}\n\n"
        for eng_title, fa_title in TARGET_EVENTS.items():
            match = next((e for e in events if e['currency'] == code and e['title'] == eng_title), None)
            time_str = match['time'] if match else '—'
            message += f"{eng_title} ({fa_title})\n{time_str}\n\n"
        message += "—————————————————-\n"
    return message.strip()

def send_to_telegram(text):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=text)

if __name__ == "__main__":
    events = fetch_forex_factory_events()
    msg = format_message(events)
    send_to_telegram(msg)
