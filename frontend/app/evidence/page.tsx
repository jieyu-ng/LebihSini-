"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Card from "@/components/ui/card";
import Container from "@/components/ui/container";
import PageHeader from "@/components/ui/pageHeader";
import { fetchEvidenceRecord } from "@/lib/api";
import { sessionStore } from "@/lib/session";
import type { EvidenceRecordResponse } from "@/types/recommendation";

export default function EvidencePage() {
  const router = useRouter();
  const [record, setRecord] = useState<EvidenceRecordResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function loadRecord() {
      const stored = sessionStore.getEvidence();
      if (!stored?.record_id) {
        if (active) {
          setError("No GreenProof Evidence Record was found.");
        }
        return;
      }
      try {
        const result = await fetchEvidenceRecord(stored.record_id);
        if (!active) return;
        sessionStore.setEvidence(result);
        setRecord(result);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Unable to load the Evidence Record.");
      }
    }
    loadRecord();
    return () => {
      active = false;
    };
  }, []);

  return (
    <Container>
      <div className="space-y-6">
        <PageHeader
          title="GreenProof Evidence Record"
          subtitle="Backend-generated audit trail after human approval."
        />

        {error ? (
          <Card>
            <div className="text-sm text-red-600">{error}</div>
          </Card>
        ) : null}

        {!record && !error ? (
          <Card>
            <div className="text-sm text-gray-600">
              Loading the saved Evidence Record...
            </div>
          </Card>
        ) : null}

        {record ? (
          <>
            <Card>
              <div className="space-y-2 text-sm text-gray-700">
                <div><strong>Record ID:</strong> {record.record_id}</div>
                <div><strong>Storage:</strong> {record.storage_mode}</div>
                <div><strong>Generated:</strong> {record.generated_at}</div>
                <div><strong>Decision:</strong> {record.user_decision.decision_type}</div>
              </div>
            </Card>

            <Card>
              <h2 className="font-medium mb-3">Selected resources</h2>
              <div className="space-y-2 text-sm text-gray-700">
                {record.resources_selected.map((item) => (
                  <div key={item.resource_id}>
                    {item.site_name} - {item.quantity_units} units
                  </div>
                ))}
                {record.selected_equipment ? (
                  <div>
                    {record.selected_equipment.site_name} - {record.selected_equipment.category}
                  </div>
                ) : null}
              </div>
            </Card>

            <Card>
              <h2 className="font-medium mb-3">Excluded resources</h2>
              <div className="space-y-2 text-sm text-gray-600">
                {record.resources_excluded.map((item) => (
                  <div key={item.resource_id}>{item.reason_text}</div>
                ))}
              </div>
            </Card>

            <Card>
              <h2 className="font-medium mb-3">Impact summary</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <div className="border rounded-lg p-3">
                  <div className="text-gray-500">Net saving</div>
                  <div className="font-semibold">
                    RM {Number(record.cost_comparison.net_saving_myr).toFixed(2)}
                  </div>
                </div>
                <div className="border rounded-lg p-3">
                  <div className="text-gray-500">Carbon avoided</div>
                  <div className="font-semibold">
                    {Number(record.carbon_comparison.net_carbon_avoided_kgco2e).toFixed(2)} kgCO2e
                  </div>
                </div>
              </div>
            </Card>
          </>
        ) : null}

        <button
          onClick={() => router.push("/")}
          className="w-full bg-black text-white py-3 rounded-xl font-medium"
        >
          New Request
        </button>
      </div>
    </Container>
  );
}
