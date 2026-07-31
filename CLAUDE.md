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
- Sesión 3: Logística verde y economía circular (balance de materiales,
  jerarquía de residuos, plan de circularidad).
- Asistente de IA que comenta resultados y plantea preguntas.
- Panel del profesor para comparar los cinco grupos.

### NO se construye (decisión vinculante hasta enero de 2027)
Control Tower · Digital Twin · Robotics Studio · Telecommunications Studio ·
Agentes multi-rol · Módulo de Dirección de Proyectos · Gestión del Cambio ·
Comité de Dirección virtual · Otros sectores · Modo Desarrollador ·
Sesiones 4 a 7

Si el usuario pide algo de esta lista, recuérdale que está pospuesto, no descartado.
La inflación de alcance es el principal riesgo de este proyecto.

**La Sesión 3 salió de esta lista el 31 de julio de 2026 por decisión expresa
de Tomás**, que levantó la restricción para poder cubrir la competencia de
logística verde y economía circular del programa. Queda constancia en el
registro de decisiones. Las sesiones 4 a 7 siguen bloqueadas.

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

## Identidad visual

Granate corporativo UCJC: **`#872046`**. Vive en `core/marca.py`, que devuelve
HTML sin importar Streamlit. La portada lleva cabecera institucional (logotipo,
escuela, nombre y cargo), el rótulo *AI Sustainability & Logistics Projects*,
el esquema de las cinco filiales y las cifras del caso, que se leen de los
datos y no están escritas a mano.

El logotipo se incrusta en base64 porque Streamlit no sirve ficheros locales
dentro de un bloque de HTML. Hay **dos tamaños a propósito**: dentro de una
sesión se reenvía el HTML en cada clic, así que allí va el pequeño.

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

- [x] Tutor de guardia (Gemini) en las dos sesiones, sin dependencias nuevas
- [x] Sesión 2 · Descarbonización: simulador de palancas con presupuesto y
      plan descargable
- [x] **Ampliación de la Sesión 2 (30 jul 2026): transporte desagregado y
      alcance 3.** Vía A, doble objetivo.
- [x] Guion del profesor de la Sesión 2 — fuera del repositorio
- [x] **Sesión 3 · Logística verde y economía circular (31 jul 2026).**
      Balance de materiales, jerarquía de residuos, seis palancas y plan
      descargable. Dos tablas de datos nuevas. Guion del profesor incluido.
      **985 pruebas en verde.**

### Siguiente
- [ ] Demo con alumnos en los próximos días. Después, afinar con lo que se
      vea.
- [ ] **Sin validar por Tomás:** los factores del alcance 3 (Sesión 2) y los
      del modelo circular (Sesión 3). Son calibraciones mías, verosímiles
      pero no contrastadas contra ninguna base publicada.
- [ ] **Sin cronometrar:** ninguna de las tres sesiones se ha probado con
      alumnos. Las tres están planificadas a 90 minutos sobre el papel.

## La ampliación de la Sesión 2 (hecha el 30 jul 2026)

Se eligió la **Vía A · doble objetivo**. El 25 % sigue midiéndose sobre
alcances 1 y 2, con su presupuesto y su calibración intactos, y el alcance 3
va aparte, con su propio objetivo y su propio presupuesto. Hay una prueba
(`test_el_objetivo_del_25_sigue_midiendose_sobre_alcances_1_y_2`) que impide
que alguien meta el alcance 3 en el denominador y tumbe la calibración.

### El transporte, desagregado

`rutas` era un solo deslizador con tres conceptos dentro. Ahora son tres
palancas distintas, y las seis de los alcances 1 y 2 quedan así:

| Palanca | Qué decide | Dato que usa |
|---|---|---|
| `refrigerante` | Reconvertir el frío a CO₂ | `refrigerantes.csv` |
| `electrificacion` | Furgonetas eléctricas | `flota.csv` |
| `vacio` | Kilómetros sin carga, suelo del 12 % | `rutas.csv` → `km_en_vacio` |
| `carga` | Ocupación media, techo del 86 % | `rutas.csv` → `ocupacion_media` |
| `consolidacion` | Recogida en tienda, techo del 55 % | `pedidos_online.csv` + `entregas_fallidas` |
| `energia` | Iluminación, frío eficiente, fotovoltaica | `energia.csv` |

