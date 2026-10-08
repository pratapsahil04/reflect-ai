# ReflectAI 🧠

### Privacy-First AI Journaling and Reflection Companion

ReflectAI is a privacy-oriented AI journaling application designed to help users reflect on their thoughts, emotions, and everyday experiences.

The system combines a deterministic safety classifier, an AI reflection companion, mood analysis, local SQLite storage, and an interactive mood dashboard.

ReflectAI is designed as a journaling and reflection tool rather than a replacement for professional mental-health care.

---

## 🌱 Overview

Journaling can help people organize their thoughts, recognize emotional patterns, and reflect on everyday experiences.

ReflectAI provides an interactive environment where users can:

- Write journal entries
- Receive reflective AI responses
- Identify mood and emotions
- Track mood patterns over time
- Review recurring themes
- Generate weekly reflection summaries
- Receive safety-oriented responses when high-risk language is detected

A key design principle of ReflectAI is that **safety classification runs before normal AI generation**.

This prevents potentially high-risk messages from being passed directly to the normal conversational companion.

---

# ✨ Key Features

## 💬 AI Journaling Companion

ReflectAI provides reflective responses designed to:

- Acknowledge emotions
- Encourage self-reflection
- Ask open-ended questions
- Identify thoughts and patterns
- Suggest simple CBT-inspired reflection exercises
- Encourage practical next steps

The companion is explicitly instructed not to:

- Diagnose mental-health conditions
- Prescribe medication
- Recommend medication changes
- Claim to provide therapy
- Make clinical judgments
- Encourage emotional dependency
- Provide false reassurance

---

## 🛡️ Safety Classification

Every user message is checked by the safety layer before normal AI generation.

The classifier categorizes messages into:

```text
none
elevated
crisis

User Message
     │
     ▼
Safety Classifier
     │
     ├── crisis
     │      │
     │      ▼
     │  Fixed Crisis Response
     │      │
     │      ▼
     │  Helplines / Emergency Guidance
     │
     ├── elevated
     │      │
     │      ▼
     │  Safety-Aware Response
     │
     └── none
            │
            ▼
       AI Companion
            │
            ▼
       Mood Extraction
            │
            ▼
       SQLite Storage---

## 🧩 System Architecture

```text
User
 │
 ▼
Streamlit Interface
 │
 ▼
Safety Classifier
 │
 ├── Crisis ───────► Crisis Response + Helplines
 │
 ├── Elevated ─────► Safety-Aware Response
 │
 └── Safe
       │
       ▼
   Gemini AI Companion
       │
       ▼
   Mood Extraction
       │
       ▼
   SQLite Database
       │
       ▼
   Plotly Dashboard---

## 🚀 Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| AI Model | Google Gemini |
| Programming Language | Python |
| Safety Layer | Deterministic Rule-Based Classifier |
| Mood Analysis | Gemini + Local Fallback |
| Database | SQLite |
| Data Analysis | Pandas |
| Visualization | Plotly |
| Data Validation | Pydantic |
| Environment Management | Python Virtual Environment |
| Testing | Pytest |
| Configuration | python-dotenv |

### Core Python Libraries

- `google-genai`
- `streamlit`
- `pydantic`
- `pandas`
- `plotly`
- `python-dotenv`
- `pytest`---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/reflect-ai.git
cd reflect-ai
## 🧪 Testing### Safety Evaluation

ReflectAI includes a developer-created internal safety evaluation
covering crisis, elevated-risk, safe, and false-positive cases.

| Metric | Result |
|---|---:|
| Total test cases | 50 |
| Correct predictions | 50 |
| Overall accuracy | 100% |
| Crisis recall | 100% |
| Elevated-risk recall | 100% |
| Safe specificity | 100% |
| False-positive rate | 0% |

The evaluation achieved 100% accuracy on the internal 50-case
test set, including 100% recall for crisis and elevated-risk
examples and 0% false positives on the evaluated examples.

**Important:** This is a developer-created functional evaluation
and does not constitute clinical validation or evidence of
real-world safety. The system should not be considered a
clinically validated mental-health risk assessment tool.

### Companion Behavioral Evaluation

ReflectAI also includes an 18-case behavioral evaluation framework
for the generative AI companion.

The evaluation covers:

- Diagnosis refusal
- Medication safety boundaries
- Therapist-role boundaries
- Avoidance of unverified agreement
- Avoidance of absolute guarantees
- Reflective responses
- Gentle cognitive reframing

Live execution of these cases requires available Gemini API quota.
No companion evaluation accuracy is reported until the live cases
have been executed.