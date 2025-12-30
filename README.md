# adaptive-autocomplete
A self-learning autocompleter that uses various methods to improve its text suggestions over time.



## Architecture Overview

Autocomplete engine designed as a layered system that seperates signal generation, aggregation, ranking, learning, and explanation. Each layer has a single responsibility and explicit invariants, allowing the system to grow and evolve without accidental coupling or errors.

User Input
   ↓
CompletionContext
   ↓
Predictors (raw signals)
   ↓
Weighted Aggregation
   ↓
Rankers (ordering + learning)
   ↓
Suggestions + Explanations

## Design Principles

Single Source of Truth:

- History is owned by the engine
- Rankers can read or learn from history but don't own it
- Predictors are stateless by default

  Explanation Model:

The system distinguishes between:
- PredictorExplanation: raw unnormalized signals
- RankingExplanation: final user-facing scoring rationale

This prevents accidental mix-ups between prediction and ranking logic
and allows explanations to remain truthful as the system evolves.

Immutability at Boundaries:

Core domain objects (Suggestion, ScoredSuggestion, CompletionContext)
are immutable.

Rankers return new ordering, not mutated input, ensuring determinism
and safe composition.

## Component Responsibilities

Predictors:

- Generate candidate suggestions
- Assign raw scores
- May optionally emit PredictorExplanation
- Do not rank or learn

Engine:

- Orchestrates the full pipeline
- Aggregates and weights predictor output
- Applies rankers sequentially
- Owns the lifecycle of CompletionContext and History

Rankers:

- Reorder suggestions
- May apply learning or normalization
- Must preserve scores and determinism

Explanations:

- Always aligned with final ranking output
- Aggregated across rankers
- Exportable in JSON-safe form for APIs


## Design Scaling

This system is intentionally designed to scale beyond autocomplete.

The same architecture supports:
- Search ranking
- Recommendation engines
- Query completion
- ML-backed ranking layers

New predictors, rankers, or learning strategies can be introduced
without modifying existing components.
