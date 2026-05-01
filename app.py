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

st.markdown("""
<style>
section[data-testid="stSidebar"] {display:none !important;}
header[data-testid="stHeader"] {display:none !important;}

.stApp {
    background:#f6f7f9;
    color:#111827;
}

.block-container {
    padding-top: 1rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
}

h1,h2,h3,h4,h5,h6,p,label {
    color:#111827 !important;
}

/* верхняя плашка */
.app-header {
    background:#111827;
    border-radius:22px;
    padding:18px;
    margin-bottom:14px;
    box-shadow:0 10px 28px rgba(15,23,42,0.14);
}

.app-title {
    color:white !important;
    font-size:24px;
    font-weight:800;
}

.app-user {
    color:#d1d5db !important;
    font-size:14px;
    margin-top:4px;
}

/* горизонтальное меню по центру */
.nav-row {
    display:flex;
    flex-direction:row;
    flex-wrap:nowrap;
    justify-content:center;
    align-items:center;
    gap:10px;
    margin-bottom:26px;
    overflow-x:auto;
    width:100%;
}

.nav-row a {
    display:inline-flex;
    justify-content:center;
    align-items:center;
    text-decoration:none !important;
    background:#111827;
    color:white !important;
    padding:10px 16px;
    border-radius:13px;
    font-weight:700;
    font-size:15px;
    white-space:nowrap;
    border:1px solid #374151;
    min-width:90px;
}

.nav-row a:hover {
    background:#374151;
    color:white !important;
}

/* поля */
input, textarea {
    background:white !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
}

/* selectbox */
div[data-baseweb="select"] > div {
    background:white !important;
    color:#111827 !important;
    border:1px solid #d1d5db !important;
}

div[data-baseweb="select"] span {
    color:#111827 !important;
}

/* убираем странный вертикальный курсор/символ в selectbox */
div[data-baseweb="select"] input {
    caret-color: transparent !important;
    color: transparent !important;
}

div[data-baseweb="select"] svg {
    color:#9ca3af !important;
}

/* number input */
div[data-baseweb="input"] input {
    background:white !important;
    color:#111827 !important;
}

/* метрики компактнее */
div[data-testid="metric-container"] {
    background:white;
    border:1px solid #e5e7eb;
    padding:14px;
    border-radius:16px;
    box-shadow:0 8px 22px rgba(15,23,42,0.04);
}

div[data-testid="metric-container"] label {
    color:#6b7280 !important;
    font-size:14px !important;
}

div[data-testid="metric-container"] div {
    color:#111827 !important;
    font-size:30px !important;
}

/* обычные кнопки */
.stButton > button {
    width:100%;
    border-radius:12px;
    background:white;
    color:#111827 !important;
    border:1px solid #d1d5db;
    font-weight:600;
    padding:10px 16px;
}

.stButton > button:hover {
    background:#111827;
    color:white !important;
    border:1px solid #111827;
}

/* компактные карточки */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background:white;
}

/* мобильная версия */
@media (max-width: 768px) {
    .block-container {
        padding-left:1rem !important;
        padding-right:1rem !important;
        padding-top:0.7rem !important;
    }

    .app-header {
        padding:16px;
        border-radius:20px;
        margin-bottom:12px;
    }

    .app-title {
        font-size:22px;
    }

    .app-user {
        font-size:13px;
    }

    .nav-row {
        justify-content:center;
        gap:7px;
        margin-bottom:22px;
    }

    .nav-row a {
        font-size:13px;
        padding:9px 10px;
        min-width:auto;
    }

    h1 {
        font-size:36px !important;
        line-height:1.05 !important;
        margin-bottom:6px !important;
    }

    h2 {
        font-size:30px !important;
    }

    h3 {
        font-size:24px !important;
    }

    div[data-testid="metric-container"] {
        padding:12px;
        border-radius:14px;
    }

    div[data-testid="metric-container"] label {
        font-size:13px !important;
    }

    div[data-testid="metric-container"] div {
        font-size:26px !important;
    }

    p {
        font-size:15px !important;
    }
}
</style>
""", unsafe_allow_html=True)


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
    data["profits"].append({"restaurant": restaurant, "month": month, "amount": amount})


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


def summary(data, restaurant, month):
    profit = get_profit(data, restaurant, month)
    withdrawals = get_withdrawals(data, restaurant, month)

    plan = planned_distribution(restaurant, profit)
    fact = fact_distribution(withdrawals)

    yadrovy = partner_amounts("Ядровы", plan, fact)
    tarasenko = partner_amounts("Тарасенко", plan, fact)
    total_withdrawn = sum(x["amount"] for x in withdrawals)

    return profit, total_withdrawn, yadrovy, tarasenko, withdrawals


def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)


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


