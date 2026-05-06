import datetime as dt
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


TEAM = "DET"
LOGO_PATH = Path("lions_logo.png")
ROSTER_URL = "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{season}.csv"


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
        --lions-gray: #f2f5f8;
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
        max-width: 760px;
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

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--lions-dark-blue);
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
        transform: translateY(-1px);
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

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #dae4ef;
    }

    .footer-note {
        color: #64748b;
        font-size: .86rem;
        margin-top: 16px;
    }

    .blue-line {
        height: 6px;
        width: 100%;
        background: linear-gradient(90deg, var(--lions-blue), var(--lions-silver), var(--lions-dark-blue));
        border-radius: 999px;
        margin: 10px 0 22px 0;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _first_existing_column(df: pd.DataFrame, options: list[str]) -> str | None:
    for col in options:
        if col in df.columns:
            return col
    return None


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_roster_for_season(season: int) -> pd.DataFrame:
    """
    Fetch one season of nflverse roster data from GitHub releases.
    This avoids Pro Football Reference 403 blocks on Streamlit Cloud.
    """
    url = ROSTER_URL.format(season=season)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text), low_memory=False)
    df["season"] = season
    return df


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_lions_rosters(start_year: int, end_year: int) -> pd.DataFrame:
    frames = []
    failed = []

    for season in range(start_year, end_year + 1):
        try:
            df = fetch_roster_for_season(season)
            frames.append(df)
        except Exception:
            failed.append(season)

    if not frames:
        raise RuntimeError(
            "No roster seasons could be downloaded. Check your internet connection or try a smaller range."
        )

    data = pd.concat(frames, ignore_index=True)

    team_col = _first_existing_column(data, ["team", "recent_team", "club_code"])
    if team_col is None:
        raise RuntimeError("Could not find a team column in the roster data.")

    data = data[data[team_col].astype(str).str.upper() == TEAM].copy()

    name_col = _first_existing_column(data, ["player_name", "full_name", "football_name", "display_name"])
    jersey_col = _first_existing_column(data, ["jersey_number", "jersey", "uniform_number", "number"])
    pos_col = _first_existing_column(data, ["position", "position_group"])

    if name_col is None or jersey_col is None:
        raise RuntimeError("Could not find player name or jersey number columns in the roster data.")

    keep_cols = ["season", name_col, jersey_col]
    if pos_col is not None:
        keep_cols.append(pos_col)

    out = data[keep_cols].copy()
    out = out.rename(
        columns={
            name_col: "Player",
            jersey_col: "Jersey #",
            pos_col if pos_col is not None else "position": "Position",
        }
    )

    out["Jersey #"] = pd.to_numeric(out["Jersey #"], errors="coerce")
    out = out.dropna(subset=["Jersey #", "Player"])
    out["Jersey #"] = out["Jersey #"].astype(int)

    if "Position" not in out.columns:
        out["Position"] = ""

    out["Source"] = "nflverse roster CSVs on GitHub releases"
    out["Download Issues"] = ", ".join(map(str, failed)) if failed else ""
    return out


def compress_player_spans(df: pd.DataFrame, number: int) -> pd.DataFrame:
    matches = df[df["Jersey #"] == int(number)].copy()
    if matches.empty:
        return matches

    grouped_rows = []
    for (player, jersey), group in matches.groupby(["Player", "Jersey #"], dropna=False):
        seasons = sorted(group["season"].dropna().astype(int).unique().tolist())
        positions = sorted({str(x) for x in group.get("Position", pd.Series(dtype=str)).dropna().unique() if str(x) != "nan"})
        spans = []
        if seasons:
            start = prev = seasons[0]
            for yr in seasons[1:]:
                if yr == prev + 1:
                    prev = yr
                else:
                    spans.append((start, prev))
                    start = prev = yr
            spans.append((start, prev))

        grouped_rows.append(
            {
                "Jersey #": jersey,
                "Player": player,
                "Position": ", ".join(positions),
                "Matching Seasons": ", ".join(str(y) for y in seasons),
                "Season Span": ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b in spans),
                "First Season": min(seasons) if seasons else None,
                "Last Season": max(seasons) if seasons else None,
            }
        )

    result = pd.DataFrame(grouped_rows)
    return result.sort_values(["First Season", "Player"], ascending=[False, True])


hero_left, hero_right = st.columns([4, 1])

with hero_left:
    st.markdown(
        """
        <div class="lions-hero">
            <div class="eyebrow">🦁 Detroit Lions Uniform History</div>
            <h1>Jersey Number Finder</h1>
            <p>Search any Lions jersey number and season range to see every player listed with that number during those seasons.</p>
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
        st.caption("Add lions_logo.png to show your logo")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Search the Pride")
    st.caption("Enter a number and timeframe.")

    number = st.number_input("Jersey number", min_value=0, max_value=99, value=20, step=1)

    current_year = dt.date.today().year
    date_mode = st.radio("Range type", ["Years", "Exact dates"], horizontal=True)

    if date_mode == "Years":
        start_year, end_year = st.slider(
            "Season range",
            min_value=1920,
            max_value=max(current_year, 2026),
            value=(1990, min(current_year, 2026)),
        )
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input("Start date", value=dt.date(1990, 1, 1))
        with col_b:
            end_date = st.date_input("End date", value=dt.date.today())
        start_year = start_date.year
        end_year = end_date.year

    search = st.button("Find Lions", use_container_width=True)

    st.caption("Exact dates are converted to NFL seasons by year because roster data is season-level.")


if not search:
    st.markdown(
        """
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Ready for kickoff</h3>
            <p>Choose a jersey number and season range in the sidebar, then click <b>Find Lions</b>.</p>
            <p style="color:#64748b;margin-bottom:0;">Example: #20 from 1989–1997.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if start_year > end_year:
    st.error("Start year must be before or equal to end year.")
    st.stop()

with st.spinner("Checking nflverse roster files..."):
    try:
        raw = fetch_lions_rosters(int(start_year), int(end_year))
        results = compress_player_spans(raw, int(number))
    except Exception as e:
        st.error("I could not download or process the roster data.")
        st.exception(e)
        st.stop()

left, mid, right = st.columns(3)
left.metric("Jersey Number", f"#{int(number)}")
mid.metric("Selected Seasons", f"{int(start_year)}–{int(end_year)}")
right.metric("Matching Players", len(results))

st.divider()

if results.empty:
    st.warning(f"No Detroit Lions found wearing #{int(number)} from {int(start_year)} to {int(end_year)}.")
    st.caption("Try widening the year range.")
else:
    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Lions listed with #{int(number)} during {int(start_year)}–{int(end_year)}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_cols = ["Jersey #", "Player", "Position", "Season Span", "Matching Seasons"]
    st.dataframe(
        results[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    csv = results[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download results as CSV",
        data=csv,
        file_name=f"detroit_lions_number_{int(number)}_{int(start_year)}_{int(end_year)}.csv",
        mime="text/csv",
    )

    issues = raw["Download Issues"].iloc[0] if "Download Issues" in raw.columns and len(raw) else ""
    if issues:
        st.info(f"Some seasons could not be downloaded and were skipped: {issues}")

with st.expander("Data source"):
    st.write("This version uses nflverse roster CSV files from GitHub releases instead of Pro Football Reference scraping.")
    st.code(ROSTER_URL, language="text")

st.markdown(
    '<div class="footer-note">Data source: nflverse roster CSVs. Results reflect season roster listings, not exact transaction dates or game-by-game uniform usage.</div>',
    unsafe_allow_html=True,
)
