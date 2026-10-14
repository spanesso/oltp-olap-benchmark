# Graph Report - oltp-olap-benchmark  (2026-10-14)

## Corpus Check
- 232 files · ~219,296 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1516 nodes · 2200 edges · 139 communities (117 shown, 16 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `67d618d2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- db.py
- Research: OLTP vs OLAP Benchmark on NYC 311
- common.sh
- Settings
- Tasks: [FEATURE NAME]
- speckit-analyze/SKILL.md
- Tasks: OLTP vs OLAP Benchmark on NYC 311
- What You Must Do When Invoked
- git/scripts/bash/create-new-feature.sh
- Contract: Command-Line Interface
- Core Principles
- Feature Specification: [FEATURE NAME]
- Feature Specification: OLTP vs OLAP Benchmark on NYC 311
- Core Principles
- Project: OLTP vs OLAP Benchmark
- Git Branching Workflow Extension
- graphify reference: extra exports and benchmark
- Create Feature Branch
- Create Feature Branch
- create-new-feature.ps1
- Implementation Plan: [FEATURE]
- speckit-checklist/SKILL.md
- speckit-plan/SKILL.md
- speckit-specify/SKILL.md
- speckit-tasks/SKILL.md
- generate_sample.py
- graphify reference: query, path, explain
- Auto-Commit Changes
- Initialize Git Repository
- Detect Git Remote URL
- Validate Feature Branch
- Auto-Commit Changes
- Initialize Git Repository
- Detect Git Remote URL
- Validate Feature Branch
- speckit-clarify/SKILL.md
- speckit-constitution/SKILL.md
- speckit-taskstoissues/SKILL.md
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- Contract: Benchmark Queries
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- speckit-implement/SKILL.md
- git-common.ps1
- `sample_311.json`
- after_pytest.py
- guard_bash.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- auto-commit.sh
- initialize-repo.sh
- .claude/CLAUDE.md
- extraction-spec.md
- test_cli.py
- nyc311-bench
- ingest.py
- ingest
- experiments.py
- report.py
- queries.py
- Implementation Plan: OLTP vs OLAP Benchmark on NYC 311
- data-model.md
- Benchmark results: quick profile
- Specification Quality Checklist: OLTP vs OLAP Benchmark on NYC 311
- Data Model: OLTP vs OLAP Benchmark on NYC 311
- OLTP vs OLAP Benchmark on NYC 311 Service Requests
- AI Workflow
- Design: OLTP vs OLAP Benchmark
- User Scenarios & Testing *(mandatory)*
- compilerOptions
- controls.py
- SchemaViewer.tsx
- 1. CONCEPTOS FUNDAMENTALES
- test_experiments.py
- cli.py
- test_model_parity.py
- ExperimentsPanel.test.tsx
- index.tsx
- run_transactional
- package.json
- Query
- test_runner_stats.py
- conftest.py
- compilerOptions
- hooks.test.tsx
- vitest
- connect_duckdb
- Handler
- TransformResults.test.ts
- Execution Steps — follow this order exactly
- devDependencies
- 5. ARCHIVOS PYTHON — QUE HACE CADA UNO
- BenchmarkResult.ts
- 7. CONFIGURACION DEL PROYECTO CLAUDE (AI-assisted development)
- Skill: Dashboard Chart
- Execution Steps
- 9. COMO EJECUTAR TODO (paso a paso)
- config.py
- build_olap
- BenchmarkRepository.ts
- runner.py
- ExplainPanel.test.tsx
- BoroughMap.tsx
- GUIA_SUSTENTACION.md
- 2. TECNOLOGÍAS USADAS EN EL PROYECTO
- 3. LA API DE DATOS: NYC 311 Service Requests
- 6.2 Archivos del dashboard — capa por capa
- Parte 2: 100 Preguntas y Respuestas
- test_schemas.py
- 4.4 Las 6 queries analíticas
- scripts
- SpeedupChart.tsx
- 4. ARQUITECTURA DEL PROYECTO (El Pipeline)
- .oxlintrc.json
- TransactionalTable.tsx
- 4.1 Diagrama del flujo de datos
- AbsoluteTimingChart.tsx
- LiveRunButton.tsx
- PipelineDiagram.test.tsx
- QueryTable.tsx
- StatTile.test.tsx
- 2.1 PostgreSQL — El motor OLTP
- 2.2 DuckDB — El motor OLAP
- 2.5 Vite + React + TypeScript — El Dashboard
- dependencies
- React + TypeScript + Vite
- ApiColumnsTable.tsx
- SpeedupRadarChart.tsx
- 2.4 Docker / Docker Compose
- 5.13 Archivos de tests
- Dashboard.tsx
- tsconfig.json

## God Nodes (most connected - your core abstractions)
1. `ingest()` - 25 edges
2. `FixtureSource` - 23 edges
3. `Settings` - 22 edges
4. `connect_duckdb()` - 22 edges
5. `compilerOptions` - 21 edges
6. `run_transactional()` - 18 edges
7. `command_run()` - 16 edges
8. `command_experiments()` - 16 edges
9. `run_sql_file()` - 16 edges
10. `Query` - 16 edges

## Surprising Connections (you probably didn't know these)
- `test_invalid_port_is_rejected()` --uses--> `ConfigError`  [INFERRED]
  tests/unit/test_config.py → src/nyc311_bench/config.py
- `test_missing_token_raises_a_clear_error()` --uses--> `ConfigError`  [INFERRED]
  tests/unit/test_config.py → src/nyc311_bench/config.py
- `test_olap_schema_can_be_applied_again()` --calls--> `run_sql_file()`  [EXTRACTED]
  tests/integration/test_schemas.py → src/nyc311_bench/db.py
- `built_models()` --calls--> `ingest()`  [INFERRED]
  tests/integration/conftest.py → src/nyc311_bench/ingest.py
- `built_models()` --calls--> `build_olap()`  [INFERRED]
  tests/integration/conftest.py → src/nyc311_bench/olap.py

## Import Cycles
- None detected.

## Communities (139 total, 16 thin omitted)

### Community 0 - "db.py"
Cohesion: 0.15
Nodes (15): Connection, connect_postgres(), Any, Path, Connections to both engines and access to the SQL files under `sql/`., Return the text of a SQL file, addressed relative to the `sql/` directory., Execute every statement of a SQL file on a PostgreSQL or DuckDB connection., read_sql() (+7 more)

### Community 1 - "Research: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.13
Nodes (15): Open items, R10. First measurements on the quick profile (2026-10-12), R11. Quick profile from an empty database (task T044, 2026-10-12), R12. Official measurement on the full profile (tasks T045–T048, 2026-10-12), R1. Source dataset, R2. Data cut and volume profiles, R3. API access and pagination, R4. OLAP engine (+7 more)

### Community 2 - "common.sh"
Cohesion: 0.14
Nodes (27): check-prerequisites.sh script, check_dir(), check_feature_branch(), check_file(), feature_json_matches_feature_dir(), find_feature_dir_by_prefix(), find_specify_root(), get_current_branch() (+19 more)

### Community 3 - "Settings"
Cohesion: 0.20
Nodes (14): load_dotenv(), Path, Read KEY=VALUE lines from a .env file without overriding existing variables., Settings, settings(), test_conninfo_targets_the_requested_database(), test_defaults_match_docker_compose(), test_empty_token_counts_as_missing() (+6 more)

### Community 4 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 5 - "speckit-analyze/SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 6 - "Tasks: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation Strategy, Incremental Delivery, MVP First (User Story 1), Needs from the human (+18 more)

### Community 7 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 8 - "git/scripts/bash/create-new-feature.sh"
Cohesion: 0.24
Nodes (14): _byte_length(), check_existing_branches(), clean_branch_name(), _extract_highest_number(), _find_project_root(), generate_branch_name(), get_highest_from_branches(), get_highest_from_remote_refs() (+6 more)

### Community 9 - "Contract: Command-Line Interface"
Cohesion: 0.14
Nodes (12): Commands, Configuration (environment variables), Contract: Command-Line Interface, Makefile targets, Output and exit codes, Retry policy for `load` (FR-006), Checks for specific requirements, Full profile: reproduce the official numbers (SC-002, SC-003) (+4 more)

### Community 10 - "Core Principles"
Cohesion: 0.15
Nodes (12): Core Principles, Governance, I. Spec-Driven Development (NON-NEGOTIABLE), II. Benchmark Integrity (NON-NEGOTIABLE), III. Fair Comparison, IV. Verifiable Quality, OLTP vs OLAP Benchmark Constitution, Technical Constraints and Deliverables (+4 more)

### Community 11 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 12 - "Feature Specification: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.29
Nodes (7): Assumptions, Feature Specification: OLTP vs OLAP Benchmark on NYC 311, Functional Requirements, Key Entities, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)*

### Community 13 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 14 - "Project: OLTP vs OLAP Benchmark"
Cohesion: 0.20
Nodes (9): Agent modes, Current status, Deliverables (at the repo root), graphify, Harness, Log for AI_WORKFLOW.md, Operating rules, Project: OLTP vs OLAP Benchmark (+1 more)

### Community 15 - "Git Branching Workflow Extension"
Cohesion: 0.20
Nodes (9): Commands, Configuration, Disabling, Git Branching Workflow Extension, Graceful Degradation, Hooks, Installation, Overview (+1 more)

### Community 16 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 17 - "Create Feature Branch"
Cohesion: 0.22
Nodes (8): Branch Numbering Mode, Create Feature Branch, Environment Variable Override, Execution, Graceful Degradation, Output, Prerequisites, User Input

### Community 18 - "Create Feature Branch"
Cohesion: 0.22
Nodes (8): Branch Numbering Mode, Create Feature Branch, Environment Variable Override, Execution, Graceful Degradation, Output, Prerequisites, User Input

### Community 19 - "create-new-feature.ps1"
Cohesion: 0.39
Nodes (7): ConvertTo-CleanBranchName(), Get-BranchName(), Get-HighestNumberFromBranches(), Get-HighestNumberFromNames(), Get-HighestNumberFromRemoteRefs(), Get-HighestNumberFromSpecs(), Get-NextBranchNumber()

### Community 20 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 21 - "speckit-checklist/SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 22 - "speckit-plan/SKILL.md"
Cohesion: 0.25
Nodes (7): Key rules, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases, Pre-Execution Checks, User Input

### Community 23 - "speckit-specify/SKILL.md"
Cohesion: 0.25
Nodes (7): For AI Generation, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements, Success Criteria Guidelines, User Input

### Community 24 - "speckit-tasks/SKILL.md"
Cohesion: 0.25
Nodes (7): Checklist Format (REQUIRED), Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules, Task Organization, User Input

### Community 25 - "generate_sample.py"
Cohesion: 0.48
Nodes (6): Random, build_row(), main(), datetime, Generate the synthetic test fixture `sample_311.json`. The rows imitate the…, timestamp()

### Community 26 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 27 - "Auto-Commit Changes"
Cohesion: 0.33
Nodes (5): Auto-Commit Changes, Behavior, Configuration, Execution, Graceful Degradation

### Community 28 - "Initialize Git Repository"
Cohesion: 0.33
Nodes (5): Customization, Execution, Graceful Degradation, Initialize Git Repository, Output

### Community 29 - "Detect Git Remote URL"
Cohesion: 0.33
Nodes (5): Detect Git Remote URL, Execution, Graceful Degradation, Output, Prerequisites

### Community 30 - "Validate Feature Branch"
Cohesion: 0.33
Nodes (5): Execution, Graceful Degradation, Prerequisites, Validate Feature Branch, Validation Rules

### Community 31 - "Auto-Commit Changes"
Cohesion: 0.33
Nodes (5): Auto-Commit Changes, Behavior, Configuration, Execution, Graceful Degradation

### Community 32 - "Initialize Git Repository"
Cohesion: 0.33
Nodes (5): Customization, Execution, Graceful Degradation, Initialize Git Repository, Output

### Community 33 - "Detect Git Remote URL"
Cohesion: 0.33
Nodes (5): Detect Git Remote URL, Execution, Graceful Degradation, Output, Prerequisites

### Community 34 - "Validate Feature Branch"
Cohesion: 0.33
Nodes (5): Execution, Graceful Degradation, Prerequisites, Validate Feature Branch, Validation Rules

### Community 35 - "speckit-clarify/SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 36 - "speckit-constitution/SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 37 - "speckit-taskstoissues/SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 38 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 39 - "Contract: Benchmark Queries"
Cohesion: 0.40
Nodes (4): Analytical queries (measured, count towards SC-003), Contract: Benchmark Queries, Equivalence rules (used by the integration tests), Transactional operations (optional, User Story 4 / FR-020)

### Community 40 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 41 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 42 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 43 - "speckit-implement/SKILL.md"
Cohesion: 0.50
Nodes (3): Outline, Pre-Execution Checks, User Input

### Community 45 - "`sample_311.json`"
Cohesion: 0.50
Nodes (3): Edge cases included, `sample_311.json`, Test fixtures

### Community 56 - "test_cli.py"
Cohesion: 0.14
Nodes (3): parametrize, test_invalid_arguments_exit_with_code_2(), test_too_few_measurement_runs_exit_with_code_2()

### Community 61 - "ingest.py"
Cohesion: 0.06
Nodes (56): format_summary(), IngestSummary, _last_cursor(), parse_row(), Any, datetime, Load API pages into the staging area, idempotently and resumably. Each page is…, Keyset position after a page: its last row that carries both key fields. (+48 more)

### Community 62 - "ingest"
Cohesion: 0.23
Nodes (18): FetchPage, ingest(), Reporter, Stage rows of the cut until `target_rows` are present, resuming from the…, FixtureSource, Stand-in for the API in integration tests: serves the fixture with keyset…, Serves rows in file order. A cursor resumes after the row it points to., Staging load: idempotent, resumable, and explicit about rejected rows. (+10 more)

### Community 63 - "experiments.py"
Cohesion: 0.13
Nodes (27): build_report(), check_equivalent(), _connections(), effects(), EquivalenceError, _ms(), Any, Exception (+19 more)

### Community 64 - "report.py"
Cohesion: 0.16
Nodes (26): build_report(), Any, datetime, Path, Turn measurements into the two result files and the significance verdict., SC-003, evaluated only on the official (full) profile., render_markdown(), significance() (+18 more)

### Community 65 - "queries.py"
Cohesion: 0.10
Nodes (26): analytical_queries(), Registry of benchmark queries: each one is a business question with a SQL file…, assert_equivalent(), Any, Compare the result of one query on both models, row by row…, Exact match for text and integers; relative tolerance for floating point., Fail with the query, the first differing row and the column that differs., run_on_both() (+18 more)

### Community 66 - "Implementation Plan: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.20
Nodes (10): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Approach, Implementation Plan: OLTP vs OLAP Benchmark on NYC 311, Project Structure, Risks, Source Code (repository root) (+2 more)

### Community 67 - "data-model.md"
Cohesion: 0.32
Nodes (3): `benchmark_<profile>.json`, `benchmark_<profile>.md`, Contract: Results Files

### Community 68 - "Benchmark results: quick profile"
Cohesion: 0.33
Nodes (5): Analytical queries, Benchmark results: quick profile, Environment, Method, Verdict

### Community 69 - "Specification Quality Checklist: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.33
Nodes (5): Content Quality, Feature Readiness, Notes, Requirement Completeness, Specification Quality Checklist: OLTP vs OLAP Benchmark on NYC 311

### Community 70 - "Data Model: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.33
Nodes (6): 1. Staging (PostgreSQL, schema `staging`), 2. OLTP model (PostgreSQL, schema `oltp`, third normal form), 3. OLAP model (DuckDB file, star schema), 4. Parity invariants (checked by integration tests, FR-021), 5. Benchmark results (files in `results/`), Data Model: OLTP vs OLAP Benchmark on NYC 311

### Community 71 - "OLTP vs OLAP Benchmark on NYC 311 Service Requests"
Cohesion: 0.05
Nodes (34): Dashboard, Data attribution, Full profile (reproduce the official numbers), How it works, Is it the schema or the engine?, Limitations, Live re-measurement, OLTP vs OLAP Benchmark on NYC 311 Service Requests (+26 more)

### Community 72 - "AI Workflow"
Cohesion: 0.13
Nodes (14): Agent modes, AI Workflow, Corrections to AI-generated work, Dashboard, Development method, Extras: control models, transactional operations, CI, Harness and guardrails, Harness and hooks (+6 more)

### Community 73 - "Design: OLTP vs OLAP Benchmark"
Cohesion: 0.17
Nodes (11): Alternatives considered, Analytical queries, Dashboard, Data models, Design: OLTP vs OLAP Benchmark, Limitations, Measurement method, OLAP — DuckDB, star schema (+3 more)

### Community 74 - "User Scenarios & Testing *(mandatory)*"
Cohesion: 0.29
Nodes (7): Edge Cases, User Scenarios & Testing *(mandatory)*, User Story 1 - Load the same data into both models (Priority: P1), User Story 2 - Measure the analytical queries on both models (Priority: P1), User Story 3 - Verify that both models give the same answers (Priority: P2), User Story 4 - Show the contrast on transactional operations (Priority: P3), User Story 5 - Separate the effect of the schema from the effect of the engine (Priority: P3)

### Community 75 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, baseUrl, erasableSyntaxOnly, ignoreDeprecations, jsx, lib (+17 more)

### Community 76 - "controls.py"
Cohesion: 0.12
Nodes (19): build_3nf_in_duckdb(), build_star_in_postgres(), _copy_normalized_tables(), _copy_normalized_tables_with_csv(), Path, _quote(), Control models that separate the effect of the schema from the effect of the…, Rebuild the `star_pg` schema from the OLTP tables. Returns the row count per… (+11 more)

### Community 77 - "SchemaViewer.tsx"
Cohesion: 0.13
Nodes (21): ACCENT, Col, edgeX(), edgeY(), FK_COLOR, makePath(), midX(), midY() (+13 more)

### Community 78 - "1. CONCEPTOS FUNDAMENTALES"
Cohesion: 0.09
Nodes (23): 1.1 ¿Qué es una base de datos relacional? (Repaso rápido), 1.2 ¿Qué es OLTP? (Online Transaction Processing), 1.3 ¿Qué es OLAP? (Online Analytical Processing), 1.4 Diferencia clave entre OLTP y OLAP, 1.5 ¿Qué es la normalización? (1NF, 2NF, 3NF), 1.6 ¿Qué es un modelo estrella (Star Schema)?, 1.7 Tabla de hechos vs. tablas de dimensiones, 1. CONCEPTOS FUNDAMENTALES (+15 more)

### Community 79 - "test_experiments.py"
Cohesion: 0.11
Nodes (9): FakeConnection, parametrize, Answers any statement with canned rows; EXPLAIN gets a two-column plan row., test_a_grid_needs_at_least_two_repeats(), test_every_cell_has_a_sql_file_for_every_query(), test_markdown_lists_every_model_and_the_effects(), test_models_that_disagree_are_never_measured(), test_the_grid_measures_every_cell_on_every_repeat() (+1 more)

### Community 80 - "cli.py"
Cohesion: 0.19
Nodes (20): ArgumentParser, OLTP vs OLAP benchmark on NYC 311 Service Requests. Usage: python benchmark.py…, Namespace, _at_least(), build_parser(), command_all(), command_build(), command_experiments() (+12 more)

### Community 81 - "test_model_parity.py"
Cohesion: 0.11
Nodes (12): build_oltp(), Build the normalized OLTP model from the staging area., Rebuild the `oltp` schema from the first `target_rows` staged rows. The whole…, table_counts(), models(), fixture, parametrize, Both models hold the same requests (data-model.md section 4, FR-011, FR-012,… (+4 more)

### Community 82 - "ExperimentsPanel.test.tsx"
Cohesion: 0.13
Nodes (12): CellSpread, ExperimentCell, ExperimentEffects, ExperimentQuery, ExperimentsReport, RatioSummary, Repeatability, ExperimentsPanel() (+4 more)

### Community 83 - "index.tsx"
Cohesion: 0.20
Nodes (12): I18nContext, I18nCtx, I18nProvider(), t(), Lang, translations, useI18n(), en (+4 more)

### Community 84 - "run_transactional"
Cohesion: 0.13
Nodes (18): fill(), _insert_values(), pick_identifiers(), Replace `@name@` tokens with integers. Only integers are accepted, so nothing a…, `count` existing request identifiers, evenly spread over the key order. The…, A new identifier and the keys of an existing request, for the T2 insert., Measure the transactional operations (User Story 4). T1 walks a fixed, evenly…, run_transactional() (+10 more)

### Community 85 - "package.json"
Cohesion: 0.12
Nodes (15): name, private, type, version, projectRoot, jsdom, oxlint, react-dom (+7 more)

### Community 86 - "Query"
Cohesion: 0.16
Nodes (15): Cell, explain_plan(), One combination of schema and engine, with the directory holding its query…, Query, explain_duckdb(), explain_postgres(), explain_query(), explain_sql() (+7 more)

### Community 87 - "test_runner_stats.py"
Cohesion: 0.16
Nodes (15): percentile(), Percentile with linear interpolation between the two nearest ranks., summarize(), validate_runs(), FakeClock, parametrize, Each measured run reads the clock twice; durations are given in milliseconds., test_median_resists_an_outlier() (+7 more)

### Community 88 - "conftest.py"
Cohesion: 0.15
Nodes (16): built_models(), loaded_models(), olap(), olap_path(), pg(), postgres_test_database(), fixture, Path (+8 more)

### Community 89 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 90 - "hooks.test.tsx"
Cohesion: 0.19
Nodes (9): App(), BenchmarkState, useBenchmarkData(), BoroughStatsState, useBoroughStats(), useExperiments(), mocked, results (+1 more)

### Community 91 - "vitest"
Cohesion: 0.30
Nodes (8): SchemaViewer(), data, operation(), timing(), renderWithI18n(), @testing-library/react, @testing-library/user-event, vitest

### Community 92 - "connect_duckdb"
Cohesion: 0.21
Nodes (12): DuckDBPyConnection, connect_duckdb(), check_parity(), ParityError, Exception, Return the number of requests both models hold, or raise ParityError (FR-018)., The two models do not hold the same data, so measuring them would be…, Measuring on real engines: results are produced, and unequal models are refused. (+4 more)

### Community 93 - "Handler"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, Handler, _public_path(), Path, Minimal live-benchmark API server. Standard library only — no extra deps. Run…, _results_path()

### Community 94 - "TransformResults.test.ts"
Cohesion: 0.24
Nodes (12): BenchmarkResult, ANALYTICAL, analyticalQueries(), ChartDatum, formatMs(), getChartData(), getStatsSummary(), StatsSummary (+4 more)

### Community 95 - "Execution Steps — follow this order exactly"
Cohesion: 0.15
Nodes (12): Checklist (verify before marking done), Execution Steps — follow this order exactly, Input, Skill: Dashboard Module, Step 1: Define the entity (domain layer), Step 2: Write the use case (domain layer), Step 3: Write the repository (infrastructure layer), Step 4: Create the React component (presentation layer) (+4 more)

### Community 96 - "devDependencies"
Cohesion: 0.15
Nodes (13): devDependencies, jsdom, oxlint, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event, @types/node, @types/react (+5 more)

### Community 97 - "5. ARCHIVOS PYTHON — QUE HACE CADA UNO"
Cohesion: 0.15
Nodes (13): 5.10 `src/nyc311_bench/runner.py` — Motor del benchmark, 5.11 `src/nyc311_bench/report.py` — Generacion de reportes, 5.12 `src/nyc311_bench/cli.py` — Interfaz de linea de comandos, 5.1 `benchmark.py` (raiz del proyecto), 5.2 `src/nyc311_bench/__init__.py`, 5.3 `src/nyc311_bench/config.py` — Configuracion y perfiles, 5.4 `src/nyc311_bench/db.py` — Conexiones a las bases de datos, 5.5 `src/nyc311_bench/socrata.py` — Cliente de la API (+5 more)

### Community 98 - "BenchmarkResult.ts"
Cohesion: 0.21
Nodes (8): Dataset, Environment, Method, Significance, Timing, EnvironmentCard(), Props, environment

### Community 99 - "7. CONFIGURACION DEL PROYECTO CLAUDE (AI-assisted development)"
Cohesion: 0.17
Nodes (12): 7.1 Que es Claude Code, 7.2 El archivo CLAUDE.md, 7.3 Los hooks (`.claude/hooks/`), 7.4 Los skills (`.claude/skills/`), 7.5 `settings.json` — Permisos, 7.6 El flujo SDD (Spec-Driven Development), 7.7 Los 3 modos del agente, 7.8 Graphify — Knowledge graph (+4 more)

### Community 100 - "Skill: Dashboard Chart"
Cohesion: 0.18
Nodes (10): Accessibility, Chart type selection, Checklist (verify before marking done), Color system, Recharts component pattern, Responsive design, Skill: Dashboard Chart, Stat tiles (KPI cards) (+2 more)

### Community 101 - "Execution Steps"
Cohesion: 0.18
Nodes (10): 1. Create the directory structure (Clean Architecture), 2. Dependencies, 3. Configuration files, 4. Clean Architecture rules (enforce in code review), 5. Smoke test, Execution Steps, Input, Output (+2 more)

### Community 102 - "9. COMO EJECUTAR TODO (paso a paso)"
Cohesion: 0.18
Nodes (11): 9.10 Correr los tests, 9.1 Requisitos previos, 9.2 Clonar y configurar, 9.3 Levantar PostgreSQL, 9.4 Configurar el token de la API, 9.5 Correr la ingesta de datos, 9.6 Ver la base de datos PostgreSQL, 9.7 Ver la base de datos DuckDB (+3 more)

### Community 103 - "config.py"
Cohesion: 0.24
Nodes (9): ConfigError, get_profile(), Profile, Exception, Settings, volume profiles and the fixed data cut., Invalid or missing configuration., test_profiles_differ_only_in_volume_and_official_flag(), test_profiles_match_the_spec() (+1 more)

### Community 104 - "build_olap"
Cohesion: 0.29
Nodes (10): build_olap(), _copy_with_csv(), _copy_with_extension(), Path, _quote(), Build the star schema in DuckDB from the OLTP model. The OLTP tables are first…, Rebuild the star schema file. Returns the row counts and the copy method used., table_counts() (+2 more)

### Community 105 - "BenchmarkRepository.ts"
Cohesion: 0.31
Nodes (6): BoroughStat, FALLBACK_BOROUGH_STATS, fetchBenchmarkResults(), fetchBoroughStats(), fetchExperiments(), runLiveBenchmark()

### Community 106 - "runner.py"
Cohesion: 0.31
Nodes (9): _in_rolled_back_transaction(), _measure_insert(), _measure_lookup(), Measure every benchmark query on both models. Timing is client-side wall-clock…, Run `run` warm-up times unmeasured, then `repetitions` times measured., T1: each model walks the same identifier list, one identifier per run., T2: begin, insert one request, roll back; the whole round trip is timed., time_query() (+1 more)

### Community 107 - "ExplainPanel.test.tsx"
Cohesion: 0.28
Nodes (5): QueryResult, ExplainPanel(), Props, withoutPlans, withPlans

### Community 108 - "BoroughMap.tsx"
Cohesion: 0.28
Nodes (6): BOROUGH_COLORS, BoroughMap(), CENTROIDS, loadGoogleMaps(), NYC_CENTER, Window

### Community 109 - "GUIA_SUSTENTACION.md"
Cohesion: 0.22
Nodes (8): ¿Cómo fluyen los datos?, Guía Completa de Preparación — OLTP vs OLAP Benchmark, Guía de Preparación para Sustentar el Proyecto OLTP vs OLAP Benchmark, PARTE 1: Conceptos, Tecnologías, API y Arquitectura, Parte 1: Explicación General del Proyecto, ¿Qué es este proyecto?, ¿Qué es la API Socrata?, ¿Qué es NYC 311?

### Community 110 - "2. TECNOLOGÍAS USADAS EN EL PROYECTO"
Cohesion: 0.22
Nodes (9): 2.3 Python 3.13, 2.6 Recharts, 2.7 Herramientas de testing y calidad, 2. TECNOLOGÍAS USADAS EN EL PROYECTO, Bibliotecas que usamos, ¿Por qué Python?, pytest (Python), ruff (Python) (+1 more)

### Community 111 - "3. LA API DE DATOS: NYC 311 Service Requests"
Cohesion: 0.22
Nodes (9): 3.1 ¿Qué es NYC 311?, 3.2 ¿Qué es Socrata?, 3.3 El dataset erm2-nwe9, 3.4 ¿Cómo se pagina?, 3.5 ¿Por qué elegimos esta API?, 3. LA API DE DATOS: NYC 311 Service Requests, ¿Cuántos registros tiene?, ¿Qué columnas tiene? (+1 more)

### Community 112 - "6.2 Archivos del dashboard — capa por capa"
Cohesion: 0.22
Nodes (9): 6.1 Que es Clean Architecture y por que la usamos, 6.2 Archivos del dashboard — capa por capa, 6.3 Como correr el dashboard, 6.4 Tests del dashboard, 6. EL DASHBOARD (UI), Archivos raiz, DOMINIO (`src/domain/`), INFRASTRUCTURE (`src/infrastructure/`) (+1 more)

### Community 113 - "Parte 2: 100 Preguntas y Respuestas"
Cohesion: 0.22
Nodes (9): AI Y METODOLOGÍA (86–95), CONCEPTOS (1–15), CÓDIGO Y ARQUITECTURA (61–75), DECISIONES TÉCNICAS (16–30), EL BENCHMARK (31–50), INFRAESTRUCTURA (76–85), LAS QUERIES (51–60), Parte 2: 100 Preguntas y Respuestas (+1 more)

### Community 114 - "test_schemas.py"
Cohesion: 0.28
Nodes (5): The three schemas apply cleanly on the real engines and match data-model.md., tables_in(), test_olap_schema_can_be_applied_again(), test_oltp_schema_has_the_expected_tables(), test_staging_schema_has_the_expected_tables()

### Community 115 - "4.4 Las 6 queries analíticas"
Cohesion: 0.25
Nodes (8): 4.4 Las 6 queries analíticas, Q1: Volumen por tipo de queja, mes y borough, Q2: Top 10 tipos de queja por ZIP code con tiempo promedio de resolución, Q3: Tasa de cierre dentro de 30 días por agencia y canal, Q4: Percentil 90 del tiempo de resolución por agencia y trimestre, Q5: Quejas de ruido en Brooklyn por día de la semana y hora, Q6: Participación de cada canal por trimestre, Resumen de resultados

### Community 116 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test, test:watch

### Community 117 - "SpeedupChart.tsx"
Cohesion: 0.33
Nodes (4): ChartRow, Props, SpeedupChart(), recharts

### Community 118 - "4. ARQUITECTURA DEL PROYECTO (El Pipeline)"
Cohesion: 0.29
Nodes (7): 4.2 El modelo OLTP: las 8 tablas normalizadas, 4.3 El modelo OLAP: star schema en DuckDB, 4. ARQUITECTURA DEL PROYECTO (El Pipeline), 8. ESTRUCTURA DE CARPETAS COMPLETA, Diferencias con OLTP:, ¿Por qué están separadas?, Índices

### Community 119 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 120 - "TransactionalTable.tsx"
Cohesion: 0.53
Nodes (4): ms(), Props, TransactionalTable(), winner()

### Community 121 - "4.1 Diagrama del flujo de datos"
Cohesion: 0.33
Nodes (6): 4.1 Diagrama del flujo de datos, Paso 1: NYC 311 API → Staging, Paso 2: Staging → OLTP Model, Paso 3: OLTP Model → OLAP Model, Paso 4: Benchmark, Paso 5: Results

### Community 122 - "AbsoluteTimingChart.tsx"
Cohesion: 0.50
Nodes (3): AbsoluteTimingChart(), Props, Row

### Community 123 - "LiveRunButton.tsx"
Cohesion: 0.60
Nodes (3): fmtElapsed(), LiveRunButton(), Props

### Community 125 - "QueryTable.tsx"
Cohesion: 0.50
Nodes (3): Props, QueryRow, QueryTable()

### Community 127 - "2.1 PostgreSQL — El motor OLTP"
Cohesion: 0.40
Nodes (5): 2.1 PostgreSQL — El motor OLTP, Configuración por defecto (importante para la sustentación), ¿Cómo la usamos?, ¿Por qué la elegimos para OLTP?, ¿Qué es?

### Community 128 - "2.2 DuckDB — El motor OLAP"
Cohesion: 0.40
Nodes (5): 2.2 DuckDB — El motor OLAP, ¿Cómo la usamos?, ¿Por qué elegimos DuckDB sobre otras opciones?, ¿Qué es?, ¿Qué la hace rápida?

### Community 129 - "2.5 Vite + React + TypeScript — El Dashboard"
Cohesion: 0.40
Nodes (5): 2.5 Vite + React + TypeScript — El Dashboard, ¿Por qué estos tres?, React, TypeScript, Vite

### Community 130 - "dependencies"
Cohesion: 0.50
Nodes (4): dependencies, react, react-dom, recharts

### Community 131 - "React + TypeScript + Vite"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + TypeScript + Vite

### Community 134 - "2.4 Docker / Docker Compose"
Cohesion: 0.50
Nodes (4): 2.4 Docker / Docker Compose, ¿Por qué lo usamos?, ¿Qué es Docker?, ¿Qué hace nuestro `docker-compose.yml`?

### Community 135 - "5.13 Archivos de tests"
Cohesion: 0.50
Nodes (4): 5.13 Archivos de tests, Fixtures (`tests/fixtures/`), Tests de integracion (`tests/integration/`), Tests unitarios (`tests/unit/`)

## Knowledge Gaps
- **633 isolated node(s):** `git-common.sh script`, `common.sh script`, `$schema`, `plugins`, `react/rules-of-hooks` (+628 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 862 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `4. ARQUITECTURA DEL PROYECTO (El Pipeline)` connect `4. ARQUITECTURA DEL PROYECTO (El Pipeline)` to `5. ARCHIVOS PYTHON — QUE HACE CADA UNO`, `7. CONFIGURACION DEL PROYECTO CLAUDE (AI-assisted development)`, `9. COMO EJECUTAR TODO (paso a paso)`, `GUIA_SUSTENTACION.md`, `6.2 Archivos del dashboard — capa por capa`, `4.4 Las 6 queries analíticas`, `4.1 Diagrama del flujo de datos`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `vitest` connect `vitest` to `BenchmarkResult.ts`, `StatTile.test.tsx`, `BenchmarkRepository.ts`, `ExplainPanel.test.tsx`, `ExperimentsPanel.test.tsx`, `index.tsx`, `package.json`, `hooks.test.tsx`, `PipelineDiagram.test.tsx`, `TransformResults.test.ts`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `FixtureSource` (e.g. with `built_models()` and `Cursor`) actually correct?**
  _`FixtureSource` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `command_all()` and `command_build()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `git-common.sh script`, `common.sh script`, `$schema` to the rest of the system?**
  _633 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._
- **Should `Research: OLTP vs OLAP Benchmark on NYC 311` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._