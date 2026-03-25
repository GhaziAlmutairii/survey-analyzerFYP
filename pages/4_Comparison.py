# 4_Comparison.py
# this page lets you compare two nationality groups side by side
# there are 4 tabs - bar charts, raw counts, percentages, and a stacked view
# the stacked tab is useful when you want to see multiple countries at once

import streamlit as st

from utils.data_processing import get_question_columns
from utils.statistics import (
    filter_by_nationality,
    get_response_counts_for_question,
    cross_tabulate,
    get_percentage_crosstab,
)
from utils.visualisations import stacked_likert_bar, PALETTE
import plotly.express as px

st.set_page_config(page_title="Comparison Tools", page_icon="⚖️", layout="wide")

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
    st.markdown("### 📋 Question")
    selected_q = st.selectbox("Select question", question_columns, key="comp_question")

    st.markdown("### ⚖️ Compare Groups")
    compare_a = st.selectbox("Group A", ["(All)"] + all_countries, index=0)
    compare_b = st.selectbox(
        "Group B", ["(All)"] + all_countries,
        index=2 if len(all_countries) > 1 else 0,
    )

    st.markdown("### 📊 Multi-group View")
    multi_countries = st.multiselect(
        "Countries for stacked chart",
        options=all_countries,
        default=all_countries[:5] if len(all_countries) >= 5 else all_countries,
    )
    show_pct = st.checkbox("Stacked chart: show %", value=True)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

st.title("⚖️ Nationality Comparison")

q_short = selected_q[:90] + "..." if len(selected_q) > 90 else selected_q
st.markdown(f"**Question:** *{q_short}*")

ga = None if compare_a == "(All)" else [compare_a]
gb = None if compare_b == "(All)" else [compare_b]
la = compare_a if compare_a != "(All)" else "All Countries"
lb = compare_b if compare_b != "(All)" else "All Countries"

ct_countries = (
    ([compare_a] if compare_a != "(All)" else []) +
    ([compare_b] if compare_b != "(All)" else [])
) or None

# ---------------------------------------------------------------------------
# Tab 1: Side-by-side bars  |  Tab 2: Count cross-tab  |  Tab 3: % cross-tab
# Tab 4: Stacked multi-group
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Bar Charts",
    "🔢 Count Cross-Tab",
    "📐 % Cross-Tab",
    "📈 Stacked (Multi-group)",
])

with tab1:
    da = get_response_counts_for_question(df, selected_q, ga)
    db = get_response_counts_for_question(df, selected_q, gb)
    ca, cb = st.columns(2)
    with ca:
        if da.empty:
            st.info(f"No data for {la}.")
        else:
            fa = px.bar(da, x="Response", y="Count", text="Percentage",
                        color_discrete_sequence=[PALETTE[0]], title=la)
            fa.update_traces(texttemplate="%{text}%", textposition="outside")
            fa.update_layout(showlegend=False, xaxis_tickangle=-15, height=370)
            st.plotly_chart(fa, use_container_width=True)
    with cb:
        if db.empty:
            st.info(f"No data for {lb}.")
        else:
            fb = px.bar(db, x="Response", y="Count", text="Percentage",
                        color_discrete_sequence=[PALETTE[1]], title=lb)
            fb.update_traces(texttemplate="%{text}%", textposition="outside")
            fb.update_layout(showlegend=False, xaxis_tickangle=-15, height=370)
            st.plotly_chart(fb, use_container_width=True)

with tab2:
    st.caption("Rows = response options · Columns = nationality groups · Values = counts")
    ct = cross_tabulate(df, selected_q, ct_countries)
    if ct.empty:
        st.info("No data.")
    else:
        st.dataframe(ct, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", ct.to_csv().encode(),
                           "crosstab_counts.csv", "text/csv")

with tab3:
    st.caption("Column percentages account for unequal group sizes — better for comparison.")
    pct = get_percentage_crosstab(df, selected_q, ct_countries)
    if pct.empty:
        st.info("No data.")
    else:
        st.dataframe(pct.style.format("{:.1f}%"), use_container_width=True)
        st.download_button("⬇️ Download (CSV)", pct.to_csv().encode(),
                           "crosstab_pct.csv", "text/csv")

with tab4:
    st.caption(
        "Stacked bars show ALL selected nationalities simultaneously. "
        "Each bar sums to 100% (when % mode is on), enabling direct comparison "
        "of response patterns regardless of group size."
    )
    if not multi_countries:
        st.info("Select at least one country from the sidebar 'Multi-group View' list.")
    else:
        fig_s = stacked_likert_bar(
            df, selected_q,
            countries=multi_countries,
            use_percentage=show_pct,
            title=f"{'Percentage' if show_pct else 'Count'} Distribution — {', '.join(multi_countries)}",
        )
        st.plotly_chart(fig_s, use_container_width=True)
