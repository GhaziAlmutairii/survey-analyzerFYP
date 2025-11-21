# Data Dictionary
## Assimilation into British University Academic Culture Survey

### Overview
This document describes the structure, fields, and data types of the international student survey data used in the Interactive Data Analysis and Visualization Application.

---

## File Information

- **File Name**: `Assimilation into British University academic culture.csv`
- **File Type**: CSV (Comma-Separated Values)
- **Source**: Primary survey data from international students
- **Total Columns**: ~200+ columns (including Points and Feedback columns for each question)
- **Data Rows**: Variable (typically 50-100+ responses)

---

## Column Categories

The dataset contains several categories of columns:

1. **Metadata Columns**: System-generated fields (ID, timestamps, points, feedback)
2. **Demographic Columns**: Student background information
3. **Education Background Columns**: Previous educational experience
4. **Language Columns**: English language proficiency ratings
5. **Choice/Preference Columns**: Factors influencing university choice
6. **Rating Columns**: Likert-scale responses for various statements
7. **Difficulty Columns**: Educational activity difficulty ratings
8. **Open-ended Columns**: Text responses and comments

---

## Core Demographic Fields

### Country/Nationality
- **Column Name**: `What is your home country? *`
- **Type**: Categorical (String)
- **Description**: Student's home country/nationality
- **Expected Values**: 
  - India
  - Nigeria
  - Myanmar
  - Kenya
  - Sri Lanka
  - Bangladesh
  - Pakistan
  - Iran
  - Romania
  - Czech Republic
  - Cyprus
  - Bahrain
- **Required**: Yes
- **Notes**: Primary grouping variable for nationality-based analysis

### Institution Type
- **Column Name**: `Which type of institution did you attend before coming to Northumbria?`
- **Type**: Categorical
- **Expected Values**: 
  - University
  - College
  - Other

### First Time Studying Overseas
- **Column Name**: `Is it your first time studying overseas? (if yes please go to question 9)`
- **Type**: Boolean (Yes/No)
- **Description**: Whether this is the student's first international study experience

### Previous Study Countries
- **Column Name**: `If you answered no to question 7 please detail the country or countries you have studied in and the qualifications gained.`
- **Type**: Text (Free-form)
- **Description**: Details of previous international study experience

### First Language
- **Column Name**: `What is your first language`
- **Type**: Categorical (String)
- **Description**: Student's native/first language
- **Examples**: English, Bengali, Tamil, Telugu, Yoruba, Sinhala, etc.

---

## Education Background Fields

### TOEFL/IELTS Test
- **Column Name**: `Have you taken TOEFL or IELTS test?`
- **Type**: Boolean (Yes/No)
- **Description**: Whether student took English proficiency test

### MSc Programme
- **Column Name**: `Which MSc programme are you studying at the moment?`
- **Type**: Categorical
- **Expected Values**: 
  - Computer Science
  - Computer Science with Advanced Practice
  - Information Science (Data Analytics)
  - Data Science
  - Data Science with Advanced Practice
  - Advanced Computer Science
  - And variations

### Months Studying at Northumbria
- **Column Name**: `How many months have you been studying at Northumbria?`
- **Type**: Numeric / Text (varies)
- **Description**: Duration of study at Northumbria
- **Examples**: "2", "6 months", "1.5 months", "14 months"

### Programme Duration
- **Column Name**: `How long is your programme`
- **Type**: Categorical
- **Expected Values**: 
  - 12 months
  - 16 months
  - 2 Years

### Previous UK Study
- **Column Name**: `Have you studied at another institution in the UK? if yes, please name the college/university, the programme and level you studied at.`
- **Type**: Text (Free-form)
- **Description**: Details of previous UK study experience

### UK First Choice
- **Column Name**: `Was the UK your first choice of a country to study in?`
- **Type**: Boolean (Yes/No)

---

## English Language Proficiency Fields

### Rating Scale
- **Type**: Categorical (Ordinal)
- **Scale**: Poor → Average → Good → Excellent

