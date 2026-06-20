import Link from "next/link";
import { ArrowRight, Building, Map } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6">
      <div className="max-w-3xl text-center space-y-8">
        <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Your electricity bill tells you what you owe.
          <span className="block text-emerald-600 mt-2">EnergiKita tells you what to do next.</span>
        </h1>
        
        <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
          The AI-orchestrated bill-to-flexibility platform for Malaysian SMEs and Community Energy Operators.
        </p>

        <div className="grid sm:grid-cols-2 gap-6 pt-8 max-w-2xl mx-auto">
          <Link href="/sme/upload" className="group flex flex-col items-center p-8 bg-white rounded-2xl shadow-sm hover:shadow-lg border border-slate-200 transition-all">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Building className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">Analyse my business</h3>
            <p className="text-slate-500 text-center mb-4 text-sm leading-relaxed">Discover your energy flexibility and save on bills.</p>
            <div className="flex items-center text-emerald-600 font-medium mt-auto group-hover:translate-x-1 transition-transform">
              Get Started <ArrowRight className="ml-2 w-4 h-4" />
            </div>
          </Link>

          <Link href="/operator" className="group flex flex-col items-center p-8 bg-white rounded-2xl shadow-sm hover:shadow-lg border border-slate-200 transition-all">
            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Map className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">Plan a solar community</h3>
            <p className="text-slate-500 text-center mb-4 text-sm leading-relaxed">Optimize local grid distribution and identify flexible loads.</p>
            <div className="flex items-center text-blue-600 font-medium mt-auto group-hover:translate-x-1 transition-transform">
              View Map <ArrowRight className="ml-2 w-4 h-4" />
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}