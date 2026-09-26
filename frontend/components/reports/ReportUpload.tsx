"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { uploadReport, type Report } from "@/lib/api";

interface Props {
  patientId: string;
  onUploaded: (report: Report) => void;
}

export function ReportUpload({ patientId, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<"en" | "hi">("en");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    try {
      const report = await uploadReport(patientId, file, language);
      onUploaded(report);
      setFile(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Upload failed. Is GROQ_API_KEY set in backend/.env?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
      <div className="flex-1">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Upload lab report (PDF)</label>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mt-1.5 block w-full text-sm text-gray-600 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-brand-600 dark:text-gray-300"
        />
      </div>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as "en" | "hi")}
        className="rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm dark:border-gray-700 dark:bg-brand-900/40 dark:text-gray-100"
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
      </select>
      <Button onClick={handleUpload} isLoading={isLoading} disabled={!file}>
        Analyze report
      </Button>
      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
