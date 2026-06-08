"""Machine-readable catalog of the deterministic clinical algorithms.

This module is the single source of truth for the condition catalog. Input
schemas are derived by **introspection** of the frozen dataclasses in
`conditions/` (`typing.get_type_hints` + `dataclasses.fields`), so a schema can
never drift from the implementation it describes. The browser demo, the MCP
server, and the REST API all consume this registry.

Design constraints (see docs/architecture.md):
  - The deterministic core in `conditions/` is imported lazily, only when a
    condition is actually used.
  - This module adds no third-party dependencies (standard library only).
  - Inputs and outputs are structured data — never raw clinical notes / PHI.

Not a medical device; outputs are scores and recommendation bands for education
and research only. See DISCLAIMER.md.
"""

from __future__ import annotations

import dataclasses
import importlib
import typing
from typing import Any, Literal, get_args, get_origin

DISCLAIMER = (
    "Not a medical device. Outputs are scores and recommendation bands for "
    "education and research only, not diagnosis or treatment. See DISCLAIMER.md."
)


@dataclasses.dataclass(frozen=True)
class _Entry:
    """One callable algorithm in the catalog.

    `dataclass_params` are the feature dataclass names in call order;
    `scalar_params` are plain `(name, json_type)` arguments appended after the
    dataclass arguments. The flattened union of all their fields is the input
    schema the caller fills.
    """

    key: str
    label: str
    module: str
    fn: str
    presentations: tuple[str, ...]
    dataclass_params: tuple[str, ...]
    scalar_params: tuple[tuple[str, str], ...] = ()


