from dataclasses import dataclass
from typing import List, Optional, Dict
from collections import defaultdict
import copy

# --- Data Structures ---
@dataclass
class StockTransaction:
    """Class to represent one stock transaction."""
    symbol: str
    date: str
    type: str
    volume: int
    price_per_unit: float
    commission: float
    mylotnumber: Optional[str] = None

    # --- New fields to match the updated JSON structure ---
    total_amount: Optional[float] = None
    realized_pl: Optional[float] = None
    cumulative_pl_for_symbol: Optional[float] = None

    # --- Old fields kept for compatibility during transition ---
    closes_lot_number: Optional[str] = None
    profit: Optional[float] = None

    def get_total_amount(self) -> float:
        """Calculates the total amount if not present in the data."""
        if self.total_amount is not None:
            return self.total_amount
        if self.type.upper() == 'BUY':
            return (self.volume * self.price_per_unit) + self.commission
        elif self.type.upper() == 'SELL':
            return (self.volume * self.price_per_unit) - self.commission
        return 0.0

@dataclass
class OpenLot:
    """Represents a currently held lot for display."""
    symbol: str
    buy_date: str
    original_volume: int
    remaining_volume: int
    buy_price: float
    total_cost: float
    lot_number: str

@dataclass
class ClosedTrade:
    """Represents a completed trade for display."""
    symbol: str
    buy_date: str
    sell_date: str
    volume_sold: int
    money_in: float
    money_out: float
    realized_pl: float
    cumulative_pl_for_symbol: float
    lot_number: str
    buy_price_per_share: float
    sell_price_per_share: float
    # New fields for detailed status
    remaining_in_lot_after_sale: int
    is_lot_fully_sold: bool = False

def analyze_portfolio_by_lot(portfolio: List[StockTransaction]) -> (List[OpenLot], List[ClosedTrade], float, float):
    """
    Analyzes portfolio by matching SELLs to specific BUYs using lot numbers.
    This is NOT FIFO; it relies on the user specifying which lot to close.
    Returns a tuple of (open_lots, closed_trades, total_investment).
    """
    # Use a deep copy to work on a temporary version of the data, preserving the original list
    transactions = sorted([copy.deepcopy(tx) for tx in portfolio], key=lambda t: t.date)
    
    buy_lots_pool: Dict[str, StockTransaction] = {
        tx.mylotnumber: tx for tx in transactions if tx.type.upper() == 'BUY' and tx.mylotnumber
    }
    
    closed_trades_results: List[ClosedTrade] = []
    cumulative_pl: Dict[str, float] = defaultdict(float)
    total_investment = sum(tx.get_total_amount() for tx in portfolio if tx.type.upper() == 'BUY')

    sell_transactions = [tx for tx in transactions if tx.type.upper() == 'SELL']

    for sell_tx in sell_transactions:
        lot_to_close = sell_tx.closes_lot_number
        if lot_to_close and lot_to_close in buy_lots_pool:
            buy_lot = buy_lots_pool[lot_to_close]
            
            # --- Logic for Partial Sale ---
            # Ensure we don't sell more than we have in the lot
            volume_to_sell = min(sell_tx.volume, buy_lot.volume)
            
            # Calculate cost basis for the portion being sold
            cost_per_share = buy_lot.get_total_amount() / buy_lot.volume
            money_in = cost_per_share * volume_to_sell
            
            money_out = sell_tx.get_total_amount()
            realized_pl = money_out - money_in
            
            cumulative_pl[buy_lot.symbol] += realized_pl
            
            # Reduce volume *before* creating the trade object to get the remaining amount
            buy_lot.volume -= volume_to_sell
            
            is_lot_now_fully_sold = buy_lot.volume == 0

            closed_trades_results.append(ClosedTrade(
                symbol=buy_lot.symbol, buy_date=buy_lot.date, sell_date=sell_tx.date,
                volume_sold=volume_to_sell, money_in=money_in, money_out=money_out,
                realized_pl=realized_pl, cumulative_pl_for_symbol=cumulative_pl[buy_lot.symbol],
                lot_number=buy_lot.mylotnumber,
                buy_price_per_share=buy_lot.price_per_unit,
                sell_price_per_share=sell_tx.price_per_unit,
                remaining_in_lot_after_sale=buy_lot.volume, # The new remaining volume
                is_lot_fully_sold=is_lot_now_fully_sold
            ))
            
            # If the lot is now fully sold, go back and update all previous trades for this lot
            if is_lot_now_fully_sold:
                for trade in closed_trades_results:
                    if trade.lot_number == lot_to_close:
                        trade.is_lot_fully_sold = True

    # The remaining lots in the pool (with volume > 0) are the open lots
    # We need the original portfolio to get the original volume
    original_buy_lots = {tx.mylotnumber: tx for tx in portfolio if tx.type.upper() == 'BUY' and tx.mylotnumber}

    open_lots_results = [
        OpenLot(
            symbol=lot.symbol, buy_date=lot.date,
            original_volume=original_buy_lots[lot.mylotnumber].volume,
            remaining_volume=lot.volume,
            buy_price=lot.price_per_unit, total_cost=lot.get_total_amount(),
            lot_number=lot.mylotnumber
        ) for lot in buy_lots_pool.values() if lot.volume > 0
    ]
    
    total_realized_pl = sum(trade.realized_pl for trade in closed_trades_results)
    
    return sorted(open_lots_results, key=lambda x: x.buy_date), sorted(closed_trades_results, key=lambda x: x.sell_date), total_investment, total_realized_pl