# 3_Questions.py
# lets you pick any survey question and see the response distribution
# I added a combined nationality + programme filter here after usability testing
# because participants wanted to filter by both at the same time
# you can also switch between a vertical and horizontal bar chart

import streamlit as st
import plotly.express as px

from utils.data_processing import get_question_columns
from utils.statistics import (
    get_response_counts_for_question,
    filter_by_nationality,
)
from utils.visualisations import response_horizontal_bar, PALETTE

st.set_page_config(page_title="Question Explorer", page_icon="📋", layout="wide")

if "df" not in st.session_state:
    st.warning("⚠️ Please upload your data on the **Home** page first.")
    st.stop()

df = st.session_state["df"]
all_countries = sorted(df["Country_Clean"].unique().tolist())
all_programmes = sorted(df["Programme_Category"].unique().tolist()) if "Programme_Category" in df.columns else []
question_columns = st.session_state.get("question_columns", get_question_columns(df))

# ---------------------------------------------------------------------------
# Sidebar — combined filter (Week 8)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🔍 Filter by Nationality")
    selected_countries = st.multiselect(
        "Countries (blank = all)",
        options=all_countries,
        default=st.session_state.get("selected_countries", []),
        key="selected_countries",
    )

    st.markdown("### 🎓 Filter by Programme")
    selected_programmes = st.multiselect(
        "Programmes (blank = all)",
        options=all_programmes,
        default=[],
        key="selected_programmes",
    )

    st.markdown("---")
    st.markdown("### 📋 Question")
    selected_q = st.selectbox("Select question", question_columns, key="q_question")
    chart_type = st.radio("Chart type", ["Vertical bars", "Horizontal bars"], index=0)

# ---------------------------------------------------------------------------
# Apply combined filter (nationality + programme)
# ---------------------------------------------------------------------------

filtered_df = filter_by_nationality(df, selected_countries)

if selected_programmes and "Programme_Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Programme_Category"].isin(selected_programmes)]

nat_label  = ", ".join(selected_countries)  if selected_countries  else "All Countries"
prog_label = ", ".join(selected_programmes) if selected_programmes else "All Programmes"
view_label = f"{nat_label} · {prog_label}"

st.title("📋 Question Explorer")
st.caption(f"Showing: **{view_label}** · {len(filtered_df)} responses")

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Response distribution
# ---------------------------------------------------------------------------

q_short = selected_q[:90] + "..." if len(selected_q) > 90 else selected_q
st.markdown(f"### *{q_short}*")

resp_data = get_response_counts_for_question(filtered_df, selected_q)

if resp_data.empty:
    st.info("No valid responses for this question in the current filter.")
else:
    col_chart, col_table = st.columns([3, 1])

    with col_chart:
        if chart_type == "Vertical bars":
            fig = px.bar(
                resp_data, x="Response", y="Count", text="Percentage",
                color="Response", color_discrete_sequence=PALETTE,
                title=f"Response Distribution — {view_label}",
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(showlegend=False, xaxis_tickangle=-20, height=400)
        else:
            fig = response_horizontal_bar(
                resp_data, f"Response Distribution — {view_label}"
            )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("**Response Counts**")
        t = resp_data.copy()
        t["Percentage"] = t["Percentage"].astype(str) + "%"
        st.dataframe(t, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download (CSV)",
            resp_data.to_csv(index=False).encode(),
            "question_responses.csv",
            "text/csv",
        )
