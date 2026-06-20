# LebihSini GreenProof

LebihSini GreenProof is a reuse-first procurement intelligence MVP for Malaysian construction SMEs. Before a contractor buys new materials or rents equipment, the system checks nearby verified surplus and idle resources, compares a reuse-first plan against normal procurement, and keeps the human decision-maker in control.

## Current Scope

This repository currently provides the shared optimisation foundation for the hackathon MVP:

- typed Python contracts for demand, resources, recommendations, evidence records, and decisions
- business rules and trust language
- deterministic cost and carbon formulas
- prepared demo data for the six-site scenario
- deterministic optimisation modules for constraints, ranking, composition, urgency, and equipment fallback
- structured AI extraction, confirmation, and resource-passport modules
- JSON serialization helpers
- frontend/backend example JSON payloads
- scenario fixtures and tests
- a small reference recommendation scaffold for contract validation only
- a thin FastAPI backend that orchestrates extraction, confirmation, passports, recommendations, decisions, and Evidence Records using in-memory state

## What Is Implemented

- Person 1 foundation contracts in [lebihsini_greenproof/contracts.py](lebihsini_greenproof/contracts.py)
- demo dataset in [lebihsini_greenproof/demo_data.py](lebihsini_greenproof/demo_data.py)
- deterministic formulas in [lebihsini_greenproof/formulas.py](lebihsini_greenproof/formulas.py)
- deterministic optimisation engine in [lebihsini_greenproof/composer.py](lebihsini_greenproof/composer.py)
- reusable filtering, ranking, urgency, and equipment modules in `lebihsini_greenproof/`
- mock-provider AI extraction pipeline in `lebihsini_greenproof/ai_extraction.py`
- Resource Passport builders in `lebihsini_greenproof/passport_builder.py`
- FastAPI backend routes and services in `lebihsini_greenproof/api/`, `lebihsini_greenproof/services/`, and `lebihsini_greenproof/repositories/`
- trust/explanation language in [lebihsini_greenproof/explanations.py](lebihsini_greenproof/explanations.py)
- reference scenario scaffold in [lebihsini_greenproof/foundation.py](lebihsini_greenproof/foundation.py)
- reusable JSON serialization in [lebihsini_greenproof/serialization.py](lebihsini_greenproof/serialization.py)
- API contract documentation in [docs/api_contract.md](docs/api_contract.md)
- privacy notes in [docs/privacy_controls.md](docs/privacy_controls.md)
- consumer-ready example payloads in [examples](examples)

## What Is Intentionally Not Implemented

- frontend application
- raw Grafilab OCR and raw voice transcription integration
- real routing optimisation
- authentication, payments, or production deployment

## Supported Python Version

This repository supports Python `3.11` and newer.

## Setup

From the repository root:

```powershell
pip install -e .
python -m unittest discover -s tests -v
python scripts\run_demo_recommendations.py
python scripts\run_ai_demo.py
python scripts\run_backend_demo.py
```

To run the backend locally:

```powershell
uvicorn lebihsini_greenproof.api.app:app --reload
```

Environment variables:

- `GREENPROOF_PROVIDER_MODE=mock` by default
- `GREENPROOF_PROVIDER_API_KEY_ENV=GRAFILAB_API_KEY` for explicit real-provider mode
- `GREENPROOF_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
- `GRAFILAB_API_KEY` required for `GREENPROOF_PROVIDER_MODE=grafilab`
- `GRAFILAB_BASE_URL=https://console-api.grafilab.ai/api/oai/v1`
- `GRAFILAB_TEXT_MODEL=grafilab/qwen3.6-flash`
- `GRAFILAB_TIMEOUT_SECONDS=15.0`

State is in-memory only and resets on process restart.

## Repository Structure

```text
docs/                     Product rules and API contract documentation
examples/                 Generated example JSON payloads for integration work
lebihsini_greenproof/     Contracts, extraction pipeline, formulas, demo data, backend API, repositories, services, serialization, scaffold, and optimiser modules
scripts/                  Example generation and demo runner scripts
tests/                    Contract, extraction, engine, backend, serialization, and example validation tests
```

## How Frontend Developers Should Use This

- Start with the files in `examples/` for payload shapes and sample screens.
- Treat the JSON examples as the UI-facing source of truth for field names and units.
- Do not hard-code recommendation wording inside components when it already exists in the response payload.
- Use extraction-response examples to build the user-confirmation flow before wiring the recommendation screens.

## How Backend Developers Should Use This

- Use the Python contracts as the canonical schema layer for the current MVP foundation.
- Keep API request and response bodies aligned with the contracts and `docs/api_contract.md`.
- Reuse the deterministic serializer rather than creating a second schema system.
- Keep raw AI/provider output outside the optimiser boundary until a confirmed `DemandRequest` exists.
- Treat the FastAPI repository state as demo-only because it is explicitly in-memory.
- Keep `GREENPROOF_PROVIDER_MODE=mock` as the default for tests and offline demos.
- Use real Grafilab mode only for Phase 1 text structuring with the official OpenAI-compatible base URL and text model.

## How The Optimiser Developer Should Begin

- Extend the existing optimiser modules rather than the scaffold.
- Preserve the exclusion reasons, units, and response shape already validated by tests.
- Treat `foundation.py` as reference-only and `composer.py` as the real engine entry point.
- Use the new extraction modules only to produce confirmed structured inputs; do not feed raw provider payloads into the optimiser.

## Backend Endpoints

- `GET /api/health`
- `POST /api/extract-request`
- `POST /api/extractions/{extraction_id}/confirm`
- `POST /api/material-passports`
- `POST /api/equipment-passports`
- `GET /api/resources`
- `GET /api/resources/{resource_id}`
- `POST /api/recommendations`
- `POST /api/recommendations/{recommendation_id}/recalculate`
- `POST /api/recommendations/{recommendation_id}/decision`
- `GET /api/evidence-records/{record_id}`

## Important Warning

Demo prices, travel times, transport rates, and carbon factors are provisional assumptions for the hackathon scenario. They should remain transparent and easy to adjust.
Grafilab integration is currently mocked offline because no official API details were present in this repository.

## Real Grafilab Phase 1

Supported in real-provider mode:

- typed English demand text
- typed Bahasa Malaysia demand text
- already-available transcript text
- already-available OCR text for structuring

Not supported in real-provider mode yet:

- raw image OCR
- raw PDF/document upload understanding
- raw WhatsApp screenshot understanding
- raw audio transcription
- raw resource-photo understanding

Optional real smoke test:

```powershell
python scripts\run_grafilab_smoke_test.py
```

This script makes a real network call only when `GRAFILAB_API_KEY` is set. It never prints the key and only sends harmless typed text.
