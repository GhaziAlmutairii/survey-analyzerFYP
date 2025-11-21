"\"\"\"Streamlit Application for International Student Survey Analysis\"\"\""

import os
from io import BytesIO
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from data_processor import SurveyDataProcessor
from calculations import (
    calculate_country_counts,
    calculate_percentage_summary,
    calculate_nationality_percentage,
)
from comparisons import (
    compare_side_by_side,
    calculate_difference_between_countries,
    generate_comparison_report,
)


SAMPLE_FILE = "Assimilation into British University academic culture.csv"

st.set_page_config(
    page_title="International Student Survey Explorer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 International Student Survey Explorer")
st.caption(
    "Upload the Excel/CSV survey file or use the built-in sample dataset to explore "
    "international student perceptions, satisfaction, and challenges."
)


def process_data(uploaded_file: Optional[BytesIO], use_sample: bool) -> Optional[SurveyDataProcessor]:
    """Load and process data via SurveyDataProcessor."""
    processor = SurveyDataProcessor()
    success = False

    if uploaded_file is not None:
        uploaded_file.seek(0)
        success = processor.process_pipeline(uploaded_file=uploaded_file)
    elif use_sample and os.path.exists(SAMPLE_FILE):
        success = processor.process_pipeline(file_path=SAMPLE_FILE)

    if success:
        return processor
    return None


def categorize_questions(columns: List[str]) -> Dict[str, List[str]]:
    """Group survey columns into friendly categories."""
    categories: Dict[str, List[str]] = {
        "Importance Factors": [],
        "Agreement & Inclusion": [],
        "Difficulty Ratings": [],
        "English Proficiency": [],
        "Programme & Background": [],
        "Other": [],
    }

    for col in columns:
        col_lower = col.lower()
        if "important" in col_lower:
            categories["Importance Factors"].append(col)
        elif "agree" in col_lower or "included" in col_lower:
            categories["Agreement & Inclusion"].append(col)
        elif "difficult" in col_lower:
            categories["Difficulty Ratings"].append(col)
        elif "english language ability" in col_lower:
            categories["English Proficiency"].append(col)
        elif any(keyword in col_lower for keyword in ["programme", "institution", "language"]):
            categories["Programme & Background"].append(col)
        else:
            categories["Other"].append(col)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


with st.sidebar:
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader("Upload Excel or CSV", type=["csv", "xlsx"])
    use_sample = st.checkbox(
        "Use built-in sample dataset",
        value=uploaded_file is None and os.path.exists(SAMPLE_FILE),
        help="Loads the provided survey file if no upload is supplied.",
    )

    navigation = st.radio(
        "Quick Navigation",
        ["Overview", "Question Explorer", "Comparisons", "Downloads"],
        help="Use tabs in the main area or jump directly using this selector.",
    )

    st.markdown("---")
    st.caption("Controls below appear once data is loaded.")


processor: Optional[SurveyDataProcessor] = None
if uploaded_file or (use_sample and os.path.exists(SAMPLE_FILE)):
    processor = process_data(uploaded_file, use_sample)
    if processor is None:
        st.error("Unable to load the dataset. Please verify the file format and try again.")
else:
    st.info(
        "Upload the survey Excel/CSV file or toggle the sample dataset from the sidebar "
        "to begin exploring the data."
    )


