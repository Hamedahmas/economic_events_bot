import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from telegram import Bot

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = '8152855589:AAHJuCR3tba9uAQxJW1JBLYxNSfDb8oRf0A'
TELEGRAM_CHANNEL_ID = '-1002509441378'

# کشورهای موردنظر
COUNTRIES = {
    'USD': '🇺🇸 USA',
    'EUR': '🇪🇺 EUD',
    'GBP': '🇬🇧 GBP',
    'JPY': '🇯🇵 JPY',
    'AUD': '🇦🇺 AUD',
    'CAD': '🇨🇦 CAD'
}

# کلیدواژه‌های تطبیق
KEYWORD_CATEGORIES = {
    'Interest Rate': ['interest rate', 'refinancing rate', 'rate statement', 'policy rate', 'fed funds rate'],
    'CPI': ['cpi', 'consumer price index'],
    'Inflation Rate': ['inflation'],
    'Unemployment Rate': ['unemployment', 'non-farm payroll', 'employment'],
    'GDP': ['gdp', 'gross domestic product'],
    'Current Account': ['current account'],
    'Government Budget': ['budget balance', 'government budget'],
    'Debt to GDP': ['debt to gdp', 'government debt']
}

# ترجمه‌ها
TRANSLATIONS = {
    'Interest Rate': 'نرخ بهره',
    'CPI': 'تورم',
    'Inflation Rate': 'تورم',
    'Unemployment Rate': 'بیکاری',
    'GDP': 'تولید ناخالص داخلی',
    'Current Account': 'حساب جاری',
    'Government Budget': 'تراز بودجه دولت',
    'Debt to GDP': 'نسبت بدهی به تولید ناخالص داخلی'
}

def match_category(title):
    title = title.lower()
    for category, keywords in KEYWORD_CATEGORIES.items():
        if any(keyword in title for keyword in keywords):
            return category
    return None

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

            matched = match_category(title)
            if not matched:
                continue

            if ':' in time_text:
                try:
                    if 'am' in time_text.lower() or 'pm' in time_text.lower():
                        time_obj = datetime.strptime(time_text, '%I:%M%p')
                    else:
                        time_obj = datetime.strptime(time_text, '%H:%M')
                except:
                    continue
            else:
                continue

            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            full_time = today.replace(hour=time_obj.hour, minute=time_obj.minute)
            tehran_time = full_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Tehran'))

            events.append({
                'currency': currency,
                'category': matched,
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
        for category in KEYWORD_CATEGORIES:
            event = next((e for e in events if e['currency'] == code and e['category'] == category), None)
            time_str = event['time'] if event else '—'
            fa_name = TRANSLATIONS[category]
            message += f"{category} ({fa_name})\n{time_str}\n\n"
        message += "—————————————————-\n"
    return message.strip()

def send_to_telegram(text):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=text)

if __name__ == "__main__":
    events = fetch_forex_factory_events()
    msg = format_message(events)
    send_to_telegram(msg)
