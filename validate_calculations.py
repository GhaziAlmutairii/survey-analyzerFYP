"""
Validation Script
=================
Validates percentage calculations against manual Excel calculations.

This script:
- Loads and processes survey data
- Calculates percentages using the code
- Compares with expected results from Excel
- Generates validation report
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from data_processor import SurveyDataProcessor
from calculations import calculate_nationality_percentage, calculate_country_counts
import os


class ValidationReport:
    """
    Class to generate and store validation results.
    """
    
    def __init__(self):
        self.results: List[Dict] = []
        self.total_tests: int = 0
        self.passed_tests: int = 0
        self.failed_tests: int = 0
    
    def add_result(self, test_name: str, expected: float, actual: float, 
                   tolerance: float = 0.01, passed: bool = None):
        """
        Add a validation test result.
        
        Args:
            test_name (str): Name of the test
            expected (float): Expected value
            actual (float): Actual calculated value
            tolerance (float): Allowed difference. Default 0.01 (0.01%)
            passed (bool, optional): Whether test passed. If None, calculates automatically
        """
        if passed is None:
            passed = abs(expected - actual) <= tolerance
        
        difference = abs(expected - actual)
        
        self.results.append({
            'test_name': test_name,
            'expected': expected,
            'actual': actual,
            'difference': difference,
            'tolerance': tolerance,
            'passed': passed
        })
        
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"Failed: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        print("\n" + "-" * 70)
        
        if self.results:
            df = pd.DataFrame(self.results)
            print("\nTest Results:")
            print(df.to_string(index=False))
        
        print("\n" + "=" * 70)


def validate_country_counts(processor: SurveyDataProcessor, 
                           expected_counts: Dict[str, int],
                           total_responses: int) -> ValidationReport:
    """
    Validate country count calculations.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        expected_counts (Dict[str, int]): Expected counts by country from Excel
        total_responses (int): Expected total number of responses
    
    Returns:
        ValidationReport: Validation results
    """
    report = ValidationReport()
    
    if processor.cleaned_data is None or processor.country_column is None:
        return report
    
    # Calculate actual counts
    actual_counts = calculate_country_counts(
        processor.cleaned_data,
        processor.country_column
    )
    
    # Validate total count
    actual_total = len(processor.cleaned_data)
    report.add_result(
        "Total Responses",
        total_responses,
        actual_total,
        tolerance=1.0  # Allow 1 response difference
    )
    
    # Validate each country count
    actual_counts_dict = dict(zip(actual_counts['Nationality'], actual_counts['Count']))
    
    for country, expected_count in expected_counts.items():
        actual_count = actual_counts_dict.get(country, 0)
        report.add_result(
            f"Count - {country}",
            expected_count,
            actual_count,
            tolerance=1.0  # Allow 1 response difference
        )
        
        # Validate percentages
        expected_pct = (expected_count / total_responses) * 100
        actual_pct = actual_counts[actual_counts['Nationality'] == country]['Percentage'].values
        if len(actual_pct) > 0:
            report.add_result(
                f"Percentage - {country}",
                expected_pct,
                actual_pct[0],
                tolerance=0.1  # Allow 0.1% difference
            )
    
    return report


def validate_percentage_calculation(processor: SurveyDataProcessor,
                                   question_column: str,
                                   country: str,
                                   value: str,
                                   expected_percentage: float,
                                   tolerance: float = 0.1) -> Tuple[bool, float]:
    """
    Validate percentage calculation for a specific question, country, and value.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        question_column (str): Column name to analyze
        country (str): Country to check
        value (str): Response value to check
        expected_percentage (float): Expected percentage from Excel
        tolerance (float): Allowed difference. Default 0.1 (0.1%)
    
    Returns:
        Tuple[bool, float]: (passed, actual_percentage)
    """
    if processor.cleaned_data is None or processor.country_column is None:
        return False, 0.0
    
    if question_column not in processor.cleaned_data.columns:
        return False, 0.0
    
    # Calculate actual percentage
    breakdown = calculate_nationality_percentage(
        processor.cleaned_data,
        processor.country_column,
        question_column,
        exclude_null=True
    )
    
    # Filter for specific country and value
    filtered = breakdown[
        (breakdown['Nationality'] == country) & 
        (breakdown['Value'] == value)
    ]
    
    if filtered.empty:
        return False, 0.0
    
    actual_percentage = filtered['Percentage'].values[0]
    passed = abs(expected_percentage - actual_percentage) <= tolerance
    
    return passed, actual_percentage


def validate_manual_excel_comparison(processor: SurveyDataProcessor,
                                    test_cases: List[Dict]) -> ValidationReport:
    """
    Validate multiple test cases from manual Excel calculations.
    
    Args:
        processor (SurveyDataProcessor): Processed survey data processor
        test_cases (List[Dict]): List of test cases with keys:
            - question: Column name
            - country: Country name
            - value: Response value
            - expected_percentage: Expected percentage
            - tolerance: Optional tolerance (default 0.1)
    
    Returns:
        ValidationReport: Validation results
    """
    report = ValidationReport()
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case.get('question')
        country = test_case.get('country')
        value = test_case.get('value')
        expected_pct = test_case.get('expected_percentage')
        tolerance = test_case.get('tolerance', 0.1)
        
        passed, actual_pct = validate_percentage_calculation(
            processor,
            question,
            country,
            value,
            expected_pct,
            tolerance
        )
        
        test_name = f"Test {i}: {country} - {question} - {value}"
        report.add_result(
            test_name,
            expected_pct,
            actual_pct,
            tolerance,
            passed
        )
    
    return report


def manual_validation_instructions():
    """
    Print instructions for manual Excel validation.
    """
    print("\n" + "=" * 70)
    print("MANUAL VALIDATION INSTRUCTIONS")
    print("=" * 70)
    print("\nTo validate calculations against Excel:")
    print("\n1. Open Excel file: 'Assimilation into British University academic culture.xlsx'")
    print("\n2. For each test case:")
    print("   a. Identify the question column (e.g., 'What is your home country? *')")
    print("   b. Filter by country (e.g., India)")
    print("   c. Count responses for a specific value")
    print("   d. Calculate percentage: (Count / Total for country) × 100")
    print("\n3. Example - Test country distribution:")
    print("   - Count all responses from 'India'")
    print("   - Count total responses")
    print("   - Percentage = (India count / Total) × 100")
    print("\n4. Compare with code output")
    print("\n5. They should match (within 0.1% tolerance)")
    print("\n" + "=" * 70)


def run_validation(file_path: str = None):
    """
    Run validation tests.
    
    Args:
        file_path (str, optional): Path to data file. If None, uses default
    """
    print("Validation Script")
    print("=" * 70)
    
    # Print instructions
    manual_validation_instructions()
    
    # Load and process data
    if file_path is None:
        file_path = "Assimilation into British University academic culture.csv"
    
    if not os.path.exists(file_path):
        print(f"\nError: File not found: {file_path}")
        return
    
    print(f"\nLoading data from: {file_path}")
    processor = SurveyDataProcessor()
    success = processor.process_pipeline(file_path=file_path)
    
    if not success:
        print("\nError: Failed to process data")
        print("Errors:", processor.processing_errors)
        return
    
    print("\nData loaded successfully!")
    summary = processor.get_data_summary()
    print(f"Total responses: {summary['cleaned_rows']}")
    print(f"Countries found: {summary['countries']}")
    
    # Validate country counts (basic test)
    print("\n" + "-" * 70)
    print("Validating Country Counts...")
    print("-" * 70)
    
    # Get actual country counts for reference
    country_counts = processor.get_nationality_counts()
    print("\nActual Country Counts (for reference):")
    print(country_counts)
    
    # Manual validation - you need to fill in expected values from Excel
    print("\n" + "-" * 70)
    print("MANUAL VALIDATION REQUIRED")
    print("-" * 70)
    print("\nPlease perform the following steps:")
    print("\n1. Open Excel file and count responses by country")
    print("2. Create test_cases list with expected percentages")
    print("3. Run validate_manual_excel_comparison() with your test cases")
    print("\nExample test cases format:")
    print("""
