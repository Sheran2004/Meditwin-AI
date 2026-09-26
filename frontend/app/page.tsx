"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { listPatients, type Patient } from "@/lib/api";

export default function NursePatientListPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    listPatients().then(setPatients).finally(() => setIsLoading(false));
  }, []);

  return (
    <DashboardShell allowedRoles={["nurse", "admin"]} title="Patients — vitals rounds">
      {isLoading && <p className="text-sm text-gray-400">Loading patients…</p>}
      {!isLoading && patients.length === 0 && (
        <Card><p className="text-sm text-gray-500 dark:text-gray-400">No patient profiles yet.</p></Card>
      )}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {patients.map((p) => (
          <Link key={p.id} href={`/nurse/patients/${p.id}`}>
            <Card className="cursor-pointer transition-shadow hover:shadow-md">
              <p className="font-medium text-gray-900 dark:text-gray-100">{p.full_name}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{p.blood_group ?? "—"} · {p.gender ?? "—"}</p>
              <p className="mt-2 text-xs text-brand-500">Record vitals →</p>
            </Card>
          </Link>
        ))}
      </div>
    </DashboardShell>
  );
}
