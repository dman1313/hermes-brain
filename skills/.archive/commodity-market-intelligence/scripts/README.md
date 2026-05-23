The CFTC COT scanner script lives at `~/.hermes/scripts/cot-scanner.py` (the cron scripts directory).
It is NOT duplicated here to avoid drift — the cron job references that path directly.

Key implementation notes for modifications:
- Uses `urllib` (stdlib only, no pip dependencies)
- Z-score threshold: 2.0σ (configurable at top of script)
- Lookback: 26 weeks (configurable)
- All CFTC API calls go through `fetch_json()` which handles URL encoding
- Disaggregated COT fields: `m_money_positions_long_all`, `m_money_positions_short_all`, `m_money_positions_spread_all`, `open_interest_all`
- Legacy COT fields: `noncomm_positions_long_all`, `noncomm_positions_short_all`, `noncomm_postions_spread_all` (note CFTC typo), `conc_net_le_4_tdr_long_all`, `conc_net_le_4_tdr_short_all`
