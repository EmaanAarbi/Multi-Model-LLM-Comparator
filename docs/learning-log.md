# Engineering Learning Log

## Milestone 2 — Provider adapter interface and automated tests

### Concept

A provider adapter implements one application-owned contract and translates an
external SDK response into the comparator's normalized `ModelResult`.

### Real problem it solves

Routes and future comparison orchestration can use Gemini, OpenAI, or Claude
without depending on each provider's SDK-specific request and response shapes.

### What can go wrong

- Provider-specific details can leak through the common interface.
- Tests can accidentally make paid network calls.
- A mock can drift away from the real SDK behavior.
- Broad exception handling can expose sensitive provider details.

### Trade-off

The adapter boundary adds a small amount of structure now, but prevents
provider conditionals from spreading throughout the API as integrations grow.
Mocked unit tests are fast and deterministic, while a smaller separate
integration suite will still be needed to verify real provider behavior.

### How we prove it works

- `GeminiService` implements the provider contract.
- API tests replace the provider dependency without configuring an API key.
- Service tests cover successful, empty, and failed SDK responses.
- Validation tests prove invalid prompts never reach a provider.
- The existing public endpoint retains its normalized response contract.

## Milestone 3 — OpenAI and Anthropic provider adapters

### Concept

Integrating multiple hosted model SDKs behind the same application-owned
`LLMProvider` interface and exposing one normalized endpoint per provider.
OpenAI uses the Responses API; Anthropic uses the Messages API.

### Real problem it solves

The comparator can call OpenAI and Claude without leaking either SDK's request
or response structure into the route layer. Future orchestration can treat all
providers uniformly.

### Why this implementation

- Each adapter owns SDK construction, latency measurement, text extraction,
  and error normalization.
- FastAPI dependency factories make adapters replaceable in tests.
- The API accepts the same bounded prompt schema for every provider.
- OpenAI uses the current Responses API rather than the older Chat
  Completions interface.

### What can go wrong

- A key may be missing, invalid, or accidentally committed.
- An account may have insufficient credits or hit a rate limit.
- A configured model may be unavailable to the account.
- Providers return text and errors in different shapes.
- A successful response may contain no text or non-text content blocks.
- Returning raw SDK exception messages may expose unnecessary provider
  details; typed public errors will be added in the resilience milestone.

### Trade-off

Direct SDK integrations provide full visibility and control, but require one
adapter and maintenance path per provider. Normalizing errors makes partial
comparisons possible, while temporarily losing provider-specific error types
until a structured error schema is introduced.

### How we prove it works

- OpenAI and Anthropic adapters implement `LLMProvider`.
- Mocked tests verify successful, empty, mixed-content, and exception paths
  without network calls or API charges.
- API tests verify `/openai`, `/claude`, and `/gemini` route to the correct
  injected adapter.
- Real requests reached both provider APIs and returned normalized billing
  errors without crashing; successful generation requires account credits.

## Milestone 4 — Concurrent comparison

### Concept

Run independent synchronous provider calls concurrently and preserve the
requested result order.

### Real problem it solves

Users wait roughly for the slowest selected provider rather than the sum of all
provider latencies, and one provider's normalized failure does not erase other
results.

### Trade-off

Worker threads fit the current synchronous SDK adapters and keep the design
simple. Native async clients may scale more efficiently at higher traffic.

### How we prove it works

Timed test adapters demonstrate concurrent wall-clock behavior, deterministic
ordering, partial failures, and selected-provider validation.

## Milestone 5 — Token usage and cost

### Concept

Read provider-native usage metadata and normalize input tokens, output tokens,
and estimated USD cost.

### Real problem it solves

Model selection can include operating cost rather than relying only on output
quality.

### Trade-off

Hardcoded pricing is fast and auditable but requires maintenance. Unknown
models return no estimate instead of a misleading value.

### How we prove it works

Adapter tests verify usage extraction and cost tests verify pricing arithmetic,
unknown models, and missing metadata.

## Milestone 6 — Persistence and evaluation

### Concept

Persist comparison runs and provider results, then attach five-dimension manual
ratings and calculate a quality score.

### Real problem it solves

Users can revisit experiments, compare evidence over time, and improve model
recommendations with human judgment.

### Trade-off

SQLite is convenient locally; PostgreSQL is configured for deployment.
Automatic schema creation is appropriate for this portfolio milestone, while a
long-lived production system should add versioned database migrations.

### How we prove it works

Repository tests cover save, retrieval, ordering, missing records, and rating
persistence. A ten-case benchmark dataset provides repeatable prompts and
evaluation criteria.

## Milestone 7 — Resilience and production packaging

### Concept

Apply safe public error codes, SDK timeouts/retries, unexpected-adapter
containment, container packaging, and continuous integration.

### Real problem it solves

External APIs fail in normal operation. The comparator stays useful, avoids
leaking raw provider details, and can be tested and deployed consistently.

### Trade-off

Retries improve transient reliability but can increase tail latency and cost.
The current policy relies on SDK retry behavior and keeps explicit application
logic small.

### How we prove it works

Tests cover error classification and adapter failures. Docker uses a supported
Python runtime, Compose provisions PostgreSQL, and CI runs the complete
network-free test suite.

## Milestone 8 — React comparison interface

### Concept

A typed, responsive client consumes the normalized comparison API and presents
model evidence without exposing provider credentials.

### Real problem it solves

Users can select providers, run one prompt, inspect side-by-side results,
review recommendations and history, and submit manual quality ratings without
working directly with API documentation.

### Trade-off

The deployed frontend needs a reachable backend URL and matching CORS origin.
Keeping that connection configurable supports local development and different
hosting providers without rebuilding the interface.

### How we prove it works

The production frontend build, lint checks, and rendered HTML tests verify the
final application and confirm that all starter-only assets and metadata were
removed.
