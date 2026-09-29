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