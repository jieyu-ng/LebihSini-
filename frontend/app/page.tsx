"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import Container from "@/components/ui/container";
import PageHeader from "@/components/ui/pageHeader";
import Card from "@/components/ui/card";
import Button from "@/components/ui/button";

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState("");

  function handleSubmit() {
    if (!input.trim()) return;

    localStorage.setItem("mockRequest", input);
    router.push("/confirm");
  }

  return (
    <Container>
      <PageHeader
        title="LebihSini GreenProof"
        subtitle="Multi-source construction optimisation system"
      />

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
            placeholder="e.g. need 500 tiles and tile cutter tomorrow"
          />

          <Button onClick={handleSubmit}>
            Submit Request
          </Button>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3 mt-4 opacity-60">
        <Card>Scan material</Card>
        <Card>Add equipment</Card>
      </div>
    </Container>
  );
}