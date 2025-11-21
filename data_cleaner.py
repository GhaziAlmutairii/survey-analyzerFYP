"""
Data Cleaning Module
Handles data cleaning and preprocessing operations for survey data.

This module provides functionality to:
- Clean country/nationality names
- Handle missing values
- Standardize categorical responses
- Normalize rating scales
- Remove test/invalid responses
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


# Standard country name mapping for normalization
COUNTRY_MAPPING = {
    'india': 'India',
    'indian': 'India',
    'india ': 'India',
    'INDIA': 'India',
    'nigeria': 'Nigeria',
    'nigeria ': 'Nigeria',
    'nigeria 🇳🇬': 'Nigeria',
    'NIGERIA': 'Nigeria',
    'myanmar': 'Myanmar',
    'sri lanka': 'Sri Lanka',
    'bangladesh': 'Bangladesh',
    'pakistan': 'Pakistan',
    'pakistan ': 'Pakistan',
    'iran': 'Iran',
    'IRAN': 'Iran',
    'romania': 'Romania',
    'ROMANIA': 'Romania',
    'czech republic': 'Czech Republic',
    'kenya': 'Kenya',
    'cyprus': 'Cyprus',
    'bahrain': 'Bahrain'
}

# Standardized rating scales
IMPORTANCE_RATINGS = ['Not at all', 'A little', 'Moderately', 'Very', 'Extremely', 'Not applicable']
AGREEMENT_RATINGS = ['Strongly disagree', 'Mildly disagree', 'Neither agree nor disagree', 
                     'Neutral', 'Mildly agree', 'Strongly agree', 'Agree', 'Disagree',
                     'Neither agree nor disagree']
DIFFICULTY_RATINGS = ['Not at all', 'Slightly (a little)', 'Moderately', 'Very', 'Extremely', 
                      'Not applicable']
ENGLISH_RATINGS = ['Poor', 'Average', 'Good', 'Excellent']
PERFORMANCE_RATINGS = ['Poor', 'Average', 'Good', 'Excellent', 'Very poor']
SATISFACTION_RATINGS = ['Very dissatisfied', 'Somewhat dissatisfied', 'Neither satisfied nor dissatisfied',
                        'Somewhat satisfied', 'Very satisfied']
IMPORTANCE_FAMILY_RATINGS = ['Not at all important', 'Somewhat important', 'Neutral', 
                             'Extremely important']


def normalize_country_names(df: pd.DataFrame, country_column: str = None) -> pd.DataFrame:
    """
    Normalize and standardize country/nationality names in the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe with country column
        country_column (str, optional): Name of country column. If None, auto-detects
    
    Returns:
        pd.DataFrame: Dataframe with normalized country names
    """
    df_clean = df.copy()
    
    # Auto-detect country column if not provided
    if country_column is None:
        country_cols = ['What is your home country? *', 'What is your home country?', 
                       'Country', 'Home Country', 'Nationality']
        for col in country_cols:
            if col in df_clean.columns:
                country_column = col
                break
    
    if country_column and country_column in df_clean.columns:
        # Normalize country names
        def normalize_country(country):
            if pd.isna(country):
                return None
            country_str = str(country).strip()
            # Check mapping first
            if country_str.lower() in COUNTRY_MAPPING:
                return COUNTRY_MAPPING[country_str.lower()]
            # Return title case if not in mapping
            return country_str.title()
        
        df_clean[country_column] = df_clean[country_column].apply(normalize_country)
    
    return df_clean


def clean_rating_responses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and standardize rating responses across the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe with rating columns
    
    Returns:
        pd.DataFrame: Dataframe with normalized ratings
    """
    df_clean = df.copy()
    
    # Helper function to normalize a rating value
    def normalize_rating(value, rating_type='importance'):
        if pd.isna(value):
            return None
        
        value_str = str(value).strip()
        
        # Handle various rating types
        if rating_type == 'importance':
            mapping = {
                'not at all': 'Not at all',
                'not at all ': 'Not at all',
                'a little': 'A little',
                'a little ': 'A little',
                'moderately': 'Moderately',
                'moderately ': 'Moderately',
                'very': 'Very',
                'very ': 'Very',
                'extremely': 'Extremely',
                'extremely ': 'Extremely',
                'not applicable': 'Not applicable',
                'not applicable ': 'Not applicable'
            }
            return mapping.get(value_str.lower(), value_str)
        
        elif rating_type == 'agreement':
            mapping = {
                'strongly disagree': 'Strongly disagree',
                'mildly disagree': 'Mildly disagree',
                'disagree': 'Disagree',
                'neither agree nor disagree': 'Neither agree nor disagree',
                'neutral': 'Neutral',
                'mildly agree': 'Mildly agree',
                'agree': 'Agree',
                'strongly agree': 'Strongly agree'
            }
            return mapping.get(value_str.lower(), value_str)
        
        elif rating_type == 'difficulty':
            mapping = {
                'not at all': 'Not at all',
                'slightly (a little)': 'Slightly (a little)',
                'slightly': 'Slightly (a little)',
                'moderately': 'Moderately',
                'very': 'Very',
                'extremely': 'Extremely',
                'not applicable': 'Not applicable'
            }
            return mapping.get(value_str.lower(), value_str)
        
        return value_str
    
    # Identify rating columns by keywords
    importance_cols = [col for col in df_clean.columns if 'important' in col.lower() and 
                      'Points' not in col and 'Feedback' not in col]
    agreement_cols = [col for col in df_clean.columns if 'agree' in col.lower() and 
                     'Points' not in col and 'Feedback' not in col]
    difficulty_cols = [col for col in df_clean.columns if 'difficult' in col.lower() and 
                      'Points' not in col and 'Feedback' not in col]
    
    # Normalize importance ratings
    for col in importance_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(lambda x: normalize_rating(x, 'importance'))
    
    # Normalize agreement ratings
    for col in agreement_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(lambda x: normalize_rating(x, 'agreement'))
    
    # Normalize difficulty ratings
    for col in difficulty_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(lambda x: normalize_rating(x, 'difficulty'))
    
    return df_clean


