#!/usr/bin/env python3
"""Render the profile README charts and project catalogue.

Reads data/profile.json (aggregated stats) and data/projects.json (the
anonymised project catalogue). Every chart is written twice
(assets/<name>-light.svg and -dark.svg) so the README can swap them with
<picture> to follow the viewer's GitHub theme, and the catalogue tables are
regenerated between the PROJECTS markers in README.md.
Only the Python standard library is used.

    python3 scripts/render_profile_assets.py
"""
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "profile.json").read_text())
OUT = ROOT / "assets"

THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d1d9e0", "text": "#1f2328", "muted": "#59636e",
        "grid": "#eaeef2", "track": "#f6f8fa", "s1": "#E11D2E", "s2": "#7C3AED",
        "soft": "#fde8ea",
    },
    "dark": {
        "bg": "#0d1117", "border": "#3d444d", "text": "#e6edf3", "muted": "#9198a1",
        "grid": "#21262d", "track": "#151b23", "s1": "#F2545B", "s2": "#9B7BF0",
        "soft": "#2a1215",
    },
}
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
W = 860


def fmt(n):
    return f"{n:,}"


def svg(height, body, t, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="{escape(title)}">\n'
        f"<title>{escape(title)}</title>\n"
        f"<style>text{{font-family:{SANS};fill:{t['text']}}}"
        f".m{{fill:{t['muted']}}}.n{{font-family:{MONO}}}"
        f"@keyframes up{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}"
        f"@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}"
        f"@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}"
        f".col{{transform-box:fill-box;transform-origin:bottom;animation:up .9s ease-out both}}"
        f".bar{{transform-box:fill-box;transform-origin:left;animation:grow .9s ease-out both}}"
        f".fd{{animation:fade 1s ease-out both}}"
        f"@media (prefers-reduced-motion:reduce){{.col,.bar,.fd{{animation:none}}}}</style>\n"
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{height-1}" rx="12" '
        f'fill="{t["bg"]}" stroke="{t["border"]}"/>\n{body}</svg>\n'
    )


def heading(t, title, subtitle):
    return (
        f'<text x="28" y="40" font-size="17" font-weight="700">{escape(title)}</text>\n'
        f'<text x="28" y="62" font-size="12.5" class="m">{escape(subtitle)}</text>\n'
    )


# --------------------------------------------------------------------------- stats
def stats_card(t):
    tiles = DATA["tiles"]
    n = len(tiles)
    pad, gap, top, h = 28, 12, 28, 104
    tw = (W - 2 * pad - gap * (n - 1)) / n
    out = []
    for i, tile in enumerate(tiles):
        x = pad + i * (tw + gap)
        accent = t["s2"] if tile.get("accent") == "ai" else t["s1"]
        out.append(
            f'<g class="fd" style="animation-delay:{i*0.08:.2f}s">'
            f'<rect x="{x:.1f}" y="{top}" width="{tw:.1f}" height="{h}" rx="10" '
            f'fill="{t["track"]}" stroke="{t["border"]}"/>'
            f'<rect x="{x:.1f}" y="{top+18}" width="3" height="{h-36}" rx="1.5" fill="{accent}"/>'
            f'<text x="{x+18:.1f}" y="{top+30}" font-size="11.5" font-weight="600" class="m" '
            f'letter-spacing=".4">{escape(tile["label"].upper())}</text>'
            f'<text x="{x+18:.1f}" y="{top+66}" font-size="30" font-weight="800" class="n">'
            f'{escape(tile["value"])}</text>'
            f'<text x="{x+18:.1f}" y="{top+88}" font-size="11" class="m">{escape(tile["note"])}</text>'
            f"</g>"
        )
    height = top + h + 28
    return svg(height, "\n".join(out), t, "Portfolio at a glance")


# ------------------------------------------------------------------------ activity
def nice_max(v):
    if v <= 0:
        return 10
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * mag >= v:
            return m * mag
    return 10 * mag


def activity(t):
    weeks = DATA["weekly"]
    left, right, top, bottom = 64, 28, 104, 46
    height = 372
    ph = height - top - bottom
    pw = W - left - right
    totals = [w["human"] + w["ai"] for w in weeks]
    ymax = nice_max(max(totals))
    n = len(weeks)
    slot = pw / n
    bw = max(3, min(22, slot - 4))
    base = top + ph
    out = [heading(t, DATA["activity"]["title"], DATA["activity"]["subtitle"])]
    lx = W - right
    for key, label in [("s2", "AI pair (Claude Code)"), ("s1", "Hand-written")]:
        lx -= 7.2 * len(label)
        out.append(f'<text x="{lx:.0f}" y="44" font-size="12.5" class="m">{escape(label)}</text>')
        lx -= 18
        out.append(f'<rect x="{lx:.0f}" y="34" width="12" height="12" rx="3" fill="{t[key]}"/>')
        lx -= 20
    for i in range(5):
        v = ymax * i / 4
        y = base - ph * i / 4
        out.append(f'<line x1="{left}" x2="{W-right}" y1="{y:.1f}" y2="{y:.1f}" stroke="{t["grid"]}"/>')
        out.append(f'<text x="{left-10}" y="{y+4:.1f}" font-size="11" class="m n" text-anchor="end">{fmt(int(v))}</text>')
    peak = max(range(n), key=lambda i: totals[i])
    for i, w in enumerate(weeks):
        cx = left + slot * i + slot / 2
        x = cx - bw / 2
        hh = ph * w["human"] / ymax
        ha = ph * w["ai"] / ymax
        delay = f"animation-delay:{i*0.015:.2f}s"
        r = min(3, bw / 2)
        if w["human"]:
            out.append(f'<rect class="col" style="{delay}" x="{x:.1f}" y="{base-hh:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="{r:.1f}" fill="{t["s1"]}"/>')
        if w["ai"]:
            gap = 2 if w["human"] else 0
            out.append(f'<rect class="col" style="{delay}" x="{x:.1f}" y="{base-hh-ha:.1f}" width="{bw:.1f}" height="{max(0, ha-gap):.1f}" rx="{r:.1f}" fill="{t["s2"]}"/>')
        if w.get("label"):
            out.append(f'<line x1="{x-2:.1f}" x2="{x-2:.1f}" y1="{base}" y2="{base+5}" stroke="{t["border"]}"/>')
            out.append(f'<text x="{x-2:.1f}" y="{base+19}" font-size="11" class="m">{escape(w["label"])}</text>')
        if i == peak:
            out.append(f'<text x="{cx:.1f}" y="{base-hh-ha-20:.1f}" font-size="10.5" class="m" text-anchor="middle">peak week</text>')
            out.append(f'<text x="{cx:.1f}" y="{base-hh-ha-7:.1f}" font-size="11.5" font-weight="700" class="n" text-anchor="middle">{fmt(totals[i])}</text>')
    full = totals[:-1] if len(totals) > 1 else totals
    avg = sum(full) / len(full)
    ya = base - ph * avg / ymax
    out.append(f'<line x1="{left}" x2="{W-right}" y1="{ya:.1f}" y2="{ya:.1f}" stroke="{t["text"]}" stroke-opacity=".45"/>')
    out.append(f'<rect x="{left+4}" y="{ya-17:.1f}" width="104" height="15" rx="3" fill="{t["bg"]}" fill-opacity=".85"/>')
    out.append(f'<text x="{left+8}" y="{ya-6:.1f}" font-size="11" font-weight="700" class="n">avg {fmt(round(avg))} / week</text>')
    out.append(f'<line x1="{left}" x2="{W-right}" y1="{base}" y2="{base}" stroke="{t["border"]}"/>')
    return svg(height, "\n".join(out), t, DATA["activity"]["title"])


