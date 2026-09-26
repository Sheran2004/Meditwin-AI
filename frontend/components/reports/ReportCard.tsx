import type { Report } from "@/lib/api";

export function ReportCard({ report }: { report: Report }) {
  const items = report.abnormal_values?.items ?? [];
  return (
    <div className="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-400">{new Date(report.uploaded_at).toLocaleString()}</p>
        <span className="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-600 dark:bg-brand-900/40 dark:text-brand-100">
          {report.language === "hi" ? "Hindi" : "English"}
        </span>
      </div>
      <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">{report.ai_summary?.summary}</p>

      {items.length > 0 ? (
        <table className="mt-4 w-full text-left text-sm">
          <thead>
            <tr className="text-xs text-gray-400">
              <th className="pb-2 font-medium">Test</th>
              <th className="pb-2 font-medium">Value</th>
              <th className="pb-2 font-medium">Normal range</th>
              <th className="pb-2 font-medium">What it means</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={i} className="border-t border-gray-100 dark:border-gray-800">
                <td className="py-2 font-medium text-gray-800 dark:text-gray-200">{item.name}</td>
                <td className="py-2 text-red-600 dark:text-red-400">{item.value}</td>
                <td className="py-2 text-gray-500 dark:text-gray-400">{item.normal_range}</td>
                <td className="py-2 text-gray-600 dark:text-gray-300">{item.explanation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="mt-3 text-xs text-brand-500">No abnormal values detected.</p>
      )}
    </div>
  );
}
