# Data policy and sample data

The committed files under `data/sample/` are deterministic and entirely synthetic. They describe fictional sources, events, prices, volumes, and annotations for software testing only. They are not historical market observations and must not be used to evaluate investment strategies.

## Files

- `news_articles.csv`: six fictional news records, including one duplicate group and one multi-asset article
- `market_candles.csv`: eight fictional hourly BTC/USD and ETH/USD candles
- `annotations.csv`: seven target-specific human-style labels, including two labels for the multi-asset article

## Storage boundaries

- `data/raw/` is ignored because provider data may have redistribution restrictions.
- `data/private/` is ignored because annotation or research datasets may not be publishable.
- Derived public samples must be synthetic, licensed, or demonstrably permitted before commit.

Run validation from the repository root:

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.validation data/sample
```
