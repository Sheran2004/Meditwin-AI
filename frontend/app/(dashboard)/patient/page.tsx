"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { VitalsChart } from "@/components/charts/VitalsChart";
import { RiskCard } from "@/components/risk/RiskCard";
import { ReportUpload } from "@/components/reports/ReportUpload";
import { ReportCard } from "@/components/reports/ReportCard";
import {
  createMyPatientProfile, getRiskHistory, getVitalsTimeline, listPatients, listReports, recordVitals,
  type Patient, type Report, type RiskAssessment, type Vitals,
} from "@/lib/api";

export default function PatientDashboardPage() {
  const [patient, setPatient] = useState<Patient | null | undefined>(undefined); // undefined = loading
  const [vitals, setVitals] = useState<Vitals[]>([]);
  const [riskHistory, setRiskHistory] = useState<RiskAssessment[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [profileForm, setProfileForm] = useState({ gender: "", blood_group: "", height_cm: "", weight_kg: "", emergency_contact_name: "", emergency_contact_phone: "" });
  const [vitalsForm, setVitalsForm] = useState({ heart_rate: "", bp_systolic: "", bp_diastolic: "", spo2: "" });

  async function loadProfile() {
    const mine = await listPatients(); // backend already filters to "self" for a patient role
    const me = mine[0] ?? null;
    setPatient(me);
    if (me) {
      const [v, r, rep] = await Promise.all([getVitalsTimeline(me.id), getRiskHistory(me.id), listReports(me.id)]);
      setVitals(v);
      setRiskHistory(r);
      setReports(rep);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  async function handleCreateProfile() {
    await createMyPatientProfile({
      gender: profileForm.gender || undefined,
      blood_group: profileForm.blood_group || undefined,
      height_cm: profileForm.height_cm ? Number(profileForm.height_cm) : undefined,
      weight_kg: profileForm.weight_kg ? Number(profileForm.weight_kg) : undefined,
      emergency_contact_name: profileForm.emergency_contact_name || undefined,
      emergency_contact_phone: profileForm.emergency_contact_phone || undefined,
    });
    await loadProfile();
  }

  async function handleAddVitals() {
    if (!patient) return;
    const payload: Record<string, number> = {};
    Object.entries(vitalsForm).forEach(([k, v]) => {
      if (v !== "") payload[k] = Number(v);
    });
    const newVital = await recordVitals(patient.id, payload);
    setVitals((prev) => [...prev, newVital]);
    setVitalsForm({ heart_rate: "", bp_systolic: "", bp_diastolic: "", spo2: "" });
  }

  if (patient === undefined) {
    return (
      <DashboardShell allowedRoles={["patient"]} title="Your health overview">
        <p className="text-sm text-gray-400">Loading…</p>
      </DashboardShell>
    );
  }

  if (patient === null) {
    return (
      <DashboardShell allowedRoles={["patient"]} title="Set up your digital twin">
        <Card className="max-w-md">
          <p className="mb-4 text-sm text-gray-600 dark:text-gray-300">
            One-time setup — this creates your patient profile so your doctor and the AI modules can track your health.
          </p>
          <div className="flex flex-col gap-3">
            <Input label="Gender" value={profileForm.gender} onChange={(e) => setProfileForm({ ...profileForm, gender: e.target.value })} />
            <Input label="Blood group" value={profileForm.blood_group} onChange={(e) => setProfileForm({ ...profileForm, blood_group: e.target.value })} />
            <Input label="Height (cm)" type="number" value={profileForm.height_cm} onChange={(e) => setProfileForm({ ...profileForm, height_cm: e.target.value })} />
            <Input label="Weight (kg)" type="number" value={profileForm.weight_kg} onChange={(e) => setProfileForm({ ...profileForm, weight_kg: e.target.value })} />
            <Input label="Emergency contact name" value={profileForm.emergency_contact_name} onChange={(e) => setProfileForm({ ...profileForm, emergency_contact_name: e.target.value })} />
            <Input label="Emergency contact phone (with country code, e.g. +91...)" value={profileForm.emergency_contact_phone} onChange={(e) => setProfileForm({ ...profileForm, emergency_contact_phone: e.target.value })} />
            <Button onClick={handleCreateProfile}>Create my profile</Button>
          </div>
        </Card>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell allowedRoles={["patient"]} title="Your health overview">
      <div className="flex flex-col gap-6">
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Your vitals timeline</p>
          <VitalsChart data={vitals} />
        </Card>

        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Log a reading</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Input label="Heart rate" type="number" value={vitalsForm.heart_rate} onChange={(e) => setVitalsForm({ ...vitalsForm, heart_rate: e.target.value })} />
            <Input label="BP systolic" type="number" value={vitalsForm.bp_systolic} onChange={(e) => setVitalsForm({ ...vitalsForm, bp_systolic: e.target.value })} />
            <Input label="BP diastolic" type="number" value={vitalsForm.bp_diastolic} onChange={(e) => setVitalsForm({ ...vitalsForm, bp_diastolic: e.target.value })} />
            <Input label="SpO2" type="number" value={vitalsForm.spo2} onChange={(e) => setVitalsForm({ ...vitalsForm, spo2: e.target.value })} />
          </div>
          <Button className="mt-4" onClick={handleAddVitals}>Add reading</Button>
        </Card>

        {riskHistory.length > 0 && (
          <div>
            <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Your risk assessments</p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {riskHistory.map((r) => <RiskCard key={r.id} assessment={r} />)}
            </div>
          </div>
        )}

        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Upload a lab report for AI analysis</p>
          <ReportUpload patientId={patient.id} onUploaded={(r) => setReports((prev) => [r, ...prev])} />
        </Card>
        <div className="flex flex-col gap-4">
          {reports.map((r) => <ReportCard key={r.id} report={r} />)}
        </div>
      </div>
    </DashboardShell>
  );
}
