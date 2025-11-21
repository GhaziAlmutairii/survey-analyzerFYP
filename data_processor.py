"""
Data Processor Module
=====================
Main data processing pipeline that combines loading and cleaning operations.

This module provides:
- Complete data processing pipeline from file to cleaned data
- Nationality-based grouping functions
- Percentage calculation algorithms
- Data structure setup for visualization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from data_loader import load_survey_data, load_survey_data_from_upload, validate_loaded_data
from data_cleaner import clean_survey_data


class SurveyDataProcessor:
    """
    Main class for processing survey data.
    Handles loading, cleaning, and structuring survey responses.
    """
    
    def __init__(self):
        self.raw_data: Optional[pd.DataFrame] = None
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.country_column: Optional[str] = None
        self.cleaning_stats: Optional[Dict] = None
        self.processing_errors: List[str] = []
    
    def load_data(self, file_path: Optional[str] = None, uploaded_file=None) -> bool:
        """
        Load survey data from file or uploaded file object.
        
        Args:
            file_path (str, optional): Path to data file
            uploaded_file: Streamlit uploaded file object
        
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            if uploaded_file is not None:
                from data_loader import load_survey_data_from_upload
                self.raw_data = load_survey_data_from_upload(uploaded_file)
            elif file_path:
                self.raw_data = load_survey_data(file_path)
            else:
                self.processing_errors.append("No file path or uploaded file provided")
                return False
            
            # Auto-detect country column
            self._detect_country_column()
            
            # Validate loaded data
            validation = validate_loaded_data(self.raw_data)
            if not validation['valid']:
                self.processing_errors.extend(validation['issues'])
                return False
            
            return True
            
        except Exception as e:
            self.processing_errors.append(f"Error loading data: {str(e)}")
            return False
    
    def _detect_country_column(self):
        """Auto-detect the country/nationality column name."""
        if self.raw_data is None:
            return
        
        country_column_names = ['What is your home country? *', 'What is your home country?', 
                               'Country', 'Home Country', 'Nationality']
        
        for col in country_column_names:
            if col in self.raw_data.columns:
                self.country_column = col
                return
        
        # If not found, check for columns containing 'country'
        for col in self.raw_data.columns:
            if 'country' in col.lower() and 'points' not in col.lower() and 'feedback' not in col.lower():
                self.country_column = col
                return
    
    def clean_data(self, 
                   normalize_countries: bool = True,
                   normalize_ratings: bool = True,
                   remove_empty: bool = True,
                   remove_tests: bool = True) -> bool:
        """
        Clean the loaded survey data.
        
        Args:
            normalize_countries (bool): Normalize country names
            normalize_ratings (bool): Normalize rating scales
            remove_empty (bool): Remove mostly empty rows
            remove_tests (bool): Remove test responses
        
        Returns:
            bool: True if cleaning successful, False otherwise
        """
        if self.raw_data is None:
            self.processing_errors.append("No data loaded. Call load_data() first.")
            return False
        
        try:
            self.cleaned_data, self.cleaning_stats = clean_survey_data(
                self.raw_data,
                normalize_countries=normalize_countries,
                normalize_ratings=normalize_ratings,
                remove_empty=remove_empty,
                remove_tests=remove_tests,
                country_column=self.country_column
            )
            
            # Update country column if it was renamed
            self._detect_country_column()
            
            return True
            
        except Exception as e:
            self.processing_errors.append(f"Error cleaning data: {str(e)}")
            return False
    
    def get_countries(self) -> List[str]:
        """
        Get list of unique countries in the dataset.
        
        Returns:
            List[str]: Sorted list of unique countries
        """
        if self.cleaned_data is None or self.country_column is None:
            return []
        
        if self.country_column not in self.cleaned_data.columns:
            return []
        
        countries = self.cleaned_data[self.country_column].dropna().unique().tolist()
        return sorted([c for c in countries if str(c).strip() != ''])
    
    def get_nationality_counts(self) -> pd.Series:
        """
        Get count of responses by nationality.
        
        Returns:
            pd.Series: Series with nationality as index and count as values
        """
        if self.cleaned_data is None or self.country_column is None:
            return pd.Series(dtype=int)
        
        if self.country_column not in self.cleaned_data.columns:
            return pd.Series(dtype=int)
        
        return self.cleaned_data[self.country_column].value_counts()
    
    def calculate_nationality_percentages(self, column: str, 
                                         exclude_null: bool = True) -> pd.DataFrame:
        """
        Calculate percentage breakdown by nationality for a given column.
        
        Args:
            column (str): Column name to analyze
            exclude_null (bool): Whether to exclude null values from calculations
        
        Returns:
            pd.DataFrame: DataFrame with nationality, value, count, and percentage
        """
        if self.cleaned_data is None or self.country_column is None:
            return pd.DataFrame()
        
        if column not in self.cleaned_data.columns:
            return pd.DataFrame()
        
        # Group by country and column value
        grouped = self.cleaned_data.groupby([self.country_column, column]).size().reset_index(name='count')
        
        # Calculate percentages
        country_totals = self.cleaned_data.groupby(self.country_column).size()
        
        result_data = []
        for _, row in grouped.iterrows():
            country = row[self.country_column]
            value = row[column]
            
            if exclude_null and pd.isna(value):
                continue
            
            country_total = country_totals.get(country, 0)
            percentage = (row['count'] / country_total * 100) if country_total > 0 else 0
            
            result_data.append({
                'Nationality': country,
                'Value': value,
                'Count': row['count'],
                'Percentage': round(percentage, 2)
            })
        
        return pd.DataFrame(result_data)
    
    def calculate_rating_breakdown(self, rating_column: str) -> pd.DataFrame:
        """
        Calculate percentage breakdown by nationality for rating-type questions.
        
        Args:
            rating_column (str): Column name containing rating responses
        
        Returns:
            pd.DataFrame: DataFrame with nationality, rating, count, and percentage
        """
        return self.calculate_nationality_percentages(rating_column, exclude_null=True)
    
    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of the processed data.
        
        Returns:
            Dict: Summary statistics including row counts, column counts, countries, etc.
        """
        summary = {
            'raw_rows': len(self.raw_data) if self.raw_data is not None else 0,
            'cleaned_rows': len(self.cleaned_data) if self.cleaned_data is not None else 0,
            'columns': len(self.cleaned_data.columns) if self.cleaned_data is not None else 0,
            'countries': self.get_countries(),
            'country_counts': self.get_nationality_counts().to_dict() if self.country_column else {},
            'errors': self.processing_errors.copy(),
            'cleaning_stats': self.cleaning_stats
        }
        
        return summary
    
    def filter_by_countries(self, countries: List[str]) -> pd.DataFrame:
        """
        Filter data to include only specified countries.
        
        Args:
            countries (List[str]): List of country names to include
        
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        if self.cleaned_data is None or self.country_column is None:
            return pd.DataFrame()
        
        if self.country_column not in self.cleaned_data.columns:
            return pd.DataFrame()
        
        return self.cleaned_data[self.cleaned_data[self.country_column].isin(countries)].copy()
    
    def get_question_columns(self, exclude_meta: bool = True) -> List[str]:
        """
        Get list of question columns (excluding Points and Feedback columns).
        
        Args:
            exclude_meta (bool): Whether to exclude Points/Feedback columns
        
        Returns:
            List[str]: List of question column names
        """
        if self.cleaned_data is None:
            return []
        
        if exclude_meta:
            # Exclude columns with 'Points' or 'Feedback' in name
            question_cols = [col for col in self.cleaned_data.columns 
                           if 'Points' not in col and 'Feedback' not in col 
                           and 'Id' not in col and 'Start time' not in col 
                           and 'Completion time' not in col and 'Total points' not in col
                           and 'Quiz feedback' not in col and 'Grade posted time' not in col]
            return question_cols
        
        return list(self.cleaned_data.columns)
    
    def process_pipeline(self, file_path: Optional[str] = None, uploaded_file=None) -> bool:
        """
        Complete processing pipeline: load and clean data.
        
        Args:
            file_path (str, optional): Path to data file
            uploaded_file: Streamlit uploaded file object
        
        Returns:
            bool: True if processing successful, False otherwise
        """
        # Load data
        if not self.load_data(file_path, uploaded_file):
            return False
        
        # Clean data
        if not self.clean_data():
            return False
        
        return True


# Convenience functions for quick processing
def process_survey_data(file_path: Optional[str] = None, uploaded_file=None) -> SurveyDataProcessor:
    """
    Quick function to process survey data.
    
    Args:
        file_path (str, optional): Path to data file
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        SurveyDataProcessor: Processed data processor object
    """
    processor = SurveyDataProcessor()
    processor.process_pipeline(file_path, uploaded_file)
    return processor


if __name__ == "__main__":
    # Test the data processor
    print("Data Processor Module")
    print("=" * 50)
    
    # Test with sample file
    sample_file = "Assimilation into British University academic culture.csv"
    import os
    
    if os.path.exists(sample_file):
        try:
            processor = process_survey_data(file_path=sample_file)
            
            print(f"\nProcessing Summary:")
            summary = processor.get_data_summary()
            print(f"  Raw rows: {summary['raw_rows']}")
            print(f"  Cleaned rows: {summary['cleaned_rows']}")
            print(f"  Columns: {summary['columns']}")
            print(f"  Countries: {summary['countries']}")
            
            if processor.country_column:
                print(f"\nCountry distribution:")
                counts = processor.get_nationality_counts()
                print(counts)
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Sample file not found: {sample_file}")

