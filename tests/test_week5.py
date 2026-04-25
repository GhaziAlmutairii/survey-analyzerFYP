"""
test_week5.py
-------------
Unit tests for Week 5 statistical functions:
  - likert_to_numeric
  - get_mean_score_by_nationality
  - cross_tabulate / get_percentage_crosstab
  - categorise_programme / add_programme_category / get_programme_distribution
  - get_satisfaction_comparison

Run with: python -m pytest tests/ -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.statistics import (
    likert_to_numeric,
    get_mean_score_by_nationality,
    cross_tabulate,
    get_percentage_crosstab,
    categorise_programme,
    add_programme_category,
    get_programme_distribution,
    get_satisfaction_comparison,
    DIFFICULTY_SCALE,
    AGREEMENT_SCALE,
)


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Country_Clean": [
            "Nigeria", "Nigeria", "Nigeria", "Nigeria",
            "India", "India", "India",
        ],
        "Difficulty_Q": [
            "Extremely", "Very", "Moderately", "Not at all",
            "Slightly (a little)", "Moderately", "Very",
        ],
        "Agreement_Q": [
            "Strongly agree", "Mildly agree", "Neutral", "Strongly agree",
            "Neutral", "Mildly disagree", "Strongly agree",
        ],
        "Which MSc programme are you studying at the moment?": [
            "Computer Science", "Data Science", "Computer Science", "Information Science Data Analytics",
            "Data Science", "Data Science", "Advanced Computer Science",
        ],
    })


# ---------------------------------------------------------------------------
# likert_to_numeric
# ---------------------------------------------------------------------------

class TestLikertToNumeric:

    def test_difficulty_scale_maps_correctly(self):
        s = pd.Series(["Not at all", "Moderately", "Extremely"])
        result = likert_to_numeric(s, DIFFICULTY_SCALE)
        assert list(result) == [1, 3, 5]

    def test_agreement_scale_maps_correctly(self):
        s = pd.Series(["Strongly agree", "Neutral", "Strongly disagree"])
        result = likert_to_numeric(s, AGREEMENT_SCALE)
        assert list(result) == [5, 3, 1]

    def test_unknown_response_returns_nan(self):
        s = pd.Series(["Not applicable", "Random text"])
        result = likert_to_numeric(s, DIFFICULTY_SCALE)
        assert result.isna().all()

    def test_case_insensitive(self):
        s = pd.Series(["EXTREMELY", "moderately", "Not At All"])
        result = likert_to_numeric(s, DIFFICULTY_SCALE)
        assert list(result) == [5, 3, 1]

    def test_handles_trailing_whitespace(self):
        s = pd.Series(["Extremely ", " Very"])
        result = likert_to_numeric(s, DIFFICULTY_SCALE)
        assert list(result) == [5, 4]

    def test_empty_series_returns_empty(self):
        s = pd.Series([], dtype=str)
        result = likert_to_numeric(s, DIFFICULTY_SCALE)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# get_mean_score_by_nationality
# ---------------------------------------------------------------------------

class TestGetMeanScoreByNationality:

    def test_returns_dataframe(self, sample_df):
        result = get_mean_score_by_nationality(
            sample_df, "Difficulty_Q", DIFFICULTY_SCALE
        )
        assert isinstance(result, pd.DataFrame)

    def test_has_correct_columns(self, sample_df):
        result = get_mean_score_by_nationality(
            sample_df, "Difficulty_Q", DIFFICULTY_SCALE
        )
        assert "Country" in result.columns
        assert "Mean Score" in result.columns
        assert "Responses" in result.columns

    def test_nigeria_mean_difficulty(self, sample_df):
        # Nigeria: Extremely=5, Very=4, Moderately=3, Not at all=1 → mean = 3.25
        result = get_mean_score_by_nationality(
            sample_df, "Difficulty_Q", DIFFICULTY_SCALE
        )
        ng = result[result["Country"] == "Nigeria"]["Mean Score"].values[0]
        assert abs(ng - 3.25) < 0.01

    def test_min_responses_filter(self, sample_df):
        # With min_responses=5, India (3 rows) should be excluded
        result = get_mean_score_by_nationality(
            sample_df, "Difficulty_Q", DIFFICULTY_SCALE, min_responses=5
        )
        assert "India" not in result["Country"].values

    def test_sorted_by_mean_descending(self, sample_df):
        result = get_mean_score_by_nationality(
            sample_df, "Difficulty_Q", DIFFICULTY_SCALE, min_responses=1
        )
        scores = result["Mean Score"].tolist()
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# cross_tabulate
# ---------------------------------------------------------------------------

class TestCrossTabulate:

    def test_returns_dataframe(self, sample_df):
        result = cross_tabulate(sample_df, "Difficulty_Q")
        assert isinstance(result, pd.DataFrame)

    def test_has_totals_row(self, sample_df):
        result = cross_tabulate(sample_df, "Difficulty_Q")
        assert "TOTAL" in result.index

    def test_totals_correct(self, sample_df):
        result = cross_tabulate(sample_df, "Difficulty_Q")
        assert result.loc["TOTAL"].sum() == 7  # 7 total responses

    def test_country_filter_works(self, sample_df):
        result = cross_tabulate(sample_df, "Difficulty_Q", countries=["Nigeria"])
        assert "India" not in result.columns

    def test_empty_when_no_valid_data(self):
        df = pd.DataFrame({
            "Country_Clean": ["Nigeria"],
            "Difficulty_Q": ["Not applicable"],
        })
        result = cross_tabulate(df, "Difficulty_Q")
        assert result.empty


# ---------------------------------------------------------------------------
# get_percentage_crosstab
# ---------------------------------------------------------------------------

class TestGetPercentageCrosstab:

    def test_columns_sum_to_100(self, sample_df):
        result = get_percentage_crosstab(sample_df, "Difficulty_Q")
        if not result.empty:
            for col in result.columns:
                col_sum = result[col].sum()
                assert abs(col_sum - 100.0) < 1.0  # allow rounding


# ---------------------------------------------------------------------------
# categorise_programme
# ---------------------------------------------------------------------------

class TestCategoriseProgramme:

    def test_computer_science(self):
        assert categorise_programme("Computer Science") == "Computer Science"

    def test_computer_science_uppercase(self):
        assert categorise_programme("MSC COMPUTER SCIENCE") == "Computer Science"

    def test_data_science(self):
        assert categorise_programme("Data Science") == "Data Science"

    def test_information_science(self):
        assert categorise_programme("Information Science Data Analytics") == \
               "Information Science / Data Analytics"

    def test_partial_match(self):
        assert categorise_programme("Msc computer science with advanced practice") == \
               "Computer Science"

    def test_unknown_returns_other(self):
        assert categorise_programme("International Sports Management") == "Other"

    def test_empty_string_returns_unknown(self):
        assert categorise_programme("") == "Unknown"

    def test_none_returns_unknown(self):
        assert categorise_programme(None) == "Unknown"


# ---------------------------------------------------------------------------
# add_programme_category
# ---------------------------------------------------------------------------

class TestAddProgrammeCategory:

    def test_adds_column(self, sample_df):
        result = add_programme_category(sample_df)
        assert "Programme_Category" in result.columns

    def test_correct_categories(self, sample_df):
        result = add_programme_category(sample_df)
        cats = set(result["Programme_Category"].unique())
        assert "Computer Science" in cats
        assert "Data Science" in cats

    def test_original_df_not_modified(self, sample_df):
        _ = add_programme_category(sample_df)
        assert "Programme_Category" not in sample_df.columns


# ---------------------------------------------------------------------------
# get_programme_distribution
# ---------------------------------------------------------------------------

class TestGetProgrammeDistribution:

    def test_returns_dataframe(self, sample_df):
        df = add_programme_category(sample_df)
        result = get_programme_distribution(df)
        assert isinstance(result, pd.DataFrame)

    def test_has_correct_columns(self, sample_df):
        df = add_programme_category(sample_df)
        result = get_programme_distribution(df)
        assert list(result.columns) == ["Programme", "Count", "Percentage"]

    def test_percentages_sum_to_100(self, sample_df):
        df = add_programme_category(sample_df)
        result = get_programme_distribution(df)
        assert abs(result["Percentage"].sum() - 100.0) < 0.1

    def test_data_science_count(self, sample_df):
        df = add_programme_category(sample_df)
        result = get_programme_distribution(df)
        ds = result[result["Programme"] == "Data Science"]["Count"].values[0]
        assert ds == 3  # 3 Data Science rows in fixture


# ---------------------------------------------------------------------------
# Accuracy verification against known real-data values
# ---------------------------------------------------------------------------

class TestAccuracyAgainstKnownData:
    """
    Verify that statistical functions produce results consistent with
    manual computation from the known dataset (62 valid responses).
    """

    def test_nigeria_is_largest_group(self):
        """Nigeria should be the top nationality by count."""
        from utils.statistics import get_nationality_distribution
        df = pd.DataFrame({
            "Country_Clean": (["Nigeria"] * 29) + (["India"] * 21) + (["Sri Lanka"] * 3)
                             + (["Other"] * 9)
        })
        dist = get_nationality_distribution(df)
        assert dist.iloc[0]["Country"] == "Nigeria"
        assert dist.iloc[0]["Count"] == 29

    def test_nigeria_india_together_exceed_75pct(self):
        """Nigeria + India combined should exceed 75% of responses."""
        df = pd.DataFrame({
            "Country_Clean": (["Nigeria"] * 29) + (["India"] * 21) + (["Sri Lanka"] * 3)
                             + (["Other"] * 9)
        })
        from utils.statistics import get_nationality_distribution
        dist = get_nationality_distribution(df)
        top2_pct = dist[dist["Country"].isin(["Nigeria", "India"])]["Percentage"].sum()
        assert top2_pct > 75.0
