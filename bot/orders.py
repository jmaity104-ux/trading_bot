"""High-level order placement logic with structured output."""

from __future__ import annotations

from typing import Any, Dict, Optional

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging

logger = setup_logging()


def _format_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float],
) -> str:
    lines = [
        "=" * 50,
        "  ORDER REQUEST SUMMARY",
        "=" * 50,
        f"  Symbol     : {symbol}",
        f"  Side       : {side}",
        f"  Type       : {order_type}",
        f"  Quantity   : {quantity}",
    ]
    if price is not None:
        lines.append(f"  Price      : {price}")
    if stop_price is not None:
        lines.append(f"  Stop Price : {stop_price}")
    lines.append("=" * 50)
    return "\n".join(lines)


def _format_order_response(response: Dict[str, Any]) -> str:
    lines = [
        "=" * 50,
        "  ORDER RESPONSE",
        "=" * 50,
        f"  Order ID   : {response.get('orderId', 'N/A')}",
        f"  Status     : {response.get('status', 'N/A')}",
        f"  Symbol     : {response.get('symbol', 'N/A')}",
        f"  Side       : {response.get('side', 'N/A')}",
        f"  Type       : {response.get('type', 'N/A')}",
        f"  Orig Qty   : {response.get('origQty', 'N/A')}",
        f"  Executed   : {response.get('executedQty', 'N/A')}",
        f"  Avg Price  : {response.get('avgPrice', 'N/A')}",
        f"  Price      : {response.get('price', 'N/A')}",
        f"  Time       : {response.get('updateTime', 'N/A')}",
        "=" * 50,
    ]
    return "\n".join(lines)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Place an order via the client and print a clean summary.

    Returns the raw API response dict.
    Raises BinanceAPIError, ConnectionError, or TimeoutError on failure.
    """
    summary = _format_order_summary(symbol, side, order_type, quantity, price, stop_price)
    print(summary)
    logger.info(
        "Order request | symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except BinanceAPIError as exc:
        logger.error("Order failed — Binance API error %s: %s", exc.code, exc.message)
        print(f"\n❌ ORDER FAILED\n   Binance API Error {exc.code}: {exc.message}\n")
        raise
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Order failed — network error: %s", exc)
        print(f"\n❌ ORDER FAILED\n   Network error: {exc}\n")
        raise
    except Exception as exc:
        logger.exception("Unexpected error placing order: %s", exc)
        print(f"\n❌ ORDER FAILED\n   Unexpected error: {exc}\n")
        raise

    formatted = _format_order_response(response)
    print(formatted)

    status = response.get("status", "")
    if status in ("FILLED", "NEW", "PARTIALLY_FILLED"):
        print(f"\n✅ ORDER PLACED SUCCESSFULLY (status: {status})\n")
        logger.info("Order placed successfully | orderId=%s status=%s", response.get("orderId"), status)
    else:
        print(f"\n⚠️  ORDER STATUS UNKNOWN: {status}\n")
        logger.warning("Unexpected order status: %s | response: %s", status, response)

    return response
