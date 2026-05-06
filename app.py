import datetime as dt
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


TEAM = "det"
TEAM_CODE = "DET"
LOGO_PATH = Path("lions_logo.png")
LOCAL_DATA_PATH = Path("lions_uniform_numbers.csv")

# Primary historical source. This is the same PFR uniform-number table, but the aws host is often friendlier
# to cloud-hosted apps than www.pro-football-reference.com.
PFR_AWS_URL = "https://aws.pro-football-reference.com/players/uniform.cgi?number={number}&team={team}"

# Recent fallback only. nflverse roster jersey coverage is not complete historically.
NFLVERSE_ROSTER_URL = "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{season}.csv"


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


def normalize_uniform_df(df: pd.DataFrame, number: int, source: str) -> pd.DataFrame:
    """Normalize uniform history columns to Jersey #, Player, From, To, AV, Source."""
    if df.empty:
        return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"])

    rename_map = {}
    for col in df.columns:
        low = str(col).strip().lower()
        if low in ["player", "name"]:
            rename_map[col] = "Player"
        elif low in ["from", "first", "start", "start_year"]:
            rename_map[col] = "From"
        elif low in ["to", "last", "end", "end_year"]:
            rename_map[col] = "To"
        elif low in ["av"]:
            rename_map[col] = "AV"
        elif low in ["jersey #", "jersey", "number", "uniform_number"]:
            rename_map[col] = "Jersey #"

    df = df.rename(columns=rename_map).copy()

    if "Jersey #" not in df.columns:
        df["Jersey #"] = number

    expected = ["Jersey #", "Player", "From", "To", "AV"]
    for col in expected:
        if col not in df.columns:
            df[col] = None

    df["Jersey #"] = pd.to_numeric(df["Jersey #"], errors="coerce").fillna(number).astype(int)
    df["From"] = pd.to_numeric(df["From"], errors="coerce").astype("Int64")
    df["To"] = pd.to_numeric(df["To"], errors="coerce").astype("Int64")
    df["AV"] = pd.to_numeric(df["AV"], errors="coerce")
    df["Player"] = df["Player"].astype(str).str.replace("*", "", regex=False).str.replace("+", "", regex=False).str.strip()
    df["Source"] = source

    return df.dropna(subset=["Player", "From", "To"])[["Jersey #", "Player", "From", "To", "AV", "Source"]]


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def load_local_historical_data(number: int) -> pd.DataFrame:
    """Optional complete local CSV. Best long-term solution for Streamlit Cloud reliability."""
    if not LOCAL_DATA_PATH.exists():
        return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"])

    df = pd.read_csv(LOCAL_DATA_PATH)
    df = normalize_uniform_df(df, number, "Local CSV: lions_uniform_numbers.csv")
    return df[df["Jersey #"] == int(number)].copy()


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_pfr_aws_uniform_number(number: int) -> pd.DataFrame:
    """Historical uniform table from the PFR aws host."""
    url = PFR_AWS_URL.format(number=number, team=TEAM)
    headers = {
        "User-Agent": "Mozilla/5.0 Detroit-Lions-Jersey-App/1.0",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))
    if not tables:
        return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"])

    return normalize_uniform_df(tables[0], number, url)


def first_existing_column(df: pd.DataFrame, options: list[str]) -> str | None:
    for col in options:
        if col in df.columns:
            return col
    return None


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_nflverse_recent(start_year: int, end_year: int, number: int) -> pd.DataFrame:
    """Recent fallback only. nflverse jersey coverage is not complete historically."""
    frames = []
    for season in range(max(2009, start_year), end_year + 1):
        try:
            response = requests.get(NFLVERSE_ROSTER_URL.format(season=season), timeout=30)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            df["season"] = season
            frames.append(df)
        except Exception:
            pass

    if not frames:
        return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"])

    data = pd.concat(frames, ignore_index=True)
    team_col = first_existing_column(data, ["team", "recent_team", "club_code"])
    name_col = first_existing_column(data, ["player_name", "full_name", "football_name", "display_name"])
    jersey_col = first_existing_column(data, ["jersey_number", "jersey", "uniform_number", "number"])

    if not all([team_col, name_col, jersey_col]):
        return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"])

    data = data[data[team_col].astype(str).str.upper() == TEAM_CODE].copy()
    data[jersey_col] = pd.to_numeric(data[jersey_col], errors="coerce")
    data = data[data[jersey_col] == int(number)].copy()

    if data.empty:
        return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"])

    rows = []
    for player, group in data.groupby(name_col):
        seasons = sorted(group["season"].astype(int).unique().tolist())
        rows.append(
            {
                "Jersey #": int(number),
                "Player": player,
                "From": min(seasons),
                "To": max(seasons),
                "AV": None,
                "Source": "nflverse recent fallback only",
            }
        )
    return normalize_uniform_df(pd.DataFrame(rows), number, "nflverse recent fallback only")


