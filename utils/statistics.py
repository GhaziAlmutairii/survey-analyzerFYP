# statistics.py
# this file has all the statistical functions I wrote for the dashboard
# it started simple (just counting nationalities) and grew as I added more features
# by week 5 I had added Likert scoring, cross-tabs, and the heatmap data functions

import pandas as pd
import numpy as np

# ----------------------------------------------------------------
# Likert scale number mappings
# I convert the text responses to numbers so I can calculate means
# ----------------------------------------------------------------

# difficulty scale - 1 means easy, 5 means very hard
DIFFICULTY_SCALE = {
    "not at all": 1,
    "slightly (a little)": 2,
    "moderately": 3,
    "very": 4,
    "extremely": 5,
}

# agreement scale - 1 means strongly disagree, 5 means strongly agree
AGREEMENT_SCALE = {
    "strongly disagree": 1,
    "mildly disagree": 2,
    "neutral": 3,
    "mildly agree": 4,
    "strongly agree": 5,
}

# satisfaction scale - used for the satisfaction questions
SATISFACTION_SCALE = {
    "very dissatisfied": 1,
    "somewhat dissatisfied": 2,
    "neither satisfied nor dissatisfied": 3,
    "somewhat satisfied": 4,
    "very satisfied": 5,
}

# English ability - only 3 options in this one
ABILITY_SCALE = {
    "average": 1,
    "good": 2,
    "excellent": 3,
}

# importance scale for the factors in choosing Northumbria questions
IMPORTANCE_SCALE = {
    "not important": 1,
    "somewhat important": 2,
    "neutral": 3,
    "very important": 4,
    "extremely important": 5,
}

# study performance - how well students think they are doing
PERFORMANCE_SCALE = {
    "very poor": 1,
    "poor": 2,
    "average": 3,
    "good": 4,
    "excellent": 5,
}

# I use this list to keep Likert responses in the right order in charts
# without this they'd sort alphabetically which makes no sense
LIKERT_DISPLAY_ORDER = [
    "Not at all", "Slightly (a little)", "Moderately", "Very", "Extremely",
    "Strongly disagree", "Mildly disagree", "Neutral", "Mildly agree", "Strongly agree",
    "Very dissatisfied", "Somewhat dissatisfied",
    "Neither satisfied nor dissatisfied",
    "Somewhat satisfied", "Very satisfied",
    "Average", "Good", "Excellent",
    "Very poor", "Poor",
    "Not important", "Somewhat important", "Very important", "Extremely important",
    "Yes", "No",
]


# ----------------------------------------------------------------
# Basic analysis functions - written in week 4
# ----------------------------------------------------------------

