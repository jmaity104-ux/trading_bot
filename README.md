# Binance Futures Testnet Trading Bot

A clean, modular Python CLI trading bot for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper
│   ├── orders.py          # Order placement logic & formatted output
│   ├── validators.py      # Input validation
│   ├── logging_config.py  # Structured logging setup
│   └── cli.py             # CLI entry point (argparse)
├── logs/                  # Auto-created; contains dated log files
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Get Testnet API Credentials

1. Go to https://testnet.binancefuture.com
2. Log in with your **GitHub account**
3. Click the **"API Key"** tab
4. Click **"Generate HMAC_SHA256 Key"**
5. Copy your **API Key** and **Secret Key** (Secret is shown only once!)

> The testnet uses virtual money only — no real funds involved.

### 2. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Set Environment Variables

Set your testnet API credentials as environment variables:

```bash
# Linux / macOS
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"

# Windows PowerShell
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_API_SECRET="your_testnet_api_secret"
```

Alternatively, pass credentials directly via --api-key / --api-secret flags.

---

## Usage

Run from the project root directory:

```bash
python -m bot.cli [OPTIONS]
```

### Options

| Flag | Required | Description |
|------|----------|-------------|
| --symbol | Yes | Trading pair, e.g. BTCUSDT |
| --side | Yes | BUY or SELL |
| --type | Yes | MARKET, LIMIT, or STOP_MARKET |
| --quantity | Yes | Order quantity (must be > 0, min notional 100 USDT) |
| --price | LIMIT only | Limit price |
| --stop-price | STOP_MARKET only | Stop trigger price |
| --api-key | No | Overrides env var |
| --api-secret | No | Overrides env var |

---

## Examples

### Market BUY

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

**Output:**
```
==================================================
  ORDER REQUEST SUMMARY
==================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.002
==================================================
==================================================
  ORDER RESPONSE
==================================================
  Order ID   : 12528204889
  Status     : NEW
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Orig Qty   : 0.002
  Executed   : 0.000
  Avg Price  : 0.00
  Price      : 0.00
  Time       : 1771950478797
==================================================

ORDER PLACED SUCCESSFULLY (status: NEW)
```

### Limit SELL

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 68000
```

### Stop-Market BUY (Bonus order type)

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.002 --stop-price 60000
```

---

## Logging

Logs are written to logs/trading_bot_YYYYMMDD.log. Each entry includes:

- DEBUG: full request/response bodies (API calls)
- INFO: order summaries and success confirmations
- WARNING: unexpected but non-fatal situations
- ERROR: validation failures, API errors, network issues

---

## Sample Log Output

```
2026-02-24 21:57:58 | INFO  | Order request | symbol=BTCUSDT side=BUY type=MARKET qty=0.002
2026-02-24 21:57:58 | INFO  | Placing BUY MARKET order | symbol=BTCUSDT qty=0.002
2026-02-24 21:58:00 | INFO  | Order placed successfully | orderId=12528204889 status=NEW

2026-02-24 21:58:31 | INFO  | Order request | symbol=BTCUSDT side=SELL type=LIMIT qty=0.002 price=68000.0
2026-02-24 21:58:31 | INFO  | Placing SELL LIMIT order | symbol=BTCUSDT qty=0.002 price=68000.0
2026-02-24 21:58:32 | INFO  | Order placed successfully | orderId=12528216936 status=NEW
```

---

## Assumptions

- The testnet base URL is https://testnet.binancefuture.com
- No python-binance library is used — all API calls are made with plain requests for transparency and minimal dependencies.
- Minimum order notional is 100 USDT (Binance requirement). For BTCUSDT at ~$64,000, use at least 0.002 quantity.
- STOP_MARKET orders require only a stopPrice; no separate limit price is needed.
- API credentials are never logged or hardcoded — always use environment variables.

---

## Bonus Feature

This bot includes a third order type: **STOP_MARKET** — a stop-market order that triggers a market order when the price reaches the specified stop price. Useful for stop-loss and take-profit strategies.

---

## Tech Stack

- Python 3.x
- requests library (only dependency)
- argparse for CLI
- logging for structured logs
- HMAC-SHA256 for API request signing
