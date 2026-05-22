import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from database import init_db, get_targets, get_weekly_revenue, update_target, update_today
from datetime import datetime
import time

init_db()
# STYLE
st.markdown("""
<style>
    /* Page max width and layout */
    .st-emotion-cache-1w723zb {
        max-width: 1200px;
        padding: 1.5rem 1rem;
    }
    
    /* Smaller professional fonts throughout */
    [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
    
    /* Headers scale down */
    .main h1 {
        font-size: 1.5rem !important;
        font-weight: 600;
    }
    
    .main h2 {
        font-size: 1.1rem !important;
        font-weight: 500;
    }
    
    .main h3 {
        font-size: 0.95rem !important;
    }
    
    /* Metric cards smaller and tighter */
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.7rem !important;
    }
    
    /* Alert width 30% and smaller font */
    .st-af {
        max-width: 30%;
        font-size: 1rem;
        padding: 0.4rem 0.8rem;
    }
    
    /* Employee cards tighter */
    [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        margin: 0.2rem;
        line-height: 1.4;
    }
    
    /* Dividers thinner */
    hr {
        margin: 0.5rem 0;
    }
    
    /* Sidebar smaller */
    [data-testid="stSidebar"] {
        font-size: 0.85rem;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        font-size: 0.82rem !important;
    }
    
    /* Buttons smaller */
    .stButton button {
        font-size: 0.78rem;
        padding: 0.3rem 0.8rem;
    }

    /* Number inputs */
    .stNumberInput label {
        font-size: 0.78rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ── PAGE NAVIGATION ─────────────────────────────────
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📊 Dashboard", "⚙️ Settings"])

# ── SHARED DATA ─────────────────────────────────────
weekly_data = get_weekly_revenue()
WEEKLY_REVENUE = [row['revenue'] for row in weekly_data]
DAYS = [row['date'][-5:] for row in weekly_data]
WEEKLY_AVG = sum(WEEKLY_REVENUE) // len(WEEKLY_REVENUE)

today_name = datetime.now().strftime('%A')
today_target = get_targets(today_name)
OWNER_TARGET = today_target['revenue_target']
CUSTOMER_TARGET = today_target['customers_target']

DAY_TARGETS = []
for row in weekly_data:
    date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
    day_name = date_obj.strftime('%A')
    target = get_targets(day_name)
    DAY_TARGETS.append(target['revenue_target'])

EMPLOYEES = [
    {"name": "Akbar",  "orders": 28, "rating": 4.8},
    {"name": "Leila",  "orders": 18, "rating": 4.2},
    {"name": "Jamil",  "orders": 12, "rating": 3.7},
    {"name": "Nodira", "orders": 35, "rating": 4.9},
]

LEVELS = [
    (0,   1, "Newcomer"),
    (41,  2, "Server"),
    (81,  3, "Skilled"),
    (121, 4, "Veteran"),
    (161, 5, "Legend"),
]

def get_score(orders, rating):
    return (orders * 5) + (rating * 10)

def get_level(score):
    result = (1, "Newcomer")
    for threshold, level, name in LEVELS:
        if score >= threshold:
            result = (level, name)
    return result

def get_next_level_info(score):
    for threshold, level, name in LEVELS:
        if score < threshold:
            return threshold - score, name
    return 0, "Legend"

def get_active_status(score):
    if score >= 120:
        return "🟢 Active", 0
    return "🟡 Needs more", 120 - score

# ════════════════════════════════════════════════════
if page == "📊 Dashboard":

    st.title("🏪 RESTAURANT DASHBOARD — Café Tashkent")
    st.divider()

    # ── ALERTS — single combined block, small ───────
    low_rating = [e['name'] for e in EMPLOYEES if e["rating"] < 4.0]
    critical = [e['name'] for e in EMPLOYEES if e["rating"] <= 3.0]

    if low_rating or critical:
        alert_lines = []
        if critical:
            alert_lines.append(f"🔴 Critical rating (≤3.0): {', '.join(critical)}")
        if low_rating:
            alert_lines.append(f"🟡 Below 4.0: {', '.join(low_rating)}")
        st.warning("⚠️ " + " | ".join(alert_lines))
        st.divider()

    # ── METRIC CARDS ───────────────────────────────
    metrics = weekly_data[-1] if weekly_data else {}
    today_rev = metrics.get('revenue', 0)
    today_cust = metrics.get('customers', 0)
    prev = weekly_data[-2] if len(weekly_data) > 1 else {}
    prev_rev = prev.get('revenue', 0)
    prev_cust = prev.get('customers', 0)

    remaining = OWNER_TARGET - today_rev
    progress_text = f"{remaining:,} UZS to target" if remaining > 0 else "✅ Target reached"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue Today",
                f"{today_rev:,} UZS",
                f"{today_rev - prev_rev:+,} vs yesterday")
    col2.metric("Today's Target",
                f"{OWNER_TARGET:,} UZS",
                progress_text,
                delta_color="off")
    col3.metric("Customers Today",
                today_cust,
                f"{today_cust - prev_cust:+} vs yesterday")
    col4.metric("Weekly Average",
                f"{WEEKLY_AVG:,} UZS")

    st.divider()

    # ── REVENUE CHART ───────────────────────────────
    st.subheader("📊 Weekly Revenue")

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    colors = []
    for i, rev in enumerate(WEEKLY_REVENUE):
        if i < len(DAY_TARGETS):
            colors.append("#00ff88" if rev >= DAY_TARGETS[i] else "#ff4444")
        else:
            colors.append("#ff4444")

    ax.bar(DAYS, WEEKLY_REVENUE, color=colors, zorder=2)

    for i, (day, target) in enumerate(zip(DAYS, DAY_TARGETS)):
        ax.plot(i, target, marker='D', color='#4fc3f7',
                markersize=5, zorder=3)
        ax.hlines(target, i - 0.4, i + 0.4,
                  colors='#4fc3f7', linewidth=1.5,
                  linestyle='--', zorder=3)

    ax.axhline(WEEKLY_AVG, color='gray', linestyle='--',
               linewidth=1, zorder=1)

    avg_patch = mpatches.Patch(color='gray', label=f'Weekly Avg: {WEEKLY_AVG:,}')
    target_patch = mpatches.Patch(color='#4fc3f7', label='Daily Target')
    green_patch = mpatches.Patch(color='#00ff88', label='Above target')
    red_patch = mpatches.Patch(color='#ff4444', label='Below target')
    ax.legend(handles=[avg_patch, target_patch, green_patch, red_patch],
              facecolor='none',fontsize=8, labelcolor='white', edgecolor='none')

    ax.tick_params(colors='white')
    ax.yaxis.set_tick_params(labelcolor='white')
    ax.xaxis.set_tick_params(labelcolor='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')

    st.pyplot(fig, transparent=True)
    st.divider()

    # ── EMPLOYEE CARDS ──────────────────────────────
    st.subheader("👥 Employee Roster")

    for emp in EMPLOYEES:
        score = get_score(emp["orders"], emp["rating"])
        level_num, level_name = get_level(score)
        left_to_next, next_name = get_next_level_info(score)
        status_text, left_to_active = get_active_status(score)
        stars = "⭐" * level_num + "☆" * (5 - level_num)

        with st.container():
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            col1.markdown(f"""
**{emp['name']}**
{stars}
**Lv.{level_num} — {level_name}**
*({left_to_next} pts → {next_name})*
            """)
            col2.markdown(f"""
**Rating:** {emp['rating']}/5.0
**Score:** {score}
            """)
            col3.markdown(f"""
**Orders today**
🛎️ {emp['orders']}
            """)
            col4.markdown(f"""
**Status**
{status_text}
{"*("+str(left_to_active)+" left)*" if left_to_active > 0 else "✅ Target hit"}
            """)
            st.divider()

# ════════════════════════════════════════════════════
elif page == "⚙️ Settings":

    st.title("⚙️ Owner Settings")

    # ── WEEKLY TARGETS ──────────────────────────────
    st.subheader("📅 Weekly Default Targets")

    days = ['Monday','Tuesday','Wednesday',
            'Thursday','Friday','Saturday','Sunday']

    for day in days:
        target = get_targets(day)
        with st.expander(f"{day} — {target['revenue_target']:,} UZS | {target['customers_target']} customers"):
            col1, col2 = st.columns(2)
            new_rev = col1.number_input(
                "Revenue target (UZS)",
                value=target['revenue_target'],
                step=50000,
                key=f"rev_{day}"
            )
            new_cust = col2.number_input(
                "Customers target",
                value=target['customers_target'],
                step=5,
                key=f"cust_{day}"
            )
            if st.button(f"💾 Save {day}", key=f"btn_{day}"):
                update_target(day, new_rev, new_cust)
                placeholder = st.empty()
                placeholder.success(f"✅ {day} saved!")
                time.sleep(2)
                placeholder.empty()
                st.rerun()

    st.divider()

    # ── SPECIAL DAY OVERRIDE ────────────────────────
    st.subheader("🗓️ Special Day Override")
    st.caption("Override today's target only — does not change weekly defaults.")

    col1, col2 = st.columns(2)
    special_rev = col1.number_input(
        f"Today's ({today_name}) revenue target",
        value=OWNER_TARGET,
        step=50000,
        key="special_rev"
    )
    special_cust = col2.number_input(
        f"Today's ({today_name}) customer target",
        value=CUSTOMER_TARGET,
        step=5,
        key="special_cust"
    )
    if st.button("💾 Override Today Only"):
        update_target(today_name, special_rev, special_cust)
        placeholder = st.empty()
        placeholder.success(f"✅ Today ({today_name}) overridden to {special_rev:,} UZS")
        time.sleep(2)
        placeholder.empty()
        st.rerun()

    st.divider()

    # ── TODAY'S ACTUAL DATA ─────────────────────────
    st.subheader("📥 Enter Today's Numbers")

    col1, col2 = st.columns(2)
    today_rev_input = col1.number_input(
        "Today's actual revenue (UZS)", step=10000, value=0)
    today_cust_input = col2.number_input(
        "Today's actual customers", step=1, value=0)

    if st.button("💾 Save Today's Data"):
        update_today(today_rev_input, today_cust_input)
        placeholder = st.empty()
        placeholder.success("✅ Today's data saved!")
        time.sleep(2)
        placeholder.empty()
        st.rerun()