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

.today-withdrawn {
    font-size:10px;
    color:#16a34a;
    font-weight:900;
    line-height:1.25;
    margin-top:4px;
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

    .mini-small,
    .today-withdrawn {
        font-size:8.5px;
        line-height:1.2;
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
    restaurant = normalize_restaurant_name(restaurant)

    for row in data["profits"]:
        if row["restaurant"] == restaurant and row["month"] == month:
            row["amount"] = amount
            return

    data["profits"].append({
        "restaurant": restaurant,
        "month": month,
        "amount": amount
    })


def get_withdrawals(data, restaurant, month):
    restaurant = normalize_restaurant_name(restaurant)

    return [
        row for row in data["withdrawals"]
        if row["restaurant"] == restaurant and row["month"] == month
    ]


def get_today_withdrawn(data, restaurant, month):
    today = date.today().strftime("%Y-%m-%d")
    restaurant = normalize_restaurant_name(restaurant)

    total = 0

    for row in data["withdrawals"]:
        if (
            row["restaurant"] == restaurant
            and row["month"] == month
            and row.get("date") == today
        ):
            total += row.get("amount", 0)

    return total


def planned_distribution(restaurant, month, profit):
    distribution = get_distribution(restaurant, month)

    return {
        name: round(profit * percent / 100, 2)
        for name, percent in distribution.items()
    }


def fact_distribution(withdrawals):
    result = {"Ядровы": 0, "Тарасенко": 0, "Возврат инвестиций": 0}

    for row in withdrawals:
        amount = row["amount"]
        mode = row.get("mode", "После утверждения прибыли")

        if mode == "До утверждения прибыли":
            result["Ядровы"] += amount / 2
            result["Тарасенко"] += amount / 2
        else:
            restaurant = row.get("restaurant")
            month = row.get("month")
            distribution = row.get("distribution")

            if not distribution and restaurant and month:
                distribution = get_distribution(restaurant, month)

            for name, percent in distribution.items():
                result[name] += amount * percent / 100

    return result


def closed_fact_from_plan(plan):
    return {
        "Ядровы": plan.get("Ядровы", 0),
        "Тарасенко": plan.get("Тарасенко", 0),
        "Возврат инвестиций": plan.get("Возврат инвестиций", 0),
    }


def partner_amounts(partner, plan, fact):
    accrued = plan.get(partner, 0)
    withdrawn = fact.get(partner, 0)
    invest_note = 0

    if partner == "Ядровы":
        accrued += plan.get("Возврат инвестиций", 0)
        withdrawn += fact.get("Возврат инвестиций", 0)
        invest_note = plan.get("Возврат инвестиций", 0)

    balance = accrued - withdrawn
    return accrued, withdrawn, balance, invest_note


def summary(data, restaurant, month):
    profit = get_profit(data, restaurant, month)
    withdrawals = get_withdrawals(data, restaurant, month)

    plan = planned_distribution(restaurant, month, profit)

    if is_closed_month(month):
        fact = closed_fact_from_plan(plan)
        total_withdrawn = profit
    else:
        fact = fact_distribution(withdrawals)
        total_withdrawn = sum(x["amount"] for x in withdrawals)

    yadrovy = partner_amounts("Ядровы", plan, fact)
    tarasenko = partner_amounts("Тарасенко", plan, fact)

    return profit, total_withdrawn, yadrovy, tarasenko, withdrawals


def render_header(user):
    st.markdown(
        f"""
<div class="app-header">
<div class="app-title">Dividends Space</div>
<div class="app-user">{user["name"]}</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_backup_button(data):
    backup_data = json.dumps(data, ensure_ascii=False, indent=4)

    st.download_button(
        "Скачать резервную копию",
        backup_data,
        file_name="dividends_backup.json",
        mime="application/json"
    )


def render_profit_chart(data, months):
    months_with_data = []

    for month in months:
        total = sum(get_profit(data, restaurant, month) for restaurant in RESTAURANTS)
        if total > 0:
            months_with_data.append(month)

    chart_months = list(reversed(months_with_data[:6]))

    if not chart_months:
        st.info("Пока нет данных для графика.")
        return

    restaurant_colors = {
        "Гончарная": "#111827",
        "Фонтанка": "#2563eb",
        "Спортивная": "#16a34a",
        "Загородный": "#f97316",
        "Науки": "#9333ea",
    }

    width = 860
    height = 280
    left = 60
    right = 30
    top = 28
    bottom = 52

    values = []
    for month in chart_months:
        for restaurant in RESTAURANTS:
            values.append(get_profit(data, restaurant, month))

    max_value = max(values) if values else 1
    if max_value <= 0:
        max_value = 1

    plot_width = width - left - right
    plot_height = height - top - bottom

    def x_pos(index):
        if len(chart_months) == 1:
            return left + plot_width / 2
        return left + index * (plot_width / (len(chart_months) - 1))

    def y_pos(value):
        return top + plot_height - (value / max_value) * plot_height

    svg = f'''
<div class="chart-box">
<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>
'''

    for i in range(5):
        y = top + i * (plot_height / 4)
        value = max_value - i * (max_value / 4)
        svg += f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" stroke="#e5e7eb" stroke-width="1"/>'
        svg += f'<text x="8" y="{y+4}" font-size="11" fill="#6b7280">{int(value/1000)}к</text>'

    for idx, month in enumerate(chart_months):
        x = x_pos(idx)
        svg += f'<text x="{x}" y="{height-20}" text-anchor="middle" font-size="11" fill="#6b7280">{month_label(month).split()[0]}</text>'

    for restaurant, color in restaurant_colors.items():
        points = []
        for idx, month in enumerate(chart_months):
            value = get_profit(data, restaurant, month)
            points.append(f'{x_pos(idx)},{y_pos(value)}')

        if len(points) > 1:
            svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'

        for idx, month in enumerate(chart_months):
            value = get_profit(data, restaurant, month)
            svg += f'<circle cx="{x_pos(idx)}" cy="{y_pos(value)}" r="3.5" fill="{color}"/>'

    legend_x = left
    legend_y = 14

    for restaurant, color in restaurant_colors.items():
        svg += f'<circle cx="{legend_x}" cy="{legend_y}" r="4" fill="{color}"/>'
        svg += f'<text x="{legend_x + 8}" y="{legend_y + 4}" font-size="11" fill="#111827">{restaurant}</text>'
        legend_x += 130

    svg += '</svg></div>'

    st.subheader("Динамика прибыли за 6 месяцев")
    st.markdown(svg, unsafe_allow_html=True)


def render_all_restaurant_cards(data, month):
    html = '<div class="cards-grid">'

    for restaurant in RESTAURANTS:
        profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)
        y_balance = yadrovy[2]
        t_balance = tarasenko[2]

        today_withdrawn = get_today_withdrawn(data, restaurant, month)

        today_text = ""
        if today_withdrawn > 0:
            today_text = f'''
<div class="today-withdrawn">Сегодня: {money(today_withdrawn)}</div>
'''

        closed_text = ""
        if is_closed_month(month):
            closed_text = '<div class="mini-small"><b>Закрыто</b></div>'

        html += f'''
<div class="mini-card">
<div class="mini-title">{restaurant}</div>
<div class="mini-label">Прибыль</div>
<div class="mini-money">{money(profit)}</div>
<div class="mini-label">Выведено</div>
<div class="mini-money">{money(total)}</div>
{today_text}
<div class="mini-small">Я: <b>{money(y_balance)}</b><br>Т: <b>{money(t_balance)}</b></div>
{closed_text}
</div>
'''

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_partner_details(yadrovy, tarasenko):
    y_accrued, y_withdrawn, y_balance, invest_note = yadrovy
    t_accrued, t_withdrawn, t_balance, _ = tarasenko

    y_note = ""
    if invest_note > 0:
        y_note = f'<div class="partner-note">Из них {money(invest_note)} — возврат инвестиций.</div>'

    st.markdown(
        f'''
<div class="partner-box">
<div class="partner-title">Ядровы</div>
<div class="partner-row">
<div><div class="partner-label">Начислено</div><div class="partner-money">{money(y_accrued)}</div></div>
<div><div class="partner-label">Выведено</div><div class="partner-money">{money(y_withdrawn)}</div></div>
<div><div class="partner-label">Остаток</div><div class="partner-money">{money(y_balance)}</div></div>
</div>
{y_note}
</div>

<div class="partner-box">
<div class="partner-title">Тарасенко</div>
<div class="partner-row">
<div><div class="partner-label">Начислено</div><div class="partner-money">{money(t_accrued)}</div></div>
<div><div class="partner-label">Выведено</div><div class="partner-money">{money(t_withdrawn)}</div></div>
<div><div class="partner-label">Остаток</div><div class="partner-money">{money(t_balance)}</div></div>
</div>
</div>
''',
        unsafe_allow_html=True
    )


def render_partner_card(restaurant, accrued, withdrawn, balance, invest_note=0):
    note = ""
    if invest_note > 0:
        note = f'<div class="partner-note">Из них {money(invest_note)} — возврат инвестиций.</div>'

    st.markdown(
        f'''
<div class="partner-box">
<div class="partner-title">{restaurant}</div>
<div class="partner-row">
<div><div class="partner-label">Начислено</div><div class="partner-money">{money(accrued)}</div></div>
<div><div class="partner-label">Выведено</div><div class="partner-money">{money(withdrawn)}</div></div>
<div><div class="partner-label">Остаток</div><div class="partner-money">{money(balance)}</div></div>
</div>
{note}
</div>
''',
        unsafe_allow_html=True
    )


def select_month(key, months, default_month=None, label="Месяц"):
    index = 0

    if default_month and default_month in months:
        index = months.index(default_month)

    return st.selectbox(
        label,
        months,
        index=index,
        format_func=month_label,
        key=key
    )


def select_restaurant(key):
    return st.selectbox(
        "Ресторан",
        list(RESTAURANTS.keys()),
        key=key
    )


if "user" not in st.session_state:
    st.session_state.user = None


if st.session_state.user is None:
    st.title("Dividends Space")
    st.caption("Кабинет распределения дивидендов")

    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        if login in USERS and USERS[login]["password"] == password:
            st.session_state.user = USERS[login]
            st.rerun()
        else:
            st.error("Неверный логин или пароль")

    st.stop()


user = st.session_state.user
data = load_data()
months = all_months(data)

default_main_month = latest_profit_month(data)
default_work_month = previous_month_key(date.today())

render_header(user)

if user["role"] == "admin":
    tab_main, tab_restaurant, tab_archive, tab_exit = st.tabs(
        ["Главная", "Ресторан", "Архив", "Выйти"]
    )
else:
    tab_main, tab_archive, tab_exit = st.tabs(
        ["Мой кабинет", "Архив", "Выйти"]
    )


if user["role"] == "partner":
    with tab_main:
        st.title("Мой кабинет")

        month = select_month("partner_month", months, default_main_month)
        restaurant = select_restaurant("partner_restaurant")

        profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

        if user["partner"] == "Ядровы":
            accrued, withdrawn, balance, invest = yadrovy
        else:
            accrued, withdrawn, balance, invest = tarasenko

        if is_closed_month(month):
            st.markdown('<div class="closed-badge">Закрытый месяц — распределено полностью</div>', unsafe_allow_html=True)

        render_partner_card(
            restaurant,
            accrued,
            withdrawn,
            balance,
            invest if user["partner"] == "Ядровы" else 0
        )

    with tab_archive:
        st.title("Архив")

        for month in months:
            month_has_profit = any(get_profit(data, restaurant, month) > 0 for restaurant in RESTAURANTS)

            if not month_has_profit and not is_closed_month(month):
                continue

            st.subheader(month_label(month))

            if is_closed_month(month):
                st.markdown('<div class="closed-badge">Закрытый месяц — распределено полностью</div>', unsafe_allow_html=True)

            for restaurant in RESTAURANTS:
                profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

                if profit == 0 and not is_closed_month(month):
                    continue

                if user["partner"] == "Ядровы":
                    accrued, withdrawn, balance, invest = yadrovy
                else:
                    accrued, withdrawn, balance, invest = tarasenko

                render_partner_card(
                    restaurant,
                    accrued,
                    withdrawn,
                    balance,
                    invest if user["partner"] == "Ядровы" else 0
                )

    with tab_exit:
        if st.button("Выйти из кабинета"):
            st.session_state.user = None
            st.rerun()

    st.stop()


with tab_main:
    st.title("Главная")

    month = select_month("main_month", months, default_main_month)
    selected_restaurant = select_restaurant("main_restaurant")

    if is_closed_month(month):
        st.markdown('<div class="closed-badge">Закрытый месяц — распределено полностью</div>', unsafe_allow_html=True)

    st.subheader("Все заведения за месяц")
    render_all_restaurant_cards(data, month)

    st.subheader(f"Партнеры — {selected_restaurant}")
    profit, total, yadrovy, tarasenko, withdrawals = summary(data, selected_restaurant, month)
    render_partner_details(yadrovy, tarasenko)

    st.divider()
    render_profit_chart(data, months)


with tab_restaurant:
    st.title("Ресторан")
    st.caption("Детальный просмотр и ввод данных")

    render_backup_button(data)
    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        month = select_month(
            "restaurant_month",
            months,
            default_work_month,
            label="Месяц прибыли"
        )
        st.markdown(
            '<span class="month-hint">Это месяц, за который распределяется прибыль. Например: в мае можно вывести деньги за апрель.</span>',
            unsafe_allow_html=True
        )

    with c2:
        restaurant = select_restaurant("restaurant_name")

    if is_closed_month(month):
        st.markdown('<div class="closed-badge">Закрытый месяц — распределено полностью</div>', unsafe_allow_html=True)

    profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

    st.subheader("Прибыль месяца")

    new_profit = st.number_input(
        "Утвержденная прибыль",
        min_value=0,
        step=10000,
        value=int(profit)
    )

    if st.button("Сохранить прибыль"):
        set_profit(data, restaurant, month, new_profit)
        save_data(data)
        st.success("Прибыль сохранена")
        st.rerun()

    st.divider()

    st.subheader("Добавить вывод")

    c3, c4 = st.columns(2)

    with c3:
        withdrawal_date = st.date_input("Дата фактического вывода", value=date.today())

    with c4:
        withdrawal_amount = st.number_input("Сумма вывода", min_value=0, step=10000)

    default_mode = "После утверждения прибыли" if profit > 0 else "До утверждения прибыли"

    mode = st.radio(
        "Режим распределения",
        ["До утверждения прибыли", "После утверждения прибыли"],
        index=0 if default_mode == "До утверждения прибыли" else 1
    )

    if st.button("Добавить вывод"):
        if withdrawal_amount <= 0:
            st.error("Введите сумму вывода")
        else:
            distribution = {"Ядровы": 50, "Тарасенко": 50}

            if mode == "После утверждения прибыли":
                distribution = get_distribution(restaurant, month)

            data["withdrawals"].append({
                "date": withdrawal_date.strftime("%Y-%m-%d"),
                "month": month,
                "restaurant": restaurant,
                "amount": withdrawal_amount,
                "mode": mode,
                "distribution": distribution
            })

            save_data(data)
            st.success("Вывод добавлен")
            st.rerun()

    st.divider()

    st.subheader(f"Партнеры — {restaurant}")
    render_partner_details(yadrovy, tarasenko)

    st.subheader("Выводы за месяц прибыли")

    if is_closed_month(month):
        st.info("Этот месяц закрыт: все дивиденды распределены и выведены полностью.")
    elif not withdrawals:
        st.info("Выводов пока нет")
    else:
        for index, row in enumerate(withdrawals):
            with st.container(border=True):
                c5, c6, c7, c8 = st.columns([2, 2, 3, 1])

                c5.write(f"**Дата вывода:** {row['date']}")
                c6.write(f"**Сумма:** {money(row['amount'])}")
                c7.write(f"**Режим:** {row.get('mode', '')}")

                if c8.button("Удалить", key=f"delete_month_{index}"):
                    original_index = data["withdrawals"].index(row)
                    data["withdrawals"].pop(original_index)
                    save_data(data)
                    st.success("Вывод удален")
                    st.rerun()


with tab_archive:
    st.title("Архив")

    for month in months:
        month_has_profit = any(get_profit(data, restaurant, month) > 0 for restaurant in RESTAURANTS)
        month_has_withdrawals = any(len(get_withdrawals(data, restaurant, month)) > 0 for restaurant in RESTAURANTS)

        if not month_has_profit and not month_has_withdrawals and not is_closed_month(month):
            continue

        st.subheader(month_label(month))

        if is_closed_month(month):
            st.markdown('<div class="closed-badge">Закрытый месяц — распределено полностью</div>', unsafe_allow_html=True)

        for restaurant in RESTAURANTS:
            profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

            if profit == 0 and total == 0 and not is_closed_month(month):
                continue

            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**{restaurant}**")
                c2.write(f"Прибыль: **{money(profit)}**")
                c3.write(f"Выведено: **{money(total)}**")

                if withdrawals and not is_closed_month(month):
                    for row in withdrawals:
                        st.caption(
                            f"Дата вывода: {row.get('date', '')} · "
                            f"Сумма: {money(row.get('amount', 0))} · "
                            f"{row.get('mode', '')}"
                        )


with tab_exit:
    if st.button("Выйти из кабинета"):
        st.session_state.user = None
        st.rerun()
