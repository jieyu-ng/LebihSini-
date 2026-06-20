"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import Container from "@/components/ui/container";
import PageHeader from "@/components/ui/pageHeader";
import Card from "@/components/ui/card";
import Button from "@/components/ui/button";

export default function HomePage() {
  const router = useRouter();

  const [input, setInput] = useState(
    "Need 500 grey porcelain tiles 600x600 and 1 tile cutter by tomorrow 11am for Site C"
  );

  function handleSubmit() {
    localStorage.setItem("mockRequest", input);
    router.push("/confirm");
  }

  return (
    <Container>
      <PageHeader
        title="LebihSini GreenProof"
        subtitle="Multi-source construction optimisation system"
      />

      {/* PRIMARY ACTION */}
      <Card>
        <div className="space-y-3">
          <div className="font-medium">
            Submit resource need
          </div>

          <textarea
            className="w-full border rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            rows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <Button onClick={handleSubmit}>
            Submit Request
          </Button>
        </div>
      </Card>

      {/* SECONDARY ACTIONS (DEMO ONLY) */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        <Card>
          <div className="opacity-50 text-sm text-center">
            Scan material 
          </div>
        </Card>

        <Card>
          <div className="opacity-50 text-sm text-center">
            Add idle equipment 
          </div>
        </Card>
      </div>

      {/* VIEW RECOMMENDATIONS */}
      <div className="mt-3">
        <Card>
          <Button
            variant="secondary"
            onClick={() => router.push("/resources")}
          >
            View Recommendations →
          </Button>
        </Card>
      </div>
    </Container>
  );
}