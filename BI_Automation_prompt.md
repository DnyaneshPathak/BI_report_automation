# MASTER PROMPT — LOCAL EXCEL → AUTOMATED DATA ANALYSIS → POWER BI DASHBOARD

## 1. ROLE

Act as a team of highly experienced professionals working together:

- Senior Data Analyst
- Senior Power BI Developer
- Statistical Analyst
- Data Visualization Expert
- Data Quality Engineer
- Automation Engineer
- Python Software Engineer
- Data Privacy & Security Engineer
- UI/UX Designer

Your task is to build a **fully automated local application/workflow** that accepts an **Excel file as the only data input**, performs intelligent data preprocessing and comprehensive exploratory/statistical analysis, automatically determines which features and relationships should be analyzed, creates an attractive professional Power BI dashboard, shows the user a dashboard preview first, and only after user confirmation generates the final downloadable **Power BI `.pbix` file**.

---

# 2. MAIN OBJECTIVE

Build the following automation:

```text
Excel File
    ↓
File Validation
    ↓
Sheet Detection
    ↓
Data Profiling
    ↓
Data Type Detection
    ↓
Data Quality Analysis
    ↓
Data Preprocessing
    ↓
Feature / Column Role Identification
    ↓
Univariate Analysis
    ↓
Bivariate Analysis
    ↓
Multivariate Analysis
    ↓
Statistical Analysis
    ↓
Probabilistic Analysis
    ↓
Automatic Insight Generation
    ↓
Automatic Dashboard Planning
    ↓
Power BI Data Model
    ↓
Professional Dashboard Creation
    ↓
Dashboard Preview
    ↓
User Approval
    ↓
Generate Final Power BI File
    ↓
Download .PBIX
```

The system must make intelligent analytical decisions automatically.

The user should NOT need to manually specify:

- Columns
- Chart types
- KPIs
- Data types
- Measures
- Relationships
- Statistical methods
- Dashboard layout
- Dashboard pages

The system must detect and decide these automatically from the Excel data.

---

# 3. STRICT INPUT REQUIREMENT

The ONLY data input must be:

```text
Excel File
.xlsx
.xls
.xlsm where safely supported
```

Do not require:

- CSV
- JSON
- Database connection
- Cloud database
- API
- Google Sheets
- Manual schema
- Manual metadata
- External data source

The application may ask the user only for actions such as:

```text
Upload Excel
Generate Dashboard
Approve Dashboard
Regenerate Dashboard
Download Power BI File
```

No additional analytical configuration should be mandatory.

---

# 4. ABSOLUTE PRIVACY REQUIREMENT

This is one of the highest-priority requirements.

## ALL DATA MUST REMAIN LOCAL.

The Excel data must NEVER be:

- uploaded to a cloud server
- uploaded to an external API
- transmitted to an LLM API
- transmitted to OpenAI
- transmitted to Gemini
- transmitted to Anthropic
- transmitted to Microsoft cloud services for analysis
- stored in Firebase
- stored in Supabase
- stored in AWS
- stored in Azure
- stored in GCP
- sent to third-party analytics services
- sent to telemetry services
- sent to error-tracking platforms
- sent to any organization outside the local computer

### Required architecture

```text
Excel
  ↓
Local Application
  ↓
Local Python Processing
  ↓
Local Data Storage / Temporary Files
  ↓
Local Statistical Engine
  ↓
Local Dashboard Generation
  ↓
Local Power BI Desktop
```

All processing must happen on the user's machine.

Use local libraries only.

Examples:

```text
Python
Pandas
NumPy
SciPy
Statsmodels
OpenPyXL
Matplotlib
Power BI Desktop
Local filesystem
```

Do not use any cloud-based AI model.

If intelligent textual insight generation is required, generate it using:

- deterministic Python logic
- predefined analytical rules
- statistical rules
- local templates

Do NOT send raw data or derived sensitive data outside the machine.

---

# 5. SECURITY REQUIREMENTS

Implement:

- local-only file processing
- no external API calls
- no network transmission of uploaded data
- no analytics trackers
- no remote logging
- no telemetry containing business data
- temporary-file cleanup
- safe filename handling
- Excel validation
- file-size validation
- sheet validation
- formula-injection safety where relevant
- secure error handling

Sensitive values should never appear in debug logs unnecessarily.

After processing finishes, temporary intermediate files should be deleted when they are no longer required.

---

# 6. EXCEL INGESTION ENGINE

After Excel upload:

1. Validate the Excel file.
2. Detect all worksheets.
3. Identify:
   - data sheets
   - lookup/reference sheets
   - empty sheets
   - summary sheets
4. Detect header row intelligently.
5. Detect merged cells.
6. Detect hidden rows/columns where relevant.
7. Detect blank rows.
8. Detect multiple tables where possible.
9. Detect duplicate columns.
10. Detect inconsistent column names.
11. Detect Excel date formats.
12. Detect numeric values stored as strings.
13. Detect percentages.
14. Detect currency fields.
15. Detect IDs.
16. Detect categorical fields.
17. Detect continuous variables.
18. Detect discrete numeric fields.
19. Detect datetime fields.
20. Detect possible geographic fields.
21. Detect textual fields.
22. Detect boolean/binary fields.

If multiple useful sheets exist, determine whether they can logically be related.

---

# 7. DATA PROFILING

Create an internal data profile for every field.

For every column calculate where applicable:

```text
Column Name
Detected Data Type
Analytical Type
Number of Records
Unique Count
Unique Percentage
Missing Count
Missing Percentage
Duplicate Count
Minimum
Maximum
Mean
Median
Mode
Standard Deviation
Variance
Range
Quartiles
IQR
Skewness
Kurtosis
Zero Count
Negative Count
Outlier Count
Cardinality
```

For categorical fields calculate:

```text
Number of categories
Most frequent category
Least frequent category
Frequency distribution
Percentage distribution
Rare categories
High-cardinality flag
```

For datetime fields calculate:

```text
Earliest Date
Latest Date
Date Range
Available Granularity
Missing Time Periods
Year Coverage
Quarter Coverage
Month Coverage
Week Coverage
Day Coverage
```

---

# 8. AUTOMATIC DATA-TYPE CLASSIFICATION

Every variable must be classified into analytical groups.

### Continuous

Examples:

```text
Revenue
Sales
Profit
Cost
Age
Price
Amount
Distance
Duration
Quantity with large range
```

### Discrete Numeric

Examples:

```text
Number of orders
Number of customers
Ticket count
Transaction count
```

### Categorical Nominal

Examples:

```text
Region
Department
Product
Country
Channel
Customer Type
Status
```

### Categorical Ordinal

Examples:

```text
Low
Medium
High

Poor
Average
Good
Excellent
```

### Binary

Examples:

```text
Yes / No
True / False
0 / 1
```

### Date / Time

Examples:

```text
Booking Date
Order Date
Departure Date
Transaction Date
Created Date
```

### Identifier

Examples:

```text
Customer ID
Booking ID
Invoice Number
Transaction ID
Employee ID
```

Identifiers should normally NOT be treated as numerical continuous variables.

---

# 9. AUTOMATIC FEATURE ROLE DETECTION

Determine the business/analytical role of each feature.

Possible roles:

```text
Identifier
Measure
Dimension
Time Dimension
Category
Location
Status
Target-Like Metric
Financial Measure
Quantity
Percentage
Duration
Ranking Variable
Descriptive Text
```

Avoid meaningless analysis.

Examples:

Do NOT calculate average of:

```text
Customer ID
Invoice Number
Phone Number
Booking ID
Postal Code
```

even if they are stored as numbers.

---

# 10. DATA PREPROCESSING

Perform preprocessing before analysis.

## Missing Values

Analyze missingness first.

Depending on field type and context:

### Numeric

Possible techniques:

```text
Median imputation
Mean imputation only where appropriate
Leave missing where business meaning is important
```

### Categorical

Possible techniques:

```text
Mode
Unknown
Not Available
```

Never silently modify important business data without maintaining an internal preprocessing log.

---

# 11. DUPLICATE HANDLING

Detect:

```text
Exact row duplicates
Possible duplicate business records
Duplicate IDs
```

Remove only clear technical duplicates.

Do not remove legitimate repeated transactions merely because some fields match.

---

# 12. OUTLIER ANALYSIS

For continuous numeric variables detect outliers using suitable methods such as:

```text
IQR
Z-score where distribution assumptions allow it
Percentile analysis
```

Do NOT automatically delete outliers.

Instead classify them as:

```text
Likely Valid
Suspicious
Extreme
```

Preserve them unless they are clear data errors.

---

# 13. TYPE CORRECTION

Automatically correct where confidence is sufficiently high:

```text
Numbers stored as strings
Dates stored as strings
Boolean values
Percentages
Currency formatting
Whitespace
Column names
```

Standardize column names internally while retaining readable names for Power BI.

---

# 14. TEXT CLEANING

Where appropriate:

- Trim leading spaces
- Trim trailing spaces
- Normalize repeated whitespace
- Normalize obvious case inconsistencies
- Remove invisible characters
- Standardize null-like strings such as:

```text
NA
N/A
null
NULL
None
-
blank
```

Use caution so legitimate values are not destroyed.

---

# 15. IMPORTANT MACHINE LEARNING RESTRICTION

This project is NOT a machine-learning project.

Therefore DO NOT perform:

```text
StandardScaler
MinMaxScaler
RobustScaler
Normalization for ML
PCA
Feature engineering intended only for ML models
Train/test split
Model training
Classification
Regression modeling
Clustering for ML purposes
Neural networks
```

Data scaling is specifically prohibited.

---

# 16. AUTOMATIC ANALYSIS ENGINE

The system must perform five primary categories of analysis:

```text
1. Univariate Analysis
2. Bivariate Analysis
3. Multivariate Analysis
4. Statistical Analysis
5. Probabilistic Analysis
```

Analysis selection must depend upon variable types.

Do not blindly perform every calculation on every column.

---

# 17. UNIVARIATE ANALYSIS

## Continuous Numerical Variables

Calculate where relevant:

```text
Count
Mean
Median
Mode
Min
Max
Range
Variance
Standard Deviation
Q1
Q3
IQR
Coefficient of Variation
Skewness
Kurtosis
Percentiles
Outliers
Distribution
```

Possible visualizations:

```text
Histogram
Box Plot
Density-style distribution where practical
KPI Card
Distribution summary
```

---

## Categorical Variables

Calculate:

```text
Frequency
Percentage
Mode
Unique Values
Cardinality
Rare Categories
```