### Columns
1. **Reading**: `How do you rate your English language ability in the following areas?.Reading`
2. **Writing**: `How do you rate your English language ability in the following areas?.Writing`
3. **Listening**: `How do you rate your English language ability in the following areas?.Listening`
4. **Speaking**: `How do you rate your English language ability in the following areas?.Speaking`
5. **Overall**: `How do you rate your English language ability in the following areas?.Overall`

---

## Choice Factors Fields

### Rating Scale
- **Type**: Categorical (Ordinal)
- **Scale**: Not at all → A little → Moderately → Very → Extremely
- **Special Value**: Not applicable

### Factor Columns (All follow pattern: `How important were the following factors in choosing Northumbria as a place to study? .[Factor Name]`)

1. **Agent's recommendation**
2. **Friend's recommendation**
3. **Teacher's recommendation**
4. **Financial support from your government or employer**
5. **Scholarship from the UK**
6. **Advertisement for study in the UK**
7. **Direct contact from Northumbria**
8. **Internet information**
9. **Family preference**
10. **Own preference**
11. **English speaking country**
12. **Family member has studied in the UK**
13. **Quality of education in the UK**
14. **International recognition of UK qualifications**
15. **Opportunity to get a job in the UK after graduation**
16. **UK culture and lifestyle**
17. **Was not possible to study in home country**
18. **Was not possible to study in another country**
19. **Cost**
20. **Easy to get a visa**

---

## Performance and Satisfaction Fields

### Performance Rating
- **Column Name**: `How well do you think you are doing in your studies.`
- **Type**: Categorical (Ordinal)
- **Scale**: Poor → Average → Good → Excellent

### Family Importance
- **Column Name**: `How important is it to your family for you to do well in your studies?`
- **Type**: Categorical
- **Expected Values**: 
  - Not at all important
  - Somewhat important
  - Neutral
  - Extremely important

### Satisfaction
- **Column Name**: `How satisfied are you with your progress so far in your studies.`
- **Type**: Categorical (Ordinal)
- **Scale**: Very dissatisfied → Somewhat dissatisfied → Neither satisfied nor dissatisfied → Somewhat satisfied → Very satisfied

---

## Agreement Statement Fields

### Rating Scale
- **Type**: Categorical (Ordinal)
- **Scale**: Strongly disagree → Mildly disagree → Neither agree nor disagree → Neutral → Mildly agree → Strongly agree
- **Alternative values**: Disagree, Agree

### Statement Columns (All follow pattern: `How much do you agree or disagree with the following statements.[Statement]`)

1. **My lecturers encourage contact between international and local students**
2. **The content of my modules is useful for my future study or employment**
3. **My lecturers make special efforts to help international students**
4. **Cultural differences are respected at Northumbria**
5. **My lecturers understand the problems of international students**
6. **In my classes there is the opportunity for other students to learn about my culture**
7. **I feel included in my classes**
8. **My lecturers understand the cultural differences in learning styles**
9. **My classmates are accepting of cultural differences**
10. **Students from different cultural groups work well with each other in my classes**

### Inclusion Statement
- **Column Name**: `How much do you agree or disagree with the statement, 'I feel included in my class'.`
- **Type**: Same as agreement scale above

---

## Difficulty Rating Fields

### Rating Scale
- **Type**: Categorical (Ordinal)
- **Scale**: Not at all → Slightly (a little) → Moderately → Very → Extremely
- **Special Value**: Not applicable

### Activity Columns (All follow pattern: `How difficult are the following educational activities for you? (if the activity is not relevant select 'not applicable').[Activity]`)

1. **Understanding lecturers**
2. **Writing assignments**
3. **Taking notes in class**
4. **Completing assessments on time**
5. **Working on group activities**
6. **Making presentations in class**
7. **Engaging in online discussions, e.g. Blackboard**
8. **Managing your workload**
9. **Asking questions in class**
10. **Thinking critically**
11. **Expressing yourself (communicating) in English**
12. **Expressing (giving) your opinions to your lecturer**
13. **Studying in a different educational system**
14. **Understanding the referencing requirements at Northumbria (HARVARD)**