def remove_empty_rows(df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
    """
    Remove rows that are mostly empty (above threshold percentage of missing values).
    
    Args:
        df (pd.DataFrame): Dataframe to clean
        threshold (float): Percentage threshold (0-1). Rows with more than this % missing are removed
    
    Returns:
        pd.DataFrame: Dataframe with empty rows removed
    """
    if df.empty:
        return df
    
    # Calculate missing percentage per row
    missing_pct = df.isnull().sum(axis=1) / len(df.columns)
    
    # Keep rows below threshold
    mask = missing_pct < threshold
    df_clean = df[mask].copy()
    
    return df_clean


def remove_test_responses(df: pd.DataFrame, country_column: str = None) -> pd.DataFrame:
    """
    Remove test responses and invalid entries.
    
    Args:
        df (pd.DataFrame): Dataframe to clean
        country_column (str, optional): Country column name for filtering
    
    Returns:
        pd.DataFrame: Dataframe with test responses removed
    """
    df_clean = df.copy()
    
    # Remove rows with empty country if country column exists
    if country_column and country_column in df_clean.columns:
        df_clean = df_clean[df_clean[country_column].notna()].copy()
    
    # Remove rows where country is empty string
    if country_column and country_column in df_clean.columns:
        df_clean = df_clean[df_clean[country_column] != ''].copy()
        df_clean = df_clean[df_clean[country_column].str.strip() != ''].copy()
    
    return df_clean


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize column names.
    
    Args:
        df (pd.DataFrame): Dataframe with columns to clean
    
    Returns:
        pd.DataFrame: Dataframe with cleaned column names
    """
    df_clean = df.copy()
    
    # Create mapping of old to new column names
    column_mapping = {}
    
    for col in df_clean.columns:
        new_col = col
        # Remove trailing/leading whitespace
        new_col = new_col.strip()
        # Replace multiple spaces with single space
        new_col = ' '.join(new_col.split())
        column_mapping[col] = new_col
    
    df_clean = df_clean.rename(columns=column_mapping)
    
    return df_clean


def clean_survey_data(df: pd.DataFrame, 
                     normalize_countries: bool = True,
                     normalize_ratings: bool = True,
                     remove_empty: bool = True,
                     remove_tests: bool = True,
                     country_column: str = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Main function to clean survey data with all cleaning operations.
    
    Args:
        df (pd.DataFrame): Raw survey data
        normalize_countries (bool): Whether to normalize country names. Default True
        normalize_ratings (bool): Whether to normalize rating scales. Default True
        remove_empty (bool): Whether to remove mostly empty rows. Default True
        remove_tests (bool): Whether to remove test responses. Default True
        country_column (str, optional): Country column name
    
    Returns:
        Tuple[pd.DataFrame, Dict]: Cleaned dataframe and cleaning statistics
    """
    df_clean = df.copy()
    original_rows = len(df_clean)
    
    cleaning_stats = {
        'original_rows': original_rows,
        'rows_removed': 0,
        'operations_performed': []
    }
    
    # Clean column names
    df_clean = clean_column_names(df_clean)
    cleaning_stats['operations_performed'].append('Column names cleaned')
    
    # Normalize countries
    if normalize_countries:
        df_clean = normalize_country_names(df_clean, country_column)
        cleaning_stats['operations_performed'].append('Country names normalized')
    
    # Normalize ratings
    if normalize_ratings:
        df_clean = clean_rating_responses(df_clean)
        cleaning_stats['operations_performed'].append('Rating responses normalized')
    
    # Remove empty rows
    if remove_empty:
        rows_before = len(df_clean)
        df_clean = remove_empty_rows(df_clean, threshold=0.8)
        rows_removed = rows_before - len(df_clean)
        cleaning_stats['rows_removed'] += rows_removed
        if rows_removed > 0:
            cleaning_stats['operations_performed'].append(f'Removed {rows_removed} mostly empty rows')
    
    # Remove test responses
    if remove_tests:
        rows_before = len(df_clean)
        df_clean = remove_test_responses(df_clean, country_column)
        rows_removed = rows_before - len(df_clean)
        cleaning_stats['rows_removed'] += rows_removed
        if rows_removed > 0:
            cleaning_stats['operations_performed'].append(f'Removed {rows_removed} test/invalid responses')
    
    cleaning_stats['final_rows'] = len(df_clean)
    cleaning_stats['rows_removed'] = original_rows - len(df_clean)
    
    return df_clean, cleaning_stats


if __name__ == "__main__":
    # Test the data cleaner
    print("Data Cleaning Module")
    print("=" * 50)
    
    # Test country normalization
    test_df = pd.DataFrame({
        'What is your home country? *': ['india', 'INDIA', 'nigeria', 'Nigeria', '  india  '],
        'Rating': ['Extremely', 'extremely ', 'Very', 'very', 'Not at all']
    })
    
    print("\nOriginal data:")
    print(test_df)
    
    cleaned_df, stats = clean_survey_data(test_df)
    print("\nCleaned data:")
    print(cleaned_df)
    print("\nCleaning statistics:")
    print(stats)