Possible visualizations:

```text
Bar Chart
Column Chart
Treemap
Donut Chart only when category count is small
Table
KPI
```

Avoid pie/donut charts when there are too many categories.

---

## Date Variables

Analyze:

```text
Yearly trends
Quarterly trends
Monthly trends
Weekly trends where meaningful
Daily trends where meaningful
Seasonality indicators
Growth / decline patterns
```

---

# 18. BIVARIATE ANALYSIS

Automatically select relevant feature pairs.

## Numerical vs Numerical

Perform:

```text
Correlation
Covariance where useful
Pearson correlation where assumptions are reasonable
Spearman correlation where appropriate
Scatter analysis
Trend analysis
```

Visualization:

```text
Scatter Plot
Correlation Heatmap
Trend Chart
```

---

## Numerical vs Categorical

Perform:

```text
Group Mean
Group Median
Group Standard Deviation
Group Count
Group Distribution
Variance comparison
```

Potential statistical testing:

```text
t-test
ANOVA
Mann-Whitney U
Kruskal-Wallis
```

Use tests only when statistically appropriate.

Visualization:

```text
Box Plot
Bar Chart
Column Chart
Grouped Chart
```

---

## Categorical vs Categorical

Perform:

```text
Cross-tabulation
Contingency Table
Percentage Comparison
Chi-Square Test
Cramer's V where useful
```

Visualization:

```text
Stacked Bar Chart
100% Stacked Bar
Matrix
Heatmap
```

---

# 19. MULTIVARIATE ANALYSIS

Find meaningful relationships among 3 or more variables.

Examples:

```text
Sales by Region over Time
Revenue by Product and Customer Segment
Profit by Category across Month
Bookings by Destination and Channel over Time
Performance by Region + Product + Time
```

Use:

```text
Correlation Matrix
Grouped Analysis
Pivot Analysis
Segment Analysis
Multi-dimensional aggregation
Conditional comparisons
```

Do not perform useless combinations.

Rank potentially useful multivariate analyses based on:

```text
Business interpretability
Statistical strength
Data volume
Variability
Relationship strength
Dashboard usefulness
```

---

# 20. STATISTICAL ANALYSIS

The system should automatically determine appropriate techniques.

Potential methods include:

```text
Mean
Median
Mode
Variance
Standard Deviation
Coefficient of Variation
Quartiles
Percentiles
IQR
Skewness
Kurtosis
Correlation
Covariance
Confidence Intervals
Hypothesis Tests
Chi-square
t-test
ANOVA
Mann-Whitney U
Kruskal-Wallis
```

Before applying a statistical test:

1. Identify variable types.
2. Check minimum sample size.
3. Consider distribution assumptions.
4. Determine whether the test is meaningful.
5. Explain the result in plain business language.

Do not perform a test simply because it is mathematically possible.

---

# 21. PROBABILISTIC ANALYSIS

Where appropriate calculate:

```text
Empirical probability
Conditional probability
Category probability
Event occurrence probability
Distribution probability
Percentile probability
```

Example:

```text
P(Status = Cancelled)

P(Channel = Online)

P(Cancelled | Region = West)

P(High Revenue | Customer Segment = Corporate)
```

Where continuous distributions reasonably resemble known probability distributions, optionally analyze distributions such as:

```text
Normal
Binomial
Poisson
Exponential
```

Never force data into a probability distribution when the evidence is weak.

---

# 22. ASSOCIATION STRENGTH

Detect the strongest useful relationships.

Rank insights based on:

```text
Strong correlations
Large group differences
Significant category associations
High growth / decline
Unusual distributions
Extreme values
Time trends
High concentration
High variance
Unexpected patterns
```

---

# 23. AUTOMATIC BUSINESS INSIGHTS

Generate concise business-language insights automatically.

Example:

```text
Revenue increased 18.4% compared with the previous period.

The West region contributes approximately 41% of total revenue.

Corporate customers have a 27% higher average booking value than retail customers.

Cancellation rates are highest for Channel X.

Product Category A generates the highest revenue but Product Category C has the highest margin.

A strong positive relationship exists between X and Y.
```

Insights must be based only on calculated results.

Never hallucinate.

Every numerical claim must be mathematically traceable to the dataset.

---

# 24. FEATURE IMPORTANCE FOR ANALYSIS

Although this is NOT machine learning, build an analytical relevance score to determine which variables deserve dashboard attention.

Score variables based on factors such as:

```text
Completeness
Variance
Cardinality
Business usefulness
Relationship strength
Time relevance
Correlation
Category concentration
Number of valid observations
Interpretability
```

This score is for dashboard design only.

Do NOT call it ML Feature Importance.

Call it:

```text
Analytical Relevance Score
```

---

# 25. KPI IDENTIFICATION

Automatically detect potential business KPIs.

Examples:

```text
Total Revenue
Total Sales
Total Bookings
Total Transactions
Total Customers
Average Order Value
Average Booking Value
Total Profit
Profit Margin
Cancellation Rate
Growth Rate
Conversion-style ratios where derivable
Average Duration
Average Cost
```

Only create KPIs supported by the dataset.

Never invent unavailable metrics.

---

# 26. POWER BI DATA MODEL

Automatically construct a clean Power BI model.

Where possible use:

```text
Fact Tables
Dimension Tables
Date Table
Relationships
Star Schema
```

Detect if the workbook contains appropriate lookup tables.

Avoid unnecessary relationships.

Prevent:

```text
Ambiguous relationships
Many-to-many relationships unless actually required
Circular dependency
Incorrect key relationships
```

Create a dedicated Date Table when date-based analysis is important.

---

# 27. DAX MEASURES

Create reusable DAX measures wherever appropriate instead of unnecessarily relying on calculated columns.

Potential measures:

```text
Total Revenue
Total Cost
Total Profit
Total Quantity
Average Revenue
Transaction Count
Distinct Customer Count
Growth %
Previous Period Value
Year-over-Year %
Month-over-Month %
Contribution %
Running Total
Cancellation %
Margin %
```

Only generate a measure when the required underlying columns exist.

Use readable naming conventions.

---

# 28. DASHBOARD PAGE PLANNING

Automatically determine the required number of dashboard/report pages.

Do not create too many pages.

Typical structure:

## Page 1 — Executive Overview

Include:

```text
Important KPI Cards
Main Business Trend
Major Category Breakdown
Top/Bottom Performers
Key Insights
Filters
```

## Page 2 — Detailed Analysis

Include:

```text
Category analysis
Segment analysis
Comparisons
Distribution
Top-N analysis
```

## Page 3 — Trend Analysis

When date data exists:

```text
Monthly Trend
Quarter Trend
YoY / MoM
Seasonality
Growth
```

## Page 4 — Statistical Insights

When sufficiently useful:

```text
Distribution summary
Correlation
Outliers
Category relationships
Statistical insights
```

Do not create empty or unnecessary pages.

---

# 29. AUTOMATIC CHART SELECTION ENGINE

Select chart type based on the analytical question.

### Trends

Use:

```text
Line Chart
Area Chart when justified
Column Trend
```

### Category Comparison

Use:

```text
Bar Chart
Column Chart
```

### Ranking

Use:

```text
Horizontal Bar
Top-N Table
```

### Part-to-Whole

Use:

```text
Treemap
Stacked Bar
Donut only for a small number of categories
```

### Relationship

Use:

```text
Scatter Plot
```

### Distribution

Use:

```text
Histogram
Box Plot
```

### Geographic Data

When valid geographical fields exist:

```text
Map
Filled Map
```

Only use local Power BI functionality. Do not send sensitive geographic/business data to external mapping APIs.

### Detailed Reporting

Use:

```text
Table
Matrix
```

Avoid poor visualization choices.

---

# 30. VISUALIZATION QUALITY RULES

Dashboard must be:

```text
Professional
Corporate
Clean
Modern
Minimal
Readable
Attractive
Consistent
Executive-friendly
Not overly colorful
```

Use a restrained corporate palette.

For example:

```text
Dark Navy
Blue
White
Light Gray
Muted Accent Color
```

Avoid:

```text
Neon colors
Too many colors
Unnecessary gradients
Heavy shadows
3D charts
Decorative clutter
Excessive icons
Excessive pie charts
Excessive borders
```

---

# 31. DASHBOARD LAYOUT

Follow strong information hierarchy.

Recommended layout:

```text
---------------------------------------------------
| Dashboard Title                     Last Refresh |
---------------------------------------------------
| KPI 1 | KPI 2 | KPI 3 | KPI 4 | KPI 5          |
---------------------------------------------------
|                Main Trend                         |
---------------------------------------------------
| Category Analysis       | Segment Analysis       |
---------------------------------------------------
| Top/Bottom Analysis     | Business Insight       |
---------------------------------------------------
| Filters / Slicers                                   |
---------------------------------------------------
```

Alignment and spacing must be consistent.

---

# 32. FILTERS AND SLICERS

Automatically create useful filters based on dataset fields.

Potential filters:

```text
Date
Year
Month
Region
Country
Department
Category
Product
Customer Segment
Status
Channel
```

Do not create slicers for:

```text
Transaction IDs
Invoice IDs
Extremely high-cardinality fields
Long free-text fields
```

unless genuinely useful.

---

# 33. TOP-N AND BOTTOM-N ANALYSIS

Where applicable automatically add:

```text
Top 5
Top 10
Bottom 5
Bottom 10
```

Examples:

```text
Top destinations
Top products
Top customers
Top regions
Highest revenue categories
Lowest-performing segments
```

Use dynamic ranking when practical.

---

# 34. DASHBOARD INTERACTIVITY

Configure appropriate Power BI interactions:

```text
Cross filtering
Cross highlighting
Drill-down
Drill-through when useful
Tooltips
Slicers
Reset Filters functionality where practical
```

Do not add interaction simply for decoration.

---

# 35. AUTOMATIC REPORT NARRATIVE

Generate a compact insight panel.

Example:

```text
KEY INSIGHTS

• Revenue increased by 14.3% during the selected period.
• Region A accounts for 38% of total revenue.
• Product X is the highest-revenue product.
• Cancellation rates are highest in Channel Y.
• Revenue shows a strong positive relationship with Quantity.
```

Each statement must be calculated from the Excel data.

---

# 36. DASHBOARD PREVIEW — MANDATORY

The system MUST NOT immediately produce the final `.pbix`.

The required workflow is:

```text
Upload Excel
      ↓
Analyze
      ↓
Generate Dashboard
      ↓
Create Preview
      ↓
Show Preview to User
```

