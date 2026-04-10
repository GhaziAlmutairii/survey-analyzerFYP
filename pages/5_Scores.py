# 5_Scores.py
# this page converts the Likert text responses to numbers (1-5)
# and shows mean scores per nationality as bar charts and a heatmap
# I also added a grouped chart so you can compare multiple metrics at once
# the heatmap was the most complex thing to build on the whole project

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.statistics import (
    filter_by_nationality,
    get_mean_score_by_nationality,
    get_satisfaction_comparison,
    get_difficulty_questions,
    get_agreement_questions,
    DIFFICULTY_SCALE,
    AGREEMENT_SCALE,
)
from utils.visualisations import grouped_mean_score_bar, mean_score_heatmap, PALETTE

st.set_page_config(page_title="Score Analysis", page_icon="📈", layout="wide")

if "df" not in st.session_state:
    st.warning("⚠️ Please upload your data on the **Home** page first.")
    st.stop()

df = st.session_state["df"]
all_countries = sorted(df["Country_Clean"].unique().tolist())
all_programmes = sorted(df["Programme_Category"].unique().tolist()) if "Programme_Category" in df.columns else []

diff_q = st.session_state.get("diff_q", get_difficulty_questions(df))
agr_q  = st.session_state.get("agr_q",  get_agreement_questions(df))
all_score_labels = list(agr_q.keys()) + list(diff_q.keys())

# ---------------------------------------------------------------------------
# Sidebar — combined filter + question selection
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🔍 Nationality Filter")
    selected_countries = st.multiselect(
        "Countries (blank = all)",
        options=all_countries,
        default=st.session_state.get("selected_countries", []),
        key="selected_countries",
    )

    st.markdown("### 🎓 Programme Filter")
    selected_programmes = st.multiselect(
        "Programmes (blank = all)",
        options=all_programmes,
        default=[],
        key="score_programmes",
    )

    st.markdown("---")
    st.markdown("### 📈 Single Metric")
    score_label = st.selectbox("Select metric", all_score_labels)

    st.markdown("### 📊 Multi-metric Grouped Chart")
    multi_metrics = st.multiselect(
        "Compare metrics",
        options=all_score_labels,
        default=all_score_labels[:3] if len(all_score_labels) >= 3 else all_score_labels,
    )

# ---------------------------------------------------------------------------
# Apply combined filter
# ---------------------------------------------------------------------------

filtered_df = filter_by_nationality(df, selected_countries)
if selected_programmes and "Programme_Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Programme_Category"].isin(selected_programmes)]

nat_label  = ", ".join(selected_countries)  if selected_countries  else "All Countries"
prog_label = ", ".join(selected_programmes) if selected_programmes else "All Programmes"

st.title("📈 Score Analysis")
st.caption(
    f"Showing: **{nat_label} · {prog_label}** · {len(filtered_df)} responses  \n"
    "Likert responses are converted to numeric scores (1–5) for mean comparison. "
    "Groups with fewer than 3 valid responses are excluded."
)

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Section 1: Single metric bar chart
# ---------------------------------------------------------------------------

st.markdown("## 🎯 Single Metric Mean Score")

if score_label in agr_q:
    score_col   = agr_q[score_label]
    score_scale = AGREEMENT_SCALE
    scale_desc  = "1 = Strongly Disagree → 5 = Strongly Agree"
else:
    score_col   = diff_q.get(score_label)
    score_scale = DIFFICULTY_SCALE
    scale_desc  = "1 = Not at all → 5 = Extremely"

if score_col and score_col in filtered_df.columns:
    mean_df = get_mean_score_by_nationality(filtered_df, score_col, score_scale)
    if mean_df.empty:
        st.info("Insufficient data (need ≥ 3 valid responses per group).")
    else:
        cm1, cm2 = st.columns([3, 1])
        with cm1:
            fig_m = px.bar(
                mean_df, x="Country", y="Mean Score", text="Mean Score",
                color="Country", color_discrete_sequence=PALETTE,
                title=f"Mean Score: {score_label}",
                labels={"Mean Score": scale_desc},
                range_y=[0, 5.5],
            )
            fig_m.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_m.update_layout(showlegend=False, height=400,
                                plot_bgcolor="white",
                                yaxis=dict(gridcolor="#e9ecef"))
            st.plotly_chart(fig_m, use_container_width=True)
        with cm2:
            st.markdown(f"**Scale**  \n{scale_desc}")
            st.dataframe(mean_df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download (CSV)", mean_df.to_csv(index=False).encode(),
                               f"mean_score_{score_label[:20]}.csv", "text/csv")
else:
    st.info("Question column not found in the uploaded data.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 2: Multi-metric grouped bar chart (Week 7)
# ---------------------------------------------------------------------------

st.markdown("## 📊 Multi-Metric Grouped Comparison")
st.caption("Compare several metrics across nationalities in one grouped chart.")

if not multi_metrics:
    st.info("Select metrics from the sidebar 'Compare metrics' list.")
else:
    score_rows = []
    for label in multi_metrics:
        if label in agr_q:
            col, scale = agr_q[label], AGREEMENT_SCALE
        else:
            col, scale = diff_q.get(label), DIFFICULTY_SCALE

        if col and col in filtered_df.columns:
            m = get_mean_score_by_nationality(filtered_df, col, scale, min_responses=2)
            for _, row in m.iterrows():
                score_rows.append({
                    "Country":     row["Country"],
                    "Metric":      label,
                    "Mean Score":  row["Mean Score"],
                })

    if score_rows:
        fig_grp = grouped_mean_score_bar(
            score_rows,
            title="Grouped Mean Scores by Nationality",
        )
        st.plotly_chart(fig_grp, use_container_width=True)

        # Download grouped data
        grp_df = pd.DataFrame(score_rows)
        st.download_button("⬇️ Download grouped scores (CSV)",
                           grp_df.to_csv(index=False).encode(),
                           "grouped_scores.csv", "text/csv")
    else:
        st.info("No data available for the selected metrics and filters.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 3: Full heatmap (Week 7)
# ---------------------------------------------------------------------------

st.markdown("## 🗺️ Agreement & Difficulty Heatmap")
st.caption(
    "All metrics simultaneously, colour-coded by mean score. "
    "Only groups with ≥ 3 responses are shown. "
    "Green = higher agreement or greater difficulty."
)

major = [c for c in sorted(filtered_df["Country_Clean"].unique())
         if (filtered_df["Country_Clean"] == c).sum() >= 3]

if not major:
    st.info("Need at least 3 responses per group to show heatmap.")
else:
    sat_df = get_satisfaction_comparison(filtered_df, countries=major)
    fig_h = mean_score_heatmap(sat_df)
    st.plotly_chart(fig_h, use_container_width=True)

    sat_clean = sat_df.drop(columns=["n"], errors="ignore")
    st.download_button(
        "⬇️ Download heatmap data (CSV)",
        sat_clean.reset_index().to_csv(index=False).encode(),
        "heatmap_scores.csv", "text/csv",
    )
