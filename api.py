import requests
from pprint import pprint

URL = 'https://cbu.uz/uz/arkhiv-kursov-valyut/json/'
CURRENCIES = {
    "USD": "🇺🇸",
    "EUR": "🇪🇺",
    "GBP": "🇬🇧",
    "RUB": "🇷🇺",  
    "CNY": "🇨🇳",  
    "KRW": "🇰🇷",
    "TRY": "🇹🇷",
    "AZN": "🇦🇿",
    "KZT": "🇰🇿",
    "TJS": "🇹🇯",
    "KGS": "🇰🇬",
    "AED": "🇦🇪"
}


def get_data():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        return False
    


def filter_countries():
    content = get_data()
    if content:
        data = []
        for country in content:
            if country['Ccy'] in CURRENCIES:
                data.append(country)
        return data

    return False


def make_text(data):
    text = ''
    plain_text = "{} 1 {} = {}\n"
    for country in data:
        flag = CURRENCIES.get(country['Ccy'], "")
        text += plain_text.format(
            flag,
            country['CcyNm_UZ'],
            country['Rate']
        )

    return text


data = filter_countries()
text = make_text(data)