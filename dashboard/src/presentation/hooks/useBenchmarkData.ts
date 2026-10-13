import { useEffect, useState } from "react";
import type { BenchmarkResult } from "@domain/entities/BenchmarkResult";
import { fetchBenchmarkResults } from "@infra/repositories/BenchmarkRepository";

interface BenchmarkState {
  data: BenchmarkResult | null;
  loading: boolean;
  error: string | null;
}

export function useBenchmarkData(): BenchmarkState {
  const [state, setState] = useState<BenchmarkState>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    fetchBenchmarkResults()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message =
            err instanceof Error ? err.message : "Failed to load data";
          setState({ data: null, loading: false, error: message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
