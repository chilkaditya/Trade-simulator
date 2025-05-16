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

## 🧠 Model Implementation

### ✅ 1. Almgren–Chriss Market Impact Model

**Goal**: Estimate the *permanent* price impact from large trades.

**Simplified Model Used**:

```python
Impact = η × OrderSize
```
 - η (eta): fixed impact coefficient (e.g., 0.00005)
 - OrderSize: USD value of market order

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