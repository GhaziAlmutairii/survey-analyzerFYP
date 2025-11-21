"""
Advanced Comparison Functions
==============================
Handles advanced comparison and analysis across multiple nationalities and questions.

This module provides functionality to:
- Compare responses across different nationalities
- Multi-nationality side-by-side comparisons
- Statistical comparisons (chi-square, t-tests)
- Trend analysis across rating scales
- Difference calculations between groups
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from scipy import stats
from data_processor import SurveyDataProcessor
from calculations import calculate_nationality_percentage, calculate_response_distribution


def compare_nationalities(processor: SurveyDataProcessor,
                         question_column: str,
                         countries: List[str],
                         exclude_not_applicable: bool = False) -> pd.DataFrame:
    """
    Compare responses across multiple nationalities for a given question.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        countries (List[str]): List of countries to compare
        exclude_not_applicable (bool): Whether to exclude 'Not applicable'. Default False
    
    Returns:
        pd.DataFrame: Comparison table with countries as columns and values as rows
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    if question_column not in processor.cleaned_data.columns:
        return pd.DataFrame()
    
    # Filter data for specified countries
    df_filtered = processor.cleaned_data[
        processor.cleaned_data[processor.country_column].isin(countries)
    ].copy()
    
    # Calculate percentages for each country
    comparison_data = []
    
    for country in countries:
        country_data = df_filtered[
            df_filtered[processor.country_column] == country
        ].copy()
        
        if len(country_data) == 0:
            continue
        
        # Calculate value counts and percentages
        value_counts = country_data[question_column].value_counts()
        total = len(country_data[country_data[question_column].notna()])
        
        if exclude_not_applicable:
            value_counts = value_counts[
                value_counts.index.astype(str).str.lower() != 'not applicable'
            ]
            total = country_data[
                (country_data[question_column].notna()) &
                (country_data[question_column].astype(str).str.lower() != 'not applicable')
            ].shape[0]
        
        percentages = (value_counts / total * 100).round(2) if total > 0 else pd.Series()
        
        for value, count in value_counts.items():
            pct = percentages[value] if value in percentages.index else 0
            comparison_data.append({
                'Value': value,
                'Country': country,
                'Count': count,
                'Percentage': pct,
                'Total': total
            })
    
    if not comparison_data:
        return pd.DataFrame()
    
    # Create comparison table
    comparison_df = pd.DataFrame(comparison_data)
    
    # Pivot table for easier comparison
    pivot_table = comparison_df.pivot_table(
        index='Value',
        columns='Country',
        values='Percentage',
        aggfunc='first',
        fill_value=0
    )
    
    return pivot_table


def compare_side_by_side(processor: SurveyDataProcessor,
                        question_column: str,
                        countries: List[str],
                        show_counts: bool = True) -> pd.DataFrame:
    """
    Create side-by-side comparison table for multiple countries.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        countries (List[str]): List of countries to compare
        show_counts (bool): Whether to show counts alongside percentages. Default True
    
    Returns:
        pd.DataFrame: Side-by-side comparison with Count (Percentage) format
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    # Calculate percentages for each country
    breakdown = calculate_nationality_percentage(
        processor.cleaned_data,
        processor.country_column,
        question_column,
        exclude_null=True
    )
    
    # Filter for specified countries
    breakdown = breakdown[breakdown['Nationality'].isin(countries)].copy()
    
    if breakdown.empty:
        return pd.DataFrame()
    
    # Create side-by-side format
    if show_counts:
        breakdown['Count_Pct'] = breakdown['Count'].astype(str) + ' (' + \
                                  breakdown['Percentage'].astype(str) + '%)'
    else:
        breakdown['Count_Pct'] = breakdown['Percentage'].astype(str) + '%'
    
    # Pivot table
    pivot_table = breakdown.pivot_table(
        index='Value',
        columns='Nationality',
        values='Count_Pct',
        aggfunc='first',
        fill_value='0 (0%)'
    )
    
    return pivot_table


def calculate_difference_between_countries(processor: SurveyDataProcessor,
                                          question_column: str,
                                          country1: str,
                                          country2: str,
                                          value: str) -> Dict:
    """
    Calculate difference in percentage between two countries for a specific value.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        country1 (str): First country to compare
        country2 (str): Second country to compare
        value (str): Response value to compare
    
    Returns:
        Dict: Dictionary with percentages and difference
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return {}
    
    # Calculate percentages
    breakdown = calculate_nationality_percentage(
        processor.cleaned_data,
        processor.country_column,
        question_column,
        exclude_null=True
    )
    
    # Filter for specific countries and value
    filtered = breakdown[
        (breakdown['Nationality'].isin([country1, country2])) &
        (breakdown['Value'] == value)
    ].copy()
    
    if filtered.empty:
        return {}
    
    # Get percentages
    pct1 = filtered[filtered['Nationality'] == country1]['Percentage'].values
    pct2 = filtered[filtered['Nationality'] == country2]['Percentage'].values
    
    pct1_value = pct1[0] if len(pct1) > 0 else 0
    pct2_value = pct2[0] if len(pct2) > 0 else 0
    
    difference = pct1_value - pct2_value
    
    return {
        'country1': country1,
        'country2': country2,
        'value': value,
        'country1_percentage': round(pct1_value, 2),
        'country2_percentage': round(pct2_value, 2),
        'difference': round(difference, 2),
        'difference_abs': round(abs(difference), 2)
    }


