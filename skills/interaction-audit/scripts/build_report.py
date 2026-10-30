#!/usr/bin/env python3
"""Build the result files for an interaction-audit run.

Reads checklist.md and findings.md from a run folder, links the proof
screenshots and videos, and optionally compares every screenshot with the
same file in a previous run. Writes into the run folder:

- report.html: assets/report-template.html filled with the run's data; proof
               images are embedded, so the file shows them anywhere (also in
               viewers that copy the page without its folder)
- summary.md:  the same result tables as Markdown, with image previews

Usage:
    python3 build_report.py <run-dir> [--previous <previous-run-dir>] [--lang de] [--link-media] [--threshold 0.002]

Only the standard library is required. If Pillow is installed, changed
screenshots also get a pixel-difference ratio and a diff image.
"""

import argparse
import base64
import datetime
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "report-template.html"
PLACEHOLDER = "__REPORT_DATA__"
STATUSES = ["ok", "problem", "blocked", "skipped", "not approved", "not reachable", "not applicable", "not supported"]
UNCHECKED = {"blocked", "not reachable", "not approved"}
MEDIA_RE = re.compile(r"[\w./*\-\[\]]+\.(?:png|jpe?g|gif|webp|svg|mp4|mov|webm)", re.IGNORECASE)
VIDEO_EXT = {".mp4", ".mov", ".webm"}
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".webp": "image/webp", ".svg": "image/svg+xml"}
EMBED_LIMIT = 40 * 1024 * 1024  # stop embedding once report.html would grow past this
PRIO_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}
GROUP_KEYS = ["fix", "decide", "leave"]
GROUP_WORDS = {"fix": ("fix", "beheben", "a"), "decide": ("decide", "entscheiden", "b"), "leave": ("leave", "lassen", "c")}

LABELS = {
    "en": {
        "eyebrow": "Interaction audit", "itemsChecked": "items checked", "comparedWith": "compared with",
        "changedShots": "changed screenshots", "allPrios": "All priorities", "search": "Search findings",
        "missing": "missing", "details": "Finding details", "startState": "Start state", "category": "Category",
        "notes": "Notes", "checklist": "All checklist items", "previous": "previous", "current": "current",
        "blink": "Blink compare", "stop": "Stop",
        "groups": {"fix": "Fix", "decide": "Decide", "leave": "Leave", "unchecked": "Not checked"},
        "hints": {"fix": "Clear bugs and rule violations. Answer with the numbers you want fixed.",
                  "decide": "May be intended or needs your call. Pick an option per number.",
                  "leave": "Cosmetic or arguably intended. Veto any you want fixed anyway.",
                  "unchecked": "Out of reach in this run, with how you can check it yourself."},
        "cols": {"no": "No.", "prio": "Prio", "where": "Where", "do": "What you do", "happens": "What happens",
                 "should": "Should be", "why": "Why it matters", "fix": "Fix", "options": "Options", "proof": "Proof",
                 "what": "What", "leave": "Why leave it", "whynot": "Why not", "howcheck": "How you check it"},
        "prioNames": {"A": "critical", "B": "core flow", "C": "other screens", "D": "polish"},
        "statuses": {"ok": "ok", "problem": "problem", "blocked": "blocked", "skipped": "skipped", "not approved": "not approved",
                     "not reachable": "not reachable", "not applicable": "not applicable",
                     "not supported": "not supported", "open": "open", "other": "other"},
        "cmp": {"changed": "changed", "new": "new", "same": "unchanged"},
        "summary": "{t} items checked · {a} fix · {b} decide · {c} leave · {n} not checked",
    },
    "de": {
        "eyebrow": "Interaktions-Prüfung", "itemsChecked": "Punkte geprüft", "comparedWith": "verglichen mit",
        "changedShots": "geänderte Screenshots", "allPrios": "Alle Prios", "search": "Funde durchsuchen",
        "missing": "fehlt", "details": "Funde im Detail", "startState": "Ausgangslage", "category": "Art",
        "notes": "Notizen", "checklist": "Alle Prüfpunkte", "previous": "vorher", "current": "jetzt",
        "blink": "Überblenden", "stop": "Stopp",
        "groups": {"fix": "Beheben", "decide": "Entscheiden", "leave": "Lassen", "unchecked": "Nicht geprüft"},
        "hints": {"fix": "Klare Fehler und Regelverstöße. Antworte mit den Nummern, die behoben werden sollen.",
                  "decide": "Vielleicht Absicht oder deine Entscheidung. Wähle pro Nummer eine Option.",
                  "leave": "Kosmetisch oder vermutlich Absicht. Widersprich, wenn doch etwas behoben werden soll.",
                  "unchecked": "In diesem Lauf nicht erreichbar, mit Anleitung zum Selbstprüfen."},
        "cols": {"no": "Nr", "prio": "Prio", "where": "Wo", "do": "Was du tust", "happens": "Was passiert",
                 "should": "Richtig wäre", "why": "Warum es stört", "fix": "Lösung", "options": "Optionen",
                 "proof": "Beweis", "what": "Was", "leave": "Warum lassen", "whynot": "Warum nicht",
                 "howcheck": "So prüfst du es"},
        "prioNames": {"A": "kritisch", "B": "Kernablauf", "C": "andere Bildschirme", "D": "Feinschliff"},
        "statuses": {"ok": "ok", "problem": "Problem", "blocked": "blockiert", "skipped": "übersprungen",
                     "not approved": "nicht freigegeben", "not reachable": "nicht erreichbar", "not applicable": "nicht zutreffend",
                     "not supported": "nicht unterstützt", "open": "offen", "other": "anderes"},
        "cmp": {"changed": "geändert", "new": "neu", "same": "unverändert"},
        "summary": "{t} Punkte geprüft · {a} beheben · {b} entscheiden · {c} lassen · {n} nicht geprüft",
    },
}


