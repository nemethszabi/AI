"""
sa-framework builders — component diagram renderer.

Draws the single figure a solution offer needs: a layered component view, on a white background,
at print resolution. Deterministic, dependency-light (Pillow only), and reproducible — the same
architecture.json always produces the same image.

**Why not Mermaid.** `mermaid-diagram-maker` and `mmdc` remain the right tool for the varied,
exploratory diagrams an HLD carries: sequences, deployments, state machines. They are the wrong
tool for the one figure that must appear in every client offer, for three reasons learned the hard
way:

1. `mmdc` is a Node toolchain that is frequently absent, and a missing diagram in a client document
   is not a warning — it is a figure reference pointing at nothing.
2. Mermaid's own theme decides the background. Offers have repeatedly shipped with a grey or
   transparent-over-grey figure.
3. Auto-layout drifts between versions, so the same architecture renders differently in v6 and v7
   of the same offer, and a reader assumes the design changed.

This renderer answers one narrow question — *what are the parts and how do they connect* — and
answers it the same way every time. Anything richer stays with Mermaid, in the HLD.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Layout constants, in pixels at 2x scale (the image is downsampled for smooth edges).
SCALE = 2
WIDTH = 1600
MARGIN = 48
TIER_LABEL_W = 150
BOX_H = 104
BOX_GAP_X = 24
TIER_GAP_Y = 76
RADIUS = 10

WHITE = (255, 255, 255)
INK = (33, 37, 41)
MUTED = (108, 117, 125)
RULE = (206, 212, 218)
TIER_BG = (248, 249, 250)

# Box roles. "primary" is what the vendor builds; "external" is what already exists. The visual
# distinction is the whole point of the figure — a client must see at a glance which boxes are
# being bought.
ROLE_STYLES = {
    "primary": {"fill": (255, 245, 240), "border": (255, 69, 0), "border_w": 2, "text": INK},
    "external": {"fill": (247, 248, 250), "border": (173, 181, 189), "border_w": 1, "text": INK},
    "data": {"fill": (243, 246, 250), "border": (134, 152, 178), "border_w": 1, "text": INK},
}


def _font(size: int, bold: bool = False):
    """Load a system font, falling back to Pillow's default.

    The fallback is legible but unattractive; it is reported by the caller rather than passed off
    as the intended output.
    """
    candidates = (
        ["calibrib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["calibri.ttf", "arial.ttf", "DejaVuSans.ttf"]
    )
    for name in candidates:
        for base in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu"), Path(".")):
            path = base / name
            if path.is_file():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w, max_lines):
    """Wrap text to fit a box, truncating with an ellipsis rather than overflowing."""
    words = (text or "").split()
    if not words:
        return []
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and draw.textlength(lines[-1] + "…", font=font) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1] += "…"
    return lines


def render_component_view(tiers, edges, out_path, title=None, max_width_px=WIDTH):
    """Render a layered component diagram to a PNG on a white background.

    `tiers` is an ordered list of `{"label": str, "boxes": [{"name", "note", "role"}]}`, drawn top
    to bottom. `edges` is a list of `{"from": box-name, "to": box-name, "label": str}`; an edge
    naming a box that is not in `tiers` is skipped and returned in the report rather than drawn to
    a guessed position.

    Returns a report dict: the output path, the pixel size, the fonts used, and any skipped edges.
    A caller that wants to know whether the figure is trustworthy reads that, not the exit code.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tiers = [t for t in (tiers or []) if t.get("boxes")]
    if not tiers:
        raise ValueError("render_component_view: no tiers with boxes — nothing to draw.")
    tiers = order_tiers(tiers, edges)

    f_box = _font(19 * SCALE, bold=True)
    f_note = _font(16 * SCALE)
    f_tier = _font(16 * SCALE, bold=True)
    f_edge = _font(15 * SCALE)
    f_title = _font(24 * SCALE, bold=True)
    default_font = isinstance(f_box, ImageFont.ImageFont)

    width = max_width_px * SCALE
    content_x = (MARGIN + TIER_LABEL_W) * SCALE
    content_w = width - content_x - MARGIN * SCALE

    title_h = (52 if title else 0) * SCALE
    tier_h = BOX_H * SCALE
    height = (
        MARGIN * SCALE
        + title_h
        + len(tiers) * tier_h
        + (len(tiers) - 1) * TIER_GAP_Y * SCALE
        + MARGIN * SCALE
    )

    img = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(img)

    if title:
        draw.text((MARGIN * SCALE, MARGIN * SCALE), title, font=f_title, fill=INK)

    positions = {}
    y = MARGIN * SCALE + title_h
    for tier in tiers:
        boxes = tier["boxes"]
        gap = BOX_GAP_X * SCALE
        box_w = (content_w - gap * (len(boxes) - 1)) // len(boxes)

        draw.rounded_rectangle(
            [MARGIN * SCALE, y, width - MARGIN * SCALE, y + tier_h],
            radius=RADIUS * SCALE,
            fill=TIER_BG,
        )
        label_lines = _wrap(draw, tier.get("label", ""), f_tier, (TIER_LABEL_W - 16) * SCALE, 3)
        ly = y + tier_h // 2 - (len(label_lines) * 22 * SCALE) // 2
        for line in label_lines:
            draw.text((MARGIN * SCALE + 12 * SCALE, ly), line, font=f_tier, fill=MUTED)
            ly += 22 * SCALE

        x = content_x
        for box in boxes:
            style = ROLE_STYLES.get(box.get("role", "primary"), ROLE_STYLES["primary"])
            top = y + 12 * SCALE
            bottom = y + tier_h - 12 * SCALE
            draw.rounded_rectangle(
                [x, top, x + box_w, bottom],
                radius=RADIUS * SCALE,
                fill=style["fill"],
                outline=style["border"],
                width=style["border_w"] * SCALE,
            )
            positions[box["name"]] = {
                "cx": x + box_w // 2,
                "top": top,
                "bottom": bottom,
                "w": box_w,
            }

            inner = box_w - 24 * SCALE
            name_lines = _wrap(draw, box["name"], f_box, inner, 2)
            note_lines = _wrap(draw, box.get("note", ""), f_note, inner, 2) if box.get("note") else []
            block_h = len(name_lines) * 24 * SCALE + len(note_lines) * 20 * SCALE
            ty = top + ((bottom - top) - block_h) // 2
            for line in name_lines:
                w = draw.textlength(line, font=f_box)
                draw.text((x + (box_w - w) // 2, ty), line, font=f_box, fill=style["text"])
                ty += 24 * SCALE
            for line in note_lines:
                w = draw.textlength(line, font=f_note)
                draw.text((x + (box_w - w) // 2, ty), line, font=f_note, fill=MUTED)
                ty += 20 * SCALE
            x += box_w + gap
        y += tier_h + TIER_GAP_Y * SCALE

    skipped = []
    for edge in edges or []:
        a, b = positions.get(edge.get("from")), positions.get(edge.get("to"))
        if not a or not b:
            skipped.append(f"{edge.get('from')} -> {edge.get('to')}")
            continue
        _arrow(draw, a, b, edge.get("label"), f_edge)

    if SCALE != 1:
        img = img.resize((width // SCALE, height // SCALE), Image.LANCZOS)
    img.save(out_path, "PNG", dpi=(200, 200))

    return {
        "path": str(out_path),
        "size_px": img.size,
        "tiers": len(tiers),
        "boxes": len(positions),
        "skipped_edges": skipped,
        "default_font": default_font,
    }


def order_tiers(tiers, edges, passes: int = 4):
    """Reorder boxes within each tier to reduce edge crossings.

    A standard barycentre heuristic: repeatedly place each box near the average position of the
    boxes it connects to in the neighbouring tier, sweeping down then up. It is not optimal —
    crossing minimisation is NP-hard — but it reliably removes the gratuitous crossings that make
    an otherwise correct figure look careless, and being a heuristic it never changes which boxes
    or edges exist, only their left-to-right order.

    Boxes with no connections keep their authored order, so a deliberate sequence in
    architecture.json survives.
    """
    tiers = [{**t, "boxes": list(t["boxes"])} for t in tiers]
    adjacency = {}
    for edge in edges or []:
        adjacency.setdefault(edge.get("from"), set()).add(edge.get("to"))
        adjacency.setdefault(edge.get("to"), set()).add(edge.get("from"))
    if not adjacency:
        return tiers

    def sweep(indices):
        for i in indices:
            neighbour_positions = {}
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < len(tiers):
                    for pos, box in enumerate(tiers[j]["boxes"]):
                        neighbour_positions[box["name"]] = (
                            pos / max(len(tiers[j]["boxes"]) - 1, 1)
                        )
            decorated = []
            for pos, box in enumerate(tiers[i]["boxes"]):
                linked = [
                    neighbour_positions[n]
                    for n in adjacency.get(box["name"], ())
                    if n in neighbour_positions
                ]
                own = pos / max(len(tiers[i]["boxes"]) - 1, 1)
                decorated.append((sum(linked) / len(linked) if linked else own, pos, box))
            tiers[i]["boxes"] = [box for _, _, box in sorted(decorated, key=lambda d: (d[0], d[1]))]

    for _ in range(passes):
        sweep(range(1, len(tiers)))
        sweep(range(len(tiers) - 2, -1, -1))
    return tiers


def _arrow(draw, a, b, label, font):
    """Draw a straight arrow between two boxes, with an optional mid-line label on white."""
    downward = b["top"] >= a["bottom"]
    x1, y1 = a["cx"], (a["bottom"] if downward else a["top"])
    x2, y2 = b["cx"], (b["top"] if downward else b["bottom"])
    draw.line([(x1, y1), (x2, y2)], fill=MUTED, width=2 * SCALE)

    head = 8 * SCALE
    if downward:
        draw.polygon([(x2, y2), (x2 - head, y2 - head), (x2 + head, y2 - head)], fill=MUTED)
    else:
        draw.polygon([(x2, y2), (x2 - head, y2 + head), (x2 + head, y2 + head)], fill=MUTED)

    if label:
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        w = draw.textlength(label, font=font)
        pad = 5 * SCALE
        draw.rectangle(
            [mx - w // 2 - pad, my - 11 * SCALE, mx + w // 2 + pad, my + 11 * SCALE],
            fill=WHITE,
        )
        draw.text((mx - w // 2, my - 9 * SCALE), label, font=font, fill=MUTED)


def render_timeline(phases, out_path, unit: str = "week", max_width_px: int = 1600):
    """Render a phase timeline bar chart to a PNG on a white background.

    `phases` is a list of `{"name", "start", "end"}` in whole units (weeks by default), optionally
    with `effort_md`. Overlapping phases are drawn overlapping, because that is the fact a reader
    most needs: a plan whose build phases overlap is a different commitment from one whose phases
    are strictly sequential, and a bar chart that quietly serialises them misrepresents the offer.

    Returns a report dict in the same shape as `render_component_view`.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    phases = [p for p in (phases or []) if p.get("start") is not None and p.get("end") is not None]
    if not phases:
        raise ValueError("render_timeline: no phases with a start and an end — nothing to draw.")

    f_label = _font(17 * SCALE, bold=True)
    f_axis = _font(15 * SCALE)
    f_bar = _font(15 * SCALE, bold=True)

    label_w = 420 * SCALE
    row_h = 46 * SCALE
    axis_h = 40 * SCALE
    width = max_width_px * SCALE
    left = MARGIN * SCALE + label_w
    right = width - MARGIN * SCALE
    height = MARGIN * SCALE + axis_h + len(phases) * row_h + MARGIN * SCALE

    last = max(int(p["end"]) for p in phases)
    first = min(int(p["start"]) for p in phases)
    span = max(last - first + 1, 1)

    img = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(img)

    def x_of(unit_index):
        return left + int((unit_index - first) / span * (right - left))

    # Gridlines and axis. Tick every unit while that stays legible, otherwise every fifth.
    step = 1 if span <= 16 else 5
    y_top = MARGIN * SCALE + axis_h
    y_bottom = y_top + len(phases) * row_h
    for u in range(first, last + 2, step):
        x = x_of(u)
        draw.line([(x, y_top), (x, y_bottom)], fill=(238, 240, 242), width=1 * SCALE)
        label = f"{unit[:1].upper()}{u}"
        draw.text((x + 4 * SCALE, MARGIN * SCALE + 12 * SCALE), label, font=f_axis, fill=MUTED)
    draw.line([(left, y_top), (right, y_top)], fill=RULE, width=1 * SCALE)

    accent = ROLE_STYLES["primary"]["border"]
    for i, phase in enumerate(phases):
        y = y_top + i * row_h
        cy = y + row_h // 2
        name = _wrap(draw, phase.get("name", ""), f_label, label_w - 16 * SCALE, 1)
        if name:
            draw.text((MARGIN * SCALE, cy - 10 * SCALE), name[0], font=f_label, fill=INK)

        x1, x2 = x_of(int(phase["start"])), x_of(int(phase["end"]) + 1)
        bar_top, bar_bottom = cy - 13 * SCALE, cy + 13 * SCALE
        draw.rounded_rectangle(
            [x1, bar_top, max(x2, x1 + 8 * SCALE), bar_bottom],
            radius=5 * SCALE,
            fill=ROLE_STYLES["primary"]["fill"],
            outline=accent,
            width=2 * SCALE,
        )
        if phase.get("effort_md") is not None:
            text = f"{phase['effort_md']} MD"
            if draw.textlength(text, font=f_bar) < (x2 - x1) - 16 * SCALE:
                w = draw.textlength(text, font=f_bar)
                draw.text((x1 + ((x2 - x1) - w) // 2, cy - 9 * SCALE), text, font=f_bar, fill=INK)

    if SCALE != 1:
        img = img.resize((width // SCALE, height // SCALE), Image.LANCZOS)
    img.save(out_path, "PNG", dpi=(200, 200))
    return {
        "path": str(out_path),
        "size_px": img.size,
        "phases": len(phases),
        "span_units": span,
        "unit": unit,
        "default_font": isinstance(f_label, ImageFont.ImageFont),
    }


def tiers_from_architecture(architecture: dict, vendor_hint: str = ""):
    """Derive diagram tiers and edges from `architecture.json`.

    Components are placed by their own `layer`/`tier` field where the architect supplied one, and
    otherwise by an explicit keyword map over the component's `type`. There is deliberately no
    clever inference: a component whose tier cannot be determined lands in "Solution components"
    and is listed in the returned report, so a human can fix the architecture rather than discover
    a mis-drawn figure in a client document.
    """
    components = (architecture or {}).get("components") or []
    order = ["Channels and sources", "Integration", "Solution components", "Data", "Consumers"]
    keyword_tier = {
        "ui": "Consumers",
        "frontend": "Consumers",
        "dashboard": "Consumers",
        "portal": "Consumers",
        "client": "Consumers",
        "store": "Data",
        "database": "Data",
        "db": "Data",
        "storage": "Data",
        "warehouse": "Data",
        "integration": "Integration",
        "connector": "Integration",
        "adapter": "Integration",
        "gateway": "Integration",
        "hook": "Integration",
        "api": "Integration",
        "source": "Channels and sources",
        "channel": "Channels and sources",
        "external": "Channels and sources",
    }

    buckets = {name: [] for name in order}
    unplaced = []
    for component in components:
        if str(component.get("status", "")).lower() == "withdrawn":
            continue
        name = component.get("name") or component.get("id")
        tier = component.get("layer") or component.get("tier")
        if not tier:
            haystack = " ".join(
                str(component.get(k, "")) for k in ("type", "kind", "name", "id")
            ).lower()
            for keyword, candidate in keyword_tier.items():
                if keyword in haystack:
                    tier = candidate
                    break
        if tier not in buckets:
            if tier:
                buckets.setdefault(tier, [])
            else:
                tier = "Solution components"
                unplaced.append(name)
        role = "external" if str(component.get("ownership", "")).lower() in ("client", "third-party", "existing") else "primary"
        if tier == "Data":
            role = "data"
        buckets[tier].append(
            {"name": name, "note": component.get("one_liner") or "", "role": role}
        )

    tiers = [{"label": label, "boxes": boxes} for label, boxes in buckets.items() if boxes]
    edges = []
    for point in (architecture or {}).get("integration_points") or []:
        if point.get("from") and point.get("to"):
            edges.append(
                {"from": point["from"], "to": point["to"], "label": point.get("protocol") or ""}
            )
    return tiers, edges, {"unplaced_components": unplaced}
