"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { VitalsChart } from "@/components/charts/VitalsChart";
import { AlertsLog } from "@/components/dashboard/AlertsLog";
import { getAlerts, getPatient, getVitalsTimeline, recordVitals, type AlertLog, type Patient, type Vitals } from "@/lib/api";

export default function NursePatientDetailPage() {
  const params = useParams();
  const patientId = params.patientId as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [vitals, setVitals] = useState<Vitals[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [form, setForm] = useState({ heart_rate: "", bp_systolic: "", bp_diastolic: "", spo2: "", temperature: "", respiration: "" });

  async function loadAll() {
    const [p, v, a] = await Promise.all([getPatient(patientId), getVitalsTimeline(patientId), getAlerts(patientId)]);
    setPatient(p);
    setVitals(v);
    setAlerts(a);
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId]);

  async function handleAdd() {
    const payload: Record<string, number> = {};
    Object.entries(form).forEach(([k, v]) => { if (v !== "") payload[k] = Number(v); });
    const newVital = await recordVitals(patientId, payload);
    setVitals((prev) => [...prev, newVital]);
    setForm({ heart_rate: "", bp_systolic: "", bp_diastolic: "", spo2: "", temperature: "", respiration: "" });
    const a = await getAlerts(patientId); // pick up any new critical alert triggered by this reading
    setAlerts(a);
  }

  return (
    <DashboardShell allowedRoles={["nurse", "admin"]} title={patient ? patient.full_name : "Patient"}>
      <div className="flex flex-col gap-6">
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Vitals timeline</p>
          <VitalsChart data={vitals} />
        </Card>
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Record a reading</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-6">
            <Input label="Heart rate" type="number" value={form.heart_rate} onChange={(e) => setForm({ ...form, heart_rate: e.target.value })} />
            <Input label="BP systolic" type="number" value={form.bp_systolic} onChange={(e) => setForm({ ...form, bp_systolic: e.target.value })} />
            <Input label="BP diastolic" type="number" value={form.bp_diastolic} onChange={(e) => setForm({ ...form, bp_diastolic: e.target.value })} />
            <Input label="SpO2" type="number" value={form.spo2} onChange={(e) => setForm({ ...form, spo2: e.target.value })} />
            <Input label="Temperature" type="number" step="0.1" value={form.temperature} onChange={(e) => setForm({ ...form, temperature: e.target.value })} />
            <Input label="Respiration" type="number" value={form.respiration} onChange={(e) => setForm({ ...form, respiration: e.target.value })} />
          </div>
          <Button className="mt-4" onClick={handleAdd}>Add reading</Button>
          <p className="mt-2 text-xs text-gray-400">Critical readings automatically trigger an emergency alert to the patient&apos;s emergency contact.</p>
        </Card>
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Alert history</p>
          <AlertsLog alerts={alerts} />
        </Card>
      </div>
    </DashboardShell>
  );
}
