"""
Data Loading Module
===================
Handles loading and initial processing of Excel/CSV survey data files.

This module provides functionality to:
- Load Excel (.xlsx) and CSV files
- Handle file format detection
- Provide initial data validation
- Return pandas DataFrames for further processing
"""

import pandas as pd
import os
from typing import Union, Optional
import streamlit as st


def load_excel_file(file_path: str, sheet_name: Optional[Union[str, int]] = 0) -> pd.DataFrame:
    """
    Load an Excel file and return a pandas DataFrame.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (str or int, optional): Name or index of sheet to load. Defaults to 0 (first sheet)
    
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame
    
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file cannot be read as Excel
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        return df
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {str(e)}")


def load_csv_file(file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
    """
    Load a CSV file and return a pandas DataFrame.
    
    Args:
        file_path (str): Path to the CSV file
        encoding (str): File encoding. Defaults to 'utf-8'
    
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame
    
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file cannot be read as CSV
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Try UTF-8 first, fall back to latin-1 if needed
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        return df
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")


def load_survey_data(file_path: str, sheet_name: Optional[Union[str, int]] = None) -> pd.DataFrame:
    """
    Automatically detect file type and load survey data.
    Supports both Excel (.xlsx) and CSV files.
    
    Args:
        file_path (str): Path to the data file
        sheet_name (str or int, optional): Sheet name/index for Excel files. Defaults to first sheet
    
    Returns:
        pd.DataFrame: Loaded survey data
    
    Raises:
        ValueError: If file format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.xlsx':
        return load_excel_file(file_path, sheet_name)
    elif file_extension == '.csv':
        return load_csv_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: .xlsx, .csv")


def load_survey_data_from_upload(uploaded_file) -> pd.DataFrame:
    """
    Load survey data from a Streamlit uploaded file object.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        pd.DataFrame: Loaded survey data
    
    Raises:
        ValueError: If file format is not supported
    """
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    try:
        if file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_extension == '.csv':
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Supported: .xlsx, .csv")
        
        return df
    except Exception as e:
        raise ValueError(f"Error reading uploaded file: {str(e)}")


def validate_loaded_data(df: pd.DataFrame) -> dict:
    """
    Perform basic validation on loaded data.
    
    Args:
        df (pd.DataFrame): Data to validate
    
    Returns:
        dict: Validation results with keys:
            - 'valid' (bool): Whether data passed validation
            - 'row_count' (int): Number of rows
            - 'column_count' (int): Number of columns
            - 'missing_columns' (list): List of expected columns that are missing
            - 'issues' (list): List of validation issues found
    """
    validation_result = {
        'valid': True,
        'row_count': len(df),
        'column_count': len(df.columns),
        'missing_columns': [],
        'issues': []
    }
    
    # Check if dataframe is empty
    if df.empty:
        validation_result['valid'] = False
        validation_result['issues'].append("DataFrame is empty")
        return validation_result
    
    # Check for country column (key demographic field)
    country_column_names = ['What is your home country? *', 'What is your home country?', 
                           'Country', 'Home Country', 'Nationality']
    country_col = None
    for col in country_column_names:
        if col in df.columns:
            country_col = col
            break
    
    if country_col is None:
        validation_result['issues'].append("No country/nationality column found. Expected one of: " + 
                                          str(country_column_names))
        # Don't fail validation, but note the issue
    
    # Check for minimum row count (at least 1 data row after header)
    if validation_result['row_count'] < 1:
        validation_result['valid'] = False
        validation_result['issues'].append("No data rows found")
    
    # Check for excessive missing values in key columns
    if country_col and country_col in df.columns:
        missing_country_pct = df[country_col].isna().sum() / len(df) * 100
        if missing_country_pct > 50:
            validation_result['issues'].append(f"High percentage ({missing_country_pct:.1f}%) of missing country data")
    
    return validation_result


if __name__ == "__main__":
    # Test the data loader
    print("Data Loading Module")
    print("=" * 50)
    
    # Test with sample file if exists
    sample_file = "Assimilation into British University academic culture.csv"
    if os.path.exists(sample_file):
        try:
            df = load_survey_data(sample_file)
            print(f"\nSuccessfully loaded: {sample_file}")
            print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Run validation
            validation = validate_loaded_data(df)
            print(f"\nValidation Results:")
            print(f"  Valid: {validation['valid']}")
            print(f"  Issues: {validation['issues']}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Sample file not found: {sample_file}")

