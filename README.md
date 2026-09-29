# BI Report Automation — Windows Setup & Run Guide

This guide explains how to set up and run **BI Report Automation** on another Windows computer.

The application takes an Excel workbook as input, performs automated data preprocessing and statistical analysis, generates a dashboard preview, and prepares a Power BI project locally.

All dataset processing is performed on the local machine.

---

## 1. System Requirements

Recommended environment:

- Windows 10 or Windows 11 — 64-bit
- Python 3.11 — 64-bit recommended
- Git — optional, required only for cloning the repository
- Power BI Desktop — required for opening/finalizing the generated Power BI report
- Minimum 4 GB RAM
- 8 GB RAM or more recommended for larger Excel files

---

# 2. Install Python

Install **Python 3.11 64-bit**.

During Python installation, make sure to select:

```text
Add Python to PATH
```

After installation, open **Command Prompt** and verify Python:

```bash
python --version
```

Expected output will be similar to:

```text
Python 3.11.x
```

You can also check pip:

```bash
pip --version
```

---

# 3. Install Git — Optional

Git is only required if you want to clone the project directly from GitHub.

After installing Git, verify it:

```bash
git --version
```

If Git is not installed, you can download the repository as a ZIP file from GitHub and extract it manually.

---

# 4. Download the Project

## Option A — Using Git

Open Command Prompt in the folder where you want to keep the project.

Run:

```bash
git clone <REPOSITORY_URL>
```

Then:

```bash
cd BI_report_automation
```

---

## Option B — Download ZIP

From the GitHub repository:

```text
Code
↓
Download ZIP
```

Extract the ZIP file.

Open the extracted folder:

```text
BI_report_automation
```

---

# 5. Open Command Prompt in the Project Folder

The project folder should contain files similar to:

```text
BI_report_automation/
│
├── analysis/
├── app/
├── dashboard/
├── ingestion/
├── powerbi/
├── preprocessing/
├── security/
├── tests/
│
├── config.py
├── main.py
├── requirements.txt
└── START.bat
```

Open Command Prompt inside this folder.

One simple method is:

```text
1. Open the project folder in File Explorer
2. Click the address bar
3. Type cmd
4. Press Enter
```

---

# 6. Create a Python Virtual Environment

Creating a virtual environment is strongly recommended.

Run:

```bash
python -m venv venv
```

Activate it using:

```bash
venv\Scripts\activate
```

After activation, the terminal should look similar to:

```text
(venv) C:\...\BI_report_automation>
```

---

## PowerShell Users

If using PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

---

# 7. Upgrade pip

Run:

```bash
python -m pip install --upgrade pip
```

---

# 8. Install Project Dependencies

Install all Python libraries using:

```bash
pip install -r requirements.txt
```

The project currently uses libraries including:

```text
pandas
numpy
scipy
statsmodels
openpyxl
xlrd
matplotlib
seaborn
Flask
Jinja2
```

Wait until installation completes without errors.

---

# 9. Verify Installation

Optional but recommended:

```bash
pip list
```

Verify that the required packages are installed.

You can also run:

```bash
python -c "import pandas, numpy, scipy, flask, openpyxl; print('Dependencies OK')"
```

Expected output:

```text
Dependencies OK
```

---

# 10. Install Power BI Desktop

Power BI Desktop is required if you want to open and finalize the generated Power BI project.

Install the latest **64-bit Power BI Desktop** on Windows.

After installation:

```text
Start Menu
↓
Search "Power BI Desktop"
↓
Open Power BI Desktop
```

Confirm that Power BI Desktop launches correctly before using the export functionality.

> Power BI Desktop is not required for running the Python analysis and dashboard preview, but it is required for working with the generated Power BI project and saving the final report as `.pbix`.

---

# 11. Start the Application

There are two methods.

## Method 1 — Recommended

From the activated virtual environment:

```bash
python main.py
```

The application will start the local Flask server.

The browser should automatically open the application on:

```text
127.0.0.1:5050
```

---

## Method 2 — Using START.bat

You can also double-click:

```text
START.bat
```

or run:

```bash
START.bat
```

The batch file automatically executes:

```bash
python main.py
```

---

# 12. Expected Startup

The terminal should display messages similar to:

```text
BI Report Automation — Starting

All data processing is LOCAL.
No external connections.

Running on 127.0.0.1:5050
```

Your default web browser should open automatically.

If it does not open automatically, manually enter:

```text
127.0.0.1:5050
```

into the browser address bar.

---

# 13. Using the Application

After the application opens:

### Step 1 — Upload Excel

Click:

```text
Choose Excel File
```

or drag and drop an Excel workbook.

Supported formats:

```text
.xlsx
.xls
.xlsm
```

Maximum upload size:

```text
200 MB
```

---

### Step 2 — Start Analysis

Click:

```text
Start Analysis
```

The application automatically performs processing such as:

```text
Reading Excel

Profiling Data

Detecting Data Types

Cleaning Data

Handling Missing Values

Detecting Outliers

Running Univariate Analysis

Running Bivariate Analysis

Running Multivariate Analysis

Running Statistical Analysis

Running Probability Analysis

Generating Insights

Detecting KPIs

Selecting Charts

Building Dashboard Preview
```

---

# 14. Dashboard Preview

After analysis completes, the system displays a dashboard preview.

