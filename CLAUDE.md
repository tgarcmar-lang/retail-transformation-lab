# Retail Transformation Lab — Estado del proyecto

> Este fichero es la memoria del proyecto. Léelo entero antes de trabajar.
> Actualízalo al final de cada sesión de trabajo.

## Qué es esto

Plataforma web docente para la Escuela Politécnica (UCJC). Cinco grupos de alumnos
dirigen cinco filiales de una empresa ficticia de retail (RetailNova Europa) y toman
decisiones sobre sostenibilidad, logística y operaciones. Cada sesión de clase
desbloquea un módulo nuevo. Las decisiones de una sesión condicionan la siguiente.

**Responsable:** Tomás (director de la Escuela Politécnica). No programa.
Valida contenido, KPIs y sentido pedagógico. No le pidas revisar código.

## Fechas

- **8 de septiembre de 2026** — primera clase con alumnos. Fecha dura.
- Objetivo para esa fecha: **Sesión 1 (Diagnóstico) funcionando en producción.**
- Objetivo para octubre: Sesión 2 (Descarbonización).

## Alcance del curso 2026-27

### Se construye
- Una sola aplicación Streamlit, desplegada en Streamlit Community Cloud.
- RetailNova Europa con 5 filiales: Madrid, Barcelona, Valencia, Sevilla, Bilbao.
- Sesión 1: Diagnóstico (explorar la empresa, KPIs, informe).
- Sesión 2: Descarbonización (huella de carbono, simulación, plan de acción).
- Asistente de IA que comenta resultados y plantea preguntas.
- Panel del profesor para comparar los cinco grupos.

### NO se construye (decisión vinculante hasta enero de 2027)
Control Tower · Digital Twin · Robotics Studio · Telecommunications Studio ·
Agentes multi-rol · Módulo de Dirección de Proyectos · Gestión del Cambio ·
Comité de Dirección virtual · Otros sectores · Modo Desarrollador ·
Sesiones 3 a 7

Si el usuario pide algo de esta lista, recuérdale que está pospuesto, no descartado.
La inflación de alcance es el principal riesgo de este proyecto.

## Decisiones técnicas cerradas

| Tema | Decisión | Por qué |
|---|---|---|
| Framework | Streamlit | Gratis, sin instalación para el alumno, rápido de construir |
| Alojamiento | Streamlit Community Cloud | Gratis, se actualiza con cada push a GitHub |
| Repositorio | GitHub (`retail-transformation-lab`) | Único origen de verdad |
| IA | Google Gemini, cuota gratuita | Sin coste; clave en `secrets.toml`, nunca en el código |
| Persistencia | Aplazada. Sesión 1 no la necesita. Cuando haga falta: Supabase | SQLite en GitHub NO funciona: el disco de Streamlit Cloud es efímero |
| Datos | Sintéticos, generados por `datos/retailnova/generador.py`, versionados como CSV | Reproducibles y revisables por el profesor |

## Restricciones de producción (respetar por diseño)

- **~1 GB de RAM por app.** Datasets por debajo de 50 MB. Usar `@st.cache_data`.
- **La app se duerme** tras días sin uso. Abrirla 10 min antes de clase.
- **Concurrencia limitada.** Regla de aula: un ordenador por grupo, no por alumno.
- **Cuota de IA limitada.** Cachear respuestas. Si se agota, mostrar análisis
  precalculado, nunca un error. La clase no se para jamás por un fallo de cuota.

## Convenciones

- Todo el texto de la interfaz **en español**, incluidos mensajes de error.
- Código y nombres de variables en español también (el mantenedor futuro será
  un alumno de TFG español).
- `core/` = lógica reutilizable, sin Streamlit dentro. `modulos/` = interfaz por sesión.
  Esta separación es lo que permitirá construir las sesiones 3-7 rápido. No la rompas.
- Nada de secretos en el código. Usar `st.secrets`.
- Cada función de cálculo con al menos un test en `tests/`.

## Estado actual

**Semana 1 (29 jul 2026).** Plataforma desplegada y datos del caso generados.

**URL de producción:** https://retailnova-lab.streamlit.app/
**Repositorio:** https://github.com/tgarcmar-lang/retail-transformation-lab

### Hecho
- [x] Estructura de carpetas
- [x] Landing page con selector de filial
- [x] `requirements.txt`, `.gitignore`, configuración de Streamlit
- [x] Repositorio en GitHub y despliegue automático en Streamlit Cloud
- [x] Generador de datos de las 5 filiales (`datos/retailnova/`), validado
      con Tomás y cubierto por pruebas
- [x] Sesión 1 · Diagnóstico: recorrido guiado de 5 pasos e informe
      descargable. 240 pruebas en verde, incluido el recorrido completo de
      los cinco grupos con el banco de pruebas de Streamlit

- [x] Guion del profesor para la Sesión 1 — **vive fuera del repositorio**,
      en `C:\Proyectos\retail-lab-profesor`

### Siguiente
- [ ] Asistente de IA (Gemini) que comente los resultados
- [ ] Panel del profesor
- [ ] Sesión 2: Descarbonización (objetivo: octubre)

## Sesión 1 · cómo está montada

Cinco pasos, unos 60-75 minutos de clase, guiados (no exploración libre: es
la primera vez que los alumnos tocan la herramienta).

1. **Tu filial** — retrato y parque de tiendas
2. **Cómo vende** — estacionalidad, categorías y canal online
3. **Cómo opera** — reparto, proveedores e inventario
4. **Qué emite** — energía, combustible y huella de carbono
5. **Tu diagnóstico** — comparación con las otras cuatro filiales e informe

Cada paso termina con una pregunta abierta. Las respuestas se guardan en
`st.session_state` y salen impresas en el informe que descarga el grupo.