The preview must show the actual intended dashboard layout as closely as possible.

It may be rendered locally as:

```text
PNG
SVG
HTML/CSS Preview
Local rendered report preview
```

No cloud rendering is allowed.

---

# 37. PREVIEW SCREEN

The preview screen must provide:

```text
Dashboard Preview

[ Approve & Generate Power BI ]
[ Regenerate Dashboard ]
```

Optionally allow:

```text
Previous Design
Next Design
```

if multiple local layouts are generated.

However, keep interaction simple.

---

# 38. APPROVAL WORKFLOW

The final Power BI file must only be generated after explicit approval.

Workflow:

```text
IF user clicks:

Approve & Generate Power BI

THEN:
    Generate Final Power BI File

ELSE IF user clicks:

Regenerate Dashboard

THEN:
    Re-plan dashboard
    Generate a new preview
```

Do NOT generate the final `.pbix` before user confirmation.

---

# 39. FINAL OUTPUT

After approval, generate:

```text
analysis_dashboard.pbix
```

or a filename derived safely from the Excel file name, such as:

```text
sales_analysis_dashboard.pbix
```

Provide a visible button:

```text
Download Power BI Dashboard
```

The downloaded file must be a valid Power BI Desktop file.

---

# 40. POWER BI GENERATION REQUIREMENT

Use Power BI Desktop installed locally.

The automation should build:

```text
Data model
Relationships
Queries / transformations
Date table where required
DAX measures
Report pages
Visuals
Filters
Slicers
Interactions
Formatting
```

and then save the result as:

```text
.pbix
```

Prefer officially supported local Power BI mechanisms wherever possible.

If direct `.pbix` programmatic generation is restricted by Power BI Desktop, automate the local Power BI Desktop workflow using a reliable supported local approach.

Do NOT silently replace `.pbix` with:

```text
CSV
Excel
PDF
Image
PowerPoint
```

because the required final deliverable is Power BI.

A `.pbip` Power BI Project may be used internally if it helps with generation, but the user-facing final deliverable should still be `.pbix` wherever the installed Power BI Desktop environment supports the conversion/save operation.

If the local machine technically cannot generate `.pbix`, clearly report the exact blocking dependency instead of pretending that a valid `.pbix` was generated.

---

# 41. LOCAL APPLICATION UI

Create a modern simple application.

## Screen 1

```text
Excel to Power BI Automation

Drag and drop Excel file

        OR

[ Choose Excel File ]

[ Start Analysis ]
```

---

## Screen 2 — Processing

Display progress:

```text
Reading Excel                  ✓
Profiling Data                 ✓
Cleaning Data                  ✓
Detecting Data Types           ✓
Running Statistical Analysis   ✓
Finding Important Insights     ✓
Planning Dashboard             ✓
Building Preview               ...
```

Do not expose overly technical logs to normal users.

---

## Screen 3 — Preview

Display:

```text
Dashboard Preview
```

Buttons:

```text
[ Approve & Generate Power BI ]

[ Regenerate Dashboard ]
```

Also show concise automatically generated:

```text
Key Findings
Detected KPIs
Data Quality Summary
```

---

## Screen 4 — Final Output

Display:

```text
Power BI Dashboard Generated Successfully
```

Button:

```text
[ Download .PBIX ]
```

Optionally:

```text
[ Analyze Another Excel File ]
```

---

# 42. DATA QUALITY SUMMARY

Before preview, provide a compact quality report such as:

```text
Rows: 52,480

Columns: 18

Missing Values: 2.8%

Duplicate Rows: 0.4%

Numeric Fields: 7

Categorical Fields: 6

Date Fields: 2

Identifier Fields: 3

Potential Outliers: 42
```

Do not overwhelm the user with technical statistics unless they choose to inspect details.

---

# 43. ANALYTICAL SUMMARY

Internally retain a report containing:

```text
Detected Columns
Column Types
Preprocessing Applied
Data Quality Findings
Univariate Results
Bivariate Results
Multivariate Results
Statistical Tests
Probability Analysis
Strong Relationships
Important KPIs
Selected Visuals
Rejected Visuals
Reasons for Visualization Selection
Generated DAX
```

This can be shown in a collapsible:

```text
View Analysis Details
```

section.

---

# 44. ANALYSIS DECISION ENGINE

For every possible analysis ask internally:

```text
Is this statistically valid?

Is this business meaningful?

Is the sample size sufficient?

Are the variable types compatible?

Is the result understandable?

Would the insight improve the dashboard?
```

Only keep analyses that provide meaningful information.

---

# 45. DASHBOARD PRIORITIZATION ALGORITHM

Prioritize visualizations approximately using:

```text
Business Value
×
Statistical Strength
×
Interpretability
×
Data Quality
×
Visual Suitability
```

High-priority insights belong on Page 1.

Lower-level supporting details may go to secondary pages.

---

# 46. AVOID VISUAL OVERLOAD

Recommended maximum per page:

```text
4–6 KPI Cards

4–7 Main Visuals

3–6 Important Slicers
```

Use judgment depending on screen size and data complexity.

Do not fill every empty space.

Whitespace is desirable.

---

# 47. ERROR HANDLING

Handle situations such as:

```text
Empty Excel file
Password-protected workbook
Corrupt workbook
No valid table
Only one usable column
Extremely large workbook
Mixed data types
Missing headers
Duplicate headers
Unsupported formulas
Invalid dates
Insufficient data
Power BI Desktop not installed
Power BI automation failure
```

Give human-readable messages.

Example:

```text
The Excel file was loaded successfully, but no structured dataset was detected.
Please ensure that the workbook contains at least one table with column headers.
```

Do not crash.

---

# 48. PERFORMANCE

The system should handle reasonably large business Excel files efficiently.

Optimize using:

```text
Vectorized Pandas operations
Efficient memory usage
Selective statistical computations
Cached profiling results
Minimal unnecessary copies
Efficient aggregation
```

Avoid expensive pairwise analysis across hundreds of columns without analytical screening.

First identify promising columns, then perform deeper analysis.

---

# 49. LOGGING

Maintain local technical logs for debugging.

Never log unnecessarily:

```text
Full customer data
Passwords
Personally identifiable information
Financial account information
Entire datasets
```

Logs remain on the machine.

---

# 50. PROJECT STRUCTURE

Use a clean modular software architecture such as:

```text
project/
│
├── app/
│   ├── ui/
│   ├── controllers/
│   └── workflow/
│
├── ingestion/
│   ├── excel_reader.py
│   └── sheet_detector.py
│
├── preprocessing/
│   ├── cleaner.py
│   ├── missing_values.py
│   ├── duplicates.py
│   ├── datatype_detector.py
│   └── outliers.py
│
├── analysis/
│   ├── profiler.py
│   ├── univariate.py
│   ├── bivariate.py
│   ├── multivariate.py
│   ├── statistical.py
│   ├── probability.py
│   └── insight_engine.py
│
├── dashboard/
│   ├── kpi_detector.py
│   ├── chart_selector.py
│   ├── layout_engine.py
│   ├── preview_renderer.py
│   └── dax_generator.py
│
├── powerbi/
│   ├── model_builder.py
│   ├── powerbi_automation.py
│   └── exporter.py
│
├── security/
│   ├── privacy.py
│   └── file_security.py
│
├── temp/
│
├── outputs/
│
└── main.py
```

Adjust architecture if a better local architecture exists.

---

# 51. CODE QUALITY

Code must be:

```text
Modular
Readable
Maintainable
Testable
Documented
Error-resistant
Production-oriented
```

Avoid putting the entire application in one file.

Use clear:

```text
classes
functions
modules
configuration
type hints
exception handling
```

where appropriate.

---

# 52. VALIDATION TESTS

Before considering the project complete, test it using multiple synthetic/local Excel datasets.

## Test Dataset A

```text
Sales dataset
```

with:

```text
Date
Region
Product
Sales
Cost
Profit
Quantity
```

Expected:

```text
KPIs
Trend
Category comparison
Profitability
Top products
Regional analysis
```

---

## Test Dataset B

```text
Travel booking dataset
```

with:

```text
Booking ID
Booking Date
Destination
Customer Type
Booking Amount
Channel
Status
Travel Date
```

Expected:

```text
Total Bookings
Booking Revenue
Average Booking Value
Cancellation Rate
Destination Analysis
Channel Analysis
Time Trend
Customer Segment Analysis
```

---

## Test Dataset C

Data quality issues:

```text
Missing values
Duplicates
Outliers
Numbers stored as strings
Dates stored incorrectly
Rare categories
```

System must handle these safely.

---

# 53. STATISTICAL VALIDATION

Validate calculations using known values.

Check:

```text
Mean
Median
Variance
Standard deviation
Correlation
Percentages
Probability
Group aggregates
Confidence intervals
```

Do not allow silently incorrect statistics.

---

# 54. DASHBOARD VALIDATION

Before preview generation check:

```text
No overlapping visuals
No truncated titles
No unreadable labels
No empty visuals
No meaningless charts
No invalid calculations
No excessive colors
No unnecessary visual
No broken filters
No incorrect DAX references
```

---

# 55. POWER BI VALIDATION

Before presenting the download button verify:

```text
File exists
File is not empty
Power BI generation completed successfully
Required report pages exist
Core measures are available
Relationships are valid
```

Never provide a fake `.pbix` file simply by renaming another file extension.

---

# 56. PRIVACY VALIDATION

Before completion verify:

```text
No external API called
No cloud storage used
No data uploaded
No analytics tracker used
No remote logging used
No LLM API used
Temporary files cleaned where possible
```

Privacy violations should be treated as blocking errors.

---

# 57. BUSINESS LANGUAGE

Dashboard titles and generated insights should use simple professional language.

Prefer:

```text
Revenue by Region
Monthly Booking Trend
Top 10 Destinations
Average Booking Value
Cancellation Rate
Customer Segment Performance
```

Avoid technical labels such as:

```text
Bivariate Result #4
Variable X Distribution
Statistical Visualization
```

unless shown inside an advanced-analysis section.

---

# 58. DECIMAL AND NUMBER FORMATTING

Automatically apply sensible formatting.

Examples:

```text
1,245

₹1.25M

$4.2M

18.4%

2.7K
```

Detect currency formatting from the Excel data where reasonably possible.

Do not assume a specific currency without evidence.

---

# 59. TITLE GENERATION

Generate dashboard names from the dataset.

Examples:

