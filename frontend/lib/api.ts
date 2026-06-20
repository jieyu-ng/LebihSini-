import type {
  ConfirmedDemandResponse,
  RequestDraft,
  StructuredExtractionResponse,
} from "@/types/requirement";
import type {
  EvidenceRecordResponse,
  RecommendationOutput,
} from "@/types/recommendation";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

type ApiErrorShape = {
  error?: {
    code?: string;
    message?: string;
  };
};

async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    let payload: ApiErrorShape | null = null;
    try {
      payload = (await response.json()) as ApiErrorShape;
    } catch {
      payload = null;
    }
    throw new Error(
      payload?.error?.message ||
        `Backend request failed with status ${response.status}.`,
    );
  }

  return (await response.json()) as T;
}

export function buildExtractionPayload(draft: RequestDraft) {
  return {
    request_id: `ui-${Date.now()}`,
    source_type: draft.sourceType,
    content: draft.text,
    content_reference: draft.contentReference,
    input_language: draft.inputLanguage,
    reference_datetime: draft.referenceDatetime,
  };
}

export function extractRequest(
  draft: RequestDraft,
): Promise<StructuredExtractionResponse> {
  return apiRequest("/extract-request", {
    method: "POST",
    body: JSON.stringify(buildExtractionPayload(draft)),
  });
}

export function confirmExtraction(
  extractionId: string,
  values: Record<string, string | number | boolean | null>,
): Promise<ConfirmedDemandResponse> {
  return apiRequest(`/extractions/${extractionId}/confirm`, {
    method: "POST",
    body: JSON.stringify({
      action: "accept",
      confirmed_values: values,
      confirmed_at: new Date().toISOString(),
    }),
  });
}

export function createRecommendation(
  confirmationId: string,
): Promise<RecommendationOutput> {
  return apiRequest("/recommendations", {
    method: "POST",
    body: JSON.stringify({
      confirmed_demand_id: confirmationId,
    }),
  });
}

export function recalculateRecommendation(
  recommendationId: string,
  revisedDeadlineAt: string,
): Promise<RecommendationOutput> {
  return apiRequest(`/recommendations/${recommendationId}/recalculate`, {
    method: "POST",
    body: JSON.stringify({
      revised_deadline_at: revisedDeadlineAt,
    }),
  });
}

export function submitDecision(
  recommendationId: string,
  decisionType:
    | "approve"
    | "modify"
    | "reject"
    | "request_inspection"
    | "proceed_with_normal_procurement",
) {
  return apiRequest<{
    decision: { decision_id: string };
    evidence_record: EvidenceRecordResponse;
  }>(`/recommendations/${recommendationId}/decision`, {
    method: "POST",
    body: JSON.stringify({
      decision_type: decisionType,
      actor_reference: "site.supervisor@lebihsini.demo",
      decided_at: new Date().toISOString(),
      override_notes:
        decisionType === "approve"
          ? "Approved after reviewing recommendation details."
          : "",
    }),
  });
}

export function fetchEvidenceRecord(
  recordId: string,
): Promise<EvidenceRecordResponse> {
  return apiRequest(`/evidence-records/${recordId}`);
}

export function fetchHealth() {
  return apiRequest<{
    provider_mode: string;
    provider_model: string;
    storage_mode: string;
  }>("/health");
}