# ----------------------------------------------------------------------- heatmap
HEAT = {
    "light": ["#ebedf0", "#fbd0d4", "#f48b95", "#e3303d", "#a3101d"],
    "dark": ["#161b22", "#4c1219", "#8f1d29", "#d4303d", "#ff6b76"],
}


def heatmap(t, mode):
    import datetime as dt
    days = DATA["daily"]
    start = dt.date.fromisoformat(DATA["window"]["start"])
    nz = sorted(v for v in days if v)
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)] if nz else [1, 2, 3]
    ramp = HEAT[mode]

    def level(v):
        if not v:
            return 0
        return 1 + sum(v > x for x in q)

    cell, gap = 12, 3
    x0, y0 = 66, 104
    out = [heading(t, "Daily commit calendar — Dec 2025 to now",
                   "Every repository, private included · darker = more commits that day")]
    for r, name in ((0, "Mon"), (2, "Wed"), (4, "Fri"), (6, "Sun")):
        out.append(f'<text x="{x0-10}" y="{y0 + r*(cell+gap) + 10}" font-size="10.5" class="m" text-anchor="end">{name}</text>')
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = None
    for i, v in enumerate(days):
        d = start + dt.timedelta(days=i)
        col, row = i // 7, d.weekday()
        x = x0 + col * (cell + gap)
        y = y0 + row * (cell + gap)
        if d.month != last_month and row == 0 or (i == 0):
            if d.month != last_month:
                out.append(f'<text x="{x}" y="{y0-10}" font-size="10.5" class="m">{abbr[d.month-1]}</text>')
                last_month = d.month
        out.append(f'<rect class="fd" style="animation-delay:{col*0.02:.2f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{ramp[level(v)]}"><title>{d.isoformat()}: {v} commits</title></rect>')
    gy = y0 + 7 * (cell + gap) + 16
    # legend
    lx = W - 28 - (5 * (cell + gap)) - 64
    out.append(f'<text x="{lx-8}" y="{gy+10}" font-size="10.5" class="m" text-anchor="end">Less</text>')
    for k in range(5):
        out.append(f'<rect x="{lx + k*(cell+gap)}" y="{gy}" width="{cell}" height="{cell}" rx="2.5" fill="{ramp[k]}"/>')
    out.append(f'<text x="{lx + 5*(cell+gap) + 4}" y="{gy+10}" font-size="10.5" class="m">More</text>')
    # KPI strip
    w = DATA["window"]
    bd = dt.date.fromisoformat(w["busiest_day"])
    kpis = [(fmt(w["commits"]), "commits in window"),
            (f'{w["active_days"]}/{w["days"]}', "active days"),
            (f'{w["longest_streak"]} days', "longest streak"),
            (fmt(w["busiest_count"]), f'busiest day · {bd.day} {abbr[bd.month-1]} {bd.year}'),
            (f'{round(w["commits"] / max(1, w["active_days"]))}', "avg per active day")]
    ky = gy + 40
    kw = (W - 56) / len(kpis)
    for k, (val, lab) in enumerate(kpis):
        x = 28 + k * kw
        out.append(f'<text x="{x}" y="{ky}" font-size="20" font-weight="800" class="n">{escape(val)}</text>')
        out.append(f'<text x="{x}" y="{ky+18}" font-size="11" class="m">{escape(lab)}</text>')
    return svg(ky + 40, "\n".join(out), t, "Daily commit calendar")


# --------------------------------------------------------------------- punchcard
def punchcard(t):
    grid = DATA["punchcard"]
    vmax = max(max(r) for r in grid) or 1
    x0, y0, cw, rh = 92, 108, (W - 92 - 40) / 24, 30
    out = [heading(t, "When I ship — commits by weekday and hour",
                   "Dec 2025 to now · local time (UTC+7) · circle area = number of commits")]
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for h in range(0, 24, 3):
        out.append(f'<text x="{x0 + h*cw + cw/2:.1f}" y="{y0-14}" font-size="10.5" class="m n" text-anchor="middle">{h:02d}:00</text>')
    best = max(((d, h) for d in range(7) for h in range(24)), key=lambda p: grid[p[0]][p[1]])
    for d in range(7):
        y = y0 + d * rh
        out.append(f'<text x="{x0-14}" y="{y+4}" font-size="11.5" class="m" text-anchor="end">{names[d]}</text>')
        out.append(f'<line x1="{x0}" x2="{W-40}" y1="{y}" y2="{y}" stroke="{t["grid"]}"/>')
        for h in range(24):
            v = grid[d][h]
            if not v:
                continue
            r = max(1.6, 12.5 * math.sqrt(v / vmax))
            cx = x0 + h * cw + cw / 2
            out.append(f'<circle class="fd" style="animation-delay:{(d*24+h)*0.004:.2f}s" cx="{cx:.1f}" cy="{y}" r="{r:.1f}" fill="{t["s1"]}"><title>{names[d]} {h:02d}:00 — {v} commits</title></circle>')
    totals_d = [sum(r) for r in grid]
    totals_h = [sum(grid[d][h] for d in range(7)) for h in range(24)]
    bd = max(range(7), key=lambda d: totals_d[d])
    bh = max(range(24), key=lambda h: totals_h[h])
    fy = y0 + 7 * rh + 6
    out.append(f'<text x="28" y="{fy}" font-size="12" class="m">Busiest slot <tspan font-weight="700" fill="{t["text"]}">{names[best[0]]} {best[1]:02d}:00</tspan> '
               f'({fmt(grid[best[0]][best[1]])}) · busiest day <tspan font-weight="700" fill="{t["text"]}">{names[bd]}</tspan> '
               f'· busiest hour <tspan font-weight="700" fill="{t["text"]}">{bh:02d}:00</tspan></text>')
    return svg(fy + 22, "\n".join(out), t, "When I ship")


