# 6_About.py
# I added this page after usability testing because participants
# said there wasnt enough help text in the app (heuristic H10)
# it has a step by step guide, explanation of the filters,
# data format info, and a glossary of terms

import streamlit as st

st.set_page_config(page_title="Help & About", page_icon="ℹ️", layout="wide")

st.title("ℹ️ Help & About")
st.caption("KV6013 Final Year Project · Northumbria University · Ghazi Almutairi")

st.markdown("---")

# getting started guide
st.markdown("## 🚀 Getting Started")

with st.expander("Step-by-step guide to using this dashboard", expanded=True):
    st.markdown("""
**Step 1 — Upload your data**
- Go to the **Home** page (top of the left sidebar navigation)
- Click **Browse files** and select your Microsoft Forms CSV or Excel export
- The dashboard will load and display an overview automatically

**Step 2 — Explore nationality distribution**
- Click **Nationality** in the sidebar
- Use the bar chart and donut chart to see the response breakdown
- Select a survey question from the sidebar to see a **stacked Likert chart** comparing all nationalities

**Step 3 — Explore individual questions**
- Click **Questions** in the sidebar
- Choose any question from the dropdown
- Filter by **nationality** and/or **programme** using the sidebar filters
- Toggle between **vertical** and **horizontal** bar chart views

**Step 4 — Compare groups**
- Click **Comparison** in the sidebar
- Select **Group A** and **Group B** from the sidebar
- The **Bar Charts** tab shows side-by-side comparisons
- The **% Cross-Tab** tab normalises for group size differences
- The **Stacked** tab shows all selected nationalities simultaneously

**Step 5 — View mean scores & heatmap**
- Click **Scores** in the sidebar
- Select a metric (agreement or difficulty question) for the bar chart
- Select multiple metrics for the **grouped comparison chart**
- Scroll down to see the full **heatmap** of all metrics
""")

st.markdown("---")

# combined filter guide - this was the main usability issue (P1)
st.markdown("## 🔍 Using the Combined Filter")
st.info(
    "**Tip:** The **Questions** and **Scores** pages both support filtering by "
    "**Nationality AND Programme simultaneously**. Use both sidebar filters together "
    "to, for example, see only Nigerian Computer Science students' responses."
)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
**Nationality filter**
- Available on all pages
- Select one or more countries
- Leave blank to include all nationalities
""")
with col2:
    st.markdown("""
**Programme filter** *(Questions & Scores pages only)*
- Filter by MSc programme category
- Categories: Computer Science, Data Science, Information Science / Data Analytics
- Leave blank to include all programmes
""")

st.markdown("---")

# data format info
st.markdown("## 📁 Data Format Requirements")

with st.expander("Required file format and columns"):
    st.markdown("""
The dashboard expects a **Microsoft Forms survey export** in CSV or Excel format.

**Required column:**
- `What is your home country? *`

**Automatically handled:**
- Country names with emoji flags (e.g. `Nigeria 🇳🇬` → `Nigeria`)
- Mixed case country names (e.g. `INDIA`, `india` → `India`)
- Leading/trailing whitespace in country names
- Blank test submissions (automatically removed)

**Programme categorisation:**
The system automatically maps free-text programme names into three categories:

| Programme Category | Examples of matched text |
|--------------------|--------------------------|
| Computer Science | "MSc Computer Science", "Advanced Computer Science" |
| Data Science | "MSc Data Science", "Data Science with Advanced Practice" |
| Information Science / Data Analytics | "Information Science (Data Analytics)", "Info Science Data Analytics" |
""")

st.markdown("---")

# glossary
st.markdown("## 📖 Glossary")

with st.expander("Terms used in this dashboard"):
    st.markdown("""
| Term | Meaning |
|------|---------|
| **Likert scale** | A response scale where participants choose from ordered options (e.g. Not at all → Extremely) |
| **Mean score** | Average numeric value after converting Likert text to numbers (1–5 scale) |
| **Cross-tabulation** | A table showing response counts for two variables simultaneously |
| **Stacked bar** | A chart where each bar is divided into segments showing response proportions |
| **SUS** | System Usability Scale — a standard 10-item questionnaire for measuring usability |
| **Heatmap** | A colour-coded grid where darker colours indicate higher values |
| **Combined filter** | Filtering data by both nationality and programme at the same time |
""")

st.markdown("---")

# about section
st.markdown("## 🎓 About This Project")
st.markdown("""
This dashboard was developed as the implementation component of a Final Year Project (KV6013) at **Northumbria University**.

**Project title:** Evaluating Web-Based Solutions for Interactive Analysis and Visualisation of International Student Survey Data  
**Student:** Ghazi Almutairi  
**Supervisor:** I Watson  
**Academic Year:** 2025–2026

**Technology stack:**
- Python 3.13 · Streamlit ≥ 1.28 · Plotly ≥ 5.18 · Pandas ≥ 2.0
- 101 automated unit and integration tests

**Data privacy:**  
All survey data is processed entirely within your browser session. No data is transmitted to any external server. The application is GDPR compliant.

**Colour accessibility:**  
All charts use the **ColorBrewer Dark2** palette, which is tested for colour-blind accessibility (Brewer, 2003).
""")