def render_nav(user):
    if user["role"] == "admin":
        st.markdown(
            """
            <div class="nav-row">
                <a href="?page=home">Главная</a>
                <a href="?page=restaurant">Ресторан</a>
                <a href="?page=archive">Архив</a>
                <a href="?page=logout">Выйти</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="nav-row">
                <a href="?page=logout">Выйти</a>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_admin_card(restaurant, month, profit, total, yadrovy, tarasenko):
    y_accrued, y_withdrawn, y_balance, invest_note = yadrovy
    t_accrued, t_withdrawn, t_balance, _ = tarasenko

    with st.container(border=True):
        st.subheader(restaurant)
        st.caption(month_label(month))

        c1, c2, c3 = st.columns(3)
        c1.metric("Прибыль", money(profit))
        c2.metric("Выведено", money(total))
        c3.metric("Остаток прибыли", money(profit - total))

        st.divider()

        c4, c5 = st.columns(2)

        with c4:
            st.markdown("### Ядровы")
            st.metric("Остаток", money(y_balance))
            st.write(f"Начислено: **{money(y_accrued)}**")
            st.write(f"Выведено: **{money(y_withdrawn)}**")
            if invest_note > 0:
                st.caption(f"Из них {money(invest_note)} — возврат инвестиций.")

        with c5:
            st.markdown("### Тарасенко")
            st.metric("Остаток", money(t_balance))
            st.write(f"Начислено: **{money(t_accrued)}**")
            st.write(f"Выведено: **{money(t_withdrawn)}**")


def render_partner_card(restaurant, month, accrued, withdrawn, balance, invest_note=0):
    with st.container(border=True):
        st.subheader(restaurant)
        st.caption(month_label(month))

        c1, c2, c3 = st.columns(3)
        c1.metric("Начислено", money(accrued))
        c2.metric("Выведено", money(withdrawn))
        c3.metric("Остаток", money(balance))

        if invest_note > 0:
            st.caption(f"Из них {money(invest_note)} — возврат инвестиций.")


if "user" not in st.session_state:
    st.session_state.user = None

if "menu" not in st.session_state:
    st.session_state.menu = "Главная"


query_page = st.query_params.get("page")

if query_page == "logout":
    st.session_state.user = None
    st.session_state.menu = "Главная"
    st.query_params.clear()
    st.rerun()

if query_page == "home":
    st.session_state.menu = "Главная"

if query_page == "restaurant":
    st.session_state.menu = "Ресторан"

if query_page == "archive":
    st.session_state.menu = "Архив"


if st.session_state.user is None:
    page_header("Dividends Space", "Кабинет распределения дивидендов")

    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        if login in USERS and USERS[login]["password"] == password:
            st.session_state.user = USERS[login]
            st.session_state.menu = "Главная"
            st.query_params.clear()
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

render_header(user)
render_nav(user)
st.divider()


if user["role"] == "partner":
    page_header("Мой кабинет", "Только нужные цифры без лишней информации")

    month = st.selectbox(
        "Месяц",
        all_months,
        index=all_months.index(current_month) if current_month in all_months else 0,
        format_func=month_label
    )

    restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

    if user["partner"] == "Ядровы":
        accrued, withdrawn, balance, invest = yadrovy
    else:
        accrued, withdrawn, balance, invest = tarasenko

    render_partner_card(
        restaurant,
        month,
        accrued,
        withdrawn,
        balance,
        invest if user["partner"] == "Ядровы" else 0
    )

    st.stop()


menu = st.session_state.menu

if menu == "Главная":
    page_header("Главная", "Выберите месяц и ресторан")

    c1, c2 = st.columns(2)

    with c1:
        month = st.selectbox(
            "Месяц",
            all_months,
            index=all_months.index(current_month) if current_month in all_months else 0,
            format_func=month_label
        )

    with c2:
        restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

    profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)

    render_admin_card(restaurant, month, profit, total, yadrovy, tarasenko)


elif menu == "Ресторан":
    page_header("Ресторан", "Ввод прибыли и выводов")

    c1, c2 = st.columns(2)

    with c1:
        month = st.selectbox(
            "Месяц",
            all_months,
            index=all_months.index(current_month) if current_month in all_months else 0,
            format_func=month_label
        )

    with c2:
        restaurant = st.selectbox("Ресторан", list(RESTAURANTS.keys()))

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
        withdrawal_date = st.date_input("Дата вывода", value=today)

    with c4:
        withdrawal_amount = st.number_input("Сумма вывода", min_value=0, step=10000)

    default_mode = "После утверждения прибыли" if profit > 0 else "До утверждения прибыли"

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

    render_admin_card(restaurant, month, profit, total, yadrovy, tarasenko)

    st.subheader("Выводы за месяц")

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
