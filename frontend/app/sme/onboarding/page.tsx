"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCaseStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, Bot, Check } from "lucide-react";

export default function OnboardingPage() {
  const router = useRouter();
  const { smeProfile, updateSmeProfile, setAgentProgress } = useCaseStore();
  const [step, setStep] = useState(1);

  const handleNext = () => {
    if (step < 5) {
      setStep(step + 1);
    } else {
      setAgentProgress({ profileCreated: true, activitiesIdentified: true });
      router.push("/sme/dashboard");
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <p className="text-lg text-slate-700">What best describes your business?</p>
            <div className="grid grid-cols-2 gap-3">
              {["Laundromat", "Supermarket", "Manufacturing", "Office"].map((type) => (
                <div 
                  key={type}
                  onClick={() => updateSmeProfile({ businessType: type })}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    smeProfile.businessType === type 
                    ? "border-emerald-500 bg-emerald-50 text-emerald-800" 
                    : "border-slate-200 hover:border-emerald-300"
                  }`}
                >
                  <span className="font-medium">{type}</span>
                </div>
              ))}
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <p className="text-lg text-slate-700">What are your typical operating hours?</p>
            <input 
              type="text" 
              className="w-full p-4 rounded-xl border-2 border-slate-200 focus:border-emerald-500 outline-none transition-colors text-slate-800"
              value={smeProfile.operatingHours}
              onChange={(e) => updateSmeProfile({ operatingHours: e.target.value })}
            />
          </div>
        );
      case 3:
        return (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <p className="text-lg text-slate-700">When are your busiest customer hours?</p>
            <input 
              type="text" 
              className="w-full p-4 rounded-xl border-2 border-slate-200 focus:border-emerald-500 outline-none transition-colors text-slate-800"
              value={smeProfile.busiestHours}
              onChange={(e) => updateSmeProfile({ busiestHours: e.target.value })}
            />
          </div>
        );
      case 4:
        return (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <p className="text-lg text-slate-700">What is your most power-hungry equipment?</p>
            <div className="grid gap-3">
              <div className="p-4 rounded-xl border-2 border-emerald-500 bg-emerald-50 text-emerald-800 font-medium flex justify-between items-center">
                <span>Washing Machines</span>
                <Check className="w-5 h-5" />
              </div>
              <div className="p-4 rounded-xl border-2 border-emerald-500 bg-emerald-50 text-emerald-800 font-medium flex justify-between items-center">
                <span>Dryers</span>
                <Check className="w-5 h-5" />
              </div>
            </div>
          </div>
        );
      case 5:
        return (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <p className="text-lg text-slate-700">Can any of these operations be shifted outside the busiest hours without hurting business?</p>
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-800 text-sm mb-4">
              <span className="font-semibold block mb-1">KitaAI Inference:</span>
              Based on other laundromats, washing cycles are often flexible if staff pre-load machines, but drying must happen immediately after.
            </div>
            <textarea 
              className="w-full p-4 rounded-xl border-2 border-slate-200 focus:border-emerald-500 outline-none transition-colors text-slate-800 min-h-[100px]"
              defaultValue="Yes, washing cycles can be shifted. Dryers are inflexible."
            />
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800">KitaAI Energy Coordinator</h1>
            <p className="text-sm text-slate-500">Step {step} of 5</p>
          </div>
        </div>

        <Card className="shadow-lg border-0 shadow-slate-200/50">
          <CardContent className="p-8">
            <div className="min-h-[200px]">
              {renderStep()}
            </div>
            
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-slate-100">
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div 
                    key={i} 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      i === step ? "w-8 bg-emerald-500" : i < step ? "w-4 bg-emerald-200" : "w-4 bg-slate-200"
                    }`} 
                  />
                ))}
              </div>
              
              <Button 
                onClick={handleNext} 
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 rounded-full"
              >
                {step === 5 ? "Generate Passport" : "Next"}
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
