import asyncio
import websockets
import json
import time
import os

from core.orderbook import OrderBook
from core.trade_simulator import (
    simulate_market_buy,
    calculate_fee,
    calculate_market_impact
)
from core.slippage_model import load_model, predict_slippage
from core.maker_taker_model import load_maker_taker_model, predict_maker_taker_proba

# WebSocket endpoint
URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

async def run():
    order_book = OrderBook()
    slippage_model = load_model()
    # maker_taker_model = load_maker_taker_model()
    maker_taker_model = None
    if os.path.exists("models/maker_taker_model.pkl"):
        maker_taker_model = load_maker_taker_model()
    else:
        print("[!] Maker/Taker model not found. Skipping prediction for now.")

    print("[*] Connecting to WebSocket stream...")
    async with websockets.connect(URL) as ws:
        print("[✓] Connected. Listening for data...\n")

        while True:
            try:
                message = await ws.recv()
                start_time = time.perf_counter()

                data = json.loads(message)
                asks = data.get("asks", [])
                bids = data.get("bids", [])
                order_book.update(asks, bids)

                usd_amount = 100
                avg_price, qty, slippage = simulate_market_buy(order_book, usd_amount)

                if avg_price and qty:
                    top = order_book.top_of_book()
                    best_ask = top['best_ask'][0]
                    best_bid = top['best_bid'][0]
                    spread = best_ask - best_bid
                    depth = sum(qty for price, qty in order_book.asks[:5])

                    predicted_slippage = predict_slippage(slippage_model, usd_amount, best_ask)
                    fee = calculate_fee(avg_price, qty)
                    impact = calculate_market_impact(usd_amount)
                    net_cost = slippage + fee + impact

                    # maker_taker_probs = predict_maker_taker_proba(maker_taker_model, usd_amount, spread, depth)

                    if maker_taker_model:
                        maker_taker_probs = predict_maker_taker_proba(maker_taker_model, usd_amount, spread, depth)
                        maker_str = f"""
                        Maker Prob:         {maker_taker_probs['maker']:.2%}
                        Taker Prob:         {maker_taker_probs['taker']:.2%}
                        """
                    else:
                        maker_str = "Maker/Taker prediction: Not available (model not trained)\n"


                    latency = (time.perf_counter() - start_time) * 1000  # ms

                    print(f"""
================ Tick ====================
Best Ask:           {best_ask:.2f}
Avg Fill Price:     {avg_price:.2f}
Filled Qty:         {qty:.6f}

Actual Slippage:    {slippage:.6f}
Predicted Slippage: {predicted_slippage:.6f}

Fee ($):            {fee:.6f}
Market Impact ($):  {impact:.6f}
Net Cost ($):       {net_cost:.6f}

Maker Prob:         {maker_taker_probs['maker']:.2%}
Taker Prob:         {maker_taker_probs['taker']:.2%}

Internal Latency:   {latency:.2f} ms
=========================================
""")

            except Exception as e:
                print(f"[!] Error: {e}")
                continue
