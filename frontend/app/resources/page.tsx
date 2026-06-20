"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ResourcesPage() {
  const router = useRouter();

  // 👇 mode now controlled by Verdict actions
  const [mode, setMode] = useState<"normal" | "greenproof" | "inspection">("greenproof");

  useEffect(() => {
    const inspectionMode = localStorage.getItem("inspectionMode");
    const normalMode = localStorage.getItem("mode");

    if (inspectionMode === "true") {
      setMode("inspection");
    } else if (normalMode === "normal") {
      setMode("normal");
    }
  }, []);

  const baseResources = [
    {
      name: "Site A",
      quantity: 300,
      risk: "Green",
      type: "Reuse",
      status: "Available",
      distance: "14 km",
    },
    {
      name: "Site B",
      quantity: 130,
      risk: "Amber",
      type: "Reuse",
      status: "Inspection Required",
      distance: "21 km",
    },
    {
      name: "Site D",
      quantity: 1,
      risk: "Green",
      type: "Equipment",
      status: "Available",
      distance: "9 km",
    },
    {
      name: "Site E",
      quantity: 200,
      risk: "Red",
      type: "Reuse",
      status: "Unverified - Excluded",
      distance: "18 km",
    },
    {
      name: "Supplier F",
      quantity: 70,
      risk: "Green",
      type: "New",
      status: "Fallback Source",
      distance: "32 km",
    },
  ];

  // 🔥 CORE LOGIC (this is what fixes your requirement)
  const resources = baseResources.filter((r) => {
    if (mode === "inspection") {
      return r.risk === "Amber" || r.risk === "Red";
    }

    if (mode === "normal") {
      return true; // everything shown
    }

    // greenproof mode
    return r.risk !== "Red";
  });

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

          <div className="text-xs text-gray-400 mt-1">
            Mode: {mode.toUpperCase()}
          </div>
        </div>

        {/* MODE SWITCH */}
        <div className="flex gap-2">
          <button
            onClick={() => setMode("normal")}
            className={`px-3 py-1 rounded-full border ${
              mode === "normal" ? "bg-black text-white" : "bg-white"
            }`}
          >
            Normal
          </button>

          <button
            onClick={() => setMode("greenproof")}
            className={`px-3 py-1 rounded-full border ${
              mode === "greenproof" ? "bg-black text-white" : "bg-white"
            }`}
          >
            GreenProof
          </button>

          <button
            onClick={() => setMode("inspection")}
            className={`px-3 py-1 rounded-full border ${
              mode === "inspection" ? "bg-black text-white" : "bg-white"
            }`}
          >
            Inspection
          </button>
        </div>

        {/* MAP VISUAL - CONTROL ROOM VERSION */}
