import clsx from "clsx";
import type { AlertLog } from "@/lib/api";

export function AlertsLog({ alerts }: { alerts: AlertLog[] }) {
  if (alerts.length === 0) {
    return <p className="text-sm text-gray-400">No emergency alerts triggered yet.</p>;
  }
  return (
    <div className="flex flex-col gap-2">
      {alerts.map((a) => (
        <div key={a.id} className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2 text-sm dark:border-gray-800">
          <div>
            <p className="font-medium text-gray-800 dark:text-gray-200">
              {a.trigger_vital.replace("_", " ")}: {a.threshold}
            </p>
            <p className="text-xs text-gray-400">{new Date(a.sent_at).toLocaleString()}</p>
          </div>
          <span
            className={clsx(
              "rounded-full px-2 py-0.5 text-xs font-medium",
              a.sent_via === "sms"
                ? "bg-brand-50 text-brand-600 dark:bg-brand-900/40 dark:text-brand-100"
                : "bg-gray-100 text-gray-500 dark:bg-white/10 dark:text-gray-400"
            )}
          >
            {a.sent_via === "sms" ? "SMS sent" : "Logged only"}
          </span>
        </div>
      ))}
    </div>
  );
}
