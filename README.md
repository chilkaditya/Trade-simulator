# 📈 Real-Time Trade Simulator

A high-performance crypto trade simulator that processes real-time order book data from OKX and computes transaction costs, slippage, market impact, and more — all visualized live with Streamlit.

---

## 📁 Project Structure

```
trade-sim/
│
├── core/
│ ├── orderbook.py # L2 OrderBook handler
│ ├── trade_simulator.py # Slippage, fee, market impact, maker/taker logic
│ ├── slippage_model.py # Linear regression for slippage
│ ├── maker_taker_model.py # Logistic regression for maker/taker classification
│
├── models/ # Saved ML models (joblib)
├── data/
│ └── maker_taker_data.csv # Raw data used for model training
│
├── ui/
│ └── dashboard.py # Streamlit dashboard
│
├── main.py # Async WebSocket entry point
└── README.md # Documentation
```
---

## 🔁 Code Flow Overview

1. **WebSocket connection** receives real-time L2 order book data.
2. On each tick:
   - Order book is updated.
   - A $100 market buy is simulated.
   - Slippage, fees, and market impact are calculated.
   - Logistic regression estimates the maker/taker probability.
   - Latency (tick processing time) is measured.
3. All outputs are displayed live in the UI (Streamlit).

---

## 📜 Module Explanations

---

### 🔧 `orderbook.py`

Handles L2 order book data structure and updates.

#### `OrderBook` class:
- `update_from_snapshot(data: dict)`  
  Parses incoming WebSocket snapshot and updates internal ask/bid arrays.
  
- `top_of_book()`  
  Returns best bid and ask prices.

---

### 📊 `trade_simulator.py`

Simulates trades and calculates associated metrics.

#### `simulate_market_buy(order_book, usd_amount)`
Simulates a market buy order:
- Traverses ask levels until `usd_amount` is filled.
- Calculates `avg_price`, `total_qty`, `slippage`, and `total_cost`.

#### `calculate_fee(order_cost: float, fee_rate: float = 0.001)`
Returns trading fee = `order_cost * fee_rate`.

#### `calculate_market_impact(order_size_usd, daily_volume=1e9, volatility=0.02, eta=0.1, epsilon=0.01)`
Implements a **simplified Almgren–Chriss model**:

#### `calculate_latency(start_time, end_time)`
Returns elapsed time in milliseconds for tick processing.

---

### 📈 `slippage_model.py`

Trains and predicts slippage using linear regression.

#### `train_model(model_type='linear')`
- Simulates historical trades using synthetic order book data.
- Trains a `LinearRegression` model on `(usd_amount, best_ask)` vs. `slippage`.

#### `predict_slippage(model, usd_amount, best_ask)`
Returns predicted slippage from the model.

#### `load_model()`
Loads a pre-trained model from disk (`models/slippage_model.pkl`).

---

### 🤖 `maker_taker_model.py`

Predicts maker/taker trade execution probability using **logistic regression**.

#### `train_maker_taker_model()`
Trains a logistic regression model using:
- Features: `order_size`, `price_diff`, etc.
- Label: 0 (taker), 1 (maker)

#### `predict_maker_taker(model, features)`
Predicts maker/taker likelihood.

---

### 📊 `market_stats.py` (Optional Extension)

Can be used to dynamically compute:
- Daily volume (via REST API)
- Volatility (rolling window of price returns)

---

## 🌐 `websocket_client.py`

Handles:
- Connecting to WebSocket (`wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP`)
- Updating order book on each tick
- Triggering trade simulation and metric computation

#### `async run()`
Main loop:
- Opens WebSocket and listens for ticks
- On each tick:
  - Updates order book
  - Simulates market buy
  - Predicts slippage using model
  - Calculates fee and impact
  - Predicts maker/taker ratio
  - Measures latency
  - Pushes results to UI

---

## 🖥️ `dashboard.py` (Streamlit UI)

