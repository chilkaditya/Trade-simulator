# core/websocket_client.py

import json
import time
import websockets
import asyncio
from datetime import datetime

from core.orderbook import OrderBook
from core.trade_simulator import *
from core.metrics import measure_latency
from ui.display import display_output

async def run():
    url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
    order_book = OrderBook()

    async with websockets.connect(url) as ws:
        print("Connected to WebSocket.")
        while True:
            try:
                start = time.perf_counter()
                message = await ws.recv()
                data = json.loads(message)

                order_book.update(data["bids"], data["asks"])

                avg_price, qty, slippage, cost = simulate_market_buy(order_book, 100)
                fee = calculate_fee(cost)
                impact = estimate_market_impact(qty)
                net_cost = calculate_net_cost(slippage, fee, impact, qty)
                latency = measure_latency(start)

                results = {
                    "Avg Price": avg_price,
                    "Expected": order_book.top_of_book()['best_ask'][0],
                    "Slippage": slippage,
                    "Qty": qty,
                    "Fee ($)": fee,
                    "Market Impact ($)": impact * qty,
                    "Net Cost ($)": net_cost,
                    "Latency (ms)": latency
                }

                display_output(results)

            except Exception as e:
                print("Error:", e)
