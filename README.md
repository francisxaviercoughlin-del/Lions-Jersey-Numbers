# Detroit Lions Jersey Number Finder — CSV Only

This Streamlit app uses only your local CSV:

```text
detroit_lions_rosters_1936_2025.csv
```

No scraping. No web requests.

## Required CSV columns

```text
Season, Player, Number, Position, College
```

Extra columns are fine.

## Run locally

Put these files in the same folder:

```text
app.py
requirements.txt
detroit_lions_rosters_1936_2025.csv
```

Then run:

```bash
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit

Upload to GitHub:

```text
app.py
requirements.txt
detroit_lions_rosters_1936_2025.csv
```

Optional:

```text
lions_logo.png
```
