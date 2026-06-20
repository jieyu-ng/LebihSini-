"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import Container from "@/components/ui/container";
import PageHeader from "@/components/ui/pageHeader";
import Card from "@/components/ui/card";
import Button from "@/components/ui/button";
import { sessionStore } from "@/lib/session";
import type { RequestDraft } from "@/types/requirement";

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState(
    "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
  );

  function submitDraft(draft: RequestDraft) {
    sessionStore.setDraft(draft);
    router.push("/confirm");
  }

  function handleSubmit() {
    if (!input.trim()) return;

    submitDraft({
      text: input,
      inputLanguage: /esok|kelabu|mesin/i.test(input) ? "ms-MY" : "en-MY",
      sourceType: "typed_text",
      contentReference: /esok|kelabu|mesin/i.test(input)
        ? "demo://voice-note/site-c/request-001"
        : "demo://typed/en/request-001",
      referenceDatetime: "2026-06-20T09:00:00+08:00",
      isDemoFixture: /esok|kelabu|mesin/i.test(input) || /need 500 grey/i.test(input),
      fixtureLabel: /esok|kelabu|mesin/i.test(input)
        ? "Demo fixture: Bahasa request"
        : "Demo fixture: English request",
    });
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
          <div className="text-sm text-gray-500">
            This screen supports the prepared Bahasa demo flow and typed text submissions.
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

          <button
            onClick={() =>
              submitDraft({
                text: "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
                inputLanguage: "ms-MY",
                sourceType: "voice_note",
                contentReference: "demo://voice-note/site-c/request-001",
                referenceDatetime: "2026-06-20T09:00:00+08:00",
                isDemoFixture: true,
                fixtureLabel: "Demo fixture: Bahasa request",
              })
            }
            className="w-full border border-black rounded-xl py-3 text-sm font-medium"
          >
            Use Prepared Bahasa Demo
          </button>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3 mt-4 opacity-60">
        <Card>Scan material</Card>
        <Card>Add equipment</Card>
      </div>
    </Container>
  );
}