_REGISTRY: tuple[_Entry, ...] = (
    _Entry("heart", "Chest pain — HEART score", "conditions.chest_pain",
           "heart_assessment", ("chest pain", "acute coronary syndrome"),
           ("HeartFeatures",)),
    _Entry("cha2ds2_vasc", "Atrial fibrillation — CHA2DS2-VASc (stroke risk)",
           "conditions.atrial_fibrillation", "cha2ds2_vasc_assessment",
           ("atrial fibrillation", "stroke risk", "anticoagulation"),
           ("Cha2ds2VascFeatures",)),
    _Entry("has_bled", "Atrial fibrillation — HAS-BLED (bleeding risk)",
           "conditions.atrial_fibrillation", "has_bled_assessment",
           ("atrial fibrillation", "bleeding risk", "anticoagulation"),
           ("HasBledFeatures",)),
    _Entry("crb_65", "Pneumonia — CRB-65 (primary-care severity)",
           "conditions.pneumonia", "crb_65_assessment",
           ("pneumonia", "cough", "dyspnea", "fever"), ("Crb65Features",)),
    _Entry("curb_65", "Pneumonia — CURB-65 (with urea)",
           "conditions.pneumonia", "curb_65_assessment",
           ("pneumonia", "cough", "dyspnea", "fever"), ("Curb65Features",)),
    _Entry("pharyngitis", "Sore throat — McIsaac / Centor score",
           "conditions.pharyngitis", "mcisaac_recommendation",
           ("sore throat", "pharyngitis"), ("PharyngitisFeatures",)),
    _Entry("uti", "UTI in women — Bent 2002 decision rule",
           "conditions.urinary_tract_infection", "uti_assessment",
           ("dysuria", "urinary symptoms", "urinary tract infection"),
           ("UtiPresentingFeatures", "UtiComplicatingFactors")),
    _Entry("start_back", "Low back pain — STarT Back stratification",
           "conditions.low_back_pain", "start_back_stratification",
           ("low back pain",), ("StartBackResponses",)),
    _Entry("lbp_red_flags", "Low back pain — red-flag screen",
           "conditions.low_back_pain", "red_flag_assessment",
           ("low back pain",), ("RedFlagFeatures",)),
    _Entry("ottawa_ankle", "Ankle injury — Ottawa Ankle Rule",
           "conditions.ankle_injury", "ottawa_ankle_assessment",
           ("ankle injury", "trauma"),
           ("AnkleAssessmentFeatures", "ApplicabilityFactors")),
    _Entry("ottawa_foot", "Midfoot injury — Ottawa Foot Rule",
           "conditions.ankle_injury", "ottawa_foot_assessment",
           ("foot injury", "trauma"),
           ("FootAssessmentFeatures", "ApplicabilityFactors")),
    _Entry("ottawa_knee", "Knee injury — Ottawa Knee Rule",
           "conditions.knee_injury", "ottawa_knee_assessment",
           ("knee injury", "trauma"),
           ("OttawaKneeFeatures", "ApplicabilityFactors")),
    _Entry("wells_dvt_2t", "DVT — Wells score (two-tier)",
           "conditions.deep_vein_thrombosis", "wells_dvt_two_tier",
           ("deep vein thrombosis", "leg swelling"), ("WellsDvtFeatures",)),
    _Entry("wells_dvt_3t", "DVT — Wells score (three-tier)",
           "conditions.deep_vein_thrombosis", "wells_dvt_three_tier",
           ("deep vein thrombosis", "leg swelling"), ("WellsDvtFeatures",)),
    _Entry("wells_pe_2t", "PE — Wells score (two-tier)",
           "conditions.pulmonary_embolism", "wells_pe_two_tier",
           ("pulmonary embolism", "dyspnea", "chest pain"), ("WellsPeFeatures",)),
    _Entry("perc", "PE — PERC rule-out", "conditions.pulmonary_embolism",
           "perc_assessment", ("pulmonary embolism", "dyspnea", "chest pain"),
           ("PercFeatures",), (("pretest_probability_is_low", "bool"),)),
    _Entry("glasgow_blatchford", "Upper GI bleeding — Glasgow-Blatchford score",
           "conditions.upper_gi_bleeding", "glasgow_blatchford_assessment",
           ("GI bleeding", "melena", "hematemesis"),
           ("GlasgowBlatchfordFeatures",)),
    _Entry("alvarado", "Appendicitis — Alvarado score (MANTRELS)",
           "conditions.appendicitis", "alvarado_assessment",
           ("abdominal pain", "appendicitis", "right lower quadrant pain"),
           ("AlvaradoFeatures",)),
    _Entry("sfsr", "Syncope — San Francisco Syncope Rule (CHESS)",
           "conditions.syncope", "sfsr_assessment", ("syncope", "collapse"),
           ("SfsrFeatures",)),
    _Entry("kdigo", "Chronic kidney disease — KDIGO staging",
           "conditions.chronic_kidney_disease", "kdigo_assessment",
           ("chronic kidney disease", "renal impairment"), ("KdigoFeatures",)),
    _Entry("four_at", "Delirium — 4AT rapid screen", "conditions.delirium",
           "four_at_assessment", ("delirium", "confusion", "altered mental status"),
           ("FourATFeatures",)),
    _Entry("nexus", "Cervical spine — NEXUS low-risk criteria",
           "conditions.cervical_spine_trauma", "nexus_assessment",
           ("cervical spine", "neck pain", "trauma"), ("NexusFeatures",)),
    _Entry("canadian_c_spine", "Cervical spine — Canadian C-Spine Rule",
           "conditions.cervical_spine_trauma", "canadian_c_spine_assessment",
           ("cervical spine", "neck pain", "trauma"),
           ("CanadianCSpineFeatures",)),
    _Entry("canadian_ct_head", "Head injury — Canadian CT Head Rule",
           "conditions.head_injury", "canadian_ct_head_assessment",
           ("head injury", "trauma"), ("CanadianCtHeadFeatures",)),
)

_BY_KEY: dict[str, _Entry] = {e.key: e for e in _REGISTRY}

_SCALAR_JSON_TYPE: dict[str, str] = {
    "bool": "boolean",
    "int": "integer",
    "float": "number",
    "str": "string",
}


def _entry(condition: str) -> _Entry:
    try:
        return _BY_KEY[condition]
    except KeyError:
        raise KeyError(
            f"unknown condition '{condition}'; see registry.condition_keys()"
        ) from None


