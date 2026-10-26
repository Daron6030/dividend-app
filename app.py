import streamlit as st
import json
import os
import urllib.parse
import urllib.request
import requests
import base64
from datetime import date
from html import escape
import re

st.set_page_config(
    page_title="Старик Хинкалыч · Dividends Space",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "data.json"

try:
    USERS = {login: dict(record) for login, record in st.secrets.get("dividends_accounts_v20261026", {}).items()}
except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
    USERS = {}

RESTAURANTS = {
    "Гончарная": {"Ядровы": 50, "Тарасенко": 50},
    "Фонтанка": {"Ядровы": 33.33, "Тарасенко": 33.33, "Возврат инвестиций": 33.34},
    "Спортивная": {"Ядровы": 50, "Тарасенко": 50},
    "Загородный": {"Ядровы": 33.33, "Тарасенко": 33.33, "Возврат инвестиций": 33.34},
    "Науки": {"Ядровы": 50, "Тарасенко": 50},
}

SPORTIVNAYA_OLD_RULE_UNTIL = "2026-04"

# Monthly accrual only. Actual withdrawals remain separate recorded operations.
NAUKI_FIXED_START = "2026-10"
NAUKI_FIXED_MONTHLY_AMOUNT = 1_000_000

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
:root {--ink:#251d1c;--muted:#76706c;--accent:#691525;--line:#e7ded5;--paper:#faf7f2;--serif:Georgia,'Times New Roman',serif;}
section[data-testid="stSidebar"],header[data-testid="stHeader"] {display:none!important;}
.stApp {background:radial-gradient(ellipse at 95% 95%,#eee6d947,transparent 32%),var(--paper);color:var(--ink);}
.block-container {max-width:1440px;padding:18px 60px 44px!important;}
h1,h2,h3,h4 {font-family:var(--serif)!important;color:#40131b!important;letter-spacing:-.03em;}
h3 {font-size:26px!important;font-weight:700!important;}
p,label {color:var(--ink);}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,[data-testid="stCaption"] {color:var(--muted)!important;opacity:1!important;font-size:12px;}
.app-header {display:flex;justify-content:space-between;align-items:center;gap:24px;min-height:64px;margin:0 0 14px;}
.brand {display:flex;align-items:center;gap:13px;}
.brand-mark {display:grid;place-items:center;width:50px;height:50px;flex-shrink:0;background:var(--accent);border-radius:15px;color:#fff;box-shadow:0 3px 8px #4b0e1610;}
.brand-mark svg {width:34px;height:34px;}
.app-title {font-family:var(--serif);font-size:23px;font-weight:700;letter-spacing:-.6px;line-height:1.15;}
.brand-subtitle {font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:5px;}
.app-user {display:flex;gap:11px;align-items:center;font-size:12px;font-weight:600;line-height:1.55;}
.account-icon {display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#f1e9df;color:var(--accent);}
.account-icon svg {width:22px;height:22px;}
.user-role {font-size:11px;color:var(--muted);font-weight:400;}
[data-testid="stTabs"] {position:relative;}
[data-testid="stTabs"] [role="tablist"] {height:auto;gap:5px;padding:4px;background:#fff9;border:1px solid #e7ded599;border-radius:17px;margin-bottom:14px;width:fit-content;}
button[data-baseweb="tab"] {min-height:43px;padding:9px 15px!important;border-radius:12px;color:var(--ink)!important;gap:8px;}
button[data-baseweb="tab"] p {font-size:12px;font-weight:550;}
button[data-baseweb="tab"][aria-selected="true"] {background:#f0e0d3;box-shadow:inset 0 0 0 1px #e3cdb9;color:var(--accent)!important;}
button[data-baseweb="tab"][aria-selected="true"] p {color:var(--accent);font-weight:700;}
button[data-baseweb="tab"]::before {content:'';display:block;width:17px;height:17px;background:currentColor;mask:var(--nav-icon) center/contain no-repeat;flex-shrink:0;}
button[data-baseweb="tab"]:nth-of-type(1) {--nav-icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 11 12 3l9 8M5 10v11h5v-7h4v7h5V10' fill='none' stroke='black' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");}
button[data-baseweb="tab"]:nth-of-type(2) {--nav-icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 3v7c0 3 6 3 6 0V3M7 3v18M19 3c-3 3-4 7-4 10h4m0-10v18' fill='none' stroke='black' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");}
button[data-baseweb="tab"]:nth-of-type(3),body:has(.app-header[data-role="partner"]) button[data-baseweb="tab"]:nth-of-type(2) {--nav-icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 7V4h7l3 3h8v13H3V7Zm0 2h18' fill='none' stroke='black' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");}
button[data-baseweb="tab"]:nth-of-type(4),body:has(.app-header[data-role="partner"]) button[data-baseweb="tab"]:nth-of-type(3) {--nav-icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M10 4H4v16h6m5-13 5 5-5 5m-7-5h12' fill='none' stroke='black' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"] {display:none;}
.page-heading {position:relative;min-height:132px;display:flex;align-items:center;margin:0 0 8px;isolation:isolate;}
.hero-copy {position:relative;z-index:1;padding:12px 0;max-width:64%;}
.eyebrow {font-size:10px;letter-spacing:.19em;font-weight:700;color:var(--muted);margin-bottom:8px;}
.page-title {font-family:var(--serif);font-size:48px;font-weight:700;color:#30151a;line-height:1.07;letter-spacing:-1.5px;}
.page-description {font-size:14px;color:var(--muted);margin-top:10px;line-height:1.5;}
.page-heading::after {content:'';position:absolute;z-index:0;right:-48px;top:-8px;width:59%;height:218px;pointer-events:none;background:var(--hero-image) right center/cover no-repeat;mask-image:linear-gradient(to right,transparent 0%,#000 23%,#000 92%,transparent);}
.hero-overview {--hero-image:url('app/static/khinkalych/overview-hero.png');}
.hero-restaurant {--hero-image:url('app/static/khinkalych/restaurant-etching.png');}
.hero-restaurant::after {background-size:contain;width:49%;height:195px;top:0;opacity:.9;}
.hero-archive::after,.hero-plain::after {display:none;}
.hero-archive,.hero-plain {min-height:110px;}
div[data-baseweb="input"],div[data-baseweb="select"]>div,textarea {background:#fffdfb!important;border-radius:11px!important;color:var(--ink)!important;border-color:#d9d2ca!important;}
div[data-baseweb="select"]>div {min-height:44px;}
input,textarea {color:var(--ink)!important;font-variant-numeric:tabular-nums;}
input[type="text"],input[type="password"],textarea {background:#fffdfb!important;}
[data-testid="stWidgetLabel"] p {font-size:13px;font-weight:600;}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button {min-height:44px;border-radius:11px;border-color:#ddcfc2;font-weight:600;}
button[kind="primary"],button[kind="primaryFormSubmit"] {background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important;}
button[kind="primary"] p,button[kind="primaryFormSubmit"] p {color:#fff!important;font-weight:600;}
button[kind="primary"]:hover,button[kind="primaryFormSubmit"]:hover {background:#4e0d1a!important;border-color:#4e0d1a!important;}
button:focus-visible {outline:3px solid #ba8e68!important;outline-offset:3px;}
[data-testid="stForm"] {border:1px solid var(--line);border-radius:17px;background:#fffcf8;padding:24px!important;}
.form-heading {display:flex;align-items:center;justify-content:space-between;margin:0 0 14px;gap:14px;}
.form-title {font:700 26px/1.15 var(--serif);letter-spacing:-.6px;color:#4d1721;}
.form-illustration {color:#aa7863;opacity:.72;}
.form-illustration svg {width:42px;height:42px;}
.st-key-withdrawal_panel,.st-key-fixed_panel {border:1px solid var(--line);border-radius:17px;padding:24px;background:#fffcf8;}
.st-key-withdrawal_panel .stButton>button {width:100%;}
.st-key-editors [data-testid="stRadio"] [role="radiogroup"] {gap:8px;}
.st-key-editors [data-testid="stRadio"] [role="radiogroup"] label {border:1px solid var(--line);border-radius:10px;padding:8px 9px;background:#f9f5ef;flex:1;}
.st-key-editors [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {background:#efe0d2;border-color:#ddc4ae;}
.st-key-editors [data-testid="stRadio"] [role="radiogroup"] label p {font-size:12px;}
.st-key-editors [data-testid="stCheckbox"] label p {font-size:12px;}
.summary-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:0 0 10px;}
.summary-item {position:relative;display:flex;gap:14px;min-width:0;padding:20px 17px;border:1px solid #eadccc;border-radius:15px;background:linear-gradient(115deg,#fffcf8,#f7eee3);overflow:hidden;}
.summary-item:nth-child(2) {background:linear-gradient(115deg,#fffefa,#f0f0e5);border-color:#e1e1d2;}
.summary-item:nth-child(3) {background:linear-gradient(115deg,#fffcfa,#f9ece6);border-color:#ecd8ce;}
.summary-content {position:relative;z-index:1;}
.summary-icon {width:44px;height:44px;border-radius:50%;display:grid;place-items:center;flex-shrink:0;background:#ecd0b6;color:#6e3d20;}
.summary-icon svg {width:25px;height:25px;}
.summary-item:nth-child(2) .summary-icon {background:#e0e3cd;color:#535c38;}
.summary-item:nth-child(3) .summary-icon {background:#f0d4ca;color:#762d29;}
.summary-label {font-size:12px;font-weight:550;color:var(--ink);margin:1px 0 6px;}
.summary-value {font-size:28px;font-weight:650;letter-spacing:-1px;font-variant-numeric:tabular-nums;line-height:1.2;}
.summary-footnote {font-size:10px;color:var(--muted);margin-top:8px;}
.summary-ornament {position:absolute;right:-10px;bottom:-18px;width:94px;height:100px;color:#b7956c;opacity:.17;transform:rotate(-20deg);}
.summary-item:nth-child(2) .summary-ornament {color:#798556;}
.summary-item:nth-child(3) .summary-ornament {color:#a75543;}
.section-heading {display:flex;align-items:center;justify-content:space-between;gap:10px;margin:8px 0 10px;}
.section-title {font:700 25px/1.2 var(--serif);color:#3b1920;letter-spacing:-.5px;}
.section-note {font-size:11px;color:var(--muted);}
.cards-grid {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;}
.mini-card {background:#fffcf9;border:1px solid #ede2d6;border-radius:15px;padding:7px;min-width:0;box-shadow:0 5px 16px #53382004;overflow:hidden;}
.mini-card.selected {border-color:#8b4a28;box-shadow:0 0 0 1px #8b4a28;}
.restaurant-image {display:block;width:100%;height:100px;object-fit:cover;border-radius:10px;}
.mini-body {padding:11px 6px 5px;}
.mini-head {display:flex;gap:7px;align-items:center;margin-bottom:13px;}
.restaurant-symbol {display:grid;place-items:center;width:25px;height:25px;border-radius:50%;background:#efe0ce;color:#783e23;flex-shrink:0;}
.restaurant-symbol svg {width:16px;height:16px;}
.mini-title {font-size:13px;font-weight:650;white-space:nowrap;}
.mini-financials {display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:11px;}
.mini-financials>div+div {border-left:1px solid #eee6dd;padding-left:8px;}
.mini-label {font-size:10px;color:var(--muted);margin-bottom:4px;}
.mini-money {font-size:13px;font-weight:650;white-space:nowrap;font-variant-numeric:tabular-nums;}
.partner-progress-row {display:grid;grid-template-columns:12px minmax(0,1fr);align-items:center;gap:5px;margin-top:7px;}
.partner-letter {font-size:11px;font-weight:600;}
.progress-wrap {position:relative;height:17px;background:#ebe8e3;border-radius:5px;overflow:hidden;}
.progress-fill {height:100%;background:#c4cba9;}
.progress-inside {position:absolute;inset:0;display:grid;place-items:center;font-size:9px;font-weight:650;color:#34362c;white-space:nowrap;font-variant-numeric:tabular-nums;}
.overpaid .progress-fill {background:#f2d4cb;}
.overpaid .progress-inside,.negative {color:#9e2434!important;}
.mini-small {border-top:1px solid #eee6dd;padding-top:8px;font-size:10px;color:var(--muted);margin-top:10px;}
.mobile-only {display:none;}
.cards-caption {font-size:11px;color:var(--muted);margin:10px 0 16px;}
.partner-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:12px;}
.partner-box {position:relative;background:#fffcf8;border:1px solid var(--line);border-radius:17px;padding:20px 22px;overflow:hidden;}
.partner-heading {display:flex;gap:11px;align-items:center;margin-bottom:16px;}
.partner-avatar {width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:#e9ecd9;color:#4a4c33;font:700 20px var(--serif);flex-shrink:0;}
.partner-avatar.blue {background:#f1ddcb;color:#743d2d;}
.partner-title {font:700 21px var(--serif);color:#471b23;}
.partner-subtitle {font-size:11px;color:var(--muted);margin-top:3px;}
.partner-row {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;position:relative;z-index:1;}
.partner-row>div+div {border-left:1px solid #eee6dd;padding-left:15px;}
.partner-label {font-size:11px;color:var(--muted);margin-bottom:6px;}
.partner-money {font-size:18px;font-weight:650;letter-spacing:-.4px;white-space:nowrap;font-variant-numeric:tabular-nums;}
.partner-note {margin-top:13px;border-top:1px solid #eee6dd;padding-top:9px;font-size:11px;color:var(--muted);}
.partner-ornament {position:absolute;top:-10px;right:-10px;width:85px;color:#89925e;opacity:.17;transform:rotate(25deg);pointer-events:none;}
.closed-badge,.pending-badge {display:inline-block;padding:5px 9px;border-radius:7px;background:#eceddf;color:#5c6244;font-size:11px;margin-bottom:5px;}
.pending-badge {background:#f0e4d8;color:#76573f;}
.today-panel {border:1px solid #dbdcc8;background:#f0f1e7;padding:18px;border-radius:16px;margin:4px 0 12px;}
.today-title {font:700 22px var(--serif);margin-bottom:12px;}
.today-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;}
.today-card {background:#fffcf8;border:1px solid #e3e3d4;border-radius:10px;padding:12px;}
.today-restaurant {font-size:12px;font-weight:650;margin-bottom:6px;}
.today-line {font-size:12px;line-height:1.6;}
.today-total {font-size:13px;font-weight:600;margin-top:12px;}
.archive-main {display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:14px;margin-bottom:10px;}
.archive-detail {font-size:12px;color:var(--muted);line-height:1.8;}
.history-row {display:flex;justify-content:space-between;align-items:center;gap:14px;}
.history-date {font-size:13px;color:var(--muted);}
.history-amount {font-size:20px;font-weight:650;}
.preview-box {background:#f6eddf;border:1px solid #e7d4bf;border-radius:12px;padding:15px;margin:10px 0;}
.preview-title {font-size:11px;color:#796450;margin-bottom:8px;}
.preview-values {display:flex;gap:16px;flex-wrap:wrap;font-size:13px;}
.st-key-login {max-width:460px;margin:55px auto 0;}
.login-intro {text-align:center;padding:0 10px 18px;}
.login-intro .brand-mark {margin:0 auto 16px;}
.login-intro .page-title {font-size:36px;}
.login-footer {text-align:center;font-size:11px;color:var(--muted);margin-top:15px;}
@media(min-width:901px) {
 button[data-baseweb="tab"] p {font-size:14px;}
 .app-user {font-size:14px;}.user-role {font-size:12px;}
 .summary-label {font-size:14px;}.summary-value {font-size:30px;}.summary-footnote {font-size:12px;}
 .mini-title {font-size:14px;}.mini-label {font-size:12px;}.mini-money {font-size:16px;}
 .progress-inside {font-size:11px;}.mini-small {font-size:11px;}
 .cards-caption {font-size:12px;}.partner-label {font-size:12px;}.partner-money {font-size:20px;}
 .partner-subtitle {font-size:12px;}.partner-note {font-size:12px;}
}
@media(min-width:1150px) {
 [data-testid="stTabs"] [role="tablist"] {position:absolute;top:-83px;left:50%;transform:translateX(-50%);z-index:2;margin:0;}
 .st-key-editors [data-testid="stForm"] {min-height:410px;}
 .st-key-editors [data-testid="stColumn"]:has([data-testid="stForm"])>div {height:100%;}
 .st-key-editors [data-testid="stLayoutWrapper"]:has(>[data-testid="stForm"]) {flex:1;}
 .st-key-editors [data-testid="stForm"] {flex:1;height:auto;}
 .st-key-fixed_panel {min-height:280px;}
}
@media(max-width:1149px) {
 .block-container {padding:18px 28px 40px!important;}
 [data-testid="stTabs"] [role="tablist"] {width:100%;}
 button[data-baseweb="tab"] {flex:1;justify-content:center;}
 .page-title {font-size:41px;}
 .hero-copy {max-width:65%;}
 .hero-restaurant::after {width:43%;}
 .summary-item {padding:16px 12px;gap:9px;}
 .summary-icon {width:36px;height:36px;}
 .mini-head {gap:4px;}
 .mini-title {font-size:11px;}
 .restaurant-symbol {width:20px;height:20px;}
 .mini-money {font-size:11px;}
 .partner-money {font-size:17px;}
}
@media(max-width:900px) {
 .summary-icon {display:none;}
 .summary-value {font-size:24px;}
 .restaurant-image {height:72px;}
 .restaurant-symbol {display:none;}
 .mini-financials {grid-template-columns:1fr;gap:7px;}
 .mini-financials>div+div {border:0;padding:0;}
 .partner-grid {grid-template-columns:1fr;}
 .hero-restaurant::after {opacity:.4;}
 .st-key-withdrawal_panel,[data-testid="stForm"] {padding:17px!important;}
}
@media(max-width:600px) {
 .block-container {padding:14px 12px 32px!important;}
 .app-header {gap:8px;min-height:48px;margin-bottom:4px;}
 .brand {gap:8px;}
 .brand-mark {width:37px;height:37px;border-radius:11px;}
 .brand-mark svg {width:26px;height:26px;}
 .app-title {font-size:17px;}
 .brand-subtitle {font-size:7px;letter-spacing:.06em;}
 .app-user {font-size:9px;max-width:90px;text-align:right;line-height:1.4;}
 .account-icon {display:none;}.user-role {font-size:8px;}
 [data-testid="stTabs"] [role="tablist"] {padding:3px;gap:2px;border-radius:12px;margin-bottom:0;}
 button[data-baseweb="tab"] {padding:8px 3px!important;min-height:42px;gap:4px;}
 button[data-baseweb="tab"] p {font-size:11px;}
 button[data-baseweb="tab"]::before {width:14px;height:14px;}
 .page-heading {min-height:112px;margin:0 0 4px;}
 .hero-copy {max-width:100%;padding:14px 0;}
 .eyebrow {font-size:8px;letter-spacing:.13em;margin-bottom:8px;}
 .page-title {font-size:34px;letter-spacing:-1px;}
 .page-description {font-size:12px;max-width:88%;line-height:1.5;margin-top:7px;}
 .page-heading::after {height:118px;top:8px;right:-12px;width:47%;opacity:.14;mask-image:linear-gradient(to right,transparent,#000 50%);}
 .hero-restaurant .page-title {font-size:31px;}
 .summary-grid {gap:5px;margin-bottom:7px;}
 .summary-item {padding:13px 9px;border-radius:11px;min-width:0;}
 .summary-label {font-size:9px;min-height:24px;line-height:1.25;}
 .summary-value {font-size:20px;letter-spacing:-.6px;}
 .summary-footnote {font-size:8px;line-height:1.45;min-height:24px;margin-top:7px;}
 .summary-ornament {width:60px;right:-20px;bottom:-40px;opacity:.1;}
 .section-title {font-size:24px;}.section-note {font-size:9px;}
 .cards-grid {gap:4px;}
 .mini-card {padding:3px;border-radius:9px;}
 .restaurant-image {height:39px;border-radius:6px;}
 .mini-body {padding:8px 2px 4px;}
 .mini-head {margin-bottom:10px;}
 .mini-title {font-size:9px;}
 .mini-financials {gap:7px;margin-bottom:9px;}
 .mini-label {font-size:8px;margin-bottom:3px;}
 .mini-money {font-size:10px;}
 .partner-progress-row {grid-template-columns:7px minmax(0,1fr);gap:2px;margin-top:5px;}
 .partner-letter {font-size:8px;}.progress-wrap {height:15px;border-radius:4px;}.progress-inside {font-size:7px;}
 .mini-small {font-size:7.5px;margin-top:8px;padding-top:7px;}
 .desktop-only {display:none;}.mobile-only {display:inline;}
 .cards-caption {font-size:9px;line-height:1.6;margin:9px 0 12px;}
 .partner-grid {gap:10px;}
 .partner-box {padding:17px 13px;border-radius:14px;}
 .partner-heading {margin-bottom:16px;}
 .partner-title {font-size:21px;}
 .partner-subtitle {font-size:10px;}.partner-avatar {width:38px;height:38px;}
 .partner-row {gap:5px;}.partner-row>div+div {padding-left:8px;}
 .partner-label {font-size:9px;}.partner-money {font-size:15px;letter-spacing:-.4px;}
 .partner-note {font-size:10px;}
 .form-title {font-size:25px;}.form-illustration svg {width:30px;height:30px;}
 .st-key-withdrawal_panel,.st-key-fixed_panel,[data-testid="stForm"] {padding:16px!important;border-radius:14px;}
 .st-key-editors [data-testid="stRadio"] [role="radiogroup"] label {flex-basis:100%;}
 .today-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
 .archive-main {flex-wrap:wrap;align-items:flex-start;font-size:13px;}
 .st-key-login {margin-top:28px;}
 input,textarea {font-size:16px!important;}
}
@media(prefers-reduced-motion:reduce) {*,*::before,*::after {animation:none!important;transition:none!important;}}

</style>
""", unsafe_allow_html=True)


def money(value):
    number = float(value)
    decimals = 0 if round(number, 2).is_integer() else 2
    return f"{number:,.{decimals}f}".replace(",", " ").replace(".", ",") + " ₽"


def format_input_money(value):
    if value is None or value == "":
        return ""
    try:
        return f"{int(float(value)):,}".replace(",", " ")
    except Exception:
        return ""


def parse_money(value):
    if value is None:
        return 0
    cleaned = str(value).replace(" ", "").replace("₽", "").replace(",", "").strip()
    if cleaned == "":
        return 0
    try:
        return int(float(cleaned))
    except Exception:
        return 0


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
                        "distribution": get_distribution(restaurant, month),
                        "notify": True,
                        "comment": ""
                    })
        data["withdrawals"] = new_withdrawals

    for row in data["profits"]:
        row["restaurant"] = normalize_restaurant_name(row["restaurant"])

    for row in data["withdrawals"]:
        row["restaurant"] = normalize_restaurant_name(row["restaurant"])
        if "notify" not in row:
            row["notify"] = True
        if "comment" not in row:
            row["comment"] = ""

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


def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


def github_headers():
    token = get_secret("GITHUB_TOKEN", "")
    if not token:
        return None

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }


def github_api_url():
    repo = get_secret("GITHUB_REPO", "")
    if not repo:
        return None

    return f"https://api.github.com/repos/{repo}/contents/{DATA_FILE}"


def load_data_from_github():
    headers = github_headers()
    api_url = github_api_url()

    if not headers or not api_url:
        return None

    try:
        response = requests.get(api_url, headers=headers, timeout=20)

        if response.status_code != 200:
            return None

        payload = response.json()
        content = payload.get("content", "")
        decoded = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded)

    except Exception as e:
        print("GitHub load error:", e)
        return None


def save_data_to_github(json_content):
    headers = github_headers()
    api_url = github_api_url()

    if not headers or not api_url:
        return False

    try:
        sha = None
        current = requests.get(api_url, headers=headers, timeout=20)

        if current.status_code == 200:
            sha = current.json().get("sha")

        encoded_content = base64.b64encode(
            json_content.encode("utf-8")
        ).decode("utf-8")

        payload = {
            "message": "Auto update data.json",
            "content": encoded_content,
            "branch": "main"
        }

        if sha:
            payload["sha"] = sha

        result = requests.put(
            api_url,
            headers=headers,
            json=payload,
            timeout=20
        )

        return result.status_code in [200, 201]

    except Exception as e:
        print("GitHub save error:", e)
        return False


def load_data():
    github_data = load_data_from_github()

    if github_data is not None:
        data = normalize_data(github_data)
        apply_initial_profits(data)

        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

        return data

    if not os.path.exists(DATA_FILE):
        data = {"profits": [], "withdrawals": []}
        apply_initial_profits(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    data = normalize_data(loaded)
    apply_initial_profits(data)

    return data


def save_data(data):
    data = normalize_data(data)

    json_content = json.dumps(
        data,
        ensure_ascii=False,
        indent=4
    )

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json_content)

    save_data_to_github(json_content)


def all_months(data):
    months = set()

    for row in data["profits"]:
        months.add(row["month"])

    for row in data["withdrawals"]:
        months.add(row["month"])

    months.update(fixed_accrual_months())
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


def is_fixed_accrual(restaurant, month):
    return normalize_restaurant_name(restaurant) == "Науки" and month >= NAUKI_FIXED_START


def fixed_accrual_months(through_month=None):
    """List elapsed/current months for the archive, never future payments."""
    last_month = through_month or month_key(date.today())
    result = []
    month = NAUKI_FIXED_START
    while month <= last_month:
        result.append(month)
        month = add_months(month, 1)
    return result


def get_profit(data, restaurant, month):
    restaurant = normalize_restaurant_name(restaurant)
    if is_fixed_accrual(restaurant, month):
        return NAUKI_FIXED_MONTHLY_AMOUNT

    for row in data["profits"]:
        if row["restaurant"] == restaurant and row["month"] == month:
            return row["amount"]

    return 0


def set_profit(data, restaurant, month, amount):
    restaurant = normalize_restaurant_name(restaurant)
    if is_fixed_accrual(restaurant, month):
        raise ValueError("Начисление Науки фиксировано: 1 000 000 ₽ в месяц.")

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


def distribution_to_partners(amount, distribution):
    result = {"Ядровы": 0, "Тарасенко": 0}

    for name, percent in distribution.items():
        value = amount * percent / 100

        if name == "Возврат инвестиций":
            result["Ядровы"] += value
        elif name in result:
            result[name] += value

    return result


def get_today_payouts(data):
    today = date.today().strftime("%Y-%m-%d")
    result = {}
    totals = {"Ядровы": 0, "Тарасенко": 0}

    for row in data["withdrawals"]:
        if row.get("date") != today:
            continue

        restaurant = normalize_restaurant_name(row["restaurant"])
        amount = row.get("amount", 0)
        mode = row.get("mode", "")

        if mode == "До утверждения прибыли":
            distribution = {"Ядровы": 50, "Тарасенко": 50}
        else:
            distribution = row.get("distribution") or get_distribution(restaurant, row["month"])

        partners = distribution_to_partners(amount, distribution)

        if restaurant not in result:
            result[restaurant] = {"Ядровы": 0, "Тарасенко": 0}

        result[restaurant]["Ядровы"] += partners["Ядровы"]
        result[restaurant]["Тарасенко"] += partners["Тарасенко"]

        totals["Ядровы"] += partners["Ядровы"]
        totals["Тарасенко"] += partners["Тарасенко"]

    return result, totals


def send_telegram_message(chat_id, text):
    token = get_secret("TELEGRAM_BOT_TOKEN", "")

    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, method="POST")
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


def get_telegram_recipients():
    recipients = []

    tarasenko_chat_id = get_secret("TELEGRAM_CHAT_ID_TARASENKO", "")
    yadrovy_chat_id = get_secret("TELEGRAM_CHAT_ID_YADROVY", "")
    alisa_chat_id = get_secret("TELEGRAM_CHAT_ID_ALISA", "")

    if tarasenko_chat_id:
        recipients.append(tarasenko_chat_id)

    if yadrovy_chat_id:
        recipients.append(yadrovy_chat_id)

    if alisa_chat_id:
        recipients.append(alisa_chat_id)

    return recipients


def notify_telegram_withdrawal(restaurant, month):
    recipients = get_telegram_recipients()

    if not recipients:
        return False

    text = (
        "💸✨ <b>Dividends Space</b>\n\n"
        "🎉 Сегодня вывод денег!\n"
        "Хороший день для приятных поступлений 🙌\n\n"
        f"🏪 Ресторан: <b>{restaurant}</b>\n"
        f"📅 Месяц прибыли: <b>{month_label(month)}</b>\n\n"
        "📲 Подробности доступны в личном кабинете."
    )

    ok = True

    for chat_id in recipients:
        sent = send_telegram_message(chat_id, text)
        if not sent:
            ok = False

    return ok


def notify_telegram_profit_saved(restaurant, month):
    recipients = get_telegram_recipients()

    if not recipients:
        return False

    text = (
        "📊✨ <b>Dividends Space</b>\n\n"
        "✅ Чистая прибыль распределена.\n"
        "Можно заглянуть в личный кабинет и посмотреть обновленные данные 🙌\n\n"
        f"🏪 Ресторан: <b>{restaurant}</b>\n"
        f"📅 Месяц прибыли: <b>{month_label(month)}</b>\n\n"
        "📲 Подробности доступны в личном кабинете."
    )

    ok = True

    for chat_id in recipients:
        sent = send_telegram_message(chat_id, text)
        if not sent:
            ok = False

    return ok


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


RESTAURANT_COLORS = {restaurant: "#d4d4d8" for restaurant in RESTAURANTS}
SHORT_NAMES = {
    "Гончарная": "Гончар.", "Фонтанка": "Фонтанка", "Спортивная": "Спортив.",
    "Загородный": "Загород.", "Науки": "Науки",
}


RESTAURANT_IMAGES = {
    "Гончарная": "goncharnaya.png", "Фонтанка": "fontanka.png", "Спортивная": "sportivnaya.png",
    "Загородный": "zagorodny.png", "Науки": "nauki.png",
}


def ui_icon(name):
    paths = {
        "khinkali": '<path d="M10 6c-2-4 6-4 4 0l-1 3c2 3 7 6 8 10 1 5-19 5-18 0 1-4 6-7 8-10Zm1 4c-2 4-4 6-4 10m5-10v11m1-11c2 4 4 6 4 10M9 5h6"/>',
        "user": '<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',
        "coins": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 10c0 4 16 4 16 0M4 15c0 4 16 4 16 0"/>',
        "arrow": '<path d="M5 19 19 5M6 5h13v13"/>',
        "hourglass": '<path d="M6 3h12M6 21h12M7 3v3c0 3 10 9 10 12v3M17 3v3c0 3-10 9-10 12v3M9 18h6"/>',
        "store": '<path d="M4 10v11h16V10M2 10l3-7h14l3 7c0 4-5 4-5 0 0 4-5 4-5 0 0 4-5 4-5 0 0 4-5 4-5 0ZM9 21v-7h6v7"/>',
        "approval": '<path d="M7 3H4v19h16V3h-3M8 2h8v4H8ZM8 11h8M8 15h3m2 2 2 2 5-6"/>',
        "payout": '<circle cx="12" cy="12" r="10"/><path d="M9 18V6h4a4 4 0 0 1 0 8H7m0 3h8"/>',
    }
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.55" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths[name] + '</svg>'


def leaf_ornament():
    return '<svg viewBox="0 0 100 130" fill="currentColor" aria-hidden="true"><path d="M48 125C45 85 53 49 79 9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M50 110C21 111 13 91 16 82c23 1 32 14 34 28ZM48 89C23 86 20 66 23 58c22 5 28 18 25 31ZM53 65C30 59 32 37 38 29c18 11 21 23 15 36ZM65 40C48 29 52 10 61 3c12 13 14 26 4 37ZM49 105C76 107 86 87 83 78c-23 1-32 13-34 27ZM51 80C77 83 90 64 90 54c-23-2-35 10-39 26ZM61 54C84 57 98 41 98 30c-22-1-34 8-37 24Z"/></svg>'


def form_heading(title, icon):
    st.markdown(f'<div class="form-heading"><div class="form-title">{escape(title)}</div>'
                f'<div class="form-illustration">{ui_icon(icon)}</div></div>', unsafe_allow_html=True)


def compact_money(value):
    value = float(value)
    magnitude = abs(value)
    if magnitude >= 1_000_000:
        return f"{value / 1_000_000:.1f}".replace(".0", "").replace(".", ",") + "м"
    if magnitude >= 1000:
        return f"{value / 1000:.1f}".replace(".0", "").replace(".", ",") + "к"
    return f"{value:,.2f}".rstrip("0").rstrip(".").replace(",", " ").replace(".", ",")


def responsive_money(value):
    return (f'<span class="desktop-only">{money(value)}</span>'
            f'<span class="mobile-only" title="{money(value)}">{compact_money(value)}</span>')


def profit_is_recorded(data, restaurant, month):
    if is_fixed_accrual(restaurant, month):
        return True
    # Legacy zeroes for Науки mean missing history, not an approved zero profit.
    if restaurant == "Науки" and month in CLOSED_MONTHS and get_profit(data, restaurant, month) == 0:
        return False
    return any(row["restaurant"] == restaurant and row["month"] == month for row in data["profits"])


def page_heading(title, description, eyebrow="DIVIDENDS SPACE", kind="plain"):
    st.markdown(f'<div class="page-heading hero-{kind}"><div class="hero-copy"><div class="eyebrow">{escape(eyebrow)}</div>'
                f'<div class="page-title">{escape(title)}</div>'
                f'<div class="page-description">{escape(description)}</div></div></div>', unsafe_allow_html=True)


def render_header(user):
    role = "Администратор" if user["role"] == "admin" else "Просмотр финансов"
    st.markdown(f'<div class="app-header" data-role="{escape(user["role"])}"><div class="brand"><div class="brand-mark">{ui_icon("khinkali")}</div>'
                '<div><div class="app-title">Старик Хинкалыч</div>'
                '<div class="brand-subtitle">Dividends Space · кабинет партнёров</div></div></div>'
                f'<div class="app-user"><div class="account-icon">{ui_icon("user")}</div><div>{escape(user["name"])}'
                f'<div class="user-role">{role}</div></div></div></div>', unsafe_allow_html=True)


def render_today_payout_panel(data):
    payouts, totals = get_today_payouts(data)
    if not payouts:
        return
    html = '<div class="today-panel"><div class="today-title">Сегодня к выдаче</div><div class="today-grid">'
    for restaurant, values in payouts.items():
        html += (f'<div class="today-card"><div class="today-restaurant">{escape(restaurant)}</div>'
                 f'<div class="today-line">Ядровы <b>{money(values["Ядровы"])}</b></div>'
                 f'<div class="today-line">Тарасенко <b>{money(values["Тарасенко"])}</b></div></div>')
    html += (f'</div><div class="today-total">Итого · Ядровы {money(totals["Ядровы"])}'
             f' · Тарасенко {money(totals["Тарасенко"])}</div></div>')
    st.markdown(html, unsafe_allow_html=True)


def render_backup_button(data):
    st.download_button("Скачать резервную копию", json.dumps(data, ensure_ascii=False, indent=4),
                       file_name=f"dividends_backup_{date.today().isoformat()}.json", mime="application/json")


def render_month_summary(data, month):
    rows = [summary(data, restaurant, month) for restaurant in RESTAURANTS]
    profit = sum(row[0] for row in rows)
    withdrawn = sum(row[1] for row in rows)
    approved = sum(profit_is_recorded(data, restaurant, month) for restaurant in RESTAURANTS)
    values = [("Начислено по сети", profit if approved else None, f"Есть начисления: {approved} из {len(RESTAURANTS)} ресторанов", "coins"),
              ("Выведено", withdrawn, "По всем ресторанам за месяц", "arrow"),
              ("Остаток", profit - withdrawn if approved or withdrawn else None,
               "Предварительный расчёт" if approved < 5 and not is_closed_month(month) else "Начислено минус выведено", "hourglass")]
    html = '<div class="summary-grid">'
    for label, value, note, icon in values:
        negative = " negative" if value is not None and value < 0 else ""
        html += (f'<div class="summary-item"><div class="summary-icon">{ui_icon(icon)}</div><div class="summary-content">'
                 f'<div class="summary-label">{label}</div><div class="summary-value{negative}">{responsive_money(value) if value is not None else "—"}</div>'
                 f'<div class="summary-footnote">{note}</div></div><div class="summary-ornament">{leaf_ornament()}</div></div>')
    st.markdown(html + '</div>', unsafe_allow_html=True)


def render_partner_progress(letter, accrued, withdrawn, balance, known=True):
    progress = min(max(withdrawn / accrued, 0), 1) if accrued > 0 else 0
    state = " overpaid" if balance < 0 else ""
    label = f"{letter}: выведено {money(withdrawn)}, остаток {money(balance)}"
    return (f'<div class="partner-progress-row{state}"><div class="partner-letter">{letter}</div>'
            f'<div class="progress-wrap" role="img" aria-label="{label}" title="{label}">'
            f'<div class="progress-fill" style="width:{progress * 100:.1f}%;"></div>'
            f'<div class="progress-inside">{responsive_money(balance) if known or withdrawn else "—"}</div></div></div>')


def render_all_restaurant_cards(data, month, selected_restaurant):
    html = '<div class="cards-grid">'
    for restaurant in RESTAURANTS:
        profit, total, yadrovy, tarasenko, _ = summary(data, restaurant, month)
        known = profit_is_recorded(data, restaurant, month)
        fixed = is_fixed_accrual(restaurant, month)
        status = "Фикс" if fixed else "Закрыто" if is_closed_month(month) and known else "Утверждено" if known else "Нет данных"
        if restaurant == "Науки" and not fixed and not known:
            status = "С окт. 26"
        amount_label = "Начислено" if fixed else "Прибыль"
        selected = " selected" if restaurant == selected_restaurant else ""
        html += (f'<div class="mini-card{selected}" title="{restaurant}">'
                 f'<img class="restaurant-image" src="app/static/khinkalych/{RESTAURANT_IMAGES[restaurant]}" alt="" loading="lazy" decoding="async">'
                 f'<div class="mini-body"><div class="mini-head"><span class="restaurant-symbol">{ui_icon("store")}</span>'
                 f'<div class="mini-title"><span class="desktop-only">{restaurant}</span><span class="mobile-only">{SHORT_NAMES[restaurant]}</span></div></div>'
                 f'<div class="mini-financials"><div><div class="mini-label">{amount_label}</div><div class="mini-money">{responsive_money(profit) if known else "—"}</div></div>'
                 f'<div><div class="mini-label">Выведено</div><div class="mini-money">{responsive_money(total)}</div></div></div>'
                 f'{render_partner_progress("Я", *yadrovy[:3], known)}{render_partner_progress("Т", *tarasenko[:3], known)}'
                 f'<div class="mini-small">{status}</div></div></div>')
    st.markdown(html + '</div><div class="cards-caption">Я — Ядровы · Т — Тарасенко. '
                'В полосах — остаток к выплате; заполнением показана выплаченная доля. '
                '<span class="mobile-only">к — тыс. ₽, м — млн ₽. Точные суммы — ниже.</span></div>', unsafe_allow_html=True)


def render_partner_details(yadrovy, tarasenko, known=True):
    html = '<div class="partner-grid">'
    for name, amounts, initials, color in [("Ядровы", yadrovy, "Я", ""), ("Тарасенко", tarasenko, "Т", " blue")]:
        accrued, withdrawn, balance, invest = amounts
        html += (f'<div class="partner-box"><div class="partner-ornament">{leaf_ornament()}</div><div class="partner-heading"><div class="partner-avatar{color}">{initials}</div>'
                 f'<div><div class="partner-title">{name}</div><div class="partner-subtitle">Дивиденды за выбранный месяц</div></div></div>'
                 '<div class="partner-row">')
        for label, amount in [("Начислено", accrued), ("Выведено", withdrawn), ("Остаток", balance)]:
            visible = known or label == "Выведено" or (label == "Остаток" and withdrawn > 0)
            negative = " negative" if visible and amount < 0 else ""
            html += f'<div><div class="partner-label">{label}</div><div class="partner-money{negative}">{money(amount) if visible else "—"}</div></div>'
        html += '</div>'
        notes = []
        if invest > 0:
            notes.append(f"В начислении учтён возврат инвестиций: {money(invest)}.")
        if not known:
            notes.append("Прибыль не утверждена. Остаток предварительный." if withdrawn else "Прибыль за этот период не указана.")
        elif balance < 0:
            notes.append(f"Выведено сверх начисления: {money(-balance)}.")
        if notes:
            html += '<div class="partner-note">' + ' '.join(notes) + '</div>'
        html += '</div>'
    st.markdown(html + '</div>', unsafe_allow_html=True)


def select_month(key, months, default_month=None, label="Месяц прибыли"):
    if key not in st.session_state:
        st.session_state[key] = default_month if default_month in months else months[0]
    return st.selectbox(label, months, format_func=month_label, key=key)


def select_restaurant(key):
    return st.selectbox("Ресторан", list(RESTAURANTS), key=key)


def render_overview(data, months, prefix, title):
    page_heading(title, "Прибыль, выплаты и остатки — за выбранный месяц.", "ОБЗОР ФИНАНСОВ", kind="overview")
    c1, c2 = st.columns(2)
    with c1:
        month = select_month(f"{prefix}_month", months, previous_month_key(date.today()))
    with c2:
        restaurant = select_restaurant(f"{prefix}_restaurant")
    if is_closed_month(month):
        st.markdown('<div class="closed-badge">Закрытый месяц · дивиденды выплачены</div>', unsafe_allow_html=True)
    render_today_payout_panel(data)
    render_month_summary(data, month)
    st.markdown(f'<div class="section-heading"><div class="section-title">Рестораны</div>'
                f'<div class="section-note">{month_label(month)}</div></div>', unsafe_allow_html=True)
    render_all_restaurant_cards(data, month, restaurant)
    st.markdown(f'<div class="section-heading"><div class="section-title">{restaurant} · партнёры</div></div>', unsafe_allow_html=True)
    if is_fixed_accrual(restaurant, month):
        st.caption("Науки · фиксированное начисление 1 000 000 ₽ в месяц: Ядровы — 500 000 ₽, Тарасенко — 500 000 ₽. Действует с октября 2026.")
    _, _, yadrovy, tarasenko, _ = summary(data, restaurant, month)
    render_partner_details(yadrovy, tarasenko, profit_is_recorded(data, restaurant, month))


def display_date(value):
    try:
        return date.fromisoformat(value).strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return str(value or "Дата не указана")


def render_withdrawal_row(row):
    st.markdown(f'<div class="history-row"><div class="history-date">{escape(display_date(row.get("date")))}</div>'
                f'<div class="history-amount">{money(row.get("amount", 0))}</div></div>', unsafe_allow_html=True)
    # The legacy notify flag records intent, not successful delivery.
    notification = "Telegram включён" if row.get("notify", True) else "Без уведомления"
    st.caption(f'{row.get("mode", "")} · {notification}')
    if row.get("comment"):
        st.text(row["comment"])


def render_archive(data, months):
    page_heading("Архив", "История прибыли и выплат. Выберите год и раскройте нужный месяц.", "ФИНАНСОВАЯ ИСТОРИЯ", kind="archive")
    available = sorted({row["month"] for row in data["profits"] + data["withdrawals"]} | set(fixed_accrual_months()), reverse=True)
    years = sorted({m[:4] for m in available}, reverse=True)
    c1, c2 = st.columns(2)
    with c1:
        year = st.selectbox("Год", ["Все годы"] + years, key="archive_year")
    with c2:
        restaurant_filter = st.selectbox("Ресторан в архиве", ["Все рестораны"] + list(RESTAURANTS), key="archive_restaurant")
    matching = [m for m in available if year == "Все годы" or m.startswith(year)]
    restaurants = list(RESTAURANTS) if restaurant_filter == "Все рестораны" else [restaurant_filter]
    if not matching:
        st.info("За выбранный период данных пока нет.")
    for i, month in enumerate(matching):
        total = sum(get_profit(data, r, month) for r in restaurants)
        status = " · Закрыт" if is_closed_month(month) else ""
        with st.expander(f"{month_label(month)}{status} · {money(total)}", expanded=i == 0):
            shown = False
            for restaurant in restaurants:
                profit, withdrawn, yadrovy, tarasenko, rows = summary(data, restaurant, month)
                known = profit_is_recorded(data, restaurant, month)
                if not known and not rows:
                    continue
                shown = True
                with st.container(border=True):
                    amount_label = "Фиксированное начисление" if is_fixed_accrual(restaurant, month) else "Прибыль"
                    st.markdown(f'<div class="archive-main"><strong>{restaurant}</strong>'
                                f'<span>{amount_label} <b>{money(profit) if known else "—"}</b> · Выведено <b>{money(withdrawn)}</b></span></div>', unsafe_allow_html=True)
                    details = []
                    for name, amounts in [("Ядровы", yadrovy), ("Тарасенко", tarasenko)]:
                        accrued, paid, balance, invest = amounts
                        details.append(f'{name} · начислено {money(accrued) if known else "—"} · выведено {money(paid)} · остаток {money(balance)}')
                        if invest:
                            details.append(f'В том числе возврат инвестиций: {money(invest)}')
                    st.markdown('<div class="archive-detail">' + '<br>'.join(details) + '</div>', unsafe_allow_html=True)
                    for row in sorted(rows, key=lambda row: row.get("date", ""), reverse=True):
                        st.divider()
                        render_withdrawal_row(row)
            if is_closed_month(month):
                st.caption("Исторические итоги. Даты выплат показаны только для операций, сохранённых в данных.")
                if "Науки" in restaurants:
                    st.caption("Науки: за этот период данные отсутствуют.")
            if not shown:
                st.info("По этому ресторану за месяц данных нет.")


def checked_amount(text, allow_negative=False):
    cleaned = str(text).replace(" ", "").replace("\u00a0", "").replace("\u202f", "").replace("₽", "").strip()
    pattern = r"-?\d+" if allow_negative else r"\d+"
    if not re.fullmatch(pattern, cleaned):
        return None
    return int(cleaned)


def flash(message):
    st.session_state["feedback"] = message
    st.rerun()


def render_restaurant(data, months):
    page_heading("Работа с рестораном", "Утвердите прибыль или зарегистрируйте выплату партнёрам.", "УПРАВЛЕНИЕ ВЫПЛАТАМИ", kind="restaurant")
    c1, c2 = st.columns(2)
    with c1:
        month = select_month("restaurant_month", months, previous_month_key(date.today()))
    with c2:
        restaurant = select_restaurant("restaurant_name")
    st.caption("Месяц прибыли — за какой период заработаны деньги. Дата вывода указывается отдельно.")
    render_month_summary(data, month)
    profit, total, yadrovy, tarasenko, withdrawals = summary(data, restaurant, month)
    known = profit_is_recorded(data, restaurant, month)
    context = f"{month}_{restaurant}"
    fixed = is_fixed_accrual(restaurant, month)
    closed = is_closed_month(month)
    if closed:
        st.info("Исторический месяц закрыт. Прибыль распределена и выплачена полностью.")
    else:
        status = "Фиксированное начисление · 500 000 ₽ каждому партнёру" if fixed else "Прибыль утверждена" if known else "Прибыль ещё не утверждена · выплаты по умолчанию 50/50"
        st.markdown(f'<div class="{"closed-badge" if known else "pending-badge"}">{status}</div>', unsafe_allow_html=True)
    st.caption(f"Начислено: {money(profit) if known else 'не указано'} · Выведено: {money(total)}")

    if not closed:
        with st.container(key="editors"):
            profit_column, withdrawal_column = st.columns(2, gap="medium")
            with profit_column:
                if fixed:
                    with st.container(key="fixed_panel"):
                        form_heading("Фиксированное начисление", "coins")
                        st.markdown('<div class="preview-box"><div class="preview-title">Науки · фикс с октября 2026</div>'
                                    '<div class="preview-values"><span>Начислено за месяц <b>1 000 000 ₽</b></span>'
                                    '<span>Ядровы <b>500 000 ₽</b></span><span>Тарасенко <b>500 000 ₽</b></span></div></div>', unsafe_allow_html=True)
                        st.caption("Начисление автоматическое. Фактический вывод зарегистрируйте в блоке «Новый вывод» — он уменьшит остаток к выплате.")
                else:
                    with st.form(f"profit_form_{context}", enter_to_submit=False):
                        form_heading("Утверждённая прибыль", "approval")
                        st.caption(f"{restaurant} · {month_label(month)}")
                        profit_input = st.text_input("Чистая прибыль, ₽", value=format_input_money(profit) if known else "",
                                                     placeholder="Например, 1 000 000", key=f"profit_{context}")
                        saved = st.form_submit_button("Сохранить прибыль", type="primary", width="stretch")
                        if saved:
                            amount = checked_amount(profit_input, allow_negative=True)
                            if amount is None:
                                st.error("Введите целую сумму в рублях. Нулевую прибыль укажите числом 0.")
                            else:
                                set_profit(data, restaurant, month, amount)
                                save_data(data)
                                telegram_ok = notify_telegram_profit_saved(restaurant, month)
                                flash("Прибыль сохранена. " + ("Telegram-уведомление отправлено." if telegram_ok else "Telegram-уведомление не отправлено."))

            with withdrawal_column:
                with st.container(key="withdrawal_panel"):
                    form_heading("Новый вывод", "payout")
                    st.caption(f"{restaurant} · прибыль за {month_label(month).lower()}")
                    revision = st.session_state.get(f"withdrawal_revision_{context}", 0)
                    key = f"withdrawal_{context}_{revision}"
                    c3, c4 = st.columns(2)
                    with c3:
                        withdrawal_date = st.date_input("Дата фактического вывода", date.today(), format="DD.MM.YYYY", key=f"{key}_date")
                    with c4:
                        withdrawal_input = st.text_input("Сумма вывода, ₽", placeholder="Например, 200 000", key=f"{key}_amount")
                    amount = checked_amount(withdrawal_input)
                    use_proportions = st.checkbox("Разделить по пропорциям ресторана", value=True, key=f"{key}_proportions")
                    if use_proportions:
                        if fixed:
                            mode = "Фиксированное начисление"
                            distribution = {"Ядровы": 50, "Тарасенко": 50}
                            st.caption("Выплата из фиксированного начисления: Ядровы 50% · Тарасенко 50%.")
                        else:
                            mode = st.radio("Режим распределения", ["До утверждения прибыли", "После утверждения прибыли"],
                                            index=1 if known else 0, horizontal=True, key=f"{key}_mode")
                            distribution = {"Ядровы": 50, "Тарасенко": 50} if mode == "До утверждения прибыли" else get_distribution(restaurant, month)
                            st.caption("Предварительная выплата: Ядровы 50% · Тарасенко 50%." if mode == "До утверждения прибыли" else
                                       " · ".join(f"{name}: {percent:g}%" for name, percent in distribution.items()))
                    else:
                        partner = st.selectbox("Получатель всей суммы", ["Ядровы", "Тарасенко"], key=f"{key}_recipient")
                        mode = f"Вся сумма: {partner}"
                        distribution = {"Ядровы": 100 if partner == "Ядровы" else 0, "Тарасенко": 100 if partner == "Тарасенко" else 0}
                    c5, c6 = st.columns(2)
                    with c5:
                        without_notification = st.checkbox("Без уведомлений", key=f"{key}_silent", help="Вывод сохранится в учёте, но сообщение в Telegram не отправится.")
                    with c6:
                        show_comment = st.checkbox("Добавить комментарий", key=f"{key}_comment_on")
                    comment = st.text_input("Комментарий", placeholder="Например, оплата кредита", key=f"{key}_comment") if show_comment else ""
                    if amount is not None and amount > 0:
                        partners = distribution_to_partners(amount, distribution)
                        st.markdown(f'<div class="preview-box"><div class="preview-title">Будет зарегистрировано · {display_date(withdrawal_date.isoformat())}</div>'
                                    f'<div class="preview-values"><span>Ядровы <b>{money(partners["Ядровы"])}</b></span>'
                                    f'<span>Тарасенко <b>{money(partners["Тарасенко"])}</b></span></div></div>', unsafe_allow_html=True)
                        investment = amount * distribution.get("Возврат инвестиций", 0) / 100
                        if investment:
                            st.caption(f"В сумме Ядровых: {money(investment)} — возврат инвестиций.")
                        if known and (partners["Ядровы"] > yadrovy[2] or partners["Тарасенко"] > tarasenko[2]):
                            st.warning("Выплата превышает остаток одного из партнёров. После сохранения будет показан отрицательный остаток.")
                    elif withdrawal_input:
                        st.error("Введите положительную целую сумму в рублях, например 200 000.")
                    if st.button("Зарегистрировать вывод", type="primary", width="stretch", key=f"{key}_save", disabled=amount is None or amount <= 0):
                        data["withdrawals"].append({"date": withdrawal_date.isoformat(), "month": month, "restaurant": restaurant,
                                                    "amount": amount, "mode": mode, "distribution": distribution,
                                                    "notify": not without_notification, "comment": comment.strip()})
                        save_data(data)
                        telegram_ok = False if without_notification else notify_telegram_withdrawal(restaurant, month)
                        st.session_state[f"withdrawal_revision_{context}"] = revision + 1
                        message = "Вывод сохранён без уведомления." if without_notification else (
                            "Вывод сохранён. Telegram-уведомление отправлено." if telegram_ok else "Вывод сохранён. Telegram-уведомление не отправлено.")
                        flash(message)

    st.subheader("Баланс партнёров")
    render_partner_details(yadrovy, tarasenko, known)
    st.subheader("История выводов")
    st.caption(f"{month_label(month)} · {len(withdrawals)} операций · выведено {money(total)}")
    if not withdrawals:
        st.info("Исторический итог сохранён; отдельных операций в данных нет." if closed else "Выводов пока нет. Новая операция появится здесь после сохранения.")
    for index, row in sorted(enumerate(withdrawals), key=lambda pair: pair[1].get("date", ""), reverse=True):
        with st.container(border=True):
            render_withdrawal_row(row)
            if not closed:
                delete_key = f"delete_{context}_{index}"
                if st.button("Удалить…", key=delete_key):
                    st.session_state["pending_delete"] = delete_key
                if st.session_state.get("pending_delete") == delete_key:
                    st.warning(f'Удалить вывод {money(row["amount"])} от {display_date(row.get("date"))}? Остатки будут пересчитаны.')
                    c7, c8 = st.columns(2)
                    if c7.button("Подтвердить удаление", key=f"{delete_key}_confirm", type="primary"):
                        data["withdrawals"].pop(data["withdrawals"].index(row))
                        save_data(data)
                        st.session_state.pop("pending_delete", None)
                        flash("Вывод удалён. Остатки пересчитаны.")
                    if c8.button("Отмена", key=f"{delete_key}_cancel"):
                        st.session_state.pop("pending_delete", None)
                        st.rerun()
    with st.expander("Резервная копия данных"):
        st.caption("Все месяцы, рестораны и операции в одном файле JSON.")
        render_backup_button(data)


if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    with st.container(key="login"):
        st.markdown(f'<div class="login-intro"><div class="brand-mark">{ui_icon("khinkali")}</div>'
                    '<div class="page-title">Старик Хинкалыч</div>'
                    '<div class="page-description">Прибыль ресторанов. Выплаты партнёрам.<br>Всё в одном кабинете.</div></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            login = st.text_input("Логин", placeholder="Ваш логин")
            password = st.text_input("Пароль", type="password", placeholder="Ваш пароль")
            if st.form_submit_button("Войти в кабинет", type="primary", width="stretch"):
                if login in USERS and USERS[login]["password"] == password:
                    st.session_state.user = USERS[login]
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль. Проверьте введённые данные.")
        st.markdown('<div class="login-footer">Старик Хинкалыч · Dividends Space</div>', unsafe_allow_html=True)
    st.stop()

user = st.session_state.user
data = load_data()
months = all_months(data)
render_header(user)
if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))

if user["role"] == "admin":
    tab_main, tab_restaurant, tab_archive, tab_exit = st.tabs(["Главная", "Ресторан", "Архив", "Выйти"])
    with tab_main:
        render_overview(data, months, "main", "Обзор месяца")
    with tab_restaurant:
        render_restaurant(data, months)
else:
    tab_main, tab_archive, tab_exit = st.tabs(["Мой кабинет", "Архив", "Выйти"])
    with tab_main:
        render_overview(data, months, "partner", "Мой кабинет")
with tab_archive:
    render_archive(data, months)
with tab_exit:
    page_heading("Выход из кабинета", "Завершите сеанс на этом устройстве.")
    if st.button("Выйти из кабинета", type="primary"):
        st.session_state.clear()
        st.rerun()
