import csv
import os

def simulate_market_buy(order_book, usd_amount=100):
    total_cost = 0
    total_qty = 0
    remaining = usd_amount

    # # 🔽 ADD THIS TO DEBUG LIQUIDITY
    # print(f"\n[DEBUG] Simulating market buy of ${usd_amount}")
    # print("[DEBUG] Top 5 ask levels:")
    # for price, size in order_book.asks[:5]:
    #     print(f"Ask: {price:.2f} x {size:.4f} → ${price * size:.2f}")

    for price, size in order_book.asks:
        value = price * size
        if value >= remaining:
            qty = remaining / price
            total_cost += qty * price
            total_qty += qty
            break
        else:
            total_cost += value
            total_qty += size
            remaining -= value

    if total_qty == 0:
        return None, None, None

    avg_price = total_cost / total_qty
    best_ask = order_book.top_of_book()['best_ask'][0]
    slippage = avg_price - best_ask

    # Log to CSV
    os.makedirs("data", exist_ok=True)
    with open("data/slippage_data.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([usd_amount, best_ask, avg_price, slippage])

    return avg_price, total_qty, slippage

def calculate_fee(avg_fill_price, qty, fee_rate=0.001):
    """
    Calculates the trading fee.
    - fee_rate is typically 0.001 for 0.1%
    """
    notional = avg_fill_price * qty
    return notional * fee_rate

def calculate_market_impact(order_size_usd, daily_volume_usd=1e9, volatility=0.02, eta=0.1, epsilon=0.01):
    """
    Estimates the market impact cost using simplified Almgren-Chriss.
    """
    permanent = eta * (order_size_usd / daily_volume_usd)
    temporary = epsilon * volatility * order_size_usd
    impact = permanent + temporary
    return impact