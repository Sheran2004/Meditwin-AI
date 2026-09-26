# MediTwin AI — Architecture & Build Plan
**Predict. Prevent. Protect.**

> This document trims the original 12-module, 7-role, full-AWS wishlist down to something one person can actually ship, demo, and defend in front of judges within ~4 weeks. Everything cut is listed explicitly as "Future Scope" — that's a *strength* slide in a hackathon deck, not a weakness.

---

## 1. Why the stack was trimmed

The original spec had two backends (FastAPI + Node/Express), three databases (Postgres + MongoDB + Redis), Three.js, GSAP, Socket.io, LangChain, YOLOv11, and AWS S3 — all for a solo build in a month. Every extra piece of infra is something that can break the night before demo. Rule for hackathons: **fewer moving parts that all work > more moving parts that half work.**

| Original | Trimmed to | Why |
|---|---|---|
| FastAPI + Node/Express | **FastAPI only** | One backend does REST, WebSockets, and AI inference natively in Python — no context-switching, no duplicate auth logic |
| Postgres + MongoDB + Redis | **Postgres + Redis** | Unstructured data (lab report text, AI explanations) stored as `JSONB` columns in Postgres — no need for a second DB |
| Socket.io | **FastAPI native WebSockets** | Avoids a Node-ecosystem library on a Python backend; frontend uses native `WebSocket` API |
| Three.js + GSAP + Framer Motion | **Framer Motion only** (Tailwind transitions for the rest) | 3D digital twin visualization is a nice-to-have, not a judge-deciding factor — cut unless Week 4 has slack |
| AWS S3 + Nginx + AWS deploy guide | **Vercel (frontend) + Render (backend) + Neon (Postgres) + Upstash (Redis)** | All have generous free tiers, zero server management, deploy in minutes — a live demo URL matters more than "AWS" on a slide |
| YOLOv11 / medical imaging CNN | **Cut to Future Scope** | Needs a labeled medical imaging dataset + GPU training time you don't have in a month. Claiming it half-working is worse than not claiming it |
| ESP32 / real hardware IoT | **Simulated live data generator** | Same risk-reward problem — a fake sensor stream that works > real hardware that might not power on during demo |
| LangChain | **Direct Groq API calls** | LangChain adds abstraction overhead for what is, here, single-turn prompt calls — you already know the raw Groq API from VisionSync |

## 2. Final tech stack

**Frontend**
- Next.js 15 (App Router) + React 19 + TypeScript
- Tailwind CSS
- Framer Motion (page/element transitions)
- Zustand (client state)
- React Query (server state / caching)
- Recharts (vitals graphs, risk charts)
- Native `WebSocket` API (real-time vitals + alerts)

**Backend**
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (async) + Alembic (migrations)
- Pydantic v2 (validation)
- python-jose (JWT) + passlib (hashing)
- FastAPI native WebSocket routes

**AI**
- scikit-learn / XGBoost — risk prediction models (heart attack, diabetes, ICU admission) trained on public datasets (UCI Heart Disease, Pima Diabetes, MIMIC-derived ICU sets)
- Groq API (Llama 3.3 70B) — report explanation (OCR text → plain-language summary, Hindi + English), clinical decision support reasoning, drug interaction reasoning
- Tesseract OCR (`pytesseract`) — PDF/report text extraction
- (Optional, Week 4 only) Web Speech API — browser-native voice commands, no custom ASR needed

**Data**
- PostgreSQL (Neon — serverless, free tier, branching for dev/prod)
- Redis (Upstash — free tier, used for cache + pub/sub on vitals alerts)

**Auth**
- JWT access + refresh tokens
- RBAC: `admin`, `doctor`, `patient` roles (Nurse/Reception/Family/Research dashboards → Future Scope)

**Realtime & Alerts**
- FastAPI WebSocket for live vitals streaming
- Twilio (SMS) — you already have working Twilio integration from Outreach, reuse it for emergency alerts

**Deployment**
- Frontend → Vercel
- Backend → Render (free web service)
- DB → Neon Postgres
- Cache → Upstash Redis
- Docker + `docker-compose.yml` for local dev (and to show you understand containerization even though prod uses managed platforms)
- GitHub Actions — one simple CI workflow (lint + test on push), not a full CD pipeline

## 3. Module priority for a 1-month solo build

**P0 — MVP core (must work flawlessly for demo)**
1. Auth + RBAC (admin / doctor / patient login)
2. AI Digital Twin — patient profile, vitals timeline (manual entry + simulated live stream), medical history, visualized with Recharts
3. AI Risk Prediction — heart attack, diabetes, ICU admission risk, with % score, confidence, and plain-language reasoning
4. Medical Report Analyzer — PDF upload → OCR → Groq-generated summary, abnormal value highlighting, Hindi + English toggle
5. Doctor Dashboard + Patient Dashboard (2 dashboards done *well* beats 7 done thin)

