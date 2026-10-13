# Graph Report - oltp-olap-benchmark  (2026-10-12)

## Corpus Check
- 101 files · ~130,218 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 714 nodes · 965 edges · 64 communities (49 shown, 10 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `11414e4a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_sql_file
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

## God Nodes (most connected - your core abstractions)
1. `ingest()` - 23 edges
2. `Settings` - 19 edges
3. `FixtureSource` - 19 edges
4. `Tasks: OLTP vs OLAP Benchmark on NYC 311` - 15 edges
5. `run_sql_file()` - 14 edges
6. `Cursor` - 14 edges
7. `FakeTransport` - 14 edges
8. `parse_row()` - 13 edges
9. `build_olap()` - 13 edges
10. `Tasks: [FEATURE NAME]` - 13 edges

## Surprising Connections (you probably didn't know these)
- `FixtureSource` --uses--> `SocrataUnavailable`  [INFERRED]
  tests/integration/sources.py → src/nyc311_bench/socrata.py
- `test_an_interrupted_load_resumes_from_the_checkpoint()` --uses--> `SocrataUnavailable`  [INFERRED]
  tests/integration/test_ingest.py → src/nyc311_bench/socrata.py
- `FixtureSource` --uses--> `Cursor`  [INFERRED]
  tests/integration/sources.py → src/nyc311_bench/socrata.py
- `test_page_size_must_be_positive()` --uses--> `SocrataClient`  [INFERRED]
  tests/unit/test_socrata.py → src/nyc311_bench/socrata.py
- `test_invalid_port_is_rejected()` --uses--> `ConfigError`  [INFERRED]
  tests/unit/test_config.py → src/nyc311_bench/config.py

## Import Cycles
- None detected.

## Communities (64 total, 10 thin omitted)

### Community 0 - "run_sql_file"
Cohesion: 0.05
Nodes (49): Connection, DuckDBPyConnection, connect_duckdb(), connect_postgres(), Any, Path, Connections to both engines and access to the SQL files under `sql/`., Return the text of a SQL file, addressed relative to the `sql/` directory. (+41 more)

### Community 1 - "Research: OLTP vs OLAP Benchmark on NYC 311"
Cohesion: 0.05
Nodes (36): Content Quality, Feature Readiness, Notes, Requirement Completeness, Specification Quality Checklist: OLTP vs OLAP Benchmark on NYC 311, `benchmark_<profile>.json`, `benchmark_<profile>.md`, Contract: Results Files (+28 more)

### Community 2 - "common.sh"
Cohesion: 0.14
Nodes (27): check-prerequisites.sh script, check_dir(), check_feature_branch(), check_file(), feature_json_matches_feature_dir(), find_feature_dir_by_prefix(), find_specify_root(), get_current_branch() (+19 more)

### Community 3 - "cli.py"
Cohesion: 0.10
Nodes (33): ArgumentParser, OLTP vs OLAP benchmark on NYC 311 Service Requests. Usage: python benchmark.py…, Namespace, build_parser(), command_build(), command_load(), _connect(), _fail() (+25 more)

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
Cohesion: 0.18
Nodes (3): OLTP vs OLAP benchmark on NYC 311 Service Requests., parametrize, test_invalid_arguments_exit_with_code_2()

### Community 61 - "test_socrata.py"
Cohesion: 0.09
Nodes (34): _last_cursor(), Keyset position after a page: its last row that carries both key fields., _read_checkpoint(), Cursor, Exception, Paginated client for the NYC 311 dataset on the Socrata (SODA 2.x) API. Pages…, Return the rows that follow `cursor`, at most `limit` (default: the page size)., The API rejected the request; retrying would not help. (+26 more)

### Community 62 - "ingest"
Cohesion: 0.12
Nodes (23): FetchPage, Reporter, ingest(), Stage rows of the cut until `target_rows` are present, resuming from the…, FixtureSource, Stand-in for the API in integration tests: serves the fixture with keyset…, Serves rows in file order. A cursor resumes after the row it points to., Staging load: idempotent, resumable, and explicit about rejected rows. (+15 more)

### Community 63 - "ingest.py"
Cohesion: 0.15
Nodes (22): format_summary(), IngestSummary, parse_row(), Any, datetime, Load API pages into the staging area, idempotently and resumably. Each page is…, Insert one page and advance the checkpoint atomically. Returns the rows added., Turn one API row into a staging tuple, or say why it cannot be loaded. The API… (+14 more)

## Knowledge Gaps
- **296 isolated node(s):** `git-common.sh script`, `common.sh script`, `nyc311-bench`, `graphify`, `Usage` (+291 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 418 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ingest()` connect `ingest` to `run_sql_file`, `cli.py`, `test_socrata.py`, `ingest.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `run_sql_file()` connect `run_sql_file` to `cli.py`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Why does `Settings` connect `cli.py` to `run_sql_file`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `Settings` (e.g. with `command_build()` and `command_load()`) actually correct?**
  _`Settings` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `FixtureSource` (e.g. with `Cursor` and `SocrataUnavailable`) actually correct?**
  _`FixtureSource` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `git-common.sh script`, `common.sh script`, `nyc311-bench` to the rest of the system?**
  _296 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `run_sql_file` be split into smaller, more focused modules?**
  _Cohesion score 0.05191256830601093 - nodes in this community are weakly interconnected._