def compare_rating_scales_across_countries(processor: SurveyDataProcessor,
                                          question_column: str,
                                          countries: List[str],
                                          rating_order: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Compare rating scale responses across countries with proper ordering.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Rating column to analyze
        countries (List[str]): List of countries to compare
        rating_order (List[str], optional): Custom order for ratings. If None, uses default order
    
    Returns:
        pd.DataFrame: Comparison table with ordered ratings
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    # Get comparison table
    comparison = compare_nationalities(
        processor,
        question_column,
        countries,
        exclude_not_applicable=True
    )
    
    if comparison.empty:
        return pd.DataFrame()
    
    # Default rating orders
    if rating_order is None:
        # Detect rating type from column name
        col_lower = question_column.lower()
        if 'important' in col_lower:
            rating_order = ['Not at all', 'A little', 'Moderately', 'Very', 'Extremely']
        elif 'agree' in col_lower:
            rating_order = ['Strongly disagree', 'Mildly disagree', 'Neither agree nor disagree',
                          'Neutral', 'Mildly agree', 'Strongly agree', 'Agree', 'Disagree']
        elif 'difficult' in col_lower:
            rating_order = ['Not at all', 'Slightly (a little)', 'Moderately', 'Very', 'Extremely']
        else:
            rating_order = comparison.index.tolist()
    
    # Reorder index
    existing_ratings = [r for r in rating_order if r in comparison.index]
    other_ratings = [r for r in comparison.index if r not in rating_order]
    ordered_index = existing_ratings + other_ratings
    
    comparison = comparison.reindex(ordered_index)
    
    return comparison


def calculate_statistical_significance(processor: SurveyDataProcessor,
                                     question_column: str,
                                     country1: str,
                                     country2: str,
                                     value: str) -> Dict:
    """
    Calculate statistical significance of difference between two countries using chi-square test.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        country1 (str): First country
        country2 (str): Second country
        value (str): Response value to test
    
    Returns:
        Dict: Statistical test results including chi-square statistic and p-value
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return {}
    
    df = processor.cleaned_data.copy()
    
    # Filter for two countries
    df_filtered = df[df[processor.country_column].isin([country1, country2])].copy()
    
    # Create contingency table
    contingency = pd.crosstab(
        df_filtered[processor.country_column],
        df_filtered[question_column] == value
    )
    
    if contingency.shape[1] < 2:
        return {
            'country1': country1,
            'country2': country2,
            'value': value,
            'error': 'Insufficient data for statistical test'
        }
    
    # Perform chi-square test
    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        
        significant = p_value < 0.05
        
        return {
            'country1': country1,
            'country2': country2,
            'value': value,
            'chi_square': round(chi2, 4),
            'p_value': round(p_value, 4),
            'degrees_of_freedom': dof,
            'significant': significant,
            'interpretation': 'Significant' if significant else 'Not significant'
        }
    except Exception as e:
        return {
            'country1': country1,
            'country2': country2,
            'value': value,
            'error': str(e)
        }


def compare_multiple_questions(processor: SurveyDataProcessor,
                              question_columns: List[str],
                              countries: List[str],
                              focus_value: Optional[str] = None) -> pd.DataFrame:
    """
    Compare multiple questions across countries.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_columns (List[str]): List of question columns to compare
        countries (List[str]): List of countries to compare
        focus_value (str, optional): If specified, only compares this value. If None, sums all percentages
    
    Returns:
        pd.DataFrame: Comparison table with questions as rows and countries as columns
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    comparison_data = []
    
    for question in question_columns:
        if question not in processor.cleaned_data.columns:
            continue
        
        breakdown = calculate_nationality_percentage(
            processor.cleaned_data,
            processor.country_column,
            question,
            exclude_null=True,
            exclude_not_applicable=True
        )
        
        # Filter for specified countries
        breakdown = breakdown[breakdown['Nationality'].isin(countries)].copy()
        
        if breakdown.empty:
            continue
        
        # If focus_value specified, get percentage for that value
        # Otherwise, sum all percentages (should be ~100%)
        if focus_value:
            for country in countries:
                country_data = breakdown[
                    (breakdown['Nationality'] == country) &
                    (breakdown['Value'] == focus_value)
                ]
                pct = country_data['Percentage'].values[0] if len(country_data) > 0 else 0
                comparison_data.append({
                    'Question': question,
                    'Country': country,
                    'Percentage': round(pct, 2)
                })
        else:
            # Sum percentages for each country (should be close to 100%)
            for country in countries:
                country_total = breakdown[breakdown['Nationality'] == country]['Percentage'].sum()
                comparison_data.append({
                    'Question': question,
                    'Country': country,
                    'Percentage': round(country_total, 2)
                })
    
    if not comparison_data:
        return pd.DataFrame()
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Pivot table
    pivot_table = comparison_df.pivot_table(
        index='Question',
        columns='Country',
        values='Percentage',
        aggfunc='first',
        fill_value=0
    )
    
    return pivot_table


def calculate_ranking_comparison(processor: SurveyDataProcessor,
                                question_column: str,
                                countries: List[str],
                                value: str = 'Extremely') -> pd.DataFrame:
    """
    Rank countries by percentage for a specific value (e.g., 'Extremely').
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        countries (List[str]): List of countries to rank
        value (str): Value to rank by. Default 'Extremely'
    
    Returns:
        pd.DataFrame: Ranked countries with percentages
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return pd.DataFrame()
    
    # Calculate percentages
    breakdown = calculate_nationality_percentage(
        processor.cleaned_data,
        processor.country_column,
        question_column,
        exclude_null=True
    )
    
    # Filter for specified countries and value
    filtered = breakdown[
        (breakdown['Nationality'].isin(countries)) &
        (breakdown['Value'] == value)
    ].copy()
    
    if filtered.empty:
        return pd.DataFrame()
    
    # Sort by percentage
    ranking = filtered.sort_values('Percentage', ascending=False).copy()
    ranking['Rank'] = range(1, len(ranking) + 1)
    
    return ranking[['Rank', 'Nationality', 'Value', 'Count', 'Percentage']]


def generate_comparison_report(processor: SurveyDataProcessor,
                              question_column: str,
                              countries: List[str]) -> str:
    """
    Generate a text report comparing countries for a question.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        countries (List[str]): List of countries to compare
    
    Returns:
        str: Formatted comparison report
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return "Error: No data available"
    
    # Get comparison table
    comparison = compare_nationalities(
        processor,
        question_column,
        countries
    )
    
    if comparison.empty:
        return "Error: No comparison data available"
    
    # Generate report
    report = []
    report.append("=" * 70)
    report.append(f"COMPARISON REPORT: {question_column}")
    report.append("=" * 70)
    report.append(f"\nCountries compared: {', '.join(countries)}")
    report.append(f"\nTotal responses per country:")
    
    for country in countries:
        count = len(processor.cleaned_data[
            processor.cleaned_data[processor.country_column] == country
        ])
        report.append(f"  - {country}: {count}")
    
    report.append("\n" + "-" * 70)
    report.append("Percentage Distribution:")
    report.append("-" * 70)
    report.append(comparison.to_string())
    
    # Add top values for each country
    report.append("\n" + "-" * 70)
    report.append("Top Response for Each Country:")
    report.append("-" * 70)
    
    for country in countries:
        if country in comparison.columns:
            country_data = comparison[country].sort_values(ascending=False)
            if len(country_data) > 0:
                top_value = country_data.index[0]
                top_pct = country_data.iloc[0]
                report.append(f"  {country}: {top_value} ({top_pct}%)")
    
    report.append("\n" + "=" * 70)
    
    return "\n".join(report)


if __name__ == "__main__":
    # Test the comparisons module
    print("Advanced Comparison Functions")
    print("=" * 70)
    
    # Test with sample data
    from data_processor import process_survey_data
    import os
    
    sample_file = "Assimilation into British University academic culture.csv"
    if os.path.exists(sample_file):
        try:
            # Process data
            processor = process_survey_data(file_path=sample_file)
            
            if processor.cleaned_data is not None and processor.country_column:
                countries = processor.get_countries()[:3]  # Test with first 3 countries
                
                if countries:
                    question_cols = processor.get_question_columns()
                    if question_cols:
                        test_col = question_cols[0]
                        print(f"\nTesting comparison for: {test_col}")
                        print(f"Countries: {countries}")
                        
                        # Test side-by-side comparison
                        comparison = compare_side_by_side(
                            processor,
                            test_col,
                            countries
                        )
                        if not comparison.empty:
                            print("\nSide-by-side comparison:")
                            print(comparison)
                        
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Sample file not found: {sample_file}")