**P1 — differentiators (build if P0 is solid by end of Week 3)**
6. Clinical Decision Support — doctor enters symptoms, Groq suggests likely conditions + confidence + recommended tests + red flags
7. Emergency Alert — vitals crossing a critical threshold triggers a simulated Twilio SMS to a registered contact
8. Drug Interaction Checker — rule-based lookup table + Groq-generated explanation of risk

**P2 — explicitly "Future Scope" (mention in pitch, do not attempt to build)**
- Medical imaging (MRI/CT/X-ray segmentation) — needs real dataset + GPU training
- Real ESP32/IoT hardware integration — simulate only
- Voice assistant beyond basic browser commands
- Nurse / Reception / Family / Research dashboards
- 3D Three.js digital twin visualization
- Full hospital analytics (bed occupancy, revenue, doctor workload)

Framing this as Future Scope in the pitch deck is a *positive* — it shows product maturity and roadmap thinking, which judges reward.

## 4. Database schema (PostgreSQL — key tables)

```
users            (id, email, password_hash, role, full_name, created_at)
patients         (id, user_id FK, dob, gender, blood_group, height_cm, weight_kg)
vitals           (id, patient_id FK, heart_rate, bp_systolic, bp_diastolic,
                   spo2, temperature, blood_sugar, respiration, recorded_at)
medical_history  (id, patient_id FK, condition, diagnosed_at, notes)
prescriptions    (id, patient_id FK, doctor_id FK, medicine, dosage, notes, created_at)
reports          (id, patient_id FK, file_url, ocr_text, ai_summary JSONB,
                   abnormal_values JSONB, language, uploaded_at)
risk_scores      (id, patient_id FK, risk_type, score_pct, confidence,
                   reasoning TEXT, computed_at)
alerts           (id, patient_id FK, trigger_vital, threshold, message,
                   sent_via, sent_at)
audit_logs       (id, user_id FK, action, resource, resource_id, timestamp)
```

Notes:
- `ai_summary`, `abnormal_values` as `JSONB` — this is what replaces MongoDB for unstructured AI output.
- `audit_logs` is a cheap, high-value addition: judges scoring "healthcare compliance awareness" will notice it immediately.
- Soft delete via `deleted_at` nullable column on `patients` and `reports` — mention it in docs, implement only if time allows.

## 5. Folder structure

```
meditwin-ai/
├── frontend/
│   ├── app/
│   │   ├── (auth)/login/
│   │   ├── (dashboard)/doctor/
│   │   ├── (dashboard)/patient/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/            # buttons, cards, inputs
│   │   ├── charts/         # vitals charts, risk gauges
│   │   └── dashboard/
│   ├── lib/                # api client, websocket client, utils
│   ├── store/               # zustand stores
│   └── types/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # routers: auth, patients, vitals, risk, reports
│   │   ├── core/             # config, security, deps
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/            # business logic (repository pattern)
│   │   ├── ai/                   # risk models, groq client, ocr
│   │   └── ws/                    # websocket routes
│   ├── alembic/                    # migrations
│   ├── tests/
│   └── main.py
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

## 6. 4-week roadmap

**Week 1 — Foundation**
- Repo setup, Docker Compose (Postgres + Redis + backend + frontend)
- DB schema + Alembic migrations
- Auth + RBAC (JWT, login/register, protected routes)
- Base Next.js layout, doctor/patient dashboard shells

**Week 2 — Digital Twin + Risk Prediction**
- Patient profile CRUD + vitals entry + timeline visualization (Recharts)
- Train and serve XGBoost risk models (heart attack, diabetes) — start with public datasets, pickle the model, serve via FastAPI endpoint
- Simulated live vitals stream over WebSocket

**Week 3 — Report Analyzer + polish P0**
- PDF upload → OCR → Groq summary pipeline
- Abnormal value highlighting + Hindi/English toggle
- Full pass on P0 UI: loading states, empty states, error states, dark mode
- Deploy to Vercel + Render, confirm the live URL actually works end-to-end

**Week 4 — P1 differentiators + demo prep**
- Clinical Decision Support module
- Emergency alert (Twilio SMS simulation)
- Drug Interaction Checker
- Record demo script, build pitch deck, rehearse judge Q&A
- Buffer day for bug fixes — do not skip this

## 7. What to say when judges ask "why not X from the original scope"

Have one line ready: *"We scoped this deliberately — Medical Imaging and full IoT hardware need dedicated datasets and training time we didn't want to fake for a demo. We prioritized modules that are fully real and working end-to-end, and the architecture is built so imaging and IoT plug in as the next milestone."* This is a stronger answer than a shaky imaging demo.

---
*Next: pick a starting module (Core skeleton, Digital Twin, or Risk Prediction) and we build it fully — real code, working end to end, not scaffolding.*
