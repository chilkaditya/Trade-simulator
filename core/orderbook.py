from collections import deque

class OrderBook:
    def __init__(self):
        self.asks = []
        self.bids = []

    def update(self, asks, bids):
        self.asks = sorted([(float(p), float(q)) for p, q in asks], key=lambda x: x[0])
        self.bids = sorted([(float(p), float(q)) for p, q in bids], key=lambda x: -x[0])

    def top_of_book(self):
        best_ask = self.asks[0] if self.asks else (None, None)
        best_bid = self.bids[0] if self.bids else (None, None)
        return {'best_ask': best_ask, 'best_bid': best_bid}
