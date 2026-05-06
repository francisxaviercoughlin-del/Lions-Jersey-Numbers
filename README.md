# Detroit Lions Jersey Number Finder

A Detroit Lions-branded Streamlit app that lets you enter:

- Jersey number
- Start/end season range, or exact dates

It returns all Detroit Lions players who wore that number during any overlapping part of the selected timeframe.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Optional logo

To show a logo in the app, add a file named:

```text
lions_logo.png
```

in the same folder as `app.py`.

The app will automatically display it. If no logo file is present, it shows a Lions-style emoji badge.

## Deploy on Streamlit Community Cloud

1. Create or open your GitHub repo.
2. Upload `app.py`, `requirements.txt`, and optionally `lions_logo.png`.
3. In Streamlit Community Cloud, select the repo.
4. Set the main file path to `app.py`.
5. Deploy.

## Notes

Pro Football Reference uniform data is season-level. If you enter exact dates, the app converts those dates to years and searches season overlap.