# ---------- parsing ----------

def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def status_of(result):
    text = result.lower().strip()
    for status in STATUSES:
        if text.startswith(status):
            return status
    return "open" if text in {"", "…", "...", "-", "–"} else "other"


def parse_checklist(path):
    """Return sections: [{title, items: [{id, what, expected, result, status, proof}]}]."""
    sections, current, header = [], None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "items": []}
            sections.append(current)
            header = None
            continue
        if not line.lstrip().startswith("|"):
            if not line.strip():
                header = None
            continue
        cells = split_row(line)
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if current is None or header[0] != "id":
            continue
        row = dict(zip(header, cells))
        result = row.get("result", "")
        what = row.get("interaction") or row.get("variation") or row.get("item") or ""
        prio = re.match(r"([ABCD])\s+(.*)$", what)
        current["items"].append({
            "id": row.get("id", ""),
            "prio": prio.group(1) if prio else "",
            "what": prio.group(2) if prio else what,
            "expected": row.get("expected") or row.get("screens checked") or "",
            "result": result,
            "status": status_of(result),
            "proof": row.get("proof", ""),
        })
    return [s for s in sections if s["items"]]


def group_of(value):
    text = value.strip().lower()
    for key, words in GROUP_WORDS.items():
        if text.startswith(words[:2]) or text == words[2]:
            return key
    return "fix"


def parse_findings(path):
    """Return findings ordered by group and priority, with one running number."""
    if not path.exists():
        return []
    findings, current, key = [], None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            fid = re.match(r"(F-\d+)", title)
            current = {"id": fid.group(1) if fid else f"F-{len(findings) + 1:03d}",
                       "title": title[len(fid.group(1)):].strip() if fid else title, "fields": {}, "steps": []}
            findings.append(current)
            key = None
            continue
        if current is None:
            continue
        field = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if field:
            key = field.group(1).strip().lower()
            current["fields"][key] = field.group(2).strip()
        elif key == "steps" and re.match(r"^\s+(\d+\.|-)\s", line):
            current["steps"].append(re.sub(r"^\s+(\d+\.|-)\s", "", line))
    for f in findings:
        fields = f["fields"]
        f["where"] = re.sub(r",?\s*item\s+\S+\s*$", "", fields.get("where", ""))
        f["group"] = group_of(fields.get("group", ""))
        prio = re.match(r"\s*([ABCD])(?![\w+])", fields.get("prio", "") or fields.get("priority", ""))
        f["prio"] = prio.group(1) if prio else ""
        f["fix"] = next((v for k, v in fields.items() if k.startswith(("fix", "proposed fix", "options"))), "")
        if not f["steps"] and fields.get("steps"):
            f["steps"] = [fields["steps"]]
    ordered = sorted(findings, key=lambda f: (GROUP_KEYS.index(f["group"]), PRIO_ORDER.get(f["prio"], 9)))
    for n, f in enumerate(ordered, 1):
        f["no"] = n
    return ordered


# ---------- media and comparison ----------

def expand_media(run_dir, proof):
    files = []
    for token in MEDIA_RE.findall(proof or ""):
        if "*" in token:
            files.extend(sorted(p.relative_to(run_dir).as_posix() for p in run_dir.glob(token)))
        else:
            files.append(token)
    return files


def rel_link(target, base):
    try:
        return Path(target).resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return Path(target).resolve().as_uri()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixel_diff(current, previous, out_path):
    """Changed-pixel ratio plus a diff image, or None without Pillow."""
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
    if changed:
        overlay = a.copy()
        overlay.paste((255, 0, 80), mask=diff)
        Image.blend(a, overlay, 0.6).save(out_path)
    return changed / (a.size[0] * a.size[1])


