"""Local, deterministic tool shared by optional framework examples."""
import argparse
import os
from decimal import Decimal, InvalidOperation

def line_total(unit_price: str, quantity: int) -> str:
    """Return an exact nonnegative order total; a teaching fixture, not a live quote."""
    if type(quantity) is not int or not 0 <= quantity <= 10000:
        raise ValueError("quantity must be an integer from 0 to 10000")
    try:
        price = Decimal(unit_price)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("invalid decimal price") from exc
    if not price.is_finite() or not 0 <= price <= Decimal("1000000"):
        raise ValueError("price must be finite and from 0 to 1000000")
    if price != price.quantize(Decimal("0.01")):
        raise ValueError("price must have at most two decimal places")
    return format(price * quantity, ".2f")

def require_run(*variables: str) -> dict[str, str]:
    parser = argparse.ArgumentParser(description="Optional live framework exercise; may incur provider charges.")
    parser.add_argument("--run", action="store_true", help="Explicitly allow the configured provider request")
    args = parser.parse_args()
    if not args.run:
        parser.error("Nothing sent. Supply --run only when ready to execute the configured model.")
    values = {key: os.environ.get(key, "").strip() for key in variables}
    missing = [key for key, value in values.items() if not value]
    if missing:
        parser.error("Set " + ", ".join(missing))
    return values
