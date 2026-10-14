import type { TKey } from "./en";

export const es: Record<TKey, string> = {
  // ── Language toggle ──────────────────────────────────────────────────────
  lang_en: "EN",
  lang_es: "ES",

  // ── Header ───────────────────────────────────────────────────────────────
  header_title: "Benchmark OLTP vs OLAP",
  header_rows: "filas",
  header_profile: "perfil",

  // ── Stat tiles ───────────────────────────────────────────────────────────
  stat_queries: "Queries",
  stat_volume: "Volumen de datos",
  stat_volume_unit: "filas",
  stat_min_speedup: "Speedup mínimo",
  stat_max_speedup: "Speedup máximo",
  stat_significance: "Significancia",
  stat_reached: "Alcanzada",
  stat_not_reached: "No alcanzada",

  // ── Live run ─────────────────────────────────────────────────────────────
  live_btn: "Actualizar medición en vivo",
  live_running: "Midiendo 6 queries × 2 motores…",
  live_hint_idle: "Requiere: python dashboard/api_server.py · ~3 min",
  live_hint_running: "Espera — esto puede tardar ~3 min con el perfil full",
  live_error_connect: "No se pudo conectar al servidor. Ejecuta: python dashboard/api_server.py",

  // ── Results table ────────────────────────────────────────────────────────
  table_aria: "Resultados del benchmark por query",
  table_col_query: "Query",
  table_col_question: "Pregunta",
  table_col_oltp: "OLTP (ms)",
  table_col_olap: "OLAP (ms)",
  table_col_speedup: "Speedup",

  // ── Dataset introduction ─────────────────────────────────────────────────
  intro_title: "¿Por qué NYC 311 Service Requests?",
  intro_p1: "NYC 311 es la línea de atención ciudadana no urgente de Nueva York: quejas de ruido, huecos en la calle, falta de calefacción, grafiti. La ciudad publica cada reporte como datos abiertos a través de la API Socrata, con acceso a más de 22.7 millones de registros desde 2010.",
  intro_p2: "Evaluamos 15 datasets públicos y elegimos NYC 311 por cuatro razones:",
  intro_why_volume: "5 millones de filas cargadas en menos de 1 hora — suficiente para diferencias de rendimiento de órdenes de magnitud.",
  intro_why_dims: "6 dimensiones analíticas naturales (tipo de queja, agencia, ubicación, tiempo, canal, estado) — ideales para las 6 queries OLAP.",
  intro_why_api: "Sin throttling con app token: hasta 50,000 filas por página, paginación keyset para reanudación fiable.",
  intro_why_time: "Rango temporal de varios años (cargamos el corte 2024–2026) que habilita análisis por año / trimestre / mes en cada query.",
  intro_why_volume_label: "Volumen",
  intro_why_dims_label: "Dimensiones",
  intro_why_api_label: "API",
  intro_why_time_label: "Rango temporal",
  intro_api_endpoint: "Endpoint y parámetros de la API",
  intro_api_pagination: "Paginación keyset: cada página pasa el último (created_date, unique_key) como cursor — seguro de reanudar si se interrumpe.",
  intro_json_example: "Ejemplo de registro crudo (una fila de la API)",

  // ── API columns table ────────────────────────────────────────────────────
  api_columns_title: "12 columnas que descargamos de la API",
  api_col_name: "Columna API",
  api_col_example: "Ejemplo real",
  api_col_desc: "Qué significa",
  api_unique_key:             "ID único de la queja. Nunca se repite. Es nuestra clave primaria.",
  api_created_date:           "Fecha y hora exacta en que el ciudadano registró la queja.",
  api_closed_date:            "Fecha en que se resolvió. NULL si sigue abierta.",
  api_agency:                 "Código corto de la agencia (NYPD, DOT, HPD…).",
  api_agency_name:            "Nombre completo de la agencia.",
  api_complaint_type:         "Categoría de la queja. ~290 tipos distintos.",
  api_descriptor:             "Subcategoría que detalla el tipo. ~1,700 descriptores.",
  api_borough:                'Distrito de NYC. 5 valores + "Unspecified": Manhattan, Brooklyn, Queens, Bronx, Staten Island.',
  api_incident_zip:           "Código postal donde ocurrió el incidente.",
  api_community_board:        "Junta comunitaria local responsable del área.",
  api_open_data_channel_type: "Cómo se registró: PHONE, ONLINE, MOBILE, OTHER.",
  api_status:                 "Estado actual: Closed, Open, Pending, Started, etc.",

  // ── Schema viewer ────────────────────────────────────────────────────────
  schema_title: "Modelo de datos — diagramas de esquema",
  schema_tab_oltp: "OLTP (PostgreSQL 3NF)",
  schema_tab_olap: "OLAP — Star Schema (DuckDB)",
  schema_tab_staging: "Staging",
  schema_legend_pk: "PK — clave primaria",
  schema_legend_fk: "FK — clave foránea",
  schema_legend_col: "columna regular",
  schema_legend_rel: "relación 1→N",
  schema_olap_note: "Esquema estrella — fact_service_request en el centro · 6 dimensiones radiales a 60°",
  schema_staging_note: "Las tablas de staging no tienen relaciones entre sí — cada una es independiente",

  // ── Section titles ───────────────────────────────────────────────────────
  section_pipeline: "Pipeline",
  section_speedup: "Speedup por query (escala logarítmica)",
  section_results: "Resultados detallados",
  section_absolute: "Tiempos absolutos — mediana en ms (escala lineal)",
  section_radar: "Cobertura de speedup — vista radar",
  section_map: "Geografía de quejas en NYC — por borough",
  section_explain: "Planes de ejecución",
  section_env: "Entorno",

  // ── Pipeline ─────────────────────────────────────────────────────────────
  pipeline_api: "API NYC 311",
  pipeline_api_sub: "Socrata",
  pipeline_staging: "Staging",
  pipeline_staging_sub: "Datos crudos",
  pipeline_oltp: "OLTP",
  pipeline_oltp_sub: "3NF, 8 tablas",
  pipeline_olap: "OLAP",
  pipeline_olap_sub: "Estrella, DuckDB",
  pipeline_bench: "Benchmark",
  pipeline_bench_sub: "6 queries ×2",
  pipeline_results: "Resultados",
  pipeline_results_sub: "JSON + MD",

  // ── Environment card ─────────────────────────────────────────────────────
  env_oltp_title: "OLTP — PostgreSQL",
  env_olap_title: "OLAP — DuckDB",

  // ── Borough map ──────────────────────────────────────────────────────────
  map_fallback_note: "Mostrando datos aproximados. Ejecuta make api para conteos en vivo desde DuckDB.",
  map_key_required: "Se requiere clave de Google Maps API",
  map_key_desc: "Pega tu clave para ver el mapa de quejas de NYC por borough. Se guarda solo en el localStorage de tu navegador.",
  map_key_placeholder: "AIzaSy...",
  map_key_help: "Consigue una clave gratis en {link} — habilita la Maps JavaScript API.",
  map_key_help_link: "Google Cloud Console",
  map_load_btn: "Cargar mapa",
  map_change_key: "Cambiar clave",
  map_error: "Error al cargar Google Maps:",
  map_reset_key: "Resetear clave",
  map_complaints: "Quejas",
  map_approximate: "aproximado — corre el servidor API para datos en vivo",

  // ── Explain panel ────────────────────────────────────────────────────────
  explain_select_placeholder: "Selecciona una query",
  explain_empty: "Selecciona una query arriba para ver los planes de ejecución.",

  // ── Footer ───────────────────────────────────────────────────────────────
  footer_generated: "Generado",
  footer_runs: "corridas medidas",
  footer_warmup: "warmup",
} as const;
