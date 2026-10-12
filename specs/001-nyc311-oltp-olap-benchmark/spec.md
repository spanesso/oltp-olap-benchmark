# Feature Specification: Benchmark OLTP vs OLAP sobre NYC 311

**Feature Branch**: `001-nyc311-oltp-olap-benchmark`  
**Created**: 2026-10-12  
**Status**: Approved (2026-10-12)  
**Input**: User description: "Benchmark OLTP vs OLAP sobre NYC 311 Service Requests: ingesta desde la API pública, modelo OLTP normalizado, modelo OLAP en esquema estrella, conjunto fijo de consultas analíticas, script de benchmark con resultados en results/ y tests de integración de equivalencia."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cargar los mismos datos en ambos modelos (Priority: P1)

Como evaluador del reto, quiero obtener las solicitudes de servicio de NYC 311 desde su API
pública y dejarlas cargadas en un modelo transaccional normalizado y en un modelo analítico
en estrella, para que cualquier comparación posterior parta exactamente de los mismos datos.

**Why this priority**: sin datos idénticos en ambos modelos no hay benchmark defendible. Es
la base de todo lo demás y por sí sola ya demuestra la ingesta y los dos diseños de datos.

**Independent Test**: ejecutar la carga con un volumen reducido y comprobar que ambos modelos
reportan el mismo número de solicitudes y los mismos totales por dimensión.

**Acceptance Scenarios**:

1. **Given** una base vacía y acceso a la API, **When** se ejecuta la carga con un volumen
   objetivo, **Then** ambos modelos contienen ese número de solicitudes, sin duplicados.
2. **Given** una carga ya completada, **When** se vuelve a ejecutar con los mismos
   parámetros, **Then** el número de solicitudes en ambos modelos no cambia.
3. **Given** una carga interrumpida a la mitad, **When** se relanza, **Then** continúa desde
   el último punto confirmado sin volver a descargar lo ya cargado.
4. **Given** que la API responde con un error temporal o de exceso de peticiones, **When**
   la carga está en curso, **Then** espera, reintenta y termina sin perder ni duplicar filas.
5. **Given** que no hay credencial de la API configurada, **When** se lanza la carga,
   **Then** se informa de ello con un mensaje claro antes de descargar nada.

---

### User Story 2 - Medir las consultas analíticas en ambos modelos (Priority: P1)

Como evaluador, quiero ejecutar un único comando que mida un conjunto fijo de consultas
analíticas en los dos modelos y me entregue los tiempos comparados, para ver con números la
diferencia de rendimiento.

**Why this priority**: es el entregable central del reto: la evidencia medible.

**Independent Test**: con ambos modelos cargados, ejecutar el benchmark y verificar que
produce un informe con tiempos por consulta y por modelo, y el factor de diferencia.

**Acceptance Scenarios**:

1. **Given** ambos modelos cargados, **When** se ejecuta el benchmark, **Then** cada consulta
   se mide en los dos modelos con ejecuciones de calentamiento descartadas y varias
   repeticiones medidas.
2. **Given** un benchmark terminado, **When** se abre el directorio de resultados, **Then**
   hay un archivo legible por máquina y un resumen legible por humanos con mediana,
   percentiles y factor de diferencia por consulta.
3. **Given** un benchmark terminado, **When** se lee el informe, **Then** constan el volumen
   de datos, el entorno de ejecución, la fecha y los parámetros de medición.
4. **Given** que la diferencia no alcanza el umbral de significancia, **When** termina el
   benchmark, **Then** el informe lo declara explícitamente y no se altera ningún dato.
5. **Given** un evaluador con poco tiempo, **When** ejecuta carga, benchmark y tests con el
   perfil rápido, **Then** todo termina en minutos y el informe advierte que esos tiempos no
   son los oficiales.
6. **Given** un evaluador que no quiere ejecutar nada, **When** abre el repositorio, **Then**
   encuentra los resultados oficiales del perfil completo ya publicados.

---

### User Story 3 - Verificar que ambos modelos responden lo mismo (Priority: P2)

Como evaluador, quiero tests automáticos que confirmen que cada consulta devuelve resultados
equivalentes en los dos modelos, para confiar en que se comparan respuestas iguales.

**Why this priority**: da validez a los números; sin ella la diferencia podría deberse a que
los modelos responden preguntas distintas.

**Independent Test**: ejecutar la suite de integración sobre una carga reducida y comprobar
que pasa; alterar una fila en un solo modelo y comprobar que falla.

**Acceptance Scenarios**:

1. **Given** ambos modelos cargados, **When** se ejecutan los tests de integración, **Then**
   se verifica que el número de solicitudes y los totales por dimensión coinciden.
2. **Given** ambos modelos cargados, **When** se ejecuta cada consulta del benchmark en los
   dos, **Then** los resultados son equivalentes (mismas filas y valores, con tolerancia
   numérica documentada para promedios).
3. **Given** una discrepancia entre modelos, **When** se ejecutan los tests, **Then** fallan
   indicando qué consulta o qué total difiere.

---

### User Story 4 - Mostrar el contraste en operaciones transaccionales (Priority: P3)