test_cases = [
    {
        'question': 'What is your home country? *',
        'country': 'India',
        'value': 'India',
        'expected_percentage': 45.5,  # From Excel
        'tolerance': 0.1
    },
    {
        'question': 'How important were the following factors...Quality of education in the UK',
        'country': 'India',
        'value': 'Extremely',
        'expected_percentage': 60.0,  # From Excel
        'tolerance': 0.1
    }
]
    """)
    
    # Example validation (commented out - uncomment and fill with actual values)
    """
    # Example: Validate country distribution
    expected_counts = {
        'India': 25,      # Fill from Excel
        'Nigeria': 20,    # Fill from Excel
        'Myanmar': 5      # Fill from Excel
    }
    
    report = validate_country_counts(
        processor,
        expected_counts,
        total_responses=64  # Fill from Excel
    )
    report.print_report()
    
    # Example: Validate specific question percentages
    test_cases = [
        {
            'question': 'How important were the following factors...Quality of education in the UK',
            'country': 'India',
            'value': 'Extremely',
            'expected_percentage': 60.0,  # Fill from Excel
            'tolerance': 0.1
        }
    ]
    
    report2 = validate_manual_excel_comparison(processor, test_cases)
    report2.print_report()
    """
    
    print("\n" + "=" * 70)
    print("Validation script completed!")
    print("=" * 70)


if __name__ == "__main__":
    run_validation()

