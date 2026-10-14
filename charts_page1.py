import math

FONT = "Georgia, 'Times New Roman', serif"


def _nice_step(raw):
    if raw <= 0:
        return 1
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def tilt_to_deg(tilt_str):
    """Clock string like '9:45' -> degrees clockwise from 12 (top)."""
    if tilt_str is None:
        return None
    s = str(tilt_str).strip()
    if not s or s.lower() in ('nan', 'undefined', '-', '–'):
        return None
    parts = s.split(':')
    if len(parts) != 2:
        return None
    try:
        h = int(parts[0]) % 12
        m = int(parts[1])
    except ValueError:
        return None
    return (h + m / 60.0) * 30.0


def deg_to_tilt(deg):
    deg = deg % 360.0
    total_min = deg / 30.0 * 60.0
    h = int(total_min // 60) % 12
    m = int(round(total_min % 60))
    if m == 60:
        m = 0
        h = (h + 1) % 12
    if h == 0:
        h = 12
    return f'{h}:{m:02d}'


def circular_mean_tilt(tilt_strs):
    xs, ys = [], []
    for t in tilt_strs:
        d = tilt_to_deg(t)
        if d is None:
            continue
        rad = math.radians(d)
        xs.append(math.sin(rad))
        ys.append(math.cos(rad))
    if not xs:
        return '–'
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    if abs(mx) < 1e-9 and abs(my) < 1e-9:
        return '–'
    mean_deg = math.degrees(math.atan2(mx, my))
    return deg_to_tilt(mean_deg)


def _text(x, y, s, size=9, anchor='middle', weight='normal', fill='#888', rotate=None):
    rot = f' transform="rotate({rotate})"' if rotate else ''
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}" font-family="{FONT}" style=""{rot}>{s}</text>')


def spin_direction_chart(pitches):
    """pitches: list of dicts with 'tilt' (clock string), 'spin_rate' (float), 'color'."""
    W = H = 560
    cx = cy = 280.0
    r_outer = 224.0
    svg = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto;">']
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff" stroke="none" stroke-width="1" opacity="1"/>')

    rates = [p['spin_rate'] for p in pitches if p.get('spin_rate') is not None]
    if rates:
        dmin, dmax = min(rates), max(rates)
        if dmax - dmin < 1:
            dmax = dmin + 50
        pad = (dmax - dmin) * 0.20
        domain_min = max(0, dmin - pad)
        domain_max = dmax + pad
    else:
        domain_min, domain_max = 0, 3000

    for i in range(1, 5):
        r = r_outer * i / 4.0
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#cccccc" stroke-width="1" opacity="1"/>')
        val = domain_min + (domain_max - domain_min) * i / 4.0
        svg.append(_text(cx + 6, cy - r + 5, f'{val:.0f}', size=9, anchor='start', fill='#999'))
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#999" stroke-width="1.3" opacity="1"/>')

    svg.append(f'<line x1="{cx}" y1="{cy - r_outer}" x2="{cx}" y2="{cy + r_outer}" stroke="#cccccc" stroke-width="1"/>')
    svg.append(f'<line x1="{cx - r_outer}" y1="{cy}" x2="{cx + r_outer}" y2="{cy}" stroke="#cccccc" stroke-width="1"/>')
    svg.append(_text(cx, cy - r_outer - 8, '12', size=12, weight='bold', fill='#555'))
    svg.append(_text(cx + r_outer + 16, cy + 4, '3', size=12, weight='bold', fill='#555'))
    svg.append(_text(cx, cy + r_outer + 18, '6', size=12, weight='bold', fill='#555'))
    svg.append(_text(cx - r_outer - 16, cy + 4, '9', size=12, weight='bold', fill='#555'))

    def rmap(v):
        if domain_max == domain_min:
            return 0
        frac = (v - domain_min) / (domain_max - domain_min)
        return max(0, frac) * r_outer

    for p in pitches:
        deg = tilt_to_deg(p.get('tilt'))
        sr = p.get('spin_rate')
        if deg is None or sr is None:
            continue
        rad = math.radians(deg)
        r = rmap(sr)
        px = cx + r * math.sin(rad)
        py = cy - r * math.cos(rad)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="{p.get("color","#888888")}" stroke="#333" stroke-width="1" opacity="0.85"/>')

    svg.append('</svg>')
    return ''.join(svg)


