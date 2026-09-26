"use client";

import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { VoiceAssistant } from "@/components/voice/VoiceAssistant";

export default function DoctorDashboardPage() {
  return (
    <DashboardShell allowedRoles={["doctor", "admin"]} title="Doctor dashboard">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <p className="text-sm text-gray-500 dark:text-gray-400">Manage patients</p>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            View digital twins, run AI risk assessments, and analyze uploaded reports.
          </p>
          <Link href="/doctor/patients">
            <Button className="mt-4">Open patient list</Button>
          </Link>
        </Card>
        <Card>
          <p className="text-sm text-gray-500 dark:text-gray-400">Hospital analytics</p>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Live patient counts, risk breakdowns, and alert trends — all real database aggregates.
          </p>
          <Link href="/admin">
            <Button className="mt-4">Open analytics</Button>
          </Link>
        </Card>
        <Card>
          <p className="mb-3 text-sm text-gray-500 dark:text-gray-400">Voice assistant</p>
          <VoiceAssistant />
        </Card>
      </div>
    </DashboardShell>
  );
}