def compare(run_dir, prev_dir, rel, threshold):
    if prev_dir is None or Path(rel).suffix.lower() in VIDEO_EXT or not (run_dir / rel).exists():
        return None
    current, previous = run_dir / rel, prev_dir / rel
    if not previous.exists():
        return {"state": "new"}
    if file_hash(current) == file_hash(previous):
        return {"state": "same"}
    diff_dir = run_dir / "report-diffs"
    diff_dir.mkdir(exist_ok=True)
    diff_path = diff_dir / rel.replace("/", "__")
    ratio = pixel_diff(current, previous, diff_path)
    if ratio is not None and ratio <= threshold:
        return {"state": "same", "ratio": ratio}
    return {"state": "changed", "prev": rel_link(previous, run_dir), "ratio": ratio,
            "diff": rel_link(diff_path, run_dir) if diff_path.exists() else None}


MIN_PROOF_WIDTH = 600


def image_size(path):
    """Width and height of a PNG or JPEG from its header, or None."""
    try:
        with open(path, "rb") as f:
            head = f.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker, size = struct.unpack(">2sH", f.read(4))
                    if marker[0] != 0xFF:
                        return None
                    if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                        h, w = struct.unpack(">xHH", f.read(5))
                        return w, h
                    f.seek(size - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def proof_warnings(data, run_dir):
    """Proofs of findings that the user could not read: missing or too small."""
    out = []
    for f in data.get("findings", []):
        for m in f.get("media", []):
            if m["missing"]:
                out.append(f"finding {f['no']}: {m['src']} is missing")
            elif m["type"] == "image":
                size = image_size(run_dir / m["src"])
                if size and size[0] < MIN_PROOF_WIDTH:
                    out.append(f"finding {f['no']}: {m['src']} is only {size[0]}×{size[1]} px; "
                               f"recapture at full resolution or scale the detail crop to ≥ {MIN_PROOF_WIDTH} px")
    return out


def media_list(run_dir, proof, prev_dir=None, threshold=0.0):
    out = []
    for rel in expand_media(run_dir, proof):
        entry = {"src": rel, "type": "video" if Path(rel).suffix.lower() in VIDEO_EXT else "image",
                 "missing": not (run_dir / rel).exists()}
        cmp = compare(run_dir, prev_dir, rel, threshold)
        if cmp:
            entry["cmp"] = cmp
        out.append(entry)
    return out


def embed_media(data, run_dir):
    """Add data: URIs for every image, as long as the total stays under EMBED_LIMIT."""
    total, cache = 0, {}

    def uri(path):
        nonlocal total
        path = Path(path)
        if path in cache:
            return cache[path]
        mime = MIME.get(path.suffix.lower())
        if not mime or not path.exists():
            return None
        raw = path.read_bytes()
        if total + len(raw) * 4 // 3 > EMBED_LIMIT:
            return None
        total += len(raw) * 4 // 3
        cache[path] = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
        return cache[path]

    lists = [f["media"] for f in data["findings"]] + [i["media"] for s in data["sections"] for i in s["items"]]
    for media in lists:
        for m in media:
            if m["type"] == "image" and not m["missing"]:
                m["data"] = uri(run_dir / m["src"])
            prev = m.get("cmp", {}).get("prev")
            if prev and not prev.startswith("file:"):
                m["cmp"]["prevData"] = uri(run_dir / prev)
    return total


# ---------- outputs ----------

def build_data(run_dir, prev_dir, threshold, lang):
    checklist = run_dir / "checklist.md"
    if not checklist.exists():
        sys.exit(f"No checklist.md in {run_dir}")
    text = checklist.read_text(encoding="utf-8")
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), run_dir.name)
    sections = parse_checklist(checklist)
    findings = parse_findings(run_dir / "findings.md")

    status_counts, changed = {}, 0
    for sec in sections:
        for item in sec["items"]:
            status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
            item["media"] = media_list(run_dir, item.pop("proof"), prev_dir, threshold)
            changed += any(m.get("cmp", {}).get("state") == "changed" for m in item["media"])

    unchecked_items = [i for s in sections for i in s["items"] if i["status"] in UNCHECKED]
    unchecked = [{"no": n, "prio": i["prio"], "what": i["what"],
                  "why": re.sub(r"^(blocked|not reachable|not approved)\s*", "", i["result"]).strip(" ()") or i["result"],
                  "how": i["expected"]} for n, i in enumerate(unchecked_items, len(findings) + 1)]

    out_findings = [{
        "no": f["no"], "id": f["id"], "group": f["group"], "prio": f["prio"], "title": f["title"],
        "where": f["where"], "start": f["fields"].get("start state", ""), "steps": f["steps"],
        "actual": f["fields"].get("actual", ""), "expected": f["fields"].get("expected", ""),
        "why": f["fields"].get("why it matters", ""), "fix": f["fix"],
        "category": f["fields"].get("category", ""), "notes": f["fields"].get("notes", ""),
        "media": media_list(run_dir, f["fields"].get("proof", "")),
    } for f in findings]

    counts = {g: sum(1 for f in findings if f["group"] == g) for g in GROUP_KEYS}
    counts.update({"unchecked": len(unchecked), "items": sum(status_counts.values()), "changed": changed})
    return {
        "lang": lang, "labels": LABELS[lang], "title": title,
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "compared": str(prev_dir) if prev_dir else None,
        "counts": counts, "statusCounts": dict(sorted(status_counts.items(), key=lambda x: -x[1])),
        "findings": out_findings, "unchecked": unchecked,
        "sections": [{"title": s["title"], "items": s["items"]} for s in sections],
    }


