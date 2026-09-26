"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { VitalsChart } from "@/components/charts/VitalsChart";
import { RiskCard } from "@/components/risk/RiskCard";
import { RiskAssessmentForms } from "@/components/risk/RiskAssessmentForms";
import { ReportUpload } from "@/components/reports/ReportUpload";
import { ReportCard } from "@/components/reports/ReportCard";
import { ClinicalDecisionSupportPanel } from "@/components/clinical/ClinicalDecisionSupportPanel";
import { DrugInteractionPanel } from "@/components/clinical/DrugInteractionPanel";
import { AlertsLog } from "@/components/dashboard/AlertsLog";
import { ImagingPanel } from "@/components/imaging/ImagingPanel";
import {
  getAlerts, getPatient, getRiskHistory, getVitalsTimeline, listReports, recordVitals,
  type AlertLog, type Patient, type Report, type RiskAssessment, type Vitals,
} from "@/lib/api";

type Tab = "vitals" | "risk" | "reports" | "clinical" | "drugs" | "imaging" | "alerts";

export default function PatientDetailPage() {
  const params = useParams();
  const patientId = params.patientId as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [vitals, setVitals] = useState<Vitals[]>([]);
  const [riskHistory, setRiskHistory] = useState<RiskAssessment[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [tab, setTab] = useState<Tab>("vitals");
  const [vitalsForm, setVitalsForm] = useState({ heart_rate: "", bp_systolic: "", bp_diastolic: "", spo2: "", temperature: "" });

  async function loadAll() {
    const [p, v, r, rep, al] = await Promise.all([
      getPatient(patientId),
      getVitalsTimeline(patientId),
      getRiskHistory(patientId),
      listReports(patientId),
      getAlerts(patientId),
    ]);
    setPatient(p);
    setVitals(v);
    setRiskHistory(r);
    setReports(rep);
    setAlerts(al);
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId]);

  async function handleAddVitals() {
    const payload: Record<string, number> = {};
    Object.entries(vitalsForm).forEach(([k, v]) => {
      if (v !== "") payload[k] = Number(v);
    });
    const newVital = await recordVitals(patientId, payload);
    setVitals((prev) => [...prev, newVital]);
    setVitalsForm({ heart_rate: "", bp_systolic: "", bp_diastolic: "", spo2: "", temperature: "" });
    getAlerts(patientId).then(setAlerts); // pick up any emergency alert the backend just triggered
  }

  return (
    <DashboardShell allowedRoles={["doctor", "admin"]} title={patient ? patient.full_name : "Patient"}>
      {patient && (
        <p className="mb-6 -mt-4 text-sm text-gray-500 dark:text-gray-400">
          {patient.email} · {patient.gender ?? "—"} · {patient.blood_group ?? "—"} · DOB {patient.date_of_birth ?? "—"}
        </p>
      )}

      <div className="mb-6 flex gap-2">
        <Button variant={tab === "vitals" ? "primary" : "ghost"} onClick={() => setTab("vitals")}>Digital twin / vitals</Button>
        <Button variant={tab === "risk" ? "primary" : "ghost"} onClick={() => setTab("risk")}>Risk prediction</Button>
        <Button variant={tab === "reports" ? "primary" : "ghost"} onClick={() => setTab("reports")}>Report analyzer</Button>
        <Button variant={tab === "clinical" ? "primary" : "ghost"} onClick={() => setTab("clinical")}>Decision support</Button>
        <Button variant={tab === "drugs" ? "primary" : "ghost"} onClick={() => setTab("drugs")}>Drug interactions</Button>
        <Button variant={tab === "imaging" ? "primary" : "ghost"} onClick={() => setTab("imaging")}>Medical imaging</Button>
        <Button variant={tab === "alerts" ? "primary" : "ghost"} onClick={() => setTab("alerts")}>
          Alerts {alerts.length > 0 && `(${alerts.length})`}
        </Button>
      </div>

      {tab === "vitals" && (
        <div className="flex flex-col gap-6">
          <Card>
            <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Vitals timeline</p>
            <VitalsChart data={vitals} />
          </Card>
          <Card>
            <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Record a new reading</p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
              <Input label="Heart rate" type="number" value={vitalsForm.heart_rate} onChange={(e) => setVitalsForm({ ...vitalsForm, heart_rate: e.target.value })} />
              <Input label="BP systolic" type="number" value={vitalsForm.bp_systolic} onChange={(e) => setVitalsForm({ ...vitalsForm, bp_systolic: e.target.value })} />
              <Input label="BP diastolic" type="number" value={vitalsForm.bp_diastolic} onChange={(e) => setVitalsForm({ ...vitalsForm, bp_diastolic: e.target.value })} />
              <Input label="SpO2" type="number" value={vitalsForm.spo2} onChange={(e) => setVitalsForm({ ...vitalsForm, spo2: e.target.value })} />
              <Input label="Temperature" type="number" step="0.1" value={vitalsForm.temperature} onChange={(e) => setVitalsForm({ ...vitalsForm, temperature: e.target.value })} />
            </div>
            <Button className="mt-4" onClick={handleAddVitals}>Add reading</Button>
          </Card>
        </div>
      )}

      {tab === "risk" && (
        <div className="flex flex-col gap-6">
          <Card>
            <RiskAssessmentForms patientId={patientId} onAssessed={(r) => setRiskHistory((prev) => [r, ...prev])} />
          </Card>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {riskHistory.map((r) => (
              <RiskCard key={r.id} assessment={r} />
            ))}
          </div>
        </div>
      )}

      {tab === "reports" && (
        <div className="flex flex-col gap-6">
          <Card>
            <ReportUpload patientId={patientId} onUploaded={(r) => setReports((prev) => [r, ...prev])} />
          </Card>
          <div className="flex flex-col gap-4">
            {reports.map((r) => (
              <ReportCard key={r.id} report={r} />
            ))}
          </div>
        </div>
      )}

      {tab === "clinical" && <ClinicalDecisionSupportPanel />}

      {tab === "drugs" && <DrugInteractionPanel />}

      {tab === "imaging" && <ImagingPanel patientId={patientId} />}

      {tab === "alerts" && (
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Emergency alert history</p>
          <AlertsLog alerts={alerts} />
        </Card>
      )}
    </DashboardShell>
  );
}