`vacio` y `carga` miden cosas distintas y conviene poder decirlo en clase:
un camión puede ir siempre cargado y aun así ir medio vacío. Pasar del 60 %
al 80 % de ocupación no ahorra un 20 % de kilómetros, ahorra un 25 %.

`consolidacion` solo toca la última milla —las furgonetas, no los rígidos— y
rinde más donde fallan más entregas, porque un pedido recogido en el
mostrador no puede fallar. **Madrid es quien más gana con ella**, que es
justo el problema que descubrió en la Sesión 1. Hay prueba que lo fija.

**Recalibrado:** con el mejor plan posible las filiales llegan al 30-36 %
(antes 29-34 %). Sigue cumpliéndose que ninguna palanca suelta le basta a
Madrid, Barcelona ni Bilbao, y que a Valencia y Sevilla el refrigerante casi
les basta.

### El alcance 3

Vive en `core/alcance3.py`. Tres categorías, todas con dato real detrás:
fabricar lo comprado (estimación por gasto sobre `compras.csv`), traerlo
(toneladas × distancia × modo, desde `pais_origen`) y tratar los residuos.

El alcance 3 sale **entre 8 y 24 veces mayor** que los alcances 1 y 2 según
la filial: lo operativo es solo el 4-11 % de la huella real. Es la cifra que
da el susto, y por eso el paso 4 va **después** de que el grupo haya cerrado
su plan y lo haya justificado por escrito. Enseñarlo antes lo convertiría en
un dato más.

Sus tres palancas, con objetivo del 10 % y presupuesto propio (0,45 % de las
ventas):

| Palanca | Qué hace | Papel en la sesión |
|---|---|---|
| `modal` | Bajar del avión al barco la mercancía asiática | La tonelada más barata del caso. **Barcelona es quien más gana**: cierra su dilema en carbono |
| `proveedores` | Programa de medición y mejora con proveedores | La palanca grande: fabricar es la mayor parte del inventario |
| `origen` | Relocalizar compra asiática a Turquía | **La trampa.** Suena a la medida más verde y es la más cara por tonelada |

**La trampa del alcance 3:** gastarse el presupuesto entero en acercar la
cadena se queda por debajo de la mitad del objetivo. Comprar en Turquía
cuesta un 15 % más que comprar en China, y ese sobrecoste se come el
presupuesto. Hay prueba que lo verifica en las cinco filiales.

**Se enseña el defecto del método.** La estimación por gasto tiene una
trampa que el paso 4 explica en voz alta: negociar un descuento del 5 % con
el proveedor baja la huella un 5 % sin que cambie nada en la fábrica. Sirve
para saber dónde mirar, no para reclamar una reducción.

### Lo que se tocó fuera de la Sesión 2

- `datos/retailnova/parametros.py` y el generador: factores de alcance 3.
  **Solo cambió `factores_emision.csv`**; los demás CSV son idénticos byte a
  byte, comprobado con `md5sum` antes y después de regenerar.
- Sesión 1: una línea que admite que falta el alcance 3 y lo emplaza a la
  Sesión 2. Antes el inventario se presentaba como completo sin serlo.
- `core/plan.py`: el plan descargable lleva secciones 4 y 5. **Las dos
  reducciones no se suman en un solo porcentaje**, y hay prueba que lo
  impide: sumarlas sería el error que la sesión intenta desmontar.
- `core/tutor.py`: banco de reserva propio para las dos preguntas nuevas.

## Sesión 2 · cómo está montada

Cuatro pasos, estructura mixta: arranque guiado corto y después simulador
libre. Es la segunda vez que tocan la herramienta.

1. **De dónde partís** — qué es una huella y dónde está la frontera de su
   inventario, más su conclusión de la Sesión 1, que vuelven a introducir a
   mano leyéndola de su informe impreso
2. **Vuestras palancas** — coste por tonelada de cada medida *en su filial*
3. **Vuestro plan** — simulador con presupuesto y plan descargable
4. **Lo que no estabais mirando** — el alcance 3

**Objetivo: −25 %. Presupuesto: 2,5 % de las ventas anuales**, presentado
como plan de inversión a tres años. El modelo vive en `core/palancas.py`.
El paso 4 tiene objetivo y presupuesto propios y vive en `core/alcance3.py`.

