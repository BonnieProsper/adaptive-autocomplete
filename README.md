# Adaptive Autocomplete Core (AAC)

Adaptive Autocomplete Core (AAC) is a modular, explainable autocomplete and ranking engine designed to demonstrate how production systems generate, rank, learn from, and explain suggestions in a deterministic and auditable way.

While the demo domain is autocomplete, the architecture maps directly to real-world search, recommendation, and ranking systems. The project prioritizes **clarity, correctness, and explainability** over feature breadth or UI polish.

This repository is intentionally scoped and opinionated. Design decisions favor explicit boundaries and inspectability over clever abstractions or scale.

---

## What this project demonstrates

AAC is built to showcase:

- Clean separation of concerns in a non-trivial backend system
- Deterministic ranking pipelines with learning and explainability
- Explicit architectural invariants enforced at runtime
- Safe extensibility via composition rather than inheritance
- Production-quality Python (typing, tests, benchmarks, CLI)

This is not a toy autocomplete — it is a **systems design exercise**.

---

## Who this is for

This project is intended for reviewers interested in:

- Backend / platform engineering
- Ranking and recommendation pipelines
- Explainable systems
- Production-quality Python architecture

It deliberately avoids frontend concerns and UI complexity.

---

## Demo (CLI)

AAC includes a minimal CLI that exercises the full pipeline end to end.

### List available presets

$ aac presets

Presets define behavioral intent, not configuration detail.

### Basic autocomplete
$ aac suggest he
hello
help
hero
helium

### Learning from user selection
$ aac record he hero
Recorded selection 'hero' for input 'he'

$ aac suggest he
hello
help
hero
helium


The engine adapts based on selection history (except in stateless mode).

### Explainability
$ aac explain he
hello        base=115.00 history=  0.00 = 115.00 [source=score]
help         base= 86.00 history=  0.00 =  86.00 [source=score]
hero         base= 50.00 history=  0.00 =  50.00 [source=score]
helium       base= 30.00 history=  0.00 =  30.00 [source=score]


Each suggestion includes:
- Base predictor score
- Learning/history adjustment
- Final ranking score
- Contributing ranker

If a score exists, it can be explained.

### Robust typo recovery
$ aac --preset robust suggest helo
hello
help
hero
hex
heap


The robust preset recovers from minor typos without polluting exact-prefix behavior.

### Debug pipeline (developer-facing)
$ aac debug he
Input: he

Scored:
  hello        score=115.00
  help         score=86.00
  helium       score=30.00
  hero         score=53.00

Ranked:
  hello        score=115.00
  help         score=86.00
  hero         score=53.00
  helium       score=30.00


The CLI is intentionally thin and delegates all logic to the core engine.

## Presets overview
Preset	Learns	Typo Recovery	Intended Use
stateless	❌	❌	Deterministic, high-throughput systems
default	✅	❌	General-purpose autocomplete
recency	✅ (decay)	❌	Time-adaptive suggestions
robust	✅	✅	Real-world noisy input

Presets are the primary public control surface. Internal wiring is hidden by design.

## High-level architecture

AAC is structured as a layered pipeline with explicit responsibilities:

User Input
   ↓
CompletionContext
   ↓
Predictors ──▶ Scored Suggestions (raw signals)
   ↓
Weighted Aggregation
   ↓
Rankers (ordering + learning)
   ↓
Final Suggestions + Explanations


Each stage is isolated. No layer reaches across boundaries or performs hidden work.

## Design principles
### Single source of truth

- History is owned by the engine
- Rankers may read from history but do not own it
- Predictors are stateless by default
- No global mutable state

Learning behavior is explicit and auditable.

### Separation of prediction and ranking

The system strictly distinguishes between:

- Prediction: generating candidate suggestions with raw scores
- Ranking: ordering candidates and applying learning or normalization

Predictors never rank. Rankers never generate suggestions.

### Explainability as a first-class invariant

AAC enforces a strict explanation model:

- Predictor explanations represent raw upstream signals
- Ranking explanations represent final, user-facing decisions
- Explanations always correspond to the final output

If a value appears in the output, it can be explained.

### Immutability at boundaries

Core domain objects are treated as immutable at system boundaries:
- CompletionContext
- Suggestion
- ScoredSuggestion

Rankers return new orderings rather than mutating inputs, ensuring determinism and safe composition.

## Component responsibilities
### Predictors

Predictors are independent signal generators. They:
- Generate candidate suggestions
- Assign raw scores
- Optionally emit predictor explanations
- Do not rank or learn
- Must not mutate shared state

## Engine

The AutocompleteEngine orchestrates the pipeline. It:
- Owns history and learning boundaries
- Aggregates weighted predictor output
- Applies rankers sequentially
- Enforces architectural invariants
- Exposes a minimal, stable public API

The engine contains no domain-specific logic - only coordination and validation.

## Rankers

Rankers are responsible for ordering and optional learning. They:

- Reorder existing suggestions
- May rescore for normalization or learning
- Must not add or remove candidates
- Preserve determinism and finite scores

Rankers are composable and applied sequentially.

## Public API stability

The following engine methods are considered stable:

- AutocompleteEngine.suggest(text: str) -> list[Suggestion]
- AutocompleteEngine.explain(text: str) -> list[RankingExplanation]
- AutocompleteEngine.explain_as_dicts(text: str) -> list[dict]
- AutocompleteEngine.record_selection(text: str, value: str)
- AutocompleteEngine.history (read-only)

Internal helpers and debug utilities are intentionally not part of the public API.

## Performance characteristics

Benchmarks were run on 60,000 autocomplete calls.

Preset	Avg Latency	Intended Use
stateless	~38 µs	High-throughput, no learning
default	~30 µs	Balanced general autocomplete
recency	~34 µs	Time-adaptive suggestions
robust	~145 µs	Typo-tolerant input

### Why is robust slower?

Robust mode uses edit-distance matching to recover from typos (e.g. helo → hello).
This introduces an intentional cost per candidate.

The tradeoff is explicit:
- CLI tools benefit from robustness
- Interactive UIs can debounce
- High-throughput systems can disable robust mode

### Testing philosophy

Core domain logic (engine, predictors, rankers, history, explanations) is fully unit-tested.

CLI and integration layers are intentionally thin and lightly tested, mirroring real production systems where business logic receives the strongest guarantees.

## Non-goals

This project intentionally does not aim to:

- Be a full ML framework
- Maximize throughput at all costs
- Provide a frontend or UI
- Compete with large-scale search engines

Clarity, correctness, and explainability are the priority.

AAC is intentionally small but complete.
It demonstrates how real systems balance learning, determinism, explainability, and performance — without hiding behavior behind opaque abstractions.