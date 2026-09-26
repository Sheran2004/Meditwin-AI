"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { runClinicalDecisionSupport, type ClinicalDecisionResult } from "@/lib/api";

export function ClinicalDecisionSupportPanel() {
  const [symptoms, setSymptoms] = useState("");
  const [context, setContext] = useState("");
  const [result, setResult] = useState<ClinicalDecisionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setIsLoading(true);
    setError(null);
    try {
      setResult(await runClinicalDecisionSupport(symptoms, context));
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Request failed. Is GROQ_API_KEY set in backend/.env?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Symptoms</label>
        <textarea
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          rows={3}
          placeholder="e.g. persistent cough for 2 weeks, mild fever in the evenings, unintentional weight loss"
          className="mt-1.5 w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-brand-900/40 dark:text-gray-100"
        />
        <label className="mt-3 block text-sm font-medium text-gray-700 dark:text-gray-300">Patient context (optional)</label>
        <input
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="e.g. 45yo male, smoker, known hypertension"
          className="mt-1.5 w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-brand-900/40 dark:text-gray-100"
        />
        <Button className="mt-4" onClick={handleRun} isLoading={isLoading} disabled={symptoms.trim().length < 3}>
          Get AI suggestion
        </Button>
        {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </Card>

      {result && (
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Likely conditions</p>
          <div className="flex flex-col gap-2">
            {result.likely_conditions.map((c, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm dark:bg-white/5">
                <span className="text-gray-800 dark:text-gray-200">{c.condition}</span>
                <span className="font-medium text-brand-600 dark:text-brand-100">{c.confidence_pct}%</span>
              </div>
            ))}
          </div>

          {result.recommended_tests.length > 0 && (
            <>
              <p className="mb-2 mt-5 text-sm font-medium text-gray-700 dark:text-gray-200">Recommended tests</p>
              <ul className="list-inside list-disc text-sm text-gray-600 dark:text-gray-300">
                {result.recommended_tests.map((t, i) => <li key={i}>{t}</li>)}
              </ul>
            </>
          )}

          {result.red_flags.length > 0 && (
            <>
              <p className="mb-2 mt-5 text-sm font-medium text-red-600 dark:text-red-400">Red flags</p>
              <ul className="list-inside list-disc text-sm text-red-600 dark:text-red-400">
                {result.red_flags.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </>
          )}

          <p className="mt-5 text-xs italic text-gray-400">{result.disclaimer}</p>
        </Card>
      )}
    </div>
  );
}