**El equilibrio está calibrado y protegido por pruebas.** Con el mejor plan
posible cada filial llega al 30-36 %: el objetivo es alcanzable eligiendo
bien e imposible eligiendo mal. Si alguien toca un coste o el presupuesto y
rompe eso, `tests/test_palancas.py` lo detecta.

| Filial | Palanca más rentable | Detalle |
|---|---|---|
| A · Madrid | Factor de carga, luego recogida en tienda | Ninguna palanca suelta le llega: tiene que combinar |
| B · Barcelona | Factor de carga, luego energía | Igual que Madrid |
| C · Valencia | Refrigerante (1.116 €/t) | Cambiar el R-404A casi le basta |
| D · Sevilla | Refrigerante (1.173 €/t) | Y le queda margen en vacío y en carga |
| E · Bilbao | Recogida en tienda, luego energía | El refrigerante no le sirve: ya migró a CO₂ |

**Las dos trampas del caso:** si Bilbao copia el plan de Valencia, se gasta
1,4 M€ en cambiar un refrigerante que ya cambió y reduce cero. Y en el paso
4, quien se gaste el presupuesto de alcance 3 en acercar la cadena de
suministro se queda por debajo de la mitad de su objetivo. Las dos están
verificadas por pruebas y las dos se avisan en pantalla, pero solo después
de que lo intenten.

## Sesión 3 · cómo está montada

Cuatro pasos, misma mecánica que la Sesión 2. Mide **material**, no carbono, y
eso cambia la lógica: el carbono se evita gastando en tecnología; el material
se evita, sobre todo, no llegando a usarlo.

1. **Qué material movéis** — balance de materiales y jerarquía de residuos
2. **Vuestras palancas** — las seis, ordenadas por coste por tonelada
3. **Vuestro plan** — simulador con presupuesto y plan descargable
4. **La cuenta en euros** — lo mismo con la otra unidad de medida

**Objetivo: recuperar un tercio del material que hoy se pierde.
Presupuesto: 0,8 % de las ventas** a tres años. Vive en `core/circular.py`.

### La idea que sostiene la sesión

`FACTOR_RECICLAJE = 0.55`: de cada tonelada que se manda a reciclar solo
vuelve al ciclo algo más de la mitad. Se pierde en la recogida, en la limpieza
y en la transformación, y lo que sale vale para menos cosas. Por eso la
métrica no es «cuánto reciclas» sino **cuánto material se pierde de verdad**,
y por eso las filiales que reciclan mucho descubren que recirculan poco:
Bilbao recicla el 84 % y recircula el 46 %.

**Reciclar es la palanca más barata en las cinco filiales (1.091 €/t) y en las
cinco es insuficiente:** al máximo posible recupera entre el 4 % y el 14 % de
la pérdida, contra un objetivo del 33 %. Hay prueba que lo fija en las cinco.

### Las seis palancas, por escalón

| Palanca | Escalón | Precio | Papel |
|---|---|---|---|
| `segregacion` | Reciclar | 1.091 €/t | La más barata y la que menos llega. Techo de 15 puntos y máximo del 88 % |
| `embalaje` | Prevenir | 1.683–2.504 €/t | La mayor bolsa de material en cuatro de las cinco filiales |
| `retornable` | Reutilizar | 1.798–3.720 €/t | **Sevilla la tiene más barata**: sus camiones ya vuelven vacíos |
| `merma` | Prevenir | 2.064–2.694 €/t | **La de Valencia**: 1.056 t y 4,46 M€ al año |
| `reacondicionado` | Reutilizar | 4.644–6.062 €/t | Convierte residuo en ingreso, pero es intensiva en mano de obra |
| `devoluciones` | Prevenir | 4.261–8.617 €/t | La peor en toneladas y de las mejores en euros |

**Calibración:** con el mejor plan las filiales llegan al 35,5–45,2 % contra
un objetivo del 33 %. Ninguna palanca suelta resuelve la sesión en ninguna
filial, y sin ninguna palanca de prevención no se llega ni gastándolo todo.

