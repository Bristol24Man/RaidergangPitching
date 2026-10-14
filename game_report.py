import sys
import pandas as pd
from common import pitch_color, is_fastball_family, load_logo_b64, cond_cell, pitch_sort_key
from charts import zone_diagram
from charts_page1 import spin_direction_chart, movement_chart, release_chart, circular_mean_tilt
from game_css import CSS

from logo_data import LOGO_B64

STRIKE_CALLS = {'strikecalled', 'strikeswinging', 'foulballnotfieldable', 'foulballfieldable', 'inplay'}
SWING_CALLS = {'strikeswinging', 'foulballnotfieldable', 'foulballfieldable', 'inplay'}
SWSTR_CALLS = {'strikeswinging'}

ZONE_SIDE = 8.5 / 12.0
ZONE_TOP = 3.5
ZONE_BOTTOM = 1.5


def norm_call(v):
    return str(v).strip().lower().replace(' ', '').replace('-', '')


def _f(row, col):
    try:
        v = row[col]
        if pd.isna(v):
            return None
        return float(v)
    except (KeyError, ValueError, TypeError):
        return None


def build_pitcher_report(pitcher_name, date_label, df):
    """df: rows (already filtered to this pitcher, possibly spanning >1 file)."""
    df = df.copy()
    df['_call'] = df['PitchCall'].apply(norm_call)
    df['_korbb'] = df['KorBB'].astype(str).str.strip().str.lower()

    logo_b64 = LOGO_B64

    # ---------- PAGE 1 : metric table + charts ----------
    pitch_types = sorted(df['TaggedPitchType'].dropna().unique(), key=pitch_sort_key)

    metric_rows = []
    spin_pts, move_pts, rel_pts = [], [], []
    legend_items = []
    for pt in pitch_types:
        sub = df[df['TaggedPitchType'] == pt]
        color = pitch_color(pt)
        legend_items.append((pt, color))
        velo = sub['RelSpeed'].dropna()
        spin = sub['SpinRate'].dropna()
        ivb = sub['InducedVertBreak'].dropna()
        hb = sub['HorzBreak'].dropna()
        rs = sub['RelSide'].dropna()
        rh = sub['RelHeight'].dropna()
        ext = sub['Extension'].dropna()
        tilt_mean = circular_mean_tilt(sub['Tilt'].dropna().tolist())

        def a1(s):
            return f'{s.mean():.1f}' if len(s) else '–'

        row = (
            '<tr class="current-row">'
            f'<td class="pitch-cell" style="border-left:6px solid {color};">{pt}<span class="tag">Current</span></td>'
            f'<td>{a1(velo)}</td>'
            f'<td>{f"{velo.max():.1f}" if len(velo) else "–"}</td>'
            f'<td>{f"{spin.mean():.0f}" if len(spin) else "–"}</td>'
            f'<td>{a1(ivb)}</td>'
            f'<td>{a1(hb)}</td>'
            f'<td>{a1(rs)}</td>'
            f'<td>{a1(rh)}</td>'
            f'<td>{a1(ext)}</td>'
            '<td>–</td>'
            f'<td>{tilt_mean}</td>'
            '</tr>'
            '<tr class="season-row">'
            f'<td class="pitch-cell" style="border-left:6px solid {color};"><span class="tag-season">Season</span></td>'
            '<td colspan="10" class="season-note">– no season data in file</td>'
            '</tr>'
        )
        metric_rows.append(row)

        for _, r in sub.iterrows():
            spin_pts.append({'tilt': r.get('Tilt'), 'spin_rate': _f(r, 'SpinRate'), 'color': color})
            move_pts.append({'horz_break': _f(r, 'HorzBreak'), 'vert_break': _f(r, 'InducedVertBreak'), 'color': color})
            rel_pts.append({'rel_side': _f(r, 'RelSide'), 'rel_height': _f(r, 'RelHeight'), 'color': color})

    legend_html = ''.join(
        f'<span class="leg-item"><span class="leg-dot" style="background:{c}"></span>{pt}</span>'
        for pt, c in legend_items
    )

    svg_spin = spin_direction_chart(spin_pts)
    svg_move = movement_chart(move_pts)
    svg_rel = release_chart(rel_pts)

    page1 = f'''
    <div class="page">
    <div class="header">
      <img class="logo" src="data:image/png;base64,{logo_b64}" alt="Wright State Raiders">
      <div class="header-title">
        <span class="pitcher-name">{pitcher_name}</span><span class="report-sub"> &nbsp;—&nbsp; After Action Report</span>
      </div>
      <div class="header-date">{date_label}</div>
    </div>

    <table class="metric-table">
      <thead>
        <tr>
          <th>Pitch</th><th>Velo.</th><th>MAX Velo.</th><th>Spin Rate</th><th>Ind. VB</th>
          <th>H. Break</th><th>Rel. Side</th><th>Rel Ht.</th><th>Exten.</th><th>Effcy.</th><th>Tilt</th>
        </tr>
      </thead>
      <tbody>
        {''.join(metric_rows)}
      </tbody>
    </table>

    <div class="legend-row">{legend_html}</div>
    <div class="charts-row">
      <div class="chart-box"><div class="chart-title">Spin Direc. – Game</div>{svg_spin}</div>
      <div class="chart-box"><div class="chart-title">Break/Movement – Game</div>{svg_move}</div>
      <div class="chart-box"><div class="chart-title">Release Position – Game</div>{svg_rel}</div>
    </div>
    <div class="page1-note">Game = current tracked session.</div>
    </div>
    '''

    # ---------- PAGE 2 : stat line + zone diagrams ----------
    total_pitches = len(df)
    pa_groups = list(df.groupby(['Inning', 'PAofInning']).groups.keys())
    bf = len(pa_groups)

    fps_num = 0
    for _, g in df.groupby(['Inning', 'PAofInning']):
        g = g.sort_values('PitchofPA')
        if g.iloc[0]['_call'] in STRIKE_CALLS:
            fps_num += 1
    fps_pct = 100.0 * fps_num / bf if bf else 0.0
    swing_pct = 100.0 * df['_call'].isin(SWING_CALLS).sum() / total_pitches if total_pitches else 0.0
    swstr_pct = 100.0 * df['_call'].isin(SWSTR_CALLS).sum() / total_pitches if total_pitches else 0.0
    k_count = (df['_korbb'] == 'strikeout').sum()
    bb_count = (df['_korbb'] == 'walk').sum()
    k_pct = 100.0 * k_count / bf if bf else 0.0
    bb_pct = 100.0 * bb_count / bf if bf else 0.0
    kbb_pct = k_pct - bb_pct

    attack_df = df[df['Strikes'] < 2]

    def in_zone(row):
        s, h = _f(row, 'PlateLocSide'), _f(row, 'PlateLocHeight')
        if s is None or h is None:
            return False
        return (-ZONE_SIDE <= s <= ZONE_SIDE) and (ZONE_BOTTOM <= h <= ZONE_TOP)

    if len(attack_df):
        attack_pct = 100.0 * attack_df.apply(in_zone, axis=1).sum() / len(attack_df)
        attack_pct_str = f'{attack_pct:.1f}%'
        attack_cell = cond_cell(attack_pct, 63)
    else:
        attack_pct_str = '–'
        attack_cell = '<td>–</td>'

    finish_df = df[df['Strikes'] == 2]
    if len(finish_df):
        finish_pct = 100.0 * finish_df['_call'].isin(SWSTR_CALLS).sum() / len(finish_df)
        finish_pct_str = f'{finish_pct:.1f}%'
        finish_cell = cond_cell(finish_pct, 50)
    else:
        finish_pct_str = '–'
        finish_cell = '<td>–</td>'

    def to_pitch_list(sub_df, fastball):
        out = []
        for _, row in sub_df.iterrows():
            pt = row.get('TaggedPitchType')
            if is_fastball_family(pt) != fastball:
                continue
            s, h = _f(row, 'PlateLocSide'), _f(row, 'PlateLocHeight')
            if s is None or h is None:
                continue
            out.append({'side': s, 'height': h, 'color': pitch_color(pt)})
        return out

    svg_attack_fb = zone_diagram(to_pitch_list(attack_df, True), shade='full')
    svg_attack_nonfb = zone_diagram(to_pitch_list(attack_df, False), shade='full')
    svg_finish_fb = zone_diagram(to_pitch_list(finish_df, True), shade='top')
    svg_finish_nonfb = zone_diagram(to_pitch_list(finish_df, False), shade='bottom')

    stat_row = (
        '<tr>'
        '<td>–</td>' + f'<td>{bf}</td>' + f'<td>{total_pitches}</td>'
        + cond_cell(fps_pct, 60)
        + cond_cell(swing_pct, 47)
        + cond_cell(swstr_pct, 14)
        + attack_cell
        + finish_cell
        + cond_cell(k_pct, 30)
        + cond_cell(bb_pct, 8, lower_better=True)
        + cond_cell(kbb_pct, 22)
        + '<td>–</td>'
        + '</tr>'
    )
    goal_row = (
        '<tr class="goal-row">'
        '<td></td><td></td><td></td>'
        '<td>60%</td><td>47%</td><td>14%</td><td>63%</td><td>50%</td>'
        '<td>30%</td><td>8%</td><td>22%</td><td></td>'
        '</tr>'
    )

    legend_col_html = '<div class="legend-col">' + ''.join(
        f'<span class="leg-item"><span class="leg-dot" style="background:{c}"></span>{pt}</span>'
        for pt, c in legend_items
    ) + '</div>'

    page2 = f'''
    <div class="page">
    <div class="header">
      <img class="logo" src="data:image/png;base64,{logo_b64}" alt="Wright State Raiders">
      <div class="header-title">
        <span class="pitcher-name">{pitcher_name}</span><span class="report-sub"> &nbsp;—&nbsp; After Action Report</span>
      </div>
      <div class="header-date">{date_label}</div>
    </div>

    <table class="stat-table">
      <thead>
        <tr>
          <th>IP</th><th>BF</th><th>Pitches</th><th>FPS %</th><th>Swing %</th><th>SwStr %</th>
          <th>Attack %</th><th>Finish %</th><th>K %</th><th>BB %</th><th>K–BB %</th><th>MANS</th>
        </tr>
      </thead>
      <tbody>
        {stat_row}
        {goal_row}
      </tbody>
    </table>

    <div class="section-bar">ATTACK</div>
    <div class="section-sub">Less than 2 Strikes</div>
    <div class="zone-row">
      <div class="zone-col"><div class="zone-label">Fastballs</div>{svg_attack_fb}</div>
      <div class="zone-col"><div class="zone-label">Non-Fastballs</div>{svg_attack_nonfb}</div>
      <div class="zone-info">
        {legend_col_html}
        <div class="info-line"><strong>Pitch Call:</strong> called/tracked pitches</div>
        <div class="info-line"><strong>ATTACK – Pre 2K In-Zone %:</strong> {attack_pct_str}</div>
      </div>
    </div>

    <div class="section-bar">FINISH</div>
    <div class="section-sub">2 Strikes</div>
    <div class="zone-row">
      <div class="zone-col"><div class="zone-label">Fastballs</div>{svg_finish_fb}</div>
      <div class="zone-col"><div class="zone-label">Non-Fastballs</div>{svg_finish_nonfb}</div>
      <div class="zone-info">
        <div class="info-line"><strong>FINISH – 2K Swinging Strike %:</strong> {finish_pct_str}</div>
      </div>
    </div>
    </div>
    '''

    return page1, page2


def write_report(pitcher_name, date_label, df, out_path):
    page1, page2 = build_pitcher_report(pitcher_name, date_label, df)
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{pitcher_name} - After Action Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
{CSS}
</head>
<body>
{page1}
{page2}
</body>
</html>
'''
    with open(out_path, 'w') as f:
        f.write(html)
    return out_path
