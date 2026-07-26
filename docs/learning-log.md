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
