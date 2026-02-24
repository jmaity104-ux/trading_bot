"""Input validation for CLI arguments."""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    """Raised when user-supplied input fails validation."""


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}': must be alphanumeric (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}': must be one of {VALID_SIDES}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}': must be one of {VALID_ORDER_TYPES}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}': must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type in ("LIMIT", "STOP_MARKET"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid price '{price}': must be a positive number.")
        if p <= 0:
            raise ValidationError(f"Price must be greater than 0, got {p}.")
        return p
    return None  # MARKET orders don't need a price


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_MARKET orders.")
        try:
            sp = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid stop price '{stop_price}': must be a positive number.")
        if sp <= 0:
            raise ValidationError(f"Stop price must be greater than 0, got {sp}.")
        return sp
    return None