Como evaluador, quiero ver también cómo se comportan ambos modelos en operaciones
transaccionales típicas (consultar una solicitud por su identificador, registrar una nueva),
para entender el compromiso completo y no solo el lado favorable al modelo analítico.

**Why this priority**: enriquece la conclusión, pero el reto se cumple sin ella. Se implementa
solo si queda tiempo una vez cumplidas las historias 1 a 3.

**Independent Test**: ejecutar el benchmark con el grupo de operaciones transaccionales
activado y comprobar que el informe las presenta separadas de las analíticas.

**Acceptance Scenarios**:

1. **Given** ambos modelos cargados, **When** se ejecuta el grupo transaccional, **Then** el
   informe muestra sus tiempos en una sección distinta de las consultas analíticas.

---

### Edge Cases

- Solicitudes sin fecha de cierre (aún abiertas): no tienen tiempo de resolución y no deben
  contar en promedios de resolución, pero sí en conteos.
- Solicitudes con fecha de cierre anterior a la de creación: se cargan, se marcan como
  inválidas para la medida de resolución y se cuentan en el informe de calidad de datos.
- Valores de dimensión ausentes o vacíos (borough, código postal, canal): se asignan a un
  miembro "Desconocido" en ambos modelos, nunca se descartan en uno solo.
- La fuente añade o modifica solicitudes mientras dura la carga: la carga trabaja sobre un
  corte fijo (rango de fechas de creación cerrado) con un orden estable de paginación.
- La API devuelve menos filas de las pedidas o una página vacía antes de alcanzar el objetivo.
- El volumen objetivo pedido supera las filas disponibles en el rango elegido.
- El benchmark se lanza con un modelo vacío o con conteos distintos entre modelos: debe
  negarse a medir y explicar por qué.

## Requirements *(mandatory)*

### Functional Requirements

**Ingesta**

- **FR-001**: El sistema DEBE obtener las solicitudes de servicio de NYC 311 desde su API
  pública, por páginas y en un orden estable.
- **FR-002**: El volumen objetivo DEBE ser configurable, con dos perfiles predefinidos:
  **completo** (5.000.000 de solicitudes, el de los resultados oficiales) y **rápido**
  (200.000 solicitudes, para que un evaluador verifique el funcionamiento en minutos). El
  mínimo aceptado es 100.000.
- **FR-003**: La ingesta DEBE trabajar sobre un corte fijo y declarado de los datos (rango de
  fechas de creación), de modo que dos cargas con los mismos parámetros obtengan lo mismo.
- **FR-004**: La ingesta DEBE ser idempotente: reejecutarla no duplica solicitudes.
- **FR-005**: La ingesta DEBE ser reanudable tras una interrupción, desde el último punto
  confirmado.
- **FR-006**: La ingesta DEBE respetar los límites de la API, reintentando con espera ante
  errores temporales y deteniéndose con un mensaje claro ante errores persistentes.
- **FR-007**: La credencial de la API DEBE leerse del entorno y no quedar nunca en el
  repositorio ni en los registros de ejecución.
- **FR-008**: La ingesta DEBE informar su progreso y, al terminar, un resumen: filas
  cargadas, filas rechazadas con su motivo y duración.

**Modelos de datos**

- **FR-009**: El modelo transaccional DEBE estar normalizado: la solicitud referencia a
  agencia, tipo de reclamo con su descriptor, ubicación, canal y estado, cada uno almacenado
  una sola vez.
- **FR-010**: El modelo analítico DEBE organizarse como esquema estrella: un hecho por
  solicitud con dimensiones de tiempo, agencia, tipo de reclamo, ubicación y canal, y el
  tiempo de resolución como medida.
- **FR-011**: Ambos modelos DEBEN derivarse de la misma carga y contener exactamente el
  mismo conjunto de solicitudes.
- **FR-012**: Los valores ausentes en una dimensión DEBEN tratarse igual en ambos modelos.

**Consultas y benchmark**

- **FR-013**: El sistema DEBE definir un conjunto fijo de al menos 6 consultas analíticas,
  cada una con su pregunta de negocio documentada, que cubra: agregación por período,
  top-N, filtro por dimensión y medida de resolución. Como mínimo incluye:
  - solicitudes por tipo de reclamo y mes, por borough;
  - los 10 tipos de reclamo más frecuentes por código postal con su tiempo medio de
    resolución;
  - tasa de cierre en 30 días por agencia y canal.
- **FR-014**: Cada consulta DEBE expresarse con la misma lógica en los dos modelos.
- **FR-015**: El benchmark DEBE medir cada consulta en cada modelo con al menos 1 ejecución
  de calentamiento descartada y al menos 10 repeticiones medidas, ambas configurables.
- **FR-016**: El benchmark DEBE reportar por consulta y modelo: mediana, percentil 95,
  mínimo, máximo y el factor de diferencia entre modelos sobre la mediana.
- **FR-017**: El benchmark DEBE escribir en `results/` un archivo legible por máquina y un
  resumen legible por humanos, que incluyan volumen de datos, entorno de ejecución, fecha y
  parámetros de medición.
