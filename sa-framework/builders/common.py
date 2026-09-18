"""
sa-framework builders — shared utilities.

Deterministic rendering helpers used by every deliverable builder. Nothing in this module
knows about a specific client, engagement or brand: client-specific behaviour arrives as a
render profile (see `profiles.py`), never as a branch in this file.

Design rules this module exists to enforce:

1. **One place rounds a number.** `md()` is the only function that turns a stored effort figure
   into display text. Four consumers rounding independently is how one estimate acquires four
   different totals (ARTIFACT-SCHEMAS.md §4.7).
2. **Read stored figures; never recompute a total.** `rollup_figure()` reads what the estimator
   stored. There is deliberately no helper here that sums line items into a rollup.
3. **Zero and absent are different.** `md()` renders a real 0 as "0" and a missing figure as an
   em dash (ESTIMATION-METHOD.md §11.4).
4. **No dependency beyond the standard library.** YAML support is optional: a minimal reader
   covers the subset the framework's own config files use, so a machine without PyYAML still
   builds deliverables.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

DASH = "—"  # em dash: "no figure exists"


# --------------------------------------------------------------------------- numbers


def md(value, *, unit: bool = False, decimals: int = 1, whole: bool = False) -> str:
    """Format a man-day figure for display. The ONLY place effort becomes text.

    `None` renders as an em dash ("no figure exists"), never as 0 — ESTIMATION-METHOD.md §11.4
    makes that distinction load-bearing, because a missing figure shown as zero silently claims
    the work is free and survives being forwarded without its caveat.

    `whole=True` applies the pinned precision rule for **any rollup or total**: whole man-days.
    Per-line figures keep one decimal. Rounding happens here, on output — never in the stored
    value, because rounding what is stored makes every downstream sum drift by a little and then
    nobody can tell whether a total is wrong or merely rounded (ESTIMATION-METHOD.md §1).

    Returns text, never a float, so a caller cannot accidentally do arithmetic on a rounded value.
    """
    if value is None:
        return DASH
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if whole:
        return f"{int(round(f))} MD" if unit else str(int(round(f)))
    if abs(f - round(f)) < 1e-9:
        out = str(int(round(f)))
    else:
        out = f"{f:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{out} MD" if unit else out


def pct(value) -> str:
    """Format a percentage. `None` renders as an em dash, 0 renders as '0%'."""
    if value is None:
        return DASH
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{int(round(f))}%"


def rollup_figure(rollup: dict, path: str, point: str = "pert"):
    """Read one stored three-point figure out of `estimation.json`'s rollup.

    `path` is dotted, e.g. "committed", "contingency.amount", "optional".
    `point` is best | likely | worst | pert.

    Returns the stored value or None. **Never computes one.** A total that is absent from the
    artifact is absent from the deliverable — a builder that fills the gap by summing lines is
    the fourth consumer ARTIFACT-SCHEMAS.md §4.7 warns about.
    """
    node = rollup or {}
    for part in path.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
        if node is None:
            return None
    if not isinstance(node, dict):
        return None
    # three-point figures live either directly on the node or under `ai_assisted`
    holder = node.get("ai_assisted") if isinstance(node.get("ai_assisted"), dict) else node
    return holder.get(point)


def render_worst(estimation: dict) -> bool:
    """Whether `worst` may appear in a rendered artifact at all.

    Default false, per ESTIMATION-METHOD.md §11.5: `worst` is always stored and always checked,
    but printing it beside the committed figure anchors readers on the tail. Only an explicit
    `basis.render_worst: true` — the engagement owner having asked — turns it on.
    """
    return bool(((estimation or {}).get("basis") or {}).get("render_worst"))


# --------------------------------------------------------------------------- text


def sentence_list(items, conjunction: str = "and") -> str:
    """Join strings into readable prose: 'a', 'a and b', 'a, b and c'."""
    items = [str(i) for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} {conjunction} {items[-1]}"


def truncate(text: str, limit: int) -> str:
    """Shorten to `limit` characters on a word boundary, with an ellipsis."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


_INTERNAL_MARKERS = (
    re.compile(r"generated from [a-z-]+\.json", re.I),
    re.compile(r"do not edit this file by hand", re.I),
    re.compile(r"\brevision \d+\b", re.I),
    re.compile(r"\bschema[_ ]version\b", re.I),
    re.compile(r"\b(req-analyst|req-architect|req-estimator|req-offer|req-auditor)\b", re.I),
    re.compile(r"ESTIMATION-METHOD\.md|ARTIFACT-SCHEMAS\.md|CONSTITUTION\.md", re.I),
    re.compile(r"\bai/sa/", re.I),
)


