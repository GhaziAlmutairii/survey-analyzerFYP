# Calculation and Comparison Modules
## Days 1-7 Implementation

This document describes the percentage calculation, validation, and comparison modules created for the Interactive Data Analysis and Visualization Application.

---

## Files Created

### 1. `calculations.py` (Days 1-3)
**Purpose**: Percentage calculation functions for nationality-based analysis

**Key Functions**:

#### Core Calculation Functions
- `calculate_nationality_percentage()`: Calculate percentage breakdown by nationality for any column
- `calculate_overall_percentage()`: Calculate overall percentage breakdown (across all nationalities)
- `calculate_country_counts()`: Calculate count and percentage of responses by country
- `calculate_country_statistics()`: Calculate statistical summaries (mean, median, std, count) by country

#### Advanced Calculation Functions
- `calculate_rating_breakdown_by_country()`: Calculate rating breakdown using SurveyDataProcessor
- `calculate_multiple_ratings_comparison()`: Compare multiple rating columns across countries
- `calculate_response_distribution()`: Create pivot table distribution (counts or percentages)
- `calculate_importance_factor_ranking()`: Rank importance factors by percentage selecting 'Extremely' or 'Very'
- `calculate_cross_tabulation()`: Create cross-tabulation between two categorical variables
- `calculate_percentage_summary()`: Comprehensive summary with by-country and overall breakdowns

**Usage Example**:
```python
from calculations import calculate_nationality_percentage
from data_processor import process_survey_data

# Load data
processor = process_survey_data(file_path="data.csv")

# Calculate percentage breakdown
breakdown = calculate_nationality_percentage(
    processor.cleaned_data,
    processor.country_column,
    "How important were the following factors...Quality of education in the UK",
    exclude_null=True,
    exclude_not_applicable=True
)

print(breakdown)
```

---

### 2. `validate_calculations.py` (Days 4-5)
**Purpose**: Validation script to compare code results with manual Excel calculations

**Key Features**:
- Manual validation instructions
- Automated comparison functions
- Validation report generation
- Test case management

**Key Classes**:
- `ValidationReport`: Stores and reports validation test results

**Key Functions**:
- `validate_country_counts()`: Validate country count calculations
- `validate_percentage_calculation()`: Validate specific percentage calculations
- `validate_manual_excel_comparison()`: Validate multiple test cases
- `run_validation()`: Main validation script with instructions
- `manual_validation_instructions()`: Print manual validation steps

**Usage Example**:
```python
from validate_calculations import run_validation, validate_country_counts
from data_processor import process_survey_data

# Run validation script
run_validation("data.csv")

# Or validate specific counts
processor = process_survey_data(file_path="data.csv")
expected_counts = {
    'India': 25,
    'Nigeria': 20,
    'Myanmar': 5
}

report = validate_country_counts(
    processor,
    expected_counts,
    total_responses=64
)
report.print_report()
```

**Manual Validation Steps**:
1. Open Excel file: `Assimilation into British University academic culture.xlsx`
2. For each test case:
   - Identify the question column
   - Filter by country (e.g., India)
   - Count responses for a specific value
   - Calculate percentage: (Count / Total for country) × 100
3. Compare with code output (should match within 0.1% tolerance)

---

### 3. `comparisons.py` (Days 6-7)
**Purpose**: Advanced comparison functions across multiple nationalities and questions

**Key Functions**:

#### Basic Comparison Functions
- `compare_nationalities()`: Compare responses across multiple nationalities (pivot table format)
- `compare_side_by_side()`: Create side-by-side comparison table with counts and percentages
- `compare_rating_scales_across_countries()`: Compare rating scales with proper ordering

#### Difference and Statistical Functions
- `calculate_difference_between_countries()`: Calculate percentage difference between two countries
- `calculate_statistical_significance()`: Chi-square test for statistical significance
- `calculate_ranking_comparison()`: Rank countries by percentage for a specific value

#### Advanced Analysis Functions
- `compare_multiple_questions()`: Compare multiple questions across countries
- `generate_comparison_report()`: Generate formatted text report comparing countries