if processor and processor.cleaned_data is not None:
    summary = processor.get_data_summary()
    countries = summary.get("countries", [])
    question_columns = processor.get_question_columns()
    categorized_questions = categorize_questions(question_columns)

    with st.sidebar:
        st.subheader("🔍 Filters")
        selected_countries = st.multiselect(
            "Countries",
            countries,
            default=countries[:5] if len(countries) > 5 else countries,
            help="Filter analyses to specific nationalities.",
        )

        if categorized_questions:
            category = st.selectbox("Question Category", list(categorized_questions.keys()))
            question_options = categorized_questions.get(category, question_columns)
        else:
            category = "All Questions"
            question_options = question_columns

        selected_question = st.selectbox(
            "Survey Question",
            question_options,
            help="Select the survey question to analyze in the tabs below.",
        )

        value_options = sorted(
            [str(v) for v in processor.cleaned_data[selected_question].dropna().unique() if str(v).strip()]
        )
        selected_value = st.selectbox(
            "Response Value (for comparisons)",
            value_options if value_options else [],
            index=0 if value_options else None,
        )

    # Tabs for multi-page layout
    tab_titles = ["Overview", "Question Explorer", "Comparisons", "Downloads"]
    tabs = st.tabs(tab_titles)
    tab_map = dict(zip(tab_titles, tabs))

    # Overview Tab -----------------------------------------------------------
    with tab_map["Overview"]:
        st.subheader("Dataset Overview")
        metrics = st.columns(4)
        metrics[0].metric("Total Responses", summary["cleaned_rows"])
        metrics[1].metric("Nationalities", len(countries))
        metrics[2].metric("Questions Available", len(question_columns))
        metrics[3].metric(
            "Rows Removed During Cleaning",
            summary["cleaning_stats"]["rows_removed"] if summary["cleaning_stats"] else 0,
        )

        country_counts = calculate_country_counts(processor.cleaned_data, processor.country_column)
        if not country_counts.empty:
            st.plotly_chart(
                px.bar(
                    country_counts,
                    x="Nationality",
                    y="Count",
                    text="Count",
                    title="Responses by Nationality",
                    color="Nationality",
                ),
                use_container_width=True,
            )
            st.dataframe(country_counts, use_container_width=True, hide_index=True)

        st.markdown("### Data Preview")
        st.dataframe(processor.cleaned_data.head(20), use_container_width=True)

    # Question Explorer Tab --------------------------------------------------
    with tab_map["Question Explorer"]:
        st.subheader("Question Explorer")
        st.caption("Explore percentage breakdowns for the selected question across nationalities.")

        percentage_summary = calculate_percentage_summary(
            processor,
            selected_question,
            countries=selected_countries if selected_countries else None,
        )

        if percentage_summary:
            by_country = percentage_summary["by_country"]
            overall = percentage_summary["overall"]

            if by_country is not None and not by_country.empty:
                st.plotly_chart(
                    px.bar(
                        by_country,
                        x="Nationality",
                        y="Percentage",
                        color="Value",
                        barmode="stack",
                        title="Percentage Breakdown by Nationality",
                        text="Percentage",
                    ),
                    use_container_width=True,
                )
                st.dataframe(by_country, use_container_width=True, hide_index=True)
            else:
                st.info("No responses available for the selected filters.")

            if overall is not None and not overall.empty:
                st.markdown("#### Overall Distribution")
                st.dataframe(overall, use_container_width=True, hide_index=True)

    # Comparisons Tab --------------------------------------------------------
    with tab_map["Comparisons"]:
        st.subheader("Country Comparisons")
        st.caption("Compare responses between selected countries.")

        if selected_countries and len(selected_countries) >= 1:
            comparison_table = compare_side_by_side(
                processor,
                selected_question,
                selected_countries,
                show_counts=True,
            )
            if not comparison_table.empty:
                st.dataframe(comparison_table, use_container_width=True)

            if selected_value and len(selected_countries) >= 2:
                c1, c2 = selected_countries[:2]
                diff_stats = calculate_difference_between_countries(
                    processor,
                    selected_question,
                    c1,
                    c2,
                    selected_value,
                )
                if diff_stats:
                    st.markdown(
                        f"**Difference for '{selected_value}':** "
                        f"{diff_stats['country1']} {diff_stats['country1_percentage']}% vs "
                        f"{diff_stats['country2']} {diff_stats['country2_percentage']}% "
                        f"(Δ {diff_stats['difference']:.2f}%)"
                    )

                report = generate_comparison_report(
                    processor,
                    selected_question,
                    selected_countries[: min(3, len(selected_countries))],
                )
                with st.expander("View Narrative Report"):
                    st.text(report)
        else:
            st.info("Select at least one country from the sidebar to view comparisons.")

    # Downloads Tab ----------------------------------------------------------
    with tab_map["Downloads"]:
        st.subheader("Downloads")
        st.caption("Export cleaned or filtered datasets for offline analysis.")

        filtered_df = (
            processor.cleaned_data[
                processor.cleaned_data[processor.country_column].isin(selected_countries)
            ].copy()
            if selected_countries
            else processor.cleaned_data
        )

        st.download_button(
            label="Download Cleaned Dataset (CSV)",
            data=convert_df_to_csv(processor.cleaned_data),
            file_name="cleaned_survey_data.csv",
            mime="text/csv",
        )

        st.download_button(
            label="Download Filtered Dataset (CSV)",
            data=convert_df_to_csv(filtered_df),
            file_name="filtered_survey_data.csv",
            mime="text/csv",
        )

        if percentage_summary and percentage_summary.get("by_country") is not None:
            st.download_button(
                label="Download Current Analysis (CSV)",
                data=convert_df_to_csv(percentage_summary["by_country"]),
                file_name="analysis_by_country.csv",
                mime="text/csv",
            )
else:
    st.stop()


