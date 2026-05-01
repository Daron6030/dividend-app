import streamlit as st
import json
import os
from datetime import date

st.set_page_config(
    page_title="Dividends Space",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "data.json"

USERS = {
    "Daron6030": {
        "password": "Daron6030?",
        "role": "admin",
        "name": "Тарасенко Богдан",
        "partner": "Тарасенко",
    },
    "Iadrov": {
        "password": "181216",
        "role": "partner",
        "name": "Ядровы",
        "partner": "Ядровы",
    },
    "Alisa": {
        "password": "669933",
        "role": "partner",
        "name": "Тарасенко Алиса",
        "partner": "Тарасенко",
    },
}

RESTAURANTS = {
    "Гончарная": {"Ядровы": 50, "Тарасенко": 50},
    "Фонтанка": {"Ядровы": 33.33, "Тарасенко": 33.33, "Возврат инвестиций": 33.34},
    "Спортивная": {"Ядровы": 50, "Тарасенко": 50},
    "Загородный": {"Ядровы": 33.33, "Тарасенко": 33.33, "Возврат инвестиций": 33.34},
    "Науки": {"Ядровы": 50, "Тарасенко": 50},
}

SPORTIVNAYA_OLD_RULE_UNTIL = "2026-04"

INITIAL_PROFITS = {
    "2025-10": {"Гончарная": 1400000, "Фонтанка": 490000, "Спортивная": 1280000, "Загородный": 650000, "Науки": 0},
    "2025-11": {"Гончарная": 619000, "Фонтанка": 430000, "Спортивная": 1000000, "Загородный": 572000, "Науки": 0},
    "2025-12": {"Гончарная": 470000, "Фонтанка": 490000, "Спортивная": 639000, "Загородный": 194000, "Науки": 0},
    "2026-01": {"Гончарная": 960000, "Фонтанка": 200000, "Спортивная": 1200000, "Загородный": 385000, "Науки": 0},
    "2026-02": {"Гончарная": 534000, "Фонтанка": 0, "Спортивная": 437000, "Загородный": 67000, "Науки": 0},
    "2026-03": {"Гончарная": 1200000, "Фонтанка": 520000, "Спортивная": 1200000, "Загородный": 750000, "Науки": 0},
}

CLOSED_MONTHS = set(INITIAL_PROFITS.keys())

st.markdown("""
<style>
section[data-testid="stSidebar"] {display:none !important;}
header[data-testid="stHeader"] {display:none !important;}

.stApp {
    background:#f6f7f9;
    color:#111827;
}

.block-container {
    padding-top:1rem !important;
    padding-left:1rem !important;
    padding-right:1rem !important;
}

h1,h2,h3,h4,h5,h6,p,label {
    color:#111827 !important;
}

.app-header {
    background:#111827;
    border-radius:22px;
    padding:18px;
    margin-bottom:16px;
    box-shadow:0 10px 28px rgba(15,23,42,0.14);
    text-align:center;
}

.app-title {
    color:white !important;
    font-size:24px;
    font-weight:800;
    text-align:center;
}

.app-user {
    color:#d1d5db !important;
    font-size:14px;
    margin-top:6px;
    text-align:center;
}

div[data-testid="stTabs"] div[role="tablist"] {
    justify-content:center !important;
    gap:18px !important;
}

button[data-baseweb="tab"] {
    font-weight:700 !important;
    color:#111827 !important;
    font-size:18px !important;
}

input, textarea {
    background:white !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
}

div[data-baseweb="input"] input {
    background:white !important;
    color:#111827 !important;
}

div[data-baseweb="select"] > div {
    background:white !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
    border-radius:13px !important;
}

div[data-baseweb="select"] span {
    color:#111827 !important;
}

div[data-baseweb="select"] input {
    opacity:0 !important;
    width:0px !important;
    min-width:0px !important;
    caret-color:transparent !important;
}

div[data-baseweb="select"] svg {
    color:#c7ccd3 !important;
}

div[data-testid="metric-container"] {
    background:white;
    border:1px solid #e5e7eb;
    padding:10px;
    border-radius:14px;
    box-shadow:0 8px 18px rgba(15,23,42,0.04);
}

div[data-testid="metric-container"] label {
    color:#6b7280 !important;
    font-size:12px !important;
}

div[data-testid="metric-container"] div {
    color:#111827 !important;
    font-size:21px !important;
}

.stButton > button,
.stDownloadButton > button {
    width:100%;
    border-radius:12px;
    background:white !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
    font-weight:650;
    padding:10px 12px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background:#111827 !important;
    color:white !important;
    border:1px solid #111827 !important;
}

.cards-grid {
    display:grid;
    grid-template-columns:repeat(5, 1fr);
    gap:8px;
    width:100%;
    margin-top:10px;
    margin-bottom:18px;
}

.mini-card {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:10px 8px;
    box-shadow:0 6px 16px rgba(15,23,42,0.04);
    min-height:118px;
    overflow:hidden;
}

.mini-title {
    font-size:13px;
    font-weight:800;
    color:#111827;
    margin-bottom:7px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.mini-label {
    color:#6b7280;
    font-size:10px;
    line-height:1.1;
    margin-top:4px;
}

.mini-money {
    font-size:13px;
    font-weight:800;
    color:#111827;
    line-height:1.15;
    white-space:nowrap;
}

.mini-small {
    font-size:10px;
    color:#4b5563;
    line-height:1.25;
    margin-top:5px;
}

.partner-box {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:16px;
    box-shadow:0 8px 18px rgba(15,23,42,0.04);
    margin-bottom:14px;
}

.partner-title {
    font-size:22px;
    font-weight:800;
    color:#111827;
    margin-bottom:10px;
}

.partner-row {
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:10px;
}

.partner-label {
    font-size:12px;
    color:#6b7280;
    margin-bottom:4px;
}

.partner-money {
    font-size:20px;
    font-weight:800;
    color:#111827;
}

.partner-note {
    font-size:12px;
    color:#6b7280;
    margin-top:10px;
}

.closed-badge {
    display:inline-block;
    background:#ecfdf5;
    color:#047857;
    border:1px solid #a7f3d0;
    border-radius:999px;
    padding:5px 10px;
    font-size:12px;
    font-weight:700;
    margin-bottom:8px;
}

.month-hint {
    display:block;
    color:#6b7280;
    font-size:13px;
    margin-top:-4px;
    margin-bottom:12px;
}

.today-panel {
    background:#ecfdf5;
    border:1px solid #a7f3d0;
    border-radius:18px;
    padding:16px;
    margin-bottom:18px;
    box-shadow:0 8px 18px rgba(22,163,74,0.08);
}

.today-title {
    font-size:22px;
    font-weight:900;
    color:#047857;
    margin-bottom:10px;
}

.today-grid {
    display:grid;
    grid-template-columns:repeat(5, 1fr);
    gap:8px;
}

.today-card {
    background:white;
    border:1px solid #bbf7d0;
    border-radius:14px;
    padding:10px;
}

.today-restaurant {
    font-size:13px;
    font-weight:900;
    color:#064e3b;
    margin-bottom:6px;
}

.today-line {
    font-size:12px;
    color:#065f46;
    line-height:1.35;
}

.today-total {
    margin-top:12px;
    font-size:14px;
    font-weight:900;
    color:#047857;
}

.chart-box {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:14px;
    box-shadow:0 8px 18px rgba(15,23,42,0.04);
    overflow-x:auto;
}

@media (max-width:768px) {
    .block-container {
        padding-left:0.85rem !important;
        padding-right:0.85rem !important;
        padding-top:0.7rem !important;
    }

    .app-header {
        padding:16px 12px;
        border-radius:20px;
        margin-bottom:14px;
    }

    .app-title {
        font-size:22px;
    }

    .app-user {
        font-size:13px;
    }

    div[data-testid="stTabs"] div[role="tablist"] {
        justify-content:center !important;
        gap:10px !important;
    }

    button[data-baseweb="tab"] {
        font-size:16px !important;
        padding-left:4px !important;
        padding-right:4px !important;
    }

    h1 {
        font-size:31px !important;
        line-height:1.05 !important;
        margin-bottom:4px !important;
    }

    h2 {
        font-size:24px !important;
    }

    h3 {
        font-size:20px !important;
    }

    .cards-grid {
        gap:5px;
    }

    .mini-card {
        padding:8px 5px;
        border-radius:12px;
        min-height:108px;
    }

    .mini-title {
        font-size:10.5px;
        margin-bottom:5px;
    }

    .mini-label {
        font-size:8.5px;
    }

    .mini-money {
        font-size:10.5px;
    }

    .mini-small {
        font-size:8.5px;
        line-height:1.2;
    }

    .today-grid {
        grid-template-columns:repeat(2, 1fr);
    }

    .today-title {
        font-size:20px;
    }

    .today-restaurant {
        font-size:12px;
    }

    .today-line {
        font-size:11px;
    }

    .partner-box {
        padding:13px;
        border-radius:16px;
    }

    .partner-title {
        font-size:20px;
    }

    .partner-money {
        font-size:18px;
    }

    .partner-label {
        font-size:11px;
    }
}
</style>
""", unsafe_allow_html=True)


def money(value):
    return f"{value:,.0f}".replace(",", " ") + " ₽"


def normalize_restaurant_name(name):
    if name == "Наука":
        return "Науки"
    return name


def month_key(d):
    return d.strftime("%Y-%m")


def add_months(month, offset):
    year, month_num = map(int, month.split("-"))
    month_num += offset

    while month_num > 12:
        month_num -= 12
        year += 1

    while month_num < 1:
        month_num += 12
        year -= 1

    return f"{year}-{month_num:02d}"


def previous_month_key(d):
    return add_months(month_key(d), -1)


def month_label(key):
    year, month = key.split("-")
    names = {
        "01": "Январь", "02": "Февраль", "03": "Март",
        "04": "Апрель", "05": "Май", "06": "Июнь",
        "07": "Июль", "08": "Август", "09": "Сентябрь",
        "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь",
    }
    return f"{names[month]} {year}"


def get_distribution(restaurant, month):
    restaurant = normalize_restaurant_name(restaurant)

    if restaurant == "Спортивная" and month <= SPORTIVNAYA_OLD_RULE_UNTIL:
        return {
            "Ядровы": 33.33,
            "Тарасенко": 33.33,
            "Возврат инвестиций": 33.34
        }

    return RESTAURANTS[restaurant]


def normalize_data(data):
    if not isinstance(data, dict):
        return {"profits": [], "withdrawals": []}

    if "profits" not in data:
        data["profits"] = []

    if "withdrawals" not in data:
        data["withdrawals"] = []

    if isinstance(data["profits"], dict):
        new_profits = []
        for month, restaurants in data["profits"].items():
            if isinstance(restaurants, dict):
                for restaurant, amount in restaurants.items():
                    new_profits.append({
                        "restaurant": normalize_restaurant_name(restaurant),
                        "month": month,
                        "amount": amount
                    })
        data["profits"] = new_profits

    if isinstance(data["withdrawals"], dict):
        new_withdrawals = []
        for month, restaurants in data["withdrawals"].items():
            if isinstance(restaurants, dict):
                for restaurant, amount in restaurants.items():
                    restaurant = normalize_restaurant_name(restaurant)
                    new_withdrawals.append({
                        "date": month + "-01",
                        "month": month,
                        "restaurant": restaurant,
                        "amount": amount,
                        "mode": "После утверждения прибыли",
                        "distribution": get_distribution(restaurant, month)
                    })
        data["withdrawals"] = new_withdrawals

    for row in data["profits"]:
        row["restaurant"] = normalize_restaurant_name(row["restaurant"])

    for row in data["withdrawals"]:
        row["restaurant"] = normalize_restaurant_name(row["restaurant"])

    return data


def apply_initial_profits(data):
    for month, restaurants in INITIAL_PROFITS.items():
        for restaurant, amount in restaurants.items():
            restaurant = normalize_restaurant_name(restaurant)
            exists = False

            for row in data["profits"]:
                if row["restaurant"] == restaurant and row["month"] == month:
                    exists = True
                    break

            if not exists:
                data["profits"].append({
                    "restaurant": restaurant,
                    "month": month,
                    "amount": amount
                })


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"profits": [], "withdrawals": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    data = normalize_data(loaded)
    apply_initial_profits(data)

    return data


def save_data(data):
    data = normalize_data(data)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def all_months(data):
    months = set()

    for row in data["profits"]:
        months.add(row["month"])

    for row in data["withdrawals"]:
        months.add(row["month"])

    current = month_key(date.today())

    for offset in range(-12, 13):
        months.add(add_months(current, offset))

    return sorted(list(months), reverse=True)


def latest_profit_month(data):
    months_with_profit = set()

    for row in data["profits"]:
        if row.get("amount", 0) > 0:
            months_with_profit.add(row["month"])

    if months_with_profit:
        return sorted(list(months_with_profit), reverse=True)[0]

    return previous_month_key(date.today())


def is_closed_month(month):
    return month in CLOSED_MONTHS


def get_profit(data, restaurant, month):
    restaurant = normalize_restaurant_name(restaurant)

    for row in data["profits"]:
        if row["restaurant"] == restaurant and row["month"] == month:
            return row["amount"]

    return 0


def set_profit(data, restaurant, month, amount):
    restaurant = normalize_rest