<div className="bg-slate-900 border border-slate-700 rounded-xl p-4 space-y-3 text-white">

  <div className="font-medium text-sm text-slate-200">
    GreenProof Logistics Control Map
  </div>

  {/* MAP CONTAINER */}
  <div className="relative w-full h-72 bg-slate-950 rounded-lg overflow-hidden border border-slate-800">

    {/* GRID BACKGROUND */}
    <div
      className="absolute inset-0 opacity-20"
      style={{
        backgroundImage:
          "linear-gradient(#1f2937 1px, transparent 1px), linear-gradient(90deg, #1f2937 1px, transparent 1px)",
        backgroundSize: "24px 24px",
      }}
    />

    {/* ZONE GLOW EFFECT */}
    <div className="absolute inset-0 bg-gradient-to-br from-green-900/10 via-transparent to-blue-900/10" />

    {/* CONNECTION LINES (ROUTES) */}
    <svg className="absolute inset-0 w-full h-full">

      {/* Site A → Site B (reuse flow) */}
      <path
        d="M 20 30 Q 45 10 70 25"
        stroke="#22c55e"
        strokeWidth="2"
        fill="none"
        strokeDasharray="6 6"
      />

      {/* Site B → Supplier F */}
      <path
        d="M 70 25 Q 85 40 90 60"
        stroke="#3b82f6"
        strokeWidth="2"
        fill="none"
        strokeDasharray="6 6"
      />

      {/* Site D → Site A */}
      <path
        d="M 30 80 Q 25 50 20 30"
        stroke="#22c55e"
        strokeWidth="2"
        fill="none"
        strokeDasharray="6 6"
      />

      {/* animated moving dot (flow simulation) */}
      <circle r="2.5" fill="#22c55e">
        <animateMotion dur="3s" repeatCount="indefinite">
          <mpath href="#route1" />
        </animateMotion>
      </circle>

    </svg>

    {/* SITE NODES */}
    {[
      { name: "Site A", x: 20, y: 30, risk: "green", status: "reuse" },
      { name: "Site B", x: 70, y: 25, risk: "amber", status: "inspection" },
      { name: "Site D", x: 30, y: 80, risk: "green", status: "equipment" },
      { name: "Site E", x: 75, y: 70, risk: "red", status: "excluded" },
      { name: "Supplier F", x: 90, y: 60, risk: "green", status: "supply" },
    ].map((r, i) => (
      <div
        key={i}
        className="absolute -translate-x-1/2 -translate-y-1/2"
        style={{ left: `${r.x}%`, top: `${r.y}%` }}
      >
        {/* PULSE RING */}
        <div
          className={`absolute w-6 h-6 rounded-full animate-ping opacity-40 ${
            r.risk === "green"
              ? "bg-green-500"
              : r.risk === "amber"
              ? "bg-yellow-500"
              : r.risk === "red"
              ? "bg-red-500"
              : "bg-gray-500"
          }`}
        />

        {/* NODE */}
        <div
          className={`relative w-3 h-3 rounded-full ${
            r.risk === "green"
              ? "bg-green-400"
              : r.risk === "amber"
              ? "bg-yellow-400"
              : r.risk === "red"
              ? "bg-red-500"
              : "bg-gray-400"
          }`}
        />

        {/* LABEL */}
        <div className="text-[10px] mt-1 text-center bg-slate-800 px-1 rounded">
          {r.name}
        </div>
      </div>
    ))}

  </div>

  {/* LEGEND */}
  <div className="flex gap-4 text-[11px] text-slate-300">

    <div className="flex items-center gap-1">
      <div className="w-2 h-2 bg-green-400 rounded-full" />
      Reuse Flow
    </div>

    <div className="flex items-center gap-1">
      <div className="w-2 h-2 bg-blue-400 rounded-full" />
      Supply Flow
    </div>

    <div className="flex items-center gap-1">
      <div className="w-2 h-2 bg-red-400 rounded-full" />
      High Risk
    </div>

  </div>

</div>

        {/* RESOURCE LIST */}
        {resources.map((r, i) => (
          <div key={i} className="bg-white border rounded-xl p-4 space-y-3">

            <div className="flex justify-between items-start">
              <div>
                <div className="font-medium">{r.name}</div>
                <div className="text-xs text-gray-500">
                  {r.type} • {r.distance}
                </div>
              </div>

              <div
                className={`text-xs px-2 py-1 rounded-full font-semibold
                  ${
                    r.risk === "Green"
                      ? "bg-green-100 text-green-700"
                      : r.risk === "Amber"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  }
                `}
              >
                {r.risk} Risk
              </div>
            </div>

            <div className="flex justify-between text-sm">
              <div>Qty: {r.quantity}</div>

              <div className="text-right">
                <div className="text-xs text-gray-500">
                  Verification Status
                </div>
                <div className="text-sm font-medium">
                  {r.status}
                </div>
              </div>
            </div>

            {/* 🔥 inspection highlight */}
            {mode === "inspection" && r.risk !== "Green" && (
              <div className="text-xs text-yellow-700">
                ⚠ Flagged for manual verification
              </div>
            )}
          </div>
        ))}

        {/* NEXT */}
        <button
          onClick={() => {
            localStorage.removeItem("inspectionMode");
            router.push("/plans");
          }}
          className="w-full bg-black text-white py-3 rounded-xl"
        >
          Generate Plans
        </button>

      </div>
    </div>
  );
}