# 2_Programmes.py
# shows the breakdown of students by MSc programme
# also lets you see which nationalities are in each programme

import streamlit as st
import plotly.express as px
from utils.statistics import (
    get_programme_distribution,
    filter_by_nationality,
    get_nationality_distribution,
)
from utils.visualisations import programme_donut_chart, nationality_bar_chart, PALETTE

st.set_page_config(page_title="Programme Analysis", page_icon="🎓", layout="wide")

if "df" not in st.session_state:
    st.warning("⚠️ Please upload your data on the **Home** page first.")
    st.stop()

df = st.session_state["df"]
all_countries = sorted(df["Country_Clean"].unique().tolist())

with st.sidebar:
    st.markdown("### 🔍 Filter")
    selected_countries = st.multiselect(
        "Select countries (blank = all)",
        options=all_countries,
        default=st.session_state.get("selected_countries", []),
        key="selected_countries",
    )

filtered_df = filter_by_nationality(df, selected_countries)
view_label = ", ".join(selected_countries) if selected_countries else "All Countries"

st.title("🎓 Programme Distribution")
st.caption(f"Showing: **{view_label}** · {len(filtered_df)} responses")

if filtered_df.empty:
    st.warning("No data for this filter.")
    st.stop()

prog_dist = get_programme_distribution(filtered_df)

if prog_dist.empty:
    st.info("No programme data available.")
    st.stop()

# ---------------------------------------------------------------------------
# Programme donut + bar side by side
# ---------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(programme_donut_chart(prog_dist), use_container_width=True)

with col2:
    fig_bar = px.bar(
        prog_dist,
        x="Programme",
        y="Count",
        text="Percentage",
        color="Programme",
        color_discrete_sequence=PALETTE,
        title="Students per Programme Category",
    )
    fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_bar.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

# Table
st.markdown("### Breakdown Table")
t = prog_dist.copy()
t["Percentage"] = t["Percentage"].astype(str) + "%"
st.dataframe(t, use_container_width=True, hide_index=True)
st.download_button("⬇️ Download (CSV)", prog_dist.to_csv(index=False).encode(),
                   "programme_distribution.csv", "text/csv")

st.markdown("---")

# ---------------------------------------------------------------------------
# Nationality split within each programme
# ---------------------------------------------------------------------------

st.markdown("## 🌍 Nationality Breakdown by Programme")
st.caption("Select a programme to see which nationalities are in it.")

programme_options = prog_dist["Programme"].tolist()
sel_prog = st.selectbox("Select programme", programme_options)

prog_df = filtered_df[filtered_df["Programme_Category"] == sel_prog]
prog_nat_dist = get_nationality_distribution(prog_df)

if not prog_nat_dist.empty:
    st.plotly_chart(
        nationality_bar_chart(prog_nat_dist, f"Nationalities in {sel_prog}"),
        use_container_width=True,
    )
else:
    st.info("No nationality data for this programme.")