def _field_schema(hint: Any) -> dict[str, Any]:
    if hint is bool:
        return {"type": "boolean"}
    if hint is int:
        return {"type": "integer"}
    if hint is float:
        return {"type": "number"}
    if get_origin(hint) is Literal:
        return {"type": "string", "enum": list(get_args(hint))}
    return {"type": "string"}


def _scalar_schema(json_kind: str) -> dict[str, Any]:
    return {"type": _SCALAR_JSON_TYPE.get(json_kind, "string")}


def _coerce(schema: dict[str, Any], value: Any) -> Any:
    kind = schema["type"]
    if kind == "boolean":
        return bool(value)
    if kind == "integer":
        return int(value)
    if kind == "number":
        return float(value)
    return value


def _jsonable(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    return obj


# --- Public API -------------------------------------------------------------


def condition_keys() -> tuple[str, ...]:
    """Return the keys of every algorithm in the catalog."""
    return tuple(e.key for e in _REGISTRY)


def list_conditions() -> list[dict[str, Any]]:
    """Return a lightweight catalog: key, label, and presentation tags."""
    return [
        {"key": e.key, "label": e.label, "presentations": list(e.presentations)}
        for e in _REGISTRY
    ]


def get_schema(condition: str) -> dict[str, Any]:
    """Return a JSON Schema describing the input features for a condition.

    The schema is the flattened union of the fields of the condition's feature
    dataclasses plus any scalar parameters. Every field is required.
    """
    entry = _entry(condition)
    module = importlib.import_module(entry.module)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for cls_name in entry.dataclass_params:
        cls = getattr(module, cls_name)
        hints = typing.get_type_hints(cls)
        for field in dataclasses.fields(cls):
            properties[field.name] = _field_schema(hints[field.name])
            required.append(field.name)
    for name, json_kind in entry.scalar_params:
        properties[name] = _scalar_schema(json_kind)
        required.append(name)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def describe(condition: str) -> dict[str, Any]:
    """Return the full catalog record for a condition."""
    entry = _entry(condition)
    return {
        "key": entry.key,
        "label": entry.label,
        "module": entry.module,
        "fn": entry.fn,
        "presentations": list(entry.presentations),
        "input_schema": get_schema(condition),
        "disclaimer": DISCLAIMER,
    }


def validate(condition: str, features: dict[str, Any]) -> list[str]:
    """Return a list of validation errors for `features` (empty if valid)."""
    schema = get_schema(condition)
    properties = schema["properties"]
    errors: list[str] = []
    for name in schema["required"]:
        if name not in features:
            errors.append(f"missing required input: {name}")
    for name, value in features.items():
        if name not in properties:
            errors.append(f"unknown input: {name}")
            continue
        prop = properties[name]
        if "enum" in prop and value not in prop["enum"]:
            errors.append(f"{name} must be one of {prop['enum']}")
    return errors


def missing_inputs(condition: str, features: dict[str, Any]) -> list[str]:
    """Return required input names not present in `features`."""
    schema = get_schema(condition)
    return [name for name in schema["required"] if name not in features]


def run(condition: str, features: dict[str, Any]) -> dict[str, Any]:
    """Run a condition's algorithm over structured `features`.

    Args:
        condition: A key from `condition_keys()`.
        features: A flat dict matching `get_schema(condition)`.

    Returns:
        The algorithm's result as a JSON-able dict.

    Raises:
        KeyError: If `condition` is unknown.
        ValueError: If `features` fail validation, or the algorithm rejects
            them (e.g., an out-of-range value).
    """
    entry = _entry(condition)
    errors = validate(condition, features)
    if errors:
        raise ValueError("; ".join(errors))
    module = importlib.import_module(entry.module)
    args: list[Any] = []
    for cls_name in entry.dataclass_params:
        cls = getattr(module, cls_name)
        hints = typing.get_type_hints(cls)
        kwargs = {
            field.name: _coerce(_field_schema(hints[field.name]), features[field.name])
            for field in dataclasses.fields(cls)
        }
        args.append(cls(**kwargs))
    for name, json_kind in entry.scalar_params:
        args.append(_coerce(_scalar_schema(json_kind), features[name]))
    result = getattr(module, entry.fn)(*args)
    return _jsonable(result)
