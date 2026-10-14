import type { BenchmarkResult } from "../../domain/entities/BenchmarkResult";
import type { ExperimentsReport } from "../../domain/entities/Experiments";
import type { BoroughStat } from "../../domain/entities/BoroughStat";

const API_BASE = "http://localhost:8788";

export async function fetchBoroughStats(): Promise<BoroughStat[]> {
  const response = await fetch(`${API_BASE}/api/borough-stats`);
  if (!response.ok) {
    throw new Error(`Failed to load borough stats: ${response.status}`);
  }
  const body = (await response.json()) as { boroughs: BoroughStat[] };
  return body.boroughs;
}

export async function fetchBenchmarkResults(): Promise<BenchmarkResult> {
  const response = await fetch("/benchmark_full.json");
  if (!response.ok) {
    throw new Error(`Failed to load benchmark results: ${response.status}`);
  }
  return response.json();
}

// The experiments file is optional: it only exists after `benchmark.py experiments` ran
// and was copied to public/. A missing file is not an error, the section is just hidden.
export async function fetchExperiments(): Promise<ExperimentsReport | null> {
  const response = await fetch("/experiments_full.json");
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`Failed to load experiments: ${response.status}`);
  }
  const body = await response.json();
  // Vite answers unknown paths with index.html; treat anything that is not our report as absent.
  return body && Array.isArray(body.queries) ? (body as ExperimentsReport) : null;
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
