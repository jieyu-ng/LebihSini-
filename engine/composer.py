from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

try:  # Works when files are imported as a package or copied into the same folder.
    from .constraints import (
        as_float,
        as_int,
        filter_material_resources,
        get_dimensions_mm,
        norm,
        risk_level,
    )
    from .equipment import equipment_request_from_demand, select_equipment
except ImportError:  # pragma: no cover
    from constraints import (
        as_float,
        as_int,
        filter_material_resources,
        get_dimensions_mm,
        norm,
        risk_level,
    )
    from equipment import equipment_request_from_demand, select_equipment


URGENCY_TO_DEADLINE_HOURS = {
    "three_days": 72,
    "3_days": 72,
    "tomorrow": 24,
    "six_hours": 6,
    "6_hours": 6,
    "three_hours": 3,
    "3_hours": 3,
}

DEFAULT_ASSUMPTIONS = {
    "transport_cost_per_km": 5.0,
    "vehicle_kg_co2e_per_km": 0.27,
    "new_material_kg_co2e_per_unit": 0.82,
    "reuse_handling_kg_co2e_per_unit": 0.03,
    "inspection_cost_per_amber_resource": 50.0,
    "platform_fee_rate": 0.03,
    "worker_idle_cost_per_hour": 40.0,
    "route_extra_stop_factor": 0.45,
    "max_cost_premium_pct": 0.0,
}


def with_urgency(demand: dict[str, Any], urgency: str | None) -> dict[str, Any]:
    updated = dict(demand)
    if urgency:
        key = norm(urgency)
        if key in URGENCY_TO_DEADLINE_HOURS:
            updated["deadline_hours"] = URGENCY_TO_DEADLINE_HOURS[key]
            updated["urgency"] = key
    updated.setdefault("deadline_hours", 24)
    return updated


def material_rank(resource: dict[str, Any], result: Any) -> tuple[float, float, float, int, float]:
    """Lower is better. Keeps the greedy composer transparent and deterministic."""
    risk_penalty = {"green": 0.0, "amber": 1.0, "red": 99.0}.get(risk_level(resource.get("risk", resource.get("risk_category"))), 1.0)
    unit_price = as_float(resource.get("price_per_unit", resource.get("transfer_price_per_unit", 0)), 0.0)
    distance = as_float(resource.get("distance_km", 0), 0.0)
    quantity_bonus = -as_int(resource.get("quantity", resource.get("available_quantity", 0)), 0)
    confidence_penalty = 1.0 - as_float(resource.get("confidence", resource.get("ai_confidence", 1.0)), 1.0)
    warning_penalty = len(getattr(result, "warnings", [])) * 0.2
    return (risk_penalty + warning_penalty, unit_price, distance, quantity_bonus, confidence_penalty)


def estimate_combined_route_distance_km(
    selected_materials: list[dict[str, Any]],
    selected_equipment: dict[str, Any] | None,
    supplier_shortfall_qty: int,
    supplier: dict[str, Any],
    assumptions: dict[str, float],
) -> float:
    """
    Lightweight demo route estimate:
    - The farthest selected stop is the main route spine.
    - Other stops add only a fraction because pickups are combined.
    - Supplier distance is included only when there is a new-material shortfall.
    """
    distances = [as_float(item["resource"].get("distance_km", 0), 0.0) for item in selected_materials]

    if selected_equipment and norm(selected_equipment.get("equipment_id")) != "commercial_rental_fallback":
        distances.append(as_float(selected_equipment.get("distance_km", 0), 0.0))

    if supplier_shortfall_qty > 0:
        distances.append(as_float(supplier.get("distance_km", supplier.get("delivery_distance_km", 0)), 0.0))

    if not distances:
        return 0.0

    distances = sorted(distances, reverse=True)
    main_spine = distances[0]
    extra_stops = sum(distances[1:]) * as_float(assumptions.get("route_extra_stop_factor"), 0.45)
    return round(main_spine + extra_stops, 2)


