"""
test_data_processing.py
------------------------
Unit tests for the data_processing module.

Tests cover:
  - Country name standardisation (emoji, case, whitespace)
  - Column validation (valid file vs missing column)
  - Data cleaning (empty rows removed, Country_Clean column created)

Run with:
    python -m pytest tests/test_data_processing.py -v
"""

import io
import sys
import os
import pytest
import pandas as pd

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_processing import (
    standardise_country_name,
    validate_columns,
    clean_data,
    COUNTRY_COLUMN,
)


# ---------------------------------------------------------------------------
# Tests for standardise_country_name
# ---------------------------------------------------------------------------

class TestStandardiseCountryName:
    """Tests for the country name cleaning function."""

    def test_removes_emoji_flag(self):
        """Nigeria with flag emoji should map to 'Nigeria'."""
        assert standardise_country_name("Nigeria \U0001f1f3\U0001f1ec") == "Nigeria"

    def test_handles_uppercase_nigeria(self):
        assert standardise_country_name("NIGERIA") == "Nigeria"

    def test_handles_uppercase_india(self):
        assert standardise_country_name("INDIA") == "India"

    def test_handles_lowercase_india(self):
        assert standardise_country_name("india") == "India"

    def test_handles_trailing_space(self):
        assert standardise_country_name("India ") == "India"

    def test_handles_leading_space(self):
        assert standardise_country_name(" Nigeria ") == "Nigeria"

    def test_handles_known_country_sri_lanka(self):
        assert standardise_country_name("Sri Lanka") == "Sri Lanka"

    def test_handles_known_country_myanmar(self):
        assert standardise_country_name("Myanmar") == "Myanmar"

    def test_handles_known_country_iran(self):
        assert standardise_country_name("IRAN") == "Iran"

    def test_handles_known_country_romania(self):
        assert standardise_country_name("ROMANIA") == "Romania"

    def test_handles_empty_string(self):
        assert standardise_country_name("") == ""

    def test_handles_none_input(self):
        assert standardise_country_name(None) == ""

    def test_handles_non_string_input(self):
        assert standardise_country_name(123) == ""

    def test_unknown_country_returns_titlecase(self):
        """A country not in the map should be returned title-cased."""
        result = standardise_country_name("new zealand")
        assert result == "New Zealand"


# ---------------------------------------------------------------------------
# Tests for validate_columns
# ---------------------------------------------------------------------------

class TestValidateColumns:
    """Tests for column validation."""

    def test_valid_dataframe_passes(self):
        """A DataFrame with the required column should pass without error."""
        df = pd.DataFrame({COUNTRY_COLUMN: ["Nigeria", "India"]})
        result = validate_columns(df)
        assert COUNTRY_COLUMN in result.columns

    def test_missing_country_column_raises(self):
        """A DataFrame without the country column should raise ValueError."""
        df = pd.DataFrame({"Some Other Column": ["value"]})
        with pytest.raises(ValueError, match="missing the following required column"):
            validate_columns(df)


# ---------------------------------------------------------------------------
# Tests for clean_data
# ---------------------------------------------------------------------------

class TestCleanData:
    """Tests for the full data cleaning pipeline."""

    def _make_df(self, country_values):
        """Helper: create a minimal DataFrame with the country column."""
        return pd.DataFrame({COUNTRY_COLUMN: country_values})

    def test_creates_country_clean_column(self):
        df = self._make_df(["Nigeria", "India"])
        result = clean_data(df)
        assert "Country_Clean" in result.columns

    def test_removes_empty_country_rows(self):
        """Rows with empty or NaN country should be dropped."""
        df = self._make_df(["Nigeria", "", None, "India"])
        result = clean_data(df)
        assert len(result) == 2

    def test_cleans_emoji_in_country(self):
        """Rows with emoji flags should be cleaned and retained."""
        df = self._make_df(["Nigeria \U0001f1f3\U0001f1ec"])
        result = clean_data(df)
        assert result.iloc[0]["Country_Clean"] == "Nigeria"

    def test_cleans_uppercase_country(self):
        df = self._make_df(["INDIA"])
        result = clean_data(df)
        assert result.iloc[0]["Country_Clean"] == "India"

    def test_cleans_whitespace_country(self):
        df = self._make_df([" Nigeria "])
        result = clean_data(df)
        assert result.iloc[0]["Country_Clean"] == "Nigeria"

    def test_mixed_data_cleaned_correctly(self):
        """A mix of valid and invalid rows should produce correct output."""
        df = self._make_df([
            "Nigeria \U0001f1f3\U0001f1ec",
            "INDIA",
            " india ",
            "",
            None,
            "Sri Lanka",
        ])
        result = clean_data(df)
        assert len(result) == 4
        assert list(result["Country_Clean"]) == [
            "Nigeria", "India", "India", "Sri Lanka"
        ]

    def test_index_is_reset_after_cleaning(self):
        """The index should be consecutive integers after cleaning."""
        df = self._make_df(["Nigeria", None, "India"])
        result = clean_data(df)
        assert list(result.index) == [0, 1]
