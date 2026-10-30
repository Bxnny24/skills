#!/usr/bin/env python3
"""Build a clickable HTML report for an interaction-audit run.

Reads checklist.md and findings.md from a run folder, links the proof
screenshots and videos, and optionally compares every screenshot with the
same file in a previous run. Writes report.html into the run folder.

Usage:
    python3 build_report.py <run-dir> [--previous <previous-run-dir>] [--threshold 0.002]

Only the standard library is required. If Pillow is installed, changed
screenshots also get a pixel-difference ratio and a diff image.
"""

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

STATUSES = ["ok", "problem", "blocked", "skipped", "asked", "not reachable", "not applicable", "not supported"]
MEDIA_RE = re.compile(r"[\w./*\-\[\]]+\.(?:png|jpe?g|gif|webp|mp4|mov|webm)", re.IGNORECASE)
VIDEO_EXT = {".mp4", ".mov", ".webm"}


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def status_of(result):
    text = result.lower()
    for status in STATUSES:
        if text.startswith(status) or f"{status} " in text[:20]:
            return status
    return "open" if not text.strip() or text.strip() in {"…", "...", "-", "–"} else "other"


def parse_checklist(path):
    """Return a list of sections: {title, items: [{id, what, expected, result, status, proof}]}."""
    sections, current, header = [], None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "items": []}
            sections.append(current)
            header = None
            continue
        if not line.lstrip().startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = split_row(line)
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if current is None or not header or header[0] != "id":
            continue
        row = dict(zip(header, cells))
        result = row.get("result", "")
        current["items"].append({
            "id": row.get("id", ""),
            "what": row.get("interaction") or row.get("variation") or row.get("item") or "",
            "expected": row.get("expected") or row.get("screens checked") or "",
            "result": result,
            "status": status_of(result),
            "proof": row.get("proof", ""),
        })
    return [s for s in sections if s["items"]]