def find_internal_leaks(text: str):
    """Return the internal-provenance markers present in a string destined for a client document.

    A client deliverable must not carry the pipeline's own scaffolding. This is not hypothetical:
    a shipped offer opened with "Generated from offer.json revision 9. Do not edit this file by
    hand." The builder calls this on every string it writes and refuses the build on a hit, because
    the alternative is that nobody notices until the document is already with the client.
    """
    hits = []
    for pattern in _INTERNAL_MARKERS:
        m = pattern.search(text or "")
        if m:
            hits.append(m.group(0))
    return hits


# --------------------------------------------------------------------------- config


def config_root() -> Path:
    """Resolve the Claude config root, per ARTIFACT-SCHEMAS.md §8's chain.

    $CLAUDE_CONFIG_DIR, then ~/.claude. Never assume ~/.claude outright — more than one
    redirected root exists on some machines and guessing silently builds against the wrong
    template set.
    """
    env = os.environ.get("CLAUDE_CONFIG_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    return Path.home() / ".claude"


def load_json(path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_json_optional(path):
    """Load a JSON artifact, or return None when it does not exist.

    Soft inputs are genuinely optional — a rom-lane engagement has no architecture.json — and a
    builder that crashes on an absent soft input turns a lane rule into a stack trace.
    """
    p = Path(path)
    return load_json(p) if p.is_file() else None


def load_config(path):
    """Load a YAML or JSON config file.

    Prefers PyYAML when installed. Falls back to `mini_yaml` for the subset this framework's own
    config files use, so a machine without PyYAML is not a machine that cannot package.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return mini_yaml(text)


def mini_yaml(text: str):
    """Minimal YAML reader for the subset the framework's config files use.

    Supports: nested block mappings, block sequences, inline flow sequences ([a, b]), quoted and
    bare scalars, ints, floats, booleans, null, and `#` comments. Deliberately does NOT support
    anchors, multi-line scalars, or flow mappings — a config file needing those should be JSON
    instead of quietly parsing wrong here.

    Raises ValueError on a construct it does not understand, rather than returning a plausible
    but incorrect structure. A config silently misread is worse than a config that fails loudly.
    """
    root: dict = {}
    # stack of (indent, container); container is a dict or a list
    stack = [(-1, root)]
    pending_key = None  # (indent, key, parent_dict) awaiting its nested block

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not _in_quotes_hash(raw) else raw.rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"mini_yaml: indentation fell below the document root: {raw!r}")

        if pending_key and indent > pending_key[0]:
            key, parent = pending_key[1], pending_key[2]
            container = [] if body.startswith("- ") or body == "-" else {}
            parent[key] = container
            stack.append((pending_key[0], container))
            pending_key = None

        _, container = stack[-1]

        if body.startswith("- "):
            if not isinstance(container, list):
                raise ValueError(f"mini_yaml: list item outside a list: {raw!r}")
            item = body[2:].strip()
            if ":" in item and not item.startswith(("'", '"')):
                k, v = item.split(":", 1)
                obj = {k.strip(): _scalar(v.strip())}
                container.append(obj)
                stack.append((indent, obj))
            else:
                container.append(_scalar(item))
            continue

        if ":" not in body:
            raise ValueError(f"mini_yaml: expected 'key: value': {raw!r}")

        key, value = body.split(":", 1)
        key, value = _unquote(key.strip()), value.strip()
        if not isinstance(container, dict):
            raise ValueError(f"mini_yaml: mapping key inside a list: {raw!r}")
        if value == "":
            pending_key = (indent, key, container)
        else:
            container[key] = _scalar(value)
    return root


def _in_quotes_hash(raw: str) -> bool:
    """True when the line's '#' sits inside a quoted scalar and is therefore not a comment."""
    if "#" not in raw:
        return False
    before = raw.split("#", 1)[0]
    return before.count('"') % 2 == 1 or before.count("'") % 2 == 1


def _unquote(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _scalar(s: str):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [_scalar(p) for p in _split_flow(inner)] if inner else []
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    low = s.lower()
    if low in ("null", "~", ""):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d*\.\d+", s):
        return float(s)
    return s


def _split_flow(inner: str):
    parts, buf, quote = [], "", None
    for ch in inner:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf += ch
        elif ch == ",":
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts
