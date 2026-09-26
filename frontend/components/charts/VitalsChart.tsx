"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { Vitals } from "@/lib/api";

interface VitalsChartProps {
  data: Vitals[];
}

export function VitalsChart({ data }: VitalsChartProps) {
  const chartData = data.map((v) => ({
    time: new Date(v.recorded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    "Heart rate": v.heart_rate,
    "SpO2": v.spo2,
    "Systolic BP": v.bp_systolic,
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-gray-400">
        No vitals recorded yet — add the first reading below.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-800" />
        <XAxis dataKey="time" fontSize={12} tickLine={false} />
        <YAxis fontSize={12} tickLine={false} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #e5e7eb" }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line type="monotone" dataKey="Heart rate" stroke="#0f7d67" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="SpO2" stroke="#1f9d84" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="Systolic BP" stroke="#c9432f" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
