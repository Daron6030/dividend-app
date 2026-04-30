import streamlit as st
import json
import os
from datetime import date

st.set_page_config(page_title="Дивиденды", layout="wide")

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
        "01": "Январь", "02": "Февраль", "03": "Март",
        "04": "Апрель", "05": "Май", "06": "Июнь",
        "07": "Июль", "08": "Август", "09": "Сентябрь",
        "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь",
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
    result = {"Ядровы": 0, "Тарасенко": 0, "Возврат инвестиций": 0}

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

    return accrued, withdrawn, accrued - withdrawn, invest_note

# LOGIN
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("Вход в систему")
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
    st.success(user["name"])

    if user["role"] == "admin":
        menu = st.radio("Меню", ["Главная", "Ресторан за месяц", "Архив выводов"])
    else:
        menu = "Партнерский кабинет"

    if st.button("Выйти"):
        st.session_state.user = None
        st.rerun()

# PARTNER VIEW
if user["role"] == "partner":
    st.title("Мои дивиденды")

    selected_month = st.selectbox(
        "Месяц",
        all_months,
        format_func=month_label
    )

    partner = user["partner"]

    total_accrued = 0
    total_withdrawn = 0
    total_balance = 0
    total_invest_note = 0

    cards = []

    for restaurant in RESTAURANTS:
        profit = get_profit(data, restaurant, selected_month)
        withdrawals = get_withdrawals(data, restaurant, selected_month)

        plan = planned_distribution(restaurant, profit)
        fact = fact_distribution(withdrawals)

        accrued, withdrawn, balance, invest_note = partner_amounts(partner, plan, fact)

        total_accrued += accrued
        total_withdrawn += withdrawn
        total_balance += balance
        total_invest_note += invest_note

        cards.append({
            "restaurant": restaurant,
            "accrued": accrued,
            "withdrawn": withdrawn,
            "balance": balance,
            "invest_note": invest_note,
        })

    c1, c2, c3 = st.columns(3)
    c1.metric("Начислено", f"{total_accrued:,.0f} ₽")
    c2.metric("Выведено", f"{total_withdrawn:,.0f} ₽")
    c3.metric("Остаток", f"{total_balance:,.0f} ₽")

    if partner == "Ядровы" and total_invest_note > 0:
        st.caption(f"Из них {total_invest_note:,.0f} ₽ — возврат инвестиций за месяц.")

    st.divider()

    for card in cards:
        with st.container(border=True):
            st.subheader(card["restaurant"])

            a, b, c = st.columns(3)
            a.metric("Начислено", f"{card['accrued']:,.0f} ₽")
            b.metric("Выведено", f"{card['withdrawn']:,.0f} ₽")
            c.metric("Остаток", f"{card['balance']:,.0f} ₽")

            if partner == "Ядровы" and card["invest_note"] > 0:
                st.caption(
                    f"Из них {card['invest_note']:,.0f} ₽ — возврат инвестиций."
                )

    st.stop()

# ADMIN VIEW
st.title("Админ-панель дивидендов")