---

## Communication Preference Fields

### Column Name
- **Column**: `Outside of class how do you prefer to ask questions of lecturers?`
- **Type**: Multiple choice (semicolon-separated)
- **Expected Values**: 
  - Via email
  - In person
  - Telephone
  - Via Blackboard FAQ
  - Via MS Teams
  - Guidance Tutor meetings
- **Notes**: Can contain multiple values separated by semicolons

---

## Open-Ended Response Fields

### Additional Comments
- **Column Name**: `Is there anything relating to your studies you would like to share? for instance you can elaborate on any of the answers you have provided above.`
- **Type**: Text (Free-form)
- **Description**: Optional open-ended feedback

### Focus Group Interest
- **Column Name**: `If you wish to participate in a focus group later in the academic year to further discuss this project please enter you email address below.`
- **Type**: Text (Email)
- **Description**: Optional email for focus group participation

---

## Metadata Columns

### System Fields
- **Id**: Unique identifier for each response
- **Start time**: Survey start timestamp
- **Completion time**: Survey completion timestamp
- **Total points**: Total points awarded (if quiz-based)
- **Quiz feedback**: Quiz feedback text
- **Grade posted time**: When grade was posted (if applicable)

### Points and Feedback Columns
- **Pattern**: For each question, there are typically three columns:
  1. `[Question Column]` - The actual response
  2. `Points - [Question Column]` - Points awarded for the response
  3. `Feedback - [Question Column]` - Feedback for the response
- **Note**: Points and Feedback columns are typically excluded from analysis

---

## Data Quality Notes

### Missing Values
- Missing values are common in optional fields
- Some questions are conditional (e.g., "if yes, please go to question 9")
- Empty responses should be handled appropriately in analysis

### Data Variations
- Country names may have inconsistent capitalization or spacing
- Rating responses may have trailing spaces or slight variations
- Some numeric fields (like months) may be stored as text with units

### Data Cleaning Considerations
1. Normalize country names to standard format
2. Standardize rating scales across similar questions
3. Handle "Not applicable" responses appropriately
4. Remove test/empty responses before analysis
5. Clean trailing/leading whitespace from text fields

---

## Data Structure for Analysis

### Primary Grouping Variable
- **Country/Nationality**: Used as the primary dimension for nationality-based percentage calculations

### Secondary Grouping Variables
- Institution type
- Programme type
- Programme duration
- First time studying overseas (Yes/No)

### Analysis Dimensions
1. **Demographics**: Country distribution, language distribution
2. **Education Background**: Institution types, previous study experience
3. **Language Proficiency**: Ratings across Reading, Writing, Listening, Speaking, Overall
4. **Choice Factors**: Importance ratings for each factor
5. **Satisfaction**: Performance ratings, satisfaction levels
6. **Inclusion**: Agreement with inclusion-related statements
7. **Difficulties**: Difficulty ratings for educational activities
8. **Communication**: Preferred communication methods

---

## Calculation Notes

### Percentage Calculations
When calculating nationality-based percentages:

1. Group responses by nationality
2. For each response category (e.g., "Extremely" rating), count occurrences per nationality
3. Calculate percentage: `(count per nationality / total responses per nationality) × 100`
4. Handle missing values according to analysis requirements (exclude or include as separate category)

### Rating Scale Ordering
For proper statistical analysis, rating scales should be treated as ordinal:
- Importance: Not at all < A little < Moderately < Very < Extremely
- Agreement: Strongly disagree < Mildly disagree < Neutral < Mildly agree < Strongly agree
- Difficulty: Not at all < Slightly < Moderately < Very < Extremely
- English: Poor < Average < Good < Excellent
- Satisfaction: Very dissatisfied < Somewhat dissatisfied < Neutral < Somewhat satisfied < Very satisfied

---

## Version History

- **Version 1.0**: Initial data dictionary creation
- **Date**: 2024
- **Last Updated**: Based on survey data structure analysis

---

## Contact

For questions about the data structure or this dictionary, refer to the project documentation or supervisor.

