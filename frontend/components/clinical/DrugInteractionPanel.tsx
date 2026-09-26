"use client";

import clsx from "clsx";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { checkDrugInteractions, type DrugInteractionResult } from "@/lib/api";

export function DrugInteractionPanel() {
  const [medsInput, setMedsInput] = useState("");
  const [result, setResult] = useState<DrugInteractionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCheck() {
    const medicines = medsInput.split(",").map((m) => m.trim()).filter(Boolean);
    if (medicines.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      setResult(await checkDrugInteractions(medicines));
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Request failed. Is GROQ_API_KEY set in backend/.env?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Medicines (comma-separated)</label>
        <input
          value={medsInput}
          onChange={(e) => setMedsInput(e.target.value)}
          placeholder="e.g. warfarin, aspirin, metformin"
          className="mt-1.5 w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-brand-900/40 dark:text-gray-100"
        />
        <Button className="mt-4" onClick={handleCheck} isLoading={isLoading} disabled={medsInput.trim().length < 2}>
          Check interactions
        </Button>
        {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </Card>

      {result && (
        <Card>
          {result.interactions.length === 0 ? (
            <p className="text-sm text-brand-500">No known dangerous interactions found in this combination.</p>
          ) : (
            <div className="flex flex-col gap-2">
              {result.interactions.map((i, idx) => (
                <div
                  key={idx}
                  className={clsx(
                    "rounded-lg border p-3 text-sm",
                    i.severity === "high" && "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/30",
                    i.severity === "medium" && "border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30"
                  )}
                >
                  <p className="font-medium text-gray-800 dark:text-gray-100">
                    {i.drug_a} + {i.drug_b} <span className="uppercase text-xs">({i.severity})</span>
                  </p>
                  <p className="mt-1 text-gray-600 dark:text-gray-300">{i.note}</p>
                </div>
              ))}
            </div>
          )}

          {(result.pregnancy_risk_drugs.length > 0 || result.kidney_risk_drugs.length > 0 || result.liver_risk_drugs.length > 0) && (
            <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
              {result.pregnancy_risk_drugs.length > 0 && <span>Pregnancy risk: {result.pregnancy_risk_drugs.join(", ")}</span>}
              {result.kidney_risk_drugs.length > 0 && <span>Kidney risk: {result.kidney_risk_drugs.join(", ")}</span>}
              {result.liver_risk_drugs.length > 0 && <span>Liver risk: {result.liver_risk_drugs.join(", ")}</span>}
            </div>
          )}

          {result.plain_language_summary && (
            <p className="mt-4 text-sm text-gray-700 dark:text-gray-300">{result.plain_language_summary}</p>
          )}

          {result.alternative_suggestions.length > 0 && (
            <>
              <p className="mb-2 mt-4 text-sm font-medium text-gray-700 dark:text-gray-200">Suggested alternatives</p>
              <ul className="list-inside list-disc text-sm text-gray-600 dark:text-gray-300">
                {result.alternative_suggestions.map((s, i) => (
                  <li key={i}>Replace <b>{s.replace}</b> with <b>{s.with}</b> — {s.reason}</li>
                ))}
              </ul>
            </>
          )}

          <p className="mt-5 text-xs italic text-gray-400">{result.disclaimer}</p>
        </Card>
      )}
    </div>
  );
}
