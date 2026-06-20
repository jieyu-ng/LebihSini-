"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Badge from "@/components/ui/badge";
import Container from "@/components/ui/container";
import Card from "@/components/ui/card";
import PageHeader from "@/components/ui/pageHeader";
import { confirmExtraction, extractRequest } from "@/lib/api";
import { sessionStore } from "@/lib/session";
import type { StructuredExtractionResponse } from "@/types/requirement";

export default function ConfirmPage() {
  const router = useRouter();
  const [loadingMessage, setLoadingMessage] = useState("Reading your request...");
  const [extraction, setExtraction] = useState<StructuredExtractionResponse | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string | number | boolean | null>>({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadExtraction() {
      const draft = sessionStore.getDraft();
      if (!draft) {
        if (active) {
          setError("No request draft was found. Please submit a request first.");
        }
        return;
      }
      try {
        setLoadingMessage("Extracting material specifications...");
        const result = await extractRequest(draft);
        if (!active) {
          return;
        }
        sessionStore.setExtraction(result);
        setExtraction(result);
        setFormValues(result.normalized_demand);
      } catch (err) {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Unable to extract the request.");
      }
    }

    loadExtraction();

    return () => {
      active = false;
    };
  }, []);

  if (!extraction && !error) {
    return (
      <Container>
        <div className="min-h-[60vh] flex justify-center items-center">
          <div className="text-center space-y-3">
            <div className="text-lg font-medium">{loadingMessage}</div>
            <div className="text-sm text-gray-500">
              AI is analysing your request through the backend extraction pipeline.
            </div>
          </div>
        </div>
      </Container>
    );
  }

  async function handleConfirm() {
    if (!extraction) {
      return;
    }
    try {
      setSubmitting(true);
      setError("");
      const confirmation = await confirmExtraction(
        extraction.extraction_id,
        formValues,
      );
      sessionStore.setConfirmation(confirmation);
      router.push("/resources");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to confirm the extraction.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Container>
      <div className="space-y-4">
        <PageHeader
          title="Confirm Requirement"
          subtitle="Review extracted fields, confidence, and missing information before generating the plan."
        />

        {error ? (
          <Card>
            <div className="space-y-3">
              <div className="text-sm text-red-600">{error}</div>
              <button
                onClick={() => router.push("/")}
                className="w-full bg-black text-white py-3 rounded-xl"
              >
                Back to Request
              </button>
            </div>
          </Card>
        ) : null}

        {sessionStore.getDraft()?.isDemoFixture ? (
          <Card>
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm text-gray-600">
                {sessionStore.getDraft()?.fixtureLabel}
              </div>
              <Badge label="Demo fixture" type="gray" />
            </div>
          </Card>
        ) : null}

        {extraction ? (
          <Card>
            <div className="space-y-3">
              {extraction.extracted_fields.map((field) => (
                <div key={field.field_name} className="space-y-1">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-xs text-gray-500">{field.field_name}</div>
                    <Badge
                      label={`${field.confidence_label} ${field.confidence_score}`}
                      type={
                        field.confidence_label === "high"
                          ? "green"
                          : field.confidence_label === "medium"
                            ? "amber"
                            : "red"
                      }
                    />
                  </div>
                  <input
                    className="w-full border rounded-lg p-2 text-sm"
                    value={String(formValues[field.field_name] ?? "")}
                    onChange={(e) =>
                      setFormValues((current) => ({
                        ...current,
                        [field.field_name]: e.target.value,
                      }))
                    }
                  />
                  {field.warning ? (
                    <div className="text-xs text-amber-600">{field.warning}</div>
                  ) : null}
                </div>
              ))}
            </div>
          </Card>
        ) : null}

        {extraction?.warnings?.length ? (
          <Card>
            <h2 className="text-sm font-medium mb-2">Warnings</h2>
            <div className="space-y-2 text-sm text-gray-600">
              {extraction.warnings.map((warning, index) => (
                <div key={`${warning.code}-${index}`}>{warning.message}</div>
              ))}
            </div>
          </Card>
        ) : null}

        {extraction?.missing_critical_fields?.length ? (
          <Card>
            <h2 className="text-sm font-medium mb-2">Missing critical fields</h2>
            <div className="space-y-2 text-sm text-red-600">
              {extraction.missing_critical_fields.map((warning) => (
                <div key={warning.field_name}>{warning.message}</div>
              ))}
            </div>
          </Card>
        ) : null}

        <button
          onClick={handleConfirm}
          disabled={!extraction || submitting}
          className="w-full bg-black text-white py-3 rounded-lg disabled:opacity-50"
        >
          {submitting ? "Confirming..." : "Confirm & Continue"}
        </button>
      </div>
    </Container>
  );
}