| Filial | Su palanca | Por qué |
|---|---|---|
| A · Madrid | Envase, y devoluciones en euros | 336.017 devoluciones al año le cuestan 1,61 M€ de gestión |
| B · Barcelona | Envase | Mayor sobreembalaje del grupo (×1,185): la cadena asiática otra vez |
| C · Valencia | Merma | Única filial donde la merma pesa más que el envase |
| D · Sevilla | Envase retornable | El 34 % de vacío paga el circuito de retorno. Logística verde y circular se tocan |
| E · Bilbao | Ninguna barata | Ya recicla el 84 %: solo le quedan 4 puntos frente a los 15 de los demás |

### Las dos trampas

1. **Resolverlo reciclando.** Es lo primero que intentan todos porque es lo
   más barato. La interfaz les avisa cuando su plan está casi todo en los
   escalones de abajo, pero solo después de haberlo montado.
2. **Descartar las devoluciones por caras.** La tabla del paso 2 invita a
   ello; el paso 4 enseña lo que cuestan hoy en dinero. Por eso el paso 4 va
   al final, igual que el alcance 3 en la Sesión 2.

### Los datos nuevos

`devoluciones.csv` y `envases.csv`, con semillas propias (20 y 21). Se derivan
de tablas existentes —las devoluciones de `pedidos_online.csv`, los envases
del cartón y el plástico de `residuos.csv`— para que no puedan contradecirse.
**Los quince CSV anteriores quedaron idénticos byte a byte**, comprobado con
`md5sum`, así que no se movió ninguna cifra de los guiones ya impresos.

## El tutor de guardia

Vive en `core/tutor.py`. Lee lo que ha escrito el grupo y devuelve **una
pregunta**. El profesor no puede estar en cinco mesas a la vez; esto cubre
los huecos.

**Tres reglas que no se negocian:**

1. **Nunca da la respuesta.** El contexto que se le envía contiene solo
   cifras que el alumno ya tiene en pantalla, nunca el diagnóstico de la
   filial. Hay pruebas que lo verifican.
2. **Nunca para la clase.** Sin clave, sin cuota, sin red o con cualquier
   fallo, devuelve una pregunta del banco escrito a mano en `RESERVA`. El
   alumno no ve jamás un error.
3. **No añade dependencias.** Se llama a la API REST con `requests`, que ya
   viene con Streamlit. `requirements.txt` no se ha tocado.

Además: se prueban varios modelos en orden (los nombres de Google se retiran),
la respuesta se descarta si no es una pregunta corta, y hay un límite de 12
consultas por grupo — pedagógico, no de cuota: sin límite, el ejercicio se
convierte en pulsar hasta que salga la respuesta.

**Clave:** `[gemini] api_key` en `st.secrets`. En Streamlit Cloud se pega en
`Settings → Secrets`, nunca en el repositorio, que es público. Ver
`.streamlit/secrets.toml.ejemplo`.

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
- **2026-07-29** — Panel del profesor **descartado**, no aplazado. La
  comparación de las cinco filiales ya está en el paso 5 y se puede proyectar
  desde cualquier grupo. Lo único que aportaría de verdad —ver lo que han
  escrito los alumnos— depende de la persistencia, no del panel.
- **2026-07-29** — Persistencia **descartada también para la Sesión 2**. Cada
  grupo llegará con su informe de la Sesión 1 y volverá a introducir su
  conclusión, que es lo que hace un consultor con el entregable de la fase
  anterior. Nos ahorra Supabase entero.
- **2026-07-29** — Tutor de guardia construido llamando a la API REST de
  Gemini en lugar de con el SDK de Google. Motivo: `requests` ya viene con
  Streamlit, así que no se toca `requirements.txt` y desaparece el riesgo de
  que una dependencia nueva tumbe el despliegue.
- **2026-07-29** — Sesión 2 con objetivo fijo del 25 % y presupuesto cerrado.
  Sin restricción económica el ejercicio sería trivial: activar todo hasta
  llegar. El objetivo fijo además hace comparables los cinco planes.
- **2026-07-29** — Presupuesto subido del 1,2 % al 2,5 % de las ventas tras
  calibrar: con el 1,2 % ninguna filial pasaba del 21 % y el objetivo era
  inalcanzable. Se presenta como plan de inversión a tres años para que la
  cifra sea creíble.
