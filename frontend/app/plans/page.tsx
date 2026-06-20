"use client";

import { useRouter } from "next/navigation";
import { plans } from "@/lib/mockData";

export default function PlansPage() {
  const router = useRouter();

  return (
    <div className="max-w-6xl mx-auto p-4">

      <h1 className="text-2xl font-semibold mb-6">
        Plan Comparison
      </h1>

      <div className="grid md:grid-cols-3 gap-4">

        {Object.values(plans).map((plan) => (
          <div
            key={plan.title}
            className="bg-white border rounded-xl p-5"
          >
            <h2 className="font-semibold mb-4">
              {plan.title}
            </h2>

            <div className="space-y-2 text-sm">

              <div>
                Reused Tiles: {plan.reusedTiles}
              </div>

              <div>
                New Tiles: {plan.newTiles}
              </div>

              <div>
                Collection Sites: {plan.collectionSites}
              </div>

              <div>
                Cost: RM {plan.cost}
              </div>

              <div>
                Carbon: {plan.carbon} kgCO₂e
              </div>

            </div>
          </div>
        ))}

      </div>

      <button
        onClick={() => router.push("/verdict")}
        className="mt-6 w-full bg-black text-white py-3 rounded-xl"
      >
        Proceed to Verdict
      </button>
    </div>
  );
}