Shows:
- Input controls (asset, size, fee tier)
- Output metrics:
  - Slippage
  - Fees
  - Market Impact
  - Net Cost
  - Maker/Taker probability
  - Latency (ms)

Auto-refreshes on each tick.

---

## 🧠 Model Summary

| Model               | Type              | Purpose                    | Notes                              |
|--------------------|-------------------|----------------------------|-------------------------------------|
| **Slippage**        | Linear Regression | Predict price deviation    | Fast, interpretable, live inference |
| **Market Impact**   | Formula-based     | Estimate permanent impact  | Simplified Almgren–Chriss           |
| **Maker/Taker**     | Logistic Regression | Estimate trade execution type | Based on price distance & size   |

---

## 🛠️ Performance Optimizations

- Models loaded once at startup
- Tick processing optimized with NumPy
- Order book stored as fast `deque`
- Async WebSocket ensures non-blocking I/O
- UI updates only on new data


---

## 🧠 Model Implementation

### ✅ 1. Almgren–Chriss Market Impact Model

**Goal**: Estimate the *permanent* price impact from large trades.

**Simplified Model Used**:

```python
Impact = gamma * OrderSize ** beta
```
beta (β):
 - This is the exponent applied to volume. It determines how strongly the impact scales with trade volume.
 - If beta = 1, impact increases linearly with volume.
 - If beta < 1, the impact increases sublinearly (diminishing returns).
 - If beta > 1, the impact increases superlinearly (more than proportionally).

gamma (γ):
 - This is a scaling factor or coefficient. It adjusts the magnitude of the impact, essentially stretching or compressing the curve defined by volume ** beta.

OrderSize: USD value of market order

**Why Simplified**?

The full Almgren–Chriss model requires volatility, liquidity curves, and execution horizon, which aren’t accessible in real-time simulation. A linear approximation balances realism and performance.

### ✅ 2. Slippage Estimation via Linear Regression
#### Objective: 
Slippage is the difference between the expected price (usually the top-of-book) and the actual execution price of a market order. The larger the trade or the thinner the book, the more slippage you typically experience.

We wanted to predict expected slippage in real time based on trade conditions, before executing the trade. This means we needed:
 - A fast and lightweight predictive model
 - A model that can be updated or retrained as needed
 - Something interpretable so we can explain why a prediction was made

#### Model: 
LinearRegression from sklearn

#### Features:
 - USD amount of the order
 - Best ask price at execution

**Why Linear Regression**?
 - Linear regression provides a clear mathematical relationship between input features and output (slippage).
 - We can easily understand how changes in trade size or price affect slippage.
 - Useful for debugging and tuning — no black-box behavior.
 - Extremely fast to train and predict, making it ideal for live streaming environments.
 - Can process thousands of ticks per second without performance issues.
 - Doesn’t require GPUs or heavy frameworks.
 - For moderate order sizes, slippage grows approximately linearly with trade size — especially when markets are not highly volatile.
 - Market impact models like Almgren-Chriss are also based on linear approximations.


### ✅ 3. Maker/Taker Classification via Logistic Regression
**Objective**: Estimate the probability of a trade behaving as a maker or taker.

**Model**: LogisticRegression from sklearn

**Features**:
 - Order size in USD
 - Spread (ask - bid)
 - Top 5 ask-side depth

**Labels**:
 - 1 = Taker (immediate execution)
 - 0 = Maker (non-immediate / limit)

**Note**: Currently, all simulated market orders are labeled takers. More real labeled data can improve future retraining.

---

## ✅ Getting Started
**Install dependencies**:
```bash
pip install -r requirements.txt
```
**Train models (once)**:
```bash
python -c "from core.slippage_model import train_model; train_model(model_type='linear')"
python -c "from core.maker_taker_model import train_maker_taker_model; train_maker_taker_model()"
```
**Run main async processor**:
```bash
python main.py
```
**Run UI dashboard**:
```bash
streamlit run ui/dashboard.py
```
