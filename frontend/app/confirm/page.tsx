"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function ConfirmPage() {
  const router = useRouter();

  const [loadingStage, setLoadingStage] = useState(0);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // fake AI pipeline
    const stages = [
      "Reading your request",
      "Extracting material specifications",
      "Checking missing information",
    ];

    let i = 0;

    const interval = setInterval(() => {
      setLoadingStage(i);

      if (i === stages.length) {
        clearInterval(interval);

        // MOCK extracted AI output
        setData({
          material: "porcelain_tile",
          dimensions: "600x600",
          colour: "grey",
          quantity: 500,
          deadline: "Tomorrow 11:00",
          equipment: "tile_cutter",
          confidence: {
            material: 0.96,
            quantity: 0.83,
            deadline: 0.94,
          },
        });

        return;
      }

      i++;
    }, 900);

    return () => clearInterval(interval);
  }, []);

  if (!data) {
    const messages = [
      "Reading your request...",
      "Extracting material specifications...",
      "Checking missing information...",
    ];

    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-center space-y-3">
          <div className="text-lg font-medium">
            {messages[loadingStage] || "Processing..."}
          </div>
          <div className="text-sm text-gray-500">
            AI is analysing your request
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center">
      <div className="w-full max-w-2xl px-4 py-6 space-y-4">

        <h1 className="text-xl font-semibold">Confirm Requirement</h1>

        {/* Editable Fields */}
        <div className="bg-white border rounded-xl p-4 space-y-3">

          <Input label="Material" value={data.material} />
          <Input label="Dimensions" value={data.dimensions} />
          <Input label="Colour" value={data.colour} />
          <Input label="Quantity" value={data.quantity} />
          <Input label="Deadline" value={data.deadline} />
          <Input label="Equipment" value={data.equipment} />

        </div>

        {/* Confidence Panel */}
        <div className="bg-white border rounded-xl p-4">
          <h2 className="text-sm font-medium mb-2">AI Confidence</h2>

          <div className="space-y-2 text-sm text-gray-600">
            <div>Material: {data.confidence.material}</div>
            <div>Quantity: {data.confidence.quantity}</div>
            <div>Deadline: {data.confidence.deadline}</div>
          </div>
        </div>

        {/* Actions */}
        <button
          onClick={() => router.push("/resources")}
          className="w-full bg-black text-white py-2 rounded-lg"
        >
          Confirm & Continue
        </button>

      </div>
    </div>
  );
}

/* small reusable input */
function Input({ label, value }: any) {
  return (
    <div>
      <div className="text-xs text-gray-500">{label}</div>
      <input
        className="w-full border rounded-lg p-2 text-sm"
        defaultValue={value}
      />
    </div>
  );
}