- **2026-07-29** — Sesión 2 mixta y no guiada por pasos como la 1: ya conocen
  la herramienta, y repetir la misma mecánica se les haría infantil.
- **2026-07-29** — El tutor solo pregunta, nunca responde. Si el modelo
  devuelve una afirmación, una parrafada o varias preguntas, se descarta y
  sale una del banco escrito a mano. Regalar el hallazgo destruiría la sesión.
- **2026-07-30** — Alcance 3 con **doble objetivo** (Vía A) y no inventario
  único. El 25 % está calibrado sobre alcances 1 y 2; meter el alcance 3 en
  el denominador lo habría vuelto inalcanzable y habría invalidado el guion
  del profesor a seis semanas de la primera clase. Además es lo que hacen
  las empresas reales. Hay una prueba que impide que alguien lo junte.
- **2026-07-30** — El paso del alcance 3 va **al final**, después de que el
  grupo haya cerrado y justificado su plan. Puesto antes sería un dato más;
  puesto después corrige una conclusión que acaban de defender por escrito.
- **2026-07-30** — El transporte se parte en tres palancas (`vacio`, `carga`,
  `consolidacion`). Con un solo deslizador el alumno no distinguía qué
  estaba decidiendo, y dos de los tres conceptos ni siquiera se calculaban
  pese a tener el dato generado.
- **2026-07-30** — `consolidacion` se cobra por tienda equipada y no sobre
  la venta online desviada. Con el coste sobre ventas, Madrid —que es quien
  tiene el problema de última milla— salía penalizado por vender mucho
  online, y la palanca que cierra su hallazgo de la Sesión 1 le resultaba
  cara. Por tienda es además lo que de verdad se compra: infraestructura.
- **2026-07-30** — El alcance 3 se estima **por gasto**, y la sesión enseña
  el defecto del método en voz alta: negociar un descuento baja la huella
  sin cambiar nada físico. Ocultarlo habría enseñado a confiar en una cifra
  que no lo merece.
- **2026-07-30** — El plan descargable **no suma las dos reducciones** en un
  solo porcentaje. Hay una prueba que lo impide: sumarlas sería exactamente
  el error que la sesión intenta desmontar.
- **2026-07-30** — Los factores de alcance 3 entran por `parametros.py` y el
  generador, no a mano en el CSV. Regenerar solo cambió `factores_emision.csv`;
  el resto quedó idéntico byte a byte (comprobado con `md5sum`), así que las
  cifras que ya conocía Tomás no se movieron.
- **2026-07-31** — **Levantada la restricción sobre la Sesión 3.** Decisión
  expresa de Tomás, que necesitaba cubrir la competencia de logística verde y
  economía circular del programa. Se le recordó la decisión vinculante del 29
  de julio y la mantuvo. Las sesiones 4 a 7 siguen bloqueadas.
- **2026-07-31** — La Sesión 3 mide **material** y no carbono, con un factor
  de recirculación del 0,55 para el reciclaje. Sin ese factor, reciclar
  equivaldría a prevenir y la jerarquía de residuos —que es el contenido de
  la sesión— no tendría ninguna consecuencia numérica.
- **2026-07-31** — El objetivo se fija sobre **la pérdida de material** y no
  sobre el residuo generado ni sobre la tasa de reciclaje. Sobre el residuo
  generado, reciclar no serviría de nada; sobre la tasa de reciclaje, la
  sesión premiaría justo lo que quiere cuestionar.
- **2026-07-31** — `segregacion` se dejó siendo **la palanca más barata a
  propósito**. Era tentador encarecerla para que nadie la eligiera primero,
  pero eso habría falseado el caso: en la realidad reciclar es lo más barato,
  y el aprendizaje está en descubrir que aun así no basta.
- **2026-07-31** — Las dos tablas nuevas se **derivan de las existentes** en
  vez de generarse por separado, y con semillas propias (20 y 21). Así una
  filial no puede devolver más de lo que vendió, el envase no puede
  contradecir al residuo recogido, y los quince CSV anteriores no se mueven.
- **2026-07-31** — El paso de los euros va **al final**, como el alcance 3 en
  la Sesión 2. Es la misma estructura deliberada: decidir con una unidad,
  comprometerse por escrito y después descubrir que la otra unidad ordena las
  cosas de otra manera.
