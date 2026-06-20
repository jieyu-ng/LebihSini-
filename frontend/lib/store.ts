import { create } from 'zustand';
import defaultState from './case_state.json';

export interface SmeProfile {
  name: string;
  businessName: string;
  location: string;
  businessType: string;
  operatingHours: string;
  busiestHours: string;
}

export interface BillData {
  billingMonth: string;
  consumptionKwh: number;
  totalAmountRm: number;
  maximumDemandKw: number;
  consumptionIncrease: string;
}

export interface Equipment {
  id: string;
  name: string;
  type: 'flexible' | 'inflexible';
  notes: string;
}

export interface OptimizationResult {
  flexibleLoadRange: string;
  suggestedWindow: string;
  estimatedSavingsRm: number;
  communityFitScore: number;
  confidenceLevel: number;
  recommendationText: string;
}

export interface AgentProgress {
  billVerified: boolean;
  profileCreated: boolean;
  activitiesIdentified: boolean;
  testingPlans: boolean;
  auditing: boolean;
}

export interface CaseState {
  smeProfile: SmeProfile;
  billData: BillData;
  equipment: Equipment[];
  optimizationResult: OptimizationResult;
  agentProgress: AgentProgress;
  setAgentProgress: (progress: Partial<AgentProgress>) => void;
  updateSmeProfile: (profile: Partial<SmeProfile>) => void;
}

export const useCaseStore = create<CaseState>((set) => ({
  ...(defaultState as Omit<CaseState, 'setAgentProgress' | 'updateSmeProfile'>),
  setAgentProgress: (progress) =>
    set((state) => ({
      agentProgress: { ...state.agentProgress, ...progress },
    })),
  updateSmeProfile: (profile) =>
    set((state) => ({
      smeProfile: { ...state.smeProfile, ...profile },
    })),
}));
