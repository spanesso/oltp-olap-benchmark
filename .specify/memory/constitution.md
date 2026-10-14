<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: none redefined; all seven translated from Spanish to English
  without change of meaning
- Added sections: "Language" rule under Technical Constraints and Deliverables
- Removed sections: none
- Templates:
  - ✅ .specify/templates/plan-template.md — "Constitution Check" is generic and derived
    from this file; no change needed
  - ✅ .specify/templates/spec-template.md — no references to principles; no change needed
  - ✅ .specify/templates/tasks-template.md — no references to principles; no change needed
  - ✅ .specify/templates/commands/ — does not exist in spec-kit 0.8.7
- Deferred TODOs:
  - OLAP engine: defined in the plan of the first feature, pending human approval
-->

# OLTP vs OLAP Benchmark Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every code change follows the flow constitution → specify → plan → tasks → implement →
analyze. No task is implemented without a spec approved by the human and a generated plan.
Each phase ends with a stop: the human authorizes the next one.

**Rationale**: the challenge evaluates the process as much as the result; the spec is the
contract the implementation is verified against.

### II. Benchmark Integrity (NON-NEGOTIABLE)

Published results MUST be real measurements, reproducible with the scripts in the
repository. Adjusting data, queries, indexes or configuration for the sole purpose of
inflating the difference between models is forbidden. If the OLTP vs OLAP difference does
not reach the significance threshold defined in the spec, work STOPS and is reported to the
human.

**Rationale**: a manipulated benchmark invalidates the whole deliverable.

### III. Fair Comparison

Both models MUST be loaded with the same dataset and answer the same logical queries, with
equivalent results verified by tests. The measurement methodology MUST be documented:
warm-up, number of repetitions, reported statistic (median and percentiles), data volume,
hardware and versions. Each model uses the indexes and design idiomatic to its paradigm;
neither is deliberately degraded.

**Rationale**: the measured difference is only defensible if the model is the only thing
that changes.

### IV. Verifiable Quality

Tests are written with pytest; integration tests live in `tests/integration/` and run
against real databases, not mocks. `ruff check` and `ruff format --check` MUST pass before
every commit. A task is not done until its tests pass.

**Rationale**: claims of correctness and of equivalence between models must be checkable by
running a command.

### V. Simplicity and Bounded Scope

No dependency is installed without human approval. No file outside the scope of the current
task is modified. The simplest solution that satisfies the spec is preferred; any additional
complexity MUST be justified in the plan.

**Rationale**: the challenge is time-boxed and `DESIGN.md` is limited to two pages; whatever
does not contribute to the measurement is noise.

### VI. Traceability

Commits are semantic and atomic (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
Files are added explicitly; `git add .` and `git add -A` are forbidden. The agent never runs
`git push`: the human publishes. Corrections made to AI-generated work are recorded for
`AI_WORKFLOW.md`.

**Rationale**: the history is part of the evidence being evaluated.

### VII. Responsible Ingestion

Ingestion MUST respect the limits of the source API. Credentials (app token) are read from
environment variables and never committed. The load MUST be idempotent and resumable:
re-running it does not duplicate rows and an interruption does not force a restart from
zero.

**Rationale**: a public source is a shared resource, and a multi-million-row ingestion that
cannot resume puts the deadline at risk.

## Technical Constraints and Deliverables

- **Language**: everything written into the repository MUST be in English: code, comments,
  commit messages, documentation, spec-kit artifacts and agent configuration files.
- **Runtime**: Python 3.12 or later.
- **OLTP**: PostgreSQL 17 via `docker compose`, local port 5433.
- **OLAP**: engine defined in the plan of the first feature, with justification.
- **Data source**: NYC 311 Service Requests (Socrata, dataset `erm2-nwe9`).
- **Tooling**: pytest for tests, ruff for lint and format.
- **Deliverables at the repo root**: `README.md`, `DESIGN.md` (maximum 2 pages),
  `AI_WORKFLOW.md`, benchmark script with results in `results/`, and integration tests in
  `tests/integration/`.

## Workflow and Quality Gates

- **Agent modes**: Research (subagent, read-only and web; delivers a report, never
  decisions), Configuration (environment and harness; everything is committed) and
  Implementation (only with an approved spec and an authorized phase).
- **Two-attempt rule**: if an error is not solved in 2 attempts, the agent stops and
  reports.
- **Phase close**: update "Current status" in `CLAUDE.md`, run `graphify update .` if code
  changed and `/speckit-analyze` if something was implemented.
- **Plan gate**: the "Constitution Check" of every plan MUST evaluate principles I–VII and
  record any deviation under "Complexity Tracking".

## Governance

This constitution supersedes any other practice in the project. `CLAUDE.md` is the runtime
operating guide and MUST stay consistent with it.

- **Amendments**: proposed by the agent or the human, approved by the human, and recorded in
  the Sync Impact Report at the top of this file.
- **Versioning**: semantic. MAJOR for removing or redefining principles, MINOR for adding
  principles or sections, PATCH for wording clarifications.
- **Compliance**: every plan checks the principles before research and after design;
  `/speckit-analyze` reviews consistency between spec, plan and tasks after each
  implementation.

**Version**: 1.1.0 | **Ratified**: 2026-10-12 | **Last Amended**: 2026-10-12
