# AI Workflow

How this project was built with Claude Code (Anthropic's CLI agent) and what went
wrong along the way.

## Development method

The project followed **Spec-Driven Development (SDD)** using the spec-kit 0.8.7
framework. Every phase required explicit human authorization before the agent could
proceed.

1. **Constitution** (`.specify/memory/constitution.md`): seven principles governing
   the project — benchmark integrity, fair comparison, verifiable quality, simplicity,
   traceability, responsible ingestion, and spec-driven development.
2. **Specification** (`specs/001-nyc311-oltp-olap-benchmark/spec.md`): four user
   stories with acceptance scenarios, success criteria and functional requirements.
3. **Plan** (`specs/001-nyc311-oltp-olap-benchmark/plan.md`): technical design backed
   by research (`research.md`), a data model (`data-model.md`), CLI and query
   contracts, and a quickstart walkthrough.
4. **Tasks** (`specs/001-nyc311-oltp-olap-benchmark/tasks.md`): 57 tasks grouped by
   user story, implemented in dependency order.
5. **Analysis**: `/speckit-analyze` ran after each user story to check compliance
   against the spec, plan and constitution.

## Tools used

| Tool | Role in the project |
|---|---|
| Claude Code (CLI) with Claude Sonnet and Opus models | The agent that wrote the code, SQL, tests, dashboard and documentation |
| spec-kit 0.8.7 | SDD framework: constitution, specify, plan, tasks, implement, analyze |
| Research subagents | Read-only evaluation of 15 public APIs (two rounds) |
| Graphify | Knowledge graph of the code, used to navigate before reading raw files |
| Claude Code hooks and permissions | Guardrails: no bulk `git add`, ruff before commit, pytest reminder |
| Project skills (`dashboard-setup`, `dashboard-module`, `dashboard-chart`) | Reusable recipes the agent followed to build the React dashboard |
| Persistent memory (engram) | Carried decisions and pending work across working sessions |

## Key prompts

The human worked in Spanish; prompts are translated here. The first group is condensed
from the session history (wording approximate); the second group is quoted from the most
recent session.

**Directing the process (condensed)**

- *Master prompt, phase by phase*: build the OLTP vs OLAP benchmark following SDD, one
  phase at a time, stopping for human approval between phases; never `git push`; never
  install dependencies without approval; if a fix fails twice, stop and report; if the
  difference is not significant, stop and do not manipulate the data.
- *Research*: "Evaluate public APIs as candidate data sources and give me a comparison
  table. Do not choose; I will." (two rounds, 15 sources, the human chose NYC 311).
- *Language*: "Everything written into the repo must be in English: code, comments,
  commits, docs and spec-kit artifacts."
- *Realism check*: the human questioned a "load in under 3 hours" success criterion,
  which led to the 1-hour limit and the quick profile.
- *Dashboard*: authorize EXPLAIN ANALYZE capture, the "what you discarded" and "what you
  would change at 10x" sections of DESIGN.md, and a React + TypeScript dashboard with
  Clean Architecture, building reusable skills first and then the modules.

**Iterating on the dashboard (quoted)**

- "How can we make the DuckDB side show the real plan, with the timings?"
- "Why does the DuckDB side look better structured? Is that something we did?"
- "Can you improve the layout of these tables so it looks more like a star?"
- "Explain this query, 90th percentile of resolution time per agency and quarter. What
  is a percentile 90?"
- "In the introduction add the dataset URL and the parameters we used to consume it, and
  an example record in JSON format."

## How AI output was verified

- **Tests**: 182 Python tests (129 unit, 53 integration against a real PostgreSQL) and
  25 dashboard tests (Vitest). The suite was green at every commit.
- **Query equivalence**: integration tests compare OLTP and OLAP results row by row, and
  the runner refuses to measure if both models do not hold the same number of rows
  (parity check, exit code 4).
- **Automated analysis**: `/speckit-analyze` after each user story checks spec, plan,
  tasks and constitution against each other. It found two of the corrections below.
- **Hooks**: ruff must pass before every commit; bulk `git add` is blocked.
- **Reading the output**: the human inspected the rendered dashboard and the stored
  EXPLAIN plans, which exposed the DuckDB plan bug (correction 14).
- **Honest reporting**: the constitution forbids tuning results; the README states the
  limitations (defaults not tuned, schema and engine effects combined).

## Agent modes

| Mode | Scope | Tools | Commits |
|---|---|---|---|
| Research | Read-only investigation with web access | WebFetch, subagent | None |
| Configuration | Environment, harness, project structure | Bash, Write, Edit | Yes |
| Implementation | Code, tests, SQL, results | All, with approved spec | Yes |

- **Research** evaluated 15 public APIs across two rounds and delivered comparative
  tables. The agent never chose the data source; the human did.
- **Configuration** set up the project skeleton, Docker Compose, the virtual
  environment, the Claude Code harness and the Graphify knowledge graph.
- **Implementation** only started after the spec, plan and tasks were approved. Each
  module was committed together with its tests, and the test suite was green at every
  commit.

## Harness and guardrails

- **`.claude/settings.json`**: permission allow-lists and deny-lists that restrict
  what tools the agent may call and on which paths. `pip install`, `curl`, writes to
  `.env*` and `.claude/hooks` are denied; the human applies those changes manually.
- **`.claude/hooks/guard_bash.py`** (PreToolUse on Bash): blocks `git add .` and
  `git add -A` (exit code 2), and runs `ruff check` and `ruff format --check` before
  every `git commit`.
- **`.claude/hooks/after_pytest.py`** (PostToolUse on Bash): when pytest runs, it
  returns an `additionalContext` reminder to verify the result against the spec.
- **Graphify** (`.claude/skills/graphify/`): a knowledge graph built from the AST,
  updated after code changes, used for codebase navigation before raw file reads.

## Corrections to AI-generated work

Every item below is a real mistake made by the AI agent and caught by the human or
by the `/speckit-analyze` verification step. They are listed in the order they
occurred.

### Harness and hooks

1. **Hook location**: the master prompt placed hooks in `.claude/hooks.json`. Claude
   Code reads them from `.claude/settings.json`. They were moved there.
2. **Hook matchers**: `Bash(git commit*)` was used as a matcher. The matcher field
   takes a tool name, not a command glob. Command filtering was moved inside
   `guard_bash.py`.
3. **Hook exit code**: the blocking hook exited with code 1, which Claude Code
   treats as a non-blocking warning. Changed to exit code 2, which blocks the tool
   call.
4. **Hook feedback mechanism**: `echo` output does not reach the model. Feedback
   must be returned as `additionalContext` (printed to stderr with exit code 0) or
   as a blocking message (printed to stderr with exit code 2).
5. **Edit rules**: the permissions used `Write(path)` to restrict file edits, but
   Claude Code governs edits with the `Edit` tool. Rules were changed to
   `Edit(path)`.
6. **Docker permission**: the master prompt denied `docker`, but PostgreSQL runs in
   a container. `docker compose` was added to the allow-list.
7. **Redundant hooks**: a hook nudged the agent toward Graphify before grep. After
   `graphify install --project`, the Graphify skill already registers its own hooks,
   making the extra one redundant.

### Spec and planning

8. **Non-existent command**: the agent referenced `/speckit-converge`, which does
   not exist in spec-kit 0.8.7. The correct command is `/speckit-analyze`.
9. **File locations**: the agent expected the constitution and specs in locations
   that did not match the framework's layout. The constitution lives in
   `.specify/memory/constitution.md` and specs in `specs/`.
10. **Unrealistic success criterion**: the agent wrote "load in under 3 hours" as a
    success criterion, which reads as the expected duration rather than a ceiling.
    Replaced with a 1-hour limit for the full profile and a quick profile (200,000
    rows, under 10 minutes) so evaluators need not wait.
11. **Language**: the agent drafted the constitution, specification and CLAUDE.md in
    Spanish. The human required English for every file in the repository. All
    artifacts were translated.

### Implementation

12. **Commit granularity**: the task list required one commit per task with tests
    written and seen failing before the implementation code. The agent instead
    committed each module together with its tests, sometimes covering several task
    IDs in one commit. `/speckit-analyze` flagged the deviation. The rule in
    `tasks.md` was rewritten to match what is actually verifiable: the test suite is
    green at every commit.
13. **Silent failure on short data**: a load that ran out of API data before reaching
    the profile's target row count exited with code 0, as though it had succeeded.
    `/speckit-analyze` flagged the undefined case. The loader now exits with code 2,
    and the CLI contract documents the exit code.

### Dashboard

14. **Wrong column in the DuckDB plan**: `EXPLAIN ANALYZE` in DuckDB returns two
    columns (a label and the plan text). The runner stored `row[0]`, so the dashboard
    showed the literal string `analyzed_plan` instead of the plan. Noticed by the human
    in the execution-plans panel; fixed to `row[1]` (commit `bd1d973`). The plans already stored in
    the result JSON files were back-filled with a one-off script that re-ran
    `EXPLAIN ANALYZE`, not by repeating the whole measurement. The timings were never
    affected.
15. **Misleading map data**: the borough map drew a circle for the `Unspecified`
    borough, which is not a place. The human spotted it; it was excluded from circles
    and legend (commit `c6062fd`).
16. **Missing barrel files**: two components were created without their `index.ts`, so
    the dev server failed at startup with "Failed to resolve import". Added in commit
    `c629ae2`.
17. **Schema diagram not a star**: the first OLAP diagram laid the tables out in a
    grid, which hid the point of a star schema. The human asked for a real star; the six
    dimensions were placed at exact 60° positions around the fact table (commit
    `69bfac8`).

## Observations

The AI agent built the entire project — from an empty directory to a measured
benchmark with 182 passing tests and a React dashboard with 25 more — over several
working sessions. The SDD framework
and the Claude Code harness provided the structure that made this possible: the
constitution prevented the agent from chasing a significance threshold, the spec
kept the scope bounded, and the hooks enforced commit hygiene automatically.

The corrections cluster in three areas: **harness configuration** (7 of 17), where the
agent did not know how Claude Code itself works, **realism checks** (4 of 17), where the
human caught assumptions that would have been misleading or fragile, and the
**dashboard** (4 of 17), where visual output had to be inspected by a person. The two
remaining ones (commit granularity and silent failure) were caught by the automated
`/speckit-analyze` step, not by the human directly.

Every correction was applied before the affected code was used downstream. None
required reworking completed features.
