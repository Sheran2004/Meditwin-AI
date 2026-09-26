"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { listPatients, type Patient } from "@/lib/api";

export default function ReceptionDashboardPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    listPatients().then(setPatients).finally(() => setIsLoading(false));
  }, []);

  const filtered = patients.filter((p) =>
    p.full_name.toLowerCase().includes(search.toLowerCase()) || p.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <DashboardShell allowedRoles={["reception", "admin"]} title="Patient directory">
      <div className="mb-4 max-w-sm">
        <Input label="Search by name or email" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="e.g. Priya" />
      </div>

      {isLoading && <p className="text-sm text-gray-400">Loading…</p>}
      {!isLoading && filtered.length === 0 && (
        <Card><p className="text-sm text-gray-500 dark:text-gray-400">No matching patients.</p></Card>
      )}

      <div className="flex flex-col gap-2">
        {filtered.map((p) => (
          <Card key={p.id} className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">{p.full_name}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{p.email}</p>
            </div>
            <div className="text-right text-sm text-gray-500 dark:text-gray-400">
              <p>{p.blood_group ?? "Blood group —"}</p>
              <p>{p.emergency_contact_phone ?? "No emergency contact on file"}</p>
            </div>
          </Card>
        ))}
      </div>
    </DashboardShell>
  );
}