```text
Sales Performance Dashboard

Travel Booking Analytics Dashboard

Customer Insights Dashboard

Financial Performance Dashboard

Operations Analytics Dashboard
```

If business context cannot be confidently determined, use:

```text
Business Analytics Dashboard
```

---

# 60. NO HALLUCINATION RULE

Never invent:

```text
KPIs
Business meaning
Currency
Targets
Benchmarks
Customer information
Forecasts
Company assumptions
Missing data
Relationships
```

Everything must originate from the uploaded Excel file or valid mathematical derivations of that data.

---

# 61. NO ML FORECASTING

Do not perform predictive forecasting because machine learning is outside the scope.

Descriptive historical trends are allowed.

Statistical trend summaries are allowed.

Do not show a future forecast unless a purely statistical forecasting feature is explicitly added later by the product owner.

---

# 62. PRIORITY ORDER

When design decisions conflict, follow this priority:

```text
1. Data Privacy
2. Data Accuracy
3. Statistical Validity
4. Business Interpretability
5. Dashboard Readability
6. User Experience
7. Visual Appearance
8. Processing Speed
```

Never sacrifice accuracy for appearance.

---

# 63. ACCEPTANCE CRITERIA

The application is complete only if the following workflow works successfully:

```text
STEP 1
User launches application locally.

STEP 2
User uploads ONE Excel workbook.

STEP 3
System reads the workbook locally.

STEP 4
System automatically detects schema and data types.

STEP 5
System cleans and preprocesses data.

STEP 6
System performs:
- Univariate analysis
- Bivariate analysis
- Multivariate analysis
- Statistical analysis
- Probabilistic analysis

STEP 7
System identifies important features and KPIs.

STEP 8
System selects useful charts automatically.

STEP 9
System creates Power BI data model and DAX plan.

STEP 10
System generates a polished dashboard preview locally.

STEP 11
User sees the preview.

STEP 12
System waits for user approval.

STEP 13
User clicks:

Approve & Generate Power BI

STEP 14
System creates the actual Power BI report locally.

STEP 15
System validates the report.

STEP 16
System provides:

Download .PBIX

STEP 17
At no point is business data transmitted outside the local computer.
```

---

# 64. DEVELOPMENT APPROACH FOR ANTIGRAVITY

Do not only create UI mockups.

Build the actual working application.

Work sequentially:

```text
PHASE 1
Create architecture and project structure.

PHASE 2
Implement Excel ingestion.

PHASE 3
Implement data profiling.

PHASE 4
Implement preprocessing.

PHASE 5
Implement analytical type detection.

PHASE 6
Implement univariate analysis.

PHASE 7
Implement bivariate analysis.

PHASE 8
Implement multivariate analysis.

PHASE 9
Implement statistical analysis.

PHASE 10
Implement probabilistic analysis.

PHASE 11
Implement insight-ranking engine.

PHASE 12
Implement KPI detection.

PHASE 13
Implement automatic chart-selection engine.

PHASE 14
Implement dashboard-layout engine.

PHASE 15
Implement dashboard preview.

PHASE 16
Implement approval workflow.

PHASE 17
Implement local Power BI generation.

PHASE 18
Implement PBIX export/download.

PHASE 19
Run functional tests.

PHASE 20
Run statistical validation.

PHASE 21
Run privacy/security validation.

PHASE 22
Fix all detected issues.
```

Do not stop after planning.

Continue implementing until a working local solution is produced.

---

# 65. AUTONOMOUS DECISION RULE

Do not repeatedly ask me questions about:

- chart selection
- preprocessing strategy
- analytical techniques
- dashboard design
- colors
- KPI selection
- column selection

Use professional judgment based on:

```text
Data type
Data quality
Statistical validity
Business usefulness
Visualization best practices
```

Only ask the user when a technical limitation prevents safe completion.

---

# 66. FINAL QUALITY GATE

Before declaring the project complete, behave as:

```text
Senior Data Analyst
+
Senior Statistician
+
Senior Power BI Developer
+
Senior Software Engineer
+
Data Privacy Engineer
```

Review the entire system.

Explicitly validate:

### Data

```text
✓ Excel reads correctly
✓ Column types are correct
✓ Missing values are handled correctly
✓ Duplicates are handled correctly
✓ Data is not unnecessarily altered
```

### Analysis

```text
✓ Univariate analysis works
✓ Bivariate analysis works
✓ Multivariate analysis works
✓ Statistical analysis is mathematically correct
✓ Probability analysis is mathematically correct
✓ Analysis depends on variable type
✓ IDs are not treated as measures
✓ No ML scaling occurs
```

### Dashboard

```text
✓ KPIs are meaningful
✓ Chart selection is appropriate
✓ Dashboard is readable
✓ Visual hierarchy is professional
✓ Colors are restrained
✓ Filters are useful
✓ Insights are accurate
```

### Power BI

```text
✓ Model is valid
✓ Relationships are correct
✓ DAX is valid
✓ Report pages work
✓ Final Power BI file opens correctly
```

### Privacy

```text
✓ 100% local processing
✓ No external API
✓ No cloud data transfer
✓ No external LLM
✓ No external storage
✓ No telemetry containing source data
```

### Workflow

```text
✓ Excel Upload
✓ Automatic Analysis
✓ Dashboard Preview
✓ User Approval
✓ Final Power BI Generation
✓ Downloadable PBIX
```

Only after all checks pass should the application be considered finished.

---

# FINAL INSTRUCTION

Build this as a **production-quality local Excel-to-Power-BI automation tool**, not as a prototype or static demonstration.

The core user experience should remain extremely simple:

```text
UPLOAD EXCEL
      ↓
AUTOMATIC ANALYSIS
      ↓
DASHBOARD PREVIEW
      ↓
APPROVE
      ↓
DOWNLOAD POWER BI (.PBIX)
```

Behind this simple workflow, implement robust:

```text
Data profiling
Data preprocessing
Data-type detection
Feature-role detection
Univariate analysis
Bivariate analysis
Multivariate analysis
Statistical analysis
Probabilistic analysis
Analytical relevance scoring
KPI identification
Insight generation
Power BI modeling
DAX creation
Automatic visualization selection
Professional dashboard design
Privacy controls
Validation
```

The most important non-negotiable requirement is:

> **The uploaded Excel file and every value derived from it must remain on the user's local machine at all times. No business data may be transmitted to any external server, API, cloud platform, AI provider, analytics service, or third-party organization.**

Start building the complete working system now.



4/10/26 : GPT Prompt : 

# ROLE

Act as a **Principal Automation Engineer, Senior Python Architect, Senior Data Analyst, Power BI Developer, BI Solution Architect, QA Engineer, and AI/LLM Prompt Engineering Specialist**.

You are working inside an existing Python project named approximately:

`BI_Report_Automation`

This is NOT a greenfield project.

You must carefully inspect the existing repository, understand the current architecture, fix the existing defects, refactor only where necessary, and upgrade the application into a robust **AI-powered Excel-to-Power-BI dashboard automation system**.

Do NOT only explain the problems.

You must:

1. inspect the code,
2. identify root causes,
3. modify the code,
4. run tests,
5. verify behavior,
6. fix regressions,
7. validate the generated Power BI project,
8. preserve existing working functionality,
9. document all important changes.

---

# PRIMARY PROJECT GOAL

The application should follow this workflow:

```text
Excel Upload
     ↓
Data Validation
     ↓
Schema Detection
     ↓
Data Profiling
     ↓
Data Cleaning
     ↓
Data Type Detection
     ↓
Feature Role Detection
     ↓
Statistical Analysis
     ↓
User Requirement Understanding
     ↓
AI Dashboard Planning
     ↓
Semantic Model Planning
     ↓
KPI Planning
     ↓
Chart Planning
     ↓
Dashboard Layout Planning
     ↓
Interactive HTML Preview
     ↓
User Confirmation / Modification
     ↓
Power BI Project Generation
     ↓
Download
```

The most important requirement is:

> The dashboard must be generated according to the USER'S REQUIREMENT and the DATA, not according to generic hard-coded chart rules.

---

# IMPORTANT SCOPE DEFINITION

Do NOT interpret the requirement "support all Power BI functionality" as "rebuild Microsoft's entire Power BI ecosystem."

There are two different capability categories.

## CATEGORY A — MUST SUPPORT

Implement or architect strong parity with **Power BI Desktop report-authoring and semantic-modeling capabilities** that can reasonably be represented programmatically.

This includes:

- Excel ingestion
- multiple Excel sheets
- data profiling
- data cleaning
- data transformation
- column typing
- categorical/continuous/date/ID detection
- relationships
- semantic models
- measures
- calculations
- KPIs
- charts
- filters
- slicers
- drill-down
- drillthrough
- sorting
- Top N
- hierarchies
- tooltips
- bookmarks where technically representable
- navigation
- multi-page reports
- tables
- matrices
- themes
- conditional formatting
- cross-filtering
- cross-highlighting where supported
- report/page/visual filters
- responsive layout planning
- dashboard/report pages
- Power BI project generation
- PBIP
- PBIR
- TMDL/TMSL compatibility where required

## CATEGORY B — DO NOT FAKE

Some Power BI features depend on Microsoft cloud infrastructure.

Examples:

- Power BI Service workspaces
- Microsoft tenant authentication
- publishing to workspace
- gateways
- scheduled cloud refresh
- subscriptions
- organizational sharing
- Fabric deployment pipelines
- tenant administration
- audit logs
- Microsoft Purview governance
- streaming infrastructure
- alerts
- cloud collaboration

Do NOT pretend that these exist locally.

Instead create an extensible interface such as:

```text
integrations/
    powerbi_service/
```

and maintain a capability matrix:

```text
SUPPORTED_LOCAL
SUPPORTED_PBIP
PARTIAL
REQUIRES_POWER_BI_SERVICE
NOT_IMPLEMENTED
```

The core application must work without Microsoft credentials.

---

# CRITICAL EXISTING BUGS ALREADY IDENTIFIED

The following issues have already been discovered in the existing application.

Treat them as confirmed high-priority defects and verify them yourself before changing code.

---

# BUG 1 — PIPELINE EXECUTES TWICE

Important file:

`app/workflow/pipeline.py`

The method:

`_execute_steps()`

currently executes the requested pipeline steps and then accidentally contains logic that reconstructs/reruns a full hard-coded pipeline.

Because of this, Phase 2 can reload the original Excel dataset after the user selected only specific columns.

Example:

User selects:

```text
Order ID
Order Date
Region
```

and selects only:

