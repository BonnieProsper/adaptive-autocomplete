# Adaptive Autocomplete Core (AAC)

Adaptive Autocomplete Core (AAC) is a modular, explainable autocomplete and ranking engine that demonstrates how production systems generate, rank, learn from, and explain suggestions in a deterministic and auditable way.

The project prioritizes architecture, correctness, and extensibility over feature breadth. It focuses on clear boundaries between signal generation, aggregation, ranking, learning, and explanation, while remaining deterministic, testable, and easy to inspect.

This repository is intentionally scoped and opinionated. Design decisions favor clarity and auditability over cleverness or scale.

## What this project demonstrates

This project is designed to showcase:

- Clean separation of concerns in a non-trivial backend system
- Deterministic ranking pipelines with learning and explainability
- Explicit architectural invariants enforced at runtime
- Safe extensibility via composition rather than inheritance
- Production-quality Python (typing, tests, linting, CI)

While the demo uses autocomplete, the underlying architecture maps directly to real-world search, recommendation, and ranking systems.

## Who this is for

This project is intended for reviewers interested in backend systems design, ranking pipelines, and production-quality Python architecture rather than UI polish or frontend features.

# Demo (CLI)

AAC includes a minimal CLI to demonstrate learning, ranking, and explanation end to end.

## Basic suggestion
$ aac suggest he
hello
help
helium
hero

## Learning from selection
$ aac record he hello
Recorded selection 'hello' for input 'he'

$ aac suggest he
hello
help
helium
hero

The ranking adapts based on usage history.

## Explanation
$ aac explain he
hello        base= 28.00 history=+ 4.50 = 32.50 [source=score]
help         base= 20.00 history=+ 3.00 = 23.00 [source=score]
helium       base=  4.00 history=  0.00 =  4.00 [source=score]


Each suggestion includes:

Base predictor score

Learning / history adjustment

Final ranking score

Contributing ranker

## Debug (developer-only)
$ aac debug he
Input: he

Scored:
  hello        score=28.00
  help         score=20.00

Ranked:
  hello        score=32.50
  help         score=23.00


The CLI is intentionally thin and delegates all logic to the core engine.

# High-level architecture

AAC is structured as a layered pipeline with explicit responsibilities and enforced invariants:

User Input
   ↓
CompletionContext
   ↓
Predictors ──▶ ScoredSuggestion (raw signals)
   ↓
Weighted Aggregation
   ↓
Rankers (ordering + learning)
   ↓
Final Suggestions + Explanations


Each stage is isolated. No layer reaches across boundaries or performs hidden work.

# Design principles
Single source of truth

- History is owned by the engine
- Rankers may read from or learn from history, but do not own it
- Predictors are stateless by default and never depend on global state

This prevents accidental coupling and makes learning behavior explicit.

## Separation of prediction and ranking

The system explicitly distinguishes between:

- Prediction: generating candidate suggestions with raw scores
- Ranking: ordering those candidates and applying learning or normalization

Predictors never rank, and rankers never generate suggestions. This separation keeps each concern testable and independently evolvable.

## Explainability as a first-class invariant

AAC enforces a strict explanation model:

- Predictor explanations represent raw, unnormalized signals produced upstream
- Ranking explanations represent the final, user-facing rationale

Explanations always correspond to the final ranked output. If a score exists, it can be explained.

## Immutability at boundaries

Core domain objects are treated as immutable at system boundaries:
- CompletionContext
- Suggestion
- ScoredSuggestion

Rankers return new orderings rather than mutating inputs. This encourages determinism, safe composition, and predictable behavior under extension.

# Component responsibilities
## Predictors

Predictors are independent signal generators. They:
- Generate candidate suggestions
- Assign raw scores
- May optionally emit predictor explanations
- Do not rank, normalize, or learn
- Must not mutate shared state

Examples include prefix matchers, trie-based lookups, frequency biasing, or history-based intent signals.

## Engine

The AutocompleteEngine orchestrates the pipeline. It:
- Owns the lifecycle of CompletionContext and history
- Aggregates and weights predictor output
- Applies rankers sequentially
- Enforces architectural invariants
- Exposes a minimal, stable public API

The engine contains no domain-specific logic - only coordination and validation.

## Rankers

Rankers are responsible for ordering and optional learning. They:
- Reorder existing suggestions
- May rescore suggestions as part of normalization or learning
- Must not add or remove candidates
- Must preserve determinism and finite scores
- May read from history but do not own it

Rankers are composable and applied sequentially.

## Explanations

Explanations are:
- Aggregated across rankers
- Always consistent with the final ranking
- Exportable in JSON-safe form
- Additive over time (no breaking removals)

This makes the system suitable for debugging, developer tooling, and API consumption.

# Public API

The following engine methods are considered stable:

- AutocompleteEngine.suggest(text: str) -> list[Suggestion]
- AutocompleteEngine.explain(text: str) -> list[RankingExplanation]
- AutocompleteEngine.explain_as_dicts(text: str) -> list[dict]
- AutocompleteEngine.record_selection(text: str, value: str)
- AutocompleteEngine.history (read-only)

Documented but semi-internal:

- AutocompleteEngine.predict_scored(ctx: CompletionContext)

Internal / developer-only:

- Debug and pipeline introspection utilities
- Unranked scoring helpers

Only documented methods should be used by external consumers.

# Extension points

AAC is designed to grow without modifying existing components.

## Custom predictors

To add a predictor:
- Implement the Predictor protocol
- Return scored suggestions
- Avoid shared mutable state
- Emit explanations when possible

## Custom rankers

To add a ranker:
- Implement the Ranker interface
- Preserve determinism
- Do not add or remove suggestions
- Optionally implement history-based learning

## Weighted composition

Predictors and rankers can be weighted externally (e.g WeightedPredictor) to tune influence without changing internal logic.

## Stability guarantees

This project follows explicit stability rules:

- Core domain types are stable once released
- Public engine APIs are backward compatible
- Internal helpers may change freely
- Explanation fields are additive only

These guarantees make the system safe to extend and reason about.

## Design scaling

Although demonstrated as an autocomplete engine, the same architecture supports:
- Search ranking
- Recommendation systems
- Query completion
- Hybrid ML + heuristic ranking

## Non-goals

Clarity, correctness, and explainability are prioritized over raw performance. This project intentionally does not aim to:
- Be a full ML framework
- Optimize for maximum throughput
- Provide a UI or frontend
- Compete with large-scale search engines

## Tradeoffs

- Clarity over performance: explicit wiring and invariants over micro-optimizations
- Determinism over stochastic models: no randomness or opaque ML
- Explicit learning: learning signals are bounded and optional

## Testing and coverage

Core domain logic (engine, predictors, rankers, history, explanations) is fully unit-tested.

CLI and integration layers are intentionally thin and not exhaustively tested, as they primarily delegate to the core engine. This mirrors real production systems, where business logic receives the strongest guarantees.

## Current limitations

History persistence is simple and file-based
- No batching or streaming APIs
- No large-scale indexing structures
- Predictors are hand-authored, not learned
- No domain-specific tuning out of the box

## Future work

Possible extensions include:
- Pluggable persistence backends (SQLite, Redis)
- Batch or streaming scoring APIs
- Learned predictor weights
- Time-decayed history models