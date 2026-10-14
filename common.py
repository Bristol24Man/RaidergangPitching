import math
import base64

PITCH_COLORS = {
    'fastball': '#e8862f', 'four-seam': '#e8862f', 'fourseam': '#e8862f',
    'sinker': '#e8862f', 'two-seam': '#e8862f', 'twoseam': '#e8862f',
    'slider': '#f5d020', 'sweeper': '#f5d020',
    'curveball': '#3a6ea5', 'curve': '#3a6ea5',
    'changeup': '#4caf50', 'change': '#4caf50',
    'cutter': '#8a4fd1',
}
FASTBALL_FAMILY_KEYWORDS = ('fastball', 'sinker', 'two-seam', 'twoseam', 'four-seam', 'fourseam', 'cutter')
DEFAULT_COLOR = '#888888'


def _norm(pt):
    return str(pt).strip().lower()


def pitch_color(pt):
    if pt is None or (isinstance(pt, float) and math.isnan(pt)):
        return DEFAULT_COLOR
    key = _norm(pt)
    if key in PITCH_COLORS:
        return PITCH_COLORS[key]
    for kw, color in PITCH_COLORS.items():
        if kw in key:
            return color
    return DEFAULT_COLOR


def is_fastball_family(pt):
    if pt is None or (isinstance(pt, float) and math.isnan(pt)):
        return False
    key = _norm(pt)
    return any(kw in key for kw in FASTBALL_FAMILY_KEYWORDS)


def pitch_sort_key(pt):
    color = pitch_color(pt)
    order = ['#e8862f', '#f5d020', '#3a6ea5', '#4caf50', '#8a4fd1', DEFAULT_COLOR]
    try:
        idx = order.index(color)
    except ValueError:
        idx = len(order)
    return (idx, _norm(pt))


def load_logo_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


def cond_cell(value, goal, lower_better=False, suffix='%'):
    if value is None:
        return '<td>–</td>'
    ok = (value <= goal) if lower_better else (value >= goal)
    if ok:
        bg, fg = '#c9ecd0', '#1c6b2c'
    else:
        bg, fg = '#f6c8c8', '#a11d1d'
    return f'<td style="background:{bg};color:{fg};font-weight:bold;">{value:.1f}{suffix}</td>'