**Usage Example**:
```python
from comparisons import compare_side_by_side, calculate_difference_between_countries
from data_processor import process_survey_data

# Load data
processor = process_survey_data(file_path="data.csv")

# Side-by-side comparison
countries = ['India', 'Nigeria', 'Myanmar']
comparison = compare_side_by_side(
    processor,
    "How important were the following factors...Quality of education in the UK",
    countries,
    show_counts=True
)
print(comparison)

# Calculate difference between two countries
diff = calculate_difference_between_countries(
    processor,
    "How important were the following factors...Quality of education in the UK",
    'India',
    'Nigeria',
    'Extremely'
)
print(f"Difference: {diff['difference']}%")

# Statistical significance test
stats_result = calculate_statistical_significance(
    processor,
    "How important were the following factors...Quality of education in the UK",
    'India',
    'Nigeria',
    'Extremely'
)
print(f"P-value: {stats_result['p_value']}, Significant: {stats_result['significant']}")
```

---

## Module Dependencies

### Required Packages
All modules require:
- `pandas>=1.5.0`
- `numpy>=1.24.0`
- `scipy>=1.10.0` (for statistical tests in comparisons.py)

### Internal Dependencies
- `data_processor.py`: SurveyDataProcessor class
- `data_loader.py`: Data loading functions
- `data_cleaner.py`: Data cleaning functions

---

## Validation Workflow

### Step 1: Manual Excel Validation
1. Open Excel file
2. Count responses by country for each question
3. Calculate percentages manually
4. Record expected values

### Step 2: Code Validation
1. Load data using `process_survey_data()`
2. Calculate percentages using `calculate_nationality_percentage()`
3. Compare with manual calculations
4. Use `validate_calculations.py` for automated comparison

### Step 3: Verification
- Check that percentages match (within 0.1% tolerance)
- Verify country counts match Excel totals
- Validate percentage calculations for key questions

---

## Calculation Examples

### Example 1: Country Distribution
```python
from calculations import calculate_country_counts
from data_processor import process_survey_data

processor = process_survey_data(file_path="data.csv")
country_counts = calculate_country_counts(
    processor.cleaned_data,
    processor.country_column
)
print(country_counts)
```

### Example 2: Importance Factor Analysis
```python
from calculations import calculate_nationality_percentage

breakdown = calculate_nationality_percentage(
    processor.cleaned_data,
    processor.country_column,
    "How important were the following factors...Quality of education in the UK",
    exclude_null=True,
    exclude_not_applicable=True
)

# Filter for high importance
high_importance = breakdown[breakdown['Value'].isin(['Extremely', 'Very'])]
print(high_importance)
```

### Example 3: Cross-Nationality Comparison
```python
from comparisons import compare_nationalities, generate_comparison_report

# Compare multiple countries
comparison = compare_nationalities(
    processor,
    "How important were the following factors...Quality of education in the UK",
    ['India', 'Nigeria', 'Myanmar'],
    exclude_not_applicable=True
)
print(comparison)

# Generate report
report = generate_comparison_report(
    processor,
    "How important were the following factors...Quality of education in the UK",
    ['India', 'Nigeria']
)
print(report)
```

---

## Testing

Each module includes a `__main__` block for basic testing:

```bash
# Test calculations
python calculations.py

# Test validation
python validate_calculations.py

# Test comparisons
python comparisons.py
```

---

## Notes

### Percentage Calculation Accuracy
- Percentages are rounded to 2 decimal places
- Calculations exclude null values by default
- 'Not applicable' can be excluded or included based on parameter
- Total percentages per country should sum to approximately 100%

### Statistical Tests
- Chi-square test in `calculate_statistical_significance()` requires sufficient sample size
- P-value < 0.05 indicates statistical significance
- Degrees of freedom calculated automatically

### Performance Considerations
- Calculations are optimized for typical survey dataset sizes (50-500 responses)
- Large datasets may require additional optimization
- Memory usage scales with number of countries and unique values

---

## Next Steps

These modules form the foundation for:
- **Day 8-9**: Streamlit interface development
- **Day 10-12**: Visualization components using Plotly
- **Day 13-14**: Interactive filtering and comparison tools
- **Day 15+**: Dashboard integration and deployment

---

## Support

For questions about:
- **Calculations**: See function docstrings in `calculations.py`
- **Validation**: See `validate_calculations.py` and manual validation instructions
- **Comparisons**: See function docstrings in `comparisons.py`
- **Data Structure**: See `DATA_DICTIONARY.md`