**Decisión sobre el informe:** HTML autocontenido, no Word ni PDF. Cero
dependencias nuevas, se imprime a PDF con Ctrl+P y no puede romper el
despliegue. Está en `core/informe.py`.

**Cada filial lidera en algo y falla en algo distinto.** Está comprobado por
pruebas, porque si dos grupos llegasen al mismo hallazgo la puesta en común
perdería sentido, y un grupo que no lidera en nada se desmotiva.

| Grupo | Lidera en | Su problema |
|---|---|---|
| A · Madrid | Ventas, €/m², cuota online | Entregas fallidas: la última milla urbana |
| B · Barcelona | Margen bruto | Plazo de entrega y stock inmovilizado |
| C · Valencia | Puntualidad de proveedores | Energía del frío y merma |
| D · Sevilla | Plazo de entrega | Kilómetros en vacío y gasóleo |
| E · Bilbao | Casi todos los ratios | No tiene escala: es la más pequeña |

Barcelona es el caso más interesante: compra más barato **porque** compra en
Asia, y paga ese margen con plazos del doble y stock parado. No tiene un
defecto, tiene un dilema.

## El caso: RetailNova Europa

Operador de **grandes almacenes polivalentes**, no una cadena de supermercados.
El núcleo del negocio es el textil y los bienes duraderos.

- Moda y Belleza 40 % · Hogar y Electrónica 36 % · Alimentación 24 %
- 134 puntos de venta en cuatro formatos: 8 grandes almacenes, 22 hipermercados,
  63 tiendas especializadas y 41 de conveniencia
- 1.149 M€ de ventas, 5.539 empleados, 451 vehículos, 9 centros logísticos
- 35.130 t CO₂e al año (50 % electricidad, 26 % gasóleo, 20 % refrigerantes)

Cada filial tiene un problema dominante que su grupo debe descubrir en los datos:
Madrid la última milla urbana, Barcelona los plazos de la cadena asiática,
Valencia la energía y el R-404A, Sevilla los kilómetros en vacío, Bilbao la falta
de escala. Ver `datos/retailnova/README.md`.

**Regla dura de los datos:** las cifras del caso viven en
`datos/retailnova/parametros.py` y en ningún otro sitio. Los CSV se regeneran,
nunca se editan a mano. La cuota de comercio electrónico se deriva del mix de
categorías: no se fija a mano, porque así es imposible que salga un número
inverosímil.

## Notas de despliegue (aprendidas a golpes)

- Streamlit Cloud ejecuta **Python 3.14**. No fijar versiones exactas de
  librerías: si no existe rueda precompilada para esa versión, intenta compilar
  desde el código fuente y falla (`pillow` no encuentra `zlib`). Usar `>=`.
- El despliegue se actualiza solo con cada push a `main`. No hay que tocar nada
  en la web de Streamlit.
- El registro del despliegue está en `Manage app`, abajo a la derecha.

## Registro de decisiones

- **2026-07-29** — Alcance recortado de 15 aplicaciones a 1 plataforma con 2 sesiones.
  El plan original (conversación previa con ChatGPT) proponía un ecosistema de 15 apps
  y 1.000 páginas de especificación. Inviable en 6 semanas y sin equipo.
- **2026-07-29** — Descartado SQLite-en-GitHub para persistencia: no funciona en
  Streamlit Cloud por sistema de ficheros efímero.
- **2026-07-29** — Persistencia aplazada: la Sesión 1 no la necesita.
- **2026-07-29** — RetailNova definida como operador de grandes almacenes, no
  como cadena de alimentación. Corrección de Tomás. Obligó a rehacer el parque
  de tiendas (cuatro formatos en vez de uno) y a multiplicar por cinco la
  energía por edificio.
- **2026-07-29** — Comercio electrónico derivado del mix de categorías en lugar
  de fijado a mano. El 38 % inicial de Madrid era inverosímil: la alimentación
  online en España está en el 3-5 %. Madrid queda en el 25 %.
- **2026-07-29** — Datos: 24 meses (2024-2025), granularidad diaria por tienda,
  incluyendo ya las variables ambientales de la Sesión 2. Regenerar en octubre
  habría cambiado números que los alumnos ya habrían usado en septiembre.
- **2026-07-29** — Sesión 1 guiada por pasos, no exploración libre. Con la
  exploración libre un grupo puede quedarse en blanco y perder la sesión entera.
- **2026-07-29** — Informe en HTML y no en Word ni PDF: no añade dependencias,
  y cada dependencia nueva es un riesgo de despliegue (ya nos pasó con `pillow`).
- **2026-07-29** — Añadido `compras.csv` y el coste de mercancía por origen.
  Sin ellos el grupo B no tenía forma de descubrir su problema en los datos,
  ni de ver que su margen depende justamente de lo que se lo causa.
- **2026-07-29** — Panel del profesor aplazado. Prioridad: que la Sesión 1
  funcione impecablemente el día 8.
- **2026-07-29** — Guion del profesor en Word y no en Markdown: se imprime,
  se anota y se lleva al aula.
- **2026-07-29** — **El material del profesor no entra en el repositorio.**
  El repositorio es público (requisito del despliegue gratuito) y el guion
  lleva escrito el hallazgo de cada filial. Vive en
  `C:\Proyectos\retail-lab-profesor`, junto al script que lo genera, y
  `.gitignore` bloquea `docs/`, `guion*` y `*.docx` por si acaso.
  Nunca llegó a subirse: no hay que limpiar el historial.
- **2026-07-29** — Asistente de IA aplazado a después de la Sesión 1. El texto
  de apoyo (pistas, avisos, explicaciones) está escrito a mano en el módulo:
  funciona sin cuota, sin clave y sin conexión a Google.
