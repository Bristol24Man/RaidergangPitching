import io
import zipfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from game_report import build_pitcher_report, write_report  # noqa: F401
from game_css import CSS

st.set_page_config(page_title="WSU After Action Reports", page_icon="⚾", layout="wide")
st.title("Wright State Baseball – After Action Report Generator")
st.caption("Upload TrackMan-style tracked-session / game CSVs. Get a 2-page HTML report per pitcher.")

with st.sidebar:
    st.header("Settings")
    team_code = st.text_input("Team code to report on", value="WRI_RAI",
                              help="Only pitchers with this PitcherTeam are included (opponents are skipped).")
    st.markdown("Files with **BP** in the filename are skipped automatically.")

files = st.file_uploader("Upload CSV file(s)", type=["csv"], accept_multiple_files=True)


def build_html(name, date_label, df):
    page1, page2 = build_pitcher_report(name, date_label, df)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>{name} - After Action Report</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
{CSS}</head><body>{page1}{page2}</body></html>"""


if files:
    frames = []
    for f in files:
        if "BP" in f.name.upper():
            st.warning(f"Skipped {f.name} (BP file).")
            continue
        try:
            d = pd.read_csv(f)
        except Exception as e:
            st.error(f"Could not read {f.name}: {e}")
            continue
        required = {"Pitcher", "TaggedPitchType", "PitchCall", "KorBB", "Balls", "Strikes",
                    "Inning", "PAofInning", "PitchofPA"}
        missing = required - set(d.columns)
        if missing:
            st.error(f"{f.name} is missing columns: {', '.join(sorted(missing))}")
            continue
        d["_src"] = f.name
        frames.append(d)

    if frames:
        data = pd.concat(frames, ignore_index=True)
        if "PitcherTeam" in data.columns and team_code:
            data = data[data["PitcherTeam"] == team_code]
        if data.empty:
            st.warning("No rows left after team filter.")
            st.stop()

        mode = st.radio("Report mode", ["Separate report per file per pitcher", "One combined report per pitcher"],
                        horizontal=True)

        # Build report jobs
        jobs = []  # (pitcher, date_label, df, src)
        if mode.startswith("Separate"):
            for src, g in data.groupby("_src"):
                for p, gp in g.groupby("Pitcher"):
                    date_label = str(gp["Date"].iloc[0]) if "Date" in gp.columns else ""
                    jobs.append((p, date_label, gp, src))
        else:
            for p, gp in data.groupby("Pitcher"):
                dates = sorted(gp["Date"].astype(str).unique()) if "Date" in gp.columns else []
                label = dates[0] if len(dates) == 1 else (f"{dates[0]} to {dates[-1]}" if dates else "")
                jobs.append((p, label, gp, "combined"))

        st.subheader("Session numbers")
        st.caption("Sets the number in each filename, e.g. 'Smith Private 3.html'.")
        prefix = st.text_input("Filename label", value="Private")
        cols = st.columns(4)
        numbers = {}
        for i, (p, dl, gp, src) in enumerate(jobs):
            with cols[i % 4]:
                numbers[i] = st.number_input(f"{p} ({dl or src})", min_value=1, value=1, step=1, key=f"n{i}")

        if st.button("Generate reports", type="primary"):
            buf = io.BytesIO()
            results = []
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for i, (p, dl, gp, src) in enumerate(jobs):
                    last = p.split(",")[0].strip()
                    suffix = "Combined" if mode.startswith("One") else f"{prefix} {numbers[i]}"
                    fname = f"{last} {suffix}.html"
                    html = build_html(p, dl, gp)
                    z.writestr(fname, html)
                    results.append((fname, html))
            st.session_state["results"] = results
            st.session_state["zip"] = buf.getvalue()

if "results" in st.session_state:
    st.success(f"Generated {len(st.session_state['results'])} report(s).")
    st.download_button("Download all (ZIP)", st.session_state["zip"], "After_Action_Reports.zip",
                       "application/zip")
    names = [r[0] for r in st.session_state["results"]]
    pick = st.selectbox("Preview report", names)
    html = dict(st.session_state["results"])[pick]
    st.download_button("Download this report", html, pick, "text/html")
    components.html(html, height=1500, scrolling=True)
