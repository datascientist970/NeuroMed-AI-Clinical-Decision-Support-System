# NeuroMed AI — Clinical Decision Support System

> A multi-agent AI system that supports — never replaces — clinical judgement: structured patient intake, risk stratification (LOW / MODERATE / HIGH) and explainable, audited recommendations, delivered through a Django REST API.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-REST%20API-092E20?logo=django&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-blue)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-8E75B2?logo=googlegemini&logoColor=white)

## Overview

NeuroMed AI is a clinical decision-support system built around a **LangGraph multi-agent pipeline** powered by Google Gemini (`gemini-2.5-flash`). A patient case submitted to the API passes through a sequence of specialised agents — each with a deliberately narrow, safety-scoped role — and returns a structured result with a risk level, supporting insights, suggested next steps and a plain-language explanation.

The system is explicitly **decision-support only**: agents are prompted not to diagnose or prescribe treatment, high-risk cases are flagged as requiring human approval, and every run is written to an audit log.

## Key Features

- **Multi-agent LangGraph pipeline** (`config/clinical/ai/clinic_agent.py`):
  - **Intake agent** — normalises patient data and vitals, flags missing or abnormal values
  - **Clinical knowledge agent** — identifies possible clinical concerns using probabilistic language only
  - **Risk agent** — stratifies risk as LOW, MODERATE or HIGH, conservatively; HIGH risk sets `approval_required`
  - **Recommendation agent** — suggests diagnostic tests and care pathways (no treatment), with a disclaimer
  - **Explainability agent** — explains the reasoning transparently for the clinician
- **REST API** — a Django REST Framework endpoint validates input with a serializer and returns the pipeline's structured JSON output
- **API-key authentication & throttling** — a `ClinicalAPIKey` model with securely generated keys (`secrets.token_hex`), plus custom authentication and throttle classes
- **Full audit trail** — every request is logged (`ClinicalAuditLog`) with request ID, timestamp, risk level, approval flag, agents executed and status
- **Web interface** — a single-page clinical UI served from Django templates

## Tech Stack

- **Backend:** Django, Django REST Framework
- **AI Orchestration:** LangGraph (state graph), Google Generative AI — Gemini 2.5 Flash (JSON response mode, low temperature for consistency)
- **Database:** SQLite (development)
- **Frontend:** HTML template (Bootstrap-style clinical dashboard)

## Project Structure

```text
NeuroMed-AI-Clinical-Decision-Support-System/
└── config/
    ├── manage.py
    ├── config/                 # Django project settings & URLs
    └── clinical/               # Clinical app
        ├── ai/
        │   └── clinic_agent.py # LangGraph multi-agent pipeline (Gemini)
        ├── models.py           # ClinicalAPIKey, ClinicalAuditLog
        ├── serializers.py      # Clinical input validation
        ├── authentication.py   # API-key authentication
        ├── throttles.py        # Rate limiting
        ├── views.py            # ClinicalDecisionSupportAPIView + home page
        ├── urls.py
        └── templates/index.html
```

## Getting Started

```bash
git clone https://github.com/datascientist970/NeuroMed-AI-Clinical-Decision-Support-System.git
cd NeuroMed-AI-Clinical-Decision-Support-System/config
pip install django djangorestframework google-generativeai langgraph
set GEMINI_API_KEY=your_key_here   # Windows; use `export` on Linux/macOS
python manage.py migrate
python manage.py runserver
```

## Usage

Open `http://127.0.0.1:8000/` for the web interface, or call the API directly:

```http
POST /clinical-support/
Content-Type: application/json

{ ...patient case data (validated by ClinicalInputSerializer)... }
```

The response contains the structured final output of the agent pipeline — patient profile, data-quality flags, clinical insights, risk assessment, recommendations and explanation. HIGH-risk results are flagged `approval_required` for clinician review.

## ⚕️ Disclaimer

This system is a decision-support and educational tool only. It does not diagnose, prescribe, or replace the judgement of a qualified healthcare professional. All outputs require review by a clinician before any action is taken.

## Author

**Muhammad Dawood** — AI & Data Science Engineer
GitHub: https://github.com/datascientist970 · Mardan, Pakistan
LinkedIn: https://www.linkedin.com/in/dawood406/
