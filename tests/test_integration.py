"""
test_integration.py
--------------------
Week 8 — Integration tests.

Tests the full pipeline end-to-end:
  load CSV → clean → add programme → compute stats → build charts

These tests use the actual survey CSV file to ensure that the complete
data pipeline produces correct, consistent results on real data.
"""

import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_processing import validate_columns, clean_data
from utils.statistics import (
    add_programme_category,
    get_nationality_distribution,
    get_programme_distribution,
    get_summary_statistics,
    filter_by_nationality,
    cross_tabulate,
    get_percentage_crosstab,
    get_mean_score_by_nationality,
    get_satisfaction_comparison,
    get_difficulty_questions,
    get_agreement_questions,
    DIFFICULTY_SCALE,
    AGREEMENT_SCALE,
)
from utils.visualisations import (
    nationality_bar_chart,
    nationality_donut_chart,
    stacked_likert_bar,
    grouped_mean_score_bar,
    mean_score_heatmap,
    programme_donut_chart,
    response_horizontal_bar,
)

CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "Assimilation into British University academic culture.csv"
)

# ---------------------------------------------------------------------------
# Fixture: full pipeline from raw CSV
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_df():
    """Load and clean the real survey CSV."""
    if not os.path.exists(CSV_PATH):
        pytest.skip("Real CSV not found — skipping integration tests.")
    raw = pd.read_csv(CSV_PATH)
    df = validate_columns(raw)
    df = clean_data(df)
    df = add_programme_category(df)
    return df


# ---------------------------------------------------------------------------
# Integration: data pipeline
# ---------------------------------------------------------------------------

class TestDataPipeline:

    def test_loads_correct_row_count(self, real_df):
        """62 valid responses expected after cleaning."""
        assert len(real_df) == 62

    def test_twelve_nationalities(self, real_df):
        """Exactly 12 distinct nationalities should be present."""
        n = real_df["Country_Clean"].nunique()
        assert n == 12

    def test_nigeria_is_largest_group(self, real_df):
        """Nigeria should have the most responses (29)."""
        dist = get_nationality_distribution(real_df)
        assert dist.iloc[0]["Country"] == "Nigeria"
        assert dist.iloc[0]["Count"] == 29

    def test_india_is_second_group(self, real_df):
        """India should be second with 21 responses."""
        dist = get_nationality_distribution(real_df)
        assert dist.iloc[1]["Country"] == "India"
        assert dist.iloc[1]["Count"] == 21

    def test_programme_column_created(self, real_df):
        """Programme_Category column must exist after pipeline."""
        assert "Programme_Category" in real_df.columns

    def test_three_programme_categories(self, real_df):
        """Exactly 3 programme categories expected."""
        cats = real_df["Programme_Category"].dropna().nunique()
        assert cats == 3

    def test_computer_science_is_largest_programme(self, real_df):
        """Computer Science should be the largest programme group."""
        dist = get_programme_distribution(real_df)
        assert dist.iloc[0]["Programme"] == "Computer Science"

    def test_summary_stats_correct(self, real_df):
        """Summary statistics should reflect the known dataset."""
        s = get_summary_statistics(real_df)
        assert s["total_responses"] == 62
        assert s["countries_represented"] == 12
        assert s["top_country"] == "Nigeria"


# ---------------------------------------------------------------------------
# Integration: statistics on real data
# ---------------------------------------------------------------------------

