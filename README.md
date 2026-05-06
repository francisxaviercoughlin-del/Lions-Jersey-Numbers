# Detroit Lions Jersey Number Finder

This version fixes the Pro Football Reference `403 Forbidden` issue by using **nflverse roster CSV files from GitHub releases** instead of scraping Pro Football Reference.

## What it does

Enter:

- Detroit Lions jersey number
- Start/end season range, or exact dates

It returns Lions players listed with that jersey number during the selected seasons.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Upload `app.py` and `requirements.txt` to your GitHub repo.
2. In Streamlit Community Cloud, set the main file path to `app.py`.
3. Deploy.

## Optional logo

Add a file named:

```text
lions_logo.png
```

in the same folder as `app.py`.

## Notes

- Source: nflverse roster CSV files on GitHub releases.
- Data is season-level, not exact transaction-date-level.
- Exact date searches are converted to season years.
