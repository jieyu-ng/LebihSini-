"""Deterministic explanation helpers.

These helpers do not certify safety and do not perform arithmetic.
"""

from __future__ import annotations

from lebihsini_greenproof.explanations import EXPLANATION_TEXT


def dedupe_messages(messages: list[str]) -> list[str]:
    return list(dict.fromkeys(messages))


def build_selection_reason(material_count: int, supplier_shortfall_units: int) -> list[str]:
    reasons: list[str] = []
    if material_count > 0 and supplier_shortfall_units == 0:
        reasons.append(EXPLANATION_TEXT["resource_selected"])
    elif material_count > 0:
        reasons.append(EXPLANATION_TEXT["partial_reuse_recommended"])
    else:
        reasons.append(EXPLANATION_TEXT["normal_procurement_recommended"])
    if supplier_shortfall_units > 0:
        reasons.append(EXPLANATION_TEXT["supplier_selected"])
    return dedupe_messages(reasons)
