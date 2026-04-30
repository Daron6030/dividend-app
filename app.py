import streamlit as st
import json
import os
from datetime import date

st.set_page_config(
    page_title="Dividends Space",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
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

# ---------- STYLE ----------

st.markdown("""
<style>
.stApp{
    background:#f6f7f9;
    color:#111827;
}

/* sidebar */
section[data-testid="stSidebar"]{
    background:#ffffff;
    border-right:1px solid #e5e7eb;
}

/* текст */
html, body, p, span, div, label, h1, h2, h3, h4, h5, h6{
    color:#111827 !important;
}

/* инпуты */
input, textarea{
    background:#ffffff !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
}

div[data-baseweb="input"]{
    background:#ffffff !important;
}

div[data-baseweb="input"] input{
    background:#ffffff !important;
    color:#111827 !important;
}

/* number input */
div[data-baseweb="base-input"]{
    background:#ffffff !important;
}

div[data-baseweb="base-input"] input{
    background:#ffffff !important;
    color:#111827 !important;
}

/* select */
div[data-baseweb="select"] *{
    color:#111827 !important;
}

/* metric cards */
div[data-testid="metric-container"]{
    background:#ffffff;
    border:1px solid #e5e7eb;
    padding:18px;
    border-radius:18px;
    box-shadow:0 8px 22px rgba(15,23,42,0.05);
}

/* buttons */
.stButton > button{
    width:100%;
    border-radius:12px;
    background:#ffffff;
    color:#111827;
    border:1px solid #d1d5db;
    font-weight:600;
}

.stButton > button:hover{
    background:#111827;
    color:#ffffff;
    border:1px solid #111827;
}

/* show sidebar toggle better */
button[kind="header"]{
    color:#111827 !important;
}
</style>
""", unsafe_allow_html=True)


# ---------- HELPERS ----------

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
        "01": "Январь", "02": "Февраль", "03": "Март",
        "04": "Апрель", "05": "Май", "06": "Июнь",
        "07": "Июль", "08": "Август", "09": "Сентябрь",
        "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"
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
    return {
        name: round(profit * percent / 100, 2)
        for name, percent in RESTAURANTS[restaurant].items()
    }


def fact_distribution(withdrawals):
    result = {"Ядровы": 0, "Тарасенко": 0, "Возврат инвестиций": 0}

    for row in withdrawals:
        amount = row["amount"]

        if row["mode"] == "До утверждения прибыли":
            result["Ядровы"] += amount / 2
            result["Тарасенко"] += amount / 2
        else:
            for name, percent in row["distribution"].items():
                result[name] += amount * percent / 100

    return result


def partner_amounts(partner, plan, fact):
    accrued = plan.get(partner, 0)
    withdrawn = fact.get(partner, 0)
    invest = 0

    if partner == "Ядровы":
        accrued += plan.get("Возврат инвестиций", 0)
        withdrawn += fact.get("Возврат инвестиций", 0)
        invest = plan.get("Возврат инвестиций", 0)

    balance = accrued - withdrawn
    return accrued, withdrawn, balance, invest


def summary(data, restaurant, month):
    profit = get_profit(data, restaurant, month)
    withdrawals = get_withdrawals(data, restaurant, month)

    plan = planned_distribution(restaurant, profit)
    fact = fact_distribution(withdrawals)

    y = partner_amounts("Ядровы", plan, fact)
    t = partner_amounts("Тарасенко", plan, fact)

    total = sum(x["amount"] for x in withdrawals)

    return profit, total, y, t, withdrawals


# ---------- SESSION ----------

if "user" not in st.session_state:
    st.session_state.user = None

if "menu" not in st.session_state:
    st.session_state.menu = "Главная"


# ---------- LOGIN ----------

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


# ---------- SIDEBAR ----------

with st.sidebar:
    st.markdown("### Dividends Space")
    st.caption(user["name"])
    st.divider()

    if user["role"] == "admin":
        if st.button("Главная"):
            st.session_state.menu = "Главная"
            st.rerun()

        if st.button("Ресторан"):
            st.session_state.menu = "Ресторан"
            st.rerun()

        if st.button("Архив"):
            st.session_state.menu = "Архив"
            st.rerun()

    st.divider()

    if st.button("Выйти"):
        st.session_state.user = None
        st.rerun()


# ---------- PARTNER ----------

if user["role"] == "partner":
    st.title("Мой кабинет")

    month = st.selectbox(
        "Месяц",
        all_months,
        index=0,
        format_func=month_label
    )

    restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit, total, y, t, w = summary(data, restaurant, month)

    if user["partner"] == "Ядровы":
        accrued, withdrawn, balance, invest = y
    else:
        accrued, withdrawn, balance, invest = t

    c1, c2, c3 = st.columns(3)
    c1.metric("Начислено", money(accrued))
    c2.metric("Выведено", money(withdrawn))
    c3.metric("Остаток", money(balance))

    if invest > 0 and user["partner"] == "Ядровы":
        st.caption(f"Из них {money(invest)} возврат инвестиций")

    st.stop()


# ---------- ADMIN ----------

menu = st.session_state.menu

if menu == "Главная":
    st.title("Главная")

    c1, c2 = st.columns(2)

    with c1:
        month = st.selectbox(
            "Месяц",
            all_months,
            index=0,
            format_func=month_label
        )

    with c2:
        restaurant = st.selectbox(
            "Ресторан",
            list(RESTAURANTS.keys())
        )

    profit, total, y, t, w = summary(data, restaurant, month)

    c1, c2, c3 = st.columns(3)
    c1.metric("Прибыль", money(profit))
    c2.metric("Выведено", money(total))
    c3.metric("Остаток", money(profit-total))

    st.divider()

    c4, c5 = st.columns(2)

    with c4:
        st.subheader("Ядровы")
        c = y
        st.metric("Остаток", money(c[2]))
        st.write("Начислено:", money(c[0]))
        st.write("Выведено:", money(c[1]))

    with c5:
        st.subheader("Тарасенко")
        c = t
        st.metric("Остаток", money(c[2]))
        st.write("Начислено:", money(c[0]))
        st.write("Выведено:", money(c[1]))


elif menu == "Ресторан":
    st.title("Ресторан")

    c1, c2 = st.columns(2)

    with c1:
        month = st.selectbox(
            "Месяц",
            all_months,
            index=0,
            format_func=month_label
        )

    with c2:
        restaurant = st.selectbox(
            "Ресторан",
            list(RESTAURANTS.keys())
        )

    profit, total, y, t, withdrawals = summary(data, restaurant, month)

    new_profit = st.number_input(
        "Утвержденная прибыль",
        min_value=0,
        step=10000,
        value=int(profit)
    )

    if st.button("Сохранить прибыль"):
        set_profit(data, restaurant, month, new_profit)
        save_data(data)
        st.success("Сохранено")
        st.rerun()

    st.divider()

    d = st.date_input("Дата вывода", value=today)
    amount = st.number_input("Сумма вывода", min_value=0, step=10000)

    mode = st.selectbox(
        "Режим",
        ["До утверждения прибыли", "После утверждения прибыли"]
    )

    if st.button("Добавить вывод"):
        dist = {"Ядровы": 50, "Тарасенко": 50}

        if mode == "После утверждения прибыли":
            dist = RESTAURANTS[restaurant]

        data["withdrawals"].append({
            "date": d.strftime("%Y-%m-%d"),
            "month": month,
            "restaurant": restaurant,
            "amount": amount,
            "mode": mode,
            "distribution": dist
        })

        save_data(data)
        st.success("Добавлено")
        st.rerun()


elif menu == "Архив":
    st.title("Архив")

    rows = sorted(
        list(enumerate(data["withdrawals"])),
        key=lambda x: x[1]["date"],
        reverse=True
    )

    for idx, row in rows:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2,2,2,1])

            c1.write(row["date"])
            c2.write(row["restaurant"])
            c3.write(money(row["amount"]))

            if c4.button("Удалить", key=f"d{idx}"):
                data["withdrawals"].pop(idx)
                save_data(data)
                st.rerun()