# --------------------------------------------------------------- ranked projects
def rank_bars(t, spec):
    rows = spec["rows"]
    top, row_h, label_w = 96, 38, 300
    height = top + row_h * len(rows) + 14
    vmax = max(r["value"] for r in rows)
    x0 = 28 + label_w
    value_w = 8 + 7.4 * max(len(r["display"]) for r in rows)
    track_w = W - x0 - 28 - value_w
    out = [heading(t, spec["title"], spec["subtitle"])]
    for i, r in enumerate(rows):
        y = top + i * row_h
        w = max(4, track_w * r["value"] / vmax)
        out.append(f'<text x="28" y="{y+10}" font-size="11" font-weight="700" class="m n">{i+1:02d}</text>')
        out.append(f'<text x="52" y="{y+10}" font-size="13">{escape(r["label"])}</text>')
        out.append(f'<text x="52" y="{y+25}" font-size="10.5" class="m">{escape(r["tag"])}</text>')
        out.append(f'<rect x="{x0}" y="{y+2}" width="{track_w:.1f}" height="16" rx="4" fill="{t["track"]}"/>')
        out.append(f'<rect class="bar" style="animation-delay:{i*0.05:.2f}s" x="{x0}" y="{y+2}" width="{w:.1f}" height="16" rx="4" fill="{t["s1"]}"/>')
        out.append(f'<text x="{x0+track_w+12:.1f}" y="{y+15}" font-size="12.5" font-weight="700" class="n">{escape(r["display"])}</text>')
    return svg(height, "\n".join(out), t, spec["title"])


# ------------------------------------------------------------ merah-putih banner
FLAG_RED = "#E70011"


def wave_path(width, base, amp, period, height):
    pts = [f"M0 0 H{width} V{base}"]
    x = width
    while x > 0:
        pts.append(f"Q{x - period/4:.1f} {base + amp} {x - period/2:.1f} {base} T{x - period:.1f} {base}")
        x -= period
    pts.append("Z")
    return " ".join(pts)


def banner_header():
    h = DATA["banner"]
    height, base = 190, 128
    long = W * 2
    front = wave_path(long, base, 12, 215, height)
    back = wave_path(long, base + 10, 14, 287, height)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="{escape(h["name"])} — {escape(h["tagline"])}">
