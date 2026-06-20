import type {
  ConfirmedDemandResponse,
  RequestDraft,
  StructuredExtractionResponse,
} from "@/types/requirement";
import type {
  EvidenceRecordResponse,
  RecommendationOutput,
} from "@/types/recommendation";

const KEYS = {
  draft: "greenproof:draft",
  extraction: "greenproof:extraction",
  confirmation: "greenproof:confirmation",
  recommendation: "greenproof:recommendation",
  evidence: "greenproof:evidence",
};

function read<T>(key: string): T | null {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = window.localStorage.getItem(key);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function write<T>(key: string, value: T) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(key, JSON.stringify(value));
}

export const sessionStore = {
  getDraft: () => read<RequestDraft>(KEYS.draft),
  setDraft: (value: RequestDraft) => write(KEYS.draft, value),
  getExtraction: () => read<StructuredExtractionResponse>(KEYS.extraction),
  setExtraction: (value: StructuredExtractionResponse) => write(KEYS.extraction, value),
  getConfirmation: () => read<ConfirmedDemandResponse>(KEYS.confirmation),
  setConfirmation: (value: ConfirmedDemandResponse) => write(KEYS.confirmation, value),
  getRecommendation: () => read<RecommendationOutput>(KEYS.recommendation),
  setRecommendation: (value: RecommendationOutput) => write(KEYS.recommendation, value),
  getEvidence: () => read<EvidenceRecordResponse>(KEYS.evidence),
  setEvidence: (value: EvidenceRecordResponse) => write(KEYS.evidence, value),
};
