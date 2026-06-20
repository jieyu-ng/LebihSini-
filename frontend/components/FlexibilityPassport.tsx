"use client";

import { useCaseStore } from "@/lib/store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Battery, Clock, DollarSign, Users, CheckCircle } from "lucide-react";

export function FlexibilityPassport() {
  const { smeProfile, optimizationResult } = useCaseStore();

  return (
    <Card className="border-t-4 border-t-emerald-500 shadow-md">
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-2xl font-bold text-slate-800">
              Energy Flexibility Passport
            </CardTitle>
            <p className="text-sm text-slate-500 mt-1">
              Verified Profile: <span className="font-semibold text-slate-700">{smeProfile.businessName}</span> ({smeProfile.businessType})
            </p>
          </div>
          <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 flex gap-1 items-center px-3 py-1">
            <CheckCircle className="w-4 h-4" />
            {optimizationResult.confidenceLevel}% Confidence
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="bg-blue-100 p-3 rounded-full text-blue-600">
              <Battery className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium">Flexible Load Range</p>
              <p className="text-xl font-bold text-slate-800">{optimizationResult.flexibleLoadRange}</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="bg-amber-100 p-3 rounded-full text-amber-600">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium">Suggested Shift Window</p>
              <p className="text-xl font-bold text-slate-800">{optimizationResult.suggestedWindow}</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="bg-emerald-100 p-3 rounded-full text-emerald-600">
              <DollarSign className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium">Estimated Monthly Savings</p>
              <p className="text-xl font-bold text-slate-800">RM {optimizationResult.estimatedSavingsRm.toFixed(2)}</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="bg-purple-100 p-3 rounded-full text-purple-600">
              <Users className="w-6 h-6" />
            </div>
            <div className="w-full">
              <div className="flex justify-between items-center mb-1">
                <p className="text-sm text-slate-500 font-medium">Community Fit Score</p>
                <span className="font-bold text-slate-800">{optimizationResult.communityFitScore}/100</span>
              </div>
              <Progress value={optimizationResult.communityFitScore} className="h-2" />
            </div>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <h4 className="text-sm font-semibold text-slate-700 mb-2">Final Recommendation</h4>
          <p className="text-slate-600 text-sm leading-relaxed">
            {optimizationResult.recommendationText}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
