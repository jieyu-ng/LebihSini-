<<<<<<< HEAD
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

## What Is Implemented

- Person 1 foundation contracts in [lebihsini_greenproof/contracts.py](lebihsini_greenproof/contracts.py)
- demo dataset in [lebihsini_greenproof/demo_data.py](lebihsini_greenproof/demo_data.py)
- deterministic formulas in [lebihsini_greenproof/formulas.py](lebihsini_greenproof/formulas.py)
- deterministic optimisation engine in [lebihsini_greenproof/composer.py](lebihsini_greenproof/composer.py)
- reusable filtering, ranking, urgency, and equipment modules in `lebihsini_greenproof/`
- mock-provider AI extraction pipeline in `lebihsini_greenproof/ai_extraction.py`
- Resource Passport builders in `lebihsini_greenproof/passport_builder.py`
- trust/explanation language in [lebihsini_greenproof/explanations.py](lebihsini_greenproof/explanations.py)
- reference scenario scaffold in [lebihsini_greenproof/foundation.py](lebihsini_greenproof/foundation.py)
- reusable JSON serialization in [lebihsini_greenproof/serialization.py](lebihsini_greenproof/serialization.py)
- API contract documentation in [docs/api_contract.md](docs/api_contract.md)
- privacy notes in [docs/privacy_controls.md](docs/privacy_controls.md)
- consumer-ready example payloads in [examples](examples)

## What Is Intentionally Not Implemented

- FastAPI endpoints
- frontend application
- Grafilab OCR or voice integration
- real Grafilab network client calls
- real routing optimisation
- authentication, payments, or production deployment

## Supported Python Version

This repository supports Python `3.11` and newer.

## Setup

From the repository root:

```powershell
python -m unittest discover -s tests -v
python scripts\run_demo_recommendations.py
python scripts\run_ai_demo.py
```

No third-party dependencies are required for the current foundation layer.

## Repository Structure

```text
docs/                     Product rules and API contract documentation
examples/                 Generated example JSON payloads for integration work
lebihsini_greenproof/     Contracts, extraction pipeline, formulas, demo data, serialization, scaffold, and optimiser modules
scripts/                  Example generation and demo runner scripts
tests/                    Contract, extraction, engine, serialization, and example validation tests
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

## How The Optimiser Developer Should Begin

- Extend the existing optimiser modules rather than the scaffold.
- Preserve the exclusion reasons, units, and response shape already validated by tests.
- Treat `foundation.py` as reference-only and `composer.py` as the real engine entry point.
- Use the new extraction modules only to produce confirmed structured inputs; do not feed raw provider payloads into the optimiser.

## Important Warning

Demo prices, travel times, transport rates, and carbon factors are provisional assumptions for the hackathon scenario. They should remain transparent and easy to adjust.
Grafilab integration is currently mocked offline because no official API details were present in this repository.

## Expected Next Development Task

Build the backend integration layer around the current extraction and optimiser pipeline:

- provider-backed extraction service wrapper
- recommendation service wrapper
- API request/response adapters
- evidence-record assembly
- FastAPI endpoints against the existing contracts

Keep the existing JSON contracts stable while exposing the real engine through the future recommendation API.
=======
# LebihSini-
>>>>>>> origin/main
