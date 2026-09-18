"""
sa-framework builders — profile resolution.

Two independent profile axes, deliberately kept apart:

* **Document profile** (`document-data/templates.yaml`) — the *brand shell*: which DOCX template,
  which placeholders, which sections are approved boilerplate. Selected by language.
* **Render profile** (`document-data/render-profiles/*.yaml`) — the *content structure*: which
  sections in which order, which workbook tabs, which commercial constraints. Selected by client.

Keeping them separate is the point. A Hungarian-language Vodafone Romania offer is a real
combination, and collapsing the two axes into one "profile" makes it unrepresentable. It also
keeps a single large customer's document preferences out of the shared builders, where they would
become everyone's default the moment somebody forgot to guard a branch.
"""

from __future__ import annotations

from pathlib import Path

from common import config_root, load_config

BASE_KEY = "extends"


# --------------------------------------------------------------------------- render profile


def resolve_render_profile(engagement: dict, root: Path | None = None) -> dict:
    """Return the fully-merged render profile for an engagement, plus how it was chosen.

    Resolution order, first hit wins:

    1. `engagement.json.render_profile` — an explicit human decision, never overridden.
    2. A profile whose `matches.client_patterns` matches the engagement's client name.
    3. `standard`.

    The result carries `_resolved` describing which rule fired, so `/sa:package` can report the
    choice rather than leaving the reader to infer it from the output.
    """
    root = root or config_root()
    directory = root / "document-data" / "render-profiles"
    available = _available(directory)

    explicit = (engagement or {}).get("render_profile")
    if explicit:
        if explicit not in available:
            raise ValueError(
                f"engagement.json names render_profile '{explicit}', which does not exist in "
                f"{directory}. Available: {', '.join(sorted(available)) or 'none'}."
            )
        return _load_merged(explicit, directory, reason=f"engagement.json names '{explicit}'")

    client = ((engagement or {}).get("client") or "").strip()
    if client:
        for name in sorted(available):
            if name == "standard":
                continue
            profile = load_config(available[name])
            patterns = ((profile.get("matches") or {}).get("client_patterns")) or []
            for pattern in patterns:
                if pattern.lower() in client.lower():
                    return _load_merged(
                        name, directory, reason=f"client '{client}' matched pattern '{pattern}'"
                    )

    if "standard" not in available:
        raise FileNotFoundError(
            f"No render profile found. Expected at least {directory / 'standard.yaml'}."
        )
    return _load_merged("standard", directory, reason="default — no client-specific profile matched")


def _available(directory: Path) -> dict:
    if not directory.is_dir():
        return {}
    found = {}
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() in (".yaml", ".yml", ".json"):
            found[path.stem] = path
    return found


def _load_merged(name: str, directory: Path, reason: str, _seen=None) -> dict:
    """Load a profile and fold it onto its base, recursively."""
    _seen = _seen or []
    if name in _seen:
        raise ValueError(f"Render profile inheritance loop: {' -> '.join(_seen + [name])}")
    available = _available(directory)
    profile = load_config(available[name])
    base_name = profile.get(BASE_KEY)
    if base_name:
        if base_name not in available:
            raise ValueError(f"Render profile '{name}' extends '{base_name}', which does not exist.")
        base = _load_merged(base_name, directory, reason, _seen + [name])
        redundant = _redundant_keys(base, profile)
        merged = _merge(base, profile)
        merged["_redundant_overrides"] = redundant
    else:
        merged = dict(profile)
        merged.setdefault("_redundant_overrides", [])
    merged["_resolved"] = {"name": name, "reason": reason, "chain": _seen + [name]}
    return merged


def _merge(base, override):
    """Deep-merge `override` onto `base`.

    Mappings merge key by key. Scalars and plain lists replace outright. Section lists are the one
    structural exception, handled by `_merge_sections`: a client profile adds a section without
    restating the eight it inherits, because a restated list is the thing that drifts.
    """
    if not isinstance(base, dict) or not isinstance(override, dict):
        return override
    out = dict(base)
    for key, value in override.items():
        if key in (BASE_KEY, "matches", "name", "description"):
            out[key] = value
        elif key == "sections" and isinstance(value, list) and isinstance(out.get("sections"), list):
            out["sections"] = _merge_sections(out["sections"], value)
        elif isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def _merge_sections(base_sections, overrides):
    """Fold section overrides into an inherited section list.

    An override matching an inherited `id` replaces that section in place. A new `id` is inserted
    where its `position` says: `first`, `last`, `before:<id>` or `after:<id>`. A new section with no
    `position` goes last — visible, rather than silently dropped for lacking a field.
    """
    out = [dict(s) for s in base_sections]
    index = {s.get("id"): i for i, s in enumerate(out)}

    for override in overrides:
        sid = override.get("id")
        if sid in index:
            out[index[sid]] = _merge(out[index[sid]], override)
            continue

        entry = dict(override)
        position = entry.pop("position", "last")
        if position == "first":
            out.insert(0, entry)
        elif isinstance(position, str) and position.startswith(("before:", "after:")):
            anchor_kind, _, anchor = position.partition(":")
            anchor_positions = [i for i, s in enumerate(out) if s.get("id") == anchor]
            if not anchor_positions:
                raise ValueError(
                    f"Section '{sid}' asks to be placed {anchor_kind} '{anchor}', "
                    f"which is not in the inherited section list."
                )
            at = anchor_positions[0] + (1 if anchor_kind == "after" else 0)
            out.insert(at, entry)
        else:
            out.append(entry)
        index = {s.get("id"): i for i, s in enumerate(out)}
    return out


