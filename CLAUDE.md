# Proyecto: OLTP vs OLAP Benchmark

Reto técnico evaluado: demostrar con números medibles la diferencia de rendimiento
entre un modelo OLTP normalizado y un modelo OLAP analítico, con una API pública
como fuente de datos.

## Reglas de operación
- Seguir el flujo SDD de spec-kit: constitution → specify → plan → tasks → implement → analyze
- NUNCA implementar sin spec aprobado y plan generado
- NUNCA modificar archivos fuera del scope de la tarea actual
- NUNCA instalar dependencias sin aprobación humana
- NUNCA hacer `git add .` ni `git add -A` — agregar archivos explícitamente
- NUNCA hacer `git push` — el humano publica el repo
- Si un error no se resuelve en 2 intentos, DETENERSE y reportar
- Si la diferencia del benchmark no es significativa, DETENERSE. No manipular datos
- Commits semánticos y atómicos: feat:, fix:, test:, docs:, refactor:, chore:

## Modos del agente
- **Investigación**: subagente, solo lectura y web. Entrega informe, nunca decisiones.
- **Configuración**: entorno, harness, estructura. Todo se commitea.
- **Implementación**: solo con spec aprobado y fase autorizada por el humano.

Al terminar una fase: actualizar "Estado actual", ejecutar `graphify update .` si
cambió código y `/speckit-analyze` si se implementó algo.

## Stack
- Python 3.12+ (local: 3.13)
- PostgreSQL 17 vía `docker compose` (OLTP), puerto local 5433
- OLAP: [se define en Fase 1]
- Testing: pytest
- Lint y formato: ruff

## Harness
- `.claude/settings.json`: permisos (allow/deny) y hooks
- `.claude/hooks/guard_bash.py`: bloquea `git add` masivo y exige ruff limpio antes de commitear
- `.claude/hooks/after_pytest.py`: recuerda el paso de verificación SDD tras correr tests
- Hooks de Graphify: sugieren `graphify query` antes de búsquedas y lecturas crudas

## Entregables (en la raíz del repo)
README.md, DESIGN.md (máx. 2 páginas), AI_WORKFLOW.md, script de benchmark con
resultados en `results/`, tests de integración en `tests/integration/`.

## Estado actual
- **Fase -1 (bootstrap): completada.** spec-kit 0.8.7 inicializado, skill de Graphify
  instalado a nivel proyecto, harness configurado, Postgres definido en `docker-compose.yml`.
- **Fase 0 (investigación de APIs): completada.** Dos rondas con subagente, 15 fuentes
  evaluadas. El humano eligió **NYC 311 Service Requests** (Socrata, dataset `erm2-nwe9`,
  `https://data.cityofnewyork.us/resource/erm2-nwe9.json`): 22,7 M de filas medidas
  (2020-01-01 a 2026-10-10), páginas de hasta 50.000 filas, sin throttling con app token.
- Pendiente de verificar en Fase 1: licencia de NYC Open Data y versión del endpoint SODA.
- **Siguiente: Fase 1** — constitution y spec; definir el motor OLAP.
- Pendiente del humano: crear un app token de Socrata y arrancar Docker Desktop antes de la Fase 2.

## Bitácora para AI_WORKFLOW.md
Correcciones reales hechas al plan generado por AI, para documentarlas al final:
- El prompt maestro definía hooks en `.claude/hooks.json`; Claude Code los lee de
  `.claude/settings.json`. Se movieron ahí.
- Los matchers `Bash(git commit*)` no son válidos en hooks (el matcher es el nombre de la
  herramienta). El filtrado por comando se hace dentro de `guard_bash.py`.
- El hook que bloqueaba `git add .` salía con `exit 1`, que no bloquea. Se cambió a `exit 2`.
- Los recordatorios por `echo` no llegan al modelo; se devuelven como `additionalContext`.
- Las reglas `Write(ruta)` se reemplazaron por `Edit(ruta)`, que es lo que gobierna las ediciones.
- `/speckit-converge` no existe en spec-kit 0.8.7; se usa `/speckit-analyze`.
- La constitution vive en `.specify/memory/constitution.md` y los specs en `specs/`.
- El prompt denegaba `docker` sin que hubiera PostgreSQL instalado; se permite `docker compose`.
- El nudge de grep hacia Graphify sobraba: `graphify install --project` ya registra sus hooks.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
