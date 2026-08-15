def compare_price_to_ema20(price, ema20, sequence_direction="NONE", tolerance=None):
    """Return the bipolar EMA20 sensor state without mutating caller data."""
    tolerance = max(abs(ema20) * 0.0005, 0.0001) if tolerance is None else tolerance
    direction = "neutral"
    if price > ema20 + tolerance:
        direction = "positive"
    elif price < ema20 - tolerance:
        direction = "negative"

    confirmed_long = direction == "positive"
    confirmed_short = direction == "negative"
    normalized_direction = (sequence_direction or "NONE").upper()
    validates_sequence = (
        (normalized_direction == "LONG" and confirmed_long)
        or (normalized_direction == "SHORT" and confirmed_short)
    )

    return {
        "direction": direction,
        "confirmedLong": confirmed_long,
        "confirmedShort": confirmed_short,
        "validatesSequence": validates_sequence,
        "sequenceDirection": normalized_direction,
        "price": price,
        "ema20": ema20,
    }
