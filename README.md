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


## Public API

The following methods are considered stable and safe for external use:

- AutocompleteEngine.suggest(text: str) -> list[Suggestion]
- AutocompleteEngine.explain(text: str) -> list[RankingExplanation]
- AutocompleteEngine.explain_as_dicts(text: str) -> list[dict]
- AutocompleteEngine.record_selection(text: str, value: str)
- AutocompleteEngine.history (read-only)

All other methods and attributes are considered internal and could change without notice.


## Design Scaling

This system is intentionally designed to scale beyond autocomplete.

The same architecture supports:
- Search ranking
- Recommendation engines
- Query completion
- ML-backed ranking layers

New predictors, rankers, or learning strategies can be introduced
without modifying existing components.


## Extension Points

Custom predictors may be implemented by conforming to the Predictor protocol.

Predictors:
- Produce ScoredSuggestion
- Must not mutate shared state
- Should emit PredictorExplanation when possible

Custom rankers must implement the Ranker interface.

Rankers:
- Operate on scored suggestions
- Must preserve determinism
- Must not strip scores or suggestions
- May optionally learn from History

Weighted Components:

Predictors and rankers may be wrapped with weights
to influence their relative impact without modifying logic.


## Stability Guarantees

This project follows these stability rules:

- Core domain types (Suggestion, ScoredSuggestion, CompletionContext)
  are stable once released
- Public engine methods are backward compatible
- Internal helper methods may change freely
- Explanation fields are additive only (no breaking removals)


## Non-Goals

This project intentionally does not aim to:

- Be a full ML framework
- Optimize for maximum performance
- Provide a UI or frontend
- Compete with production search engines


# Tradeoffs

- Simplicity over performance:
  The engine prioritizes clarity and correctness over throughput.

- Determinism over stochastic models:
  No randomness or ML models are used.

- Explicit design over implicit magic:
  All ranking and learning behavior is visible and explainable.


## Current Limitations

- No persistence layer for history (its in-memory only)
- No batching/streaming support
- No large-scale indexing structures
- Predictors are hand-written, not learned
- No domain-specific tuning out of the box