def estimate_worker_delay_cost(demand: dict[str, Any], route_distance_km: float, assumptions: dict[str, float]) -> float:
    """
    Simple delay proxy. If route travel/handling exceeds the available deadline buffer, count excess hours.
    This keeps the demo deterministic without pretending to be a full scheduling solver.
    """
    deadline_h = as_float(demand.get("deadline_hours", 24), 24.0)
    worker_start_h = as_float(demand.get("worker_start_in_hours", deadline_h), deadline_h)
    avg_speed_kmh = as_float(demand.get("average_transport_speed_kmh", 35), 35.0)
    handling_h = as_float(demand.get("handling_hours", 1.0), 1.0)
    route_h = (route_distance_km / max(avg_speed_kmh, 1.0)) + handling_h
    excess_h = max(0.0, route_h - max(worker_start_h, 0.0))
    return round(excess_h * as_float(assumptions.get("worker_idle_cost_per_hour"), 40.0), 2)


def calculate_baseline(
    demand: dict[str, Any],
    supplier: dict[str, Any],
    commercial_equipment: dict[str, Any] | None,
    assumptions: dict[str, float],
) -> dict[str, Any]:
    required_qty = as_int(demand.get("quantity"), 0)
    supplier_unit_price = as_float(supplier.get("unit_price", supplier.get("price_per_unit", 0)), 0.0)
    supplier_delivery_cost = as_float(supplier.get("delivery_fee", supplier.get("transport_cost", 0)), 0.0)
    supplier_distance = as_float(supplier.get("distance_km", supplier.get("delivery_distance_km", 0)), 0.0)

    equipment_cost = 0.0
    req = equipment_request_from_demand(demand)
    if req:
        duration_days = as_float(req.get("duration_days", 1), 1.0)
        rate = as_float(
            (commercial_equipment or {}).get("rate_per_day", req.get("commercial_rate_per_day", supplier.get("commercial_equipment_rate_per_day", 120))),
            120.0,
        )
        equipment_cost = duration_days * rate

    material_cost = required_qty * supplier_unit_price
    transport_cost = supplier_delivery_cost
    total_cost = material_cost + transport_cost + equipment_cost
    carbon = (
        required_qty * as_float(assumptions.get("new_material_kg_co2e_per_unit"), 0.82)
        + supplier_distance * as_float(assumptions.get("vehicle_kg_co2e_per_km"), 0.27)
    )

    return {
        "plan_name": "Normal procurement",
        "new_material_quantity": required_qty,
        "reused_quantity": 0,
        "material_cost": round(material_cost, 2),
        "transport_cost": round(transport_cost, 2),
        "equipment_cost": round(equipment_cost, 2),
        "worker_delay_cost": 0.0,
        "platform_fee": 0.0,
        "inspection_cost": 0.0,
        "total_cost": round(total_cost, 2),
        "estimated_kg_co2e": round(carbon, 2),
        "deadline_status": "met",
        "sources_count": 1,
    }


