# International Student Survey Analysis Dashboard

**Student:** Ghazi Almutairi | **Module:** KV6013 Final Year Project | **Supervisor:** I Watson

A web-based interactive dashboard for analysing and comparing international student survey data from Northumbria University, built with Python and Streamlit.

---

## Project Structure

```
project/
├── app.py                          # Home page - file upload, KPI overview, charts
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── pages/
│   ├── 1_Nationality.py            # Bar + donut + stacked Likert comparison
│   ├── 2_Programmes.py             # Programme distribution + nationality split
│   ├── 3_Questions.py              # Question explorer + combined filter
│   ├── 4_Comparison.py             # 4-tab comparison (bars, cross-tabs, stacked)
│   ├── 5_Scores.py                 # Mean scores, grouped bar, heatmap
│   └── 6_About.py                  # Help, glossary, onboarding guide
│
├── utils/
│   ├── __init__.py
│   ├── data_processing.py          # CSV/Excel loading, cleaning, validation
│   ├── statistics.py               # All statistical computation functions
│   └── visualisations.py           # Reusable Plotly chart builders (7 chart types)
│
└── tests/
    ├── __init__.py
    ├── test_data_processing.py     # 23 unit tests for data cleaning
    ├── test_statistics.py          # 21 unit tests for statistical functions
    ├── test_week5.py               # 34 unit tests for scoring and cross-tabs
    └── test_integration.py         # 23 integration tests on real CSV data
```

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the dashboard

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

### 3. Upload your data

Upload the `Assimilation into British University academic culture.csv` file using the sidebar on the Home page.

---

## How to Run Tests

```bash
python -m pytest tests/ -v
```

Expected output: **101 passed** in under 4 seconds.

---

## Features

| Feature | Description | Page |
|---------|-------------|------|
| **File Upload** | Accepts `.csv` and `.xlsx` exports from Microsoft Forms | Home |
| **Data Cleaning** | Automatically standardises country names (removes emojis, fixes case/whitespace) | Home |
| **Nationality Distribution** | Bar chart + donut chart of response counts | Home, Nationality |
| **Stacked Likert Chart** | Compare all nationality groups' responses to any question | Nationality |
| **Programme Analysis** | Donut + bar charts of MSc programme breakdown | Programmes |
| **Question Explorer** | Select any survey question, view distribution as vertical or horizontal bar | Questions |
| **Combined Filter** | Filter by nationality AND programme simultaneously | Questions, Scores |
| **Cross-tabulation** | Count and percentage cross-tabs comparing nationality groups | Comparison |
| **Mean Score Analysis** | Likert-to-numeric (1–5) mean scores per nationality | Scores |
| **Grouped Bar Chart** | Compare multiple metrics across nationalities side by side | Scores |
| **Heatmap** | Colour-coded grid of all metrics across all nationality groups | Scores |
| **CSV Export** | Download any table or chart data as CSV | All pages |
| **Help & Glossary** | Step-by-step guide and term definitions | About |
| **Accessibility** | Uses colour-blind safe palette (ColorBrewer Dark2) | All pages |
| **Data Privacy** | No data stored server-side — session only, GDPR compliant | All pages |

---

## Key Data Cleaning Rules

The survey CSV contains inconsistent country name formatting. The following are handled automatically:

| Raw value | Cleaned value |
|-----------|---------------|
| `Nigeria 🇳🇬` | Nigeria |
| `NIGERIA` | Nigeria |
| `INDIA` | India |
| `india` | India |
| `India ` (trailing space) | India |
| ` Nigeria ` (leading space) | Nigeria |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | ≥1.28.0 | Web framework and UI components |
| pandas | ≥2.0.0 | Data loading and manipulation |
| plotly | ≥5.18.0 | Interactive charts |
| openpyxl | ≥3.1.0 | Excel file support |
| pytest | ≥7.0.0 | Unit and integration testing |
