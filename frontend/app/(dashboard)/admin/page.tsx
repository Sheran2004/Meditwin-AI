"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { getHospitalAnalytics, type HospitalAnalytics } from "@/lib/api";

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <Card>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">{value}</p>
    </Card>
  );
}

export default function AdminDashboardPage() {
  const [data, setData] = useState<HospitalAnalytics | null>(null);

  useEffect(() => {
    getHospitalAnalytics().then(setData);
  }, []);

  return (
    <DashboardShell allowedRoles={["doctor", "admin"]} title="Hospital analytics">
      {!data && <p className="text-sm text-gray-400">Loading live stats…</p>}
      {data && (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            <StatCard label="Total patients" value={data.total_patients} />
            <StatCard label="Doctors" value={data.total_doctors} />
            <StatCard label="Vitals recorded" value={data.total_vitals_recorded} />
            <StatCard label="Reports analyzed" value={data.total_reports_analyzed} />
            <StatCard label="Total alerts" value={data.total_alerts} />
            <StatCard label="SMS alerts sent" value={data.sms_alerts_sent} />
            <StatCard label="High-risk patients (≥70%)" value={data.high_risk_patient_count} />
          </div>

          {data.risk_breakdown.length > 0 && (
            <Card>
              <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Average risk by type</p>
              <div className="flex flex-col gap-2">
                {data.risk_breakdown.map((r) => (
                  <div key={r.risk_type} className="flex items-center justify-between text-sm">
                    <span className="capitalize text-gray-600 dark:text-gray-300">{r.risk_type.replace("_", " ")}</span>
                    <span className="text-gray-500 dark:text-gray-400">{r.avg_score_pct}% avg · {r.assessment_count} assessments</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {data.alert_breakdown.length > 0 && (
            <Card>
              <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Most common alert triggers</p>
              <div className="flex flex-col gap-2">
                {data.alert_breakdown.map((a) => (
                  <div key={a.vital} className="flex items-center justify-between text-sm">
                    <span className="capitalize text-gray-600 dark:text-gray-300">{a.vital.replace("_", " ")}</span>
                    <span className="text-gray-500 dark:text-gray-400">{a.count}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          <p className="text-xs text-gray-400">
            Every figure above is a live query against the database — there is no mock data here.
          </p>
        </div>
      )}
    </DashboardShell>
  );
}
