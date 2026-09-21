# Triangular Arbitrage Detector

Detects triangular arbitrage opportunities across ETH/BTC/USDT in real time from
Binance's public WebSocket feed.

## Method

Three live mid-prices (ETH/USDT, BTC/USDT, ETH/BTC) define a 3-node currency graph.
Each directed edge's weight is `-log(rate * (1 - fee))`; a cycle with negative total
weight is a profitable arbitrage loop (the classic Bellman-Ford formulation of
currency arbitrage — summing log-rates turns compounding returns into additive
weights, so a negative cycle sum corresponds to a net gain of
`exp(-cycle_weight) - 1`).

Because the graph has only 3 nodes, the two possible triangular cycles
(`ETH->BTC->USDT->ETH` and `ETH->USDT->BTC->ETH`) are checked directly on every
tick rather than running a general-purpose Bellman-Ford — see
`check_arbitrage_optimized` in `main.py`.

## How to run

```bash
pip install websocket-client
python main.py
```

Streams `btcusdt`, `ethusdt`, and `ethbtc` mini-ticker updates from Binance and
prints any detected arbitrage cycle with its weight and implied profit rate.

## Limitations

- Detection only — no order execution, sizing, or slippage/latency modeling.
- Assumes all three legs are fillable simultaneously at the quoted mid-price, which
  understates real execution cost.
- Single fee rate (`0.00075`) hardcoded for all three legs.