def calculate_greenproof_costs(
    demand: dict[str, Any],
    selected_materials: list[dict[str, Any]],
    supplier_shortfall_qty: int,
    selected_equipment: dict[str, Any] | None,
    equipment_source_type: str,
    supplier: dict[str, Any],
    assumptions: dict[str, float],
) -> dict[str, Any]:
    reuse_material_cost = sum(
        item["selected_quantity"] * as_float(item["resource"].get("price_per_unit", item["resource"].get("transfer_price_per_unit", 0)), 0.0)
        for item in selected_materials
    )
    supplier_unit_price = as_float(supplier.get("unit_price", supplier.get("price_per_unit", 0)), 0.0)
    new_material_cost = supplier_shortfall_qty * supplier_unit_price

    amber_count = sum(1 for item in selected_materials if risk_level(item["resource"].get("risk", item["resource"].get("risk_category"))) == "amber")
    inspection_cost = amber_count * as_float(assumptions.get("inspection_cost_per_amber_resource"), 50.0)

    route_distance_km = estimate_combined_route_distance_km(selected_materials, selected_equipment, supplier_shortfall_qty, supplier, assumptions)
    transport_cost = route_distance_km * as_float(assumptions.get("transport_cost_per_km"), 5.0)

    req = equipment_request_from_demand(demand)
    equipment_cost = 0.0
    if req and selected_equipment:
        duration_days = as_float(req.get("duration_days", 1), 1.0)
        rate = as_float(selected_equipment.get("rate_per_day", selected_equipment.get("price_per_day", 0)), 0.0)
        equipment_cost = duration_days * rate

    subtotal_before_fee = reuse_material_cost + new_material_cost + transport_cost + inspection_cost + equipment_cost
    platform_fee = subtotal_before_fee * as_float(assumptions.get("platform_fee_rate"), 0.03)
    worker_delay_cost = estimate_worker_delay_cost(demand, route_distance_km, assumptions)
    total_cost = subtotal_before_fee + platform_fee + worker_delay_cost

    reused_qty = sum(item["selected_quantity"] for item in selected_materials)
    carbon = (
        supplier_shortfall_qty * as_float(assumptions.get("new_material_kg_co2e_per_unit"), 0.82)
        + reused_qty * as_float(assumptions.get("reuse_handling_kg_co2e_per_unit"), 0.03)
        + route_distance_km * as_float(assumptions.get("vehicle_kg_co2e_per_km"), 0.27)
    )

    return {
        "plan_name": "GreenProof plan",
        "new_material_quantity": supplier_shortfall_qty,
        "reused_quantity": reused_qty,
        "reuse_material_cost": round(reuse_material_cost, 2),
        "new_material_cost": round(new_material_cost, 2),
        "transport_cost": round(transport_cost, 2),
        "equipment_cost": round(equipment_cost, 2),
        "inspection_cost": round(inspection_cost, 2),
        "platform_fee": round(platform_fee, 2),
        "worker_delay_cost": round(worker_delay_cost, 2),
        "total_cost": round(total_cost, 2),
        "estimated_kg_co2e": round(carbon, 2),
        "route_distance_km": route_distance_km,
        "transport_trips": 1 if (selected_materials or selected_equipment or supplier_shortfall_qty > 0) else 0,
        "sources_count": len(selected_materials) + (1 if supplier_shortfall_qty > 0 else 0),
        "equipment_source_type": equipment_source_type,
        "deadline_status": "met",
    }


def build_verdict(
    baseline: dict[str, Any],
    greenproof: dict[str, Any],
    selected_materials: list[dict[str, Any]],
    excluded_count: int,
    assumptions: dict[str, float],
) -> dict[str, Any]:
    saving = round(as_float(baseline["total_cost"]) - as_float(greenproof["total_cost"]), 2)
    carbon_avoided = round(as_float(baseline["estimated_kg_co2e"]) - as_float(greenproof["estimated_kg_co2e"]), 2)
    required_premium_limit = as_float(baseline["total_cost"]) * as_float(assumptions.get("max_cost_premium_pct"), 0.0)

    if not selected_materials:
        recommendation = "Normal procurement recommended"
        confidence = "Medium"
        summary = "No suitable reusable material passed the hard constraints."
    elif carbon_avoided < 0:
        recommendation = "Normal procurement recommended"
        confidence = "Medium"
        summary = "Reuse is rejected because added transport/handling makes net carbon impact worse."
    elif saving + required_premium_limit < 0:
        recommendation = "Normal procurement recommended"
        confidence = "Medium"
        summary = "Reuse is feasible, but the landed cost is higher than normal procurement."
    elif greenproof["new_material_quantity"] == 0:
        recommendation = "Full reuse recommended"
        confidence = "High"
        summary = "Reusable resources can fulfil the full material requirement within the constraints."
    else:
        recommendation = "Partial reuse recommended"
        confidence = "High" if saving >= 0 and carbon_avoided >= 0 else "Medium"
        summary = "Use verified nearby surplus first and purchase only the remaining shortfall."

    return {
        "recommendation": recommendation,
        "summary": summary,
        "confidence": confidence,
        "net_saving_rm": saving,
        "working_capital_protected_rm": max(0.0, saving),
        "net_carbon_avoided_kg_co2e": carbon_avoided,
        "new_material_avoided_units": greenproof["reused_quantity"],
        "uncertain_resources_excluded": excluded_count,
    }