def expand_media(run_dir, proof):
    files = []
    for token in MEDIA_RE.findall(proof):
        if "*" in token:
            files.extend(sorted(p.relative_to(run_dir).as_posix() for p in run_dir.glob(token)))
        elif (run_dir / token).exists():
            files.append(token)
        else:
            files.append(token + "#missing")
    return files


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixel_diff(current, previous, out_path):
    """Return the changed-pixel ratio and write a diff image, or None without Pillow."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return None
    a = Image.open(current).convert("RGB")
    b = Image.open(previous).convert("RGB")
    if a.size != b.size:
        return 1.0
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 24 else 0)
    changed = sum(1 for v in diff.getdata() if v)
    ratio = changed / (a.size[0] * a.size[1])
    if changed:
        overlay = a.copy()
        overlay.paste((255, 0, 80), mask=diff)
        Image.blend(a, overlay, 0.6).save(out_path)
    return ratio


def compare(run_dir, prev_dir, rel, threshold):
    if prev_dir is None or rel.endswith("#missing") or Path(rel).suffix.lower() in VIDEO_EXT:
        return None
    current, previous = run_dir / rel, prev_dir / rel
    if not previous.exists():
        return {"state": "new"}
    if file_hash(current) == file_hash(previous):
        return {"state": "same", "previous": previous}
    diff_dir = run_dir / "report-diffs"
    diff_dir.mkdir(exist_ok=True)
    diff_path = diff_dir / (rel.replace("/", "__"))
    ratio = pixel_diff(current, previous, diff_path)
    if ratio is not None and ratio <= threshold:
        return {"state": "same", "previous": previous, "ratio": ratio}
    return {"state": "changed", "previous": previous, "ratio": ratio,
            "diff": diff_path if diff_path.exists() else None}


def rel_link(target, base):
    try:
        return Path(target).resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return Path(target).resolve().as_uri()


def inline_md(text):
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\b(F-\d+)\b", r'<a href="#\1">\1</a>', text)


def render_findings(path):
    if not path.exists():
        return "<p class=muted>No findings.md.</p>"
    out, in_list = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            title = line[3:].strip()
            anchor = re.match(r"(F-\d+)", title)
            out.append(f'<h3 id="{anchor.group(1) if anchor else ""}">{inline_md(title)}</h3>')
        elif re.match(r"\s*(-|\d+\.)\s", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            entry = re.sub(r"^\s*(-|\d+\.)\s", "", line)
            out.append(f"<li>{inline_md(entry)}</li>")
        elif line.startswith("# ") or not line.strip():
            continue
        else:
            out.append(f"<p>{inline_md(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def media_html(run_dir, rel, cmp):
    if rel.endswith("#missing"):
        return f'<div class="media missing">missing: {html.escape(rel[:-8])}</div>'
    src = html.escape(rel)
    if Path(rel).suffix.lower() in VIDEO_EXT:
        return f'<div class="media"><video src="{src}" controls preload="metadata"></video><span>{src}</span></div>'
    badge, extra = "", ""
    if cmp:
        label = {"new": "new", "same": "unchanged", "changed": "changed"}[cmp["state"]]
        if cmp.get("ratio") is not None:
            label += f" ({cmp['ratio'] * 100:.2f} %)"
        badge = f'<span class="cmp cmp-{cmp["state"]}">{label}</span>'
        if cmp["state"] == "changed":
            prev = html.escape(rel_link(cmp["previous"], run_dir))
            diff = f'<a href="{html.escape(rel_link(cmp["diff"], run_dir))}" target="_blank">diff</a>' if cmp.get("diff") else ""
            extra = (f'<div class="pair"><figure><figcaption>previous</figcaption><img src="{prev}" loading="lazy"></figure>'
                     f'<figure><figcaption>current</figcaption><img src="{src}" loading="lazy"></figure></div>'
                     f'<div class="blink" data-a="{prev}" data-b="{src}"><button type="button">Blink compare</button>{diff}</div>')
    if extra:
        return f'<div class="media">{badge}{extra}<span>{src}</span></div>'
    return f'<div class="media">{badge}<a href="{src}" target="_blank"><img src="{src}" loading="lazy"></a><span>{src}</span></div>'


CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--muted:#6e6e73;--card:#f5f5f7;--line:#d2d2d7;--ok:#1a7f37;--problem:#cf222e;--warn:#9a6700;--info:#0969da}
@media (prefers-color-scheme:dark){:root{--bg:#111;--fg:#f5f5f7;--muted:#a1a1a6;--card:#1c1c1e;--line:#3a3a3c;--ok:#3fb950;--problem:#ff6b6b;--warn:#d29922;--info:#58a6ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px}h1{font-size:24px;margin:0 0 4px}.muted{color:var(--muted)}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.stats button{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:4px 12px;cursor:pointer}
.stats button.active{outline:2px solid var(--info)}input[type=search]{width:100%;padding:8px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg)}
details{border:1px solid var(--line);border-radius:12px;margin:12px 0;background:var(--card)}summary{padding:10px 14px;cursor:pointer;font-weight:600}
.item{border-top:1px solid var(--line);padding:10px 14px}.item header{display:flex;gap:8px;flex-wrap:wrap;align-items:baseline}
.id{font-family:ui-monospace,monospace;font-size:13px}.st{border-radius:6px;padding:0 6px;font-size:12px;font-weight:600;color:#fff;background:var(--muted)}
.st-ok{background:var(--ok)}.st-problem{background:var(--problem)}.st-blocked,.st-skipped,.st-asked{background:var(--warn)}.st-open{background:var(--info)}
.media{display:inline-flex;flex-direction:column;gap:4px;margin:8px 8px 0 0;max-width:100%;font-size:12px;color:var(--muted);vertical-align:top}
.media img,.media video{max-height:320px;max-width:100%;border-radius:8px;border:1px solid var(--line)}.missing{color:var(--problem)}
.pair{display:flex;gap:8px;flex-wrap:wrap}.pair figure{margin:0}.pair figcaption{font-size:12px}
.cmp{font-size:12px;font-weight:600}.cmp-changed{color:var(--problem)}.cmp-new{color:var(--info)}.cmp-same{color:var(--ok)}
.blink button{margin-right:8px}.findings h3{margin-top:20px}code{font-family:ui-monospace,monospace;font-size:13px}
"""

