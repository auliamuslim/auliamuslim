#!/usr/bin/env python3
"""Render the profile README charts from data/profile.json.

Every chart is written twice (assets/<name>-light.svg and -dark.svg) so the
README can swap them with <picture> to follow the viewer's GitHub theme.
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
    months = DATA["monthly"]
    left, right, top, bottom = 64, 28, 104, 46
    height = 360
    ph = height - top - bottom
    pw = W - left - right
    totals = [m["human"] + m["ai"] for m in months]
    ymax = nice_max(max(totals))
    n = len(months)
    slot = pw / n
    bw = max(4, min(26, slot - 6))
    out = [heading(t, DATA["activity"]["title"], DATA["activity"]["subtitle"])]
    # legend
    lx = W - right
    items = [("s2", "AI pair (Claude Code)"), ("s1", "Hand-written")]
    for key, label in items:
        tw = 7.2 * len(label)
        lx -= tw
        out.append(f'<text x="{lx:.0f}" y="44" font-size="12.5" class="m">{escape(label)}</text>')
        lx -= 18
        out.append(f'<rect x="{lx:.0f}" y="34" width="12" height="12" rx="3" fill="{t[key]}"/>')
        lx -= 20
    # grid
    for i in range(5):
        v = ymax * i / 4
        y = top + ph - ph * i / 4
        out.append(f'<line x1="{left}" x2="{W-right}" y1="{y:.1f}" y2="{y:.1f}" stroke="{t["grid"]}"/>')
        out.append(f'<text x="{left-10}" y="{y+4:.1f}" font-size="11" class="m n" text-anchor="end">{fmt(int(v))}</text>')
    peak = max(range(n), key=lambda i: totals[i])
    for i, m in enumerate(months):
        cx = left + slot * i + slot / 2
        x = cx - bw / 2
        hh = ph * m["human"] / ymax
        ha = ph * m["ai"] / ymax
        base = top + ph
        delay = f"animation-delay:{i*0.03:.2f}s"
        if m["human"]:
            out.append(f'<rect class="col" style="{delay}" x="{x:.1f}" y="{base-hh:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="{min(4, bw/2):.1f}" fill="{t["s1"]}"/>')
        if m["ai"]:
            y2 = base - hh - ha
            gap = 2 if m["human"] else 0
            out.append(f'<rect class="col" style="{delay}" x="{x:.1f}" y="{y2:.1f}" width="{bw:.1f}" height="{max(0, ha-gap):.1f}" rx="{min(4, bw/2):.1f}" fill="{t["s2"]}"/>')
        label = m.get("label")
        if label:
            out.append(f'<text x="{cx:.1f}" y="{base+20}" font-size="11" class="m" text-anchor="middle">{escape(label)}</text>')
        if i == peak:
            out.append(f'<text x="{cx:.1f}" y="{base-hh-ha-8:.1f}" font-size="11.5" font-weight="700" class="n" text-anchor="middle">{fmt(totals[i])}</text>')
    out.append(f'<line x1="{left}" x2="{W-right}" y1="{top+ph}" y2="{top+ph}" stroke="{t["border"]}"/>')
    return svg(height, "\n".join(out), t, DATA["activity"]["title"])


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


def main():
    OUT.mkdir(exist_ok=True)
    charts = {
        "stats": stats_card,
        "activity": activity,
        "domains": lambda t: bars(t, DATA["domains"]),
        "languages": lambda t: bars(t, DATA["languages"]),
        "timeline": timeline,
    }
    for name, fn in charts.items():
        for mode, theme in THEMES.items():
            (OUT / f"{name}-{mode}.svg").write_text(fn(theme))
            print(f"wrote assets/{name}-{mode}.svg")


if __name__ == "__main__":
    main()
