# LebihSini GreenProof Business Rules

## Scope

These rules define the stable product logic for the hackathon MVP. They are intended to guide frontend, backend, AI extraction, and optimisation work.

## Hard exclusion rules

A resource must be excluded from automatic recommendation when any of the following is true:

- dimensions do not match the demand
- product specification is incompatible
- available quantity is zero
- delivery or collection cannot meet the deadline
- risk exceeds the demand's maximum tolerated risk
- critical documentation is missing
- transport is impossible
- the material category is outside the MVP scope

Equipment must also be excluded when:

- the category does not match the request
- availability does not cover the requested duration
- maintenance evidence is below the minimum threshold
- collection or return windows are infeasible

## Risk rules

- `green`: may be automatically considered after human confirmation of the extracted demand
- `amber`: may be considered, but must carry an inspection or approval condition
- `red`: must never be automatically recommended

## Site E rule

Site E must be excluded from automatic recommendation.

Required explanation:

`Excluded from automatic recommendation because the product specification could not be verified.`

Additional guidance:

- do not state that Site E is unsafe
- do state that the label is unreadable or the condition is insufficiently verified
- do allow a future manual inspection pathway outside the automatic recommendation flow

## Feasibility priority

The system must evaluate feasibility in this order:

1. safety and specification compatibility
2. deadline feasibility
3. landed cost
4. worker-delay exposure
5. carbon impact
6. number of sources and operational complexity

## Supplier fallback

- Supplier F fills any unresolved material shortfall.
- Supplier fallback is valid whenever reuse cannot fully satisfy quantity, timing, or confidence requirements.

## Recommendation rules

- reuse is preferred only when it remains operationally feasible
- reuse is never mandatory
- normal procurement can be the correct recommendation
- excluded resources and inspection conditions must be explicitly shown
- all cost and carbon outputs must be presented as estimates using stated assumptions
