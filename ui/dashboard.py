import streamlit as st
import asyncio
import json
import websockets
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from core.orderbook import OrderBook
from core.trade_simulator import simulate_market_buy, calculate_fee, calculate_market_impact
from core.slippage_model import load_model, predict_slippage
from core.maker_taker_model import load_maker_taker_model, predict_maker_taker_proba

slippage_model = load_model()
maker_taker_model = load_maker_taker_model()

URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

st.set_page_config(page_title="Live Trade Simulator", layout="wide")
st.title("📈 Real-Time Trade Simulator")
output = st.empty()

async def run_stream():
    order_book = OrderBook()

    async with websockets.connect(URL) as ws:
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
                    maker_taker_probs = predict_maker_taker_proba(maker_taker_model, usd_amount, spread, depth)
                    latency = (time.perf_counter() - start_time) * 1000

                    output.markdown(f"""
### 🧮 Trade Simulation

- **Best Ask**: `{best_ask:.2f}`
- **Average Fill Price**: `{avg_price:.2f}`
- **Filled Quantity**: `{qty:.6f}`

**Slippage**:
- Actual: `{slippage:.6f}`
- Predicted: `{predicted_slippage:.6f}`

**Costs**:
- Fee: `${fee:.6f}`
- Market Impact: `${impact:.6f}`
- Net Cost: `${net_cost:.6f}`

**Probabilities**:
- Maker: `{maker_taker_probs['maker']:.2%}`
- Taker: `{maker_taker_probs['taker']:.2%}`

**Latency**:
- `{latency:.2f} ms`
""")

                await asyncio.sleep(0.01)

            except Exception as e:
                st.error(f"Error: {e}")
                await asyncio.sleep(1)

def main():
    asyncio.run(run_stream())

if __name__ == "__main__":
    main()
