# LebihSini GreenProof

LebihSini GreenProof is a reuse-first procurement intelligence MVP for Malaysian construction SMEs. Before a contractor buys new materials or rents equipment, the system checks nearby verified surplus and idle resources, compares a reuse-first plan against normal procurement, and keeps the human decision-maker in control.

## Current Scope

This repository currently provides the shared foundation for the hackathon MVP:

- typed Python contracts for demand, resources, recommendations, evidence records, and decisions
- business rules and trust language
- deterministic cost and carbon formulas
- prepared demo data for the six-site scenario
- JSON serialization helpers
- frontend/backend example JSON payloads
- scenario fixtures and tests
- a small reference recommendation scaffold for contract validation only

## What Is Implemented

- Person 1 foundation contracts in [lebihsini_greenproof/contracts.py](lebihsini_greenproof/contracts.py)
- demo dataset in [lebihsini_greenproof/demo_data.py](lebihsini_greenproof/demo_data.py)
- deterministic formulas in [lebihsini_greenproof/formulas.py](lebihsini_greenproof/formulas.py)
- trust/explanation language in [lebihsini_greenproof/explanations.py](lebihsini_greenproof/explanations.py)
- reference scenario scaffold in [lebihsini_greenproof/foundation.py](lebihsini_greenproof/foundation.py)
- reusable JSON serialization in [lebihsini_greenproof/serialization.py](lebihsini_greenproof/serialization.py)
- API contract documentation in [docs/api_contract.md](docs/api_contract.md)
- consumer-ready example payloads in [examples](examples)

## What Is Intentionally Not Implemented

- full optimiser/composer
- FastAPI endpoints
- frontend application
- Grafilab OCR or voice integration
- real routing optimisation
- authentication, payments, or production deployment

## Supported Python Version

This repository supports Python `3.11` and newer.

## Setup

From the repository root:

```powershell
python -m unittest discover -s tests -v
```

No third-party dependencies are required for the current foundation layer.

## Repository Structure

```text
docs/                     Product rules and API contract documentation
examples/                 Generated example JSON payloads for integration work
lebihsini_greenproof/     Shared contracts, formulas, data, serialization, and scaffold logic
tests/                    Contract, scenario, serialization, and example validation tests
```

## How Frontend Developers Should Use This

- Start with the files in `examples/` for payload shapes and sample screens.
- Treat the JSON examples as the UI-facing source of truth for field names and units.
- Do not hard-code recommendation wording inside components when it already exists in the response payload.

## How Backend Developers Should Use This

- Use the Python contracts as the canonical schema layer for the current MVP foundation.
- Keep API request and response bodies aligned with the contracts and `docs/api_contract.md`.
- Reuse the deterministic serializer rather than creating a second schema system.

## How The Optimiser Developer Should Begin

- Implement `constraints.py` and `composer.py` against the existing contracts.
- Preserve the exclusion reasons, units, and response shape already validated by tests.
- Treat `foundation.py` as a reference validation scaffold, not as the final engine.

## Important Warning

Demo prices, travel times, transport rates, and carbon factors are provisional assumptions for the hackathon scenario. They should remain transparent and easy to adjust.

## Expected Next Development Task

Build the real optimiser modules:

- hard-constraint filtering
- candidate ranking
- multi-source composition
- supplier shortfall fill
- equipment fallback handling

Expose those results through the future recommendation API while keeping the existing JSON contracts stable.
