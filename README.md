# Detroit Lions Jersey Number Finder — Historical Version

This version fixes the problem where nflverse jersey-number data only goes back to recent seasons.

## Source order

The app now uses:

1. `lions_uniform_numbers.csv` if you add it locally
2. PFR's historical uniform-number table through the `aws.pro-football-reference.com` host
3. nflverse roster data only as a recent fallback

## Files

- `app.py`
- `requirements.txt`
- `lions_uniform_numbers.csv` sample file

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Best production setup

For the most reliable Streamlit Cloud deployment, build out `lions_uniform_numbers.csv` with:

```text
Jersey #,Player,From,To,AV
```

The app will use that local CSV first and will not depend on a website request.

## Notes

- Data is season-level, not game-by-game.
- Exact dates are converted to season years.
- nflverse is only used as a fallback because jersey number coverage may not go all the way back historically.
