export const en = {
  // ── Language toggle ──────────────────────────────────────────────────────
  lang_en: "EN",
  lang_es: "ES",

  // ── Header ───────────────────────────────────────────────────────────────
  header_title: "OLTP vs OLAP Benchmark",
  header_rows: "rows",
  header_profile: "profile",

  // ── Stat tiles ───────────────────────────────────────────────────────────
  stat_queries: "Queries",
  stat_volume: "Data volume",
  stat_volume_unit: "rows",
  stat_min_speedup: "Min speedup",
  stat_max_speedup: "Max speedup",
  stat_significance: "Significance",
  stat_reached: "Reached",
  stat_not_reached: "Not reached",

  // ── Live run ─────────────────────────────────────────────────────────────
  live_btn: "Refresh live measurement",
  live_running: "Measuring 6 queries × 2 engines…",
  live_hint_idle: "Requires: python dashboard/api_server.py · ~3 min",
  live_hint_running: "Please wait — the full profile can take ~3 min",
  live_error_connect: "Could not reach the server. Run: python dashboard/api_server.py",

  // ── Results table ────────────────────────────────────────────────────────
  table_aria: "Query benchmark results",
  table_col_query: "Query",
  table_col_question: "Question",
  table_col_oltp: "OLTP (ms)",
  table_col_olap: "OLAP (ms)",
  table_col_speedup: "Speedup",

  // ── Dataset introduction ─────────────────────────────────────────────────
  intro_title: "Why NYC 311 Service Requests?",
  intro_p1: "NYC 311 is New York City's non-emergency service line — citizens call or go online to report noise, potholes, lack of heat, graffiti. The city publishes every report as open data through the Socrata API, with access to over 22.7 million records since 2010.",
  intro_p2: "We evaluated 15 public datasets and chose NYC 311 for four reasons:",
  intro_why_volume: "5 million rows loaded in under 1 hour — large enough to show order-of-magnitude performance differences.",
  intro_why_dims: "6 natural analytical dimensions (complaint type, agency, location, time, channel, status) — ideal for the 6 OLAP queries.",
  intro_why_api: "No throttling with an app token: up to 50,000 rows per page, keyset pagination for reliable resumption.",
  intro_why_time: "Multi-year time range (we load the 2024–2026 cut) enabling year / quarter / month breakdowns in every query.",
  intro_why_volume_label: "Volume",
  intro_why_dims_label: "Dimensions",
  intro_why_api_label: "API",
  intro_why_time_label: "Time range",
  intro_api_endpoint: "API endpoint & parameters",
  intro_api_pagination: "Keyset pagination: each page passes the last (created_date, unique_key) as cursor — safe to resume after interruption.",
  intro_json_example: "Example raw record (one row from the API)",

  // ── API columns table ────────────────────────────────────────────────────
  api_columns_title: "12 columns downloaded from the API",
  api_col_name: "API column",
  api_col_example: "Real example",
  api_col_desc: "What it means",
  api_unique_key:             "Unique complaint ID. Never repeats. It is our primary key.",
  api_created_date:           "Exact date and time the citizen filed the complaint.",
  api_closed_date:            "Date it was resolved. NULL if still open.",
  api_agency:                 "Short agency code (NYPD, DOT, HPD…).",
  api_agency_name:            "Full agency name.",
  api_complaint_type:         "Complaint category. ~290 distinct types.",
  api_descriptor:             "Sub-category that details the type. ~1,700 descriptors.",
  api_borough:                'NYC borough. 5 values + "Unspecified": Manhattan, Brooklyn, Queens, Bronx, Staten Island.',
  api_incident_zip:           "ZIP code where the incident occurred.",
  api_community_board:        "Local community board responsible for the area.",
  api_open_data_channel_type: "How it was filed: PHONE, ONLINE, MOBILE, OTHER.",
  api_status:                 "Current status: Closed, Open, Pending, Started, etc.",

  // ── Schema viewer ────────────────────────────────────────────────────────
  schema_title: "Data model — schema diagrams",
  schema_tab_oltp: "OLTP (PostgreSQL 3NF)",
  schema_tab_olap: "OLAP — Star Schema (DuckDB)",
  schema_tab_staging: "Staging",
  schema_legend_pk: "PK — primary key",
  schema_legend_fk: "FK — foreign key",
  schema_legend_col: "regular column",
  schema_legend_rel: "1→N relation",
  schema_olap_note: "Star schema — fact_service_request in the center · 6 radial dimensions at 60°",
  schema_staging_note: "Staging tables have no relations between them — each is independent",

  // ── Section titles ───────────────────────────────────────────────────────
  section_pipeline: "Pipeline",
  section_speedup: "Speedup by query (log scale)",
  section_results: "Detailed results",
  section_absolute: "Absolute timing — median ms (linear scale)",
  section_radar: "Speedup coverage — radar view",
  section_map: "NYC complaint geography — by borough",
  section_explain: "Execution plans",
  section_env: "Environment",

  // ── Pipeline ─────────────────────────────────────────────────────────────
  pipeline_api: "NYC 311 API",
  pipeline_api_sub: "Socrata",
  pipeline_staging: "Staging",
  pipeline_staging_sub: "Raw data",
  pipeline_oltp: "OLTP",
  pipeline_oltp_sub: "3NF, 8 tables",
  pipeline_olap: "OLAP",
  pipeline_olap_sub: "Star, DuckDB",
  pipeline_bench: "Benchmark",
  pipeline_bench_sub: "6 queries ×2",
  pipeline_results: "Results",
  pipeline_results_sub: "JSON + MD",

  // ── Environment card ─────────────────────────────────────────────────────
  env_oltp_title: "OLTP — PostgreSQL",
  env_olap_title: "OLAP — DuckDB",

  // ── Borough map ──────────────────────────────────────────────────────────
  map_fallback_note: "Showing approximate borough data. Run make api for live complaint counts from DuckDB.",
  map_key_required: "Google Maps API Key required",
  map_key_desc: "Paste your key to see the NYC complaint map by borough. Stored only in your browser's localStorage.",
  map_key_placeholder: "AIzaSy...",
  map_key_help: "Get a free key at {link} — enable the Maps JavaScript API.",
  map_key_help_link: "Google Cloud Console",
  map_load_btn: "Load map",
  map_change_key: "Change key",
  map_error: "Failed to load Google Maps:",
  map_reset_key: "Reset key",
  map_complaints: "Complaints",
  map_approximate: "approximate — run API server for live data",

  // ── Explain panel ────────────────────────────────────────────────────────
  explain_select_placeholder: "Select a query",
  explain_empty: "Select a query above to see the execution plans.",

  // ── Footer ───────────────────────────────────────────────────────────────
  footer_generated: "Generated",
  footer_runs: "measured runs",
  footer_warmup: "warmup",
} as const;

export type TKey = keyof typeof en;
