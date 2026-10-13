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

## Observations

The AI agent built the entire project — from an empty directory to a measured
benchmark with 182 passing tests — in a single working session. The SDD framework
and the Claude Code harness provided the structure that made this possible: the
constitution prevented the agent from chasing a significance threshold, the spec
kept the scope bounded, and the hooks enforced commit hygiene automatically.

The corrections cluster in two areas: **harness configuration** (7 of 13), where the
agent did not know how Claude Code itself works, and **realism checks** (4 of 13),
where the human caught assumptions that would have been misleading or fragile. The
remaining two (commit granularity and silent failure) were caught by the automated
`/speckit-analyze` step, not by the human directly.

Every correction was applied before the affected code was used downstream. None
required reworking completed features.
