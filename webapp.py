import json
from flask import Flask, render_template, request, jsonify
from dataclasses import asdict
from datetime import date

# --- นำเข้าฟังก์ชันและคลาสจากไลบรารีกลางของเรา ---
from portfolio_lib import StockTransaction, analyze_portfolio_by_lot


app = Flask(__name__)

@app.route('/')
def index():
    """แสดงหน้าเว็บหลัก (index.html)"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_portfolio():
    """รับไฟล์ที่อัปโหลดมา, วิเคราะห์, และส่งผลลัพธ์กลับไป"""
    if 'portfolio_file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['portfolio_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.json'):
        try:
            # อ่านข้อมูลจากไฟล์ที่อัปโหลดมาเป็น string แล้วแปลงเป็น JSON
            content = file.read().decode('utf-8')
            portfolio_data = json.loads(content)
            
            # แปลง list of dicts ที่ได้จาก JSON ให้เป็น list of StockTransaction objects
            portfolio_objects = [StockTransaction(**item) for item in portfolio_data]

            # --- เรียกใช้ฟังก์ชันวิเคราะห์ตัวใหม่ ---
            open_lots, closed_trades, total_investment, total_realized_pl, total_dividends = analyze_portfolio_by_lot(portfolio_objects)
            
            # --- รวบรวมรายชื่อหุ้นที่ยังคงมีอยู่ในพอร์ตเท่านั้น ---
            symbols_in_open_lots = sorted(list(set(lot.symbol for lot in open_lots)))
            
            return jsonify({
                "total_investment": total_investment, 
                "total_realized_pl": total_realized_pl,
                "total_dividends": total_dividends,
                "transaction_count": len(portfolio_objects),
                # แปลงผลลัพธ์ให้อยู่ในรูปแบบที่ส่งผ่าน JSON ได้
                "open_lots": [asdict(lot) for lot in open_lots],
                "closed_trades": [asdict(trade) for trade in closed_trades],
                "all_symbols": symbols_in_open_lots
            })
        except Exception as e:
            # เพิ่มการแสดง error ใน terminal เพื่อให้ดีบักง่ายขึ้น
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"An internal error occurred: {e}"}), 500

@app.route('/close_year', methods=['POST'])
def close_year_end():
    """
    Receives the current portfolio, calculates the open lots, and returns a new
    set of 'BUY' transactions representing the starting balance for a new period.
    This effectively clears all history (sells, dividends) and resets P/L.
    """
    try:
        portfolio_data = request.get_json()
        if not portfolio_data:
            return jsonify({"error": "No portfolio data provided"}), 400

        portfolio_objects = [StockTransaction(**item) for item in portfolio_data]
        open_lots, _, _, _, _ = analyze_portfolio_by_lot(portfolio_objects)

        closing_date = date.today().strftime('%Y-%m-%d')
        new_portfolio_as_dicts = []

        for lot in open_lots:
            if lot.remaining_volume <= 0:
                continue

            avg_cost_per_share = lot.total_cost / lot.remaining_volume if lot.remaining_volume > 0 else 0
            
            new_tx = StockTransaction(
                symbol=lot.symbol, date=closing_date, type='BUY',
                volume=lot.remaining_volume,
                price_per_unit=round(avg_cost_per_share, 4),
                commission=0, mylotnumber=lot.lot_number,
                total_amount=round(lot.total_cost, 2),
                remark=f"Year-end closing balance from lot bought on {lot.buy_date}",
            )
            new_portfolio_as_dicts.append(asdict(new_tx))
        
        return jsonify(new_portfolio_as_dicts)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An internal error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)