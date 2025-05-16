import asyncio
import websockets
import json
import time
from core.orderbook import OrderBook
from core.trade_simulator import (
    simulate_market_buy,
    calculate_fee,
    calculate_market_impact
)
from core.slippage_model import load_model, predict_slippage

# WebSocket URL for OKX L2 data (BTC-USDT-SWAP for now)
URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

async def run():
    order_book = OrderBook()
    model = load_model()

    print("[*] Connecting to WebSocket stream...")
    async with websockets.connect(URL) as ws:
        print("[✓] Connected. Listening for data...\n")

        while True:
            try:
                message = await ws.recv()
                start_time = time.perf_counter()
                data = json.loads(message)

                # Update order book
                asks = data.get("asks", [])
                bids = data.get("bids", [])
                order_book.update(asks, bids)

                # Simulate market buy
                usd_amount = 100
                avg_price, qty, slippage = simulate_market_buy(order_book, usd_amount)

                if avg_price and qty:
                    best_ask = order_book.top_of_book()['best_ask'][0]
                    predicted_slippage = predict_slippage(model, usd_amount, best_ask)

                    fee = calculate_fee(avg_price, qty, fee_rate=0.001)
                    impact = calculate_market_impact(order_size_usd=usd_amount)
                    net_cost = slippage + fee + impact
                    latency = (time.perf_counter() - start_time) * 1000

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

Internal Latency:   {latency:.2f} ms
=========================================
""")
            except Exception as e:
                print(f"[!] Error: {e}")
                continue
