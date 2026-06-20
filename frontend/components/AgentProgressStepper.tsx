"use client";

import { useCaseStore } from "@/lib/store";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AgentProgressStepper() {
  const { agentProgress } = useCaseStore();

  const steps = [
    { label: "Bill information verified", key: "billVerified" },
    { label: "Business profile created", key: "profileCreated" },
    { label: "Flexible activities identified", key: "activitiesIdentified" },
    { label: "Testing optimisation plans", key: "testingPlans" },
    { label: "Auditing final recommendation", key: "auditing" },
  ] as const;

  // Determine current active step index based on the first false step
  let currentStepIndex = steps.findIndex((step) => !agentProgress[step.key]);
  if (currentStepIndex === -1) currentStepIndex = steps.length;

  return (
    <Card className="bg-white/50 backdrop-blur-sm border-emerald-100 shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-emerald-900">KitaAI Energy Coordinator</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {steps.map((step, index) => {
            const isCompleted = index < currentStepIndex;
            const isCurrent = index === currentStepIndex;
            
            return (
              <div key={step.key} className="flex items-center gap-3">
                {isCompleted ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                ) : isCurrent ? (
                  <Loader2 className="h-5 w-5 text-emerald-500 animate-spin" />
                ) : (
                  <Circle className="h-5 w-5 text-slate-300" />
                )}
                <span
                  className={`text-sm ${
                    isCompleted
                      ? "text-slate-600 line-through"
                      : isCurrent
                      ? "text-emerald-700 font-medium"
                      : "text-slate-400"
                  }`}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
