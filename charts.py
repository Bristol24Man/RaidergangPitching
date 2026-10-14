from common import pitch_color

WIDTH = 260
HEIGHT = 340
ZY_BOTTOM = 191.60377358490564
ZY_TOP = 87.83018867924531
ZONE_H = ZY_BOTTOM - ZY_TOP  # 103.7736
ZONE_W = 83.71212121212123
ZX0 = WIDTH / 2 - ZONE_W / 2  # 88.14393939393939
ZX1 = WIDTH / 2 + ZONE_W / 2  # 171.85606060606062
SCALE_X = (ZONE_W / 2) / (8.5 / 12.0)   # px per ft, horizontal
SCALE_Y = ZONE_H / 2.0                   # px per ft, vertical (zone spans 1.5-3.5 ft)
H_TOP = 3.5
H_BOTTOM = 1.5


def xmap(side):
    return WIDTH / 2 + SCALE_X * side


def ymap(height):
    return ZY_BOTTOM + (H_BOTTOM - height) * SCALE_Y


def zone_diagram(pitches, shade='full', dot_radius=6.5):
    """pitches: list of dicts with 'side', 'height', 'color' keys (side/height may be None)."""
    svg = []
    svg.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="xMidYMid meet" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto;">'
    )
    svg.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="#ffffff" stroke="none" stroke-width="1" opacity="1"/>')

    if shade == 'full':
        sx, sy, sw, sh = ZX0, ZY_TOP, ZONE_W, ZONE_H
    elif shade == 'top':
        sx, sy, sw, sh = ZX0, ZY_TOP - 6, ZONE_W, (ZONE_H / 3) + 6
    elif shade == 'bottom':
        sx, sy, sw, sh = ZX0, ZY_TOP + 2 * ZONE_H / 3, ZONE_W, (ZONE_H / 3) + 6
    else:
        sx, sy, sw, sh = ZX0, ZY_TOP, ZONE_W, ZONE_H

    svg.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#bfe3c9" stroke="none" stroke-width="1" opacity="0.65"/>')
    svg.append(f'<rect x="{ZX0}" y="{ZY_TOP}" width="{ZONE_W}" height="{ZONE_H}" fill="none" stroke="#1b6b3a" stroke-width="1.6" opacity="1"/>')

    x1 = ZX0 + ZONE_W / 3
    x2 = ZX0 + 2 * ZONE_W / 3
    y1 = ZY_TOP + ZONE_H / 3
    y2 = ZY_TOP + 2 * ZONE_H / 3
    svg.append(f'<line x1="{x1}" y1="{ZY_TOP}" x2="{x1}" y2="{ZY_BOTTOM}" stroke="#1b6b3a" stroke-width="0.6"/>')
    svg.append(f'<line x1="{ZX0}" y1="{y1}" x2="{ZX1}" y2="{y1}" stroke="#1b6b3a" stroke-width="0.6"/>')
    svg.append(f'<line x1="{x2}" y1="{ZY_TOP}" x2="{x2}" y2="{ZY_BOTTOM}" stroke="#1b6b3a" stroke-width="0.6"/>')
    svg.append(f'<line x1="{ZX0}" y1="{y2}" x2="{ZX1}" y2="{y2}" stroke="#1b6b3a" stroke-width="0.6"/>')

    plate_cy = ymap(-0.05)
    pts = [
        (ZX0, plate_cy - 8),
        (ZX1, plate_cy - 8),
        (ZX1, plate_cy + 2),
        (WIDTH / 2, plate_cy + 14),
        (ZX0, plate_cy + 2),
    ]
    pts_str = ' '.join(f'{x},{y}' for x, y in pts)
    svg.append(f'<polygon points="{pts_str}" fill="#eeeeee" stroke="#999" stroke-width="1"/>')

    for p in pitches:
        side = p.get('side')
        height = p.get('height')
        if side is None or height is None:
            continue
        cx = round(xmap(side), 1)
        cy = round(ymap(height), 1)
        color = p.get('color') or '#888888'
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{dot_radius}" fill="{color}" stroke="#333" stroke-width="1" opacity="0.85"/>')

    svg.append('</svg>')
    return ''.join(svg)


def legend_col_html(pitch_types_in_order):
    items = []
    for pt in pitch_types_in_order:
        color = pitch_color(pt)
        items.append(f'<span class="leg-item"><span class="leg-dot" style="background:{color}"></span>{pt}</span>')
    return '<div class="legend-col">' + ''.join(items) + '</div>'