def get_uniform_history(number: int, start_year: int, end_year: int, source_preference: str) -> tuple[pd.DataFrame, str, str]:
    """
    Returns df, source_used, warning.
    """
    warnings = []

    if source_preference in ["Auto", "Local CSV only"]:
        local = load_local_historical_data(number)
        if not local.empty:
            return local, "Local CSV", ""
        if source_preference == "Local CSV only":
            return local, "Local CSV", "No local CSV found or no matching records."

    if source_preference in ["Auto", "PFR AWS historical"]:
        try:
            pfr = fetch_pfr_aws_uniform_number(number)
            if not pfr.empty:
                return pfr, "PFR AWS historical", ""
        except Exception as e:
            warnings.append(f"PFR AWS historical source failed: {e}")

    if source_preference in ["Auto", "nflverse recent fallback"]:
        recent = fetch_nflverse_recent(start_year, end_year, number)
        if not recent.empty:
            msg = "Warning: nflverse jersey-number data is a recent fallback and may not go before 2009."
            return recent, "nflverse recent fallback", msg

    return pd.DataFrame(columns=["Jersey #", "Player", "From", "To", "AV", "Source"]), "None", " | ".join(warnings) if warnings else "No records found."


def filter_overlap(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    if df.empty:
        return df

    result = df[(df["From"] <= end_year) & (df["To"] >= start_year)].copy()
    if result.empty:
        return result

    result["Overlap Years"] = result.apply(
        lambda r: f"{max(int(r['From']), start_year)}–{min(int(r['To']), end_year)}",
        axis=1,
    )
    result["Full Number Span"] = result.apply(
        lambda r: f"{int(r['From'])}–{int(r['To'])}",
        axis=1,
    )

    cols = ["Jersey #", "Player", "Overlap Years", "Full Number Span"]
    if "AV" in result.columns:
        cols.append("AV")
    cols.append("Source")

    return result[cols].sort_values(["Full Number Span", "Player"], ascending=[False, True])


hero_left, hero_right = st.columns([4, 1])

with hero_left:
    st.markdown(
        """
        <div class="lions-hero">
            <div class="eyebrow">🦁 Detroit Lions Uniform History</div>
            <h1>Jersey Number Finder</h1>
            <p>Search any Lions jersey number and season range. Uses local historical CSV first, then PFR historical data, then recent roster fallback.</p>
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
        st.caption("Add lions_logo.png")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="blue-line"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Search the Pride")

    number = st.number_input("Jersey number", min_value=0, max_value=99, value=20, step=1)

    current_year = dt.date.today().year
    date_mode = st.radio("Range type", ["Years", "Exact dates"], horizontal=True)

    if date_mode == "Years":
        start_year, end_year = st.slider(
            "Season range",
            min_value=1930,
            max_value=max(current_year, 2026),
            value=(1950, min(current_year, 2026)),
        )
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input("Start date", value=dt.date(1950, 1, 1))
        with col_b:
            end_date = st.date_input("End date", value=dt.date.today())
        start_year = start_date.year
        end_year = end_date.year

    source_preference = st.selectbox(
        "Data source",
        ["Auto", "Local CSV only", "PFR AWS historical", "nflverse recent fallback"],
        help="Auto uses local CSV first, then the historical PFR AWS table, then nflverse as a recent fallback."
    )

    search = st.button("Find Lions", use_container_width=True)

    st.caption("Exact dates are converted to season years because source data is season-level.")


if not search:
    st.markdown(
        """
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Ready for kickoff</h3>
            <p>Choose a jersey number and season range in the sidebar, then click <b>Find Lions</b>.</p>
            <p style="color:#64748b;margin-bottom:0;">For the most reliable full history on Streamlit Cloud, add a completed <code>lions_uniform_numbers.csv</code> file.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if start_year > end_year:
    st.error("Start year must be before or equal to end year.")
    st.stop()

with st.spinner("Checking uniform history..."):
    try:
        all_rows, source_used, warning = get_uniform_history(int(number), int(start_year), int(end_year), source_preference)
        results = filter_overlap(all_rows, int(start_year), int(end_year))
    except Exception as e:
        st.error("I could not download or process the data.")
        st.exception(e)
        st.stop()

left, mid, right = st.columns(3)
left.metric("Jersey Number", f"#{int(number)}")
mid.metric("Selected Seasons", f"{int(start_year)}–{int(end_year)}")
right.metric("Matching Players", len(results))

if warning:
    st.warning(warning)

st.info(f"Data source used: {source_used}")

st.divider()

if results.empty:
    st.warning(f"No Detroit Lions found wearing #{int(number)} from {int(start_year)} to {int(end_year)}.")
else:
    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Lions who wore #{int(number)} during {int(start_year)}–{int(end_year)}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_cols = [c for c in ["Jersey #", "Player", "Overlap Years", "Full Number Span", "AV"] if c in results.columns]
    st.dataframe(results[display_cols], use_container_width=True, hide_index=True)

    csv = results[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download results as CSV",
        data=csv,
        file_name=f"detroit_lions_number_{int(number)}_{int(start_year)}_{int(end_year)}.csv",
        mime="text/csv",
    )

with st.expander("Best long-term data setup"):
    st.write(
        "For 100% reliability on Streamlit Cloud, create a file named `lions_uniform_numbers.csv` with columns:"
    )
    st.code("Jersey #,Player,From,To,AV", language="text")
    st.write(
        "The app will use that file first. If it is missing, it tries the PFR AWS historical table. "
        "If that fails, it falls back to nflverse recent roster data."
    )

st.markdown(
    '<div class="footer-note">Results are season-level, not exact transaction-date or game-by-game uniform usage.</div>',
    unsafe_allow_html=True,
)