if menu == "Главная":
    st.header("Общая панель")

    selected_month = st.selectbox(
        "Месяц",
        all_months,
        format_func=month_label
    )

    rows = []

    total_profit = 0
    total_yadrovy_plan = 0
    total_tarasenko_plan = 0
    total_invest_plan = 0
    total_yadrovy_fact = 0
    total_tarasenko_fact = 0
    total_invest_fact = 0

    for restaurant in RESTAURANTS:
        profit = get_profit(data, restaurant, selected_month)
        withdrawals = get_withdrawals(data, restaurant, selected_month)

        plan = planned_distribution(restaurant, profit)
        fact = fact_distribution(withdrawals)

        yadrovy_total = plan.get("Ядровы", 0) + plan.get("Возврат инвестиций", 0)
        yadrovy_fact_total = fact.get("Ядровы", 0) + fact.get("Возврат инвестиций", 0)

        total_profit += profit
        total_yadrovy_plan += yadrovy_total
        total_tarasenko_plan += plan.get("Тарасенко", 0)
        total_invest_plan += plan.get("Возврат инвестиций", 0)

        total_yadrovy_fact += yadrovy_fact_total
        total_tarasenko_fact += fact.get("Тарасенко", 0)
        total_invest_fact += fact.get("Возврат инвестиций", 0)

        rows.append({
            "Ресторан": restaurant,
            "Прибыль": profit,
            "Ядровы начислено": yadrovy_total,
            "Ядровы выведено": yadrovy_fact_total,
            "Ядровы остаток": yadrovy_total - yadrovy_fact_total,
            "Тарасенко начислено": plan.get("Тарасенко", 0),
            "Тарасенко выведено": fact.get("Тарасенко", 0),
            "Тарасенко остаток": plan.get("Тарасенко", 0) - fact.get("Тарасенко", 0),
            "Возврат инвестиций за месяц": plan.get("Возврат инвестиций", 0),
        })

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Прибыль за месяц", f"{total_profit:,.0f} ₽")
    c2.metric("Ядровы остаток", f"{total_yadrovy_plan - total_yadrovy_fact:,.0f} ₽")
    c3.metric("Тарасенко остаток", f"{total_tarasenko_plan - total_tarasenko_fact:,.0f} ₽")
    c4.metric("Возврат инвестиций", f"{total_invest_plan:,.0f} ₽")

    st.subheader("Рестораны")
    st.dataframe(rows, use_container_width=True)

elif menu == "Ресторан за месяц":
    st.header("Ресторан за месяц")

    selected_month = st.selectbox(
        "Месяц",
        all_months,
        format_func=month_label
    )

    restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit = get_profit(data, restaurant, selected_month)
    withdrawals = get_withdrawals(data, restaurant, selected_month)

    st.subheader(f"{restaurant} — {month_label(selected_month)}")

    new_profit = st.number_input(
        "Утвержденная прибыль за месяц",
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

    st.subheader("Добавить вывод денег")

    withdrawal_date = st.date_input("Дата вывода", value=today)
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

    plan = planned_distribution(restaurant, profit)
    fact = fact_distribution(withdrawals)

    yadrovy_accrued, yadrovy_withdrawn, yadrovy_balance, invest_note = partner_amounts("Ядровы", plan, fact)
    tarasenko_accrued, tarasenko_withdrawn, tarasenko_balance, _ = partner_amounts("Тарасенко", plan, fact)

    st.subheader("Итог по ресторану")

    c1, c2, c3 = st.columns(3)
    c1.metric("Утвержденная прибыль", f"{profit:,.0f} ₽")
    c2.metric("Всего выведено", f"{sum(x['amount'] for x in withdrawals):,.0f} ₽")
    c3.metric("Остаток по прибыли", f"{profit - sum(x['amount'] for x in withdrawals):,.0f} ₽")

    st.subheader("По участникам")

    result_rows = [
        {
            "Участник": "Ядровы",
            "Начислено": yadrovy_accrued,
            "Выведено": yadrovy_withdrawn,
            "Остаток": yadrovy_balance,
            "Сноска": f"из них {invest_note:,.0f} ₽ возврат инвестиций" if invest_note > 0 else ""
        },
        {
            "Участник": "Тарасенко",
            "Начислено": tarasenko_accrued,
            "Выведено": tarasenko_withdrawn,
            "Остаток": tarasenko_balance,
            "Сноска": ""
        },
    ]

    st.dataframe(result_rows, use_container_width=True)

    st.subheader("Выводы за месяц")

    if not withdrawals:
        st.info("Выводов пока нет")
    else:
        st.dataframe(withdrawals, use_container_width=True)

elif menu == "Архив выводов":
    st.header("Архив выводов")

    if not data["withdrawals"]:
        st.info("Выводов пока нет")
    else:
        sorted_rows = sorted(
            list(enumerate(data["withdrawals"])),
            key=lambda item: item[1]["date"],
            reverse=True
        )

        for original_index, row in sorted_rows:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

                c1.write(f"**Дата:** {row['date']}")
                c2.write(f"**Ресторан:** {row['restaurant']}")
                c3.write(f"**Сумма:** {row['amount']:,.0f} ₽")

                if c4.button("Удалить", key=f"delete_withdrawal_{original_index}"):
                    data["withdrawals"].pop(original_index)
                    save_data(data)
                    st.success("Вывод удален")
                    st.rerun()

                st.caption(f"Режим: {row['mode']}")