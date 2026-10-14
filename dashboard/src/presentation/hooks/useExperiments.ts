import { useEffect, useState } from "react";
import type { ExperimentsReport } from "@domain/entities/Experiments";
import { fetchExperiments } from "@infra/repositories/BenchmarkRepository";

// The experiments are an optional extra: any failure simply hides the section.
export function useExperiments(): ExperimentsReport | null {
  const [report, setReport] = useState<ExperimentsReport | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchExperiments()
      .then((loaded) => {
        if (!cancelled) setReport(loaded);
      })
      .catch(() => {
        if (!cancelled) setReport(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return report;
}
