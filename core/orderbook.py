# core/orderbook.py

class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []

    def update(self, bids, asks):
        self.bids = sorted([[float(p), float(s)] for p, s in bids], reverse=True)
        self.asks = sorted([[float(p), float(s)] for p, s in asks])

    def top_of_book(self):
        return {
            "best_bid": self.bids[0] if self.bids else None,
            "best_ask": self.asks[0] if self.asks else None
        }
