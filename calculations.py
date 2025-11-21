"""
Percentage Calculation Functions
=================================
Handles nationality-based percentage calculations and statistical analysis.

This module provides functionality to:
- Calculate nationality-based percentage breakdowns
- Compute statistics by country
- Handle rating scales and categorical data
- Support comparison across multiple nationalities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from data_processor import SurveyDataProcessor


def calculate_nationality_percentage(df: pd.DataFrame,
                                    country_column: str,
                                    value_column: str,
                                    exclude_null: bool = True,
                                    exclude_not_applicable: bool = False) -> pd.DataFrame:
    """
    Calculate percentage breakdown by nationality for a given column.
    
    Args:
        df (pd.DataFrame): Cleaned survey data
        country_column (str): Name of country/nationality column
        value_column (str): Name of column to analyze
        exclude_null (bool): Whether to exclude null values. Default True
        exclude_not_applicable (bool): Whether to exclude 'Not applicable' values. Default False
    
    Returns:
        pd.DataFrame: DataFrame with columns: Nationality, Value, Count, Percentage
    """
    if country_column not in df.columns or value_column not in df.columns:
        return pd.DataFrame()
    
    # Filter out nulls if requested
    df_filtered = df.copy()
    if exclude_null:
        df_filtered = df_filtered[df_filtered[value_column].notna()].copy()
    
    # Filter out 'Not applicable' if requested
    if exclude_not_applicable:
        df_filtered = df_filtered[
            df_filtered[value_column].astype(str).str.lower() != 'not applicable'
        ].copy()
    
    # Group by nationality and value
    grouped = df_filtered.groupby([country_column, value_column]).size().reset_index(name='Count')
    
    # Calculate total counts per nationality
    country_totals = df_filtered.groupby(country_column).size()
    
    # Calculate percentages
    result_data = []
    for _, row in grouped.iterrows():
        country = row[country_column]
        value = row[value_column]
        count = row['Count']
        
        country_total = country_totals.get(country, 0)
        percentage = (count / country_total * 100) if country_total > 0 else 0
        
        result_data.append({
            'Nationality': country,
            'Value': value,
            'Count': count,
            'Percentage': round(percentage, 2),
            'Total': country_total
        })
    
    return pd.DataFrame(result_data)


def calculate_overall_percentage(df: pd.DataFrame,
                                 value_column: str,
                                 exclude_null: bool = True,
                                 exclude_not_applicable: bool = False) -> pd.DataFrame:
    """
    Calculate overall percentage breakdown for a given column (across all nationalities).
    
    Args:
        df (pd.DataFrame): Cleaned survey data
        value_column (str): Name of column to analyze
        exclude_null (bool): Whether to exclude null values. Default True
        exclude_not_applicable (bool): Whether to exclude 'Not applicable' values. Default False
    
    Returns:
        pd.DataFrame: DataFrame with columns: Value, Count, Percentage
    """
    if value_column not in df.columns:
        return pd.DataFrame()
    
    # Filter out nulls if requested
    df_filtered = df.copy()
    if exclude_null:
        df_filtered = df_filtered[df_filtered[value_column].notna()].copy()
    
    # Filter out 'Not applicable' if requested
    if exclude_not_applicable:
        df_filtered = df_filtered[
            df_filtered[value_column].astype(str).str.lower() != 'not applicable'
        ].copy()
    
    # Calculate value counts
    value_counts = df_filtered[value_column].value_counts().reset_index()
    value_counts.columns = ['Value', 'Count']
    
    # Calculate percentages
    total = len(df_filtered)
    value_counts['Percentage'] = (value_counts['Count'] / total * 100).round(2)
    
    return value_counts


def calculate_country_statistics(df: pd.DataFrame,
                                country_column: str,
                                value_column: str,
                                statistic: str = 'mean') -> pd.DataFrame:
    """
    Calculate statistical summary by country for a numeric column.
    
    Args:
        df (pd.DataFrame): Cleaned survey data
        country_column (str): Name of country/nationality column
        value_column (str): Name of numeric column to analyze
        statistic (str): Statistical measure ('mean', 'median', 'std', 'count'). Default 'mean'
    
    Returns:
        pd.DataFrame: DataFrame with statistics by country
    """
    if country_column not in df.columns or value_column not in df.columns:
        return pd.DataFrame()
    
    # Convert to numeric if possible
    df_numeric = df.copy()
    df_numeric[value_column] = pd.to_numeric(df_numeric[value_column], errors='coerce')
    
    # Calculate statistic by country
    if statistic == 'mean':
        stats = df_numeric.groupby(country_column)[value_column].mean()
    elif statistic == 'median':
        stats = df_numeric.groupby(country_column)[value_column].median()
    elif statistic == 'std':
        stats = df_numeric.groupby(country_column)[value_column].std()
    elif statistic == 'count':
        stats = df_numeric.groupby(country_column)[value_column].count()
    else:
        return pd.DataFrame()
    
    result = stats.reset_index()
    result.columns = ['Nationality', statistic.title()]
    
    return result


def calculate_rating_breakdown_by_country(processor: SurveyDataProcessor,
                                         rating_column: str,
                                         exclude_not_applicable: bool = False) -> pd.DataFrame:
    """
    Calculate rating breakdown by nationality using SurveyDataProcessor.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        rating_column (str): Name of rating column to analyze
        exclude_not_applicable (bool): Whether to exclude 'Not applicable'. Default False
    
    Returns:
        pd.DataFrame: DataFrame with nationality-based rating percentages
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    return calculate_nationality_percentage(
        processor.cleaned_data,
        processor.country_column,
        rating_column,
        exclude_null=True,
        exclude_not_applicable=exclude_not_applicable
    )


