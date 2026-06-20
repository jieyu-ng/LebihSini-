"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function EvidencePage() {
  const router = useRouter();
  const [timestamp] = useState(() => new Date().toISOString());

  const evidence = {
    originalRequirement:
      "500 porcelain tiles (600x600 grey) + tile cutter needed by tomorrow 11:00",

    selectedResources: [
      "Site A → 300 tiles (available stock)",
      "Site B → 130 tiles (inspection required)",
      "Supplier F → 70 tiles (new supply)",
      "Site D → tile cutter (idle equipment)",
    ],

    excludedResources: ["Site E → Unverified condition (High risk)"],

    costCarbonAssumptions: {
      baselineCost: 12500,
      optimizedCost: 9100,
      costSaved: 3400,

      baselineCarbon: 1600,
      optimizedCarbon: 720,
      carbonSaved: 880,
    },

    humanDecision: "APPROVED (Human Verified by Site Supervisor)",

    finalApprovedPlan: "GreenProof Hybrid Reuse Plan (Balanced Risk Optimisation)",
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold">Evidence Record</h1>
          <p className="text-sm text-gray-500">
            Immutable audit trail of procurement decision
          </p>
        </div>

        {/* TIMESTAMP */}
        <div className="bg-white border rounded-xl p-4">
          <div className="text-xs text-gray-500">Timestamp</div>
          <div className="text-sm">{timestamp}</div>
        </div>

        {/* ORIGINAL REQUIREMENT */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Original Requirement</h2>
          <p className="text-sm text-gray-700">
            {evidence.originalRequirement}
          </p>
        </div>

        {/* FINAL PLAN */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Final Approved Plan</h2>
          <p className="text-green-700 font-semibold">
            {evidence.finalApprovedPlan}
          </p>
        </div>

        {/* HUMAN DECISION */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Human Decision</h2>
          <p className="text-blue-700 font-semibold">
            {evidence.humanDecision}
          </p>
        </div>

        {/* SELECTED RESOURCES */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Selected Resources</h2>
          <ul className="space-y-2 text-sm">
            {evidence.selectedResources.map((item, i) => (
              <li key={i} className="text-gray-700 flex gap-2">
                <span className="text-green-600">✔</span>
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
              <li key={i} className="text-gray-500 flex gap-2">
                <span className="text-red-500">✖</span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* COST + CARBON */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Cost & Carbon Assumptions</h2>

          <div className="grid grid-cols-2 gap-4 text-sm">

            <div className="border rounded-lg p-3">
              <div className="text-gray-500">Cost Savings</div>
              <div className="text-green-600 font-semibold">
                RM {evidence.costCarbonAssumptions.costSaved}
              </div>
              <div className="text-xs text-gray-500">
                {evidence.costCarbonAssumptions.optimizedCost} vs{" "}
                {evidence.costCarbonAssumptions.baselineCost}
              </div>
            </div>

            <div className="border rounded-lg p-3">
              <div className="text-gray-500">Carbon Reduction</div>
              <div className="text-green-600 font-semibold">
                {evidence.costCarbonAssumptions.carbonSaved} kg CO₂e
              </div>
              <div className="text-xs text-gray-500">
                {evidence.costCarbonAssumptions.optimizedCarbon} vs{" "}
                {evidence.costCarbonAssumptions.baselineCarbon}
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