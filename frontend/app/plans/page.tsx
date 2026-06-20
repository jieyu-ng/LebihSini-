"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { plans } from "@/lib/mockData";

export default function PlansPage() {
  const router = useRouter();

  const planList = Object.values(plans);
  const [selectedPlan, setSelectedPlan] = useState("GreenProof Plan");

  function handleProceed() {
    localStorage.setItem("selectedPlan", selectedPlan);
    router.push("/verdict");
  }

  function getScore(plan: any) {
    // simple heuristic for demo realism
    const efficiency =
      (plan.reusedTiles / (plan.newTiles + plan.reusedTiles)) * 100;

    const costScore = (15000 - plan.cost) / 100;
    const carbonScore = (2000 - plan.carbon) / 10;

    return Math.round(efficiency + costScore + carbonScore);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">

        <h1 className="text-2xl font-semibold">
          Plan Comparison
        </h1>

        <p className="text-sm text-gray-500">
          AI evaluates cost, carbon, reuse efficiency, and risk
        </p>

        {/* COMPARISON GRID */}
        <div className="grid md:grid-cols-3 gap-4">

          {planList.map((plan) => {
            const score = getScore(plan);
            const isSelected = selectedPlan === plan.title;

            return (
              <div
                key={plan.title}
                onClick={() => setSelectedPlan(plan.title)}
                className={`cursor-pointer border rounded-xl p-5 space-y-3 transition
                  ${
                    isSelected
                      ? "border-black bg-white shadow-md"
                      : "bg-white opacity-80 hover:opacity-100"
                  }`}
              >

                {/* HEADER */}
                <div className="flex justify-between items-center">
                  <div className="text-lg font-semibold">
                    {plan.title}
                  </div>

                  {/* SCORE BADGE */}
                  <div className="text-xs bg-black text-white px-2 py-1 rounded-full">
                    Score {score}
                  </div>
                </div>

                {/* BEST TAG */}
                {plan.title === "GreenProof Plan" && (
                  <div className="text-xs text-green-600 font-medium">
                    🏆 AI Recommended
                  </div>
                )}

                {/* METRICS */}
                <div className="space-y-2 text-sm">

                  <div>
                    <span className="text-gray-500">New Tiles:</span>{" "}
                    <span className="font-medium">{plan.newTiles}</span>
                  </div>

                  <div>
                    <span className="text-gray-500">Reused Tiles:</span>{" "}
                    <span className="font-medium">{plan.reusedTiles}</span>
                  </div>

                  <div>
                    <span className="text-gray-500">Equipment:</span>{" "}
                    <span className="font-medium">
                      {plan.equipmentSource || "External rental"}
                    </span>
                  </div>

                  <div>
                    <span className="text-gray-500">Sites:</span>{" "}
                    <span className="font-medium">
                      {plan.collectionSites}
                    </span>
                  </div>

                  <div>
                    <span className="text-gray-500">Cost:</span>{" "}
                    <span className="font-medium">
                      RM {plan.cost}
                    </span>
                  </div>

                  <div>
                    <span className="text-gray-500">Carbon:</span>{" "}
                    <span className="font-medium">
                      {plan.carbon} kgCO₂e
                    </span>
                  </div>

                  <div>
                    <span className="text-gray-500">Risk:</span>{" "}
                    <span className="font-medium">
                      {plan.risk || "Medium"}
                    </span>
                  </div>

                </div>
              </div>
            );
          })}

        </div>

        {/* CTA */}
        <button
          onClick={handleProceed}
          className="w-full bg-black text-white py-3 rounded-xl font-medium"
        >
          Proceed with Selected Plan → Verdict
        </button>

      </div>
    </div>
  );
}