def _redundant_keys(base, override, path=""):
    """Find override keys whose value already equals the inherited one.

    Reported, never corrected. A client profile restating a value it inherits is harmless today and
    is exactly what stops tracking the base tomorrow, so it is worth one line in the build report.
    """
    found = []
    if not isinstance(base, dict) or not isinstance(override, dict):
        return found
    for key, value in override.items():
        if key in (BASE_KEY, "name", "description", "matches"):
            continue
        here = f"{path}.{key}" if path else key
        if key in base:
            if isinstance(value, dict) and isinstance(base[key], dict):
                found.extend(_redundant_keys(base[key], value, here))
            elif base[key] == value:
                found.append(here)
    return found


# --------------------------------------------------------------------------- document profile


def resolve_document_profile(engagement: dict, root: Path | None = None) -> dict:
    """Resolve the branded DOCX shell, per ARTIFACT-SCHEMAS.md §8.

    Returns a dict with `profile`, `template_path`, `org`, `reason`, and `branded`. **Never raises
    for a missing template** — it returns `branded: False` with a reason, because an unbranded
    build that says so is recoverable and an exception in the middle of packaging is not. What it
    must never do is return `branded: True` for a template it did not actually find: a document
    that quietly lost the client's branding looks like carelessness and nobody notices until it has
    been sent.
    """
    root = root or config_root()
    result = {"profile": None, "template_path": None, "org": None, "branded": False, "reason": ""}

    explicit = (engagement or {}).get("template_path")
    if explicit and Path(explicit).is_file():
        result.update(
            template_path=Path(explicit),
            branded=True,
            reason="engagement.json.template_path",
        )

    config_path = root / "document-data" / "templates.yaml"
    if not config_path.is_file():
        if not result["branded"]:
            result["reason"] = f"no templates.yaml at {config_path}"
        return result

    config = load_config(config_path)
    orgs = config.get("orgs") or {}
    org_name = (engagement or {}).get("vendor_org_key") or config.get("default_org")
    org = orgs.get(org_name) or {}
    result["org"] = {"key": org_name, **{k: v for k, v in org.items() if k != "profiles"}}

    profiles = org.get("profiles") or {}
    name = (engagement or {}).get("document_profile")
    if not name:
        locale = (engagement or {}).get("locale")
        language = (engagement or {}).get("deliverable_language")
        for candidate, body in profiles.items():
            if language and str(body.get("language", "")).lower() == str(language).lower():
                name = candidate
                break
            if locale and locale in (body.get("locales") or []):
                name = candidate
                break
        name = name or org.get("default_profile")

    profile = profiles.get(name)
    if not profile:
        if not result["branded"]:
            result["reason"] = f"no profile '{name}' under org '{org_name}' in templates.yaml"
        return result

    result["profile"] = {"key": name, **profile}
    if not result["branded"]:
        template = config_path.parent / str(profile.get("template", ""))
        if template.is_file():
            result.update(template_path=template, branded=True, reason=f"profile '{name}'")
        else:
            result["reason"] = f"profile '{name}' names template '{template}', which does not exist"
    return result


def check_language_match(engagement: dict, document_profile: dict):
    """Return a refusal message when the artifacts' language differs from the profile's.

    `deliverable_language` selects the profile; it does not authorize translation. Machine-
    translating a client document is a decision for a person, not a side effect of packaging.
    """
    profile = (document_profile or {}).get("profile") or {}
    wanted = (engagement or {}).get("deliverable_language")
    have = profile.get("language")
    if wanted and have and str(wanted).lower() != str(have).lower():
        return (
            f"engagement.json asks for a {wanted} deliverable but the resolved document profile "
            f"'{profile.get('key')}' is {have}. Packaging will not translate. Set document_profile "
            f"explicitly, or have the artifacts rewritten in {have} first."
        )
    return None