```text
Univariate Analysis
```

but later the pipeline again contains all original columns and runs:

```text
Bivariate
Multivariate
Statistical
Probability
```

This is incorrect.

## REQUIRED FIX

`_execute_steps()` must ONLY execute the steps passed to it.

Desired conceptual implementation:

```python
def _execute_steps(self, steps):
    for step_name, step_fn in steps:
        try:
            step_fn()
        except Exception as exc:
            self.result.error = f"{step_name} failed: {exc}"

            if step_name == "Reading Excel":
                return False

    return True
```

Do not blindly copy this code.

Adapt it correctly to the application's architecture and logging/result system.

Remove the accidental duplicate pipeline execution.

---

# BUG 2 — WRONG PHASE 1 ORDER

Current processing is conceptually similar to:

```text
Excel
↓
Detect Types
↓
Clean
↓
Missing values
↓
Outliers
↓
Profile
```

This is logically incorrect if cleaning depends on correct type information.

Change the conceptual flow to:

```text
Excel ingestion
↓
Initial validation
↓
Schema/type detection
↓
Profiling
↓
Cleaning
↓
Missing-value handling
↓
Outlier analysis
↓
Updated profiling
```

Then stop Phase 1.

Do NOT perform all dashboard analyses before the user configuration is known.

---

# BUG 3 — USER FEATURE SELECTION IS LOST

When Phase 2 starts and a user selected specific features/columns:

1. filter the dataframe,
2. create a `.copy()`,
3. recreate metadata,
4. recreate column profiles,
5. recreate feature classifications,
6. clear previous analyses,
7. execute only the requested analyses.

Conceptually:

```python
df = df[selected_valid_columns].copy()
```

Then rebuild all dependent metadata.

Never reuse metadata belonging to the original dataframe.

---

# BUG 4 — OLD ANALYSIS RESULTS LEAK INTO NEW EXECUTION

Before Phase 2 analysis, clear all results that can contain old dataset information.

Examples:

```text
univariate
bivariate
multivariate
statistical_tests
probability_results
chart_specs
kpis
dashboard_spec
```

Implement a proper reset method rather than scattering resets throughout the code.

Example concept:

```python
result.reset_analysis_state()
```

---

# BUG 5 — `if result.success or True`

Inspect:

`app/controllers/flask_app.py`

There is logic equivalent to:

```python
if result.success or True:
```

This condition is permanently true.

Remove this behavior.

Use proper error handling:

```python
if result.success:
```

Failures must remain failures.

Never allow the application to silently continue when the pipeline failed.

---

# BUG 6 — DATA QUALITY FIELD NAME MISMATCH

The pipeline and UI use inconsistent names.

Possible pipeline fields:

```text
missing_pct
duplicate_pct
outlier_count
```

while frontend/rendering logic may expect:

```text
missing_cells
duplicates
outliers
```

Create a canonical model.

For example:

```python
class DataQualitySummary:
    total_rows
    total_columns
    missing_cells
    missing_percentage
    duplicate_rows
    duplicate_percentage
    outlier_count
```

Use exactly the same schema throughout:

```text
analysis
→ controller
→ API
→ frontend
→ preview
```

Never silently default an unknown metric to zero.

---

# BUG 7 — FAKE `Count` AND `Frequency` COLUMNS

The existing chart generator creates specifications such as:

```text
x = Region
y = Count
```

or:

```text
x = Sales
y = Frequency
```

But `Count` and `Frequency` may not exist in the actual dataset.

The Power BI exporter then treats them as real columns.

This is fundamentally incorrect.

## REPLACE THE CURRENT CHART MODEL

Do NOT represent charts using only:

```text
x_column
y_column
```

Create a semantic visual specification.

For example:

```python
class VisualSpec:
    id: str
    title: str

    chart_type: str

    dimension: str | None
    dimension2: str | None

    measure: str | None
    measure2: str | None

    aggregation: str | None

    legend: str | None

    time_grain: str | None

    sort_by: str | None
    sort_direction: str | None

    top_n: int | None

    filters: list

    page: str | None

    tooltip_fields: list

    drilldown_fields: list

    drillthrough_page: str | None

    conditional_formatting: dict | None
```

For category count:

```text
dimension = Region
measure = Order ID
aggregation = count
```

or a semantic row-count measure.

Never create a fictional physical column named `Count`.

For histogram:

use histogram/binning semantics.

Do NOT pretend that `Frequency` exists as a physical dataset field.

---

# BUG 8 — PREVIEW AND POWER BI USE DIFFERENT LOGIC

Currently HTML/ECharts preview may calculate:

```text
Average Sales by Channel
```

while Power BI generation may interpret the same chart as:

```text
SUM(Sales)
```

This is unacceptable.

Implement ONE canonical object:

`DashboardSpec`

The following components must consume the same specification:

```text
HTML Preview
Power BI Report Generator
Validation Engine
User Modification Engine
```

Architecture:

```text
                ┌→ HTML/ECharts renderer
DashboardSpec ──┼→ Power BI renderer
                └→ Validation engine
```

Neither renderer may reinterpret the business meaning of a chart.

---

# CREATE A SINGLE SOURCE OF TRUTH

Implement a strongly typed model.

Prefer:

- Python dataclasses, or
- Pydantic models

Example conceptual architecture:

```python
class KPIIntent:
    name: str
    measure: str
    aggregation: str
    format: str | None
    target: float | None

class VisualSpec:
    ...

class PageSpec:
    name: str
    visuals: list[VisualSpec]
    filters: list
    slicers: list
    layout: dict

class DashboardSpec:
    title: str
    description: str
    kpis: list[KPIIntent]
    pages: list[PageSpec]
    global_filters: list
    theme: dict
```

Validate it before preview generation.

Validate it again before PBIP generation.

---

# BUG 9 — NATURAL LANGUAGE INTENT PARSER IS TOO WEAK

Important area:

`src/bi_automation/intent/`

The current parser appears to rely too much on basic keyword matching.

A requirement such as:

```text
Show total sales, total profit, sales by region,
monthly sales trend and top 10 products by sales.
```

must produce structured intent approximately equivalent to:

```json
{
  "kpis": [
    {
      "metric": "Sales",
      "aggregation": "sum",
      "title": "Total Sales"
    },
    {
      "metric": "Profit",
      "aggregation": "sum",
      "title": "Total Profit"
    }
  ],

  "visuals": [
    {
      "title": "Sales by Region",
      "chart_type": "bar",
      "dimension": "Region",
      "measure": "Sales",
      "aggregation": "sum"
    },

    {
      "title": "Monthly Sales Trend",
      "chart_type": "line",
      "dimension": "Order Date",
      "measure": "Sales",
      "aggregation": "sum",
      "time_grain": "month"
    },

    {
      "title": "Top 10 Products by Sales",
      "chart_type": "bar",
      "dimension": "Product",
      "measure": "Sales",
      "aggregation": "sum",
      "top_n": 10,
      "sort_direction": "desc"
    }
  ]
}
```

---

# DESIGN A BETTER INTENT ENGINE

Create a two-stage system.

## STAGE 1 — AI / NLP INTERPRETATION

Interpret:

- requested KPIs
- metrics
- dimensions
- aggregations
- comparisons
- trends
- periods
- rankings
- Top N
- filters
- chart requests
- page requests
- drill requests
- business objective
- requested formatting

## STAGE 2 — DETERMINISTIC VALIDATION

Never trust raw LLM output directly.

Validate:

```text
Does column exist?
Is metric numeric?
Is dimension categorical?
Is requested date column actually date-like?
Is aggregation valid?
Is Top N valid?
Does chart support requested fields?
```

If the LLM suggests:

```text
measure = Revenue
```

but the dataset contains:

```text
Sales Amount
```

perform semantic column matching.

If confidence is insufficient, do NOT invent a column.

Return a meaningful warning.

---

# COLUMN SEMANTIC MATCHING

Implement column normalization.

Examples:

```text
sales
Sales
SALES
total_sales
Sales Amount
sales_amount
Revenue
Net Sales
```

Do NOT automatically assume these are all identical.

Use:

1. exact match
2. normalized match
3. alias dictionary
4. semantic similarity
5. data-type compatibility
6. confidence score

Return the final mapping and confidence.

---

# FEATURE ROLE DETECTION

Each column should have a richer semantic role.

Possible roles:

```text
identifier
categorical_dimension
numeric_measure
date
datetime
geography
currency
percentage
boolean
text
ordinal
continuous_numeric
discrete_numeric
latitude
longitude
email
url
unknown
```

Do not infer roles only from pandas dtype.

Use:

- column name
- dtype
- cardinality
- uniqueness
- distribution
- sample values

---

# IDENTIFIER DETECTION

Avoid generating charts such as:

```text
Sales by Customer ID
```

when Customer ID has almost one value per row unless explicitly requested.

Possible identifier indicators:

```text
high uniqueness
ID-like name
sequential numbers
UUID pattern
order number
transaction ID
customer ID
invoice ID
```

Identifiers should usually not become chart dimensions automatically.

---

# ANALYSIS ENGINE

The project must continue supporting:

## Univariate analysis

Numeric:

- count
- mean
- median
- mode where useful
- standard deviation
- variance
- min
- max
- range
- quartiles
- IQR
- skewness
- kurtosis
- percentiles
- missing values
- outliers
- histogram statistics

Categorical:

- frequency
- percentage
- cardinality
- mode
- rare categories

Date:

- min date
- max date
- timespan
- frequency
- trends
- gaps

---

# BIVARIATE ANALYSIS

Support appropriate combinations:

```text
numeric vs numeric
numeric vs categorical
categorical vs categorical
date vs numeric
date vs categorical
```

Possible analysis:

- correlation
- covariance
- grouped aggregation
- cross-tabulation
- contingency analysis
- temporal aggregation

---

# MULTIVARIATE ANALYSIS

Support useful exploratory analysis where appropriate.

Possible techniques:

- correlation matrix
- multiple grouping
- pivot-like analysis
- multivariate comparisons
- interaction detection
- contribution analysis

Do NOT perform machine learning unless explicitly required.

Do NOT scale data merely because ML libraries are available.

---

# STATISTICAL ANALYSIS

Apply tests only when assumptions are reasonable.

Possible tests:

- Pearson correlation
- Spearman correlation
- chi-square
- t-test
- ANOVA
- normality checks where useful

Do NOT blindly run every test on every column.

Explain applicability.

---

# PROBABILITY ANALYSIS

Support meaningful probability/distribution analysis.

Potential distributions:

- normal
- binomial
- Poisson
- empirical distribution

Only use them where appropriate.

Do not force-fit distributions.

---

# BUSINESS KPI ENGINE

Do NOT automatically convert every numeric column into a KPI.

Infer useful business KPIs from:

- column semantics
- user requirement
- business relationships
- analysis results

Examples:

Sales dataset:

```text
Total Sales
Total Profit
Profit Margin
Order Count
Average Order Value
Quantity Sold
```

HR dataset:

```text
Employee Count
Average Salary
Attrition Rate
Average Tenure
```

Finance dataset:

```text
Revenue
Expenses
Gross Profit
Net Profit
Margin
Variance
```

E-commerce dataset:

```text
Revenue
Orders
Customers
Average Order Value
Units
```

User requirement always has higher priority than generic heuristics.

---

# KPI FORMULA ENGINE

Where appropriate, support derived KPIs.

Example:

```text
Profit Margin = Profit / Sales
```

But validate denominator.

Handle:

- divide-by-zero
- nulls
- formatting

Prefer explicit reusable measures.

---

# POWER BI MEASURE ENGINE

Build a proper semantic layer.

Do NOT calculate everything as preaggregated Python output if it should remain interactive in Power BI.

Support generation of DAX measures where appropriate.

Examples:

```DAX
Total Sales = SUM('Sales'[Sales])

Total Profit = SUM('Sales'[Profit])

Order Count = DISTINCTCOUNT('Sales'[Order ID])

Profit Margin = DIVIDE([Total Profit], [Total Sales])
```

Generate measure names safely.

Escape table/column names correctly.

Never generate invalid DAX.

---

# DATE TABLE

When date analytics is required, create a proper date/calendar table where appropriate.

Potential fields:

```text
Date
Year
Quarter
Month Number
Month
Year-Month
Week
Day
Day Name
```

Create relationships with fact date columns when reasonable.

Allow:

```text
Year → Quarter → Month → Date
```

drill hierarchy.

---

# MULTI-SHEET EXCEL

The application must support Excel files containing multiple sheets.

Do NOT simply merge sheets.

Analyze each sheet.

Determine:

```text
fact table
dimension table
lookup table
unrelated table
```

Infer possible relationships using:

- matching names
- data types
- uniqueness
- referential overlap
- cardinality

Examples:

```text
Orders.CustomerID → Customers.CustomerID

Orders.ProductID → Products.ProductID
```

Require high confidence before automatically creating relationships.

Avoid ambiguous many-to-many relationships unless explicitly supported.

---

# SEMANTIC MODEL

Create a proper Power BI semantic model.

Support:

- tables
- columns
- correct types
- relationships
- measures
- hierarchies
- formats
- hidden technical columns where appropriate
- sort-by-column
- display folders where reasonable

Prefer star-schema concepts when the input supports them.

Do NOT unnecessarily normalize a simple single-table dataset.

---

# DASHBOARD AI PLANNER

Create a dedicated component such as:

```text
dashboard/
    planner.py
```

The planner should consider:

```text
user intent
+
data schema
+
feature roles
+
statistics
+
business semantics
+
visualization best practices
```

Output only a valid `DashboardSpec`.

---

# DASHBOARD PLANNING PRIORITY

Chart priority must be:

```text
1. User explicitly requested it
2. Required to answer user's business question
3. Business-important KPI
4. Important trend/comparison
5. Statistically useful supporting insight
6. Generic exploratory chart
```

Do NOT fill a dashboard with charts merely because they are statistically possible.

---

# VISUAL RECOMMENDATION ENGINE

Choose charts based on analytical objective.

## Comparison

Use:

```text
bar chart
column chart
clustered bar/column
```

## Time trends

Use:

```text
line chart
area chart
combo chart
```

## Composition

Use carefully:

```text
stacked chart
100% stacked chart
treemap
donut
pie
```

Avoid pie/donut when category count is excessive.

## Distribution

Use:

```text
histogram
box-plot-style alternative if supported
```

## Relationship

Use:

```text
scatter chart
bubble chart
```

## Detail

Use:

```text
table
matrix
```

## Performance

Use:

```text
KPI
card
gauge where meaningful
```

## Contribution

Use:

```text
waterfall
```

## Process

Use:

```text
funnel
```

when semantically valid.

## Geography

Use map-related visuals only when valid geographical information exists.

Do not classify arbitrary text as geography.

---

# VISUAL TYPES TO SUPPORT

Architect support for at least:

```text
card
multi-row card
KPI
bar
stacked bar
100% stacked bar
column
stacked column
100% stacked column
line
area
stacked area
combo
pie
donut
treemap
scatter
bubble
waterfall
funnel
table
matrix
gauge
histogram
map-compatible specification
```

If a visualization cannot safely be generated into PBIR, mark it as partially supported rather than generating corrupted files.

---

# TOP N MUST ACTUALLY WORK

The current system may parse `top_n` but fail to apply it.

Fix this.

Example:

```text
Top 5 products by Sales
```

must produce:

```text
dimension = Product
measure = Sales
aggregation = SUM
sort = Sales descending
TopN = 5
```

Preview and Power BI must both show exactly five ranked products unless ties/Power BI behavior is explicitly configured otherwise.

---

# FILTER ENGINE

Support:

```text
report-level filters
page-level filters
visual-level filters
```

Represent filters semantically.

Example:

```json
{
  "column": "Region",
  "operator": "in",
  "values": ["West", "North"]
}
```

Support where appropriate:

```text
equals
not equals
contains
greater than
less than
between
in
not in
relative date
Top N
```

---

# SLICERS

Generate slicers when useful.

Examples:

```text
Date
Region
Category
Department
Product Category
Channel
```

Avoid creating slicers for:

- transaction IDs
- very high-cardinality fields
- raw measures

unless explicitly requested.

---

# INTERACTIVE CROSS FILTERING

Where supported by PBIR/report definitions, preserve Power BI visual interaction semantics.

At minimum design the internal architecture for:

```text
filter
highlight
none
```

for visual-to-visual interaction.

---

# DRILL-DOWN

Create hierarchies when appropriate.

Examples:

```text
Year
Quarter
Month
Date
```

or:

```text
Country
State
City
```

or:

```text
Category
Subcategory
Product
```

Support drilldown only if the hierarchy is semantically valid.

---

# DRILLTHROUGH

Architect support for drillthrough pages.

Example:

```text
Overview
    ↓
Product detail
```

User selecting:

```text
Laptop
```

can navigate to a detail page filtered to Laptop.

Implement only according to valid PBIR structures.

---

# TOOLTIPS

Support tooltip fields.

Example:

Sales by Region:

```text
Region
Sales
Profit
Profit Margin
Order Count
```

Support rich report-page tooltip architecture where technically appropriate.

---

# BOOKMARKS AND NAVIGATION

Architect support for:

```text
page navigation
bookmark navigation
reset filter button
back button
```

Do not create nonfunctional placeholder buttons.

Only include them in generated PBIP when technically valid.

---

# MULTI-PAGE REPORT GENERATION

Do not force everything onto one dashboard page.

AI planner should decide when multiple pages are useful.

Possible structure:

```text
Page 1 — Executive Overview

KPIs
high-level trend
business breakdown
slicers

Page 2 — Sales Analysis

regional sales
product sales
category analysis
channel analysis

Page 3 — Profitability

profit
margin
cost
waterfall
profit drivers

Page 4 — Detailed Data

matrix
table
drillthrough/detail
```

Pages must depend on dataset and user requirements.

Never use hard-coded page names when they are semantically inappropriate.

---

# CONDITIONAL FORMATTING

Architect support for:

```text
background color rules
font color rules
data bars
icons
thresholds
positive/negative indicators
variance highlighting
```

Use semantic rules.

Example:

```text
Profit < 0 → negative indicator
Profit > 0 → positive indicator
```

Do NOT hardcode a particular color palette into business logic.

Keep themes configurable.

---

# THEME ENGINE

Support configurable report themes.

Create an application default professional theme, but separate:

```text
theme specification
```

from:

```text
business logic
```

Allow:

```text
light
dark
corporate
custom
```

but do not modify visual meaning when a theme changes.

---

# DASHBOARD LAYOUT ENGINE

Create a layout planner.

Layout rules:

1. KPIs near top.
2. Most important visual gets priority.
3. Slicers grouped consistently.
4. Avoid overlaps.
5. Avoid excessive whitespace.
6. Maintain alignment.
7. Use reasonable visual dimensions.
8. Maintain consistent spacing.
9. Avoid too many visuals.
10. Use multiple pages instead of overcrowding.

Create deterministic layout coordinates.

Do not randomly place visuals.

---

# INSIGHT ENGINE

In addition to charts, generate short data-driven insights.

Examples:

```text
West region contributes 34% of total sales.

Profit margin decreased during Q3.

Product A is the highest revenue contributor.

Channel X has high revenue but low margin.
```

Insights must come from actual calculations.

Never hallucinate insights.

---

# PREVIEW REQUIREMENTS

The web preview must show the same business meaning as the Power BI output.

Preview should support, where practical:

- KPI cards
- charts
- filtering
- slicers
- tooltip
- sorting
- pagination for tables
- multi-page dashboard navigation
- Top N
- basic drill behavior
- theme

Again:

```text
DashboardSpec
```

must drive the preview.

Do NOT independently generate a second dashboard interpretation.

---

# USER MODIFICATION AFTER PREVIEW

This is a critical feature.

After preview, user must be able to request changes such as:

```text
Remove pie chart.

Change Sales by Region to horizontal bar.

Show top 5 products instead of top 10.

Add Profit Margin KPI.

Move the sales trend to first page.

Add Category slicer.

Remove Cost chart.

Create another page for Customer Analysis.
```

These instructions must modify the existing `DashboardSpec`.

Do NOT rerun everything from scratch unless required.

Architecture:

```text
Original DashboardSpec
        +
Modification Intent
        ↓
DashboardSpec Patcher
        ↓
Validation
        ↓
New Preview
```

---

# USER INTENT MUST OVERRIDE DEFAULT RECOMMENDATIONS

Example:

If statistical engine prefers a scatterplot but user explicitly requests:

```text
Show Sales by Region as bar chart
```

use bar chart as long as it is technically valid.

Only reject user instructions when:

```text
column doesn't exist
chart is impossible
instruction is ambiguous enough to produce wrong data
Power BI format does not support requested feature
```

Return a useful explanation instead of silently changing intent.

---

# POWER BI EXPORT FORMAT

