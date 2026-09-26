"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  assessDiabetesRisk,
  assessHeartRisk,
  type DiabetesRiskInput,
  type HeartRiskInput,
  type RiskAssessment,
} from "@/lib/api";

const HEART_DEFAULTS: HeartRiskInput = {
  age: 45, sex: 1, cp: 0, trestbps: 120, chol: 200, fbs: 0,
  restecg: 0, thalach: 150, exang: 0, oldpeak: 0, slope: 1, ca: 0, thal: 2,
};

const DIABETES_DEFAULTS: DiabetesRiskInput = {
  Pregnancies: 0, Glucose: 100, BloodPressure: 70, SkinThickness: 20,
  Insulin: 80, BMI: 24, DiabetesPedigreeFunction: 0.4, Age: 30,
};

interface Props {
  patientId: string;
  onAssessed: (result: RiskAssessment) => void;
}

export function RiskAssessmentForms({ patientId, onAssessed }: Props) {
  const [tab, setTab] = useState<"heart" | "diabetes">("heart");
  const [heart, setHeart] = useState<HeartRiskInput>(HEART_DEFAULTS);
  const [diabetes, setDiabetes] = useState<DiabetesRiskInput>(DIABETES_DEFAULTS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runHeartAssessment() {
    setIsLoading(true);
    setError(null);
    try {
      onAssessed(await assessHeartRisk(patientId, heart));
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Assessment failed");
    } finally {
      setIsLoading(false);
    }
  }

  async function runDiabetesAssessment() {
    setIsLoading(true);
    setError(null);
    try {
      onAssessed(await assessDiabetesRisk(patientId, diabetes));
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Assessment failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      <div className="mb-4 flex gap-2">
        <Button variant={tab === "heart" ? "primary" : "ghost"} onClick={() => setTab("heart")}>
          Heart attack risk
        </Button>
        <Button variant={tab === "diabetes" ? "primary" : "ghost"} onClick={() => setTab("diabetes")}>
          Diabetes risk
        </Button>
      </div>

      {tab === "heart" && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <Input label="Age" type="number" value={heart.age} onChange={(e) => setHeart({ ...heart, age: +e.target.value })} />
          <Input label="Sex (1=M, 0=F)" type="number" min={0} max={1} value={heart.sex} onChange={(e) => setHeart({ ...heart, sex: +e.target.value })} />
          <Input label="Chest pain type (0-3)" type="number" min={0} max={3} value={heart.cp} onChange={(e) => setHeart({ ...heart, cp: +e.target.value })} />
          <Input label="Resting BP (mmHg)" type="number" value={heart.trestbps} onChange={(e) => setHeart({ ...heart, trestbps: +e.target.value })} />
          <Input label="Cholesterol (mg/dl)" type="number" value={heart.chol} onChange={(e) => setHeart({ ...heart, chol: +e.target.value })} />
          <Input label="Fasting sugar >120 (1/0)" type="number" min={0} max={1} value={heart.fbs} onChange={(e) => setHeart({ ...heart, fbs: +e.target.value })} />
          <Input label="Max heart rate" type="number" value={heart.thalach} onChange={(e) => setHeart({ ...heart, thalach: +e.target.value })} />
          <Input label="Exercise angina (1/0)" type="number" min={0} max={1} value={heart.exang} onChange={(e) => setHeart({ ...heart, exang: +e.target.value })} />
          <Input label="ST depression" type="number" step="0.1" value={heart.oldpeak} onChange={(e) => setHeart({ ...heart, oldpeak: +e.target.value })} />
          <Input label="Vessels colored (0-4)" type="number" min={0} max={4} value={heart.ca} onChange={(e) => setHeart({ ...heart, ca: +e.target.value })} />
          <Input label="Thal (0-3)" type="number" min={0} max={3} value={heart.thal} onChange={(e) => setHeart({ ...heart, thal: +e.target.value })} />
          <Input label="ECG slope (0-2)" type="number" min={0} max={2} value={heart.slope} onChange={(e) => setHeart({ ...heart, slope: +e.target.value })} />
          <div className="col-span-full mt-2">
            <Button onClick={runHeartAssessment} isLoading={isLoading}>Run heart attack risk assessment</Button>
          </div>
        </div>
      )}

      {tab === "diabetes" && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <Input label="Pregnancies" type="number" value={diabetes.Pregnancies} onChange={(e) => setDiabetes({ ...diabetes, Pregnancies: +e.target.value })} />
          <Input label="Glucose" type="number" value={diabetes.Glucose} onChange={(e) => setDiabetes({ ...diabetes, Glucose: +e.target.value })} />
          <Input label="Blood pressure" type="number" value={diabetes.BloodPressure} onChange={(e) => setDiabetes({ ...diabetes, BloodPressure: +e.target.value })} />
          <Input label="Skin thickness" type="number" value={diabetes.SkinThickness} onChange={(e) => setDiabetes({ ...diabetes, SkinThickness: +e.target.value })} />
          <Input label="Insulin" type="number" value={diabetes.Insulin} onChange={(e) => setDiabetes({ ...diabetes, Insulin: +e.target.value })} />
          <Input label="BMI" type="number" step="0.1" value={diabetes.BMI} onChange={(e) => setDiabetes({ ...diabetes, BMI: +e.target.value })} />
          <Input label="Pedigree function" type="number" step="0.01" value={diabetes.DiabetesPedigreeFunction} onChange={(e) => setDiabetes({ ...diabetes, DiabetesPedigreeFunction: +e.target.value })} />
          <Input label="Age" type="number" value={diabetes.Age} onChange={(e) => setDiabetes({ ...diabetes, Age: +e.target.value })} />
          <div className="col-span-full mt-2">
            <Button onClick={runDiabetesAssessment} isLoading={isLoading}>Run diabetes risk assessment</Button>
          </div>
        </div>
      )}

      {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
