# Project: OLTP vs OLAP Benchmark

Evaluated technical challenge: show, with measurable numbers, the performance difference
between a normalized OLTP model and an analytical OLAP model, using a public API as the
data source.

## Operating rules
- Follow the spec-kit SDD flow: constitution → specify → plan → tasks → implement → analyze
- NEVER implement without an approved spec and a generated plan
- NEVER modify files outside the scope of the current task
- NEVER install dependencies without human approval
- NEVER run `git add .` or `git add -A` — add files explicitly
- NEVER run `git push` — the human publishes the repo
- If an error is not solved in 2 attempts, STOP and report
- If the benchmark difference is not significant, STOP. Do not manipulate data
- Semantic, atomic commits: feat:, fix:, test:, docs:, refactor:, chore:
- Everything written into the repo is in English: code, comments, commits, docs, spec-kit
  artifacts and Claude files

## Agent modes
- **Research**: subagent, read-only and web. Delivers a report, never decisions.
- **Configuration**: environment, harness, structure. Everything is committed.
- **Implementation**: only with an approved spec and a phase authorized by the human.

When a phase ends: update "Current status", run `graphify update .` if code changed and
`/speckit-analyze` if something was implemented.

## Stack
- Python 3.12+ (local: 3.13)
- PostgreSQL 17 via `docker compose` (OLTP), local port 5433
- OLAP: DuckDB (embedded, star schema in `data/olap.duckdb`)
- Dependencies approved by the human: `duckdb`, `psycopg[binary]`; HTTP via the standard library
- Testing: pytest
- Lint and format: ruff

## Harness
- `.claude/settings.json`: permissions (allow/deny) and hooks
- `.claude/hooks/guard_bash.py`: blocks bulk `git add` and requires clean ruff before committing
- `.claude/hooks/after_pytest.py`: reminds the agent of the SDD verification step after tests
- Graphify hooks: suggest `graphify query` before raw searches and reads

## Deliverables (at the repo root)
README.md, DESIGN.md (max. 2 pages), AI_WORKFLOW.md, benchmark script with results in
`results/`, integration tests in `tests/integration/`.

## Current status
- **Phase -1 (bootstrap): done.** spec-kit 0.8.7 initialized, Graphify skill installed at
  project level, harness configured, Postgres defined in `docker-compose.yml`.
- **Phase 0 (API research): done.** Two subagent rounds, 15 sources evaluated. The human
  chose **NYC 311 Service Requests** (Socrata, dataset `erm2-nwe9`,
  `https://data.cityofnewyork.us/resource/erm2-nwe9.json`): 22.7 M rows measured
  (2020-01-01 to 2026-10-10), pages of up to 50,000 rows, no throttling with an app token.
- **Phase 1 (constitution, spec, plan, tasks): done.** Constitution v1.1.0, spec and plan
  approved (DuckDB as OLAP engine), 57 tasks in
  `specs/001-nyc311-oltp-olap-benchmark/tasks.md`, on branch `001-nyc311-oltp-olap-benchmark`.
- **Phase 2 (implementation): in progress.** T001–T048 done: User Stories 1 to 3 and the
  official measurement. Full profile (5,000,000 requests): OLAP 55x to 184x faster on all
  six queries, significance threshold reached (6 of 6), medians repeatable within 10%,
  every query equivalent on both models. Results committed in `results/`. 182 tests pass.
- **Next**: documentation (T049–T053): README, DESIGN, AI_WORKFLOW, quickstart walkthrough.
  Requires human authorization. User Story 4 (T054–T057) is optional.
- The test fixture is synthetic: the NYC Open Data terms page returned 404, so no real rows
  are committed.
- Pending from the human: read the NYC Open Data terms in a browser before the README is
  published.

## Log for AI_WORKFLOW.md
Real corrections made to AI-generated work, to be documented at the end:
- The master prompt defined hooks in `.claude/hooks.json`; Claude Code reads them from
  `.claude/settings.json`. They were moved there.
- `Bash(git commit*)` matchers are not valid in hooks (the matcher is the tool name).
  Command filtering is done inside `guard_bash.py`.
- The hook that blocked `git add .` exited with `exit 1`, which does not block. Changed to
  `exit 2`.
- `echo` reminders do not reach the model; they are returned as `additionalContext`.
- `Write(path)` rules were replaced with `Edit(path)`, which is what governs edits.
- `/speckit-converge` does not exist in spec-kit 0.8.7; `/speckit-analyze` is used.
- The constitution lives in `.specify/memory/constitution.md` and specs in `specs/`.
- The prompt denied `docker` although no PostgreSQL was installed; `docker compose` is allowed.
- The grep nudge towards Graphify was redundant: `graphify install --project` already
  registers its hooks.
- The agent wrote a "load in under 3 hours" success criterion that read as the expected
  duration. The human questioned it; it was replaced by a 1-hour limit for the full profile
  plus a quick profile (200,000 rows, under 10 minutes) so evaluators need not wait.
- The task list required one commit per task and tests written and seen failing before the
  code. The agent instead committed each module together with its tests, sometimes covering
  several task ids. `/speckit-analyze` flagged it; the rule in tasks.md was rewritten to
  match what is actually verifiable (green suite at every commit).
- A load that ran out of data before reaching its target exited with code 0. The analysis
  flagged the undefined case; it now exits with code 2 and the contract documents it.
- The agent drafted the constitution, spec and CLAUDE.md in Spanish. The human required
  English for the whole repo; all artifacts were translated.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan at
`specs/001-nyc311-oltp-olap-benchmark/plan.md`
<!-- SPECKIT END -->

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
