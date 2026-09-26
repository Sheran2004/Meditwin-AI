/**
 * Central API client. Attaches the access token to every request and
 * exposes typed helper functions for the auth endpoints.
 * Backend base URL comes from NEXT_PUBLIC_API_URL (set per environment).
 */
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("meditwin_access_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type UserRole = "admin" | "doctor" | "nurse" | "reception" | "patient";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function register(
  email: string,
  password: string,
  full_name: string,
  role: UserRole
): Promise<User> {
  const { data } = await api.post<User>("/auth/register", { email, password, full_name, role });
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

// ---- Patients ----
export interface Patient {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  date_of_birth: string | null;
  gender: string | null;
  blood_group: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  assigned_doctor_id: string | null;
  created_at: string;
}

export async function listPatients(): Promise<Patient[]> {
  const { data } = await api.get<Patient[]>("/patients");
  return data;
}

export async function getPatient(patientId: string): Promise<Patient> {
  const { data } = await api.get<Patient>(`/patients/${patientId}`);
  return data;
}

export async function createMyPatientProfile(payload: Partial<Patient>): Promise<Patient> {
  const { data } = await api.post<Patient>("/patients", payload);
  return data;
}

// ---- Vitals ----
export interface Vitals {
  id: string;
  patient_id: string;
  heart_rate: number | null;
  bp_systolic: number | null;
  bp_diastolic: number | null;
  spo2: number | null;
  temperature: number | null;
  blood_sugar: number | null;
  respiration: number | null;
  recorded_at: string;
}

export async function getVitalsTimeline(patientId: string, limit = 50): Promise<Vitals[]> {
  const { data } = await api.get<Vitals[]>(`/patients/${patientId}/vitals`, { params: { limit } });
  return data;
}

export async function recordVitals(patientId: string, payload: Partial<Vitals>): Promise<Vitals> {
  const { data } = await api.post<Vitals>(`/patients/${patientId}/vitals`, payload);
  return data;
}

// ---- Risk ----
export interface RiskAssessment {
  id: string;
  patient_id: string;
  risk_type: string;
  score_pct: number;
  confidence: number;
  reasoning: string;
  recommendation: string;
  model_accuracy: number;
  computed_at: string;
}

export interface HeartRiskInput {
  age: number; sex: number; cp: number; trestbps: number; chol: number; fbs: number;
  restecg: number; thalach: number; exang: number; oldpeak: number; slope: number; ca: number; thal: number;
}

export interface DiabetesRiskInput {
  Pregnancies: number; Glucose: number; BloodPressure: number; SkinThickness: number;
  Insulin: number; BMI: number; DiabetesPedigreeFunction: number; Age: number;
}

export async function assessHeartRisk(patientId: string, payload: HeartRiskInput): Promise<RiskAssessment> {
  const { data } = await api.post<RiskAssessment>(`/patients/${patientId}/risk/heart-attack`, payload);
  return data;
}

export async function assessDiabetesRisk(patientId: string, payload: DiabetesRiskInput): Promise<RiskAssessment> {
  const { data } = await api.post<RiskAssessment>(`/patients/${patientId}/risk/diabetes`, payload);
  return data;
}

export async function getRiskHistory(patientId: string): Promise<RiskAssessment[]> {
  const { data } = await api.get<RiskAssessment[]>(`/patients/${patientId}/risk`);
  return data;
}

// ---- Reports ----
export interface Report {
  id: string;
  patient_id: string;
  file_url: string;
  ai_summary: { summary: string } | null;
  abnormal_values: { items: Array<{ name: string; value: string; normal_range: string; explanation: string }> } | null;
  language: string;
  uploaded_at: string;
}

export async function uploadReport(patientId: string, file: File, language: "en" | "hi"): Promise<Report> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<Report>(`/patients/${patientId}/reports`, formData, {
    params: { language },
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listReports(patientId: string): Promise<Report[]> {
  const { data } = await api.get<Report[]>(`/patients/${patientId}/reports`);
  return data;
}

// ---- Alerts ----
export interface AlertLog {
  id: string;
  patient_id: string;
  trigger_vital: string;
  threshold: number;
  message: string;
  sent_via: string;
  sent_at: string;
}

export async function getAlerts(patientId: string): Promise<AlertLog[]> {
  const { data } = await api.get<AlertLog[]>(`/patients/${patientId}/vitals/alerts`);
  return data;
}

// ---- Clinical Decision Support ----
export interface ClinicalDecisionResult {
  likely_conditions: Array<{ condition: string; confidence_pct: number }>;
  recommended_tests: string[];
  red_flags: string[];
  disclaimer: string;
}

export async function runClinicalDecisionSupport(symptoms: string, patientContext: string): Promise<ClinicalDecisionResult> {
  const { data } = await api.post<ClinicalDecisionResult>("/clinical/decision-support", {
    symptoms, patient_context: patientContext,
  });
  return data;
}

// ---- Drug Interaction Checker ----
export interface DrugInteractionResult {
  interactions: Array<{ drug_a: string; drug_b: string; severity: string; note: string }>;
  pregnancy_risk_drugs: string[];
  kidney_risk_drugs: string[];
  liver_risk_drugs: string[];
  plain_language_summary: string;
  alternative_suggestions: Array<{ replace: string; with: string; reason: string }>;
  disclaimer: string;
}

export async function checkDrugInteractions(medicines: string[]): Promise<DrugInteractionResult> {
  const { data } = await api.post<DrugInteractionResult>("/clinical/drug-interactions", { medicines });
  return data;
}

// ---- Voice Assistant ----
export interface VoiceCommandResult {
  intent: string;
  patient_name: string | null;
  confirmation_text: string;
}

export async function sendVoiceCommand(transcript: string, knownPatientNames: string[]): Promise<VoiceCommandResult> {
  const { data } = await api.post<VoiceCommandResult>("/voice/command", {
    transcript, known_patient_names: knownPatientNames,
  });
  return data;
}

// ---- Analytics ----
export interface HospitalAnalytics {
  total_patients: number;
  total_doctors: number;
  total_vitals_recorded: number;
  total_reports_analyzed: number;
  total_alerts: number;
  sms_alerts_sent: number;
  high_risk_patient_count: number;
  risk_breakdown: Array<{ risk_type: string; avg_score_pct: number; assessment_count: number }>;
  alert_breakdown: Array<{ vital: string; count: number }>;
}

export async function getHospitalAnalytics(): Promise<HospitalAnalytics> {
  const { data } = await api.get<HospitalAnalytics>("/analytics/hospital");
  return data;
}

// ---- Medical Imaging ----
export interface ImagingResult {
  prediction: string;
  confidence_pct: number;
  heatmap: number[][];
  clinically_meaningful: boolean;
  model_trained_on_n_images: number;
  model_cv_accuracy: number;
  model_cv_accuracy_std: number;
  warning: string | null;
}

export async function classifyChestXray(patientId: string, file: File): Promise<ImagingResult> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<ImagingResult>(`/patients/${patientId}/imaging/chest-xray`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
