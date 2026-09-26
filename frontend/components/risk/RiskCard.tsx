import clsx from "clsx";
import type { RiskAssessment } from "@/lib/api";

function riskColor(pct: number) {
  if (pct >= 70) return "risk-high";
  if (pct >= 40) return "risk-medium";
  return "risk-low";
}

const LABELS: Record<string, string> = {
  heart_attack: "Heart attack risk",
  diabetes: "Diabetes risk",
};

export function RiskCard({ assessment }: { assessment: RiskAssessment }) {
  const level = riskColor(assessment.score_pct);
  return (
    <div
      className={clsx(
        "rounded-xl border p-5",
        level === "risk-high" && "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/30",
        level === "risk-medium" && "border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30",
        level === "risk-low" && "border-brand-100 bg-brand-50 dark:border-brand-900 dark:bg-brand-950/30"
      )}
    >
      <div className="flex items-baseline justify-between">
        <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
          {LABELS[assessment.risk_type] ?? assessment.risk_type}
        </p>
        <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{assessment.score_pct}%</p>
      </div>
      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        Confidence: {assessment.confidence}% · {new Date(assessment.computed_at).toLocaleString()}
      </p>
      <p className="mt-3 text-sm text-gray-700 dark:text-gray-300">{assessment.reasoning}</p>
    </div>
  );
}