def compose_greenproof_plan(
    demand: dict[str, Any],
    material_resources: list[dict[str, Any]],
    equipment_resources: list[dict[str, Any]] | None = None,
    supplier: dict[str, Any] | None = None,
    *,
    urgency: str | None = None,
    assumptions: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Main hackathon function.
    Builds a complete, explainable plan from multiple reusable sources + supplier fallback + idle equipment.
    """
    demand = with_urgency(demand, urgency)
    assumptions = {**DEFAULT_ASSUMPTIONS, **(assumptions or {})}
    supplier = supplier or {
        "supplier_id": "supplier-fallback",
        "source_name": "Supplier fallback",
        "unit_price": 0,
        "delivery_fee": 0,
        "distance_km": 0,
    }
    equipment_resources = equipment_resources or []

    required_qty = as_int(demand.get("quantity", 0), 0)
    if required_qty <= 0:
        raise ValueError("Demand quantity must be greater than zero.")

    allowed, rejected = filter_material_resources(material_resources, demand)
    ranked_allowed = sorted(allowed, key=lambda pair: material_rank(pair[0], pair[1]))

    remaining_qty = required_qty
    selected_materials: list[dict[str, Any]] = []

    for resource, result in ranked_allowed:
        if remaining_qty <= 0:
            break
        available_qty = as_int(resource.get("quantity", resource.get("available_quantity", 0)), 0)
        selected_qty = min(remaining_qty, available_qty)
        if selected_qty <= 0:
            continue
        selected_materials.append(
            {
                "resource_id": resource.get("resource_id") or resource.get("id"),
                "site_id": resource.get("site_id") or resource.get("site") or resource.get("site_name"),
                "site_name": resource.get("site_name") or resource.get("site_id") or resource.get("site"),
                "selected_quantity": selected_qty,
                "available_quantity": available_qty,
                "category": resource.get("category"),
                "dimensions_mm": list(get_dimensions_mm(resource)),
                "product_code": resource.get("product_code"),
                "risk": risk_level(resource.get("risk", resource.get("risk_category"))),
                "distance_km": as_float(resource.get("distance_km", 0), 0.0),
                "price_per_unit": as_float(resource.get("price_per_unit", resource.get("transfer_price_per_unit", 0)), 0.0),
                "conditions": result.warnings,
                "reasons": result.reasons,
                "resource": resource,
            }
        )
        remaining_qty -= selected_qty

    supplier_shortfall_qty = max(0, remaining_qty)

    commercial_equipment = supplier.get("commercial_equipment") if isinstance(supplier.get("commercial_equipment"), dict) else None
    equipment_decision = select_equipment(equipment_resources, demand, fallback=commercial_equipment)
    selected_equipment = equipment_decision.selected

    baseline = calculate_baseline(demand, supplier, commercial_equipment, assumptions)
    greenproof = calculate_greenproof_costs(
        demand,
        selected_materials,
        supplier_shortfall_qty,
        selected_equipment,
        equipment_decision.source_type,
        supplier,
        assumptions,
    )
    verdict = build_verdict(baseline, greenproof, selected_materials, len(rejected) + len(equipment_decision.excluded), assumptions)

    # Remove full raw resource objects from the public selected list to keep API response clean.
    public_selected = []
    for item in selected_materials:
        clean = dict(item)
        clean.pop("resource", None)
        public_selected.append(clean)

    supplier_shortfall = None
    if supplier_shortfall_qty > 0:
        supplier_shortfall = {
            "supplier_id": supplier.get("supplier_id") or supplier.get("id") or "supplier-fallback",
            "source_name": supplier.get("source_name") or supplier.get("name") or "Supplier fallback",
            "quantity": supplier_shortfall_qty,
            "unit_price": as_float(supplier.get("unit_price", supplier.get("price_per_unit", 0)), 0.0),
            "reason": "Reusable resources did not fully cover the required quantity, so supplier fills the shortfall.",
        }

    comparison = {
        "baseline": baseline,
        "greenproof": greenproof,
        "difference": {
            "cost_saving_rm": verdict["net_saving_rm"],
            "carbon_avoided_kg_co2e": verdict["net_carbon_avoided_kg_co2e"],
            "new_material_avoided_units": verdict["new_material_avoided_units"],
            "new_material_reduction_pct": round((verdict["new_material_avoided_units"] / required_qty) * 100, 1),
        },
    }

    return {
        "recommendation_id": str(uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "demand": {
            "requirement_id": demand.get("requirement_id") or demand.get("id"),
            "material_category": demand.get("material_category") or demand.get("category"),
            "quantity": required_qty,
            "dimensions_mm": list(get_dimensions_mm(demand)),
            "product_code": demand.get("product_code"),
            "colour": demand.get("colour") or demand.get("color"),
            "deadline_hours": as_float(demand.get("deadline_hours"), 24.0),
            "urgency": demand.get("urgency"),
            "risk_tolerance": risk_level(demand.get("risk_tolerance", "amber")),
        },
        "verdict": verdict,
        "selected_materials": public_selected,
        "supplier_shortfall": supplier_shortfall,
        "equipment": equipment_decision.to_dict(),
        "excluded_resources": rejected,
        "comparison": comparison,
        "assumptions": assumptions,
        "evidence_record": {
            "record_type": "GreenProof Evidence Record",
            "not_a_certificate": True,
            "resources_considered": len(material_resources) + len(equipment_resources),
            "materials_selected": len(public_selected),
            "materials_excluded": len(rejected),
            "equipment_excluded": len(equipment_decision.excluded),
            "human_approval_required": True,
            "message": "AI structures evidence; deterministic rules calculate the plan; contractor approves the final decision.",
        },
    }


if __name__ == "__main__":
    demo_demand = {
        "requirement_id": "REQ-SITE-C-001",
        "material_category": "porcelain_tile",
        "product_code": "GT-600-GREY",
        "dimensions_mm": [600, 600],
        "colour": "grey",
        "quantity": 500,
        "deadline_hours": 24,
        "max_distance_km": 25,
        "risk_tolerance": "amber",
        "equipment": {"type": "tile_cutter", "duration_days": 2, "start_in_hours": 24, "commercial_rate_per_day": 150},
    }
    demo_materials = [
        {"resource_id": "A-TILE", "site_id": "Site A", "site_name": "Puchong Utama", "category": "porcelain_tile", "product_code": "GT-600-GREY", "dimensions_mm": [600, 600], "colour": "grey", "quantity": 300, "distance_km": 8, "travel_minutes": 25, "price_per_unit": 4, "risk": "green", "label_readable": True, "confidence": 0.96, "packaging_status": "sealed"},
        {"resource_id": "B-TILE", "site_id": "Site B", "site_name": "Bandar Puteri", "category": "porcelain_tile", "product_code": "GT-600-GREY", "dimensions_mm": [600, 600], "colour": "grey", "quantity": 130, "distance_km": 12, "travel_minutes": 40, "price_per_unit": 3.5, "risk": "amber", "label_readable": True, "confidence": 0.84, "packaging_status": "opened"},
        {"resource_id": "E-TILE", "site_id": "Site E", "site_name": "Kinrara", "category": "porcelain_tile", "dimensions_mm": [600, 600], "colour": "grey", "quantity": 100, "distance_km": 5, "travel_minutes": 20, "price_per_unit": 2, "risk": "amber", "label_readable": False, "confidence": 0.60, "packaging_status": "outdoor_storage"},
    ]
    demo_equipment = [
        {"equipment_id": "D-CUTTER", "site_id": "Site D", "source_name": "Subang Jaya", "type": "tile_cutter", "distance_km": 10, "travel_minutes": 35, "available_from_hours": 0, "available_until_hours": 72, "maintenance_status": "ok", "maintenance_record_present": True, "rate_per_day": 80},
    ]
    demo_supplier = {
        "supplier_id": "Supplier F",
        "source_name": "Petaling Jaya supplier",
        "unit_price": 12,
        "delivery_fee": 120,
        "distance_km": 14,
        "commercial_equipment": {"equipment_id": "COMMERCIAL-CUTTER", "type": "tile_cutter", "source_name": "Commercial rental", "rate_per_day": 150},
    }

    import json

    print(json.dumps(compose_greenproof_plan(demo_demand, demo_materials, demo_equipment, demo_supplier), indent=2))