Review:

- KPI cards
- Charts
- Trends
- Statistical insights
- Data quality information
- Business insights

If the dashboard is acceptable, approve it.

---

# 15. Generate the Power BI Project

After approval, the system prepares a Power BI project locally.

The generated files are stored in the project's local output/temp directories.

No cloud service is required for the Python analysis pipeline.

---

# 16. Important: PBIX Generation

The current project **does not directly create a `.pbix` file programmatically**.

Power BI Desktop does not provide a supported command-line method in this project for automatically converting the generated project into `.pbix`.

The application therefore generates a Power BI project bundle.

The normal workflow is:

```text
Excel
   ↓
Python Analysis
   ↓
Dashboard Preview
   ↓
Approve Dashboard
   ↓
Power BI Project Bundle
   ↓
Open in Power BI Desktop
   ↓
File → Save As
   ↓
.pbix
```

If the application downloads a ZIP file:

```text
1. Extract the ZIP
2. Locate the .pbip project file
3. Open it using Power BI Desktop
4. Allow the model/data to load
5. Go to File
6. Select Save As
7. Save the report as a Power BI (.pbix) file
```

---

# 17. Generated Folders

During execution the application automatically uses:

```text
temp/
```

for temporary project files and:

```text
outputs/
```

for generated Power BI output files.

These directories are created automatically if they do not already exist.

---

# 18. Stop the Application

Go to the Command Prompt where the application is running.

Press:

```text
Ctrl + C
```

This stops the local Flask server.

Then deactivate the Python virtual environment:

```bash
deactivate
```

---

# 19. Running the Application Again

For future use, you do **not** need to reinstall dependencies.

Open the project folder and run:

```bash
venv\Scripts\activate
```

Then:

```bash
python main.py
```

Alternatively:

```text
START.bat
```

---

# 20. Quick Start

After completing the first-time installation, the normal startup process is simply:

```bash
cd BI_report_automation
venv\Scripts\activate
python main.py
```

Then:

```text
Upload Excel
↓
Start Analysis
↓
Review Dashboard
↓
Approve
↓
Download Power BI Project
↓
Open in Power BI Desktop
↓
Save As .pbix
```

---

# Troubleshooting

## `python` is not recognized

Example:

```text
'python' is not recognized as an internal or external command
```

Python is either not installed or was not added to PATH.

Reinstall Python and enable:

```text
Add Python to PATH
```

Or try:

```bash
py --version
```

and:

```bash
py main.py
```

---

## `pip` is not recognized

Use:

```bash
python -m pip install -r requirements.txt
```

instead of:

```bash
pip install -r requirements.txt
```

---

## ModuleNotFoundError

Example:

```text
ModuleNotFoundError: No module named 'pandas'
```

Make sure the virtual environment is activated:

```bash
venv\Scripts\activate
```

Then reinstall dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Flask Port 5050 Already in Use

If another application is using port `5050`, close that application and restart BI Report Automation.

You can check the port using:

```bash
netstat -ano | findstr :5050
```

Find the PID and terminate the process if appropriate:

```bash
taskkill /PID <PID> /F
```

Then start again:

```bash
python main.py
```

---

## Power BI Desktop Is Not Opening

First verify Power BI Desktop is installed.

Open it manually from:

```text
Start Menu → Power BI Desktop
```

The application checks common Power BI Desktop installation locations.

If it cannot locate Power BI Desktop automatically, you can still download the generated Power BI project bundle and open it manually.

---

## `.pbip` File Does Not Open

Use the **latest version of Power BI Desktop**.

If Power BI reports that the generated PBIP project structure is invalid or unsupported, the Power BI export module may need to be updated to the latest PBIP/PBIR project schema.

This does **not** affect the Python Excel analysis or browser dashboard preview.

---

## Excel File Is Not Accepted

Supported file types are:

```text
.xlsx
.xls
.xlsm
```

Maximum file size:

```text
200 MB
```

Make sure:

- The workbook is not corrupted
- The workbook contains data
- At least one worksheet contains a usable table
- The Excel file is not password protected
- The first useful row contains recognizable column headers

---

# Local Data Privacy

The project is designed to process Excel data locally.

The main analysis pipeline does not require:

```text
OpenAI API
Gemini API
Anthropic API
AWS
Azure Storage
Supabase
Firebase
External database
Cloud analytics API
```

Uploaded business data is processed by local Python modules.

Temporary processing files are cleaned by the application's privacy utilities.

---

# Recommended Production Setup

For another employee or Windows computer, the recommended configuration is:

```text
Windows 10/11 64-bit
        +
Python 3.11 64-bit
        +
Python Virtual Environment
        +
requirements.txt
        +
Latest Power BI Desktop 64-bit
        +
BI Report Automation Repository
```

Then run:

```text
START.bat
```

or:

```bash
venv\Scripts\activate
python main.py
```

---

# Current Power BI Limitation

The analysis and dashboard-preview portions of the system can run fully locally.

However, the current exporter does not perform an automatic `.pbip → .pbix` conversion.

The final `.pbix` should therefore be created using:

```text
Power BI Desktop
→ Open generated Power BI Project
→ File
→ Save As
→ Power BI Report (.pbix)
```

Do not rename `.zip`, `.pbip`, or another file to `.pbix`, because that does not create a valid Power BI file.