JS = """
const items=[...document.querySelectorAll('.item')];let filter='all';
function apply(){const q=document.getElementById('q').value.toLowerCase();
items.forEach(i=>{const okS=filter==='all'||i.dataset.status===filter||(filter==='changed'&&i.dataset.changed==='1');
i.style.display=okS&&i.textContent.toLowerCase().includes(q)?'':'none'});
document.querySelectorAll('details.screen').forEach(d=>{d.style.display=[...d.querySelectorAll('.item')].some(i=>i.style.display!=='none')?'':'none'})}
document.querySelectorAll('.stats button').forEach(b=>b.onclick=()=>{filter=b.dataset.f;document.querySelectorAll('.stats button').forEach(x=>x.classList.toggle('active',x===b));apply()});
document.getElementById('q').oninput=apply;
document.querySelectorAll('.blink').forEach(w=>{const btn=w.querySelector('button');const img=w.previousElementSibling.querySelectorAll('img')[1];let t=null;
btn.onclick=()=>{if(t){clearInterval(t);t=null;img.src=w.dataset.b;btn.textContent='Blink compare';return}
let a=false;t=setInterval(()=>{a=!a;img.src=a?w.dataset.a:w.dataset.b},600);btn.textContent='Stop'}});
"""


def build(run_dir, prev_dir, threshold):
    checklist = run_dir / "checklist.md"
    if not checklist.exists():
        sys.exit(f"No checklist.md in {run_dir}")
    sections = parse_checklist(checklist)
    title = next((l[2:].strip() for l in checklist.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), run_dir.name)

    counts, changed_total, body = {}, 0, []
    for section in sections:
        rows = []
        for item in section["items"]:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
            media, changed = [], False
            for rel in expand_media(run_dir, item["proof"]):
                cmp = compare(run_dir, prev_dir, rel, threshold)
                changed |= bool(cmp and cmp["state"] == "changed")
                media.append(media_html(run_dir, rel, cmp))
            changed_total += changed
            rows.append(
                f'<div class="item" data-status="{item["status"]}" data-changed="{int(changed)}">'
                f'<header><span class="id">{html.escape(item["id"])}</span>'
                f'<span class="st st-{item["status"].replace(" ", "-")}">{html.escape(item["status"])}</span>'
                f'<strong>{inline_md(item["what"])}</strong></header>'
                f'<div class="muted">Expected: {inline_md(item["expected"])}</div>'
                f'<div>Result: {inline_md(item["result"])}</div>{"".join(media)}</div>')
        problems = sum(1 for i in section["items"] if i["status"] == "problem")
        open_attr = " open" if problems else ""
        body.append(f'<details class="screen"{open_attr}><summary>{inline_md(section["title"])} '
                    f'<span class="muted">· {len(section["items"])} items · {problems} problems</span></summary>{"".join(rows)}</details>')

    total = sum(counts.values())
    buttons = [f'<button data-f="all" class="active">all {total}</button>']
    buttons += [f'<button data-f="{s}">{html.escape(s)} {n}</button>' for s, n in sorted(counts.items(), key=lambda x: -x[1])]
    if prev_dir:
        buttons.append(f'<button data-f="changed">changed since previous run {changed_total}</button>')
    compared = f' · compared with <code>{html.escape(str(prev_dir))}</code>' if prev_dir else ""

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Interaction audit</title><style>{CSS}</style></head><body><main>
<h1>{html.escape(title)}</h1><div class="muted">{total} items{compared}</div>
<div class="stats">{''.join(buttons)}</div><input id="q" type="search" placeholder="Filter by text, ID or file">
{''.join(body)}
<section class="findings"><h2>Findings</h2>{render_findings(run_dir / 'findings.md')}</section>
</main><script>{JS}</script></body></html>"""
    out = run_dir / "report.html"
    out.write_text(page, encoding="utf-8")
    print(json.dumps({"report": str(out), "items": total, "counts": counts, "changed": changed_total if prev_dir else None}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--previous", type=Path, help="previous run folder to compare screenshots with")
    parser.add_argument("--threshold", type=float, default=0.002, help="changed-pixel ratio still counted as unchanged (Pillow only)")
    args = parser.parse_args()
    prev = args.previous.resolve() if args.previous else None
    if prev and not prev.is_dir():
        sys.exit(f"Previous run not found: {prev}")
    build(args.run_dir.resolve(), prev, args.threshold)


if __name__ == "__main__":
    main()
