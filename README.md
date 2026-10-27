Smart Expense Tracker

A beginner-friendly Python program for recording and reviewing expenses. It stores entries in a CSV file and uses pandas and NumPy for analysis. Matplotlib and Seaborn create the charts.

## Project files

- `program/expense_tracker.py` — application and interactive menu.
- `data/expenses.csv` — sample expense data; new expenses are saved here.
- `setup/README.md` — setup and run instructions.

## Requirements

Python 3.10 or newer.

## Install

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r setup/requirements.txt
```

## Start the program

From the project folder, run:

```powershell
python program/expense_tracker.py
```

Use the menu to add an expense, view summaries, filter expenses, print a report, or generate charts. Dates must use `YYYY-MM-DD`; amounts must be positive numbers. The program checks the CSV and ignores rows with invalid dates, nonpositive amounts, or blank categories.

Charts are saved to `program/figures/`. If Matplotlib or Seaborn is missing, install the dependencies using the command above.