def get_nationality_distribution(df):
    """
    Calculate the count and percentage of responses for each nationality.

    Returns
    -------
    pd.DataFrame with columns: Country, Count, Percentage (sorted by Count desc).
    """
    counts = df["Country_Clean"].value_counts().reset_index()
    counts.columns = ["Country", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def filter_by_nationality(df, selected_countries):
    # filters the dataframe by selected countries
    # if nothing is selected, it just returns everything
    if not selected_countries:
        return df
    return df[df["Country_Clean"].isin(selected_countries)].copy()


def get_response_counts_for_question(df, question_column, selected_countries=None):
    """
    Get response frequency counts for a single question, optionally filtered
    by nationality. Returns DataFrame with columns: Response, Count, Percentage.
    """
    if selected_countries:
        df = filter_by_nationality(df, selected_countries)

    valid = df[question_column].dropna()
    if valid.empty:
        return pd.DataFrame(columns=["Response", "Count", "Percentage"])
    valid = valid.astype(str)
    valid = valid[valid.str.strip().str.lower() != "not applicable"]
    valid = valid[valid.str.strip() != ""]

    if valid.empty:
        return pd.DataFrame(columns=["Response", "Count", "Percentage"])

    counts = valid.value_counts().reset_index()
    counts.columns = ["Response", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)

    order_map = {resp: i for i, resp in enumerate(LIKERT_DISPLAY_ORDER)}
    counts["_order"] = counts["Response"].map(order_map).fillna(999)
    counts = counts.sort_values("_order").drop(columns="_order")

    return counts.reset_index(drop=True)


def get_summary_statistics(df, selected_countries=None):
    """
    Return high-level summary statistics dictionary.
    Keys: total_responses, countries_represented, top_country, top_country_pct.
    """
    if selected_countries:
        filtered = filter_by_nationality(df, selected_countries)
    else:
        filtered = df

    dist = get_nationality_distribution(filtered)

    if dist.empty:
        return {
            "total_responses": 0,
            "countries_represented": 0,
            "top_country": "N/A",
            "top_country_pct": 0.0,
        }

    return {
        "total_responses": int(filtered.shape[0]),
        "countries_represented": int(dist.shape[0]),
        "top_country": dist.iloc[0]["Country"],
        "top_country_pct": float(dist.iloc[0]["Percentage"]),
    }


# ---------------------------------------------------------------------------
# Week 5: Likert-to-numeric conversion
# ---------------------------------------------------------------------------

def likert_to_numeric(series, scale_map):
    """
    Convert a pandas Series of Likert text responses to numeric scores
    using the provided scale mapping.

    Responses not found in the map (including 'not applicable') are set to NaN
    so they are excluded from mean calculations.

    Parameters
    ----------
    series : pd.Series
        Raw text response column.
    scale_map : dict
        Mapping of lowercase response text to integer score.

    Returns
    -------
    pd.Series
        Numeric series (float), NaN where response was unmappable.
    """
    return series.astype(str).str.strip().str.lower().map(scale_map)


def get_mean_score_by_nationality(df, question_column, scale_map,
                                  min_responses=3):
    """
    Calculate the mean numeric Likert score for each nationality group
    for a given question.

    Groups with fewer than min_responses valid responses are excluded
    to avoid unreliable means from very small samples.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    question_column : str
        Survey question column to score.
    scale_map : dict
        Likert scale mapping to use (e.g. DIFFICULTY_SCALE).
    min_responses : int
        Minimum valid responses needed to include a group (default 3).

    Returns
    -------
    pd.DataFrame
        Columns: Country, Mean Score, Responses (count), Interpretation.
        Sorted by Mean Score descending.
    """
    df = df.copy()
    df["_score"] = likert_to_numeric(df[question_column], scale_map)

    grouped = (
        df.groupby("Country_Clean")["_score"]
        .agg(["mean", "count"])
        .reset_index()
    )
    grouped.columns = ["Country", "Mean Score", "Responses"]
    grouped["Mean Score"] = grouped["Mean Score"].round(2)

    # Remove groups with too few valid responses
    grouped = grouped[grouped["Responses"] >= min_responses]
    grouped = grouped.sort_values("Mean Score", ascending=False).reset_index(drop=True)

    return grouped


# ---------------------------------------------------------------------------
# Week 5: Cross-tabulation
# ---------------------------------------------------------------------------

def cross_tabulate(df, question_column, countries=None):
    """
    Produce a cross-tabulation table showing response counts for each
    nationality side-by-side for a given question.

    This directly addresses the TOR requirement: "algorithms for statistical
    grouping of demographics" and enables comparative displays.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    question_column : str
        The survey question to cross-tabulate.
    countries : list of str or None
        If provided, restricts to these countries. None = all countries.

    Returns
    -------
    pd.DataFrame
        Pivot table: rows = response options, columns = nationality groups.
        Cell values = count of responses. Totals row appended at bottom.
    """
    if countries:
        df = filter_by_nationality(df, countries)

    valid = df[["Country_Clean", question_column]].copy()
    valid[question_column] = valid[question_column].astype(str).str.strip()
    valid = valid[
        (valid[question_column].str.lower() != "not applicable") &
        (valid[question_column].str.lower() != "nan") &
        (valid[question_column] != "")
    ]

    if valid.empty:
        return pd.DataFrame()

    ct = pd.crosstab(
        valid[question_column],
        valid["Country_Clean"],
    )

    # Sort rows by natural Likert display order
    order_map = {resp: i for i, resp in enumerate(LIKERT_DISPLAY_ORDER)}
    ct["_order"] = [order_map.get(r, 999) for r in ct.index]
    ct = ct.sort_values("_order").drop(columns="_order")

    # Add totals row
    ct.loc["TOTAL"] = ct.sum()

    return ct


def get_percentage_crosstab(df, question_column, countries=None):
    """
    Like cross_tabulate but returns column percentages (within each nationality).
    Useful for comparing response patterns across groups of different sizes.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    question_column : str
        Survey question column.
    countries : list of str or None
        Countries to include.

    Returns
    -------
    pd.DataFrame
        Pivot table with percentage values (0–100), rounded to 1 decimal place.
        Rows = response options, columns = nationality groups.
    """
    ct = cross_tabulate(df, question_column, countries)
    if ct.empty:
        return pd.DataFrame()

    # Remove totals row before computing percentages
    ct_vals = ct.drop(index="TOTAL", errors="ignore")
    pct = (ct_vals / ct_vals.sum() * 100).round(1)
    return pct


# ---------------------------------------------------------------------------
# Week 5: Programme categorisation
# ---------------------------------------------------------------------------

PROGRAMME_CATEGORIES = {
    "computer science": "Computer Science",
    "advanced computer science": "Computer Science",
    "msc computer science": "Computer Science",
    "msc advanced computer science": "Computer Science",
    "computer science with advance practice": "Computer Science",
    "computer science with advanced practice": "Computer Science",
    "msc computer science distance learning": "Computer Science",
    "pgr in computer science": "Computer Science",
    "data science": "Data Science",
    "msc data science": "Data Science",
    "data science with advanced practice": "Data Science",
    "data science with advance practice": "Data Science",
    "information science": "Information Science / Data Analytics",
    "information science data analytics": "Information Science / Data Analytics",
    "information science(data analytics)": "Information Science / Data Analytics",
    "information science-data analytics": "Information Science / Data Analytics",
    "information science with data analytics": "Information Science / Data Analytics",
    "information science/ data analytics": "Information Science / Data Analytics",
    "information science (data analytics)": "Information Science / Data Analytics",
    "information science data analytics": "Information Science / Data Analytics",
    "information science and data analytics": "Information Science / Data Analytics",
    "msc. information science( data analytics)": "Information Science / Data Analytics",
    "information science ( data analytics)": "Information Science / Data Analytics",
}


def categorise_programme(raw_name):
    """
    Map a raw MSc programme name string to a standardised category.

    Parameters
    ----------
    raw_name : str
        Raw programme name as entered in the survey.

    Returns
    -------
    str
        Standardised category name, or 'Other' if no match found.
    """
    if not isinstance(raw_name, str) or raw_name.strip() == "":
        return "Unknown"

    normalised = raw_name.strip().lower()

    # Direct match
    if normalised in PROGRAMME_CATEGORIES:
        return PROGRAMME_CATEGORIES[normalised]

    # Partial match — check if any key is contained within the response
    for key, category in PROGRAMME_CATEGORIES.items():
        if key in normalised:
            return category

    return "Other"


def add_programme_category(df, programme_column="Which MSc programme are you studying at the moment?"):
    """
    Add a 'Programme_Category' column to the DataFrame using categorise_programme().

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    programme_column : str
        Column containing raw programme names.

    Returns
    -------
    pd.DataFrame
        DataFrame with new 'Programme_Category' column added.
    """
    df = df.copy()
    if programme_column in df.columns:
        df["Programme_Category"] = df[programme_column].apply(categorise_programme)
    else:
        df["Programme_Category"] = "Unknown"
    return df


def get_programme_distribution(df):
    """
    Calculate the count and percentage of students per programme category.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'Programme_Category' column.

    Returns
    -------
    pd.DataFrame
        Columns: Programme, Count, Percentage. Sorted by Count descending.
    """
    if "Programme_Category" not in df.columns:
        return pd.DataFrame(columns=["Programme", "Count", "Percentage"])

    counts = df["Programme_Category"].value_counts().reset_index()
    counts.columns = ["Programme", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


# ---------------------------------------------------------------------------
# Week 5: Satisfaction score comparison
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Dynamic column finders — resolve exact column names from the DataFrame
# This avoids encoding issues (curly quotes \u2018/\u2019, replacement chars)
# in the difficulty question column prefix.
# ---------------------------------------------------------------------------

def _find_col(df, *substrings):
    """
    Find the first column in df.columns that contains ALL of the given
    substrings (case-insensitive). Returns None if not found.
    """
    for col in df.columns:
        col_lower = col.lower()
        if all(s.lower() in col_lower for s in substrings):
            return col
    return None


def get_difficulty_questions(df):
    """
    Return a label -> column_name dict for the difficulty question block,
    resolved dynamically from the DataFrame's actual column names.
    """
    mapping = {
        "Understanding Lecturers": ("difficult", "understanding lecturer"),
        "Writing Assignments": ("difficult", "writing assignment"),
        "Taking Notes in Class": ("difficult", "taking notes"),
        "Working on Group Activities": ("difficult", "working on group"),
        "Making Presentations": ("difficult", "making presentations"),
        "Managing Workload": ("difficult", "managing your workload"),
        "Asking Questions in Class": ("difficult", "asking questions"),
        "Thinking Critically": ("difficult", "thinking critically"),
        "Communicating in English": ("difficult", "communicating) in english"),
        "Harvard Referencing": ("difficult", "harvard"),
    }
    result = {}
    for label, substrings in mapping.items():
        col = _find_col(df, *substrings)
        if col:
            result[label] = col
    return result


def get_agreement_questions(df):
    """
    Return a label -> column_name dict for the agreement question block.
    """
    mapping = {
        "Lecturers Help International Students": ("agree or disagree with the following", "make special efforts"),
        "Cultural Differences Respected": ("agree or disagree with the following", "cultural differences are respected"),
        "Lecturers Understand Int'l Students": ("agree or disagree with the following", "understand the problems of international"),
        "Content Useful for Future": ("agree or disagree with the following", "useful for my future"),
        "Classmates Accept Cultural Differences": ("agree or disagree with the following", "classmates are accepting"),
        "Feel Included in Classes": ("agree or disagree with the following", "feel included in my classes"),
        "Lecturers Understand Learning Styles": ("agree or disagree with the following", "cultural differences in learning"),
        "Cross-cultural Group Work": ("agree or disagree with the following", "different cultural groups work well"),
    }
    result = {}
    for label, substrings in mapping.items():
        col = _find_col(df, *substrings)
        if col:
            result[label] = col
    return result


def get_satisfaction_questions(df):
    """
    Return a label -> column_name dict for satisfaction/performance questions.
    """
    mapping = {
        "Study Progress (Self-rated)": ("how well do you think you are doing",),
        "Satisfaction with Progress": ("satisfied with your progress",),
        "Feel Included in Class": ("included in my class",),
        "Family Importance of Doing Well": ("important is it to your family",),
    }
    result = {}
    for label, substrings in mapping.items():
        col = _find_col(df, *substrings)
        if col:
            result[label] = col
    return result


# Keep static dicts for backward compatibility with tests that don't have a df
DIFFICULTY_QUESTIONS = {
    "Understanding Lecturers": "<dynamic — call get_difficulty_questions(df)>",
    "Writing Assignments": "<dynamic — call get_difficulty_questions(df)>",
}
AGREEMENT_QUESTIONS = {
    "Lecturers Help International Students": "<dynamic — call get_agreement_questions(df)>",
    "Cultural Differences Respected": "<dynamic — call get_agreement_questions(df)>",
}


def get_satisfaction_comparison(df, countries=None):
    """
    Compute mean agreement and difficulty scores per nationality for key
    survey question blocks, using dynamic column resolution to handle
    encoding variations in MS Forms export column names.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    countries : list of str or None
        If provided, restricts comparison to these countries.

    Returns
    -------
    pd.DataFrame
        Rows = nationalities (index), columns = metric names,
        values = mean scores (1–5 scale). NaN where data insufficient.
    """
    # Resolve actual column names from this specific DataFrame
    agreement_cols = get_agreement_questions(df)
    difficulty_cols = get_difficulty_questions(df)

    if countries:
        df = filter_by_nationality(df, countries)

    rows = []
    all_countries = sorted(df["Country_Clean"].unique())

    for country in all_countries:
        country_df = df[df["Country_Clean"] == country]
        row = {"Country": country, "n": len(country_df)}

        # Agreement questions (Strongly Disagree=1 → Strongly Agree=5)
        for label, col in agreement_cols.items():
            scores = likert_to_numeric(country_df[col], AGREEMENT_SCALE)
            row[label] = round(scores.mean(), 2) if scores.notna().sum() > 0 else None

        # Difficulty questions (Not at all=1 → Extremely=5)
        for label, col in difficulty_cols.items():
            scores = likert_to_numeric(country_df[col], DIFFICULTY_SCALE)
            row[f"⚠ {label}"] = round(scores.mean(), 2) if scores.notna().sum() > 0 else None

        rows.append(row)

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.set_index("Country")
    return result

