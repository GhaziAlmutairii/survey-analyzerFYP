"""
test_statistics.py
-------------------
Unit tests for the statistics module.

Tests cover:
  - Nationality distribution calculation
  - Filtering by nationality
  - Likert response distribution
  - Summary statistics
"""

import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.statistics import (
    get_nationality_distribution,
    filter_by_nationality,
    get_response_counts_for_question,
    get_summary_statistics,
)


# ---------------------------------------------------------------------------
# Fixture: a minimal cleaned DataFrame
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df():
    """Representative sample of cleaned survey data."""
    return pd.DataFrame({
        "Country_Clean": [
            "Nigeria", "Nigeria", "Nigeria",
            "India", "India",
            "Sri Lanka",
        ],
        "English_Reading": [
            "Excellent", "Good", "Excellent",
            "Good", "Average",
            "Average",
        ],
    })


# ---------------------------------------------------------------------------
# Tests for get_nationality_distribution
# ---------------------------------------------------------------------------

class TestGetNationalityDistribution:

    def test_returns_dataframe(self, sample_df):
        result = get_nationality_distribution(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_correct_columns(self, sample_df):
        result = get_nationality_distribution(sample_df)
        assert list(result.columns) == ["Country", "Count", "Percentage"]

    def test_correct_counts(self, sample_df):
        result = get_nationality_distribution(sample_df)
        nigeria_row = result[result["Country"] == "Nigeria"].iloc[0]
        assert nigeria_row["Count"] == 3

    def test_percentages_sum_to_100(self, sample_df):
        result = get_nationality_distribution(sample_df)
        assert abs(result["Percentage"].sum() - 100.0) < 0.1

    def test_nigeria_percentage(self, sample_df):
        result = get_nationality_distribution(sample_df)
        nigeria_row = result[result["Country"] == "Nigeria"].iloc[0]
        # 3 out of 6 = 50%
        assert nigeria_row["Percentage"] == 50.0

    def test_sorted_by_count_descending(self, sample_df):
        result = get_nationality_distribution(sample_df)
        assert result.iloc[0]["Country"] == "Nigeria"
        assert result.iloc[1]["Country"] == "India"


# ---------------------------------------------------------------------------
# Tests for filter_by_nationality
# ---------------------------------------------------------------------------

class TestFilterByNationality:

    def test_empty_list_returns_all(self, sample_df):
        result = filter_by_nationality(sample_df, [])
        assert len(result) == len(sample_df)

    def test_filter_single_country(self, sample_df):
        result = filter_by_nationality(sample_df, ["Nigeria"])
        assert len(result) == 3
        assert all(result["Country_Clean"] == "Nigeria")

    def test_filter_multiple_countries(self, sample_df):
        result = filter_by_nationality(sample_df, ["Nigeria", "India"])
        assert len(result) == 5

    def test_filter_nonexistent_country_returns_empty(self, sample_df):
        result = filter_by_nationality(sample_df, ["Germany"])
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Tests for get_response_counts_for_question
# ---------------------------------------------------------------------------

class TestGetResponseCountsForQuestion:

    def test_returns_dataframe(self, sample_df):
        result = get_response_counts_for_question(sample_df, "English_Reading")
        assert isinstance(result, pd.DataFrame)

    def test_has_correct_columns(self, sample_df):
        result = get_response_counts_for_question(sample_df, "English_Reading")
        assert "Response" in result.columns
        assert "Count" in result.columns
        assert "Percentage" in result.columns

    def test_counts_correct(self, sample_df):
        result = get_response_counts_for_question(sample_df, "English_Reading")
        excellent = result[result["Response"] == "Excellent"]["Count"].values[0]
        assert excellent == 2

    def test_filtered_by_nationality(self, sample_df):
        # Only Nigeria has 3 rows: Excellent, Good, Excellent
        result = get_response_counts_for_question(
            sample_df, "English_Reading", selected_countries=["Nigeria"]
        )
        excellent = result[result["Response"] == "Excellent"]["Count"].values[0]
        assert excellent == 2

    def test_empty_df_returns_empty_result(self):
        empty_df = pd.DataFrame({
            "Country_Clean": [],
            "English_Reading": [],
        })
        result = get_response_counts_for_question(empty_df, "English_Reading")
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Tests for get_summary_statistics
# ---------------------------------------------------------------------------

class TestGetSummaryStatistics:

    def test_returns_dict(self, sample_df):
        result = get_summary_statistics(sample_df)
        assert isinstance(result, dict)

    def test_total_responses(self, sample_df):
        result = get_summary_statistics(sample_df)
        assert result["total_responses"] == 6

    def test_countries_represented(self, sample_df):
        result = get_summary_statistics(sample_df)
        assert result["countries_represented"] == 3

    def test_top_country(self, sample_df):
        result = get_summary_statistics(sample_df)
        assert result["top_country"] == "Nigeria"

    def test_filtered_total(self, sample_df):
        result = get_summary_statistics(sample_df, selected_countries=["India"])
        assert result["total_responses"] == 2

    def test_empty_df_returns_zeros(self):
        empty_df = pd.DataFrame({"Country_Clean": []})
        result = get_summary_statistics(empty_df)
        assert result["total_responses"] == 0
        assert result["top_country"] == "N/A"
