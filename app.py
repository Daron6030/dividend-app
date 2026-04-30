import streamlit as st
import json
import os
from datetime import date

st.set_page_config(
    page_title="Dividends Space",
    page_icon="●",
    layout="wide"
)

DATA_FILE = "data.json"

USERS = {
    "bogdan": {
        "password": "1234",
        "role": "admin",
        "name": "Тарасенко Богдан",
        "partner": "Тарасенко",
    },
    "yadrovy": {
        "password": "1111",
        "role": "partner",
        "name": "Ядровы",
        "partner": "Ядровы",
    },
    "alisa": {
        "password": "2222",
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

MENU_ADMIN = {
    "Главная": "Главная",
    "Ресторан": "Ресторан за месяц",
    "Архив": "Архив выводов",
}


st.markdown(
    """
    <style>
    .stApp {
        background: #f6f7f9;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    div[data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 18px;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="metric-container"] label {
        color: #6b7280;
        font-size: 14px;
    }

    .stButton > button {
        border-radius: 14px;
        background: #111827;
        color: white;
        border: none;
        font-weight: 600;
        padding: 10px 18px;
    }

    .stButton > button:hover {
        background: #374151;
        color: white;
    }

    .soft-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        margin-bottom: 18px;
    }

    .small-muted {
        color: #6b7280;
        font-size: 14px;
    }

    .big-title {
        font-size: 34px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 22px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def money(value):
    return f"{value:,.0f}".replace(",", " ") + " ₽"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"profits": [], "withdrawals": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def month_key(d):
    return d.strftime("%Y-%m")


def month_label(key):
    year, month = key.split("-")
    names = {
        "01": "Январь",
        "02": "Февраль",
        "03": "Март",
        "04": "Апрель",
        "05": "Май",
        "06": "Июнь",
        "07": "Июль",
        "08": "Август",
        "09": "Сентябрь",
        "10": "Октябрь",
        "11": "Ноябрь",
        "12": "Декабрь",
    }
    return f"{names[month]} {year}"


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
    result = {}
    for name, percent in RESTAURANTS[restaurant].items():
        result[name] = round(profit * percent / 100, 2)
    return result


def fact_distribution(withdrawals):
    result = {
        "Ядровы": 0,
        "Тарасенко": 0,
        "Возврат инвестиций": 0
    }

    for row in withdrawals:
        amount = row["amount"]
        mode = row["mode"]

        if mode == "До утверждения прибыли":
            result["Ядровы"] += amount / 2
            result["Тарасенко"] += amount / 2
        else:
            for name, percent in row["distribution"].items():
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


def restaurant_summary(data, restaurant, month):
    profit = get_profit(data, restaurant, month)
    withdrawals = get_withdrawals(data, restaurant, month)

    plan = planned_distribution(restaurant, profit)
    fact = fact_distribution(withdrawals)

    yadrovy = partner_amounts("Ядровы", plan, fact)
    tarasenko = partner_amounts("Тарасенко", plan, fact)

    total_withdrawn = sum(x["amount"] for x in withdrawals)
    return profit, total_withdrawn, yadrovy, tarasenko, withdrawals


def page_header(title, subtitle):
    st.markdown(f"<div class='big-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted'>{subtitle}</div>", unsafe_allow_html=True)
    st.write("")


def render_admin_restaurant_card(restaurant, month, profit, total_withdrawn, yadrovy, tarasenko):
    y_accrued, y_withdrawn, y_balance, invest_note = yadrovy
    t_accrued, t_withdrawn, t_balance, _ = tarasenko

    st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
    st.subheader(f"{restaurant}")
    st.caption(month_label(month))

    c1, c2, c3 = st.columns(3)
    c1.metric("Прибыль месяца", money(profit))
    c2.metric("Всего выведено", money(total_withdrawn))
    c3.metric("Остаток прибыли", money(profit - total_withdrawn))

    st.divider()

    c4, c5 = st.columns(2)

    with c4:
        st.markdown("#### Ядровы")
        st.metric("Остаток", money(y_balance))
        st.write(f"Начислено: **{money(y_accrued)}**")
        st.write(f"Выведено: **{money(y_withdrawn)}**")
        if invest_note > 0:
            st.caption(f"Из них {money(invest_note)} — возврат инвестиций.")

    with c5:
        st.markdown("#### Тарасенко")
        st.metric("Остаток", money(t_balance))
        st.write(f"Начислено: **{money(t_accrued)}**")
        st.write(f"Выведено: **{money(t_withdrawn)}**")

    st.markdown("</div>", unsafe_allow_html=True)


def render_partner_restaurant_card(restaurant, month, accrued, withdrawn, balance, invest_note=0):
    st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
    st.subheader(restaurant)
    st.caption(month_label(month))

    c1, c2, c3 = st.columns(3)
    c1.metric("Начислено", money(accrued))
    c2.metric("Выведено", money(withdrawn))
    c3.metric("Остаток", money(balance))

    if invest_note > 0:
        st.caption(f"Из них {money(invest_note)} — возврат инвестиций.")

    st.markdown("</div>", unsafe_allow_html=True)


# LOGIN

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    page_header("Dividends Space", "Кабинет распределения дивидендов")

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

today = date.today()
current_month = month_key(today)

all_months = sorted(
    list(set(
        [current_month]
        + [x["month"] for x in data["profits"]]
        + [x["month"] for x in data["withdrawals"]]
    )),
    reverse=True
)

with st.sidebar:
    st.markdown("### Dividends Space")
    st.caption(user["name"])
    st.divider()

    if user["role"] == "admin":
        menu = st.radio(
            "Раздел",
            list(MENU_ADMIN.keys()),
            label_visibility="collapsed"
        )
    else:
        menu = "Мой кабинет"

    st.divider()

    if st.button("Выйти"):
        st.session_state.user = None
        st.rerun()


# PARTNER VIEW

if user["role"] == "partner":
    page_header("Мой кабинет", "Только нужные цифры без лишней информации")

    selected_month = st.selectbox(
        "Месяц",
        all_months,
        index=all_months.index(current_month) if current_month in all_months else 0,
        format_func=month_label
    )

    restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit, total_withdrawn, yadrovy, tarasenko, withdrawals = restaurant_summary(
        data,
        restaurant,
        selected_month
    )

    partner = user["partner"]

    if partner == "Ядровы":
        accrued, withdrawn, balance, invest_note = yadrovy
    else:
        accrued, withdrawn, balance, invest_note = tarasenko

    render_partner_restaurant_card(
        restaurant,
        selected_month,
        accrued,
        withdrawn,
        balance,
        invest_note if partner == "Ядровы" else 0
    )

    st.stop()


# ADMIN VIEW

if menu == "Главная":
    page_header("Главная", "Выберите месяц и ресторан, чтобы увидеть итог")

    c1, c2 = st.columns(2)

    with c1:
        selected_month = st.selectbox(
            "Месяц",
            all_months,
            index=all_months.index(current_month) if current_month in all_months else 0,
            format_func=month_label
        )

    with c2:
        restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit, total_withdrawn, yadrovy, tarasenko, withdrawals = restaurant_summary(
        data,
        restaurant,
        selected_month
    )

    render_admin_restaurant_card(
        restaurant,
        selected_month,
        profit,
        total_withdrawn,
        yadrovy,
        tarasenko
    )


elif menu == "Ресторан":
    page_header("Ресторан", "Ввод прибыли и выводов за выбранный месяц")

    c1, c2 = st.columns(2)

    with c1:
        selected_month = st.selectbox(
            "Месяц",
            all_months,
            index=all_months.index(current_month) if current_month in all_months else 0,
            format_func=month_label
        )

    with c2:
        restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit, total_withdrawn, yadrovy, tarasenko, withdrawals = restaurant_summary(
        data,
        restaurant,
        selected_month
    )

    st.markdown("### Прибыль месяца")

    new_profit = st.number_input(
        "Утвержденная прибыль",
        min_value=0,
        step=10000,
        value=int(profit)
    )

    if st.button("Сохранить прибыль"):
        set_profit(data, restaurant, selected_month, new_profit)
        save_data(data)
        st.success("Прибыль сохранена")
        st.rerun()

    st.divider()

    st.markdown("### Добавить вывод")

    c3, c4 = st.columns(2)

    with c3:
        withdrawal_date = st.date_input("Дата вывода", value=today)

    with c4:
        withdrawal_amount = st.number_input("Сумма вывода", min_value=0, step=10000)

    profit_exists = profit > 0
    default_mode = "После утверждения прибыли" if profit_exists else "До утверждения прибыли"

    mode = st.selectbox(
        "Режим распределения",
        ["До утверждения прибыли", "После утверждения прибыли"],
        index=0 if default_mode == "До утверждения прибыли" else 1
    )

    st.caption(
        "До утверждения прибыли вывод делится 50/50. "
        "После утверждения прибыли — по процентам ресторана."
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
                "month": selected_month,
                "restaurant": restaurant,
                "amount": withdrawal_amount,
                "mode": mode,
                "distribution": distribution
            })

            save_data(data)
            st.success("Вывод добавлен")
            st.rerun()

    st.divider()

    render_admin_restaurant_card(
        restaurant,
        selected_month,
        profit,
        total_withdrawn,
        yadrovy,
        tarasenko
    )

    st.markdown("### Выводы за месяц")

    if not withdrawals:
        st.info("Выводов пока нет")
    else:
        for index, row in enumerate(withdrawals):
            with st.container(border=True):
                c5, c6, c7, c8 = st.columns([2, 2, 3, 1])

                c5.write(f"**Дата:** {row['date']}")
                c6.write(f"**Сумма:** {money(row['amount'])}")
                c7.write(f"**Режим:** {row['mode']}")

                if c8.button("Удалить", key=f"delete_month_{index}"):
                    original_index = data["withdrawals"].index(row)
                    data["withdrawals"].pop(original_index)
                    save_data(data)
                    st.success("Вывод удален")
                    st.rerun()


elif menu == "Архив":
    page_header("Архив", "Все сохраненные выводы")

    if not data["withdrawals"]:
        st.info("Выводов пока нет")
    else:
        selected_restaurant = st.selectbox(
            "Фильтр по ресторану",
            ["Все"] + list(RESTAURANTS.keys())
        )

        rows = list(enumerate(data["withdrawals"]))

        if selected_restaurant != "Все":
            rows = [
                (i, row) for i, row in rows
                if row["restaurant"] == selected_restaurant
            ]

        sorted_rows = sorted(
            rows,
            key=lambda item: item[1]["date"],
            reverse=True
        )

        for original_index, row in sorted_rows:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

                c1.write(f"**Дата:** {row['date']}")
                c2.write(f"**Ресторан:** {row['restaurant']}")
                c3.write(f"**Сумма:** {money(row['amount'])}")

                if c4.button("Удалить", key=f"delete_withdrawal_{original_index}"):
                    data["withdrawals"].pop(original_index)
                    save_data(data)
                    st.success("Вывод удален")
                    st.rerun()

                st.caption(f"Режим: {row['mode']}")