def calculate_multiple_ratings_comparison(processor: SurveyDataProcessor,
                                         rating_columns: List[str],
                                         countries: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Calculate percentage breakdown for multiple rating columns by nationality.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        rating_columns (List[str]): List of rating column names to analyze
        countries (List[str], optional): List of countries to include. If None, includes all
    
    Returns:
        pd.DataFrame: Combined results for all rating columns
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    df = processor.cleaned_data.copy()
    
    # Filter by countries if specified
    if countries:
        df = df[df[processor.country_column].isin(countries)].copy()
    
    all_results = []
    
    for rating_col in rating_columns:
        if rating_col not in df.columns:
            continue
        
        # Calculate percentages for this rating
        breakdown = calculate_nationality_percentage(
            df,
            processor.country_column,
            rating_col,
            exclude_null=True
        )
        
        if not breakdown.empty:
            breakdown['Question'] = rating_col
            all_results.append(breakdown)
    
    if all_results:
        return pd.concat(all_results, ignore_index=True)
    
    return pd.DataFrame()


def calculate_response_distribution(df: pd.DataFrame,
                                   country_column: str,
                                   value_column: str,
                                   normalize: bool = True) -> pd.DataFrame:
    """
    Calculate response distribution by nationality as counts or percentages.
    
    Args:
        df (pd.DataFrame): Cleaned survey data
        country_column (str): Name of country/nationality column
        value_column (str): Name of column to analyze
        normalize (bool): If True, return percentages; if False, return counts. Default True
    
    Returns:
        pd.DataFrame: Pivot table with nationalities as rows and values as columns
    """
    if country_column not in df.columns or value_column not in df.columns:
        return pd.DataFrame()
    
    # Create pivot table
    pivot_table = pd.crosstab(
        df[country_column],
        df[value_column],
        normalize='index' if normalize else False,
        dropna=True
    )
    
    # Convert to percentage if normalized
    if normalize:
        pivot_table = pivot_table * 100
    
    # Round to 2 decimal places
    pivot_table = pivot_table.round(2)
    
    return pivot_table.reset_index()


def calculate_country_counts(df: pd.DataFrame,
                            country_column: str) -> pd.DataFrame:
    """
    Calculate count of responses by country.
    
    Args:
        df (pd.DataFrame): Cleaned survey data
        country_column (str): Name of country/nationality column
    
    Returns:
        pd.DataFrame: DataFrame with columns: Nationality, Count, Percentage
    """
    if country_column not in df.columns:
        return pd.DataFrame()
    
    counts = df[country_column].value_counts().reset_index()
    counts.columns = ['Nationality', 'Count']
    
    total = len(df)
    counts['Percentage'] = (counts['Count'] / total * 100).round(2)
    
    return counts.sort_values('Nationality')


def calculate_importance_factor_ranking(processor: SurveyDataProcessor,
                                       importance_column: str,
                                       countries: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Rank importance factors by nationality based on percentage selecting 'Extremely' or 'Very'.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        importance_column (str): Name of importance rating column
        countries (List[str], optional): List of countries to include. If None, includes all
    
    Returns:
        pd.DataFrame: Ranked factors by nationality
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    df = processor.cleaned_data.copy()
    
    # Filter by countries if specified
    if countries:
        df = df[df[processor.country_column].isin(countries)].copy()
    
    # Calculate percentages
    breakdown = calculate_nationality_percentage(
        df,
        processor.country_column,
        importance_column,
        exclude_null=True,
        exclude_not_applicable=True
    )
    
    if breakdown.empty:
        return pd.DataFrame()
    
    # Filter for high importance (Extremely or Very)
    high_importance = breakdown[
        breakdown['Value'].isin(['Extremely', 'Very'])
    ].copy()
    
    # Sum percentages for 'Extremely' and 'Very' per country
    ranking = high_importance.groupby('Nationality')['Percentage'].sum().reset_index()
    ranking.columns = ['Nationality', 'High_Importance_%']
    ranking = ranking.sort_values('High_Importance_%', ascending=False)
    
    return ranking


def calculate_cross_tabulation(df: pd.DataFrame,
                              row_column: str,
                              column_column: str,
                              country_filter: Optional[str] = None,
                              country_column: str = None,
                              normalize: bool = False) -> pd.DataFrame:
    """
    Create cross-tabulation table between two categorical variables.
    
    Args:
        df (pd.DataFrame): Cleaned survey data
        row_column (str): Column name for rows
        column_column (str): Column name for columns
        country_filter (str, optional): Filter by specific country. If None, uses all
        country_column (str, optional): Country column name if filtering
        normalize (bool): If True, normalize to percentages. Default False
    
    Returns:
        pd.DataFrame: Cross-tabulation table
    """
    df_filtered = df.copy()
    
    # Filter by country if specified
    if country_filter and country_column and country_column in df.columns:
        df_filtered = df_filtered[df_filtered[country_column] == country_filter].copy()
    
    if row_column not in df_filtered.columns or column_column not in df_filtered.columns:
        return pd.DataFrame()
    
    # Create cross-tabulation
    if normalize:
        crosstab = pd.crosstab(
            df_filtered[row_column],
            df_filtered[column_column],
            normalize='index' if normalize else False,
            dropna=True
        ) * 100
    else:
        crosstab = pd.crosstab(
            df_filtered[row_column],
            df_filtered[column_column],
            dropna=True
        )
    
    return crosstab.round(2)


def calculate_percentage_summary(processor: SurveyDataProcessor,
                                question_column: str,
                                countries: Optional[List[str]] = None) -> Dict:
    """
    Calculate comprehensive percentage summary for a question.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        countries (List[str], optional): List of countries to include. If None, includes all
    
    Returns:
        Dict: Summary dictionary with:
            - by_country: Breakdown by nationality
            - overall: Overall breakdown
            - country_totals: Response counts by country
            - value_counts: Overall value counts
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return {}
    
    df = processor.cleaned_data.copy()
    
    # Filter by countries if specified
    if countries:
        df = df[df[processor.country_column].isin(countries)].copy()
    
    # Calculate by country
    by_country = calculate_nationality_percentage(
        df,
        processor.country_column,
        question_column,
        exclude_null=True
    )
    
    # Calculate overall
    overall = calculate_overall_percentage(
        df,
        question_column,
        exclude_null=True
    )
    
    # Country totals
    country_totals = df[processor.country_column].value_counts().to_dict()
    
    # Value counts
    value_counts = df[question_column].value_counts().to_dict()
    
    return {
        'by_country': by_country,
        'overall': overall,
        'country_totals': country_totals,
        'value_counts': value_counts,
        'question': question_column
    }


if __name__ == "__main__":
    # Test the calculations module
    print("Percentage Calculation Functions")
    print("=" * 50)
    
    # Test with sample data
    from data_processor import process_survey_data
    import os
    
    sample_file = "Assimilation into British University academic culture.csv"
    if os.path.exists(sample_file):
        try:
            # Process data
            processor = process_survey_data(file_path=sample_file)
            
            if processor.cleaned_data is not None and processor.country_column:
                print(f"\nCountry Distribution:")
                country_counts = calculate_country_counts(
                    processor.cleaned_data,
                    processor.country_column
                )
                print(country_counts)
                
                # Test percentage calculation
                question_cols = processor.get_question_columns()
                if question_cols:
                    test_col = question_cols[0]
                    print(f"\n\nTesting percentage calculation for: {test_col}")
                    breakdown = calculate_nationality_percentage(
                        processor.cleaned_data,
                        processor.country_column,
                        test_col,
                        exclude_null=True
                    )
                    if not breakdown.empty:
                        print(breakdown.head(10))
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Sample file not found: {sample_file}")

