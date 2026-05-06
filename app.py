import datetime as dt
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


TEAM = "det"
PFR_URL = "https://www.pro-football-reference.com/players/uniform.cgi?number={number}&team={team}"
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
        max-width: 720px;
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

    div.stButton > button {
        background: linear-gradient(135deg, var(--lions-blue), var(--lions-dark-blue)) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,.18) !important;
        border-radius: 14px !important;
        font-weight: 900 !important;
        padding: .75rem 1rem !important;
        box-shadow: 0 8px 18px rgba(0,51,141,.22);
    }

    div.stButton > button:hover {
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


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_uniform_number(number: int) -> pd.DataFrame:
    url = PFR_URL.format(number=number, team=TEAM)
    headers = {"User-Agent": "Mozilla/5.0 jersey-number-research-app/1.0"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))
    if not tables:
        return pd.DataFrame(columns=["Player", "From", "To", "AV", "Source"])

    df = tables[0].copy()
    keep = [c for c in ["Player", "From", "To", "AV"] if c in df.columns]
    df = df[keep]

    if "From" in df.columns:
        df["From"] = pd.to_numeric(df["From"], errors="coerce").astype("Int64")
    if "To" in df.columns:
        df["To"] = pd.to_numeric(df["To"], errors="coerce").astype("Int64")
    if "AV" in df.columns:
        df["AV"] = pd.to_numeric(df["AV"], errors="coerce")

    df["Jersey #"] = number
    df["Source"] = url
    return df


def overlap_filter(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    if df.empty:
        return df

    mask = (df["From"] <= end_year) & (df["To"] >= start_year)
    result = df.loc[mask].copy()

    if result.empty:
        return result

    result["Overlap Years"] = result.apply(
        lambda r: f"{max(int(r['From']), start_year)}–{min(int(r['To']), end_year)}",
        axis=1,
    )
    result["Full Lions Number Span"] = result.apply(
        lambda r: f"{int(r['From'])}–{int(r['To'])}",
        axis=1,
    )

    cols = ["Jersey #", "Player", "Overlap Years", "Full Lions Number Span"]
    if "AV" in result.columns:
        cols.append("AV")
    cols.append("Source")

    return result[cols].sort_values(["Full Lions Number Span", "Player"], ascending=[False, True])


hero_left, hero_right = st.columns([4, 1])

with hero_left:
    st.markdown(
        """
        <div class="lions-hero">
            <div class="eyebrow">🦁 Detroit Lions Uniform History</div>
            <h1>Jersey Number Finder</h1>
            <p>Search any Lions jersey number and season range to see every player who wore it during that timeframe.</p>
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
            min_value=1930,
            max_value=max(current_year + 1, 2026),
            value=(1990, current_year),
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

    st.caption("Exact dates are converted to NFL seasons by year because source data is season-level.")


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

with st.spinner("Checking the Lions uniform history..."):
    try:
        raw = fetch_uniform_number(int(number))
        results = overlap_filter(raw, int(start_year), int(end_year))
    except Exception as e:
        st.error("I could not fetch the data source right now.")
        st.exception(e)
        st.stop()

left, mid, right = st.columns(3)
left.metric("Jersey Number", f"#{int(number)}")
mid.metric("Selected Range", f"{int(start_year)}–{int(end_year)}")
right.metric("Matching Players", len(results))

st.divider()

if results.empty:
    st.warning(f"No Detroit Lions found wearing #{int(number)} from {int(start_year)} to {int(end_year)}.")
    st.caption("Try widening the year range.")
else:
    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0;color:#00338D;">Lions who wore #{int(number)} during {int(start_year)}–{int(end_year)}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        results.drop(columns=["Source"]),
        use_container_width=True,
        hide_index=True,
    )

    csv = results.drop(columns=["Source"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download results as CSV",
        data=csv,
        file_name=f"detroit_lions_number_{int(number)}_{int(start_year)}_{int(end_year)}.csv",
        mime="text/csv",
    )

    with st.expander("Source link"):
        st.write(results["Source"].iloc[0])

st.markdown(
    '<div class="footer-note">Data source: Pro Football Reference uniform-number pages. Results reflect season spans, not exact transaction dates.</div>',
    unsafe_allow_html=True,
)