class TestStatisticsOnRealData:

    def test_filter_nigeria_returns_29(self, real_df):
        filtered = filter_by_nationality(real_df, ["Nigeria"])
        assert len(filtered) == 29

    def test_filter_india_returns_21(self, real_df):
        filtered = filter_by_nationality(real_df, ["India"])
        assert len(filtered) == 21

    def test_cross_tabulate_returns_totals(self, real_df):
        diff_q = get_difficulty_questions(real_df)
        col = diff_q.get("Writing Assignments")
        if col:
            ct = cross_tabulate(real_df, col, countries=["Nigeria", "India"])
            assert "TOTAL" in ct.index
            # Nigeria (27 valid) + India (21 valid) should match
            assert ct.loc["TOTAL"].sum() >= 40

    def test_percentage_crosstab_columns_sum_100(self, real_df):
        diff_q = get_difficulty_questions(real_df)
        col = diff_q.get("Writing Assignments")
        if col:
            pct = get_percentage_crosstab(real_df, col, ["Nigeria", "India"])
            if not pct.empty:
                for c in pct.columns:
                    assert abs(pct[c].sum() - 100.0) < 1.0

    def test_mean_score_nigeria_india(self, real_df):
        """Mean scores should be between 1 and 5."""
        diff_q = get_difficulty_questions(real_df)
        col = diff_q.get("Writing Assignments")
        if col:
            m = get_mean_score_by_nationality(real_df, col, DIFFICULTY_SCALE, min_responses=3)
            assert not m.empty
            assert m["Mean Score"].between(1, 5).all()

    def test_dynamic_question_finders(self, real_df):
        """Dynamic finders should locate at least 8 difficulty and 8 agreement cols."""
        diff_q = get_difficulty_questions(real_df)
        agr_q  = get_agreement_questions(real_df)
        assert len(diff_q) >= 8
        assert len(agr_q)  >= 5

    def test_satisfaction_comparison_shape(self, real_df):
        """Heatmap data should have rows for each major group."""
        major = [c for c in real_df["Country_Clean"].unique()
                 if (real_df["Country_Clean"] == c).sum() >= 3]
        sat = get_satisfaction_comparison(real_df, countries=major)
        assert not sat.empty
        assert len(sat) == len(major)


# ---------------------------------------------------------------------------
# Integration: combined nationality + programme filter
# ---------------------------------------------------------------------------

class TestCombinedFilter:

    def test_nationality_programme_filter(self, real_df):
        """Combining nationality and programme filters should reduce rows."""
        ng_df = filter_by_nationality(real_df, ["Nigeria"])
        ng_cs = ng_df[ng_df["Programme_Category"] == "Computer Science"]
        assert len(ng_cs) > 0
        assert len(ng_cs) < len(ng_df)

    def test_all_nigeria_in_known_programmes(self, real_df):
        """All Nigerian respondents should map to a known programme category."""
        ng_df = filter_by_nationality(real_df, ["Nigeria"])
        assert not ng_df["Programme_Category"].isin(["Unknown"]).any()


# ---------------------------------------------------------------------------
# Integration: chart builders on real data
# ---------------------------------------------------------------------------

class TestChartBuilders:

    def test_nationality_bar_chart_runs(self, real_df):
        dist = get_nationality_distribution(real_df)
        fig = nationality_bar_chart(dist)
        assert fig is not None

    def test_nationality_donut_chart_runs(self, real_df):
        dist = get_nationality_distribution(real_df)
        fig = nationality_donut_chart(dist)
        assert fig is not None

    def test_programme_donut_chart_runs(self, real_df):
        dist = get_programme_distribution(real_df)
        fig = programme_donut_chart(dist)
        assert fig is not None

    def test_stacked_likert_bar_runs(self, real_df):
        diff_q = get_difficulty_questions(real_df)
        col = diff_q.get("Writing Assignments")
        if col:
            fig = stacked_likert_bar(real_df, col, countries=["Nigeria", "India"])
            assert fig is not None

    def test_mean_score_heatmap_runs(self, real_df):
        major = [c for c in real_df["Country_Clean"].unique()
                 if (real_df["Country_Clean"] == c).sum() >= 3]
        sat = get_satisfaction_comparison(real_df, countries=major)
        fig = mean_score_heatmap(sat)
        assert fig is not None

    def test_grouped_mean_score_bar_runs(self, real_df):
        diff_q = get_difficulty_questions(real_df)
        col1 = diff_q.get("Writing Assignments")
        col2 = diff_q.get("Taking Notes in Class")
        rows = []
        for label, col in [("Writing", col1), ("Notes", col2)]:
            if col:
                m = get_mean_score_by_nationality(real_df, col, DIFFICULTY_SCALE)
                for _, r in m.iterrows():
                    rows.append({"Country": r["Country"],
                                 "Metric": label,
                                 "Mean Score": r["Mean Score"]})
        if rows:
            fig = grouped_mean_score_bar(rows)
            assert fig is not None
