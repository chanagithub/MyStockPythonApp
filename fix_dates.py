import json
import os
from datetime import datetime

# --- Configuration ---
PORTFOLIO_JSON_FILE = 'portfolio.json'
BACKUP_FILE_PATH = 'portfolio.backup.json'

# List of possible incorrect date formats (Day-Month-Year)
# Add more formats here if needed, e.g., '%d.%m.%Y'
INCORRECT_FORMATS = [
    '%d/%m/%Y',  # e.g., 21/11/2018
    '%d-%m-%Y',  # e.g., 21-11-2018
    '%d/%m/%y',  # e.g., 21/11/18
    '%d-%m-%y',  # e.g., 21-11-18
    '%d %b %Y',  # e.g., 21 Mar 2019
]
CORRECT_FORMAT = '%Y-%m-%d'

def fix_date_formats():
    """
    Reads the portfolio.json file, corrects date formats from D-M-Y to Y-M-D,
    and saves the corrected file. Creates a backup of the original file.
    """
    # 1. Check if the portfolio file exists
    if not os.path.exists(PORTFOLIO_JSON_FILE):
        print(f"Error: Main portfolio file '{PORTFOLIO_JSON_FILE}' not found.")
        return

    # 2. Create a backup of the original file
    try:
        with open(PORTFOLIO_JSON_FILE, 'r', encoding='utf-8') as f_in, \
             open(BACKUP_FILE_PATH, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
        print(f"Successfully created a backup at '{BACKUP_FILE_PATH}'")
    except Exception as e:
        print(f"Error: Could not create backup file. Aborting. Error: {e}")
        return

    # 3. Load the portfolio data
    try:
        with open(PORTFOLIO_JSON_FILE, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not read '{PORTFOLIO_JSON_FILE}'. It might be corrupted.")
        return

    # 4. Iterate and fix dates
    records_fixed = 0
    for index, tx in enumerate(transactions):
        date_str = tx.get('date')
        if not date_str:
            continue

        try:
            datetime.strptime(date_str, CORRECT_FORMAT)
            continue
        except ValueError:
            pass

        for fmt in INCORRECT_FORMATS:
            try:
                dt_object = datetime.strptime(date_str, fmt)
                correct_date_str = dt_object.strftime(CORRECT_FORMAT)
                tx['date'] = correct_date_str
                print(f"Fixed record {index + 1}: Changed date from '{date_str}' to '{correct_date_str}'")
                records_fixed += 1
                break
            except ValueError:
                continue

    # 5. Save the corrected data back to the file
    if records_fixed > 0:
        with open(PORTFOLIO_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully fixed {records_fixed} record(s). The file '{PORTFOLIO_JSON_FILE}' has been updated.")
    else:
        print("\nNo records needed fixing. All dates appear to be in the correct format.")

if __name__ == "__main__":
    fix_date_formats()