export interface ResourceListItem {
  resource_id: string;
  site_id: string;
  site_name: string;
  resource_type: "material" | "equipment";
  category: string;
  quantity_units?: number;
  status: string;
  risk_category: string;
  verification_status: string;
  automatic_matching_eligibility: boolean;
}
