"use client";

import { FormEvent, useMemo, useState } from "react";

type Provider = "gemini" | "openai" | "anthropic";

type ModelResult = {
  provider: string;
  model: string;
  content: string | null;
  latency_ms: number;
  input_tokens: number | null;
  output_tokens: number | null;
  estimated_cost: number | null;
  quality_score: number | null;
  error_code: string | null;
  error: string | null;
};

type Recommendation = {
  provider: string;
  score: number;
  reason: string;
};

type CompareResponse = {
  comparison_id: number | null;
  results: ModelResult[];
  recommendation: Recommendation | null;
};

type HistoryItem = {
  id: number;
  prompt: string;
  created_at: string;
  results: ModelResult[];
  recommendation: Recommendation | null;
};

const providerDetails: Record<
  Provider,
  { label: string; short: string; accent: string }
> = {
  gemini: { label: "Google Gemini", short: "G", accent: "violet" },
  openai: { label: "OpenAI", short: "O", accent: "green" },
  anthropic: { label: "Anthropic Claude", short: "A", accent: "amber" },
};

const defaultPrompt =
  "Explain vector embeddings to a beginner in under 100 words.";

const ratingFields = [
  "accuracy",
  "completeness",
  "format_following",
  "conciseness",
  "usefulness",
] as const;

function formatCost(cost: number | null) {
  if (cost === null) return "Unknown";
  if (cost === 0) return "$0";
  return `$${cost.toFixed(6)}`;
}

function formatProvider(provider: string) {
  return (
    providerDetails[provider as Provider]?.label ??
    provider.charAt(0).toUpperCase() + provider.slice(1)
  );
}

