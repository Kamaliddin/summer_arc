import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Restaurant Dashboard", layout="wide")

# ── LEVEL SYSTEM ───────────────────────────────────
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

# ── FAKE DATA ──────────────────────────────────────
METRICS = {
    "customers_today": 47,
    "customers_yesterday": 32,
    "loyal_customers": 12,
    "revenue_today": 850000,
    "revenue_yesterday": 640000,
}

EMPLOYEES = [
    {"name": "Akbar",  "orders": 28, "rating": 4.8},
    {"name": "Leila",  "orders": 18, "rating": 4.2},
    {"name": "Jamil",  "orders": 12, "rating": 3.7},
    {"name": "Nodira", "orders": 35, "rating": 4.9},
]

WEEKLY_REVENUE = [520000, 640000, 480000, 710000, 390000, 640000, 850000]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"]

# ── HEADER ─────────────────────────────────────────
st.title("🏪 RESTAURANT DASHBOARD — Café Tashkent")
st.divider()

# ── ALERTS ─────────────────────────────────────────
alerts = [f"{e['name']}: rating {e['rating']} below 4.0"
          for e in EMPLOYEES if e["rating"] < 4.0]
if alerts:
    st.error("⚠️ OWNER ALERT")
    for a in alerts:
        st.warning(a)
    st.divider()

# ── METRIC CARDS ───────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Customers Today", METRICS["customers_today"],
            f"+{METRICS['customers_today'] - METRICS['customers_yesterday']}")
col2.metric("Loyal Customers", METRICS["loyal_customers"])
col3.metric("Revenue Today", f"{METRICS['revenue_today']:,} UZS",
            f"+{METRICS['revenue_today'] - METRICS['revenue_yesterday']:,}")

st.divider()

# ── REVENUE CHART ───────────────────────────────────
st.subheader("📊 Weekly Revenue")
avg = sum(WEEKLY_REVENUE) / len(WEEKLY_REVENUE)
colors = ["#00ff88" if r >= avg else "#ff4444" for r in WEEKLY_REVENUE]

fig, ax = plt.subplots(figsize=(10, 3))
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.bar(DAYS, WEEKLY_REVENUE, color=colors)
ax.axhline(avg, color='gray', linestyle='--', linewidth=1, label='Average')
ax.tick_params(colors='white')
ax.yaxis.set_tick_params(labelcolor='white')
ax.xaxis.set_tick_params(labelcolor='white')
ax.legend(facecolor='none', labelcolor='white', edgecolor='none')
for spine in ax.spines.values():
    spine.set_edgecolor('#333')
st.pyplot(fig, transparent=True)

st.divider()

# ── EMPLOYEE CARDS ──────────────────────────────────
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