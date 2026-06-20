"use client";

import { useEffect, useState } from "react";
import { AgentProgressStepper } from "@/components/AgentProgressStepper";
import { FlexibilityPassport } from "@/components/FlexibilityPassport";
import { useCaseStore } from "@/lib/store";
import { Loader2 } from "lucide-react";

export default function DashboardPage() {
  const { agentProgress, setAgentProgress } = useCaseStore();
  const [isAuditing, setIsAuditing] = useState(false);

  useEffect(() => {
    // Simulate the AI multi-agent workflow
    if (!agentProgress.testingPlans) {
      const timer = setTimeout(() => {
        setAgentProgress({ testingPlans: true });
        setIsAuditing(true);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [agentProgress.testingPlans, setAgentProgress]);

  useEffect(() => {
    if (isAuditing && !agentProgress.auditing) {
      const timer = setTimeout(() => {
        setAgentProgress({ auditing: true });
        setIsAuditing(false);
      }, 2500);
      return () => clearTimeout(timer);
    }
  }, [isAuditing, agentProgress.auditing, setAgentProgress]);

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Your Energy Workspace</h1>
          <p className="text-slate-500 mt-2">Monitor KitaAI's progress and view your final results.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <AgentProgressStepper />
          </div>
          
          <div className="md:col-span-2">
            {!agentProgress.auditing ? (
              <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white rounded-xl border border-slate-200 border-dashed text-slate-400">
                <Loader2 className="w-12 h-12 mb-4 animate-spin text-emerald-400" />
                <p className="text-lg font-medium text-slate-600">Generating Flexibility Passport...</p>
                <p className="text-sm mt-2 text-center max-w-md">
                  KitaAI is running simulations against local community grids to find the optimal schedule for your business.
                </p>
              </div>
            ) : (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <FlexibilityPassport />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
