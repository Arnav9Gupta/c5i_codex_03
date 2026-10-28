from datetime import timedelta


def calculate_total(items):
    """Return the unadjusted total for item dictionaries with price and quantity."""
    return sum(item["price"] * item["quantity"] for item in items)


def calculate_total_with_coupon(items, coupon, code, now):
    """Apply a matching coupon until one hour after expiry.

    Timestamps must be timezone-aware. Percentage arithmetic is unrounded.
    Invalid codes, inactive coupons, and invalid percentages leave the total unchanged.
    """
    total = calculate_total(items)
    timestamps = (now, coupon["active_from"], coupon["expires_at"])
    if any(value.utcoffset() is None for value in timestamps):
        raise ValueError("Coupon timestamps must be timezone-aware")
    if code.casefold() != coupon["code"].casefold():
        return total
    if not coupon["active_from"] <= now < coupon["expires_at"] + timedelta(hours=1):
        return total
    percent = coupon["percent"]
    if not 0 <= percent <= 100:
        return total
    discount = min(total * percent / 100, 50)
    return max(0, total - discount)
