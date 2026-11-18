"""Deterministic dip-bounce scalper for agent-fun/bars-replay/v1."""
import json
import sys

DIP_BPS = 150
BOUNCE_BPS = 20
HIGH_BARS = 60
LOW_BARS = 10
TP_BPS = 200
STOP_BPS = 100
TRAIL_ARM_BPS = 120
TRAIL_BPS = 60
MAX_HOLD = 480
COOLDOWN_BARS = 5
SIZE_PCT = 100
MAX_SLIPPAGE_BPS = 200
LAST_ENTRY_SEQ = 1200


def reached_above(price, reference, bps):
    return price * 10000 >= reference * (10000 + bps)


def reached_below(price, reference, bps):
    return price * 10000 <= reference * (10000 - bps)


def main():
    closes = []
    entry_price = 0
    entry_seq = 0
    highest = 0
    position_qty = "0"
    cooldown_until = -1
    order_number = 0

    for line in sys.stdin:
        message = json.loads(line)
        kind = message.get("type")
        if kind == "hello":
            # The harness warms the strategy through its first 60 closes.
            warmup_bars = HIGH_BARS
            continue
        if kind == "done":
            break
        if kind != "batch":
            continue

        seq = int(message["seq"])
        account = message.get("account", {})
        positions = account.get("positions", [])
        account_qty = "0"
        for position in positions:
            if position.get("symbol") == "CBBTC":
                account_qty = str(position.get("qty", "0"))
                break
        position_qty = account_qty

        # A completed buy fill supplies authoritative entry data.
        for fill in message.get("fills", []):
            if (fill.get("status") == "filled" and fill.get("side") == "buy"
                    and fill.get("symbol") == "CBBTC"):
                entry_price = int(fill["price"])
                position_qty = str(fill["qty"])
                entry_seq = seq
                highest = entry_price
            elif (fill.get("status") == "filled" and fill.get("side") == "sell"
                    and fill.get("symbol") == "CBBTC"):
                entry_price = 0
                position_qty = "0"
                entry_seq = 0
                highest = 0

        for bar in message.get("bars", []):
            if bar.get("symbol") == "CBBTC":
                closes.append(int(bar["c"]))

        orders = []
        warmup_bars = int(message.get("warmup_bars", HIGH_BARS))
        if position_qty not in ("0", "0.0", "") and entry_price > 0 and seq >= warmup_bars:
            close = closes[-1] if closes else entry_price
            highest = max(highest, close)
            held = seq - entry_seq
            trailing_armed = reached_above(highest, entry_price, TRAIL_ARM_BPS)
            should_sell = (
                reached_above(close, entry_price, TP_BPS)
                or reached_below(close, entry_price, STOP_BPS)
                or (trailing_armed and reached_below(close, highest, TRAIL_BPS))
                or held >= MAX_HOLD
            )
            if should_sell:
                order_number += 1
                orders.append({
                    "side": "sell",
                    "client_id": f"s{order_number}",
                    "symbol": "CBBTC",
                    "qty": position_qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                })
                cooldown_until = seq + COOLDOWN_BARS
        elif position_qty in ("0", "0.0", ""):
            if len(closes) >= HIGH_BARS:
                close = closes[-1]
                recent_high = max(closes[-HIGH_BARS:])
                recent_low = min(closes[-LOW_BARS:])
                cash = account.get("cash_quote_units", "0")
                if (seq >= warmup_bars and seq > cooldown_until and seq <= LAST_ENTRY_SEQ
                        and reached_below(close, recent_high, DIP_BPS)
                        and reached_above(close, recent_low, BOUNCE_BPS)):
                    order_number += 1
                    notional = str(cash)
                    orders.append({
                        "side": "buy",
                        "client_id": f"b{order_number}",
                        "symbol": "CBBTC",
                        "notional_quote_units": notional,
                        "max_slippage_bps": MAX_SLIPPAGE_BPS,
                    })

        print(json.dumps({"type": "reply", "seq": seq, "orders": orders}, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
