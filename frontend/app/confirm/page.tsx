"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function ConfirmPage() {
  const router = useRouter();

  const [loadingStage, setLoadingStage] = useState(0);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
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

        setData({
          material: "porcelain_tile",
          dimensions: "600x600",
          colour: "grey",
          quantity: 500,
          deadline: "Tomorrow 11:00",
          equipment: "tile_cutter",
          confidence: {
            material: 0.96,
            dimensions: 0.91,
            colour: 0.88,
            quantity: 0.83,
            deadline: 0.94,
            equipment: 0.89,
          },
        });

        return;
      }

      i++;
    }, 900);

    return () => clearInterval(interval);
  }, []);

  // loading state
  if (!data) {
    const messages = [
      "Reading your request...",
      "Extracting material specifications...",
      "Checking missing information...",
    ];

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-2">
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

  // update field helper
  function updateField(field: string, value: string) {
    setData((prev: any) => ({
      ...prev,
      [field]: value,
    }));
  }

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center">
      <div className="w-full max-w-2xl px-4 py-6 space-y-4">

        <h1 className="text-xl font-semibold">
          Confirm Requirement
        </h1>

        {/* EDITABLE FIELDS */}
        <div className="bg-white border rounded-xl p-4 space-y-4">

          <Field
            label="Material"
            value={data.material}
            confidence={data.confidence.material}
            onChange={(v: string) => updateField("material", v)}
          />

          <Field
            label="Dimensions"
            value={data.dimensions}
            confidence={data.confidence.dimensions}
            onChange={(v:string) => updateField("dimensions", v)}
          />

          <Field
            label="Colour"
            value={data.colour}
            confidence={data.confidence.colour}
            onChange={(v:string) => updateField("colour", v)}
          />

          <Field
            label="Quantity"
            value={data.quantity}
            confidence={data.confidence.quantity}
            onChange={(v:string) => updateField("quantity", v)}
          />

          <Field
            label="Deadline"
            value={data.deadline}
            confidence={data.confidence.deadline}
            onChange={(v:string) => updateField("deadline", v)}
          />

          <Field
            label="Equipment"
            value={data.equipment}
            confidence={data.confidence.equipment}
            onChange={(v:string) => updateField("equipment", v)}
          />
        </div>

        {/* ACTION */}
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

/* FIELD COMPONENT */
function Field({
  label,
  value,
  confidence,
  onChange,
}: any) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-500">
        <span>{label}</span>
        <span>Confidence: {confidence}</span>
      </div>

      <input
        className="w-full border rounded-lg p-2 text-sm"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}