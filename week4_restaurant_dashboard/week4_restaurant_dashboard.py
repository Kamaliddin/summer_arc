import streamlit as st
import database as db
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time

db.init_db()
db.ensure_weekly_revenue()


if 'modal_table' not in st.session_state:
    st.session_state.modal_table = None
if 'modal_mode' not in st.session_state:
    st.session_state.modal_mode = None
if 'nav_page' not in st.session_state:
    st.session_state.nav_page = "🏠  MAIN"
if 'hide_rating_alert_main' not in st.session_state:
    st.session_state.hide_rating_alert_main = False
if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False
if 'light_mode' not in st.session_state:
    st.session_state.light_mode = False

try:
    params = st.experimental_get_query_params()
except Exception:
    params = {}

light_mode = st.session_state.light_mode

if light_mode:
    button_bg = '#ffffff'
    button_hover = '#e2d8c2'
    panel_bg = '#f7f4ef'
    panel_border = '#b9a17a'
    link_color = '#6b4f12'
    primary = '#8b6914'
    strong_text = '#211a15'
else:
    button_bg = '#8B6914'
    button_hover = '#D4A017'
    panel_bg = '#120a05'
    panel_border = '#8B6914'
    link_color = '#D4A017'
    primary = '#D4A017'
    strong_text = '#F8E3A9'

if params.get('hide_alert') == ['1']:
    st.session_state.hide_rating_alert_main = True
    clean_params = {k: v for k, v in params.items() if k != 'hide_alert'}
    st.experimental_set_query_params(**clean_params)
    st.experimental_rerun()
if 'page' in params:
    param_page = params['page'][0]
    if param_page == 'STAFF':
        st.session_state.nav_page = "👥  STAFF"
    elif param_page == 'REVENUE':
        st.session_state.nav_page = "📈  REVENUE"
    elif param_page == 'REPORTS':
        st.session_state.nav_page = "📋  REPORTS"
    elif param_page == 'SETTINGS':
        st.session_state.nav_page = "⚙️  SETTINGS"
    elif param_page == 'MAIN':
        st.session_state.nav_page = "🏠  MAIN"
if 'menu' in params:
    st.session_state.menu_open = params['menu'][0] == 'open'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

