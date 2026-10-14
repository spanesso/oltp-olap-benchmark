export interface ExperimentCell {
  key: string;
  label: string;
  engine: "postgres" | "duckdb";
  schema: "normalized" | "star";
}

export interface CellSpread {
  medians_ms: number[];
  median_ms: number;
  min_ms: number;
  max_ms: number;
  cv_percent: number;
  range_percent: number;
}

export interface RatioSummary {
  median: number;
  min: number;
  max: number;
}

export interface ExperimentEffects {
  engine_on_normalized: RatioSummary;
  engine_on_star: RatioSummary;
  schema_on_postgres: RatioSummary;
  schema_on_duckdb: RatioSummary;
  combined: RatioSummary;
}

export interface ExperimentQuery {
  id: string;
  question: string;
  result_rows: number;
  cells: Record<string, CellSpread>;
  effects: ExperimentEffects;
}

export interface Repeatability {
  limit_percent: number;
  series: number;
  within_limit: number;
  worst: number;
}

export interface ExperimentsReport {
  schema_version: number;
  profile: string;
  generated_at: string;
  method: { repeats: number; warmup_runs: number; measured_runs: number };
  cells: ExperimentCell[];
  queries: ExperimentQuery[];
  repeatability: Repeatability;
}