Modernize the exporter.

Target a valid Power BI Project structure.

Prefer modern:

```text
PBIP
+
PBIR for report definition
+
TMDL for semantic model
```

where supported by current Power BI Desktop.

Do not invent schemas.

Use official Microsoft schemas and current PBIP conventions.

Conceptual target:

```text
GeneratedDashboard/
│
├── GeneratedDashboard.pbip
│
├── GeneratedDashboard.Report/
│   ├── definition.pbir
│   ├── definition/
│   │   ├── pages/
│   │   ├── visuals/
│   │   └── ...
│   └── StaticResources/
│
└── GeneratedDashboard.SemanticModel/
    ├── definition.pbism
    └── definition/
        ├── model.tmdl
        ├── database.tmdl
        ├── relationships.tmdl
        └── tables/
```

The exact structure MUST follow current Microsoft specifications.

If the installed Power BI version requires TMSL instead of TMDL, support an explicit compatibility mode.

Never generate mutually incompatible combinations.

---

# PBIR RULE

Do not generate a fake or guessed PBIR JSON structure.

Before implementing each PBIR component:

1. inspect current Microsoft schema,
2. inspect existing valid PBIP examples if available,
3. build schema-valid output,
4. validate JSON,
5. validate references.

---

# SEMANTIC MODEL RULE

Never reference a field that doesn't exist.

Before generating Power BI:

```text
For every visual:
    validate dimension
    validate measure
    validate aggregation
    validate legend
    validate sort field
    validate tooltip fields
    validate drill fields
    validate filter fields
```

If even one reference is invalid:

```text
DO NOT silently export.
```

Return a structured validation error.

---

# CREATE A POWER BI VALIDATOR

Implement something like:

```text
powerbi/
    validator.py
```

Validation should include:

```text
project structure
required files
valid JSON
valid semantic-model references
missing fields
duplicate IDs
missing visual references
invalid measure names
invalid relationships
broken filters
invalid page references
invalid drillthrough references
invalid sort columns
```

Create:

```python
validate_before_export()
```

Power BI package generation should fail cleanly if validation fails.

---

# DUPLICATED APPLICATION ARCHITECTURE

The project currently appears to have parallel implementations:

```text
analysis/
dashboard/
app/
```

and:

```text
src/bi_automation/
```

The runtime may follow something similar to:

```text
START.bat
→ main.py
→ src/bi_automation/web/app.py
→ app/controllers/flask_app.py
→ app/workflow/pipeline.py
```

This means edits to one pipeline may not affect the actual running application.

## REQUIRED ACTION

Trace the exact runtime import graph.

Produce a dependency/runtime map.

Determine:

```text
ACTIVE
LEGACY
UNUSED
DUPLICATED
```

for major modules.

Create ONE canonical implementation under:

```text
src/bi_automation/
```

preferably:

```text
src/bi_automation/
│
├── ingestion/
├── profiling/
├── preprocessing/
├── analysis/
├── intent/
├── semantic/
├── dashboard/
├── preview/
├── powerbi/
├── services/
├── models/
├── validation/
├── web/
└── utils/
```

However:

Do NOT immediately delete legacy files.

First:

1. migrate,
2. redirect imports,
3. run regression tests,
4. verify UI,
5. mark legacy modules deprecated.

Only remove files when references are proven absent.

---

# SEPARATE RESPONSIBILITIES

Avoid huge classes.

Create clear modules.

Suggested high-level responsibilities:

```text
ExcelReader
SchemaDetector
DataProfiler
DataCleaner
FeatureRoleDetector
AnalysisEngine
IntentParser
IntentValidator
KPIPlanner
VisualPlanner
DashboardPlanner
DashboardValidator
PreviewRenderer
DashboardModifier
SemanticModelBuilder
DAXMeasureBuilder
PowerBIReportBuilder
PBIPPackager
PowerBIValidator
```

---

# DO NOT HARDCODE DATASET-SPECIFIC LOGIC

Never write:

```python
if "Sales" in columns:
```

as the primary architecture.

The application must work with:

```text
sales
finance
HR
inventory
healthcare
marketing
education
operations
manufacturing
customer support
travel
banking
```

Use semantic detection.

Dataset-specific aliases can exist in configurable dictionaries but not inside generic pipeline logic.

---

# ERROR HANDLING

Every stage should return structured errors.

Example:

```json
{
  "success": false,
  "stage": "dashboard_validation",
  "code": "INVALID_MEASURE",
  "message": "Requested metric Revenue was not found.",
  "details": {}
}
```

Do NOT:

- swallow exceptions,
- use bare `except`,
- silently replace failure with zero,
- automatically continue after critical errors.

---

# LOGGING

Implement structured logs for important operations.

Example:

```text
[INGESTION]
[PROFILING]
[INTENT]
[ANALYSIS]
[DASHBOARD_PLAN]
[PREVIEW]
[POWERBI_MODEL]
[POWERBI_REPORT]
[VALIDATION]
```

Do not log sensitive raw data unnecessarily.

---

# PERFORMANCE

The application should remain usable with realistically sized Excel files.

Avoid:

```text
nested row loops
repeated full dataframe scans
repeating expensive analysis
regenerating unchanged dashboard components
```

Cache safe deterministic intermediate results using a dataset/configuration fingerprint where useful.

---

# SECURITY

Treat uploaded Excel content as untrusted.

Validate:

- file extension
- MIME/type where possible
- file size
- sheet names
- unsupported formulas/content
- invalid path names

Prevent:

- path traversal
- arbitrary file overwrite
- command injection
- unsafe deserialization
- untrusted code execution

Never execute Excel-provided strings as Python.

---

# AUTOMATED TESTING — REQUIRED

Do NOT consider the project finished without tests.

Create/update:

```text
tests/
```

Use `pytest` where appropriate.

---

# TEST 1 — SELECTED COLUMNS REMAIN SELECTED

Input has:

```text
11 columns
```

User selects only:

```text
Order ID
Order Date
Region
```

Expected Phase 2 dataset:

```text
exactly 3 columns
```

No original unselected columns may reappear.

---

# TEST 2 — ANALYSIS SELECTION

User selects only:

```text
Univariate
```

Expected:

```text
univariate > 0

bivariate = 0
multivariate = 0
statistical = 0
probability = 0
```

---

# TEST 3 — NATURAL LANGUAGE INTENT

Input:

```text
Show total sales, total profit, sales by region,
monthly sales trend and top 10 products by sales.
```

Expected:

```text
2 KPIs
3 visuals
```

with exact semantic mappings.

---

# TEST 4 — TOP N

Requirement:

```text
Top 5 products by sales
```

Preview must contain 5 ranked products.

Power BI specification must contain equivalent Top N semantics.

---

# TEST 5 — AGGREGATION CONSISTENCY

Requirement:

```text
Average sales by channel
```

Expected:

```text
Preview = Average
Power BI = Average
```

NOT:

```text
Preview = Average
Power BI = Sum
```

---

# TEST 6 — NO FAKE FIELDS

No exported visual may reference:

```text
Count
Frequency
```

unless such columns genuinely exist.

Row count and histogram frequencies must use proper semantic calculation.

---

# TEST 7 — FAILURE STATE

Force an ingestion failure.

Expected:

```text
success = false
```

Frontend must display failure.

It must NOT proceed because of `or True` logic.

---

# TEST 8 — MISSING VALUES

Use known missing values.

UI data quality results must exactly match backend result.

---

# TEST 9 — OUTLIERS

Create a dataset with known outliers.

Backend and preview must show the same count.

---

# TEST 10 — MULTIPLE SHEETS

Test:

```text
Orders
Customers
Products
```

Verify relationship inference without incorrect merging.

---

# TEST 11 — DIFFERENT BUSINESS DOMAINS

Create sample datasets for:

```text
Sales
HR
Finance
Inventory
```

The application must generate context-appropriate KPIs/charts.

---

# TEST 12 — NONSTANDARD COLUMN NAMES

Example:

```text
Net_Revenue_INR
Txn_Date
Cust_No
Item_Group
```

Ensure semantic detection still works.

---

# TEST 13 — IDENTIFIERS

Ensure transaction IDs don't become default chart dimensions.

---

# TEST 14 — BAD USER REQUEST

Example:

```text
Show revenue by country
```

Dataset contains neither revenue nor country.

Expected:

structured warning.

Never hallucinate fields.

---

# TEST 15 — PBIP VALIDATION

Generated project must pass internal PBIP validation.

All referenced:

```text
pages
visuals
tables
columns
measures
relationships
filters
```

must exist.

---

# TEST 16 — OPEN IN POWER BI DESKTOP

Where Power BI Desktop is available on the machine:

Generate a real test PBIP.

Open it.

Verify:

```text
project loads
semantic model loads
pages load
visuals appear
no broken field references
no missing schema files
```

If Power BI Desktop cannot be programmatically opened in the environment, clearly report this limitation and still perform structural/schema validation.

---

# UPDATE OUTDATED TESTS

Existing tests may call something similar to:

```python
pipeline.run()
```

while the current API uses:

```python
run_phase1()
run_phase2()
```

Update the tests.

Do NOT preserve outdated tests merely to avoid changing them.

---

# TEST DATASETS

Create controlled synthetic test fixtures.

Example Sales dataset:

```text
Order ID
Order Date
Region
Product
Category
Channel
Sales
Cost
Profit
Quantity
Customer ID
```

Generate known expected totals to make assertions deterministic.

---

# DASHBOARD QUALITY VALIDATION

Build a dashboard quality checker.

Check:

```text
duplicate charts
too many visuals
invalid dimensions
invalid measures
wrong aggregation
overcrowded page
too many pie categories
identifier used incorrectly
chart title mismatch
Top N not applied
missing user requirement
user requirement represented twice
```

---

# REQUIREMENT COVERAGE SCORE

This is important.

After dashboard generation, compute requirement coverage.

Example:

User asked:

```text
Total Sales
Total Profit
Sales by Region
Monthly Trend
Top 10 Products
```

Create:

```text
Requirement Coverage:

Total Sales          ✅
Total Profit         ✅
Sales by Region      ✅
Monthly Trend        ✅
Top 10 Products      ✅

Coverage = 5 / 5 = 100%
```

Do NOT finalize a dashboard if important user requirements are missing without explicitly warning.

---

# DATA-TO-VISUAL LINEAGE

Every visual should be traceable.

Example:

```text
Visual:
Sales by Region

Source table:
Orders

Dimension:
Region

Measure:
Total Sales

Aggregation:
SUM

Filters:
None

Top N:
None
```

