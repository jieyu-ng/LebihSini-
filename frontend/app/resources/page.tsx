"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Card from "@/components/ui/card";
import Container from "@/components/ui/container";
import PageHeader from "@/components/ui/pageHeader";
import Badge from "@/components/ui/badge";
import { createRecommendation } from "@/lib/api";
import { sessionStore } from "@/lib/session";
import type { RecommendationOutput } from "@/types/recommendation";

export default function ResourcesPage() {
  const router = useRouter();
  const [recommendation, setRecommendation] = useState<RecommendationOutput | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function loadRecommendation() {
      const confirmation = sessionStore.getConfirmation();
      if (!confirmation?.confirmation_id) {
        if (active) {
          setError("No confirmed demand was found. Please return to the confirmation step.");
        }
        return;
      }
      try {
        const result = await createRecommendation(confirmation.confirmation_id);
        if (!active) return;
        sessionStore.setRecommendation(result);
        setRecommendation(result);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Unable to generate the recommendation.");
      }
    }
    loadRecommendation();
    return () => {
      active = false;
    };
  }, []);

  return (
    <Container>
      <div className="space-y-6">
        <PageHeader
          title="Resource Discovery"
          subtitle="Verified supply, fallback shortfall, and excluded resources from the backend recommendation."
        />

        {error ? (
          <Card>
            <div className="space-y-3">
              <div className="text-sm text-red-600">{error}</div>
              <button
                onClick={() => router.push("/confirm")}
                className="w-full bg-black text-white py-3 rounded-xl"
              >
                Back to Confirmation
              </button>
            </div>
          </Card>
        ) : null}

        {!recommendation && !error ? (
          <Card>
            <div className="text-sm text-gray-600">
              Generating the live GreenProof recommendation from the backend...
            </div>
          </Card>
        ) : null}

        {recommendation ? (
          <>
            <div className="space-y-3">
              {recommendation.selected_material_resources.map((resource) => (
                <Card key={resource.resource_id}>
                  <div className="flex justify-between items-start gap-3">
                    <div>
                      <div className="font-medium">{resource.site_name}</div>
                      <div className="text-xs text-gray-500">
                        {resource.quantity_units} units selected
                      </div>
                    </div>
                    <Badge
                      label={resource.inspection_required ? "Inspection required" : "Ready"}
                      type={resource.inspection_required ? "amber" : "green"}
                    />
                  </div>
                </Card>
              ))}

              {recommendation.selected_equipment ? (
                <Card>
                  <div className="flex justify-between items-start gap-3">
                    <div>
                      <div className="font-medium">{recommendation.selected_equipment.site_name}</div>
                      <div className="text-xs text-gray-500">
                        Equipment: {recommendation.selected_equipment.category}
                      </div>
                    </div>
                    <Badge label="Equipment selected" type="green" />
                  </div>
                </Card>
              ) : null}

              <Card>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium">Supplier F</div>
                    <div className="text-xs text-gray-500">
                      Remaining shortfall fulfilled by new supply
                    </div>
                  </div>
                  <div className="text-sm font-semibold">
                    {recommendation.supplier_shortfall_units} units
                  </div>
                </div>
              </Card>
            </div>

            <Card>
              <h2 className="text-sm font-medium mb-3">Excluded from automatic recommendation</h2>
              <div className="space-y-2 text-sm text-gray-600">
                {recommendation.excluded_resources.map((resource) => (
                  <div key={resource.resource_id}>
                    <div className="font-medium text-gray-800">{resource.site_name}</div>
                    <div>{resource.reason_text}</div>
                  </div>
                ))}
              </div>
            </Card>

            <button
              onClick={() => router.push("/verdict")}
              className="w-full bg-black text-white py-3 rounded-xl font-medium"
            >
              Review Verdict
            </button>
          </>
        ) : null}
      </div>
    </Container>
  );
}