def md_cell(text):
    return " ".join(str(text).split()).replace("|", "\\|")


def md_proof(media):
    out = []
    for m in media:
        if m["missing"]:
            out.append(f"missing: {m['src']}")
        elif m["type"] == "video":
            out.append(f"[▶ {Path(m['src']).name}]({m['src']})")
        else:
            out.append(f'<img src="{m["src"]}" width="160">')
    return " ".join(out)


def summary_markdown(data):
    """The user-facing result as Markdown: overview line and the four tables."""
    L, c = data["labels"], data["counts"]
    cols = L["cols"]
    lines = [f"# {data['title']}", "",
             L["summary"].format(t=c["items"], a=c["fix"], b=c["decide"], c=c["leave"], n=c["unchecked"]), ""]
    for group in ("fix", "decide"):
        rows = [f for f in data["findings"] if f["group"] == group]
        if not rows:
            continue
        last = cols["fix"] if group == "fix" else cols["options"]
        lines += [f"## {L['groups'][group]}", "",
                  f"| {cols['no']} | {cols['prio']} | {cols['where']} | {cols['do']} | {cols['happens']} | "
                  f"{cols['should']} | {cols['why']} | {last} | {cols['proof']} |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for f in rows:
            cells = [f["no"], f["prio"], f["where"], " → ".join(f["steps"]), f["actual"], f["expected"],
                     f["why"], f["fix"], md_proof(f["media"])]
            lines.append("| " + " | ".join(md_cell(x) for x in cells) + " |")
        lines.append("")
    rows = [f for f in data["findings"] if f["group"] == "leave"]
    if rows:
        lines += [f"## {L['groups']['leave']}", "",
                  f"| {cols['no']} | {cols['prio']} | {cols['where']} | {cols['what']} | {cols['leave']} |", "|---|---|---|---|---|"]
        lines += [f"| {f['no']} | {f['prio']} | {md_cell(f['where'])} | {md_cell(f['title'])} | {md_cell(f['why'])} |" for f in rows]
        lines.append("")
    if data["unchecked"]:
        lines += [f"## {L['groups']['unchecked']}", "",
                  f"| {cols['no']} | {cols['what']} | {cols['whynot']} | {cols['howcheck']} |", "|---|---|---|---|"]
        lines += [f"| {u['no']} | {md_cell(u['what'])} | {md_cell(u['why'])} | {md_cell(u['how'])} |" for u in data["unchecked"]]
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--previous", type=Path, help="previous run folder to compare screenshots with")
    parser.add_argument("--lang", choices=sorted(LABELS), default="en", help="language of headings and column names")
    parser.add_argument("--link-media", action="store_true",
                        help="link images instead of embedding them in report.html (smaller file, needs the run folder)")
    parser.add_argument("--threshold", type=float, default=0.002,
                        help="changed-pixel ratio still counted as unchanged (Pillow only)")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    prev = args.previous.resolve() if args.previous else None
    if prev and not prev.is_dir():
        sys.exit(f"Previous run not found: {prev}")

    data = build_data(run_dir, prev, args.threshold, args.lang)
    if not any(s["items"] for s in data.get("sections", [])):
        print("Warning: no checklist items found. checklist.md needs table rows (| ID | Interaction | …) under '## ' headings, "
              "as in references/checklist-template.md.", file=sys.stderr)
    for warning in proof_warnings(data, run_dir):
        print("Proof warning: " + warning, file=sys.stderr)
    summary = summary_markdown(data)
    if not args.link_media:
        embed_media(data, run_dir)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        sys.exit(f"Placeholder {PLACEHOLDER} not found in {TEMPLATE}")
    (run_dir / "report.html").write_text(template.replace(PLACEHOLDER, payload), encoding="utf-8")
    (run_dir / "summary.md").write_text(summary, encoding="utf-8")
    print(json.dumps({"report": str(run_dir / "report.html"), "summary": str(run_dir / "summary.md"),
                      "counts": data["counts"]}))


if __name__ == "__main__":
    main()
