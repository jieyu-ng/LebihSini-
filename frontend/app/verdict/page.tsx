"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function VerdictPage() {
  const router = useRouter();

  // ✅ Fix hydration issue: freeze timestamp once
  const [timestamp] = useState(() => new Date().toISOString());

  const evidence = {
    request: "500 porcelain tiles + tile cutter needed by tomorrow",

    selectedResources: [
      "Site A - 300 tiles",
      "Site B - 130 tiles (inspection required)",
      "Supplier F - 70 tiles (new supply)",
      "Site D - tile cutter",
    ],

    excludedResources: [
      "Site E - uncertain condition (unreadable label)",
    ],

    cost: {
      baseline: 12500,
      greenproof: 9100,
      savings: 3400,
    },

    carbon: {
      baseline: 1600,
      greenproof: 720,
      saved: 880,
    },

    decision: "Approved - Partial Reuse Plan",
    timestamp,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* HEADER */}
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">Evidence Record</h1>
          <p className="text-sm text-gray-500">
            Immutable audit trail of GreenProof decision
          </p>
        </div>

        {/* REQUEST */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Original Request</h2>
          <p className="text-sm text-gray-600">{evidence.request}</p>
        </div>

        {/* DECISION */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Final Decision</h2>

          <div className="text-green-600 font-semibold">
            {evidence.decision}
          </div>

          <div className="text-xs text-gray-500 mt-2">
            Timestamp: {evidence.timestamp}
          </div>
        </div>

        {/* RESOURCES */}
        <div className="grid gap-4">

          {/* SELECTED */}
          <div className="bg-white border rounded-xl p-5">
            <h3 className="font-medium mb-3">Selected Resources</h3>

            <ul className="space-y-2 text-sm">
              {evidence.selectedResources.map((item, i) => (
                <li key={i} className="flex gap-2 text-gray-700">
                  <span className="text-green-600">✔</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* EXCLUDED */}
          <div className="bg-white border rounded-xl p-5">
            <h3 className="font-medium mb-3">Excluded Resources</h3>

            <ul className="space-y-2 text-sm">
              {evidence.excludedResources.map((item, i) => (
                <li key={i} className="flex gap-2 text-gray-500">
                  <span className="text-red-500">✖</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* IMPACT */}
        <div className="bg-white border rounded-xl p-5">
          <h3 className="font-medium mb-3">Impact Summary</h3>

          <div className="grid grid-cols-2 gap-4 text-sm">

            {/* COST */}
            <div className="p-3 border rounded-lg">
              <div className="text-gray-500">Cost Savings</div>
              <div className="text-lg font-semibold text-green-600">
                RM {evidence.cost.savings}
              </div>
              <div className="text-xs text-gray-500">
                {evidence.cost.greenproof} vs {evidence.cost.baseline}
              </div>
            </div>

            {/* CARBON */}
            <div className="p-3 border rounded-lg">
              <div className="text-gray-500">Carbon Reduction</div>
              <div className="text-lg font-semibold text-green-600">
                {evidence.carbon.saved} kg CO₂e
              </div>
              <div className="text-xs text-gray-500">
                {evidence.carbon.greenproof} vs {evidence.carbon.baseline}
              </div>
            </div>

          </div>
        </div>

        {/* CTA */}
        <button
          onClick={() => router.push("/evidence")}
          className="w-full bg-black text-white py-3 rounded-xl font-medium hover:bg-gray-800"
        >
          New Request
        </button>

      </div>
    </div>
  );
}