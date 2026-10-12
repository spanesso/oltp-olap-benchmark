<!--
Sync Impact Report
- Version change: (plantilla sin ratificar) → 1.0.0
- Principios modificados: ninguno (ratificación inicial)
- Secciones añadidas: Core Principles (I–VII), Restricciones técnicas y entregables,
  Flujo de trabajo y puertas de calidad, Governance
- Secciones eliminadas: ninguna
- Plantillas:
  - ✅ .specify/templates/plan-template.md — "Constitution Check" es genérico y se deriva
    de este archivo; sin cambios
  - ✅ .specify/templates/spec-template.md — sin referencias a principios; sin cambios
  - ✅ .specify/templates/tasks-template.md — sin referencias a principios; sin cambios
  - ✅ .specify/templates/commands/ — no existe en spec-kit 0.8.7
- TODOs diferidos:
  - Motor OLAP: se define en el plan de la primera feature
  - Umbral de "diferencia significativa" del benchmark: se define en el spec
-->

# OLTP vs OLAP Benchmark Constitution

## Core Principles

### I. Spec-Driven Development (NO NEGOCIABLE)

Todo cambio de código sigue el flujo constitution → specify → plan → tasks → implement →
analyze. Ninguna tarea se implementa sin un spec aprobado por el humano y un plan generado.
Cada fase termina en una parada: el humano autoriza la siguiente.

**Razón**: el reto evalúa el proceso tanto como el resultado; el spec es el contrato contra
el que se verifica la implementación.

### II. Integridad del benchmark (NO NEGOCIABLE)

Los resultados publicados DEBEN ser mediciones reales y reproducibles con los scripts del
repositorio. Está prohibido ajustar datos, consultas, índices o configuración con el único
fin de inflar la diferencia entre modelos. Si la diferencia OLTP vs OLAP no alcanza el umbral
de significancia definido en el spec, el trabajo se DETIENE y se reporta al humano.

**Razón**: un benchmark manipulado invalida el entregable completo.

### III. Comparación justa

Ambos modelos DEBEN cargarse con el mismo conjunto de datos y responder las mismas consultas
lógicas, con resultados equivalentes verificados por tests. La metodología de medición DEBE
quedar documentada: calentamiento, número de repeticiones, estadístico reportado (mediana y
percentiles), volumen de datos, hardware y versiones. Cada modelo usa los índices y el diseño
idiomáticos de su paradigma; no se degrada deliberadamente ninguno.

**Razón**: la diferencia medida solo es defendible si lo único que cambia es el modelo.

### IV. Calidad verificable

Los tests se escriben con pytest; los de integración viven en `tests/integration/` y corren
contra bases de datos reales, no mocks. `ruff check` y `ruff format --check` DEBEN pasar
antes de cada commit. Una tarea no está terminada hasta que sus tests pasan.

**Razón**: las afirmaciones de corrección y de equivalencia entre modelos deben poder
comprobarse ejecutando un comando.

### V. Simplicidad y alcance acotado

No se instala ninguna dependencia sin aprobación humana. No se modifican archivos fuera del
scope de la tarea en curso. Se prefiere la solución más simple que cumpla el spec; toda
complejidad adicional DEBE justificarse en el plan.

**Razón**: el reto tiene tiempo acotado y `DESIGN.md` un máximo de dos páginas; lo que no
aporta a la medición es ruido.

### VI. Trazabilidad

Los commits son semánticos y atómicos (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`,
`chore:`). Los archivos se agregan explícitamente; `git add .` y `git add -A` están
prohibidos. El agente nunca ejecuta `git push`: el humano publica. Las correcciones hechas
al trabajo generado por AI se registran para `AI_WORKFLOW.md`.

**Razón**: el historial es parte de la evidencia que se evalúa.

### VII. Ingesta responsable

La ingesta DEBE respetar los límites de la API de origen. Las credenciales (app token) se
leen de variables de entorno y nunca se commitean. La carga DEBE ser idempotente y
reanudable: reejecutarla no duplica filas y una interrupción no obliga a empezar de cero.

**Razón**: una fuente pública es un recurso compartido, y una ingesta de millones de filas
que no se puede reanudar pone en riesgo el plazo.

## Restricciones técnicas y entregables

- **Lenguaje**: Python 3.12 o superior.
- **OLTP**: PostgreSQL 17 vía `docker compose`, puerto local 5433.
- **OLAP**: motor por definir en el plan de la primera feature, con justificación.
- **Fuente de datos**: NYC 311 Service Requests (Socrata, dataset `erm2-nwe9`).
- **Tooling**: pytest para tests, ruff para lint y formato.
- **Entregables en la raíz del repo**: `README.md`, `DESIGN.md` (máximo 2 páginas),
  `AI_WORKFLOW.md`, script de benchmark con resultados en `results/` y tests de integración
  en `tests/integration/`.

## Flujo de trabajo y puertas de calidad

- **Modos del agente**: Investigación (subagente, solo lectura y web; entrega informe, nunca
  decisiones), Configuración (entorno y harness; todo se commitea) e Implementación (solo con
  spec aprobado y fase autorizada).
- **Regla de los dos intentos**: si un error no se resuelve en 2 intentos, el agente se
  detiene y reporta.
- **Cierre de fase**: actualizar "Estado actual" en `CLAUDE.md`, ejecutar `graphify update .`
  si cambió código y `/speckit-analyze` si se implementó algo.
- **Puerta de plan**: el "Constitution Check" de cada plan DEBE evaluar los principios I–VII
  y registrar cualquier desviación en "Complexity Tracking".

## Governance

Esta constitución prevalece sobre cualquier otra práctica del proyecto. `CLAUDE.md` es la
guía operativa de ejecución y DEBE mantenerse coherente con ella.

- **Enmiendas**: las propone el agente o el humano, las aprueba el humano y se registran en
  el Sync Impact Report al inicio de este archivo.
- **Versionado**: semántico. MAJOR para eliminar o redefinir principios, MINOR para añadir
  principios o secciones, PATCH para aclaraciones de redacción.
- **Cumplimiento**: cada plan verifica los principios antes de la investigación y tras el
  diseño; `/speckit-analyze` revisa la coherencia entre spec, plan y tareas tras cada
  implementación.

**Version**: 1.0.0 | **Ratified**: 2026-10-12 | **Last Amended**: 2026-10-12