Maintain this in internal metadata.

This is useful for debugging and validation.

---

# USER-FACING EXPLANATION

After dashboard creation, provide a summary such as:

```text
Dashboard generated from 15,420 rows and 11 columns.

Detected:
4 measures
3 categorical dimensions
1 date field
2 identifiers

Created:
4 KPIs
6 charts
2 slicers
3 pages

User requirement coverage:
100%
```

Do not expose internal stack traces to ordinary users.

---

# IMPORTANT ENGINEERING RULE — LLM IS NOT THE SOURCE OF TRUTH

Gemini/AI may help interpret user intent.

But the LLM must NOT directly generate unchecked PBIR/TMDL output.

Use:

```text
User request
↓
LLM Intent Interpretation
↓
Structured JSON/Pydantic model
↓
Deterministic Validation
↓
DashboardSpec
↓
Deterministic Renderer
```

This prevents hallucinated Power BI fields.

---

# ARCHITECTURE TARGET

Final architecture should approximately be:

```text
                        USER
                         │
                         ▼
                 Excel Upload
                         │
                         ▼
                Ingestion Layer
                         │
                         ▼
              Schema Detection
                         │
                         ▼
                 Profiling
                         │
                         ▼
               Preprocessing
                         │
                         ▼
            Feature Role Detection
                         │
                         ▼
               User Requirement
                         │
                         ▼
             AI Intent Interpreter
                         │
                         ▼
             Intent Validator
                         │
                         ▼
        ┌─────────────────────────┐
        │ Dashboard Intelligence  │
        └─────────────────────────┘
             │               │
             ▼               ▼
        KPI Planner     Visual Planner
             │               │
             └───────┬───────┘
                     ▼
               DashboardSpec
                     │
             Dashboard Validator
                     │
            ┌────────┴─────────┐
            ▼                  ▼
       Web Preview      Semantic Model
                              │
                         Power BI Report
                              │
                         PBIP Validator
                              │
                              ▼
                     Downloadable PBIP
```

---

# IMPLEMENTATION PHASES

Do NOT attempt a giant uncontrolled rewrite.

Perform changes in these phases.

## PHASE 0 — REPOSITORY AUDIT

Before changing code:

1. inspect repository tree,
2. find application entry point,
3. trace runtime imports,
4. identify duplicate implementations,
5. identify current models,
6. identify current tests,
7. identify current frontend API contracts,
8. identify Power BI generator.

Produce a short internal migration map.

Then start implementation.

Do NOT stop after the audit.

---

# PHASE 1 — FIX CRITICAL PIPELINE DEFECTS

Fix:

```text
duplicate pipeline execution
selected-column reset
analysis selection reset
wrong processing order
failure handling
data-quality schema mismatch
```

Run tests.

Do not proceed until they pass.

---

# PHASE 2 — INTRODUCE CANONICAL DOMAIN MODELS

Implement:

```text
DatasetProfile
FeatureProfile
AnalysisConfig
DashboardIntent
KPIIntent
VisualSpec
PageSpec
DashboardSpec
DataQualitySummary
```

Use Pydantic/dataclasses.

Add validation.

---

# PHASE 3 — REBUILD INTENT PARSING

Replace fragile keyword-only interpretation with structured semantic interpretation plus deterministic validation.

Test complex user requirements.

---

# PHASE 4 — DASHBOARD PLANNER

Implement goal-aware:

```text
KPI planning
visual planning
page planning
filter planning
slicer planning
layout planning
```

---

# PHASE 5 — PREVIEW

Make preview consume `DashboardSpec`.

Remove duplicated visualization business logic from preview renderer.

---

# PHASE 6 — SEMANTIC MODEL

Implement:

```text
tables
relationships
measures
hierarchies
date table
formats
```

---

# PHASE 7 — MODERN POWER BI EXPORTER

Upgrade toward valid:

```text
PBIP
PBIR
TMDL
```

according to current Microsoft documentation/schema.

---

# PHASE 8 — USER DASHBOARD MODIFICATION ENGINE

Implement natural-language modifications against an existing DashboardSpec.

---

# PHASE 9 — FULL REGRESSION TESTS

Run:

```text
unit tests
integration tests
end-to-end tests
PBIP structure validation
```

---

# PHASE 10 — CLEANUP

After everything works:

1. remove dead imports,
2. mark legacy code,
3. remove confirmed dead code,
4. update README,
5. update architecture documentation.

---

# DO NOT CHANGE WORKING UI UNNECESSARILY

The current UI is not the primary problem.

Prioritize:

```text
correctness
intent understanding
analysis
semantic modeling
Power BI generation
validation
```

Do not waste the implementation effort redesigning colors/buttons unless necessary for the workflow.

---

# PRESERVE EXISTING USER FLOW

The user should still have a simple experience.

## STEP 1

Upload Excel.

## STEP 2

System automatically analyzes it.

## STEP 3

User selects/adjusts:

```text
features
analysis types
dashboard requirement
```

## STEP 4

System generates preview.

## STEP 5

User can say:

```text
Looks good
```

or request modifications.

## STEP 6

System generates Power BI project.

---

# FINAL QUALITY REQUIREMENT

I do NOT want a system that merely generates charts.

I want a system that understands:

```text
What is this dataset?

Which fields are dimensions?

Which fields are measures?

What does the user want to know?

Which KPIs answer that question?

Which visual best communicates that answer?

Which aggregation is correct?

Which filters are relevant?

How should pages be organized?

How should the semantic model be constructed?

Will the resulting Power BI project actually work?
```

The application must answer these questions systematically.

---

# IMPORTANT: DO NOT OVER-ENGINEER

Prefer:

```text
clear
tested
maintainable
modular
deterministic
```

over complicated AI agents everywhere.

AI should mainly be used for:

```text
semantic understanding
business-context inference
user intent interpretation
dashboard recommendation
```

Deterministic Python should handle:

```text
data processing
statistics
validation
aggregation
specification validation
Power BI file generation
```

---

# POWER BI CAPABILITY MATRIX

Create documentation:

`docs/POWER_BI_CAPABILITY_MATRIX.md`

Use categories:

```text
Capability
Implementation Status
Local Preview
PBIP Export
Requires Power BI Service
Notes
```

Cover at least:

```text
Excel import
multi-sheet import
Power Query-like transformations
data types
relationships
DAX measures
calculated measures
date tables
hierarchies
cards
bar charts
column charts
line charts
area charts
pie/donut
treemap
scatter
waterfall
funnel
table
matrix
gauge
maps
filters
slicers
Top N
sorting
conditional formatting
drilldown
drillthrough
tooltips
bookmarks
navigation
multi-page reports
themes
mobile layout
RLS
refresh
publishing
workspaces
subscriptions
alerts
gateways
Fabric integration
```

Never mark something `Supported` unless it actually works.

---

# DOCUMENTATION

Update README with:

```text
architecture
installation
Windows setup
running application
supported Excel formats
workflow
supported analyses
Power BI capabilities
limitations
testing
troubleshooting
project structure
```

Also explain:

```text
Preview and final Power BI dashboard are generated from the same DashboardSpec.
```

---

# REQUIRED OUTPUT FROM YOU AFTER IMPLEMENTATION

When you complete the code changes, give me a report with these sections:

## 1. Root Causes Found

List every actual issue discovered.

## 2. Files Modified

For each file:

```text
file path
what changed
why
```

## 3. Architecture Changes

Show before and after.

## 4. Bugs Fixed

Report status:

```text
FIXED
PARTIALLY FIXED
NOT APPLICABLE
BLOCKED
```

## 5. New Functionalities

List everything added.

## 6. Power BI Capability Matrix

Summarize support.

## 7. Tests Executed

For every test:

```text
name
input
expected
actual
pass/fail
```

## 8. Remaining Limitations

Be transparent.

## 9. How to Run

Give Windows commands.

## 10. How to Validate

Give exact steps for testing:

```text
Excel upload
requirement
preview
modification
PBIP generation
Power BI Desktop opening
```

---

# ACCEPTANCE SCENARIO

Use at least this scenario before considering the project complete.

Input Excel columns:

```text
Order ID
Order Date
Region
Product
Category
Channel
Sales
Cost
Profit
Quantity
Customer ID
```

User requirement:

```text
Create an executive sales dashboard.

Show Total Sales, Total Profit, Profit Margin and Order Count.

Show monthly Sales and Profit trends.

Compare Sales and Profit by Region.

Show top 10 Products by Sales.

Show Category performance.

Show Channel performance.

Add Region, Category and Date filters.

Create a separate detailed Product Analysis page.

Allow drill-down from Category to Product.

Use a professional dashboard design.
```

Expected interpretation:

### KPIs

```text
Total Sales
Total Profit
Profit Margin
Order Count
```

### Executive Overview

```text
KPI cards
Monthly Sales/Profit trend
Sales/Profit by Region
Category performance
Region slicer
Category slicer
Date slicer
```

### Product Analysis

```text
Top 10 Products by Sales
Product Profit
Product Sales
Category → Product drill hierarchy
Detailed matrix/table
```

### Channel

Include Channel analysis either on overview or suitable second page according to layout quality.

### Validation

The final Power BI report must NOT contain:

```text
fake Count columns
fake Frequency columns
missing fields
wrong aggregation
unselected columns accidentally restored
generic charts unrelated to the requirement
```

---

# DEFINITION OF DONE

Do NOT say the project is complete just because:

```text
application runs
```

It is complete only when:

```text
pipeline respects user configuration
+
intent parser correctly understands requirements
+
dashboard specification is valid
+
preview matches dashboard specification
+
Power BI output matches dashboard specification
+
no fake fields exist
+
valid semantic model is generated
+
user modifications work
+
automated tests pass
+
Power BI project structure is validated
+
documented limitations are accurate
```

---

# FINAL INSTRUCTION

Start by analyzing the current repository.

Do NOT rewrite everything blindly.

Do NOT only provide recommendations.

Implement the fixes directly.

After every major phase:

```text
run tests
inspect failures
fix failures
continue
```

Do not hide errors.

Do not claim unsupported Power BI capabilities.

Use current official Microsoft Power BI PBIP/PBIR/TMDL specifications when generating Power BI project files.

The highest priorities are:

```text
1. Correct user intent
2. Correct calculations
3. Correct semantic model
4. Correct visual specifications
5. Preview = final Power BI meaning
6. Valid Power BI project
7. Good user experience
8. Extensible architecture
```

Proceed with implementation now.