from __future__ import annotations

from lebihsini_greenproof.constraints import MaterialCandidateEvaluation


def rank_material_candidates(
    evaluations: list[MaterialCandidateEvaluation],
) -> list[MaterialCandidateEvaluation]:
    eligible = [item for item in evaluations if item.eligible]
    return sorted(
        eligible,
        key=lambda item: (
            round(item.landed_cost_per_unit_myr or 0.0, 6),
            -(item.slack_minutes or 0),
            round(item.transport_carbon_kgco2e or 0.0, 6),
            -item.resource.quantity_units,
            item.resource.resource_id,
        ),
    )
