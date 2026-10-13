import { useCallback, useEffect, useState } from "react";
import type { BenchmarkResult } from "@domain/entities/BenchmarkResult";
import {
  fetchBenchmarkResults,
  runLiveBenchmark,
} from "@infra/repositories/BenchmarkRepository";

interface BenchmarkState {
  data: BenchmarkResult | null;
  loading: boolean;
  running: boolean;
  error: string | null;
  runError: string | null;
  triggerLiveRun: () => void;
}

export function useBenchmarkData(): BenchmarkState {
  const [data, setData] = useState<BenchmarkResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchBenchmarkResults()
      .then((d) => {
        if (!cancelled) { setData(d); setLoading(false); }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load data");
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, []);

  const triggerLiveRun = useCallback(() => {
    if (running) return;
    setRunning(true);
    setRunError(null);
    runLiveBenchmark("full")
      .then((result) => { setData(result); })
      .catch((err: unknown) => {
        setRunError(err instanceof Error ? err.message : "Live benchmark failed");
      })
      .finally(() => { setRunning(false); });
  }, [running]);

  return { data, loading, running, error, runError, triggerLiveRun };
}
