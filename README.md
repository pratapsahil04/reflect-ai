# ReflectAI 🧠
### Privacy-First AI Journaling and Reflection Companion

ReflectAI is a privacy-oriented AI journaling application that helps users reflect on their thoughts, emotions, and everyday experiences.

It combines a deterministic safety classifier, an AI reflection companion powered by Google Gemini, mood analysis, local SQLite storage, and an interactive dashboard.

> **Important:** ReflectAI is a journaling and reflection tool, not a replacement for professional mental-health care.

---

## 🌱 Overview

ReflectAI provides an interactive environment where users can:

- Write and review journal entries
- Receive reflective AI responses
- Identify moods and emotions
- Track mood patterns over time
- Review recurring themes
- Generate weekly reflection summaries
- Receive safety-oriented responses when high-risk language is detected

**Core design principle:** Safety classification runs before normal AI generation, allowing the application to route detected high-risk messages to dedicated safety responses.

## ✨ Key Features

### 💬 AI Journaling Companion

The AI companion is designed to acknowledge emotions, encourage self-reflection, ask open-ended questions, explore thought patterns, and suggest simple CBT-inspired reflection exercises.

It is instructed not to diagnose conditions, prescribe or recommend medication changes, claim to provide therapy, make clinical judgments, encourage emotional dependency, or provide false reassurance.

### 🛡️ Safety Classification

The safety layer categorizes messages into three levels:

- `none`: No elevated-risk category detected by the classifier
- `elevated`: Elevated-risk language requiring a safety-aware response
- `crisis`: Crisis-related language requiring a predefined crisis response

```text
User Message
     |
     v
Safety Classifier
     |
     +---- Crisis ----> Fixed Crisis Response
     |                       |
     |                       v
     |                Helplines / Guidance
     |
     +---- Elevated --> Safety-Aware Response
     |
     +---- None ------> Gemini AI Companion
                              |
                              v
                        Mood Extraction
                              |
                              v
                        SQLite Storage
```

The classifier uses deterministic rules. It is not a clinically validated risk assessment system and cannot guarantee detection of every crisis statement.

### 📊 Mood Tracking and Analytics

- Mood extraction with a local fallback
- Historical mood tracking using SQLite
- Interactive visualizations using Plotly
- Emotion and recurring-theme analysis
- Dashboard metrics and journal activity views

### 📝 Journal Management

- Browse journal entries
- Search journal content
- Explore tags and categories
- Use reflection templates
- View journal activity in a calendar
- Review insights and weekly summaries

### 🔒 Privacy-Focused Storage

Journal records are stored locally in SQLite. The application also uses the Google Gemini API for AI-powered features, so data sent to that external service may be processed according to Google's applicable terms and privacy policies.

Local database storage does not mean that all processing is offline. Review what information is sent to the AI service before using the application with sensitive journal content.

---

## 🧩 System Architecture

```text
User
 |
 v
Streamlit Interface
 |
 v
Safety Classifier
 |
 +---- Crisis ------> Predefined Crisis Response
 |                           |
 |                           v
 |                    Helpline Guidance
 |
 +---- Elevated ---> Safety-Aware Response
 |
 +---- None --------> Gemini AI Companion
                            |
                            v
                      Mood Extraction
                            |
                            v
                      SQLite Database
                            |
                            v
                     Plotly Dashboard
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| User interface | Streamlit |
| AI model | Google Gemini API |
| Programming language | Python |
| Safety layer | Deterministic rule-based classifier |
| Mood analysis | Gemini with local fallback |
| Database | SQLite |
| Data analysis | Pandas |
| Visualization | Plotly |
| Data validation | Pydantic |
| Testing | Pytest |
| Environment configuration | python-dotenv |
| Version control | Git and GitHub |

### Core Python Libraries

`google-genai`, `streamlit`, `pydantic`, `pandas`, `plotly`, `python-dotenv`, and `pytest`.

---

## ⚙️ Installation and Setup

### Prerequisites

- Python installed on your system
- Git
- A Google Gemini API key for AI-powered features

### 1. Clone the repository

```bash
git clone https://github.com/pratapsahil04/reflect-ai.git
cd reflect-ai
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Use the exact variable name expected by your application configuration if it differs.

**Security:** Never commit `.env`, API keys, journal databases, or real private journal entries to GitHub.

### 5. Run the application

```powershell
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

---

## 🧪 Testing and Evaluation

### Automated Tests

Run the test suite:

```powershell
pytest
```

The existing test suite previously passed six tests. Run it again after making changes to confirm the current result.

### Safety Classifier Evaluation

The developer-created internal evaluation produced the following results:

| Metric | Result |
|---|---:|
| Test cases | 50 |
| Correct predictions | 50 |
| Accuracy on the test set | 100% |
| Crisis recall on the test set | 100% |
| Elevated-risk recall on the test set | 100% |
| Safe specificity on the test set | 100% |
| False-positive rate on the test set | 0% |

These results apply only to the 50 developer-created evaluation cases. They do not establish real-world reliability, clinical validity, or guaranteed crisis detection.

Run the evaluation with:

```powershell
python tests/run_evaluation.py
```

### Companion Behavioral Evaluation

An 18-case evaluation framework covers:

- Diagnosis refusal
- Medication safety boundaries
- Therapist-role boundaries
- Avoidance of unverified agreement
- Avoidance of absolute guarantees
- Reflective responses
- Gentle cognitive reframing

Live evaluation requires available Gemini API quota. No companion evaluation accuracy is claimed until the cases have been executed and results recorded.

Run it with:

```powershell
python tests/run_companion_evaluation.py
```

---

## 📌 Project Status

### Implemented

- [x] Streamlit journaling interface
- [x] Gemini-powered reflective companion
- [x] Deterministic safety classification
- [x] Predefined crisis responses
- [x] Elevated-risk response handling
- [x] Configurable crisis helplines
- [x] Mood extraction and local fallback
- [x] SQLite mood storage
- [x] Interactive dashboard and visualizations
- [x] Weekly reflection summary
- [x] Journal search and analysis
- [x] Journal templates, tags, and calendar view
- [x] Automated safety tests
- [x] Internal 50-case safety evaluation
- [x] Companion behavioral evaluation framework
- [x] GitHub repository and documentation

### Current Limitations

- The rule-based classifier may miss nuanced or indirect crisis statements.
- Gemini-powered features depend on API availability and quota.
- Mood analysis is approximate and is not a clinical assessment.
- The application has not undergone clinical validation or testing on a clinical population.
- Local SQLite storage does not eliminate the privacy considerations associated with external API processing.

## 🔮 Future Improvements

- Expand safety evaluation with more diverse, independently reviewed cases.
- Complete and document live companion behavioral evaluation.
- Add stronger automated regression tests.
- Improve configurable privacy controls and data export/deletion workflows.
- Evaluate additional AI models and fallback strategies.

## ⚖️ Disclaimer

ReflectAI is an experimental journaling and reflection application. It is not a medical device, diagnostic system, or substitute for professional mental-health care. Its safety classifier can make mistakes and must not be relied upon as the sole means of identifying or managing a crisis.

## 📄 License

This project is distributed under the MIT License. See [`LICENSE`](LICENSE) for details, if the repository's license file is present.