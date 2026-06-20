"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function VerdictPage() {
  const router = useRouter();
  const [approving, setApproving] = useState(false);

  const verdict = {
    recommendedPlan: "GreenProof Hybrid Reuse Plan",

    reasons: [
      "Sufficient reuse material available from Site A & B",
      "Equipment already available at Site D (no rental needed)",
      "Supplier F fills material shortfall efficiently",
      "Optimised transport distance across sites",
    ],

    conditions: [
      "Site B tiles require inspection before final approval",
      "Delivery must be completed before 11:00 tomorrow",
    ],

    excludedResources: ["Site E – Unverified condition (High risk)"],

    confidenceBreakdown: {
      materialMatch: 0.94,
      availability: 0.88,
      riskAssessment: 0.79,
      deadlineFeasibility: 0.85,
    },
  };

  function approve() {
    setApproving(true);

    setTimeout(() => {
      localStorage.setItem("decision", "approved");
      localStorage.setItem("selectedPlan", "greenproof");

      router.push("/evidence");
    }, 1200);
  }

  function modify() {
    localStorage.setItem("returningFrom", "verdict");
    router.push("/plans");
  }

  function normalPurchase() {
    localStorage.setItem("mode", "normal");
    router.push("/resources");
  }

  function requestInspection() {
    localStorage.setItem("inspectionMode", "true");
    router.push("/resources");
  }

  function reject() {
    localStorage.clear();
    router.push("/");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold">Verdict</h1>
          <p className="text-sm text-gray-500">
            AI-generated procurement decision summary
          </p>
        </div>

        {/* RECOMMENDED PLAN */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-2">Recommended Plan</h2>
          <p className="text-green-700 font-semibold">
            {verdict.recommendedPlan}
          </p>
        </div>

        {/* REASONS */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Reasons</h2>
          <ul className="space-y-2 text-sm">
            {verdict.reasons.map((r, i) => (
              <li key={i} className="text-gray-700 flex gap-2">
                <span className="text-blue-600">•</span>
                {r}
              </li>
            ))}
          </ul>
        </div>

        {/* CONDITIONS */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Conditions</h2>
          <ul className="space-y-2 text-sm">
            {verdict.conditions.map((c, i) => (
              <li key={i} className="text-yellow-700 flex gap-2">
                <span>⚠</span>
                {c}
              </li>
            ))}
          </ul>
        </div>

        {/* EXCLUDED */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Excluded Resources</h2>
          <ul className="space-y-2 text-sm">
            {verdict.excludedResources.map((e, i) => (
              <li key={i} className="text-red-600 flex gap-2">
                <span>✖</span>
                {e}
              </li>
            ))}
          </ul>
        </div>

        {/* CONFIDENCE */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-medium mb-3">Confidence</h2>

          <div className="text-sm space-y-1 text-gray-700">
            <div>Material Match: {verdict.confidenceBreakdown.materialMatch}</div>
            <div>Availability: {verdict.confidenceBreakdown.availability}</div>
            <div>Risk Assessment: {verdict.confidenceBreakdown.riskAssessment}</div>
            <div>Deadline Feasibility: {verdict.confidenceBreakdown.deadlineFeasibility}</div>
          </div>
        </div>

        {/* ACTIONS */}
        <div className="grid gap-3">

          <button
            onClick={approve}
            className="w-full bg-green-600 text-white py-3 rounded-xl"
          >
            {approving ? "Generating Audit Log..." : "Approve"}
          </button>

          <button
            onClick={modify}
            className="w-full bg-blue-600 text-white py-3 rounded-xl"
          >
            Modify Plan
          </button>

          <button
            onClick={normalPurchase}
            className="w-full bg-black text-white py-3 rounded-xl"
          >
            Proceed with Normal Purchase
          </button>

          <button
            onClick={requestInspection}
            className="w-full bg-yellow-600 text-white py-3 rounded-xl"
          >
            Request Inspection
          </button>

          <button
            onClick={reject}
            className="w-full bg-red-600 text-white py-3 rounded-xl"
          >
            Reject
          </button>

          <button
            onClick={() => router.push("/evidence")}
            className="w-full border py-3 rounded-xl"
          >
            View Evidence Record
          </button>
        </div>

      </div>
    </div>
  );
}