<title>{escape(h["name"])}</title>
<style>
text{{font-family:{SANS};fill:#ffffff}}
@keyframes flow{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}
@keyframes sheen{{from{{transform:translateX(-{W}px)}}to{{transform:translateX({W}px)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.f1{{animation:flow 9s linear infinite}}.f2{{animation:flow 14s linear infinite}}
.sh{{animation:sheen 6s ease-in-out infinite}}.t{{animation:rise .9s ease-out both}}
@media (prefers-reduced-motion:reduce){{.f1,.f2,.sh,.t{{animation:none}}}}
</style>
<defs>
<clipPath id="card"><rect width="{W}" height="{height}" rx="14"/></clipPath>
<linearGradient id="gl" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{height}" fill="#ffffff"/>
<path class="f2" d="{back}" fill="{FLAG_RED}" fill-opacity=".35"/>
<path class="f1" d="{front}" fill="{FLAG_RED}"/>
<rect class="sh" x="0" y="0" width="{W*0.45:.0f}" height="{base+20}" fill="url(#gl)"/>
<text class="t" x="{W/2}" y="70" font-size="40" font-weight="800" text-anchor="middle" letter-spacing=".3">{escape(h["name"])}</text>
<text class="t" style="animation-delay:.25s" x="{W/2}" y="102" font-size="16" font-weight="600" text-anchor="middle" fill-opacity=".95">{escape(h["tagline"])}</text>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{height-1}" rx="14" fill="none" stroke="#d1d9e0" stroke-opacity=".6"/>
</svg>
'''


def banner_footer():
    height, base, amp, period = 72, 34, 9, 215
    parts = [f"M0 {height} V{base}"]
    x = 0
    while x < W * 2:
        parts.append(f"Q{x + period/4:.1f} {base - amp} {x + period/2:.1f} {base} T{x + period:.1f} {base}")
        x += period
    parts.append(f"V{height} Z")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Merah putih footer wave">
<style>@keyframes flow{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}.f1{{animation:flow 10s linear infinite}}
@media (prefers-reduced-motion:reduce){{.f1{{animation:none}}}}</style>
<defs><clipPath id="c"><rect width="{W}" height="{height}" rx="12"/></clipPath></defs>
<g clip-path="url(#c)"><path class="f1" d="{" ".join(parts)}" fill="{FLAG_RED}"/></g>
</svg>
'''


# ---------------------------------------------------------------- impact wall
def impact_wall(t):
    items = DATA["impact"]
    cols, gap, top, ch = 4, 12, 92, 104
    cw = (W - 56 - gap * (cols - 1)) / cols
    rows = math.ceil(len(items) / cols)
    out = [heading(t, "Impact highlights", "Concrete numbers from shipped work · measured from the repositories")]
    for i, it in enumerate(items):
        x = 28 + (i % cols) * (cw + gap)
        y = top + (i // cols) * (ch + gap)
        out.append(f'<g class="fd" style="animation-delay:{i*0.07:.2f}s">'
                   f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="10" fill="{t["track"]}" stroke="{t["border"]}"/>'
                   f'<rect x="{x:.1f}" y="{y+16}" width="3" height="{ch-32}" rx="1.5" fill="{t["s1"]}"/>'
                   f'<text x="{x+18:.1f}" y="{y+42}" font-size="28" font-weight="800" class="n" fill="{t["s1"]}" style="fill:{t["s1"]}">{escape(it["value"])}</text>'
                   f'<text x="{x+18:.1f}" y="{y+64}" font-size="12.5" font-weight="700">{escape(it["label"])}</text>'
                   f'<text x="{x+18:.1f}" y="{y+82}" font-size="10.5" class="m">{escape(it["note"])}</text></g>')
    return svg(top + rows * (ch + gap) + 16, "\n".join(out), t, "Impact highlights")


# --------------------------------------------------------------- now shipping
def now_shipping(t):
    import datetime as dt
    ns = DATA["now_shipping"]
    rows = ns["rows"]
    start = dt.date.fromisoformat(ns["start"])
    end = dt.date.fromisoformat(ns["end"])
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    sub = (f'{fmt(ns["total"])} commits from {start.day} {abbr[start.month-1]} to {end.day} {abbr[end.month-1]} '
           f'{end.year} · the four busiest projects right now')
    out = [heading(t, "Now shipping — last 30 days", sub)]
    # pulsing live dot next to the title
    dot = 28 + 9.6 * len("Now shipping — last 30 days") + 14
    out.append(f'<circle cx="{dot:.0f}" cy="34" r="5" fill="{t["s1"]}"/>'
               f'<circle class="pulse" cx="{dot:.0f}" cy="34" r="5" fill="none" stroke="{t["s1"]}" stroke-width="2"/>')
    cols, gap, top, ch = len(rows), 12, 86, 150
    cw = (W - 56 - gap * (cols - 1)) / cols
    vmax = max(max(r["daily"]) for r in rows) or 1
    for i, r in enumerate(rows):
        x = 28 + i * (cw + gap)
        out.append(f'<rect x="{x:.1f}" y="{top}" width="{cw:.1f}" height="{ch}" rx="10" fill="{t["track"]}" stroke="{t["border"]}"/>')
        lines = wrap(r["name"], int((cw - 28) / 6.6))[:2]
        for j, line in enumerate(lines):
            out.append(f'<text x="{x+14:.1f}" y="{top+24+j*15}" font-size="12.5" font-weight="700">{escape(line)}</text>')
        out.append(f'<text x="{x+14:.1f}" y="{top+24+len(lines)*15}" font-size="10.5" class="m">{escape(r["tag"])}</text>')
        out.append(f'<text x="{x+14:.1f}" y="{top+90}" font-size="24" font-weight="800" class="n">{fmt(r["commits"])}</text>')
        out.append(f'<text x="{x+14 + 15.5*len(fmt(r["commits"])):.1f}" y="{top+90}" font-size="11" class="m">commits</text>')
        sx0, sx1, base, sh = x + 14, x + cw - 14, top + ch - 14, 30
        slot = (sx1 - sx0) / len(r["daily"])
        for k, v in enumerate(r["daily"]):
            if v:
                bh = max(1.5, sh * v / vmax)
                out.append(f'<rect class="col" style="animation-delay:{k*0.02:.2f}s" x="{sx0 + k*slot:.1f}" y="{base-bh:.1f}" '
                           f'width="{max(1.5, slot-1.2):.1f}" height="{bh:.1f}" rx="1" fill="{t["s1"]}"/>')
        out.append(f'<line x1="{sx0:.1f}" x2="{sx1:.1f}" y1="{base+0.5}" y2="{base+0.5}" stroke="{t["grid"]}"/>')
    doc = svg(top + ch + 22, "\n".join(out), t, "Now shipping")
    return doc.replace("@media (prefers-reduced-motion:reduce)",
                       "@keyframes pulse{0%{r:5;opacity:.9}100%{r:13;opacity:0}}.pulse{animation:pulse 1.6s ease-out infinite}"
                       "@media (prefers-reduced-motion:reduce){.pulse{animation:none}}"
                       "@media (prefers-reduced-motion:reduce)", 1)


# ----------------------------------------------------------- project universe
TREE = {
    "light": {"ramp": ["#fde2e4", "#fbbcc2", "#f48b95", "#e3303d", "#a3101d"], "ink": ["#1f2328"] * 3 + ["#ffffff"] * 2},
    "dark": {"ramp": ["#3a1418", "#5c1a22", "#8f1d29", "#d4303d", "#ff8a93"], "ink": ["#e6edf3"] * 4 + ["#0d1117"]},
}
BUCKETS = [10, 50, 200, 800]


def squarify(areas, x, y, w, h):
    rects, i = [], 0

    def worst(row, side):
        s = sum(row)
        return max(max(side * side * r / (s * s), (s * s) / (side * side * r)) for r in row)

    while i < len(areas):
        side = min(w, h)
        row = [areas[i]]
        i += 1
        while i < len(areas) and worst(row + [areas[i]], side) <= worst(row, side):
            row.append(areas[i])
            i += 1
        s = sum(row)
        if w >= h:
            cw = s / h if h else 0
            yy = y
            for a in row:
                rh = a / cw if cw else 0
                rects.append((x, yy, cw, rh))
                yy += rh
            x += cw
            w -= cw
        else:
            rh = s / w if w else 0
            xx = x
            for a in row:
                rw = a / rh if rh else 0
                rects.append((xx, y, rw, rh))
                xx += rw
            y += rh
            h -= rh
    return rects


def universe(t, mode, catalog):
    pal = TREE[mode]
    titles = {c["key"]: c["title"] for c in catalog["categories"]}
    groups = {}
    for u in DATA["universe"]:
        groups.setdefault(u["cat"], []).append(u)
    weight = lambda c: math.sqrt(max(c, 1)) + 3
    cats = sorted(groups, key=lambda k: -sum(weight(u["commits"]) for u in groups[k]))
    x0, y0, tw, th = 28, 92, W - 56, 600
    cat_w = [sum(weight(u["commits"]) for u in groups[k]) for k in cats]
    scale = tw * th / sum(cat_w)
    crects = squarify([v * scale for v in cat_w], x0, y0, tw, th)
    out = [heading(t, "Project universe — every project, grouped by domain",
                   "Tile area grows with commits (square-root scale) · darker red = more commits · 76 catalogue entries, 93 repos")]
    for k, (cx, cy, cw, chh) in zip(cats, crects):
        g = 3
        cx, cy, cw, chh = cx + g / 2, cy + g / 2, cw - g, chh - g
        total = sum(u["commits"] for u in groups[k])
        out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{chh:.1f}" rx="6" fill="{t["track"]}" stroke="{t["border"]}"/>')
        label = titles[k]
        maxc = int((cw - 12) / 6.3)
        head = label if len(label) <= maxc else label[:max(0, maxc - 1)] + "…"
        out.append(f'<text x="{cx+7:.1f}" y="{cy+14:.1f}" font-size="10.5" font-weight="700" class="m">{escape(head)}</text>')
        items = sorted(groups[k], key=lambda u: -u["commits"])
        iw = [weight(u["commits"]) for u in items]
        ix, iy, iww, ihh = cx + 3, cy + 20, cw - 6, chh - 23
        s2 = iww * ihh / sum(iw)
        for u, (rx, ry, rw, rh) in zip(items, squarify([v * s2 for v in iw], ix, iy, iww, ihh)):
            lvl = sum(u["commits"] >= b for b in BUCKETS)
            rx, ry, rw, rh = rx + 1, ry + 1, max(0, rw - 2), max(0, rh - 2)
            out.append(f'<rect class="fd" x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" rx="3" fill="{pal["ramp"][lvl]}">'
                       f'<title>{escape(u["name"])}: {fmt(u["commits"])} commits</title></rect>')
            if rw >= 56 and rh >= 22:
                n = max(4, int((rw - 10) / 5.7))
                lines = wrap(u["name"], n)
                room = 1 if rh < 44 else 2 if rh < 70 else 3
                shown = lines[:room]
                if len(lines) > room:
                    last = shown[-1]
                    shown[-1] = (last if len(last) < n else last[:n - 1]) + "…"
                ink = pal["ink"][lvl]
                for j, line in enumerate(shown):
                    out.append(f'<text x="{rx+5:.1f}" y="{ry+14+j*12:.1f}" font-size="10" font-weight="600" style="fill:{ink}">{escape(line[:n])}</text>')
                cy2 = ry + 14 + len(shown) * 12 + 2
                if cy2 + 4 <= ry + rh:
                    out.append(f'<text x="{rx+5:.1f}" y="{cy2:.1f}" font-size="10" class="n" style="fill:{ink};opacity:.85">{fmt(u["commits"])}</text>')
    ly = y0 + th + 22
    labels = ["1–9", "10–49", "50–199", "200–799", "800+ commits"]
    lx = 28
    for i, lab in enumerate(labels):
        out.append(f'<rect x="{lx}" y="{ly-10}" width="12" height="12" rx="2.5" fill="{pal["ramp"][i]}"/>')
        out.append(f'<text x="{lx+17}" y="{ly}" font-size="10.5" class="m">{lab}</text>')
        lx += 17 + 7 * len(lab) + 16
    return svg(ly + 16, "\n".join(out), t, "Project universe")


# -------------------------------------------------------------------------- bars
def bars(t, spec):
    rows = spec["rows"]
    top, row_h, label_w = 92, 30, 240
    height = top + row_h * len(rows) + 22
    vmax = max(r["value"] for r in rows)
    x0 = 28 + label_w
    value_w = 8 + 7.4 * max(len(r.get("display", str(r["value"]))) for r in rows)
    track_w = W - x0 - 28 - value_w
    out = [heading(t, spec["title"], spec["subtitle"])]
    for i, r in enumerate(rows):
        y = top + i * row_h
        w = max(4, track_w * r["value"] / vmax)
        out.append(f'<text x="28" y="{y+15}" font-size="13">{escape(r["label"])}</text>')
        out.append(f'<rect x="{x0}" y="{y+3}" width="{track_w}" height="16" rx="4" fill="{t["track"]}"/>')
        out.append(f'<rect class="bar" style="animation-delay:{i*0.05:.2f}s" x="{x0}" y="{y+3}" width="{w:.1f}" height="16" rx="4" fill="{t["s1"]}"/>')
        out.append(f'<text x="{x0+track_w+12}" y="{y+16}" font-size="12.5" font-weight="700" class="n">{escape(r.get("display", str(r["value"])))}</text>')
    return svg(height, "\n".join(out), t, spec["title"])


# ---------------------------------------------------------------------- timeline
def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def timeline(t):
    items = DATA["timeline"]
    n = len(items)
    left, right = 125, 125
    axis_y = 112
    span = W - left - right
    out = [heading(t, "The journey", "From research-lab prototypes to production platforms")]
    out.append(f'<line x1="{left-30}" x2="{W-right+30}" y1="{axis_y}" y2="{axis_y}" stroke="{t["border"]}" stroke-width="2"/>')
    col_w = span / (n - 1) if n > 1 else span
    chars = max(16, int(min(col_w, 2 * left - 20) / 6.2))
    max_lines = 0
    for i, it in enumerate(items):
        x = left + col_w * i if n > 1 else W / 2
        color = t["s2"] if it.get("accent") == "ai" else t["s1"]
        out.append(f'<g class="fd" style="animation-delay:{i*0.12:.2f}s">')
        out.append(f'<circle cx="{x:.1f}" cy="{axis_y}" r="9" fill="{t["bg"]}" stroke="{color}" stroke-width="2"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{axis_y}" r="4" fill="{color}"/>')
        out.append(f'<text x="{x:.1f}" y="{axis_y-22}" font-size="15" font-weight="800" text-anchor="middle" class="n">{escape(it["year"])}</text>')
        out.append(f'<text x="{x:.1f}" y="{axis_y+34}" font-size="12.5" font-weight="700" text-anchor="middle">{escape(it["title"])}</text>')
        lines = wrap(it["text"], chars)
        max_lines = max(max_lines, len(lines))
        for j, line in enumerate(lines):
            out.append(f'<text x="{x:.1f}" y="{axis_y+54+j*16}" font-size="11.5" class="m" text-anchor="middle">{escape(line)}</text>')
        out.append("</g>")
    height = axis_y + 54 + max_lines * 16 + 14
    return svg(height, "\n".join(out), t, "The journey")


# ------------------------------------------------------------- category banner
def live_total(projects):
    return sum(p.get("live_count", p.get("count", 1)) for p in projects if p["live"])


def repo_total(projects):
    return sum(p.get("count", 1) for p in projects)


def category_banner(t, cat, idx, total):
    act = DATA["category_activity"][cat["key"]]
    height = 124
    out = [
        f'<rect x="1" y="18" width="4" height="{height-36}" rx="2" fill="{t["s1"]}"/>',
        f'<text x="28" y="36" font-size="11" font-weight="700" class="m n" letter-spacing="1">'
        f'CATEGORY {idx:02d} / {total:02d}</text>',
        f'<text x="28" y="64" font-size="20" font-weight="800">{escape(cat["title"])}</text>',
    ]
    for j, line in enumerate(wrap(cat["tagline"], 62)[:2]):
        out.append(f'<text x="28" y="{88 + j*17}" font-size="12.5" class="m">{escape(line)}</text>')
    # stats
    stats = [("REPOS", fmt(repo_total(cat["projects"]))), ("COMMITS", fmt(act["commits"])),
             ("LIVE", fmt(live_total(cat["projects"])))]
    sx = 520
    for k, (label, value) in enumerate(stats):
        x = sx + k * 104
        out.append(f'<text x="{x}" y="36" font-size="10.5" font-weight="700" class="m" letter-spacing=".6">{label}</text>')
        out.append(f'<text x="{x}" y="60" font-size="21" font-weight="800" class="n">{value}</text>')
    # sparkline of weekly commits in the activity window
    series = DATA["category_weekly"][cat["key"]]
    weeks = DATA["category_weeks"]
    smax = max(series) or 1
    x0, x1, base, h = 520, W - 28, 100, 26
    slot = (x1 - x0) / len(series)
    bw = max(2.5, slot - 2)
    out.append(f'<line x1="{x0}" x2="{x1}" y1="{base+0.5}" y2="{base+0.5}" stroke="{t["grid"]}"/>')
    for i, v in enumerate(series):
        bh = max(1.5, h * v / smax) if v else 0
        if bh:
            out.append(f'<rect class="col" style="animation-delay:{i*0.015:.2f}s" x="{x0 + i*slot:.1f}" '
                       f'y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="1" fill="{t["s1"]}"/>')
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    lab = lambda m: f"{abbr[int(m[5:7]) - 1]} '{m[2:4]}"
    out.append(f'<text x="{x0}" y="{base+15}" font-size="10" class="m">{lab(weeks[0])}</text>')
    out.append(f'<text x="{(x0+x1)/2:.0f}" y="{base+15}" font-size="10" class="m" text-anchor="middle">commits / week</text>')
    out.append(f'<text x="{x1}" y="{base+15}" font-size="10" class="m" text-anchor="end">now</text>')
    return svg(height, "\n".join(out), t, cat["title"])


# ------------------------------------------------------------------ hero terminal
def hero_terminal():
    h = DATA["hero"]
    red, violet, fg, mute = "#F2545B", "#B49CF6", "#e6edf3", "#9198a1"
    lines = []
    for cmd, output in h["lines"]:
        lines.append(("cmd", cmd))
        lines.append(("out", output))
    top, step = 66, 25
    height = top + step * len(lines) + 14
    body = [
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{height-1}" rx="12" fill="#0d1117" stroke="#30363d"/>',
        f'<path d="M0.5 36 H{W-0.5}" stroke="#30363d"/>',
        '<circle cx="24" cy="18" r="6" fill="#ff5f57"/><circle cx="44" cy="18" r="6" fill="#febc2e"/>'
        '<circle cx="64" cy="18" r="6" fill="#28c840"/>',
        f'<text x="{W/2}" y="22" font-size="12" fill="{mute}" text-anchor="middle" class="n">{escape(h["title"])}</text>',
    ]
    delay = 0.3
    for i, (kind, text) in enumerate(lines):
        y = top + i * step
        if kind == "cmd":
            body.append(f'<text x="28" y="{y}" font-size="15" class="n type" style="animation-delay:{delay:.2f}s">'
                        f'<tspan fill="{red}" font-weight="700">$ </tspan><tspan fill="{fg}">{escape(text)}</tspan></text>')
            delay += 0.9
        else:
            parts = text.split("**")
            bold = ' font-weight="700"'
            spans = "".join(
                f'<tspan fill="{fg if k % 2 else mute}"{bold if k % 2 else ""}>{escape(c)}</tspan>'
                for k, c in enumerate(parts))
            body.append(f'<text x="28" y="{y}" font-size="14" class="n show" style="animation-delay:{delay:.2f}s">{spans}</text>')
            delay += 0.45
    cy = top + (len(lines) - 1) * step
    body.append(f'<rect class="cur" x="{28 + 8.6 * (len(lines[-1][1].replace("**", "")) + 1):.0f}" y="{cy-13}" '
                f'width="9" height="17" fill="{violet}" style="animation-delay:{delay:.2f}s"/>')
    style = (
        f"<style>text{{font-family:{MONO}}}.n{{font-family:{MONO}}}"
        "@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}"
        "@keyframes show{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".type{animation:type .8s steps(28,end) both}.show{animation:show .4s ease-out both}"
        ".cur{animation:blink 1s step-end infinite}"
        "@media (prefers-reduced-motion:reduce){.type,.show,.cur{animation:none}}</style>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
        f'role="img" aria-label="{escape(h["alt"])}">\n<title>{escape(h["alt"])}</title>\n{style}\n'
        + "\n".join(body) + "\n</svg>\n"
    )


# ------------------------------------------------------------- README section
def chips(stack):
    # non-breaking spaces keep each tag on one line ("PHP&nbsp;8.1")
    return " ".join(f"<code>{escape(part.strip()).replace(' ', '&nbsp;')}</code>" for part in stack.split("·"))


def status_label(p):
    n = p.get("count", 1)
    if not p["live"]:
        return "⚪ <sub>delivered</sub>"
    lc = p.get("live_count", n)
    return "🟢 <sub>live</sub>" if lc == n else f"🟢 <sub>{lc}/{n} live</sub>"


def project_rows(projects):
    """Full-width HTML table: GitHub sizes tables to their content, so the
    long description cells stretch every table edge to edge."""
    rows = ['<table>', '<thead><tr>',
            '<th align="left" width="30%">Project</th>',
            '<th align="left" width="32%">Main function</th>',
            '<th align="left" width="38%">What makes it notable</th>',
            '</tr></thead>', '<tbody>']
    for p in projects:
        n = p.get("count", 1)
        name = f'<a href="{p["url"]}">{escape(p["name"])}</a>' if p.get("url") else escape(p["name"])
        count = f" <sub>×{n}</sub>" if n > 1 else ""
        public = " 🔓" if p.get("public") else ""
        rows.append(
            f'<tr><td valign="top"><b>{name}</b>{count}{public}<br/>{status_label(p)} <sub>· since {p["year"]}</sub><br/>{chips(p["stack"])}</td>'
            f'<td valign="top">{escape(p["function"])}</td>'
            f'<td valign="top">{escape(p["highlights"])}</td></tr>')
    rows += ["</tbody>", "</table>"]
    return "\n".join(rows)


def picture(name, alt):
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg"/>\n'
            f'  <img width="100%" alt="{escape(alt, {chr(34): "&quot;"})}" src="assets/{name}-light.svg"/>\n</picture>')


def readme_projects(catalog):
    cats = catalog["categories"]
    out = []
    total_repos = sum(repo_total(c["projects"]) for c in cats)
    out.append(f"<sub>{total_repos} project repositories in {len(cats)} categories. Each row leads with the "
               "project's <b>main function</b>, then what makes it notable. 🟢 in production · "
               "⚪ delivered, internal or staging · ×N groups sibling repositories.</sub>\n")
    out.append(pic("universe", "Project universe treemap: every catalogued project grouped by domain, tile area "
                   "growing with commits. Largest: " + "; ".join(
                       f'{u["name"]} {fmt(u["commits"])}' for u in sorted(DATA["universe"], key=lambda u: -u["commits"])[:8])))
    out.append("<table>")
    for i in range(0, len(cats), 2):
        out.append("<tr>")
        for c in cats[i:i + 2]:
            act = DATA["category_activity"][c["key"]]
            out.append(
                f'<td width="50%" valign="top"><a href="#cat-{c["key"]}"><b>{c["emoji"]} {escape(c["title"])}</b></a><br/>'
                f'<sub>{repo_total(c["projects"])} repos · {fmt(act["commits"])} commits · '
                f'{live_total(c["projects"])} live</sub><br/>{escape(c["tagline"])}</td>')
        out.append("</tr>")
    out.append("</table>\n")
    for c in cats:
        act = DATA["category_activity"][c["key"]]
        alt = (f'{c["title"]}: {repo_total(c["projects"])} repositories, {fmt(act["commits"])} commits, '
               f'{live_total(c["projects"])} live. {c["tagline"]}')
        out.append(f'<a id="cat-{c["key"]}"></a>\n')
        out.append(picture(f"cat-{c['key']}", alt) + "\n")
        out.append(project_rows(c["projects"]) + "\n")
        out.append('<div align="right"><sub><a href="#projects">↑ back to categories</a></sub></div>\n')
    collab = catalog["collaborations"]
    out.append('<a id="cat-collab"></a>\n')
    out.append(f"**🤝 Collaborations & open source** <sub>— {len(collab)} repos</sub>\n")
    out.append(project_rows(collab))
    return "\n".join(out)


def readme_stack_table():
    spec = DATA["stack_commits"]
    total = sum(r["value"] for r in spec["rows"])
    repos = sum(r["repos"] for r in spec["rows"])
    rows = ['<table>', '<thead><tr>',
            '<th align="left" width="26%">Main stack</th>',
            '<th align="right" width="8%">Repos</th>',
            '<th align="right" width="11%">Commits</th>',
            '<th align="right" width="9%">Share</th>',
            '<th align="left" width="46%">Typical projects</th>',
            '</tr></thead>', '<tbody>']
    for r in spec["rows"]:
        rows.append(f'<tr><td><b>{escape(r["label"])}</b></td><td align="right">{r["repos"]}</td>'
                    f'<td align="right"><code>{fmt(r["value"])}</code></td>'
                    f'<td align="right">{100 * r["value"] / total:.1f}%</td><td>{escape(r["examples"])}</td></tr>')
    rows.append(f'<tr><td><b>Total</b></td><td align="right"><b>{repos}</b></td>'
                f'<td align="right"><b><code>{fmt(total)}</code></b></td><td align="right"><b>100%</b></td>'
                f'<td><sub>All 93 project repos</sub></td></tr>')
    rows += ["</tbody>", "</table>"]
    return "\n".join(rows)


def readme_tldr(catalog):
    t, w, pr = DATA["totals"], DATA["window"], DATA["profile"]
    cats = catalog["categories"]
    stack = DATA["stack_commits"]["rows"]
    return (
        f'> **TL;DR** — {pr["name"]} is a {pr["role"].lower()} at {pr["company"]} ({pr["location"]}) who builds '
        f'business platforms end to end: government and enterprise ERP/CRM, university systems, SaaS, logistics, '
        f'e-commerce and AI automation. Across **{len(cats)} domains** there are **108 repositories** '
        f'(93 project repos, 65 in production) and **{fmt(t["commits"])} commits**, '
        f'{t["ai_share"]}% of them pair-programmed with Claude Code. Main stacks by commits: '
        + ", ".join(f'{r["label"]} ({fmt(r["value"])})' for r in stack[:5])
        + f'. Since Dec 2025: {fmt(w["commits"])} commits on {w["active_days"]} active days.'
    )


def readme_ai_profile(catalog):
    t, w, pr = DATA["totals"], DATA["window"], DATA["profile"]
    q = lambda v: '"' + str(v).replace('"', "'") + '"'
    out = ["<details>", "<summary><b>🤖 Machine-readable profile</b> — structured summary for AI assistants, "
           "recruiters and tools</summary>", "", "```yaml",
           f"name: {q(pr['name'])}", f"github: {pr['github']}", f"role: {q(pr['role'])}",
           f"company: {q(pr['company'])}", f"website: {pr['website']}", f"location: {pr['location']}",
           f"linkedin: {pr['linkedin']}", f"email: {pr['email']}", f"on_github_since: {pr['on_github_since']}",
           f"open_to: {pr['open_to']}", f"updated: {DATA['generated']}", "stats:",
           "  repositories: 108", "  project_repos: 93", "  live_systems: 65",
           f"  commits_total: {t['commits']}", f"  commits_ai_paired_pct: {t['ai_share']}",
           f"  repos_with_ai_pairing: {t['ai_repos']}", f"  active_days: {t['active_days']}",
           f"  window_since: {w['start']}", f"  window_commits: {w['commits']}",
           f"  window_active_days: {w['active_days']}", f"  window_longest_streak_days: {w['longest_streak']}",
           "focus:"]
    out += [f"  - {q(f)}" for f in pr["focus"]]
    out.append("domains:")
    for c in catalog["categories"]:
        act = DATA["category_activity"][c["key"]]
        out += [f"  - name: {q(c['title'])}", f"    repos: {repo_total(c['projects'])}",
                f"    live: {live_total(c['projects'])}", f"    commits: {act['commits']}",
                f"    purpose: {q(c['tagline'])}"]
    out.append("main_stacks:")
    for r in DATA["stack_commits"]["rows"]:
        out.append(f"  - {{stack: {q(r['label'])}, repos: {r['repos']}, commits: {r['value']}}}")
    out.append("ai_in_products:")
    out += [f"  - {q(a)}" for a in pr["ai_in_products"]]
    out.append("top_projects_since_dec_2025:")
    out += [f"  - {{name: {q(r['label'])}, domain: {q(r['tag'])}, commits: {r['value']}}}"
            for r in DATA["top_projects"]["rows"]]
    out += ["note: \"Client names are withheld; most work is private client work under NDA.\"", "```", "", "</details>"]
    return "\n".join(out)


def alt_attr(text):
    return escape(text, {'"': "&quot;"})


def pic(name, alt):
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg"/>\n'
            f'  <img width="100%" alt="{alt_attr(alt)}" src="assets/{name}-light.svg"/>\n</picture>\n')


def readme_glance():
    t, ns = DATA["totals"], DATA["now_shipping"]
    impact = "; ".join(f'{i["value"]} {i["label"]} ({i["note"]})' for i in DATA["impact"])
    return "\n".join([
        pic("stats", f'108 repositories, {fmt(t["commits"])} commits, {t["active_days"]} active days, '
                     f'65 systems in production, {t["ai_share"]}% of commits paired with Claude Code'),
        pic("now-shipping", f'Now shipping, last 30 days: {fmt(ns["total"])} commits. Busiest: '
            + "; ".join(f'{r["name"]} {fmt(r["commits"])}' for r in ns["rows"])),
        pic("impact", "Impact highlights: " + impact),
        pic("timeline", "Journey: 2013 joined GitHub, 2016 research lab, 2025 client platforms, "
                        "2026 AI-native development and ecosystems at scale"),
    ])


def readme_activity():
    import datetime as dt
    w = DATA["window"]
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    end = dt.date.fromisoformat(w["end"])
    bd = dt.date.fromisoformat(w["busiest_day"])
    peak = max(DATA["weekly"], key=lambda x: x["human"] + x["ai"])
    pkd = dt.date.fromisoformat(peak["week"])
    grid = DATA["punchcard"]
    best = max(((d, h) for d in range(7) for h in range(24)), key=lambda q: grid[q[0]][q[1]])
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return "\n".join([
        "<sub>Every chart counts all repositories I own or contribute to, private ones included: my own commits plus "
        "Claude Code sessions in my repositories. Upstream and other contributors are excluded. "
        f"Window: <b>1 Dec 2025 → {end.day} {abbr[end.month-1]} {end.year}</b>, times in WIB (UTC+7).</sub>\n",
        pic("activity", f'Weekly commits since December 2025, hand-written vs Claude Code: {fmt(w["commits"])} commits, '
                        f'peak week of {fmt(peak["human"] + peak["ai"])} starting {pkd.day} {abbr[pkd.month-1]} {pkd.year}'),
        pic("heatmap", f'Daily commit calendar since December 2025: {fmt(w["commits"])} commits on {w["active_days"]} of '
                       f'{w["days"]} days, longest streak {w["longest_streak"]} days, busiest day {bd.day} '
                       f'{abbr[bd.month-1]} {bd.year} with {w["busiest_count"]} commits'),
        pic("punchcard", f'Commits by weekday and hour in WIB since December 2025; busiest slot '
                         f'{days[best[0]]} {best[1]:02d}:00'),
        pic("top-projects", "Most active projects since December 2025: "
            + "; ".join(f'{r["label"]} {fmt(r["value"])}' for r in DATA["top_projects"]["rows"])),
        pic("domains", "All-time commits per domain: "
            + "; ".join(f'{r["label"]} {fmt(r["value"])}' for r in DATA["domains"]["rows"])),
    ])


def sync_numbers():
    """Keep the few hand-written figures in README.md in step with the data."""
    import re
    path = ROOT / "README.md"
    text = path.read_text()
    t = DATA["totals"]
    stack_total = sum(r["value"] for r in DATA["stack_commits"]["rows"])
    subs = [
        (r"badge/Commits-[\d.]+k-", f'badge/Commits-{t["commits"] / 1000:.1f}k-'),
        (r'alt="[\d.]+k commits"', f'alt="{t["commits"] / 1000:.1f}k commits"'),
        (r"Terminal intro: 108 repos, 93 projects, [\d,]+ commits, 65 live systems, \d+% AI-paired",
         f'Terminal intro: 108 repos, 93 projects, {fmt(t["commits"])} commits, 65 live systems, {t["ai_share"]}% AI-paired'),
        (r"\d+% of [\d,]+ commits paired with Claude Code across \d+ repositories",
         f'{t["ai_share"]}% of {fmt(t["commits"])} commits paired with Claude Code across {t["ai_repos"]} repositories'),
        (r"add up to the [\d,]+ commits in the 93 project repos\. The remaining \d+ of the [\d,]+ total",
         f'add up to the {fmt(stack_total)} commits in the 93 project repos. The remaining '
         f'{t["commits"] - stack_total} of the {fmt(t["commits"])} total'),
        (r'alt="Commits per main stack: [^"]*"',
         'alt="Commits per main stack: ' + alt_attr("; ".join(
             f'{r["label"]} {fmt(r["value"])} across {r["repos"]} repo{"s" if r["repos"] != 1 else ""}'
             for r in DATA["stack_commits"]["rows"])) + '"'),
    ]
    for pattern, repl in subs:
        text, n = re.subn(pattern, lambda m, r=repl: r, text)
        if not n:
            print(f"warning: no match for {pattern[:40]}")
    path.write_text(text)


def inject_readme(marker, section):
    path = ROOT / "README.md"
    text = path.read_text()
    start, end = f"<!-- {marker}:START -->", f"<!-- {marker}:END -->"
    a, b = text.index(start) + len(start), text.index(end)
    path.write_text(text[:a] + "\n" + section + "\n" + text[b:])
    print(f"updated README.md {marker.lower()} section")


def main():
    OUT.mkdir(exist_ok=True)
    catalog = json.loads((ROOT / "data" / "projects.json").read_text())
    charts = {
        "stats": stats_card,
        "activity": activity,
        "punchcard": punchcard,
        "top-projects": lambda t: rank_bars(t, DATA["top_projects"]),
        "domains": lambda t: bars(t, DATA["domains"]),
        "stack-commits": lambda t: bars(t, DATA["stack_commits"]),
        "languages": lambda t: bars(t, DATA["languages"]),
        "timeline": timeline,
    }
    total = len(catalog["categories"])
    for i, cat in enumerate(catalog["categories"], 1):
        charts[f"cat-{cat['key']}"] = lambda t, c=cat, i=i: category_banner(t, c, i, total)
    for name, fn in charts.items():
        for mode, theme in THEMES.items():
            (OUT / f"{name}-{mode}.svg").write_text(fn(theme))
            print(f"wrote assets/{name}-{mode}.svg")
    charts["impact"] = impact_wall
    charts["now-shipping"] = now_shipping
    for name in ("impact", "now-shipping"):
        for mode, theme in THEMES.items():
            (OUT / f"{name}-{mode}.svg").write_text(charts[name](theme))
    for mode, theme in THEMES.items():
        (OUT / f"heatmap-{mode}.svg").write_text(heatmap(theme, mode))
        (OUT / f"universe-{mode}.svg").write_text(universe(theme, mode, catalog))
        print(f"wrote assets/heatmap-{mode}.svg, universe-{mode}.svg")
    (OUT / "hero-terminal.svg").write_text(hero_terminal())
    (OUT / "banner-header.svg").write_text(banner_header())
    (OUT / "banner-footer.svg").write_text(banner_footer())
    print("wrote assets/hero-terminal.svg, banner-header.svg, banner-footer.svg")
    inject_readme("TLDR", readme_tldr(catalog))
    inject_readme("GLANCE", readme_glance())
    inject_readme("ACTIVITY", readme_activity())
    inject_readme("PROJECTS", readme_projects(catalog))
    inject_readme("STACK", readme_stack_table())
    inject_readme("AI-PROFILE", readme_ai_profile(catalog))
    sync_numbers()


if __name__ == "__main__":
    main()
