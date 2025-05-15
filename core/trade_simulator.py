# core/trade_simulator.py

from config import FEE_RATE, IMPACT_LAMBDA, IMPACT_GAMMA, ESTIMATED_VOLUME

def simulate_market_buy(order_book, usd_amount):
    total_cost = 0
    total_qty = 0
    remaining = usd_amount

    for ask_price, ask_size in order_book.asks:
        level_value = ask_price * ask_size
        if level_value >= remaining:
            qty = remaining / ask_price
            total_cost += qty * ask_price
            total_qty += qty
            break
        else:
            total_cost += level_value
            total_qty += ask_size
            remaining -= level_value

    avg_price = total_cost / total_qty
    expected = order_book.top_of_book()['best_ask'][0]
    slippage = avg_price - expected

    return avg_price, total_qty, slippage, total_cost

def calculate_fee(cost):
    return cost * FEE_RATE

def estimate_market_impact(qty, volume=ESTIMATED_VOLUME):
    return IMPACT_LAMBDA * (qty / volume) ** IMPACT_GAMMA

def calculate_net_cost(slippage, fee, impact, qty):
    return slippage * qty + fee + impact * qty
