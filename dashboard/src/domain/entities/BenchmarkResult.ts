export interface Timing {
  runs_ms: number[];
  median_ms: number;
  p95_ms: number;
  min_ms: number;
  max_ms: number;
}

export interface QueryResult {
  id: string;
  group: string;
  question: string;
  result_rows: number;
  oltp: Timing;
  olap: Timing;
  speedup: number;
  oltp_explain?: string;
  olap_explain?: string;
}

export interface Environment {
  os: string;
  cpu: string;
  cores: number;
  memory_gb: number;
  python: string;
  postgresql: string;
  postgresql_runtime: string;
  postgresql_settings: Record<string, string>;
  duckdb: string;
  duckdb_runtime: string;
  duckdb_settings: Record<string, string>;
}

export interface Dataset {
  source: string;
  rows: number;
  first_created_at: string;
  last_created_at: string;
}

export interface Method {
  warmup_runs: number;
  measured_runs: number;
  timer: string;
}

export interface Significance {
  evaluated: boolean;
  rule: string;
  queries_meeting_3x: number;
  analytical_queries: number;
  reached: boolean | null;
}

export interface BenchmarkResult {
  schema_version: number;
  profile: string;
  official: boolean;
  generated_at: string;
  dataset: Dataset;
  environment: Environment;
  method: Method;
  queries: QueryResult[];
  significance: Significance;
}
