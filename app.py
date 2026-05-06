from pathlib import Path
import datetime as dt

import pandas as pd
import streamlit as st


DATA_FILE = Path("detroit_lions_rosters_1936_2025.csv")
LOGO_PATH = Path("lions_logo.png")


st.set_page_config(
    page_title="Detroit Lions Jersey Number Finder",
    page_icon="🦁",
    layout="wide",
)


CUSTOM_CSS = """
<style>
    :root {
        --lions-blue: #0076B6;
        --lions-dark-blue: #00338D;
        --lions-silver: #B0B7BC;
        --lions-white: #ffffff;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0,118,182,.16), transparent 34%),
            linear-gradient(180deg, #f8fbff 0%, #edf2f7 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    .lions-hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg, rgba(0,51,141,.98) 0%, rgba(0,118,182,.96) 58%, rgba(176,183,188,.92) 100%);
        color: white;
        padding: 30px 34px;
        border-radius: 26px;
        margin-bottom: 24px;
        box-shadow: 0 14px 34px rgba(0,51,141,.24);
        border: 1px solid rgba(255,255,255,.25);
    }

    .lions-hero:after {
        content: "LIONS";
        position: absolute;
        right: -14px;
        bottom: -36px;
        font-size: 110px;
        font-weight: 900;
        letter-spacing: 8px;
        color: rgba(255,255,255,.10);
        line-height: 1;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255,255,255,.17);
        border: 1px solid rgba(255,255,255,.26);
        border-radius: 999px;
        padding: 7px 13px;
        font-size: .8rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .lions-hero h1 {
        margin: 0;
        font-size: clamp(2rem, 4vw, 3.15rem);
        line-height: 1;
        font-weight: 900;
        letter-spacing: -0.035em;
    }

    .lions-hero p {
        margin: 14px 0 0 0;
        font-size: 1.08rem;
        max-width: 780px;
        opacity: .94;
    }

    .logo-card {
        background: white;
        border: 1px solid #dfe7ef;
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(17,24,39,.08);
        text-align: center;
    }

    .logo-placeholder {
        width: 94px;
        height: 94px;
        margin: 0 auto 8px auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--lions-blue), var(--lions-dark-blue));
        color: white;
        font-size: 48px;
        box-shadow: inset 0 0 0 5px rgba(255,255,255,.18);
    }

    .result-card {
        background: white;
        border: 1px solid #e1e8f0;
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(17,24,39,.07);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #edf5fb 100%);
        border-right: 1px solid #d7e2ee;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        background: linear-gradient(135deg, var(--lions-blue), var(--lions-dark-blue)) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,.18) !important;
        border-radius: 14px !important;
        font-weight: 900 !important;
        padding: .75rem 1rem !important;
        box-shadow: 0 8px 18px rgba(0,51,141,.22);
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        background: linear-gradient(135deg, #008bd7, #002b78) !important;
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #dde7f1;
        border-left: 7px solid var(--lions-blue);
        border-radius: 18px;
        padding: 15px 17px;
        box-shadow: 0 6px 18px rgba(17,24,39,.06);
    }

    div[data-testid="stMetricValue"] {
        color: var(--lions-dark-blue);
        font-weight: 900;
    }

    .blue-line {
        height: 6px;
        width: 100%;
        background: linear-gradient(90deg, var(--lions-blue), var(--lions-silver), var(--lions-dark-blue));
        border-radius: 999px;
        margin: 10px 0 22px 0;
    }

    .footer-note {
        color: #64748b;
        font-size: .86rem;
        margin-top: 16px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def clean_number(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    text = text.replace(".0", "")
    if text == "" or text.lower() == "nan":
        return None
    try:
        return int(float(text))
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Missing {DATA_FILE}. Put detroit_lions_rosters_1936_2025.csv in the same folder as app.py."
        )

    df = pd.read_csv(DATA_FILE)

    required = ["Season", "Player", "Number", "Position", "College"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    df = df.copy()
    df["Season"] = pd.to_numeric(df["Season"], errors="coerce").astype("Int64")
    df["Number"] = df["Number"].apply(clean_number).astype("Int64")
    df["Player"] = df["Player"].fillna("").astype(str).str.strip()
    df["Position"] = df["Position"].fillna("").astype(str).str.strip()
    df["College"] = df["College"].fillna("").astype(str).str.strip()

    df = df.dropna(subset=["Season", "Number"])
    df = df[df["Player"] != ""]

    return df


def compress_results(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for (player, number, position, college), group in df.groupby(
        ["Player", "Number", "Position", "College"], dropna=False
    ):
        seasons = sorted(group["Season"].astype(int).unique().tolist())

        spans = []
        if seasons:
            start = prev = seasons[0]
            for season in seasons[1:]:
                if season == prev + 1:
                    prev = season
                else:
                    spans.append((start, prev))
                    start = prev = season
            spans.append((start, prev))

        rows.append({
            "Player": player,
            "Number": int(number),
            "Position": position,
            "College": college,
            "Season Span": ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b in spans),
            "Matching Seasons": ", ".join(str(s) for s in seasons),
            "First Season": min(seasons) if seasons else None,
            "Last Season": max(seasons) if seasons else None,
        })

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    return out.sort_values(["First Season", "Player"], ascending=[False, True])


hero_left, hero_right = st.columns([4, 1])

with hero_left:
    st.markdown(
        """
        <div class="lions-hero">
            <div class="eyebrow">🦁 Detroit Lions CSV Database</div>
            <h1>Jersey Number Finder</h1>
            <p>Search your local Lions roster CSV by jersey number and season range. No scraping. No internet requests.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown('<div class="logo-card">', unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
        st.caption("Detroit Lions")
    else:
        st.markdown('<div class="logo-placeholder">🦁</div>', unsafe_allow_html=True)
        st.caption("CSV-only app")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

try:
    data = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

min_year = int(data["Season"].min())
max_year = int(data["Season"].max())
available_numbers = sorted(data["Number"].dropna().astype(int).unique().tolist())

with st.sidebar:
    st.header("Search the Pride")

    number = st.selectbox(
        "Jersey number",
        available_numbers,
        index=available_numbers.index(20) if 20 in available_numbers else 0,
    )

    start_year, end_year = st.slider(
        "Season range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    player_search = st.text_input("Optional player search", "")

    search = st.button("Find Lions", use_container_width=True)

    st.caption(f"Loaded {len(data):,} roster rows from {DATA_FILE.name}.")


if not search:
    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Ready for kickoff</h3>
            <p>Choose a jersey number and season range in the sidebar, then click <b>Find Lions</b>.</p>
            <p style="color:#64748b;margin-bottom:0;">CSV loaded: {len(data):,} rows covering {min_year}–{max_year}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

filtered = data[
    (data["Number"] == int(number)) &
    (data["Season"] >= int(start_year)) &
    (data["Season"] <= int(end_year))
].copy()

if player_search.strip():
    filtered = filtered[filtered["Player"].str.contains(player_search.strip(), case=False, na=False)]

summary = compress_results(filtered)

left, mid, right = st.columns(3)
left.metric("Jersey Number", f"#{int(number)}")
mid.metric("Selected Seasons", f"{int(start_year)}–{int(end_year)}")
right.metric("Matching Players", len(summary))

st.divider()

if summary.empty:
    st.warning(f"No Detroit Lions found wearing #{int(number)} from {int(start_year)} to {int(end_year)}.")
else:
    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Lions listed with #{int(number)} during {int(start_year)}–{int(end_year)}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_cols = ["Number", "Player", "Position", "College", "Season Span", "Matching Seasons"]
    st.dataframe(summary[display_cols], use_container_width=True, hide_index=True)

    csv = summary[display_cols].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Download results as CSV",
        data=csv,
        file_name=f"detroit_lions_number_{int(number)}_{int(start_year)}_{int(end_year)}.csv",
        mime="text/csv",
    )

    with st.expander("Show raw season rows"):
        raw_cols = ["Season", "Player", "Number", "Position", "College"]
        st.dataframe(
            filtered[raw_cols].sort_values(["Season", "Number", "Player"]),
            use_container_width=True,
            hide_index=True,
        )

st.markdown(
    '<div class="footer-note">This app reads only detroit_lions_rosters_1936_2025.csv from the app folder.</div>',
    unsafe_allow_html=True,
)
