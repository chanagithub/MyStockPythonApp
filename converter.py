import csv
import json
import os
from typing import List, Dict

# --- Configuration ---
# The CSV file should contain ONLY THE NEW transactions you want to add.
CSV_INPUT_FILE = 'new_transactions.csv'
# This is your main portfolio file. The script will add new data to it.
PORTFOLIO_JSON_FILE = 'portfolio.json'

def append_csv_to_json():
    """
    Reads new transactions from a CSV file and appends them to an existing
    portfolio.json file. If portfolio.json doesn't exist, it will be created.
    """
    # 1. Check if the CSV input file exists
    if not os.path.exists(CSV_INPUT_FILE):
        print(f"Error: Input file '{CSV_INPUT_FILE}' not found.")
        print("Please create a CSV with your new transactions and name it 'new_transactions.csv'.")
        return

    # 2. Load existing portfolio data from the main JSON file
    existing_transactions: List[Dict] = []
    if os.path.exists(PORTFOLIO_JSON_FILE):
        try:
            with open(PORTFOLIO_JSON_FILE, 'r', encoding='utf-8') as f:
                existing_transactions = json.load(f)
            print(f"Loaded {len(existing_transactions)} existing transactions from '{PORTFOLIO_JSON_FILE}'.")
        except json.JSONDecodeError:
            print(f"Warning: '{PORTFOLIO_JSON_FILE}' is corrupted or empty. Starting with a new list.")
            existing_transactions = []
    else:
        print(f"'{PORTFOLIO_JSON_FILE}' not found. A new file will be created.")

    # Create a set of existing lot numbers for quick duplicate checking
    existing_lot_numbers = {
        tx.get('mylotnumber')
        for tx in existing_transactions
        if tx.get('mylotnumber')
    }

    # 3. Read and convert new transactions from the CSV file
    newly_converted_transactions: List[Dict] = []
    try:
        with open(CSV_INPUT_FILE, mode='r', encoding='utf-8') as csv_file:
            # DictReader uses the first row as headers
            csv_reader = csv.DictReader(csv_file)
            
            print("Starting conversion...")
            for index, row in enumerate(csv_reader):
                try:
                    tx_type = row.get('Type', '').upper().strip()
                    
                    # Basic validation
                    if not tx_type or not row.get('Date') or not row.get('Symbol'):
                        print(f"Warning: Skipping row {index + 2} due to missing required fields (Type, Date, Symbol).")
                        continue

                    transaction = {
                        "symbol": row.get('Symbol', '').upper().strip(),
                        "date": row.get('Date', '').strip(),
                        "type": tx_type,
                        "volume": 0,
                        "price_per_unit": 0.0,
                        "commission": 0.0,
                        "mylotnumber": None,
                        "closes_lot_number": None,
                        "total_amount": None, # Will be calculated by the app
                        "remark": row.get('Remark', '').strip() or None,
                        "tax_rate": None,
                        "realized_pl": None,
                        "cumulative_pl_for_symbol": None
                    }

                    if tx_type in ['BUY', 'SELL']:
                        transaction['volume'] = int(row.get('Volume', 0))
                        transaction['price_per_unit'] = float(row.get('Price per Share', 0.0))
                        transaction['commission'] = float(row.get('Commission', 0.0))
                    elif tx_type == 'DIVIDEND':
                        div_per_share = float(row.get('Price per Share', 0.0))
                        volume = int(row.get('Volume', 0))
                        tax_rate = float(row.get('Tax Rate (%)', 10.0))
                        
                        gross_amount = div_per_share * volume
                        net_amount = gross_amount * (1 - (tax_rate / 100))

                        transaction['volume'] = volume
                        transaction['price_per_unit'] = div_per_share
                        transaction['tax_rate'] = tax_rate
                        transaction['total_amount'] = round(net_amount, 2)
                    elif tx_type == 'CASH_RETURN':
                        return_per_share = float(row.get('Price per Share', 0.0))
                        volume = int(row.get('Volume', 0))
                        
                        total_return = return_per_share * volume
                        
                        transaction['volume'] = volume
                        transaction['price_per_unit'] = return_per_share
                        transaction['total_amount'] = round(total_return, 2)

                    # Handle Lot Number logic
                    lot_number = row.get('Lot Number', '').strip()
                    if tx_type == 'BUY':
                        # --- DUPLICATE CHECK ---
                        if lot_number in existing_lot_numbers:
                            print(f"Info: Skipping row {index + 2}. Lot Number '{lot_number}' already exists in the portfolio.")
                            continue
                        # --- END DUPLICATE CHECK ---
                        transaction['mylotnumber'] = lot_number
                    elif tx_type in ['SELL', 'DIVIDEND', 'CASH_RETURN']:
                        transaction['closes_lot_number'] = lot_number

                    newly_converted_transactions.append(transaction)

                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not process row {index + 2}. Invalid data format. Error: {e}")
                    continue

        # 4. Combine old and new transactions and save back to the main portfolio file
        all_transactions = existing_transactions + newly_converted_transactions
        with open(PORTFOLIO_JSON_FILE, 'w', encoding='utf-8') as json_file:
            json.dump(all_transactions, json_file, indent=2, ensure_ascii=False)
        
        print(f"\nSuccess! Conversion complete.")
        print(f"Added {len(newly_converted_transactions)} new transactions.")
        print(f"'{PORTFOLIO_JSON_FILE}' now contains a total of {len(all_transactions)} transactions.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    append_csv_to_json()