export default function Home() {
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [providers, setProviders] = useState<Provider[]>([
    "gemini",
    "openai",
    "anthropic",
  ]);
  const [apiBaseUrl, setApiBaseUrl] = useState(
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  );
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ratings, setRatings] = useState<
    Record<string, Record<string, number>>
  >({});
  const [ratingStatus, setRatingStatus] = useState<Record<string, string>>({});

  const totalCost = useMemo(
    () =>
      result?.results.reduce(
        (sum, item) => sum + (item.estimated_cost ?? 0),
        0,
      ) ?? 0,
    [result],
  );

  function toggleProvider(provider: Provider) {
    setProviders((current) =>
      current.includes(provider)
        ? current.filter((item) => item !== provider)
        : [...current, provider],
    );
  }

  function saveApiUrl(value: string) {
    const normalized = value.replace(/\/$/, "");
    setApiBaseUrl(normalized);
    window.localStorage.setItem("comparator-api-url", normalized);
  }

  async function compare(event: FormEvent) {
    event.preventDefault();
    if (!prompt.trim() || providers.length === 0) return;

    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt.trim(), providers }),
      });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      const data = (await response.json()) as CompareResponse;
      setResult(data);
    } catch {
      setError(
        "Could not reach the comparator API. Confirm the backend is running and the API URL is correct.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory() {
    setHistoryLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/compare/history`);
      if (!response.ok) throw new Error("History request failed");
      setHistory((await response.json()) as HistoryItem[]);
    } catch {
      setError("Could not load comparison history from the API.");
    } finally {
      setHistoryLoading(false);
    }
  }

  function setRating(provider: string, field: string, value: number) {
    setRatings((current) => ({
      ...current,
      [provider]: {
        ...(current[provider] ?? {}),
        [field]: value,
      },
    }));
  }

  async function submitRating(provider: string) {
    if (!result?.comparison_id) return;
    const providerRatings = ratings[provider] ?? {};
    const complete = ratingFields.every((field) => providerRatings[field]);
    if (!complete) {
      setRatingStatus((current) => ({
        ...current,
        [provider]: "Score all five dimensions first.",
      }));
      return;
    }

    setRatingStatus((current) => ({
      ...current,
      [provider]: "Saving…",
    }));
    try {
      const response = await fetch(
        `${apiBaseUrl}/api/v1/compare/history/${result.comparison_id}/ratings/${provider}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(providerRatings),
        },
      );
      if (!response.ok) throw new Error("Rating request failed");
      const rated = (await response.json()) as ModelResult;
      setResult((current) =>
        current
          ? {
              ...current,
              results: current.results.map((item) =>
                item.provider === provider ? rated : item,
              ),
            }
          : current,
      );
      setRatingStatus((current) => ({
        ...current,
        [provider]: `Saved · quality ${rated.quality_score?.toFixed(1)}/5`,
      }));
    } catch {
      setRatingStatus((current) => ({
        ...current,
        [provider]: "Could not save rating.",
      }));
    }
  }

  return (
    <main>
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <nav className="topbar">
        <a className="brand" href="#top" aria-label="Model Meter home">
          <span className="brand-mark">M</span>
          <span>Model Meter</span>
        </a>
        <div className="nav-actions">
          <button className="text-button" onClick={loadHistory} type="button">
            {historyLoading ? "Loading…" : "History"}
          </button>
          <span className="status-dot">
            <i />
            Comparator workspace
          </span>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="eyebrow">
          <span>Multi-model intelligence lab</span>
        </div>
        <h1>
          One prompt.
          <br />
          <span>Every perspective.</span>
        </h1>
        <p className="hero-copy">
          Compare leading language models on the evidence that matters:
          response quality, speed, token usage, cost, and reliability.
        </p>
      </section>

      <section className="workspace">
        <form className="prompt-panel" onSubmit={compare}>
          <div className="panel-heading">
            <div>
              <span className="section-number">01</span>
              <h2>Compose your test</h2>
            </div>
            <span className="character-count">{prompt.length} / 20,000</span>
          </div>

          <label className="sr-only" htmlFor="prompt">
            Prompt
          </label>
          <textarea
            id="prompt"
            maxLength={20000}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Ask a question, test an instruction, or paste content to analyze…"
            rows={6}
            value={prompt}
          />

          <div className="provider-section">
            <p>Select providers</p>
            <div className="provider-grid">
              {(Object.keys(providerDetails) as Provider[]).map((provider) => {
                const details = providerDetails[provider];
                const selected = providers.includes(provider);
                return (
                  <button
                    aria-pressed={selected}
                    className={`provider-option ${selected ? "selected" : ""}`}
                    key={provider}
                    onClick={() => toggleProvider(provider)}
                    type="button"
                  >
                    <span className={`provider-symbol ${details.accent}`}>
                      {details.short}
                    </span>
                    <span>{details.label}</span>
                    <i>{selected ? "✓" : "+"}</i>
                  </button>
                );
              })}
            </div>
          </div>

          <details className="api-settings">
            <summary>Connection settings</summary>
            <label htmlFor="api-url">Backend API URL</label>
            <input
              id="api-url"
              onBlur={(event) => saveApiUrl(event.target.value)}
              onChange={(event) => setApiBaseUrl(event.target.value)}
              value={apiBaseUrl}
            />
          </details>

          <button
            className="compare-button"
            disabled={loading || !prompt.trim() || providers.length === 0}
            type="submit"
          >
            <span>{loading ? "Comparing models…" : "Run comparison"}</span>
            <b>{loading ? "•••" : "→"}</b>
          </button>
        </form>

        <aside className="evidence-panel">
          <span className="section-number">How it works</span>
          <ol>
            <li>
              <b>Parallel inference</b>
              <span>Your prompt reaches every selected provider at once.</span>
            </li>
            <li>
              <b>Normalized evidence</b>
              <span>Responses use one contract for fair comparison.</span>
            </li>
            <li>
              <b>Measured recommendation</b>
              <span>Quality, latency, and cost shape the final ranking.</span>
            </li>
          </ol>
          <div className="evidence-note">
            <span>Engineering principle</span>
            <p>One measurement is an observation. Repeated tests are evidence.</p>
          </div>
        </aside>
      </section>

      {error && (
        <section className="notice error-notice" role="alert">
          <span>Connection issue</span>
          <p>{error}</p>
        </section>
      )}

      {loading && (
        <section className="loading-section" aria-live="polite">
          <div className="loading-line" />
          <p>Models are working in parallel. Results arrive together.</p>
        </section>
      )}

      {result && (
        <section className="results-section">
          <div className="results-heading">
            <div>
              <span className="section-number">02</span>
              <h2>Comparison evidence</h2>
            </div>
            <div className="run-summary">
              <span>{result.results.length} models</span>
              <span>{formatCost(totalCost)} estimated total</span>
              {result.comparison_id && <span>Run #{result.comparison_id}</span>}
            </div>
          </div>

          {result.recommendation && (
            <div className="recommendation">
              <span className="recommendation-icon">★</span>
              <div>
                <small>Recommended for this prompt</small>
                <h3>{formatProvider(result.recommendation.provider)}</h3>
                <p>{result.recommendation.reason}</p>
              </div>
              <b>{Math.round(result.recommendation.score * 100)} score</b>
            </div>
          )}

          <div className="result-grid">
            {result.results.map((item) => {
              const details =
                providerDetails[item.provider as Provider] ??
                providerDetails.openai;
              return (
                <article
                  className={`result-card ${item.error ? "failed" : ""}`}
                  key={item.provider}
                >
                  <header>
                    <div>
                      <span className={`provider-symbol ${details.accent}`}>
                        {details.short}
                      </span>
                      <div>
                        <h3>{formatProvider(item.provider)}</h3>
                        <code>{item.model}</code>
                      </div>
                    </div>
                    <span className={item.error ? "error-chip" : "success-chip"}>
                      {item.error ? "Failed" : "Complete"}
                    </span>
                  </header>

                  <div className="metrics">
                    <div>
                      <span>Latency</span>
                      <b>{item.latency_ms.toLocaleString()} ms</b>
                    </div>
                    <div>
                      <span>Tokens</span>
                      <b>
                        {(item.input_tokens ?? 0) + (item.output_tokens ?? 0) ||
                          "—"}
                      </b>
                    </div>
                    <div>
                      <span>Est. cost</span>
                      <b>{formatCost(item.estimated_cost)}</b>
                    </div>
                    <div>
                      <span>Quality</span>
                      <b>
                        {item.quality_score
                          ? `${item.quality_score.toFixed(1)}/5`
                          : "Unrated"}
                      </b>
                    </div>
                  </div>

                  <div className="response-copy">
                    {item.error ? (
                      <>
                        <small>{item.error_code}</small>
                        <p>{item.error}</p>
                      </>
                    ) : (
                      <p>{item.content}</p>
                    )}
                  </div>

                  {!item.error && result.comparison_id && (
                    <div className="rating-panel">
                      <p>Rate this response</p>
                      <div className="rating-grid">
                        {ratingFields.map((field) => (
                          <label key={field}>
                            <span>{field.replace("_", " ")}</span>
                            <select
                              onChange={(event) =>
                                setRating(
                                  item.provider,
                                  field,
                                  Number(event.target.value),
                                )
                              }
                              value={ratings[item.provider]?.[field] ?? ""}
                            >
                              <option disabled value="">
                                —
                              </option>
                              {[1, 2, 3, 4, 5].map((score) => (
                                <option key={score} value={score}>
                                  {score}
                                </option>
                              ))}
                            </select>
                          </label>
                        ))}
                      </div>
                      <button
                        onClick={() => submitRating(item.provider)}
                        type="button"
                      >
                        Save rating
                      </button>
                      {ratingStatus[item.provider] && (
                        <small>{ratingStatus[item.provider]}</small>
                      )}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        </section>
      )}

      {history.length > 0 && (
        <section className="history-section">
          <div className="results-heading">
            <div>
              <span className="section-number">03</span>
              <h2>Recent experiments</h2>
            </div>
            <button className="text-button" onClick={() => setHistory([])}>
              Close
            </button>
          </div>
          <div className="history-list">
            {history.slice(0, 10).map((item) => (
              <article key={item.id}>
                <div>
                  <span>Run #{item.id}</span>
                  <time>{new Date(item.created_at).toLocaleString()}</time>
                </div>
                <p>{item.prompt}</p>
                <small>
                  {item.results.length} models
                  {item.recommendation
                    ? ` · recommended ${formatProvider(item.recommendation.provider)}`
                    : ""}
                </small>
              </article>
            ))}
          </div>
        </section>
      )}

      <footer>
        <span>Model Meter</span>
        <p>Measure the trade-off. Choose with evidence.</p>
      </footer>
    </main>
  );
}
