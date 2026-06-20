export interface SelectedMaterialResource {
  resource_id: string;
  site_id: string;
  site_name: string;
  quantity_units: number;
  transfer_price_myr_per_unit: number;
  distance_km: number;
  inspection_required: boolean;
  conditions: string[];
}

export interface SelectedEquipment {
  resource_id: string;
  site_id: string;
  site_name: string;
  category: string;
  duration_days: number;
  rental_cost_myr: number;
  is_commercial_fallback: boolean;
  conditions: string[];
}

export interface ExcludedResource {
  resource_id: string;
  site_id: string;
  site_name: string;
  reason_code: string;
  reason_text: string;
  confidence: number;
  evidence_notes: string[];
}

export interface RecommendationOutput {
  recommendation_id: string;
  verdict: string;
  deadline_met: boolean;
  selected_material_resources: SelectedMaterialResource[];
  selected_equipment: SelectedEquipment | null;
  excluded_resources: ExcludedResource[];
  supplier_shortfall_units: number;
  quantity_fulfilled_units: number;
  cost_breakdown: {
    normal_procurement_baseline_myr: number;
    greenproof_total_myr: number;
    net_saving_myr: number;
  } & Record<string, number | string | string[]>;
  carbon_breakdown: {
    baseline_carbon_kgco2e: number;
    greenproof_carbon_kgco2e: number;
    net_carbon_avoided_kgco2e: number;
  } & Record<string, number | string | string[]>;
  conditions: string[];
  reasons: string[];
  assumptions: string[];
  confidence: number;
  calculation_version: string;
}

export interface EvidenceRecordResponse {
  record_id: string;
  name: string;
  generated_at: string;
  storage_mode: string;
  original_request_reference?: string | null;
  confirmed_demand: Record<string, string | number | boolean | null>;
  resources_selected: SelectedMaterialResource[];
  selected_equipment: SelectedEquipment | null;
  resources_excluded: ExcludedResource[];
  cost_comparison: Record<string, string | number | string[]>;
  carbon_comparison: Record<string, string | number | string[]>;
  user_decision: {
    decision_id: string;
    decision_type: string;
    actor_reference: string;
    decided_at: string;
    override_notes: string;
  };
  final_approved_plan: Record<string, string | number | boolean | string[] | object>;
}