def _cartesian_axes(x_min, x_max, x_step, y_min, y_max, y_step, x_label, y_label, zero_bold=False):
    W = H = 560
    left, top = 50.6, 27.6
    plot_w = plot_h = 486.4
    right = left + plot_w
    bottom = top + plot_h

    svg = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto;">']
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff" stroke="none" stroke-width="1" opacity="1"/>')
    svg.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#999" stroke-width="1.2" opacity="1"/>')

    def xmap(v):
        return left + (v - x_min) / (x_max - x_min) * plot_w

    def ymap(v):
        return bottom - (v - y_min) / (y_max - y_min) * plot_h

    xv = x_min
    while xv <= x_max + 1e-9:
        px = xmap(xv)
        bold = zero_bold and abs(xv) < 1e-9
        stroke = '#666' if bold else '#cccccc'
        sw = '1.3' if bold else '0.7'
        svg.append(f'<line x1="{px}" y1="{top}" x2="{px}" y2="{bottom}" stroke="{stroke}" stroke-width="{sw}"/>')
        svg.append(_text(px, bottom + 14, f'{xv:g}', size=9))
        xv += x_step

    yv = y_min
    while yv <= y_max + 1e-9:
        py = ymap(yv)
        bold = zero_bold and abs(yv) < 1e-9
        stroke = '#666' if bold else '#cccccc'
        sw = '1.3' if bold else '0.7'
        svg.append(f'<line x1="{left}" y1="{py}" x2="{right}" y2="{py}" stroke="{stroke}" stroke-width="{sw}"/>')
        svg.append(_text(left - 8, py + 3, f'{yv:g}', size=9, anchor='end'))
        yv += y_step

    svg.append(_text((left + right) / 2, bottom + 26, x_label, size=11, fill='#444'))
    svg.append(f'<text x="14" y="{(top + bottom) / 2}" font-size="11" fill="#444" font-family="{FONT}" text-anchor="middle" transform="rotate(-90 14 {(top + bottom) / 2})">{y_label}</text>')

    return svg, xmap, ymap


def movement_chart(pitches):
    """pitches: dicts with 'horz_break','vert_break','color'. Fixed domain -30..30 in."""
    svg, xmap, ymap = _cartesian_axes(-30, 30, 10, -30, 30, 10, 'Horizontal Break (in.)', 'Induced Vert. Break (in.)', zero_bold=True)
    for p in pitches:
        hb, vb = p.get('horz_break'), p.get('vert_break')
        if hb is None or vb is None:
            continue
        px, py = xmap(hb), ymap(vb)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="16" fill="{p.get("color","#888888")}" stroke="#333" stroke-width="1" opacity="0.8"/>')
    svg.append('</svg>')
    return ''.join(svg)


def release_chart(pitches):
    """pitches: dicts with 'rel_side','rel_height','color'. Fixed domain side -3..3 ft, height 0..8 ft."""
    svg, xmap, ymap = _cartesian_axes(-3, 3, 1, 0, 8, 1, 'Release Side (ft)', 'Release Height (ft)', zero_bold=False)

    y0 = ymap(0)
    x_l = xmap(-2.2)
    x_r = xmap(2.2)
    x_c = xmap(0)
    y_top = y0 - (ymap(0) - ymap(0.43))
    svg.append(f'<path d="M {x_l} {y0} Q {x_c} {ymap(0.43)} {x_r} {y0}" fill="none" stroke="#b8935a" stroke-width="2"/>')
    rw = xmap(0.21) - xmap(-0.21)
    svg.append(f'<rect x="{x_c - rw/2}" y="{y0 - 3.5}" width="{rw}" height="7" fill="#e9e3d5" stroke="#999" stroke-width="1" opacity="1"/>')

    for p in pitches:
        rs, rh = p.get('rel_side'), p.get('rel_height')
        if rs is None or rh is None:
            continue
        px, py = xmap(rs), ymap(rh)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" fill="{p.get("color","#888888")}" stroke="#333" stroke-width="1" opacity="0.85"/>')
    svg.append('</svg>')
    return ''.join(svg)
