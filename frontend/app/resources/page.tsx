"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ResourcesPage() {
  const router = useRouter();

  const [selected, setSelected] = useState("greenproof");

  const resources = [
    {
      name: "Site A",
      type: "Reuse Site",
      quantity: 300,
      distance: "14 km",
      risk: "Green",
      status: "Available",
    },
    {
      name: "Site B",
      type: "Reuse Site",
      quantity: 130,
      distance: "21 km",
      risk: "Amber",
      status: "Inspection Required",
    },
    {
      name: "Site D",
      type: "Equipment",
      quantity: 1,
      distance: "9 km",
      risk: "Green",
      status: "Available",
    },
    {
      name: "Site E",
      type: "Reuse Site",
      quantity: 200,
      distance: "18 km",
      risk: "Red",
      status: "EXCLUDED - Unverified",
    },
    {
      name: "Supplier F",
      type: "New Supply",
      quantity: 70,
      distance: "32 km",
      risk: "Green",
      status: "Fallback Source",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* HEADER */}
        <div>
          <h1 className="text-xl font-semibold">
            Resource Discovery
          </h1>
          <p className="text-sm text-gray-500">
            Multi-source availability & verification layer
          </p>
        </div>

        {/* MODE SWITCH */}
        <div className="flex gap-2">
          <button
            onClick={() => setSelected("normal")}
            className={`px-3 py-1 rounded-full text-sm border ${
              selected === "normal"
                ? "bg-black text-white"
                : "bg-white"
            }`}
          >
            Normal Procurement
          </button>

          <button
            onClick={() => setSelected("greenproof")}
            className={`px-3 py-1 rounded-full text-sm border ${
              selected === "greenproof"
                ? "bg-black text-white"
                : "bg-white"
            }`}
          >
            GreenProof Plan
          </button>
        </div>

        {/* RESOURCE LIST */}
        <div className="space-y-3">
          {resources.map((r, i) => (
            <div
              key={i}
              className="bg-white border rounded-xl p-4 flex justify-between items-center"
            >
              {/* LEFT */}
              <div>
                <div className="font-medium">{r.name}</div>
                <div className="text-xs text-gray-500">
                  {r.type} • {r.distance}
                </div>
              </div>

              {/* MIDDLE */}
              <div className="text-sm text-gray-700">
                Qty: {r.quantity}
              </div>

              {/* RIGHT STATUS */}
              <div className="text-right">
                <div
                  className={`text-xs font-semibold ${
                    r.risk === "Green"
                      ? "text-green-600"
                      : r.risk === "Amber"
                      ? "text-yellow-600"
                      : "text-red-600"
                  }`}
                >
                  {r.risk}
                </div>

                <div className="text-xs text-gray-500">
                  {r.status}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* NEXT STEP BUTTON */}
        <button
          onClick={() => router.push("/verdict")}
          className="w-full bg-black text-white py-3 rounded-xl font-medium hover:bg-gray-800"
        >
          Generate GreenProof Verdict
        </button>

      </div>
    </div>
  );
}