import json
from dataclasses import asdict
from typing import List

# --- นำเข้าฟังก์ชันและคลาสจากไลบรารีกลางของเรา ---
from portfolio_lib import StockTransaction, analyze_portfolio_by_lot

def load_portfolio(filepath: str) -> List[StockTransaction]:
    """
    Loads portfolio data from a JSON file.
    Returns an empty list if the file doesn't exist or is empty.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [StockTransaction(**item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        # If file not found or is empty/corrupt, start with an empty portfolio
        return []

def save_portfolio(filepath: str, portfolio: List[StockTransaction]):
    """Saves the entire portfolio to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        # Convert list of dataclass objects to list of dictionaries for JSON serialization
        data_to_save = [asdict(transaction) for transaction in portfolio]
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Define the path to our data file
    portfolio_file = 'portfolio.json'

    # 1. Load existing data from the file
    my_portfolio = load_portfolio(portfolio_file)
    print(f"Portfolio loaded. Found {len(my_portfolio)} transaction(s).")

    # --- ข้อควรระวัง ---
    # โค้ดสำหรับเพิ่มข้อมูลใหม่จะถูกคอมเมนต์ไว้ก่อน
    # เพื่อป้องกันการเพิ่มข้อมูลเดิมซ้ำทุกครั้งที่รันโปรแกรม
    # หากต้องการเพิ่มรายการใหม่ ให้ลบเครื่องหมาย """ ออก แล้วใส่ข้อมูลใหม่ได้เลย
    """
    # 2. เพิ่มรายการใหม่
    new_transaction = StockTransaction(symbol="KBANK", date="2024-02-20", type="BUY", volume=50, price_per_unit=125.00, commission=27.88)
    my_portfolio.append(new_transaction)

    # 3. บันทึกข้อมูลที่อัปเดตแล้ว
    save_portfolio(portfolio_file, my_portfolio)
    print("Portfolio saved successfully!")
    """

    # 4. วิเคราะห์ข้อมูลจากพอร์ตของเราด้วยฟังก์ชันใหม่
    open_lots, closed_trades, total_investment, total_realized_pl, total_dividends = analyze_portfolio_by_lot(my_portfolio)

    print(f"\n--- Portfolio Analysis ---")
    print(f"Total investment cost (all BUYs): {total_investment:,.2f} THB")
    print(f"Total realized P/L: {total_realized_pl:,.2f} THB")
    print(f"Total dividends received: {total_dividends:,.2f} THB")

    print("\n--- Current Holdings (Open Lots) ---")
    for lot in open_lots:
        print(f"  Lot {lot.lot_number}: {lot.symbol} - {lot.remaining_volume}/{lot.original_volume} shares @ {lot.buy_price:,.2f} THB | Dividends: {lot.dividends_received:,.2f} THB")

    print("\n--- Closed Trades (Realized P/L) ---")
    for trade in closed_trades:
        print(f"  Sold {trade.symbol} (Lot): Realized P/L: {trade.realized_pl:,.2f} THB | Cumulative P/L: {trade.cumulative_pl_for_symbol:,.2f} THB")