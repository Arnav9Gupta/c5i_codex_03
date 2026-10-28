# Cart service

`calculate_total(items)` returns the unadjusted numeric total and retains its original interface.

`calculate_total_with_coupon(items, coupon, code, now)` applies a matching coupon from activation until one hour after its expiration time. The grace-period end is exclusive: a coupon expiring at 12:00 works at 12:30 but stops working at 13:00.

The coupon dictionary contains `code`, `percent`, `active_from`, and `expires_at`. Matching is case-insensitive. Timestamps must be timezone-aware; naive timestamps raise `ValueError`. Equivalent instants in other timezones are accepted.

Percentages from 0 through 100 are accepted. Discounts are capped at 50 currency units and discounted totals are floored at zero. An unmatched code, inactive coupon, or out-of-range percentage returns the original total. Arithmetic is unrounded, consistent with the sample patch; a production currency-rounding policy remains undefined.

Run dependency-free tests from this directory:

```powershell
python -B -m unittest discover -s tests -v
```

No payment integration or network calls are involved. This implemented grace period supersedes the original exclusive-expiry behavior in the training brief; the seeded review patch remains a historical exercise against that original brief.
