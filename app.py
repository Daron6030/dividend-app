import streamlit as st
import json
import os
from datetime import date
import altair as alt

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
                        "restaurant": restaurant,
                        "month": month,
                        "amount": amount
                    })
        data["profits"] = new_profits

    if isinstance(data["withdrawals"], dict):
        new_withdrawals = []
        for month, restaurants in data["withdrawals"].items():
            if isinstance(restaurants, dict):
                for restaurant, amount in restaurants.items():
                    new_withdrawals.append({
                        "date": month + "-01",
                        "month": month,
                        "restaurant": restaurant,
                        "amount": amount,
                        "mode": "После утверждения прибыли",
                        "distribution": RESTAURANTS.get(
                            restaurant,
                            {"Ядровы": 50, "Тарасенко": 50}
                        )
                    })
        data["withdrawals"] = new_withdrawals

    return data


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"profits": [], "withdrawals": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    return normalize_data(loaded)


def save_data(data):
    data = normalize_data(data)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def month_key(d):
    return d.strftime("%Y-%m")


def month_label(key):
    year, month = key.split("-")
    names = {
        "01": "Январь", "02": "Февраль", "03": "Март",
        "04": "Апрель", "05": "Май", "06": "Июнь",
        "07": "Июль", "08": "Август", "09": "Сентябрь",
        "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь",
    }
    return f"{names[month]} {year}"


def all_months(data):
    months = set()

    for row in data["profits"]:
        months.add(row["month"])

    for row in data["withdrawals"]:
        months.add(row["month"])

    current = month_key(date.today())
    months.add(current)

    return sorted(list(months), reverse=True)


def get_profit(data, restaurant, month):
    for row in data["profits"]:
        if row["restaurant"] == restaurant and row["month"] == month:
            return row["amount"]
    return 0


def set_profit(data, restaurant, month, amount):
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
    return [
        row for row in data["withdrawals"]
        if row["restaurant"] == restaurant and row["month"] == month
    ]


def planned_distribution(restaurant, profit):
    return {
        name: round(profit * percent / 100, 2)
        for name, percent in RESTAURANTS[restaurant].items()
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
            for name, percent in row.get("distribution", {}).items():
                result[name] += amount * percent / 100

    return result


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

    plan = planned_distribution(restaurant, profit)
    fact = fact_distribution(withdrawals)

    yadrovy = partner_amounts("Ядровы", plan, fact)
    tarasenko = partner_amounts("Тарасенко", plan, fact)
    total_withdrawn = sum(x["amount"] for x in withdrawals)

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
    chart_months = list(reversed(months[:6]))

    rows = []

    for month in chart_months:
        for restaurant in RESTAURANTS:
            rows.append({
                "Месяц": month_label(month),
                "Ресторан": restaurant,
                "Прибыль": get_profit(data, restaurant, month)
            })

    chart = (
        alt.Chart(alt.Data(values=rows))
        .mark_line(point=True)
        .encode(
            x=alt.X("Месяц:N", title="Месяц"),
            y=alt.Y("Прибыль:Q", title="Прибыль"),
            color=alt.Color("Ресторан:N", title="Ресторан"),
            tooltip=["Месяц", "Ресторан", "Прибыль"]
        )
        .properties(
            height=260,
            background="white"
        )
        .configure_view(
            strokeWidth=0
        )
        .configure_axis(
            labelColor="#111827",
            titleColor="#111827",
            gridColor="#e5e7eb"
        )
        .configure_legend(
            labelColor="#111827",
            titleColor="#111827"
        )
    )

    st.subheader("Динамика прибыли за 6 месяцев")
    st.altair_chart(chart, use_container_width=True)


def render_all_restaurant_cards(data, month):
    html = '<div class="cards-grid">'

    for restaurant in RESTAURANTS:
        profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)
        y_balance = yadrovy[2]
        t_balance = tarasenko[2]

        html += f'''
<div class="mini-card">
<div class="mini-title">{restaurant}</div>
<div class="mini-label">Прибыль</div>
<div class="mini-money">{money(profit)}</div>
<div class="mini-label">Выведено</div>
<div class="mini-money">{money(total)}</div>
<div class="mini-small">Я: <b>{money(y_balance)}</b><br>Т: <b>{money(t_balance)}</b></div>
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


def select_month(key, months):
    return st.selectbox(
        "Месяц",
        months,
        index=0,
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

render_header(user)

if user["role"] == "admin":
    tab_main, tab_restaurant, tab_archive, tab_exit = st.tabs(
        ["Главная", "Ресторан", "Архив", "Выйти"]
    )
else:
    tab_main, tab_exit = st.tabs(["Мой кабинет", "Выйти"])


if user["role"] == "partner":
    with tab_main:
        st.title("Мой кабинет")

        month = select_month("partner_month", months)
        restaurant = select_restaurant("partner_restaurant")

        profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

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

    month = select_month("main_month", months)
    selected_restaurant = select_restaurant("main_restaurant")

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
        month = select_month("restaurant_month", months)

    with c2:
        restaurant = select_restaurant("restaurant_name")

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
        withdrawal_date = st.date_input("Дата вывода", value=date.today())

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
                distribution = RESTAURANTS[restaurant]

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

    st.subheader("Выводы за месяц")

    if not withdrawals:
        st.info("Выводов пока нет")
    else:
        for index, row in enumerate(withdrawals):
            with st.container(border=True):
                c5, c6, c7, c8 = st.columns([2, 2, 3, 1])

                c5.write(f"**Дата:** {row['date']}")
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
    st.caption("Все сохраненные выводы")

    if not data["withdrawals"]:
        st.info("Выводов пока нет")
    else:
        selected_restaurant = st.selectbox(
            "Фильтр по ресторану",
            ["Все"] + list(RESTAURANTS.keys()),
            key="archive_filter"
        )

        rows = list(enumerate(data["withdrawals"]))

        if selected_restaurant != "Все":
            rows = [
                (i, row) for i, row in rows
                if row["restaurant"] == selected_restaurant
            ]

        sorted_rows = sorted(
            rows,
            key=lambda item: item[1].get("date", ""),
            reverse=True
        )

        for original_index, row in sorted_rows:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

                c1.write(f"**Дата:** {row.get('date', '')}")
                c2.write(f"**Ресторан:** {row.get('restaurant', '')}")
                c3.write(f"**Сумма:** {money(row.get('amount', 0))}")

                if c4.button("Удалить", key=f"delete_withdrawal_{original_index}"):
                    data["withdrawals"].pop(original_index)
                    save_data(data)
                    st.success("Вывод удален")
                    st.rerun()

                st.caption(f"Режим: {row.get('mode', '')}")


with tab_exit:
    if st.button("Выйти из кабинета"):
        st.session_state.user = None
        st.rerun()
