"""Applicability and dispatch over the catalog.

Given the structured features available for a case, decide which algorithms can
run, run them, and report which ones need more data. Optionally narrow to a
clinical presentation (e.g. "chest pain"). Built entirely on `engine.registry`;
the deterministic core stays untouched and instant, so dispatch is near-real-
time.

The feature space is flat: a field name (e.g. `systolic_bp_mmhg`) is assumed to
mean the same thing across algorithms, which holds for the vitals, labs, and
demographics these rules share. Callers pass one bag of available features; each
algorithm reads only the fields it declares.

Not a medical device. See DISCLAIMER.md and docs/architecture.md.
"""

from __future__ import annotations

from typing import Any

from . import registry


def presentations() -> list[str]:
    """Return every distinct presentation tag in the catalog, sorted."""
    tags: set[str] = set()
    for condition in registry.list_conditions():
        tags.update(condition["presentations"])
    return sorted(tags)


def _matches(query: str, tags: list[str]) -> bool:
    needle = query.lower()
    return any(needle in tag.lower() for tag in tags)


def by_presentation(presentation: str) -> list[str]:
    """Return the condition keys whose tags match `presentation`."""
    return [
        condition["key"]
        for condition in registry.list_conditions()
        if _matches(presentation, condition["presentations"])
    ]


def _candidates(presentation: str | None) -> list[dict[str, Any]]:
    conditions = registry.list_conditions()
    if presentation is None:
        return conditions
    return [c for c in conditions if _matches(presentation, c["presentations"])]


def suggest(
    features: dict[str, Any],
    presentation: str | None = None,
) -> list[dict[str, Any]]:
    """Rank catalog algorithms by how close they are to runnable on `features`.

    Args:
        features: A bag of available structured features (a flat dict).
        presentation: Optional presentation tag to narrow the catalog.

    Returns:
        One record per candidate condition — `key`, `label`, `presentations`,
        `runnable` (all inputs present), and `missing_inputs` — sorted with the
        runnable ones first, then by fewest missing inputs.
    """
    records = []
    for condition in _candidates(presentation):
        missing = registry.missing_inputs(condition["key"], features)
        records.append({
            "key": condition["key"],
            "label": condition["label"],
            "presentations": condition["presentations"],
            "runnable": not missing,
            "missing_inputs": missing,
        })
    records.sort(key=lambda r: (len(r["missing_inputs"]), r["key"]))
    return records


def _project(condition: str, features: dict[str, Any]) -> dict[str, Any]:
    required = registry.get_schema(condition)["required"]
    return {name: features[name] for name in required if name in features}


def run_applicable(
    features: dict[str, Any],
    presentation: str | None = None,
    include_unmet: bool = True,
) -> dict[str, Any]:
    """Run every algorithm whose inputs `features` fully satisfy.

    Args:
        features: A bag of available structured features (a flat dict). Extra
            fields are ignored per algorithm; each reads only what it declares.
        presentation: Optional presentation tag to narrow the catalog.
        include_unmet: If True, also report the algorithms that need more data.

    Returns:
        A dict with `applicable` (key, label, result for algorithms that ran),
        `needs_more_data` (key, label, missing_inputs), `errors` (key, label,
        error for inputs an algorithm rejected), and a `disclaimer`.
    """
    applicable: list[dict[str, Any]] = []
    needs_more_data: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for condition in _candidates(presentation):
        key, label = condition["key"], condition["label"]
        missing = registry.missing_inputs(key, features)
        if missing:
            if include_unmet:
                needs_more_data.append({"key": key, "label": label,
                                        "missing_inputs": missing})
            continue
        try:
            result = registry.run(key, _project(key, features))
        except ValueError as exc:
            errors.append({"key": key, "label": label, "error": str(exc)})
            continue
        applicable.append({"key": key, "label": label, "result": result})

    return {
        "applicable": applicable,
        "needs_more_data": needs_more_data,
        "errors": errors,
        "disclaimer": registry.DISCLAIMER,
    }
