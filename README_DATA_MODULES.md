# Data Processing Modules
## Days 1-7 Implementation

This directory contains the core data processing modules for the Interactive Data Analysis and Visualization Application.

---

## Files Created

### 1. `data_loader.py` (Days 1-2)
**Purpose**: Data loading module for Excel/CSV file import

**Key Functions**:
- `load_excel_file()`: Load Excel (.xlsx) files
- `load_csv_file()`: Load CSV files
- `load_survey_data()`: Auto-detect and load file type
- `load_survey_data_from_upload()`: Load from Streamlit uploaded file
- `validate_loaded_data()`: Basic data validation

**Usage Example**:
```python
from data_loader import load_survey_data, validate_loaded_data

# Load data
df = load_survey_data("Assimilation into British University academic culture.csv")

# Validate
validation = validate_loaded_data(df)
print(validation)
```

---

### 2. `data_cleaner.py` (Days 3-4)
**Purpose**: Data cleaning functions to handle missing values and inconsistencies

**Key Functions**:
- `normalize_country_names()`: Standardize country names
- `clean_rating_responses()`: Normalize rating scales
- `remove_empty_rows()`: Remove mostly empty rows
- `remove_test_responses()`: Remove invalid/test responses
- `clean_column_names()`: Normalize column names
- `clean_survey_data()`: Main cleaning function with all operations

**Usage Example**:
```python
from data_cleaner import clean_survey_data

# Clean data
cleaned_df, stats = clean_survey_data(df, 
                                     normalize_countries=True,
                                     normalize_ratings=True,
                                     remove_empty=True,
                                     remove_tests=True)

print(f"Removed {stats['rows_removed']} rows")
print(f"Operations: {stats['operations_performed']}")
```

---

### 3. `data_processor.py` (Days 5-7)
**Purpose**: Main data pipeline combining loading and cleaning

**Key Class**: `SurveyDataProcessor`

**Key Methods**:
- `load_data()`: Load survey data from file or upload
- `clean_data()`: Clean the loaded data
- `process_pipeline()`: Complete load + clean pipeline
- `get_countries()`: Get list of unique countries
- `get_nationality_counts()`: Count responses by nationality
- `calculate_nationality_percentages()`: Calculate percentage breakdowns
- `filter_by_countries()`: Filter data by countries
- `get_data_summary()`: Get processing summary statistics

**Usage Example**:
```python
from data_processor import SurveyDataProcessor

# Create processor
processor = SurveyDataProcessor()

# Process data
success = processor.process_pipeline(file_path="data.csv")

if success:
    # Get summary
    summary = processor.get_data_summary()
    print(f"Countries: {summary['countries']}")
    print(f"Total responses: {summary['cleaned_rows']}")
    
    # Get nationality counts
    counts = processor.get_nationality_counts()
    print(counts)
    
    # Calculate percentages for a rating column
    percentages = processor.calculate_nationality_percentages(
        "How important were the following factors in choosing Northumbria as a place to study? .Quality of education in the UK"
    )
    print(percentages)
```

**Quick Function**:
```python
from data_processor import process_survey_data

# One-line processing
processor = process_survey_data(file_path="data.csv")
```

---

### 4. `DATA_DICTIONARY.md` (Day 7)
**Purpose**: Complete documentation of all data fields and structures

**Contents**:
- Overview of dataset structure
- Description of all column categories
- Detailed field descriptions with:
  - Column names
  - Data types
  - Expected values
  - Rating scales
- Data quality notes
- Calculation guidelines
- Analysis dimensions

---

### 5. `requirements.txt`
**Purpose**: Python package dependencies

**Dependencies**:
- pandas>=1.5.0
- streamlit>=1.28.0
- plotly>=5.17.0
- openpyxl>=3.1.0
- numpy>=1.24.0

**Installation**:
```bash
pip install -r requirements.txt
```

---

## Data Structure

### Processing Flow

```
Raw Data File (Excel/CSV)
    ↓
[Data Loader]
    ↓
Raw DataFrame
    ↓
[Data Cleaner]
    ↓
Cleaned DataFrame
    ↓
[Data Processor]
    ↓
Structured Data Ready for Visualization
```

### Key Data Fields

**Primary Grouping Variable**:
- Country/Nationality (`What is your home country? *`)

**Demographic Fields**:
- Institution type
- First language
- Programme type
- Programme duration

**Rating Fields** (Multiple types):
- Importance ratings: Not at all → Extremely
- Agreement ratings: Strongly disagree → Strongly agree
- Difficulty ratings: Not at all → Extremely
- English proficiency: Poor → Excellent
- Satisfaction ratings: Very dissatisfied → Very satisfied

---

## Testing

Each module includes a `__main__` block for basic testing:

```bash
# Test data loader
python data_loader.py

# Test data cleaner
python data_cleaner.py

# Test data processor
python data_processor.py
```

---

## Next Steps

These modules form the foundation for:
- **Day 8-9**: Streamlit interface development
- **Day 10-12**: Visualization components
- **Day 13-14**: Interactive filtering and comparison tools
- **Day 15+**: Dashboard integration and deployment

---

## Notes

- All modules follow PEP 8 style guidelines
- Functions include comprehensive docstrings
- Error handling is implemented throughout
- Modules are designed to work independently or together
- Data processing is optimized for survey analysis workflows

---

## Support

For questions or issues, refer to:
- `DATA_DICTIONARY.md` for field descriptions
- Individual module docstrings for function details
- Project supervisor for data-specific questions