.stApp { background: #1a0f0a; font-family: 'Crimson Text', Georgia, serif; }
.block-container { max-width: 1100px !important; padding: 0 2rem 2rem 2rem !important; margin-top: 0 !important; }


header[data-testid="stHeader"] {
    display: none;
}

.tavern-header {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999;
    background: linear-gradient(180deg, #0d0700 0%, #1a0f0a 100%);
    border-bottom: 2px solid #8B6914;
    padding: 0.8rem 2rem;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 20px rgba(139,105,20,0.3);
}
.tavern-title { font-family: 'Cinzel', serif; font-size: 1.4rem; color: #D4A017; letter-spacing: 4px; text-transform: uppercase; text-shadow: 0 0 20px rgba(212,160,23,0.5); }
.tavern-subtitle { font-family: 'Crimson Text', serif; font-size: 0.85rem; color: #8B6914; letter-spacing: 2px; font-style: italic; }
.tavern-time { font-family: 'Cinzel', serif; font-size: 0.75rem; color: #6B4F12; letter-spacing: 2px; text-align: right; }

.main-content { margin-top: 85px; }

[data-testid="stSidebar"] { background: #120a05 !important; border-right: 1px solid #3D2B0A !important; }
section[data-testid="stSidebar"] { margin-top: 70px !important; }
.stRadio label { font-family: 'Cinzel', serif !important; font-size: 0.78rem !important; color: #8B6914 !important; letter-spacing: 1px !important; }

[data-testid="stMetric"] { background: #120a05; border: 1px solid #3D2B0A; border-top: 2px solid #8B6914; padding: 0.8rem 1rem; border-radius: 4px; }
[data-testid="stMetricLabel"] { font-family: 'Cinzel', serif !important; font-size: 0.62rem !important; color: #6B4F12 !important; letter-spacing: 2px !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-family: 'Cinzel', serif !important; font-size: 1rem !important; color: #D4A017 !important; }
[data-testid="stMetricDelta"] { font-size: 0.68rem !important; }

[data-testid="stAlert"] { max-width: 35%; font-size: 0.72rem; padding: 0.35rem 0.8rem; border-radius: 4px; }
.rating-alert { background: rgba(212,160,23,0.08); border: 1px solid #8B6914; border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: 1rem; }
.alert-title { font-family: 'Cinzel', serif; font-size: 0.85rem; color: #D4A017; margin-bottom: 0.5rem; }
.alert-text { font-family: 'Crimson Text', serif; color: #6B4F12; line-height: 1.55; margin-bottom: 0.85rem; }
.alert-actions { display: flex; gap: 0.5rem; align-items: center; }
.alert-button,
.alert-close { display: inline-flex; align-items: center; justify-content: center; padding: 0.45rem 0.8rem; border-radius: 6px; font-family: 'Cinzel', serif; font-size: 0.72rem; text-decoration: none; }
.alert-button { background: #8B6914; color: #fff; }
.alert-button:hover { background: #a37c2e; }
.alert-close { background: #3D2B0A; color: #D4A017; }
.alert-close:hover { background: #5a4114; }
.section-header { font-family: 'Cinzel', serif; font-size: 0.7rem; color: #6B4F12; letter-spacing: 4px; text-transform: uppercase; border-bottom: 1px solid #3D2B0A; padding-bottom: 6px; margin: 1.5rem 0 1rem 0; }

.table-visual { border-radius: 8px; padding: 0.7rem 0.4rem; margin-bottom: 4px; border: 2px solid; text-align: center; }
.table-empty-v { background: #1a1205; border-color: #8B6914; color: #D4A017; }
.table-occupied-v { background: #1f0a0a; border-color: #8B2020; color: #FF6B6B; }
.table-num { font-family: 'Cinzel', serif; font-size: 1.2rem; font-weight: 700; }
.table-lbl { font-size: 0.5rem; letter-spacing: 1px; margin-top: 3px; opacity: 0.7; font-family: 'Cinzel', serif; }
.table-who { font-size: 0.55rem; margin-top: 2px; color: #FF9999; font-style: italic; }

.modal-box { background: #1a0f0a; border: 2px solid #8B6914; border-radius: 8px; padding: 1.5rem; box-shadow: 0 0 30px rgba(139,105,20,0.4); margin: 1rem 0; }
.modal-title { font-family: 'Cinzel', serif; font-size: 0.85rem; color: #D4A017; letter-spacing: 3px; text-align: center; margin-bottom: 1rem; }

.emp-card { background: #120a05; border: 1px solid #3D2B0A; border-left: 3px solid #8B6914; padding: 0.7rem 1rem; border-radius: 4px; margin-bottom: 8px; }
.emp-name { font-family: 'Cinzel', serif; font-size: 0.78rem; color: #D4A017; margin-bottom: 4px; }
.emp-stats { font-size: 0.75rem; color: #8B6914; line-height: 1.6; }
element.style { transition: all 0.3s ease; color:rgb(134, 92, 0); font-weight:600; }
.progress-bg { background: #1a1205; border-radius: 2px; height: 3px; margin-top: 6px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #8B6914, #D4A017); border-radius: 2px; }

.float-order { position: fixed; right: 1.5rem; bottom: 5rem; z-index: 998; }

.stButton button { font-family: 'Cinzel', serif !important; font-size: 0.72rem !important; letter-spacing: 1px !important; background: transparent !important; border: 1px solid #8B6914 !important; color: #D4A017 !important; border-radius: 4px !important; }
.stButton button:hover { background: #8B6914 !important; color: #0d0700 !important; }

.tavern-footer { margin-top: 6rem; padding: 3rem 2rem; border-top: 1px solid #3D2B0A; background: linear-gradient(180deg, #1a0f0a, #0d0700); text-align: center; }
.footer-text { font-family: 'Cinzel', serif; font-size: 0.65rem; color: rgb(160, 120, 0); letter-spacing: 3px; text-transform: uppercase; }

.page-coming { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 50vh; color: #3D2B0A; font-family: 'Cinzel', serif; font-size: 0.75rem; letter-spacing: 4px; text-transform: uppercase; gap: 0.5rem; }

hr { border-color: #3D2B0A !important; margin: 1rem 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0700; }
::-webkit-scrollbar-thumb { background: #3D2B0A; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)
st.markdown(f"""
<style>
#nav-toggle {{ display: none; }}
.body-menu-button {{ position: fixed; top: 100px; left: 1rem; z-index: 1001; transition: transform 0.28s ease, top 0.28s ease; }}
.body-menu-button label.menu-trigger {{ display: inline-flex; align-items: center; justify-content: center; width: 42px; height: 42px; background: {button_bg}; color: {strong_text}; border: none; border-radius: 10px; cursor: pointer; font-size: 1.4rem; font-weight: 700; box-shadow: 0 6px 18px rgba(0,0,0,0.25); text-align: center; transition: background 0.28s ease, transform 0.28s ease, color 0.28s ease; }}
.body-menu-button label.menu-trigger::after {{ content: '☰'; }}
#nav-toggle:checked + .body-menu-button {{ top: calc(1rem - 3px); transform: translateX(calc(min(26vw, 340px) - 42px - 2rem)); }}
#nav-toggle:checked + .body-menu-button label.menu-trigger {{ background: {button_hover}; }}
#nav-toggle:checked + .body-menu-button label.menu-trigger::after {{ content: '✕'; }}
.body-menu-button label.menu-trigger:hover {{ background: {button_hover}; }}
.page-nav-overlay {{ position: fixed; top: 0; left: 0; z-index: 1000; width: 26vw; max-width: 340px; min-width: 240px; height: 100vh; background: {panel_bg}; border-right: 1px solid {panel_border}; box-shadow: 6px 0 24px rgba(0,0,0,0.25); padding: 1.4rem 1rem; transform: translateX(-105%); transition: transform 0.28s ease, opacity 0.28s ease; opacity: 0; pointer-events: none; }}
#nav-toggle:checked ~ .page-nav-overlay {{ transform: translateX(0); opacity: 1; pointer-events: auto; }}
.page-nav-overlay .menu-heading {{ font-family: 'Cinzel', serif; font-size: 0.95rem; color: {primary}; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1rem; }}
.page-nav-overlay .menu-item {{ display: block; padding: 0.85rem 0.95rem; margin-bottom: 0.5rem; color: {link_color}; text-decoration: none; border-radius: 8px; background: rgba(212,160,23,0.08); font-family: 'Cinzel', serif; }}
.page-nav-overlay .menu-item:hover {{ background: rgba(212,160,23,0.16); }}
</style>
<input type="checkbox" id="nav-toggle">
<div class="body-menu-button">
    <label for="nav-toggle" class="menu-trigger" title="Toggle sidebar menu"></label>
</div>
<div class="page-nav-overlay">
    <div class="menu-heading">STAFF NAVIGATION</div>
    <a class="menu-item" href="?page=MAIN">🏠 MAIN</a>
    <a class="menu-item" href="?page=REVENUE">📈 REVENUE</a>
    <a class="menu-item" href="?page=STAFF">👥 STAFF</a>
    <a class="menu-item" href="?page=REPORTS">📋 REPORTS</a>
    <a class="menu-item" href="?page=SETTINGS">⚙️ SETTINGS</a>
</div>
""", unsafe_allow_html=True)

# SHARED DATA (simulated today = Wednesday)
today_name = db.get_simulated_today_name()
sim_today = db.get_simulated_today()
today_date = sim_today.strftime('%d %B %Y')
today_time = datetime.now().strftime('%H:%M')
today_target = db.get_targets(today_name)
OWNER_TARGET = today_target['revenue_target']
CUSTOMER_TARGET = today_target['customers_target']
weekly_data = db.get_weekly_revenue()
WEEKLY_REVENUE = [r['revenue'] for r in weekly_data]
DAYS = [datetime.strptime(r['date'], '%Y-%m-%d').strftime('%a') for r in weekly_data]
WEEKLY_AVG = sum(WEEKLY_REVENUE)//len(WEEKLY_REVENUE) if WEEKLY_REVENUE else 0
employees = db.get_all_employees()
tables = db.get_all_tables()
DAY_TARGETS = []
for row in weekly_data:
    d = datetime.strptime(row['date'], '%Y-%m-%d').strftime('%A')
    t = db.get_targets(d)
    DAY_TARGETS.append(t['revenue_target'])
today_row = db.get_today_revenue_row()
today_rev = today_row['revenue']
today_cust = today_row['customers']
tuesday_str = (sim_today - timedelta(days=1)).isoformat()
tuesday_row = next((r for r in weekly_data if r['date'] == tuesday_str), None)
prev_rev = tuesday_row['revenue'] if tuesday_row else 0
prev_cust = tuesday_row['customers'] if tuesday_row else 0
LEVELS = [(0,1,"Apprentice"),(41,2,"Server"),(81,3,"Skilled"),(121,4,"Veteran"),(161,5,"Legend")]

def get_score(o, r): return (o*5)+(r*10)
def get_level(s):
    res=(1,"Apprentice")
    for t,l,n in LEVELS:
        if s>=t: res=(l,n)
    return res
def get_next(s):
    for t,l,n in LEVELS:
        if s<t: return t-s,n
    return 0,"Legend"

emp_stats_cache = {e['id']: db.get_employee_stats(e['id']) for e in employees}
low_rated = [e for e in employees if emp_stats_cache[e['id']]['rating'] and emp_stats_cache[e['id']]['rating'] <= 3.0]
overall_ratings = [emp_stats_cache[e['id']]['rating'] for e in employees if emp_stats_cache[e['id']]['rating']]
overall_average_rating = round(sum(overall_ratings)/len(overall_ratings),1) if overall_ratings else 0
rating_alerts = []
if low_rated:
    low_names = ', '.join([e['name'] for e in low_rated])
    rating_alerts.append(f"Waiter got rated below 3.0: {low_names}")
if overall_average_rating and overall_average_rating < 4.0:
    rating_alerts.append("Waiter rating dropped below 4.0")

# FIXED HEADER
st.markdown(f"""
<div class="tavern-header">
    <div>
        <div class="tavern-title">☕ Café Tashkent</div>
        <div class="tavern-subtitle">Est. 2024 · Tashkent, Uzbekistan</div>
    </div>
    <div class="tavern-time">{today_name.upper()}<br>{today_date}<br>{today_time}</div>
</div>
""", unsafe_allow_html=True)

# FLOATING ORDER BUTTON
st.markdown("""
<div class="float-order">
    <details style="background:#1a0f0a;border:2px solid #8B6914;border-radius:8px;padding:0.5rem 1rem;">
        <summary style="font-family:Cinzel,serif;font-size:0.72rem;color:#D4A017;letter-spacing:2px;list-style:none;cursor:pointer;">
            🛵 ORDER HOME
        </summary>
        <div style="margin-top:0.8rem;font-family:Crimson Text,serif;font-size:0.82rem;color:#8B6914;line-height:2;">
            <a href="tel:+998901234567" style="color:#8B6914;text-decoration:none;">+998 90 123 45 67</a><br>
            📍 Chilonzor 12, Tashkent<br>
            ⏰ 10:00 — 22:00
        </div>
    </details>
</div>
""", unsafe_allow_html=True)

# NAVIGATION
st.sidebar.markdown("""<div style='padding:0.5rem 0 1rem;font-family:Cinzel,serif;font-size:0.62rem;color:#3D2B0A;letter-spacing:4px;'>⚜ NAVIGATION ⚜</div>""", unsafe_allow_html=True)
st.sidebar.checkbox("Light mode", key="light_mode")
page = st.sidebar.radio("", ["🏠  MAIN","📈  REVENUE","👥  STAFF","📋  REPORTS","⚙️  SETTINGS"], label_visibility="collapsed", key="nav_page")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# MAIN PAGE
if page == "🏠  MAIN":
    if rating_alerts and not st.session_state.hide_rating_alert_main:
        alert_lines = ''.join(f"<div>{msg}</div>" for msg in rating_alerts)
        st.markdown(f"""
        <div class="rating-alert">
            <div class="alert-title">⚠ Waiter rating warning</div>
            <div class="alert-text">{alert_lines}</div>
            <div class="alert-actions">
                <a class="alert-button" href="?page=STAFF">Rating biased</a>
                <a class="alert-close" href="?page=MAIN&hide_alert=1">Hide alert</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    low = [e['name'] for e in employees if emp_stats_cache[e['id']]['rating']>0 and emp_stats_cache[e['id']]['rating']<4.0]
    if low: st.warning(f"⚠️ Low rating today: {', '.join(low)}")

    progress_pct = min(int(today_rev/OWNER_TARGET*100),100) if OWNER_TARGET else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Revenue Today", f"{today_rev:,}", f"{today_rev-prev_rev:+,}")
    c2.metric("Daily Target", f"{OWNER_TARGET:,}", f"{progress_pct}% reached", delta_color="off")
    c3.metric("Guests Today", today_cust, f"{today_cust-prev_cust:+}")
    c4.metric("Weekly Average", f"{WEEKLY_AVG:,}")

    # MODAL
    if st.session_state.modal_table is not None:
        t_id = st.session_state.modal_table
        mode = st.session_state.modal_mode
        st.markdown(f"""<div class="modal-box"><div class="modal-title">{"⚔ SEAT GUEST — TABLE "+str(t_id) if mode=="book" else "💰 CLOSE TABLE — TABLE "+str(t_id)}</div></div>""", unsafe_allow_html=True)
        if mode == 'book':
            emp_names = {e['name']: e['id'] for e in employees}
            chosen = st.selectbox("Assign to:", list(emp_names.keys()), key="modal_emp")
            col1,col2 = st.columns(2)
            if col1.button("⚔ Confirm Seating"):
                db.book_table(t_id, emp_names[chosen])
                st.session_state.modal_table = None
                st.session_state.modal_mode = None
                st.rerun()
            if col2.button("✕ Cancel"):
                st.session_state.modal_table = None
                st.session_state.modal_mode = None
                st.rerun()
        elif mode == 'pay':
            rating = st.slider("Rate service", 1.0, 5.0, 4.5, 0.5, key="modal_rating")
            revenue = st.number_input("Table total (UZS)", step=10000, value=0, key="modal_revenue")
            col1,col2 = st.columns(2)
            if col1.button("💰 Confirm Payment"):
                db.clear_table(t_id, rating, revenue)
                st.session_state.modal_table = None
                st.session_state.modal_mode = None
                st.rerun()
            if col2.button("✕ Cancel"):
                st.session_state.modal_table = None
                st.session_state.modal_mode = None
                st.rerun()
        st.divider()

    # TABLES
    st.markdown('<div class="section-header">⚜ HALL MAP</div>', unsafe_allow_html=True)
    occupied = sum(1 for t in tables if t['status']=='occupied')
    sc1,sc2,sc3 = st.columns(3)
    sc1.markdown(f"<span style='color:#D4A017;font-size:0.78rem;font-family:Cinzel,serif;'>🟡 EMPTY: {20-occupied}</span>", unsafe_allow_html=True)
    sc2.markdown(f"<span style='color:#FF6B6B;font-size:0.78rem;font-family:Cinzel,serif;'>🔴 OCCUPIED: {occupied}</span>", unsafe_allow_html=True)
    sc3.markdown(f"<span style='color:#6B4F12;font-size:0.78rem;font-family:Cinzel,serif;'>⚜ TOTAL: 20</span>", unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    rows_of_tables = [tables[i:i+5] for i in range(0,20,5)]
    for row in rows_of_tables:
        cols = st.columns(5)
        for col, table in zip(cols, row):
            t_id = table['id']
            is_occ = table['status']=='occupied'
            waiter = table.get('employee_name','') or ''
            with col:
                if is_occ:
                    st.markdown(f"""<div class="table-visual table-occupied-v"><div class="table-num">{t_id:02d}</div><div class="table-lbl">OCCUPIED</div><div class="table-who">{waiter}</div></div>""", unsafe_allow_html=True)
                    if st.button("💰 Pay", key=f"p_{t_id}", use_container_width=True):
                        st.session_state.modal_table = t_id
                        st.session_state.modal_mode = 'pay'
                        st.rerun()
                else:
                    st.markdown(f"""<div class="table-visual table-empty-v"><div class="table-num">{t_id:02d}</div><div class="table-lbl">EMPTY</div></div>""", unsafe_allow_html=True)
                    if st.button("+ Seat", key=f"b_{t_id}", use_container_width=True):
                        st.session_state.modal_table = t_id
                        st.session_state.modal_mode = 'book'
                        st.rerun()

    # CHART
    st.markdown('<div class="section-header">⚜ REVENUE SCROLL</div>', unsafe_allow_html=True)
    if WEEKLY_REVENUE:
        fig, ax = plt.subplots(figsize=(10,3))
        fig.patch.set_facecolor('#120a05')
        ax.set_facecolor('#120a05')
        colors = ["#D4A017" if i<len(DAY_TARGETS) and WEEKLY_REVENUE[i]>=DAY_TARGETS[i] else "#8B2020" for i in range(len(WEEKLY_REVENUE))]
        ax.bar(DAYS, WEEKLY_REVENUE, color=colors, width=0.6, alpha=0.85, zorder=2)
        for i,(d,target) in enumerate(zip(DAYS,DAY_TARGETS)):
            ax.hlines(target, i-0.35, i+0.35, colors='#C084FC', linewidth=2, linestyle='--', zorder=3)
        ax.axhline(WEEKLY_AVG, color='#3D2B0A', linestyle=':', linewidth=1)
        avg_p=mpatches.Patch(color='#3D2B0A',label=f'Avg {WEEKLY_AVG:,}')
        tgt_p=mpatches.Patch(color='#C084FC',label='Daily Target')
        gold_p=mpatches.Patch(color='#D4A017',label='Above Target')
        red_p=mpatches.Patch(color='#8B2020',label='Below Target')
        ax.legend(handles=[avg_p,tgt_p,gold_p,red_p],facecolor='#120a05',labelcolor='#8B6914',edgecolor='#3D2B0A',fontsize=7)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,p: f'{int(x/1000)}K'))
        ax.tick_params(colors='#6B4F12',labelsize=7)
        ax.yaxis.set_tick_params(labelcolor='#6B4F12')
        ax.xaxis.set_tick_params(labelcolor='#6B4F12')
        for spine in ax.spines.values(): spine.set_edgecolor('#3D2B0A')
        st.pyplot(fig, transparent=False)

    # STAFF
    st.markdown('<div class="section-header">⚜ STAFF ON DUTY</div>', unsafe_allow_html=True)
    emp_cols = st.columns(len(employees))
    for col,emp in zip(emp_cols,employees):
        stats=emp_stats_cache[emp['id']]
        score=get_score(stats['orders'],stats['rating'])
        level_num,level_name=get_level(score)
        _,next_name=get_next(score)
        stars="★"*level_num+"☆"*(5-level_num)
        progress=min(score/161*100,100)
        col.markdown(f"""<div class="emp-card"><div class="emp-name">{emp['name']}</div><div class="emp-stats">{stars}<br>Lv.{level_num} · {level_name}<br>🛎 {stats['orders']} orders<br>⭐ {stats['rating']}/5.0<br>💰 {stats['earnings']:,} UZS</div><div class="progress-bg"><div class="progress-fill" style="width:{progress:.0f}%"></div></div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="tavern-footer"><div style="color:#3D2B0A;font-size:1rem;">⚜ ─────────────────── ⚜</div><div class="footer-text">Café Tashkent · Est. 2024</div><div class="footer-text" style="margin-top: 1rem; color: rgb(134, 92, 0);">Good food · Good service · Good company</div><div style="color:#3D2B0A;font-size:1rem;margin-top:1rem;">⚜ ─────────────────── ⚜</div></div>""", unsafe_allow_html=True)

elif page == "📈  REVENUE":
    st.markdown('<div class="section-header">⚜ REVENUE CHRONICLES</div>', unsafe_allow_html=True)
    st.markdown("""<div class="page-coming"><div style="font-size:2rem;opacity:0.3;">📜</div><div>REVENUE CHRONICLES</div><div style="font-size:0.58rem;margin-top:0.5rem;">HISTORICAL · DATE SEARCH · YEAR OVER YEAR</div><div style="font-size:0.58rem;margin-top:0.3rem;color:#2a1a05;">COMING TUESDAY</div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="tavern-footer"><div style="color:#3D2B0A;">⚜ ─────────────────── ⚜</div></div>""", unsafe_allow_html=True)

elif page == "👥  STAFF":
    st.markdown('<div class="section-header">⚜ THE GUILD</div>', unsafe_allow_html=True)
    if rating_alerts:
        alert_lines = ''.join(f"<div>{msg}</div>" for msg in rating_alerts)
        st.markdown(f"""
        <div class="modal-box">
            <div class="modal-title">⚠ Stored rating alerts</div>
            <div style="font-size:0.82rem;line-height:1.6;color:#D4A017;">{alert_lines}</div>
        </div>
        """, unsafe_allow_html=True)
    for emp in employees:
        stats=emp_stats_cache[emp['id']]
        score=get_score(stats['orders'],stats['rating'])
        level_num,level_name=get_level(score)
        left,next_name=get_next(score)
        stars="★"*level_num+"☆"*(5-level_num)
        progress=min(score/161*100,100)
        st.markdown(f"""<div class="emp-card" style="padding:1rem 1.5rem;margin-bottom:12px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><div class="emp-name" style="font-size:0.95rem;">{emp['name']} · {emp['role']}</div><div style="font-size:0.8rem;color:#8B6914;margin-top:2px;">{stars} &nbsp; Lv.{level_num} {level_name} &nbsp;·&nbsp; {left} pts to {next_name}</div></div><div style="text-align:right;font-family:Cinzel,serif;font-size:0.72rem;color:#6B4F12;">🛎 {stats['orders']} orders &nbsp; ⭐ {stats['rating']}/5.0 &nbsp; 💰 {stats['earnings']:,} UZS</div></div><div class="progress-bg" style="margin-top:10px;"><div class="progress-fill" style="width:{progress:.0f}%"></div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="tavern-footer"><div style="color:#3D2B0A;">⚜ ─────────────────── ⚜</div><div class="footer-text">THE GUILD · Staff Records</div><div style="color:#3D2B0A;margin-top:1rem;">⚜ ─────────────────── ⚜</div></div>""", unsafe_allow_html=True)

elif page == "📋  REPORTS":
    st.markdown('<div class="section-header">⚜ THE LEDGER</div>', unsafe_allow_html=True)
    st.markdown("""<div class="page-coming"><div style="font-size:2rem;opacity:0.3;">📖</div><div>THE LEDGER</div><div style="font-size:0.58rem;margin-top:0.5rem;">WEEKLY SUMMARY · BEST STAFF · PEAK HOURS</div><div style="font-size:0.58rem;margin-top:0.3rem;color:#2a1a05;">COMING THURSDAY</div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="tavern-footer"><div style="color:#3D2B0A;">⚜ ─────────────────── ⚜</div></div>""", unsafe_allow_html=True)

elif page == "⚙️  SETTINGS":
    st.markdown('<div class="section-header">⚜ STEWARD\'S QUARTERS</div>', unsafe_allow_html=True)
    days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for day in days:
        target=get_targets(day)
        with st.expander(f"{day} · {target['revenue_target']:,} UZS · {target['customers_target']} guests"):
            c1,c2=st.columns(2)
            new_rev=c1.number_input("Revenue target",value=target['revenue_target'],step=50000,key=f"r_{day}")
            new_cust=c2.number_input("Guest target",value=target['customers_target'],step=5,key=f"c_{day}")
            if st.button(f"Save {day}",key=f"s_{day}"):
                db.update_target(day,new_rev,new_cust)
                ph=st.empty(); ph.success("✓ Saved to the ledger"); time.sleep(2); ph.empty(); st.rerun()
    st.divider()
    st.markdown('<div class="section-header">⚜ TODAY\'S RECORD</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    t_rev=c1.number_input("Today's revenue",step=10000,value=today_rev)
    t_cust=c2.number_input("Today's guests",step=1,value=today_cust)
    if st.button("Record Today"):
        db.update_today_revenue(t_rev,t_cust)
        ph=st.empty(); ph.success("✓ Recorded"); time.sleep(2); ph.empty(); st.rerun()
    st.divider()
    st.markdown('<div class="section-header">⚜ SPECIAL DAY OVERRIDE</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    s_rev=c1.number_input(f"{today_name} override",value=OWNER_TARGET,step=50000)
    s_cust=c2.number_input(f"{today_name} guests",value=CUSTOMER_TARGET,step=5)
    if st.button("Override Today Only"):
        db.update_target(today_name,s_rev,s_cust)
        ph=st.empty(); ph.success(f"✓ {today_name} overridden"); time.sleep(2); ph.empty(); st.rerun()
    st.markdown("""<div class="tavern-footer"><div style="color:#3D2B0A;">⚜ ─────────────────── ⚜</div><div class="footer-text">Steward's Quarters</div><div style="color:#3D2B0A;margin-top:1rem;">⚜ ─────────────────── ⚜</div></div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)