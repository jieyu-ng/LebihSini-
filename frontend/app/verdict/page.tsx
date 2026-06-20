"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Badge from "@/components/ui/badge";
import Card from "@/components/ui/card";
import Container from "@/components/ui/container";
import PageHeader from "@/components/ui/pageHeader";
import { recalculateRecommendation, submitDecision } from "@/lib/api";
import { sessionStore } from "@/lib/session";
import type { RecommendationOutput } from "@/types/recommendation";

const URGENT_DEADLINE = "2026-06-21T09:30:00+08:00";

export default function VerdictPage() {
  const router = useRouter();
  const [recommendation, setRecommendation] = useState<RecommendationOutput | null>(null);
  const [error, setError] = useState("");
  const [recalculating, setRecalculating] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadStoredRecommendation() {
      const stored = sessionStore.getRecommendation();
      await Promise.resolve();

      if (!active) {
        return;
      }

      if (stored) {
        setRecommendation(stored);
        return;
      }

      setError("No recommendation was found. Please complete the earlier steps first.");
    }

    loadStoredRecommendation();

    return () => {
      active = false;
    };
  }, []);

  async function handleUrgency() {
    if (!recommendation) return;
    try {
      setRecalculating(true);
      const updated = await recalculateRecommendation(
        recommendation.recommendation_id,
        URGENT_DEADLINE,
      );
      sessionStore.setRecommendation(updated);
      setRecommendation(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to recalculate urgency.");
    } finally {
      setRecalculating(false);
    }
  }

  async function handleDecision(
    decisionType:
      | "approve"
      | "request_inspection"
      | "reject"
      | "proceed_with_normal_procurement",
  ) {
    if (!recommendation) return;
    try {
      setSubmitting(true);
      const result = await submitDecision(recommendation.recommendation_id, decisionType);
      sessionStore.setEvidence(result.evidence_record);
      router.push("/evidence");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to submit the decision.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Container>
      <div className="space-y-6">
        <PageHeader
          title="GreenProof Verdict"
          subtitle="Compare cost, carbon, urgency, exclusions, and approval actions from the backend recommendation."
        />

        {error ? (
          <Card>
            <div className="text-sm text-red-600">{error}</div>
          </Card>
        ) : null}

        {recommendation ? (
          <>
            <Card>
              <div className="flex justify-between items-center gap-3">
                <div>
                  <div className="font-medium">Recommendation verdict</div>
                  <div className="text-sm text-gray-500">
                    {recommendation.verdict}
                  </div>
                </div>
                <Badge
                  label={recommendation.deadline_met ? "Deadline met" : "Manual review"}
                  type={recommendation.deadline_met ? "green" : "red"}
                />
              </div>
            </Card>

            <Card>
              <h2 className="text-sm font-medium mb-3">Plan comparison</h2>
              <div className="space-y-2 text-sm text-gray-700">
                <div>
                  Selected materials:{" "}
                  {recommendation.selected_material_resources
                    .map((item) => `${item.site_name}: ${item.quantity_units}`)
                    .join(", ")}
                </div>
                <div>Supplier F shortfall: {recommendation.supplier_shortfall_units}</div>
                <div>
                  Equipment: {recommendation.selected_equipment?.site_name || "No equipment selected"}
                </div>
                <div>
                  Net saving: RM {Number(recommendation.cost_breakdown.net_saving_myr).toFixed(2)}
                </div>
                <div>
                  Carbon avoided:{" "}
                  {Number(recommendation.carbon_breakdown.net_carbon_avoided_kgco2e).toFixed(2)} kgCO2e
                </div>
              </div>
            </Card>

            <Card>
              <h2 className="text-sm font-medium mb-3">Urgency</h2>
              <div className="space-y-3">
                <div className="text-sm text-gray-600">
                  Use backend recalculation to test the prepared urgent three-hour scenario.
                </div>
                <button
                  onClick={handleUrgency}
                  disabled={recalculating}
                  className="w-full border border-black rounded-xl py-3 text-sm font-medium disabled:opacity-50"
                >
                  {recalculating ? "Recalculating..." : "Switch to three-hour urgency"}
                </button>
              </div>
            </Card>

            <Card>
              <h2 className="text-sm font-medium mb-3">Exclusions and conditions</h2>
              <div className="space-y-3 text-sm text-gray-600">
                {recommendation.excluded_resources.map((resource) => (
                  <div key={resource.resource_id}>
                    <div className="font-medium text-gray-800">{resource.site_name}</div>
                    <div>{resource.reason_text}</div>
                  </div>
                ))}
                {recommendation.conditions.map((condition, index) => (
                  <div key={`${condition}-${index}`}>{condition}</div>
                ))}
              </div>
            </Card>

            <div className="space-y-3">
              <button
                onClick={() => handleDecision("approve")}
                disabled={submitting}
                className="w-full bg-black text-white py-3 rounded-xl font-medium disabled:opacity-50"
              >
                Approve Plan
              </button>
              <button
                onClick={() => handleDecision("request_inspection")}
                disabled={submitting}
                className="w-full border border-black py-3 rounded-xl font-medium"
              >
                Request Inspection
              </button>
              <button
                onClick={() => handleDecision("proceed_with_normal_procurement")}
                disabled={submitting}
                className="w-full border border-gray-300 py-3 rounded-xl font-medium"
              >
                Proceed with Normal Procurement
              </button>
              <button
                onClick={() => handleDecision("reject")}
                disabled={submitting}
                className="w-full text-sm text-gray-500"
              >
                Reject
              </button>
            </div>
          </>
        ) : null}
      </div>
    </Container>
  );
}
