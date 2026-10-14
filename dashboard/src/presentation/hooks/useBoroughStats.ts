import { useEffect, useState } from "react";
import {
  FALLBACK_BOROUGH_STATS,
  type BoroughStat,
} from "@domain/entities/BoroughStat";
import { fetchBoroughStats } from "@infra/repositories/BenchmarkRepository";

interface BoroughStatsState {
  stats: BoroughStat[] | null;
  usingFallback: boolean;
}

export function useBoroughStats(): BoroughStatsState {
  const [stats, setStats] = useState<BoroughStat[] | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchBoroughStats()
      .then((live) => {
        if (cancelled) return;
        setStats(live);
        setUsingFallback(false);
      })
      .catch(() => {
        if (cancelled) return;
        setStats(FALLBACK_BOROUGH_STATS);
        setUsingFallback(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { stats, usingFallback };
}
