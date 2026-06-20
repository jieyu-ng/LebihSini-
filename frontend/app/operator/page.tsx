"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Map, Zap, Settings, Play } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const mockCommunityMap = [
  { id: 1, name: "Aisyah Laundromat", status: "optimized", x: 20, y: 30 },
  { id: 2, name: "Mega Supermarket", status: "pending", x: 70, y: 20 },
  { id: 3, name: "EV Hub PJ", status: "pending", x: 40, y: 70 },
  { id: 4, name: "Alpha Manufacturing", status: "optimized", x: 80, y: 80 },
];

const chartData = [
  {
    name: "Solar Utilisation",
    Before: 45,
    After: 78,
  },
  {
    name: "Grid Import",
    Before: 85,
    After: 42,
  },
  {
    name: "Peak Demand",
    Before: 90,
    After: 55,
  },
];

export default function OperatorPage() {
  const [isOptimized, setIsOptimized] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Community Energy Manager</h1>
            <p className="text-slate-500 mt-2">Zone: Petaling Jaya North</p>
          </div>
          <Button 
            onClick={() => setIsOptimized(true)}
            disabled={isOptimized}
            className={`${isOptimized ? 'bg-slate-300' : 'bg-blue-600 hover:bg-blue-700'} text-white`}
          >
            {isOptimized ? (
              <span className="flex items-center"><Zap className="w-4 h-4 mr-2" /> Balanced Plan Active</span>
            ) : (
              <span className="flex items-center"><Play className="w-4 h-4 mr-2" /> Run Balanced Plan</span>
            )}
          </Button>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <Card className="shadow-sm">
            <CardHeader className="border-b border-slate-100 bg-slate-50/50">
              <CardTitle className="flex items-center text-lg font-bold text-slate-800">
                <Map className="w-5 h-5 mr-2 text-blue-600" />
                Community Cluster View
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="relative w-full h-[400px] bg-slate-100 rounded-xl border-2 border-dashed border-slate-200 overflow-hidden">
                {/* CSS Grid Mock Map Background */}
                <div className="absolute inset-0" style={{ 
                  backgroundImage: 'radial-gradient(#cbd5e1 1px, transparent 1px)', 
                  backgroundSize: '20px 20px' 
                }}></div>
                
                {mockCommunityMap.map((node) => (
                  <div 
                    key={node.id}
                    className="absolute flex flex-col items-center group cursor-pointer transition-transform hover:scale-110 z-10"
                    style={{ left: `${node.x}%`, top: `${node.y}%`, transform: 'translate(-50%, -50%)' }}
                  >
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      isOptimized || node.status === 'optimized' 
                        ? 'bg-emerald-500 border-white shadow-[0_0_15px_rgba(16,185,129,0.5)]' 
                        : 'bg-amber-400 border-white shadow-[0_0_10px_rgba(251,191,36,0.5)]'
                    }`} />
                    <span className="mt-2 text-xs font-semibold text-slate-700 bg-white/90 px-2 py-1 rounded shadow-sm opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                      {node.name}
                    </span>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-center gap-6 mt-4 text-sm text-slate-600">
                <span className="flex items-center"><div className="w-3 h-3 rounded-full bg-amber-400 mr-2" /> Pending Optimization</span>
                <span className="flex items-center"><div className="w-3 h-3 rounded-full bg-emerald-500 mr-2" /> Flexible Load Activated</span>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardHeader className="border-b border-slate-100 bg-slate-50/50">
              <CardTitle className="flex items-center text-lg font-bold text-slate-800">
                <Settings className="w-5 h-5 mr-2 text-blue-600" />
                Optimization Results: Balanced Plan
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {isOptimized ? (
                <div className="h-[400px] w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        cursor={{fill: '#f1f5f9'}}
                      />
                      <Legend wrapperStyle={{ paddingTop: '20px' }} />
                      <Bar dataKey="Before" fill="#94a3b8" radius={[4, 4, 0, 0]} name="Baseline (%)" />
                      <Bar dataKey="After" fill="#10b981" radius={[4, 4, 0, 0]} name="KitaAI Optimized (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[400px] flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
                  <Zap className="w-12 h-12 mb-4 text-slate-300" />
                  <p>Run the Balanced Plan to view impact analytics.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
