# app.py - this is the main home page of the dashboard
# it handles file upload and shows the basic nationality overview
# all pages share the same uploaded data through session_state
#
# to run: streamlit run app.py
#
# I updated this after usability testing to add:
# - a loading spinner when the file uploads
# - a re-upload button so you don't have to refresh the page
# - tooltips on the filters to make them clearer
# - a help expander at the top

import streamlit as st

from utils.data_processing import load_survey_data, get_question_columns
from utils.statistics import (
    add_programme_category,
    get_nationality_distribution,
    get_summary_statistics,
    filter_by_nationality,
    get_difficulty_questions,
    get_agreement_questions,
)
from utils.visualisations import nationality_bar_chart, nationality_donut_chart

st.set_page_config(
    page_title="International Student Survey Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { min-width: 280px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🎓 Survey Analysis")
    st.markdown("*Northumbria University · KV6013*")
    st.markdown("---")
    st.markdown("### 📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel (MS Forms export)",
        type=["csv", "xlsx", "xls"],
        help="Export your Microsoft Forms survey and upload the CSV or Excel file here.",
    )

    # Week 9 fix: re-upload button (P2 issue)
    if "df" in st.session_state:
        if st.button("🔄 Clear data & re-upload", use_container_width=True):
            for key in ["df", "_file", "diff_q", "agr_q", "question_columns"]:
                st.session_state.pop(key, None)
            st.rerun()

    st.markdown("---")
    st.markdown("### 🗂️ Pages")
    st.markdown("""
- **🏠 Home** — Overview & upload  
- **🌍 Nationality** — Distribution charts  
- **🎓 Programmes** — Programme breakdown  
- **📋 Questions** — Question explorer  
- **⚖️ Comparison** — Cross-tabulation  
- **📈 Scores** — Heatmap & mean scores  
- **ℹ️ About** — Help & documentation
""")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🎓 International Student Survey Analysis")
st.markdown(
    "**Northumbria University · KV6013 Final Year Project**  \n"
    "Student: Ghazi Almutairi · Supervisor: I Watson"
)

# Week 9 improvement: in-app help expander (H10 fix)
with st.expander("ℹ️ How to use this dashboard"):
    st.markdown("""
1. **Upload** your MS Forms CSV using the sidebar
2. **Explore** the nationality distribution on this page
3. Use **Nationality** page for stacked Likert comparisons
4. Use **Questions** page to explore any individual question
5. Use **Comparison** page for side-by-side and cross-tab views
6. Use **Scores** page for numeric mean score analysis and heatmap
7. See the **About** page for full documentation and glossary
""")

# ---------------------------------------------------------------------------
# File upload & session management
# ---------------------------------------------------------------------------

if uploaded_file is not None:
    # Week 9 fix: loading spinner (P3 issue)
    with st.spinner("Loading and cleaning survey data..."):
        try:
            df_raw = load_survey_data(uploaded_file)
        except ValueError as e:
            st.error(f"❌ {e}")
            st.stop()
        df = add_programme_category(df_raw)

    # store in session state so all pages can access the data
    st.session_state["df"] = df
    st.session_state["_file"] = uploaded_file.name
    st.session_state["diff_q"] = get_difficulty_questions(df)
    st.session_state["agr_q"] = get_agreement_questions(df)
    st.session_state["question_columns"] = get_question_columns(df)

    st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df)} valid responses across {df['Country_Clean'].nunique()} nationalities.")

elif "df" not in st.session_state:
    st.info("👈 **Upload your survey CSV or Excel file** using the sidebar to begin.")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**🌍 Nationality**  \nBar charts and donut charts of respondent home countries.")
    c2.markdown("**📋 Question Explorer**  \nInteractive response distributions for any survey question.")
    c3.markdown("**📈 Score Analysis**  \nLikert → numeric scores and heatmaps across nationalities.")
    st.markdown("---")
    st.markdown("**Need help?** Navigate to the **ℹ️ About** page for a full guide.")
    st.stop()

df = st.session_state["df"]
all_countries = sorted(df["Country_Clean"].unique().tolist())

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🔍 Nationality Filter")
    selected_countries = st.multiselect(
        "Select countries (blank = all)",
        options=all_countries,
        default=st.session_state.get("selected_countries", []),
        key="selected_countries",
        # Week 9 fix: tooltip explaining combined filter (P1 issue)
        help="Filter all charts to selected nationalities. "
             "Combine with the Programme filter on the Questions and Scores pages "
             "to drill down further.",
    )

# ---------------------------------------------------------------------------
# Apply filter
# ---------------------------------------------------------------------------

filtered_df = filter_by_nationality(df, selected_countries)
view_label = ", ".join(selected_countries) if selected_countries else "All Countries"

# ---------------------------------------------------------------------------
# Section 1: Summary KPIs
# ---------------------------------------------------------------------------

st.markdown(f"## 📊 Overview — {view_label}")
summary = get_summary_statistics(filtered_df)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Responses",       summary["total_responses"])
m2.metric("Countries Represented", summary["countries_represented"])
m3.metric("Largest Group",         summary["top_country"])
m4.metric("Largest Group %",       f"{summary['top_country_pct']}%")

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 2: Dual chart — bar + donut
# ---------------------------------------------------------------------------

st.markdown("## 🌍 Nationality Distribution")

dist = get_nationality_distribution(filtered_df)
col_bar, col_donut = st.columns(2)

with col_bar:
    st.plotly_chart(
        nationality_bar_chart(dist, f"Responses by Country — {view_label}"),
        use_container_width=True,
    )

with col_donut:
    st.plotly_chart(
        nationality_donut_chart(dist),
        use_container_width=True,
    )

st.download_button(
    "⬇️ Download nationality table (CSV)",
    dist.to_csv(index=False).encode(),
    "nationality_distribution.csv",
    "text/csv",
)

st.markdown("---")
st.caption(
    "ℹ️ Data processed in-session only — not stored externally. "
    "ColorBrewer Dark2 palette (colour-blind safe). "
    "For help, see the **ℹ️ About** page."
)
