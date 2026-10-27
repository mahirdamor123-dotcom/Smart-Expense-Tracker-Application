"""Learning starter for the Smart Expense Tracker exam project.

Complete the TODOs, run the program, and make sure you can explain your code.
"""
from pathlib import Path
import pandas as pd
import numpy as np

try:
    import matplotlib.pyplot as plt  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency for plotting
    plt = None

try:
    import seaborn as sns  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency for plotting
    sns = None

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT.parent / "data" / "expenses.csv"
FIGURES_DIR = ROOT / "figures"
COLUMNS = ["Date", "Amount", "Category", "Description"]


class ExpenseTracker:
    """Store expense records and provide analysis operations."""

    def __init__(self, file_path=DATA_FILE):
        self.file_path = Path(file_path)
        self.data = pd.DataFrame(columns=COLUMNS)

        if not self.file_path.exists():
            print(f"No expense file found at {self.file_path}; starting with an empty tracker.")
            return

        try:
            self.data = pd.read_csv(self.file_path)
        except Exception as exc:  # pragma: no cover - defensive fallback
            raise ValueError(f"Could not read expense file {self.file_path}: {exc}") from exc

        missing = [column for column in COLUMNS if column not in self.data.columns]
        if missing:
            raise ValueError(f"Expense file is missing required columns: {missing}")

        self.data["Date"] = pd.to_datetime(self.data["Date"], errors="coerce")
        self.data["Amount"] = pd.to_numeric(self.data["Amount"], errors="coerce")
        self.data["Category"] = self.data["Category"].fillna("").astype(str).str.strip()
        self.data["Description"] = self.data["Description"].fillna("").astype(str).str.strip()
        self.data = self.data.dropna(subset=["Date", "Amount"])
        self.data = self.data[(self.data["Amount"] > 0) & (self.data["Category"] != "")]
        self.data = self.data.reset_index(drop=True)

    def add_expense(self, date, amount, category, description):
        """Validate and add one expense row, then persist it to CSV."""
        try:
            parsed_date = pd.to_datetime(date, format="%Y-%m-%d", errors="raise")
        except Exception as exc:
            raise ValueError(f"Invalid date: {date}") from exc

        try:
            parsed_amount = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Amount must be numeric: {amount}") from exc

        if not np.isfinite(parsed_amount) or parsed_amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        category_text = str(category).strip()
        description_text = str(description).strip()
        if not category_text:
            raise ValueError("Category cannot be empty.")

        new_row = {
            "Date": parsed_date.strftime("%Y-%m-%d"),
            "Amount": parsed_amount,
            "Category": category_text,
            "Description": description_text,
        }

        self.data = pd.concat([self.data, pd.DataFrame([new_row], columns=COLUMNS)], ignore_index=True)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data.to_csv(self.file_path, index=False)
        return new_row

    def get_summary(self):
        """Return total, average, category totals, and monthly totals."""
        if self.data.empty:
            return {
                "total": 0.0,
                "average": 0.0,
                "num_entries": 0,
                "category_totals": {},
                "monthly_totals": {},
            }

        total = float(self.data["Amount"].sum())
        average = float(np.mean(self.data["Amount"]))

        category_totals = (
            self.data.groupby("Category")["Amount"].sum().sort_values(ascending=False).to_dict()
        )
        monthly_totals = (
            self.data.assign(Month=pd.to_datetime(self.data["Date"]).dt.to_period("M").astype(str))
            .groupby("Month")["Amount"].sum()
            .sort_index()
            .to_dict()
        )

        return {
            "total": total,
            "average": average,
            "num_entries": len(self.data),
            "category_totals": category_totals,
            "monthly_totals": monthly_totals,
        }

    def filter_expenses(self, category=None, start_date=None, end_date=None,
                        min_amount=None, max_amount=None):
        """Return rows matching whichever filters the caller supplied."""
        filtered = self.data.copy()

        if category is not None:
            category_value = str(category).strip()
            if not category_value:
                raise ValueError("Category filter cannot be empty.")
            filtered = filtered[filtered["Category"].str.lower() == category_value.lower()]

        if start_date is not None:
            start = pd.to_datetime(start_date, errors="raise")
            filtered = filtered[filtered["Date"] >= start]

        if end_date is not None:
            end = pd.to_datetime(end_date, errors="raise")
            filtered = filtered[filtered["Date"] <= end]

        if start_date is not None and end_date is not None:
            if pd.to_datetime(start_date) > pd.to_datetime(end_date):
                raise ValueError("Start date cannot be after end date.")

        if min_amount is not None:
            min_value = float(min_amount)
            if min_value < 0:
                raise ValueError("Minimum amount cannot be negative.")
            filtered = filtered[filtered["Amount"] >= min_value]

        if max_amount is not None:
            max_value = float(max_amount)
            if max_value < 0:
                raise ValueError("Maximum amount cannot be negative.")
            filtered = filtered[filtered["Amount"] <= max_value]

        if min_amount is not None and max_amount is not None and min_value > max_value:
            raise ValueError("Minimum amount cannot be greater than maximum amount.")

        return filtered.reset_index(drop=True)

    def generate_report(self):
        """Print or return a readable summary of spending metrics."""
        summary = self.get_summary()
        if self.data.empty:
            message = "No expense records available. Add entries to generate a report."
            print(message)
            return message

        top_category = max(summary["category_totals"].items(), key=lambda item: item[1], default=("N/A", 0))[0]

        message = (
            "Expense report\n"
            f"Total spent: {summary['total']:.2f}\n"
            f"Average expense: {summary['average']:.2f}\n"
            f"Number of entries: {summary['num_entries']}\n"
            f"Top category: {top_category}"
        )
        print(message)
        return message

    def visualize(self):
        """Create category bar, monthly line, category pie, and amount histogram."""
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

        if self.data.empty:
            print("No expense data available to visualize.")
            return
        if plt is None or sns is None:
            raise ImportError("Charts require matplotlib and seaborn. Install them with: python -m pip install -r setup/requirements.txt")

        category_totals = self.data.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        monthly_totals = (
            self.data.assign(Month=pd.to_datetime(self.data["Date"]).dt.to_period("M").astype(str))
            .groupby("Month")["Amount"].sum()
            .sort_index()
        )

        fig, ax = plt.subplots()
        category_totals.plot(kind="bar", ax=ax, color="steelblue")
        ax.set_title("Expenses by Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Amount")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "category_totals.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots()
        monthly_totals.plot(kind="line", marker="o", ax=ax, color="darkorange")
        ax.set_title("Monthly Spending Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "monthly_trend.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots()
        category_totals.plot(kind="pie", autopct="%1.1f%%", ax=ax)
        ax.set_title("Spending Share by Category")
        ax.set_ylabel("")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "category_pie.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots()
        sns.histplot(self.data["Amount"], bins=10, kde=True, ax=ax)
        ax.set_title("Expense Amount Distribution")
        ax.set_xlabel("Amount")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "amount_histogram.png", dpi=150)
        plt.close(fig)

        print(f"Charts saved to {FIGURES_DIR}")


