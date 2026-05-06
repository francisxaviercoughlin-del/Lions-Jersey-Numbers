# Detroit Lions Jersey Number Finder — CSV Only V2

This version fixes duplicate player rows.

## What changed

The app now groups results by:

```text
Player + Number
```

instead of:

```text
Player + Number + Position + College
```

So if a player's position or college is blank/changed in one year, he will still show once.

## Required file

Put your real CSV in the same folder as app.py:

```text
detroit_lions_rosters_1936_2025.csv
```

Required columns:

```text
Season, Player, Number, Position, College
```

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
