export type InputSourceType =
  | "typed_text"
  | "voice_note"
  | "image"
  | "handwritten_list"
  | "quotation_document"
  | "whatsapp_screenshot"
  | "resource_photo";

export type ConfidenceLabel = "high" | "medium" | "low";

export type ConfirmationAction =
  | "accept"
  | "edit"
  | "provide"
  | "reject"
  | "retake"
  | "manual_review";

export interface RequestDraft {
  text: string;
  inputLanguage: string;
  sourceType: InputSourceType;
  contentReference: string;
  referenceDatetime: string;
  isDemoFixture: boolean;
  fixtureLabel?: string;
}

export interface ExtractedField {
  field_name: string;
  extracted_value: string | number | boolean | null;
  confidence_score: number;
  confidence_label: ConfidenceLabel;
  confirmation_required: boolean;
  warning?: string | null;
}

export interface MissingFieldWarning {
  field_name: string;
  message: string;
  critical: boolean;
}

export interface ProcessingWarning {
  code: string;
  message: string;
  field_name?: string | null;
}

export interface StructuredExtractionResponse {
  extraction_id: string;
  request_id: string;
  source_type: InputSourceType;
  detected_language: string;
  extracted_fields: ExtractedField[];
  missing_fields: MissingFieldWarning[];
  missing_critical_fields: MissingFieldWarning[];
  warnings: ProcessingWarning[];
  can_proceed_to_confirmation: boolean;
  requires_manual_review: boolean;
  normalized_demand: Record<string, string | number | boolean | null>;
  confirmation_status: string;
  provider_metadata: {
    provider_name: string;
    model_name: string;
    model_version: string;
    request_id: string;
    operation_type?: string | null;
    status: string;
  };
}

export interface ConfirmedDemandResponse {
  confirmation_id: string;
  request_id: string;
  status: string;
  warnings: ProcessingWarning[];
  confirmed_demand?: Record<string, string | number | boolean | null> | null;
}
