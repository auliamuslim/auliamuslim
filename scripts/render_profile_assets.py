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


# ------------------------------------------------------------- category banner
def live_total(projects):
    return sum(p.get("live_count", p.get("count", 1)) for p in projects if p["live"])


def repo_total(projects):
    return sum(p.get("count", 1) for p in projects)


def category_banner(t, cat, idx, total):
    act = DATA["category_activity"][cat["key"]]
    months = DATA["category_months"]
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
    # sparkline of monthly commits
    series = act["monthly"]
    smax = max(series) or 1
    x0, x1, base, h = 520, W - 28, 100, 26
    slot = (x1 - x0) / len(series)
    bw = max(3, slot - 3)
    out.append(f'<line x1="{x0}" x2="{x1}" y1="{base+0.5}" y2="{base+0.5}" stroke="{t["grid"]}"/>')
    for i, v in enumerate(series):
        bh = max(1.5, h * v / smax) if v else 0
        if bh:
            out.append(f'<rect class="col" style="animation-delay:{i*0.03:.2f}s" x="{x0 + i*slot:.1f}" '
                       f'y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="1.5" fill="{t["s1"]}"/>')
    first, last = months[0], months[-1]
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    lab = lambda m: f"{abbr[int(m[5:7]) - 1]} '{m[2:4]}"
    out.append(f'<text x="{x0}" y="{base+15}" font-size="10" class="m">{lab(first)}</text>')
    out.append(f'<text x="{(x0+x1)/2:.0f}" y="{base+15}" font-size="10" class="m" text-anchor="middle">commits / month</text>')
    out.append(f'<text x="{x1}" y="{base+15}" font-size="10" class="m" text-anchor="end">{lab(last)}</text>')
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
def project_rows(projects):
    rows = ["| Project | Main function | What makes it notable |", "|---|---|---|"]
    for p in projects:
        n = p.get("count", 1)
        if p["live"]:
            lc = p.get("live_count", n)
            status = "🟢" if lc == n else f"🟢 <sub>{lc}/{n} live</sub>"
        else:
            status = "⚪"
        name = f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]
        count = f" ×{n}" if n > 1 else ""
        public = " 🔓" if p.get("public") else ""
        rows.append(f"| {status} **{name}**{count}{public}<br/><sub>{p['stack']} · {p['year']}</sub> "
                    f"| {p['function']} | {p['highlights']} |")
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


def inject_readme(section):
    path = ROOT / "README.md"
    text = path.read_text()
    start, end = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"
    a, b = text.index(start) + len(start), text.index(end)
    path.write_text(text[:a] + "\n" + section + "\n" + text[b:])
    print("updated README.md project catalogue")


def main():
    OUT.mkdir(exist_ok=True)
    catalog = json.loads((ROOT / "data" / "projects.json").read_text())
    charts = {
        "stats": stats_card,
        "activity": activity,
        "domains": lambda t: bars(t, DATA["domains"]),
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
    (OUT / "hero-terminal.svg").write_text(hero_terminal())
    print("wrote assets/hero-terminal.svg")
    inject_readme(readme_projects(catalog))


if __name__ == "__main__":
    main()
