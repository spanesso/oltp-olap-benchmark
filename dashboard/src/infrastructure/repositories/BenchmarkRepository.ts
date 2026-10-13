import type { BenchmarkResult } from "../../domain/entities/BenchmarkResult";

const API_BASE = "http://localhost:8788";

export async function fetchBenchmarkResults(): Promise<BenchmarkResult> {
  const response = await fetch("/benchmark_full.json");
  if (!response.ok) {
    throw new Error(`Failed to load benchmark results: ${response.status}`);
  }
  return response.json();
}

export async function runLiveBenchmark(
  profile: "full" | "quick" = "full",
): Promise<BenchmarkResult> {
  const controller = new AbortController();
  // 11-minute client-side timeout (benchmark.py itself times out at 10 min)
  const timer = setTimeout(() => controller.abort(), 660_000);
  try {
    const response = await fetch(`${API_BASE}/api/benchmark/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile }),
      signal: controller.signal,
    });
    if (!response.ok) {
      const err = await response
        .json()
        .catch(() => ({ error: `Server error ${response.status}` }));
      throw new Error(
        (err as { error?: string }).error ?? `Server error ${response.status}`,
      );
    }
    return response.json();
  } finally {
    clearTimeout(timer);
  }
}
