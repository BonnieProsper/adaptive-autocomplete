# Adaptive Autocomplete Core (AAC)

Adaptive Autocomplete Core (AAC) is a modular, explainable autocomplete and ranking engine designed to demonstrate how production systems generate, rank, learn from, and explain suggestions in a deterministic and auditable way.

The project focuses on architecture, correctness, and extensibility over features, emphasising clear boundaries between signal generation, aggregation, ranking, learning, and explanation while remaining deterministic, testable, and inspectable.

This repository is intentionally scoped and opinionated. Design decisions are intentionally made to favor clarity, extensibility, and auditability.

## What this project demonstrates

This project is intentionally designed to showcase:

- Clean separation of concerns in a non-trivial backend system
- Deterministic ranking pipelines with learning and explainability
- Explicit architectural invariants enforced at runtime
- Safe extension via composition rather than inheritance
- Production-quality Python: typing, testing, linting, and CI

While the demo is an autocomplete engine, the underlying architecture directly maps to real-world search, recommendation, and ranking systems.


## High-level architecture

AAC is structured as a layered pipeline with explicit responsibilities and invariants:

User Input
  → CompletionContext
    → Predictors (raw signals)
      → Weighted Aggregation
        → Rankers (ordering + learning)
          → Suggestions + Explanations


Each stage is isolated. No layer reaches across boundaries or performs hidden work.

# Design principles

## Single source of truth

- History is owned by the engine
- Rankers may read from or learn from history, but do not own it
- Predictors are stateless by default and never depend on global state

This prevents accidental coupling and makes learning behavior explicit.

## Separation of prediction and ranking

The system explicitly distinguishes between:

- Prediction: generating candidate suggestions with raw scores
- Ranking: ordering those candidates and applying learning or normalization

Predictors never rank and rankers never generate suggestions.
This separation allows each concern to evolve independently and remain testable.

## Explainability as a first-class invariant

AAC enforces a strict explanation model:

- PredictorExplanation represents raw, unnormalized signals
- RankingExplanation represents the final user-facing rationale

Explanations always correspond to the final ranked output, not intermediate or discarded values. If a score exists, it can be explained.

## Immutability at boundaries

Core domain objects are immutable:

- CompletionContext
- Suggestion
- ScoredSuggestion

Rankers return new orderings rather than mutating input. This encourages determinism, safe composition, and predictable behavior under extension.

# Component responsibilities
## Predictors

Predictors are independent signal generators. They:

- Generate candidate suggestions
- Assign raw scores
- May optionally emit PredictorExplanation
- Do not rank, normalize, or learn
- Must not mutate shared state

Examples include prefix matchers, trie-based lookups, frequency biasing, or history-based intent signals.

## Engine

The AutocompleteEngine orchestrates the entire pipeline. It:

- Owns the lifecycle of CompletionContext and History
- Aggregates and weights predictor output
- Applies rankers sequentially
- Enforces architectural invariants
- Exposes a minimal, stable public API

The engine contains no domain-specific logic, only coordination and validation.

## Rankers

Rankers are responsible for ordering and optional learning. They:

- Reorder existing suggestions
- Must not add or remove candidates
- May apply learning, decay, or normalization
- Must preserve determinism and finite scores
- May read from history but do not own it
- Rankers may rescore suggestions as part of normalization or learning, but must not add or remove candidates.

Rankers are composable and applied sequentially.

## Explanations

Explanations are:

- Aggregated across rankers
- Always consistent with final ranking
- Exportable in JSON-safe form
- Additive over time (no breaking removals)

This makes the system suitable for developer tooling, debugging, and API consumption.

## Public API

The following engine methods are considered stable:

- AutocompleteEngine.suggest(text: str) -> list[Suggestion]
- AutocompleteEngine.explain(text: str) -> list[RankingExplanation]
- AutocompleteEngine.explain_as_dicts(text: str) -> list[dict]
- AutocompleteEngine.record_selection(text: str, value: str)
- AutocompleteEngine.history  # read-only access

Semi-internal (documented, but not for end users):

- AutocompleteEngine.predict_scored(ctx: CompletionContext)

Internal/developer-only:

- Debug and pipeline introspection utilities
- Unranked scoring helpers

Only documented methods should be used by external consumers.

## CLI

AAC includes a minimal CLI to demonstrate usability and integration.

Examples:

aac suggest pri
aac explain pri
aac record pri print
aac debug pri


The CLI is intentionally thin and delegates all logic to the core engine.

# Extension points

AAC is designed to grow without modification to existing components.

## Custom predictors

To add a predictor, implement the Predictor protocol:

- Return ScoredSuggestion
- Avoid shared mutable state
- Emit PredictorExplanation when possible

## Custom rankers

To add a ranker:

- Implement the Ranker interface
- Preserve determinism
- Do not add or remove suggestions
- Optionally implement history-based learning

## Weighted composition

Predictors and rankers can be weighted externally (e.g WeightedPredictor) to tune influence without modifying internal logic.

## Stability guarantees

This project follows explicit stability rules:

- Core domain types are stable once released
- Public engine APIs are backward compatible
- Internal helpers may change freely
- Explanation fields are additive only

These guarantees make the system safe to extend and reason about.

## Design scaling

The system is intentionally generic and domain-agnostic. Although demonstrated as an autocomplete engine, the same architecture supports:

- Search ranking
- Recommendation systems
- Query completion
- Hybrid ML + heuristic ranking

## Non-goals

Clarity, correctness, and explainability are prioritized over raw performance. CLI and storage layers are intentionally thin and integration-tested manually; core logic is exhaustively unit-tested. This project intentionally does not aim to:

- Be a full ML framework
- Optimize for maximum throughput
- Provide a UI or frontend
- Compete with large-scale search engines


## Tradeoffs

- Clarity over performance: explicit wiring and invariants are favored over micro-optimizations
- Determinism over stochastic models: no randomness or opaque ML
- Explicit learning: learning signals are bounded and optional

## Testing and coverage

Core domain logic (engine, predictors, rankers, history, explanation) is fully unit-tested.

CLI, configuration, and persistence layers are intentionally thin and not exhaustively unit-tested, as they primarily delegate to the core engine. This mirrors real production systems, where business logic receives the strongest testing guarantees.



## Current limitations

- History persistence is simple and file-based
- No batching or streaming APIs
- No large-scale indexing structures
- Predictors are hand-authored, not learned
- No domain-specific tuning out of the box


## Demo

Adaptive Autocomplete learns from usage and explains its decisions.

### Basic suggestion

$ aac suggest he
hello
help
helium
hero

### Learning from selection

$ aac record he hello
Recorded selection 'hello' for input 'he'

$ aac suggest he
hello
help
helium
hero

(The ranking adapts based on usage history.)

### Explanation

$ aac explain he
hello        base= 28.00 history=+ 4.50 = 32.50 [source=score]
help         base= 20.00 history=+ 3.00 = 23.00 [source=score]
helium       base=  4.00 history=  0.00 =  4.00 [source=score]

Each suggestion includes:
- Base predictor score
- Learning / history adjustment
- Final ranking score
- Source ranker

### Debug (developer-only)

$ aac debug he
Input: he

Scored:
  hello        score=28.00
  help         score=20.00

Ranked:
  hello        score=32.50
  help         score=23.00