- **FR-018**: El benchmark DEBE negarse a medir si los modelos no contienen el mismo número
  de solicitudes.
- **FR-019**: El informe DEBE declarar si se alcanza el umbral de significancia (SC-003). Si
  no se alcanza, lo indica explícitamente; en ningún caso se modifican datos, consultas o
  configuración para alcanzarlo.
- **FR-020**: El benchmark PUEDE incluir un grupo separado de operaciones transaccionales
  (lectura de una solicitud por identificador y alta de una solicitud), reportado aparte de
  las consultas analíticas.

**Verificación**

- **FR-021**: Tests de integración DEBEN verificar, contra los dos modelos reales, que el
  número de solicitudes y los totales por cada dimensión coinciden.
- **FR-022**: Tests de integración DEBEN verificar que cada consulta del benchmark devuelve
  resultados equivalentes en ambos modelos.
- **FR-023**: Los tests de integración DEBEN poder ejecutarse sobre un volumen reducido sin
  depender de la carga completa.

**Reproducción por el evaluador**

- **FR-024**: Los resultados oficiales, medidos con el perfil completo, DEBEN publicarse en
  `results/` dentro del repositorio, de modo que puedan consultarse sin ejecutar nada.
- **FR-025**: El perfil rápido DEBE ejecutar la misma carga, las mismas consultas y los
  mismos tests que el completo, cambiando únicamente el volumen.
- **FR-026**: Todo informe de resultados DEBE indicar con qué perfil y volumen se generó. El
  umbral de significancia (SC-003) se evalúa solo sobre el perfil completo; un informe del
  perfil rápido DEBE advertir que sus tiempos no son los oficiales.

### Key Entities

- **Solicitud de servicio**: un reclamo o aviso de un ciudadano. Tiene identificador único de
  origen, fecha de creación, fecha de cierre (opcional) y referencias a agencia, tipo de
  reclamo, ubicación, canal y estado.
- **Agencia**: organismo municipal responsable de atender la solicitud.
- **Tipo de reclamo**: categoría de la solicitud, con un descriptor más específico.
- **Ubicación**: borough, código postal y community board donde ocurre el problema.
- **Canal**: medio por el que se registró la solicitud (teléfono, web, móvil u otro).
- **Estado**: situación de la solicitud (abierta, cerrada, etc.).
- **Tiempo**: fecha de creación descompuesta en día, mes, trimestre, año y día de la semana.
- **Tiempo de resolución**: medida derivada, diferencia entre cierre y creación.
- **Consulta de benchmark**: pregunta de negocio con su expresión equivalente en cada modelo.
- **Ejecución de benchmark**: conjunto de mediciones con su entorno, volumen y parámetros.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona con el repositorio y una credencial de la API reproduce carga,
  benchmark y tests siguiendo solo el README, con no más de 5 comandos.
- **SC-002**: Con el perfil completo (5.000.000 de solicitudes), el proceso entero de
  preparación de datos —descarga desde la API y carga en ambos modelos— termina en menos de
  1 hora en un portátil con conexión doméstica.
- **SC-003**: La diferencia se considera significativa si, con el perfil completo, el modelo
  analítico es al menos 3 veces más rápido en la mediana en al menos dos tercios de las
  consultas analíticas.
- **SC-004**: El 100 % de las consultas del benchmark devuelve resultados equivalentes en
  ambos modelos, verificado por los tests de integración.
- **SC-005**: Relanzar una carga completada deja el número de solicitudes sin cambios (0
  duplicados) en ambos modelos.
- **SC-006**: Dos ejecuciones consecutivas del benchmark sobre los mismos datos dan medianas
  que difieren menos de un 20 % por consulta y modelo.
- **SC-007**: El informe de resultados permite a un lector identificar en menos de 1 minuto
  qué modelo gana en cada consulta y por cuánto.
- **SC-008**: Con el perfil rápido (200.000 solicitudes), un evaluador completa carga,
  benchmark y tests de integración en menos de 10 minutos.
- **SC-009**: Un evaluador puede leer los resultados oficiales en el repositorio sin ejecutar
  ningún comando.

## Assumptions

- La fuente es el dataset público NYC 311 Service Requests, accesible con una credencial
  gratuita que el usuario crea y configura en su entorno.
- El corte de datos por defecto son las solicitudes más recientes dentro de un rango de
  fechas de creación cerrado, suficientes para alcanzar el volumen objetivo.
- El benchmark se ejecuta en una sola máquina, sin concurrencia de usuarios; la concurrencia
  queda fuera de alcance.
- Los tiempos se miden de extremo a extremo desde el cliente, incluyendo la recuperación
  completa del resultado.
- Los nombres y la disponibilidad exactos de los campos de la fuente se confirman contra la
  API durante la fase de plan.
- La licencia de uso de los datos se verifica en la fase de plan y se cita en el README.
- El motor analítico concreto, los índices y el formato de los archivos de resultados son
  decisiones del plan, no de este spec.
- Fuera de alcance: interfaz web, despliegue en la nube, actualización incremental en tiempo
  real y análisis geoespacial con coordenadas.
