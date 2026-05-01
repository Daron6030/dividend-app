import streamlit as st
import json
import os
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Dividends Space",
    page_icon="💼",
    layout="wide"
)

DATA_FILE = "data.json"

RESTAURANTS = {
    "Гончарная": ["Ядровы", "Тарасенко"],
    "Фонтанка": ["Ядровы", "Тарасенко", "Алиса"],
    "Спортивная": ["Ядровы", "Тарасенко"],
    "Загородный": ["Ядровы", "Тарасенко", "Алиса"],
    "Науки": ["Ядровы", "Тарасенко"]
}

USERS = {
    "Daron6030": {"password": "Daron6030?", "name": "Тарасенко Богдан"},
    "Iadrov": {"password": "181216", "name": "Ядровы"},
    "Alisa": {"password": "669933", "name": "Тарасенко Алиса"},
}

# -------------------------
# DATA
# -------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"profits": {}, "withdrawals": {}}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# -------------------------
# HELPERS
# -------------------------
def money(x):
    return f"{int(x):,}".replace(",", " ") + " ₽"

def current_month():
    return datetime.now().strftime("%Y-%m")

def month_label(m):
    y, mm = m.split("-")
    names = {
        "01":"Янв","02":"Фев","03":"Мар","04":"Апр",
        "05":"Май","06":"Июн","07":"Июл","08":"Авг",
        "09":"Сен","10":"Окт","11":"Ноя","12":"Дек"
    }
    return f"{names[mm]} {y}"

def get_profit(restaurant, month):
    return data["profits"].get(month, {}).get(restaurant, 0)

def get_withdraw(restaurant, month):
    return data["withdrawals"].get(month, {}).get(restaurant, 0)

def all_months():
    months = set(data["profits"].keys()) | set(data["withdrawals"].keys())
    if not months:
        months = {current_month()}
    return sorted(list(months))

# -------------------------
# LOGIN
# -------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class='topbox'><h1>Dividends Space</h1></div>", unsafe_allow_html=True)

    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти", use_container_width=True):
        if login in USERS and USERS[login]["password"] == password:
            st.session_state.auth = True
            st.session_state.user = USERS[login]["name"]
            st.rerun()
        else:
            st.error("Неверный логин или пароль")
    st.stop()

# -------------------------
# HEADER
# -------------------------
st.markdown(f"""
<div class='topbox'>
<h1>Dividends Space</h1>
<div>{st.session_state.user}</div>
</div>
""", unsafe_allow_html=True)

tab = st.radio(
    "",
    ["Главная", "Ресторан", "Архив", "Выйти"],
    horizontal=True,
    label_visibility="collapsed"
)

if tab == "Выйти":
    st.session_state.auth = False
    st.rerun()

# -------------------------
# MAIN
# -------------------------
if tab == "Главная":

    st.title("Главная")

    months = all_months()
    selected_month = st.selectbox(
        "Месяц",
        months,
        index=len(months)-1,
        format_func=month_label
    )

    selected_restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    # BACKUP
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        st.download_button(
            "Скачать резервную копию",
            f.read(),
            file_name="dividends_backup.json",
            mime="application/json"
        )

    # CHART
    st.subheader("Динамика прибыли за 6 месяцев")

    months6 = months[-6:]

    rows = []
    for m in months6:
        row = {"Месяц": month_label(m)}
        for r in RESTAURANTS:
            row[r] = get_profit(r, m)
        rows.append(row)

    st.line_chart(rows, x="Месяц", y=list(RESTAURANTS.keys()), height=260)

    # CARDS
    st.subheader("Все заведения за месяц")

    cols = st.columns(5)

    for i, r in enumerate(RESTAURANTS):
        p = get_profit(r, selected_month)
        w = get_withdraw(r, selected_month)

        with cols[i]:
            st.markdown(f"""
            <div class='smallcard'>
            <b>{r}</b><br><br>
            <div class='label'>Прибыль</div>
            <b>{money(p)}</b><br>
            <div class='label'>Выведено</div>
            <b>{money(w)}</b>
            </div>
            """, unsafe_allow_html=True)

    # PARTNERS
    st.subheader(f"Партнёры — {selected_restaurant}")

    total = get_profit(selected_restaurant, selected_month)
    out = get_withdraw(selected_restaurant, selected_month)

    count = len(RESTAURANTS[selected_restaurant])
    share = total / count if count else 0

    for person in RESTAURANTS[selected_restaurant]:
        st.markdown(f"""
        <div class='card'>
        <h2>{person}</h2>
        <div class='label'>Начислено</div>
        <div class='bigmoney'>{money(share)}</div>
        <div class='label'>Выведено</div>
        <div class='bigmoney'>{money(out/count if count else 0)}</div>
        <div class='label'>Остаток</div>
        <div class='bigmoney'>{money((share)-(out/count if count else 0))}</div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# RESTAURANT ADMIN
# -------------------------
if tab == "Ресторан":

    st.title("Ресторан")

    month = st.selectbox("Месяц", all_months(), format_func=month_label)
    restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit = st.number_input("Утвержденная прибыль", min_value=0, step=10000)
    withdraw = st.number_input("Выведено", min_value=0, step=10000)

    if st.button("Сохранить", use_container_width=True):

        if month not in data["profits"]:
            data["profits"][month] = {}

        if month not in data["withdrawals"]:
            data["withdrawals"][month] = {}

        data["profits"][month][restaurant] = int(profit)
        data["withdrawals"][month][restaurant] = int(withdraw)

        save_data(data)
        st.success("Сохранено")

# -------------------------
# ARCHIVE
# -------------------------
if tab == "Архив":

    st.title("Архив")

    for m in reversed(all_months()):
        st.subheader(month_label(m))

        for r in RESTAURANTS:
            p = get_profit(r, m)
            w = get_withdraw(r, m)

            st.markdown(f"""
            <div class='card'>
            <b>{r}</b><br>
            Прибыль: {money(p)}<br>
            Выведено: {money(w)}
            </div>
            """, unsafe_allow_html=True)
