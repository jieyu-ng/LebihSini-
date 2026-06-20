"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function EvidencePage() {
  const router = useRouter();
  const [timestamp] = useState(() => new Date().toISOString());

  const evidence = {
    recordId: "GP-REC-001",
    project: "Site C - Tile Procurement",

    request:
      "500 porcelain tiles (600x600 grey) + tile cutter needed by tomorrow 11:00",

    extractedRequirements: {
      material: "Porcelain tile",
      spec: "600x600 mm",
      quantity: 500,
      equipment: "Tile cutter",
      deadline: "Tomorrow 11:00",
    },

    selectedPlan: [
      "Site A → 300 tiles (sealed stock)",
      "Site B → 130 tiles (batch variation, inspection required)",
      "Supplier F → 70 tiles (new supply)",
      "Site D → tile cutter (idle equipment)",
    ],

    excludedResources: [
      "Site E → Unverified label (risk: Red)",
    ],

    decisionLogic: [
      "Matched specification across Sites A & B",
      "Excluded Site E due to missing verification",
      "Filled shortfall via Supplier F",
      "Used idle equipment instead of rental",
      "Validated deadline feasibility (Tomorrow 11:00)",
    ],

    costComparison: {
      baseline: 12500,
      greenproof: 9100,
      savings: 3400,
    },

    carbonComparison: {
      baseline: 1600,
      greenproof: 720,
      avoided: 880,
    },

    riskSummary: {
      level: "Medium",
      reason: "Batch variation requires inspection at Site B",
    },

    decision: "APPROVED (Human Confirmed)",

    approvedBy: "Siti (Site Supervisor)",

    timestamp,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold">
            GreenProof Evidence Record
          </h1>
          <p className="text-sm text-gray-500">
            Audit trail for procurement verification & accountability
          </p>
        </div>

        {/* RECORD META */}
        <div className="bg-white border rounded-xl p-5">
          <div className="text-sm text-gray-500">Record ID</div>
          <div className="font-medium">{evidence.recordId}</div>

          <div className="mt-3 text-sm text-gray-500">Timestamp</div>
          <div className="text-sm">{evidence.timestamp}</div>

          <div className="mt-3 text-sm text-gray-500">Approved By</div>
          <div className="font-medium">{evidence.approvedBy}</div>
        </div>

        {/* ORIGINAL REQUEST */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Original Request</h2>
          <p className="text-sm text-gray-700">{evidence.request}</p>
        </div>

        {/* EXTRACTED STRUCTURE */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">
            Extracted Requirements (AI Parsed)
          </h2>

          <div className="text-sm space-y-1 text-gray-700">
            <div>Material: {evidence.extractedRequirements.material}</div>
            <div>Spec: {evidence.extractedRequirements.spec}</div>
            <div>Quantity: {evidence.extractedRequirements.quantity}</div>
            <div>Equipment: {evidence.extractedRequirements.equipment}</div>
            <div>Deadline: {evidence.extractedRequirements.deadline}</div>
          </div>
        </div>

        {/* DECISION LOGIC */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Decision Logic</h2>

          <ul className="space-y-2 text-sm">
            {evidence.decisionLogic.map((step, i) => (
              <li key={i} className="text-gray-700 flex gap-2">
                <span className="text-blue-600">•</span>
                {step}
              </li>
            ))}
          </ul>
        </div>

        {/* SELECTED PLAN */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Selected Resources</h2>

          <ul className="space-y-2 text-sm">
            {evidence.selectedPlan.map((item, i) => (
              <li key={i} className="text-green-700 flex gap-2">
                <span>✔</span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* EXCLUDED */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Excluded Resources</h2>

          <ul className="space-y-2 text-sm">
            {evidence.excludedResources.map((item, i) => (
              <li key={i} className="text-red-500 flex gap-2">
                <span>✖</span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* RISK */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Risk Assessment</h2>

          <div className="text-sm">
            <div>
              Level:{" "}
              <span className="font-semibold">
                {evidence.riskSummary.level}
              </span>
            </div>
            <div className="text-gray-600 mt-1">
              {evidence.riskSummary.reason}
            </div>
          </div>
        </div>

        {/* IMPACT */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Impact Summary</h2>

          <div className="grid grid-cols-2 gap-4 text-sm">

            <div className="border rounded-lg p-3">
              <div className="text-gray-500">Cost Savings</div>
              <div className="text-green-600 font-semibold">
                RM {evidence.costComparison.savings}
              </div>
            </div>

            <div className="border rounded-lg p-3">
              <div className="text-gray-500">Carbon Avoided</div>
              <div className="text-green-600 font-semibold">
                {evidence.carbonComparison.avoided} kg CO₂e
              </div>
            </div>

          </div>
        </div>

        {/* CTA */}
        <button
          onClick={() => router.push("/")}
          className="w-full bg-black text-white py-3 rounded-xl"
        >
          New Request
        </button>

      </div>
    </div>
  );
}