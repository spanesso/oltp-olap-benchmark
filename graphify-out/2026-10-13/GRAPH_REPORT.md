# Graph Report - oltp-olap-benchmark  (2026-10-12)

## Corpus Check
- 122 files · ~135,703 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 814 nodes · 1202 edges · 71 communities (56 shown, 10 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 81 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7bb16925`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_run.py
- Research: OLTP vs OLAP Benchmark on NYC 311
- common.sh
- cli.py
- Tasks: [FEATURE NAME]
- speckit-analyze/SKILL.md
- Tasks: OLTP vs OLAP Benchmark on NYC 311
- What You Must Do When Invoked
- git/scripts/bash/create-new-feature.sh
- Contract: Command-Line Interface
- Core Principles
- Feature Specification: [FEATURE NAME]
- User Scenarios & Testing *(mandatory)*
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
- test_socrata.py
- ingest
- ingest.py
- runner.py
- conftest.py
- Implementation Plan: OLTP vs OLAP Benchmark on NYC 311
- data-model.md
- Benchmark results: quick profile
- Specification Quality Checklist: OLTP vs OLAP Benchmark on NYC 311
- Data Model: OLTP vs OLAP Benchmark on NYC 311

## God Nodes (most connected - your core abstractions)
1. `ingest()` - 24 edges
2. `Settings` - 21 edges
3. `FixtureSource` - 21 edges
4. `command_run()` - 15 edges
5. `Tasks: OLTP vs OLAP Benchmark on NYC 311` - 15 edges
6. `run_sql_file()` - 14 edges
7. `build_olap()` - 14 edges
8. `Cursor` - 14 edges
9. `FakeTransport` - 14 edges
10. `command_load()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_page_size_must_be_positive()` --uses--> `SocrataClient`  [INFERRED]
  tests/unit/test_socrata.py → src/nyc311_bench/socrata.py
- `test_client_errors_are_not_retried()` --uses--> `SocrataError`  [INFERRED]
  tests/unit/test_socrata.py → src/nyc311_bench/socrata.py
- `test_the_token_never_appears_in_error_messages()` --uses--> `SocrataError`  [INFERRED]
  tests/unit/test_socrata.py → src/nyc311_bench/socrata.py
- `test_client_errors_are_not_retried()` --uses--> `SocrataUnavailable`  [INFERRED]
  tests/unit/test_socrata.py → src/nyc311_bench/socrata.py
- `test_gives_up_after_the_configured_retries()` --uses--> `SocrataUnavailable`  [INFERRED]
  tests/unit/test_socrata.py → src/nyc311_bench/socrata.py

## Import Cycles
- None detected.

## Communities (71 total, 10 thin omitted)

### Community 0 - "test_run.py"
Cohesion: 0.05
Nodes (46): Connection, DuckDBPyConnection, connect_duckdb(), connect_postgres(), Any, Path, Connections to both engines and access to the SQL files under `sql/`., Return the text of a SQL file, addressed relative to the `sql/` directory. (+38 more)

### Community 1 - "Research: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.15
Nodes (13): Open items, R10. First measurements on the quick profile (2026-10-12), R1. Source dataset, R2. Data cut and volume profiles, R3. API access and pagination, R4. OLAP engine, R5. Python dependencies, R6. Measurement method (+5 more)

### Community 2 - "common.sh"
Cohesion: 0.14
Nodes (27): check-prerequisites.sh script, check_dir(), check_feature_branch(), check_file(), feature_json_matches_feature_dir(), find_feature_dir_by_prefix(), find_specify_root(), get_current_branch() (+19 more)

### Community 3 - "cli.py"
Cohesion: 0.10
Nodes (36): ArgumentParser, OLTP vs OLAP benchmark on NYC 311 Service Requests. Usage: python benchmark.py…, Namespace, build_parser(), command_all(), command_build(), command_load(), command_run() (+28 more)

### Community 4 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 5 - "speckit-analyze/SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 6 - "Tasks: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.08
Nodes (25): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation Strategy, Incremental Delivery, MVP First (User Story 1), Needs from the human (+17 more)

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

### Community 12 - "User Scenarios & Testing *(mandatory)*"
Cohesion: 0.15
Nodes (13): Assumptions, Edge Cases, Feature Specification: OLTP vs OLAP Benchmark on NYC 311, Functional Requirements, Key Entities, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+5 more)

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
Cohesion: 0.15
Nodes (4): OLTP vs OLAP benchmark on NYC 311 Service Requests., parametrize, test_invalid_arguments_exit_with_code_2(), test_too_few_measurement_runs_exit_with_code_2()

### Community 61 - "test_socrata.py"
Cohesion: 0.19
Nodes (21): Exception, A failed HTTP exchange. `status` is None when no response was received., TransportError, urllib_transport(), FakeTransport, make_client(), parametrize, query_of() (+13 more)

### Community 62 - "ingest"
Cohesion: 0.06
Nodes (43): FetchPage, ingest(), _last_cursor(), Reporter, Keyset position after a page: its last row that carries both key fields., Stage rows of the cut until `target_rows` are present, resuming from the…, _read_checkpoint(), build_oltp() (+35 more)

### Community 63 - "ingest.py"
Cohesion: 0.15
Nodes (22): format_summary(), IngestSummary, parse_row(), Any, datetime, Load API pages into the staging area, idempotently and resumably. Each page is…, Insert one page and advance the checkpoint atomically. Returns the rows added., Turn one API row into a staging tuple, or say why it cannot be loaded. The API… (+14 more)

### Community 64 - "runner.py"
Cohesion: 0.07
Nodes (55): Query, build_report(), Any, datetime, Path, Turn measurements into the two result files and the significance verdict., SC-003, evaluated only on the official (full) profile., render_markdown() (+47 more)

### Community 65 - "conftest.py"
Cohesion: 0.19
Nodes (12): olap(), olap_path(), pg(), postgres_test_database(), fixture, Path, Integration test harness: real PostgreSQL and DuckDB, isolated from loaded…, Create an empty `bench_test` database and return its connection string. (+4 more)

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

## Knowledge Gaps
- **301 isolated node(s):** `git-common.sh script`, `common.sh script`, `nyc311-bench`, `graphify`, `Usage` (+296 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 451 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ingest()` connect `ingest` to `cli.py`, `ingest.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `FixtureSource` connect `ingest` to `test_run.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `Settings` connect `cli.py` to `test_run.py`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Settings` (e.g. with `command_all()` and `command_build()`) actually correct?**
  _`Settings` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `FixtureSource` (e.g. with `Cursor` and `SocrataUnavailable`) actually correct?**
  _`FixtureSource` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `command_run()` (e.g. with `cli.py` and `command_all()`) actually correct?**
  _`command_run()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `git-common.sh script`, `common.sh script`, `nyc311-bench` to the rest of the system?**
  _301 weakly-connected nodes found - possible documentation gaps or missing edges._