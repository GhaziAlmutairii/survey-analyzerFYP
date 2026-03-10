# 1_Nationality.py
# this page shows the nationality breakdown charts
# including a stacked Likert chart so you can compare all countries at once
# I think the stacked chart is the most useful one on the whole dashboard

import streamlit as st
from utils.data_processing import get_question_columns
from utils.statistics import (
    get_nationality_distribution,
    filter_by_nationality,
)
from utils.visualisations import (
    nationality_bar_chart,
    nationality_donut_chart,
    stacked_likert_bar,
)

st.set_page_config(page_title="Nationality Analysis", page_icon="🌍", layout="wide")

if "df" not in st.session_state:
    st.warning("⚠️ Please upload your data on the **Home** page first.")
    st.stop()

df = st.session_state["df"]
all_countries = sorted(df["Country_Clean"].unique().tolist())
question_columns = st.session_state.get("question_columns", get_question_columns(df))

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🔍 Filter")
    selected_countries = st.multiselect(
        "Select countries (blank = all)",
        options=all_countries,
        default=st.session_state.get("selected_countries", []),
        key="selected_countries",
    )
    st.markdown("---")
    st.markdown("### 📋 Select Question")
    st.caption("For the stacked Likert chart below")
    selected_q = st.selectbox("Question", question_columns, key="nat_question")
    show_pct = st.checkbox("Show as percentages (normalised)", value=True)

filtered_df = filter_by_nationality(df, selected_countries)
view_label = ", ".join(selected_countries) if selected_countries else "All Countries"

st.title("🌍 Nationality Analysis")
st.caption(f"Showing: **{view_label}** · {len(filtered_df)} responses")

if filtered_df.empty:
    st.warning("No data for this filter.")
    st.stop()

# ---------------------------------------------------------------------------
# Row 1: Bar + Donut
# ---------------------------------------------------------------------------

dist = get_nationality_distribution(filtered_df)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(nationality_bar_chart(dist), use_container_width=True)
with col2:
    st.plotly_chart(nationality_donut_chart(dist), use_container_width=True)

# Breakdown table
with st.expander("📋 View country breakdown table"):
    t = dist.copy()
    t["Percentage"] = t["Percentage"].astype(str) + "%"
    st.dataframe(t, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download (CSV)", dist.to_csv(index=False).encode(),
                       "nationality_distribution.csv", "text/csv")

st.markdown("---")

# ---------------------------------------------------------------------------
# Row 2: Stacked Likert bar (Week 7 key chart)
# ---------------------------------------------------------------------------

q_short = selected_q[:80] + "..." if len(selected_q) > 80 else selected_q
st.markdown(f"## 📊 Stacked Likert Distribution")
st.markdown(f"**Question:** *{q_short}*")
st.caption(
    "Stacked bars show what percentage of each nationality group chose each response. "
    "This enables direct visual comparison across all groups simultaneously."
)

fig_stack = stacked_likert_bar(
    filtered_df,
    selected_q,
    title=f"Response Distribution by Nationality — {view_label}",
    use_percentage=show_pct,
)
st.plotly_chart(fig_stack, use_container_width=True)
