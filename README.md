# AgeWell

An educational health-risk prediction prototype with a Streamlit demo and an optional authenticated Flask API.

> **Research demo only.** The model is not clinically validated. Results and generated food/activity examples are not medical advice and must not guide care decisions. Use synthetic inputs only; never enter real patient or identifying information.

## Live demo

https://agewell-risk-demo.onrender.com/

The hosted demo does not save predictions, generate email alerts, or connect to a database. Inputs are processed by the public hosting service, so use fictional sample values only; the app requires you to confirm this before running a prediction. If you request a PDF, the generated file is removed immediately after its bytes are loaded into the current Streamlit session for download. Use **Reset fictional sample** to clear entered values, consent, options and any session-held report bytes.

## What it does

- Estimates a binary risk label from age, heart rate, systolic blood pressure and cholesterol.
- Calculates a reference BMI and prototype score, then displays rule-based examples.
- Shows the PDF download action as soon as an explicitly requested sample report is ready; MySQL persistence remains opt-in and local-only.
- Provides an optional Flask API with bearer-token authentication; persistence and reports default off.

## Local setup

Requires Python 3.12.11. Create a virtual environment, then install dependencies:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the demo:

```powershell
streamlit run app.py
```

Optional database, report and email settings are documented in `.env.example`. Keep all real secrets in a local `.env` file and never commit them. Database storage controls stay disabled until all required MySQL settings are present. Email alerts require an explicit opt-in for each run and remain off in the service/API defaults.

## Optional API

Set `AGEWELL_API_TOKEN` to a unique secret of at least 32 characters before starting the Flask API:

```powershell
$env:AGEWELL_API_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
python -m app.routes.api
```

- `GET /health` — service health; no patient data.
- `POST /predict` — requires `Authorization: Bearer <token>` and a JSON body containing `age`, `heart_rate`, `systolic_bp`, `cholesterol`, `weight`, and `height`.
- `GET /records` — requires the same bearer token and a configured MySQL database.

Prediction requests do not save records or create reports unless `save_to_db` or `generate_pdf` is explicitly set to `true`. Do not expose a token in browser code, logs, screenshots or a public repository.

## Project map

- `app.py` — Streamlit interface.
- `app/routes/api.py` — authenticated Flask endpoints.
- `app/services/health_service.py` — model workflow and opt-in side effects.
- `app/models/` — predictor and serialized research model.
- `app/utils/` — database, PDF and email helpers.
- `tests/` — privacy-default and report-file checks.

## Run checks

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions runs Python compilation and the test suite on pushes and pull requests to `main`.

## Privacy and limitations

This prototype has not been clinically validated or assessed for medical use. Public hosting is intended only for synthetic sample values. The hosted service has no database or email credentials configured, and the UI disables record storage until a complete local MySQL configuration is provided. Before any real-world use, obtain clinical, privacy, security and regulatory review, and build appropriate consent, access control, retention and monitoring.
