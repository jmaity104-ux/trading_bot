"""CLI entry point for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import os
import sys

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logging()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY
  python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

  # Stop-Market BUY (bonus order type)
  python -m bot.cli --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000

API credentials are read from environment variables:
  BINANCE_API_KEY    — your testnet API key
  BINANCE_API_SECRET — your testnet API secret
        """,
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET, LIMIT, or STOP_MARKET",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity (must be > 0)",
    )
    parser.add_argument(
        "--price",
        default=None,
        help="Order price (required for LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        default=None,
        dest="stop_price",
        help="Stop price (required for STOP_MARKET orders)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Binance API key (overrides BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret",
        default=None,
        help="Binance API secret (overrides BINANCE_API_SECRET env var)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- Resolve credentials ---
    api_key = args.api_key or os.environ.get("BINANCE_API_KEY", "")
    api_secret = args.api_secret or os.environ.get("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        parser.error(
            "API credentials not found. Set BINANCE_API_KEY and BINANCE_API_SECRET "
            "environment variables, or pass --api-key / --api-secret."
        )

    # --- Validate inputs ---
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValidationError as exc:
        logger.error("Input validation failed: %s", exc)
        print(f"\n❌ VALIDATION ERROR: {exc}\n")
        sys.exit(1)

    # --- Build client & place order ---
    try:
        client = BinanceClient(api_key=api_key, api_secret=api_secret)
        place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except (BinanceAPIError, ConnectionError, TimeoutError, ValueError):
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unhandled exception: %s", exc)
        print(f"\n❌ UNEXPECTED ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
