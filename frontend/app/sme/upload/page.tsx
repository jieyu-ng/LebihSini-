"use client";

import Link from "next/link";
import { UploadCloud, CheckCircle, AlertCircle, FileText } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useCaseStore } from "@/lib/store";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadVerifyPage() {
  const { billData, setAgentProgress } = useCaseStore();
  const [uploaded, setUploaded] = useState(false);
  const router = useRouter();

  const handleSimulateUpload = () => {
    setUploaded(true);
    setAgentProgress({ billVerified: true });
  };

  const handleContinue = () => {
    router.push("/sme/onboarding");
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Upload your Electricity Bill</h1>
          <p className="text-slate-500 mt-2">Let our KitaAI Energy Coordinator analyze your usage patterns.</p>
        </div>

        {!uploaded ? (
          <div 
            onClick={handleSimulateUpload}
            className="border-2 border-dashed border-emerald-300 bg-emerald-50 rounded-2xl p-12 text-center cursor-pointer hover:bg-emerald-100 transition-colors"
          >
            <div className="bg-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm text-emerald-600">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-slate-800">Drag & drop your TNB Bill PDF</h3>
            <p className="text-sm text-slate-500 mt-2">or click to browse from your device</p>
          </div>
        ) : (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center gap-4 bg-emerald-100/50 p-4 rounded-xl border border-emerald-200">
              <FileText className="w-8 h-8 text-emerald-600" />
              <div>
                <h3 className="font-semibold text-slate-800">TNB_Bill_Oct2026.pdf</h3>
                <p className="text-sm text-emerald-600 font-medium">Successfully processed by KitaAI</p>
              </div>
            </div>

            <Card className="shadow-sm">
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead>Extracted Field</TableHead>
                      <TableHead>Detected Value</TableHead>
                      <TableHead className="text-right">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-medium">Billing Month</TableCell>
                      <TableCell>{billData.billingMonth}</TableCell>
                      <TableCell className="text-right"><Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100">Verified</Badge></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Consumption</TableCell>
                      <TableCell>{billData.consumptionKwh} kWh</TableCell>
                      <TableCell className="text-right"><Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100">Verified</Badge></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Total Amount</TableCell>
                      <TableCell>RM {billData.totalAmountRm.toFixed(2)}</TableCell>
                      <TableCell className="text-right"><Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100">Please check</Badge></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Maximum Demand</TableCell>
                      <TableCell>{billData.maximumDemandKw} kW</TableCell>
                      <TableCell className="text-right"><Badge className="bg-slate-100 text-slate-600 hover:bg-slate-100">Missing</Badge></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <div className="flex justify-end gap-4 pt-4">
              <Button variant="outline" onClick={() => setUploaded(false)}>Re-upload</Button>
              <Button onClick={handleContinue} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                Confirm & Continue
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
