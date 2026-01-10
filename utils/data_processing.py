# this file handles loading and cleaning the survey CSV
# I needed to deal with a lot of messy data - country names had emojis,
# different cases (INDIA vs India), and extra spaces, so I wrote
# functions to clean all of that automatically

import re
import pandas as pd

# this is the exact column name from the MS Forms export
COUNTRY_COLUMN = "What is your home country? *"

# list of columns the file must have for the app to work
REQUIRED_COLUMNS = [COUNTRY_COLUMN]

# I built this dictionary by looking through the actual CSV data
# and noting all the different ways countries were written
COUNTRY_NAME_MAP = {
    "nigeria": "Nigeria",
    "india": "India",
    "sri lanka": "Sri Lanka",
    "myanmar": "Myanmar",
    "kenya": "Kenya",
    "bangladesh": "Bangladesh",
    "pakistan": "Pakistan",
    "iran": "Iran",
    "romania": "Romania",
    "czech republic": "Czech Republic",
    "cyprus": "Cyprus",
    "bahrain": "Bahrain",
}


def load_survey_data(uploaded_file):
    # loads the uploaded file - supports both CSV and Excel
    # returns a cleaned dataframe or raises an error with a readable message
    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(
                "Unsupported file format. Please upload a CSV (.csv) "
                "or Excel (.xlsx) file."
            )
    except Exception as e:
        raise ValueError(f"Could not read file: {e}")

    df = validate_columns(df)
    df = clean_data(df)
    return df


def validate_columns(df):
    # checks the uploaded file actually has the columns we need
    # raises an error if something is missing so the user knows what went wrong
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"The uploaded file is missing the following required column(s): "
            f"{missing}. Please check you have uploaded the correct survey file."
        )
    return df


def clean_data(df):
    # this function applies all the cleaning steps to the raw data
    # step 1: remove blank rows (there was a test submission with no country)
    # step 2: standardise all country names into a consistent format
    df = df.dropna(subset=[COUNTRY_COLUMN]).copy()
    df = df[df[COUNTRY_COLUMN].str.strip() != ""].copy()

    # create a new column with the cleaned country name
    df["Country_Clean"] = df[COUNTRY_COLUMN].apply(standardise_country_name)

    # remove any rows where the country name couldn't be cleaned
    df = df[df["Country_Clean"] != ""].copy()

    return df.reset_index(drop=True)


def standardise_country_name(raw_name):
    # takes a raw country string and returns a clean version
    # handles: emoji flags, UPPERCASE, extra spaces
    # if the country isn't in my dictionary, I just title-case it as a fallback
    if not isinstance(raw_name, str):
        return ""

    # remove emoji using regex - I found some responses had flag emojis attached
    cleaned = re.sub(
        r"[\U0001F1E0-\U0001F1FF"   # flag emoji characters
        r"\U0001F300-\U0001F5FF"
        r"\U0001F600-\U0001F64F"
        r"\U0001F680-\U0001F6FF"
        r"\u2600-\u26FF"
        r"\u2700-\u27BF]+",
        "",
        raw_name
    )

    cleaned = cleaned.strip()
    lookup_key = cleaned.lower()

    # check if its in my known countries dictionary
    if lookup_key in COUNTRY_NAME_MAP:
        return COUNTRY_NAME_MAP[lookup_key]

    # if not, just tidy up the capitalisation
    return cleaned.title() if cleaned else ""


def get_question_columns(df):
    # returns a list of column names that are actual survey questions
    # I filter out the metadata columns that MS Forms adds automatically
    # like Id, timestamps, Points, Feedback etc.
    exclude_prefixes = (
        "Points -", "Feedback -", "Id", "Start time",
        "Completion time", "Total points", "Quiz feedback",
        "Grade posted time", "Country_Clean"
    )
    return [
        col for col in df.columns
        if not any(col.startswith(prefix) for prefix in exclude_prefixes)
        and col != COUNTRY_COLUMN
    ]
