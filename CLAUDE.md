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

**Semana 1 (29 jul 2026).** Plataforma desplegada y funcionando.

**URL de producción:** https://retailnova-lab.streamlit.app/
**Repositorio:** https://github.com/tgarcmar-lang/retail-transformation-lab

### Hecho
- [x] Estructura de carpetas
- [x] Landing page con selector de filial
- [x] `requirements.txt`, `.gitignore`, configuración de Streamlit
- [x] Repositorio en GitHub y despliegue automático en Streamlit Cloud

### Siguiente
- [ ] Generador de las 5 filiales de RetailNova — **la tarea crítica**
- [ ] Sesión 1: Diagnóstico

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
