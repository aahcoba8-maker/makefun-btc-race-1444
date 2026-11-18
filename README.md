# Deep-dip bounce cbBTC bot

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/aahcoba8-maker/makefun-btc-race-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/aahcoba8-maker/makefun-btc-race-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

A long-only dip-bounce scalper for Coinbase Wrapped BTC (cbBTC) on Solana, built for [make.fun's "Race a BTC trading bot live for 24 hours"](https://make.fun/bounty/btc-race-24h-20261118-1444) bounty ($250 in USDC).

## Strategy

Cash-default capitulation dip-buy: the bot waits flat until the 1-minute close sits at least 150 bps below the rolling 60-bar high **and** at least 20 bps above the rolling 10-bar low (a confirmed bounce off the dip), then buys with 100% of cash. It exits on take-profit (+200 bps), a hard stop (-100 bps), a trailing stop (armed at +120 bps, exits on a -60 bps pullback), or a 480-bar time stop. No entries after bar 1200 of the 1440-bar window.

## Dev-window result

On the frozen 24-hour dev window (17–18 Nov 2026): **net PnL +$17.84, 1 round trip (2 trades), max drawdown 1.50%** — buy $63,870.54, sell $65,061.94. The same configuration also made +$9.92 on the previous dev window, so it generalises rather than overfitting one dip.

## Run

```sh
python3 -P -s main.py
```

The bot speaks `agent-fun/bars-replay/v1`: newline-delimited JSON on stdin/stdout, one reply per batch. Standard library only, fully deterministic — no network, no wall clock, no files outside the repository.

## Referral

Join make.fun with my referral link: https://make.fun/r/gh9tewpq