def main():
    """Add a simple command menu that calls the tracker methods."""
    tracker = ExpenseTracker()
    print("Smart Expense Tracker starter")

    while True:
        print("\n1. Add expense")
        print("2. Show summary")
        print("3. Filter expenses")
        print("4. Generate report")
        print("5. Create charts")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                date = input("Date (YYYY-MM-DD): ").strip()
                amount = input("Amount: ").strip()
                category = input("Category: ").strip()
                description = input("Description: ").strip()
                result = tracker.add_expense(date, amount, category, description)
                print("Expense added:")
                print(result)
            elif choice == "2":
                print(tracker.get_summary())
            elif choice == "3":
                category = input("Category filter (blank for any): ").strip() or None
                start_date = input("Start date (YYYY-MM-DD, blank for any): ").strip() or None
                end_date = input("End date (YYYY-MM-DD, blank for any): ").strip() or None
                min_amount = input("Minimum amount (blank for any): ").strip() or None
                max_amount = input("Maximum amount (blank for any): ").strip() or None
                filtered = tracker.filter_expenses(
                    category=category,
                    start_date=start_date,
                    end_date=end_date,
                    min_amount=min_amount,
                    max_amount=max_amount,
                )
                if filtered.empty:
                    print("No expenses match the selected filters.")
                else:
                    print(filtered.to_string(index=False))
            elif choice == "4":
                tracker.generate_report()
            elif choice == "5":
                tracker.visualize()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please choose a number from 1 to 6.")
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
