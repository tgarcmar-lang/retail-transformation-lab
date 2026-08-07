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
- Sesión 4: Medición, reporting y estrategia ESG (doble materialidad,
  indicadores, memoria de sostenibilidad verificada).
- Sesión 5: Ejecución del plan con métodos ágiles (backlog, sprints,
  capacidad, contratiempos y enfoque híbrido).
- Sesión 6: Seguimiento con Kanban y enfoques híbridos (límite de trabajo en
  curso, ley de Little, flujo acumulado).
- Sesión 7: Gestión del cambio (mapa de actores, adopción y la brecha entre
  entregar y cambiar). Cierra el curso.
- Asistente de IA que comenta resultados y plantea preguntas.
- Panel del profesor para comparar los cinco grupos.

### NO se construye (decisión vinculante hasta enero de 2027)
Control Tower · Digital Twin · Robotics Studio · Telecommunications Studio ·
Agentes multi-rol · Módulo de Dirección de Proyectos · Gestión del Cambio ·
Comité de Dirección virtual · Otros sectores · Modo Desarrollador

Si el usuario pide algo de esta lista, recuérdale que está pospuesto, no descartado.
La inflación de alcance es el principal riesgo de este proyecto.

**Las sesiones 3 a 6 salieron de esta lista el 31 de julio de 2026 por
decisión expresa de Tomás**, que levantó la restricción para cubrir
cuatro competencias del programa: logística verde y economía circular,
medición y reporting ESG, ejecución con métodos ágiles y seguimiento con
Kanban e híbridos. En cada caso se le recordó la decisión vinculante del 29
de julio y la mantuvo. Queda constancia en el registro de decisiones. **La
Sesión 7 se construyó el 7 de agosto**, después de la primera prueba con
alumnos. Ya no queda nada bloqueado del alcance original.

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
- [x] **Sesión 4 · Medición, reporting y estrategia ESG (31 jul 2026).**
      Doble materialidad calculada desde los datos, catálogo de 25
      indicadores con su estándar, cinco tentaciones de greenwashing y
      memoria verificada. Datos sociales nuevos. Guion del profesor incluido.
- [x] **Sesión 5 · Ejecución del plan (31 jul 2026).** Backlog derivado de
      las palancas, seis sprints con capacidad insuficiente, dependencias y
      diez contratiempos fijos. Guion del profesor incluido.
- [x] **Sesión 6 · Seguimiento con Kanban (31 jul 2026).** Tablero de cuatro
      columnas, límite de trabajo en curso con óptimo distinto por filial,
      ley de Little comprobada y sistema híbrido. Guion del profesor
      incluido.
- [x] **Tutor de guardia reabierto (7 ago 2026), tras la primera prueba con
      alumnos.** Tres modos: explicar, decir dónde mirar y preguntar. Banco
      de 30 conceptos escrito a mano.
- [x] **Sesión 7 · Gestión del cambio (7 ago 2026).** Mapa de actores,
      dependencia conductual por iniciativa, seis palancas de cambio y la
      brecha entre entregar y adoptar. Documento de cierre del curso.
      **1.805 pruebas en verde.**

### Siguiente
- [ ] **Guion del profesor de la Sesión 7.** Es lo único que falta para que
      el curso esté completo. Los seis anteriores están en
      `C:\Proyectos\retail-lab-profesor`.
- [ ] **Sin validar por Tomás:** los factores del alcance 3 (Sesión 2) y los
      del modelo circular (Sesión 3). Son calibraciones mías, verosímiles
      pero no contrastadas contra ninguna base publicada.
- [ ] **Sin cronometrar:** las siete siguen planificadas a 90 minutos sobre
      el papel. La prueba de agosto no midió tiempos.
- [ ] **Caduca solo:** el contenido normativo de la Sesión 4 (CSRD, ESRS,
      SBTi). Verificar antes de cada curso. Es lo único del proyecto que se
      queda obsoleto sin que nadie toque nada.

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

## Sesión 4 · cómo está montada

Cuatro pasos, pero **la mecánica cambia**. En las sesiones 2 y 3 había un
presupuesto y un óptimo que encontrar. Aquí no hay óptimo: hay criterio, y hay
una firma debajo. La restricción no es el dinero, es que la memoria resista
una revisión.

1. **A quién hay que contárselo** — la CSRD tras el Ómnibus y el mapa de
   estándares
2. **Qué es material** — la matriz de doble materialidad de su filial
3. **Qué publicáis** — eligen indicadores con límite y toman cinco decisiones
   de presentación
4. **La revisión** — el verificador devuelve una opinión y la memoria se
   descarga con las salvedades dentro

Vive en `core/reporting.py`, y el documento en `core/memoria.py`.

### Las dos ideas

**Doble materialidad.** Un asunto es material por impacto o por consecuencias
financieras, y **basta con uno**: es una unión, no una intersección. La matriz
**se calcula con los datos del caso**, así que ningún grupo puede copiar la
del vecino.

**Se puede engañar sin decir una cifra falsa.** Las cinco tentaciones del paso
3 son todas literalmente ciertas. Tres son hallazgo grave y dos, salvedad:

| Tentación | Por qué engaña | Gravedad |
|---|---|---|
| Sumar el 25 % y el 10 % | Dos inventarios, dos denominadores. El SBTi v2.0 exige separarlos | Grave |
| Publicar la huella sin declarar su frontera | La cifra deja de ser interpretable y comparable | Grave |
| Omitir un asunto material | Es lo que detecta la cobertura | Grave |
| Dar el alcance 3 sin decir el método | Está estimado por gasto | Salvedad |
| Destacar la tasa de reciclaje | Más de 30 puntos por encima de la circularidad | Salvedad |
| Publicar solo cifras absolutas | Bajar vendiendo menos no es mejorar | Salvedad |

### El error conceptual que hay que corregir en clase

**Materialidad no es desempeño.** Casi todos los grupos creen que un asunto es
material si lo hacen mal. La escala se calcula **contra la media** y no de
mínimo a máximo justo por eso: con la otra escala, Madrid —la más eficiente
por millón vendido— se habría quedado sin asuntos materiales, y eso es falso.
El transporte es material en una filial que mueve mucha mercancía aunque la
mueva bien. Hay prueba que lo fija.

Además, **toda filial informa de al menos cuatro asuntos** (`MINIMO_ASUNTOS`),
aunque ninguno pase el umbral. Una memoria que dijera «no tenemos asuntos
materiales» no la firmaría nadie.

| Filial | Sus asuntos materiales | Lo que enseña |
|---|---|---|
| A · Madrid | Cadena de valor, trabajo en la cadena, empleo, gobernanza | La más eficiente del grupo y tiene cuatro asuntos: desmonta el error conceptual |
| B · Barcelona | Trabajo en la cadena (4,6 sobre 5), cadena de valor, gobernanza, envase | Compra el 48 % en países de riesgo y evalúa al 14 % de sus proveedores |
| C · Valencia | Gases fluorados y merma (5 sobre 5), emisiones propias, empleo, seguridad | Cinco asuntos y diez indicadores de límite: obliga a priorizar |
| D · Sevilla | Emisiones propias, transporte, gases fluorados, seguridad | Única filial con el transporte material. 148 g CO₂e/t·km, lo peor |
| E · Bilbao | Cadena de valor, envase, trabajo en la cadena, gobernanza | No supera el umbral en nada: informa por el suelo de cuatro asuntos |

**Barcelona y Bilbao acaban con el mismo conjunto por caminos opuestos**: una
porque compra mal, la otra porque opera tan bien que solo le queda la cadena
de valor. Es la mejor comparación de la puesta en común y está aprovechada en
el guion.

### Los estándares, y su fecha de caducidad

Anclas de la sesión: **ISO 14083:2023** (sobre el GLEC Framework v3.0) para
transporte y logística, y los **ESRS** de la CSRD como marco obligatorio.
GHG Protocol, GRI y SBTi se citan y se sitúan.

**Comprobado por búsqueda web el 31 de julio de 2026:**

- **Paquete Ómnibus I** (publicado en febrero de 2026): las empresas obligadas
  por la CSRD bajan de unas 50.000 a unas 5.000, los ESRS pierden hasta la
  mitad de sus puntos de dato y el nuevo perímetro se aplica desde el 1 de
  enero de 2027. RetailNova, con 1.149 M€ y 5.539 empleados, **sigue dentro**.
- **SBTi Corporate Net-Zero Standard v2.0** (final, junio de 2026, obligatorio
  para nuevas validaciones desde 2028): **separa los objetivos de alcances 1 y
  2 de los de alcance 3**, que es exactamente la Vía A de la Sesión 2.

**Esto es lo único del proyecto que caduca solo.** Verificarlo antes de cada
curso.

### Los datos nuevos

`plantilla.csv`, con semilla propia (22): empleados, temporalidad, rotación,
accidentes, formación, brecha salarial y mujeres en dirección. Sin dato
social, «ESG» sería solo la E y cuatro de las cinco filiales no tendrían
asuntos sociales que declarar. **Los diecisiete CSV anteriores quedaron
idénticos byte a byte.**

### Nota de rendimiento

`matriz_materialidad` recorre las cinco filiales enteras y cuesta casi un
segundo. Está cacheada con `lru_cache`, y `core.datos.registrar_cache` permite
que `limpiar_cache()` la vacíe junto con las demás sin crear importaciones
circulares. Sin esa caché, la suite de pruebas no terminaba.

## Sesión 5 · cómo está montada

Cuatro pasos. La mecánica vuelve a cambiar: aquí no se decide **qué** hacer
—eso está decidido en las sesiones 2, 3 y 4— sino **en qué orden** y con qué
consecuencias.

1. **Qué hay que ejecutar** — el backlog y la clasificación predictivo/iterativo
2. **Vuestros sprints** — reparto entre seis sprints con capacidad insuficiente
3. **Lo que no estaba en el plan** — los contratiempos de su filial
4. **La retrospectiva** — curva de entrega y acta descargable

Vive en `core/proyecto.py`, y el documento en `core/acta.py`.

### El backlog no está escrito a mano

Cada iniciativa nace de una palanca real: el esfuerzo se deriva del coste
(`EUROS_POR_PUNTO = 120.000`) y el valor, del porcentaje del objetivo que
aporta. Se añaden dos iniciativas de la Sesión 4 —el sistema de medición y la
evaluación de proveedores— que **no reducen ni una tonelada** y sin las cuales
no hay memoria que verificar. Son las primeras que los grupos quieren quitar.

**Esto resolvió el problema de la persistencia.** Un backlog con historial de
sprints no se puede copiar a mano entre clases, y era la primera vez que la
decisión de no tener persistencia hacía daño. Generándolo desde el caso, un
grupo que faltó a una sesión puede hacer esta igual.

### Las dos ideas

**No todo se gestiona igual.** Cambiar el refrigerante es una obra: proveedor,
permiso y fecha. El programa de proveedores es iterativo: nadie sabe qué
funciona hasta probarlo. `ENFOQUE_PALANCA` clasifica las doce palancas con su
razón escrita. Entre el 65 % y el 78 % del esfuerzo es predictivo según la
filial. **Distinguirlo es la competencia**, y es lo que el temario llama
enfoque híbrido.

**Lo ágil no hace ir más rápido: hace enterarse antes.** Priorizar por valor
entrega el 84-91 % del valor; empezar por lo más grande, el 13-50 %. Y sobre
todo entrega antes: quien tiene algo en la calle en el sprint 2 puede
defenderlo cuando llega el recorte.

### La calibración

| Filial | Esfuerzo | Capacidad/sprint | Sprints que haría falta |
|---|---|---|---|
| A · Madrid | 187 | 24,9 | 7,5 |
| B · Barcelona | 132 | 16,8 | 7,9 |
| C · Valencia | 133 | 13,3 | 10,0 |
| D · Sevilla | 101 | 10,1 | 10,0 |
| E · Bilbao | 55 | 7,0 | 7,9 |

**A nadie le cabe todo, y es la premisa.** La capacidad se calcula sobre el
propio backlog y se modula por empleados por punto de esfuerzo: Valencia y
Sevilla arrastran inversiones grandes con plantillas pequeñas y van más
justas, que es exactamente su situación real.

Las iniciativas grandes **ocupan varios sprints y no entregan nada hasta que
terminan**. La de energía de Madrid son 67 puntos sobre una capacidad de 24,9:
casi tres sprints sin enseñar nada. Es lo que hace visible el coste de empezar
por lo grande, y también el trabajo que queda a medias.

### Los diez contratiempos

Fijos y no aleatorios, para que los cinco grupos sean comparables y el guion
pueda anticiparlos. Uno por filial en la primera mitad y otro en la segunda.
Los más instructivos: a Sevilla se le va el jefe de tráfico **en el sprint 1**,
antes de haber entregado nada; a Valencia se le retrasa el instalador de CO₂,
que es su iniciativa más rentable y la más rígida; y a Bilbao le llega un
recorte del 20 % y una petición de Madrid para copiar su modelo — ninguno de
los dos es un fallo, y los dos consumen capacidad.

### Nota de rendimiento

`backlog` recorre las palancas de dos sesiones enteras y cuesta un segundo.
Está cacheado con `lru_cache` y registrado en `core.datos.registrar_cache`,
igual que la matriz de materialidad de la Sesión 4.

## Sesión 6 · cómo está montada

Cuatro pasos. La Sesión 5 repartía el trabajo en cajas de tiempo; esta lo
deja fluir y se ocupa de **seguirlo**.

1. **El tablero** — cuatro columnas, y la que importa es «Bloqueado»
2. **El límite de trabajo en curso** — el experimento que da la vuelta a la
   intuición
3. **El sistema híbrido** — qué va al tablero y qué se compromete con fecha
4. **El seguimiento** — flujo acumulado, tiempo de ciclo e informe

Vive en `core/kanban.py`, y el documento en `core/informe_seguimiento.py`.
Reutiliza el backlog y la capacidad de la Sesión 5: es el mismo proyecto
mirado con otra lente, y la capacidad semanal es la mitad de la del sprint.

### La idea, que tiene dos mitades contradictorias

**Abrir más cosas no termina más cosas.** La capacidad se reparte y la
multitarea cuesta un 7 % de eficiencia por tarea abierta de más.

**Pero el mínimo tampoco es la respuesta**, y esto es lo que casi ningún
curso de Kanban dice. Toda iniciativa espera a un tercero cuando se abre —dos
semanas las obras, una los programas— y mientras espera **ocupa un hueco del
tablero**. Con una sola tarea abierta, el equipo se para. Con WIP 1 las cinco
filiales entregan 3 iniciativas de 14.

**El óptimo está en medio y no es el mismo en todas.** Hay prueba que impide
que caiga en cualquiera de los dos extremos.

| Filial | Óptimo | Capacidad semanal | WIP 1 | Óptimo | WIP 10 |
|---|---|---|---|---|---|
| A · Madrid | 4 | 12,45 | 13 de 40 | 23 | 13 |
| B · Barcelona | 5 | 8,40 | 10 de 39 | 23 | 10 |
| C · Valencia | 3 | 6,65 | 12 de 45 | 21 | **2** |
| D · Sevilla | 3 | 5,05 | 11 de 43 | 19 | 7 |
| E · Bilbao | 5 | 3,50 | 9 de 33 | 18 | 7 |

En Madrid y Barcelona **los dos extremos entregan lo mismo** por motivos
opuestos: es la campana perfecta. Valencia es el caso extremo: con diez
tareas abiertas entrega 2 puntos de valor de 45 con el equipo trabajando a
tope las doce semanas.

### La ley de Little

Tiempo de ciclo = trabajo en curso ÷ ritmo de entrega. Se comprueba sobre los
propios números del ejercicio y **cuadra con un 6-15 % de desviación en el
óptimo** de cada filial. Donde se desvía es porque el sistema no está en
régimen estable: al terminar las doce semanas quedan tareas abiertas, y el
módulo lo dice en voz alta. Saber cuándo no se aplica una herramienta vale
tanto como saber usarla.

### El sistema híbrido

Es la parte que conecta con la competencia del temario. El grupo reparte su
backlog entre lo que va al tablero y lo que se compromete con fecha, y cada
mitad se mide con un indicador distinto: tiempo de ciclo una, puntualidad la
otra. La aplicación detecta los dos errores:

- **Obras en el tablero de flujo**: esperan al proveedor ocupando un hueco de
  WIP y no ganan nada, porque su fecha ya estaba comprometida con un tercero.
- **Fecha sobre lo iterativo**: se compromete una cifra que nadie puede saber
  y que después todos repiten en el comité.

### Por qué el bloqueo se dispara al abrir la tarea

La primera versión bloqueaba las tareas al llegar a cierto porcentaje de
avance, y no funcionaba: las tareas pequeñas terminaban antes de llegar a su
punto de espera, así que nunca se bloqueaban y **WIP 1 salía óptimo en dos
filiales**. Moverlo a la entrada lo arregló y además es más realista: se abre
la tarea, se descubre que hace falta un presupuesto o un permiso, y se espera.

## La primera prueba con alumnos (agosto de 2026)

Tomás probó las sesiones construidas con alumnos reales. **Funcionó**, y lo
que más gustó fue lo que más caro costó de construir: que **los cinco grupos
no obtengan los mismos resultados**. Esa era la apuesta de diseño que podía
no notarse, y se notó.

**La única queja fue el tutor**, y era buena: solo preguntaba y nunca
resolvía nada, así que los alumnos acababan consultando un motor de IA
externo. Su frase, según Tomás, fue que el motor externo *«tampoco les
soluciona la vida, pero les da algunas pautas mejor recibidas»*. Lo que
querían no era la respuesta: era método.

### Lo que se cambió, y por qué el diseño original estaba a medias

El diseño protegía lo correcto —el hallazgo de cada filial— pero con
demasiada brocha. Qué es el alcance 3, por qué reciclar pierde material o qué
exige la CSRD **no son hallazgos, son conceptos**, y negarse a explicarlos
volvía el tutor inútil frente a cualquier alternativa.

Ahora hay **tres modos**, en `core/tutor.py` y `modulos/ayuda.py`:

| Modo | Qué hace | Riesgo de filtrar |
|---|---|---|
| **Explicar** | Responde de verdad sobre conceptos, métodos y estándares | Ninguno: no recibe datos de la filial |
| **Dónde mirar** | En qué paso y en qué columna está el dato | Ninguno: dice dónde, no qué |
| **Preguntar** | Lee lo escrito y devuelve una pregunta | El de siempre, ya controlado |

**La protección es estructural, no una prohibición en el prompt.**
`tutor.explicar()` no acepta el grupo como parámetro: no puede enviar datos
de la filial ni queriendo. Hay una prueba que lo verifica por introspección.

`core/conceptos.py` es un **banco de 30 conceptos escritos a mano** que cubre
las siete sesiones. Se eligió escribirlos y no generarlos por tres razones:
no pueden filtrar nada, no gastan cuota ni fallan, y están mejor redactados
que lo que da un modelo gratuito. La IA solo entra cuando el banco no llega.

**Una prueba encontró un fallo real al escribirlo:** la explicación de
circularidad citaba «reciclar el 84 % y recircular el 46 %», que son
exactamente las cifras de Bilbao. Estaba regalando su hallazgo. La prueba
`test_ninguna_explicacion_del_banco_nombra_a_una_filial` lo vigila.

## Sesión 7 · cómo está montada

Cuatro pasos. Las seis anteriores eran racionales: datos, objetivo y una
respuesta mejor que las demás. Esta introduce lo único que no tenían: gente.

1. **A quién le toca** — el mapa de actores del propio plan
2. **Qué depende de las personas** — máquinas frente a hábitos
3. **Vuestro plan de cambio** — seis palancas con presupuesto y curva de
   adopción a doce meses
4. **El cierre** — la brecha entre entregar y cambiar

Vive en `core/cambio.py`, y el documento en `core/plan_cambio.py`.

### Las dos ideas

**Quien tiene que cambiar no es quien se lleva el beneficio.** Se le pide al
personal de tienda que prepare paquetes para que bajen las emisiones de
reparto; al equipo de compras, que complique su propio objetivo de precio. La
resistencia rara vez es irracional: es que el esfuerzo y el beneficio caen en
manos distintas. El mapa de actores lo hace visible cruzando **cuánto le toca
a cada rol** con **cuánto poder tiene**, y casi nunca coinciden.

**Se puede entregar un proyecto al 100 % y no cambiar nada.** Cada iniciativa
tiene una *dependencia conductual* escrita y razonada: el refrigerante es
0,05 —una máquina que funciona la quiera alguien o no— y la segregación es
0,90 —miles de gestos diarios—. Entre el 42 % y el 46 % del valor del plan de
cada filial está en manos de otros. Sin gestionar el cambio se pierde más de
un tercio.

### Por qué el mandato no es la respuesta

Ordenarlo desde dirección es lo más barato y lo más rápido: llega al 62 % en
el mes 2 y después **se desinfla hasta el 47 %**, porque nadie ha cambiado de
opinión, solo ha dejado de discutir. Participar es lo más lento y lo único
que aguanta. Hay pruebas que fijan las dos cosas.

El presupuesto está calibrado para que comprarlo todo cueste **más del doble**
de lo disponible: el plan que lo arregla del todo no cabe, y hay prueba que
lo verifica.

### El documento de cierre

Un solo fichero con el plan de gestión del cambio **y la memoria del curso
completo**, con las siete sesiones puestas en fila. Se hizo así porque un
alumno enseña un documento en una entrevista, no siete.

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
- **2026-07-31** — **Levantada también la restricción sobre la Sesión 4.**
  Segunda reversión expresa de Tomás el mismo día, para cubrir la competencia
  de medición y reporting ESG. Las sesiones 5 a 7 siguen bloqueadas.
- **2026-07-31** — La Sesión 4 **no es un cuarto simulador**. Las sesiones 2 y
  3 comparten mecánica (objetivo, presupuesto, palancas) y una tercera igual
  habría resultado repetitiva. Además el reporting no es un problema de
  optimización: no hay óptimo que un deslizador pueda encontrar. La
  restricción es la revisión del verificador.
- **2026-07-31** — El contenido normativo se **verificó por búsqueda web** en
  lugar de escribirlo de memoria. Fue acertado: el paquete Ómnibus había
  cambiado el perímetro de la CSRD de 50.000 a 5.000 empresas y el SBTi había
  cerrado su norma v2.0 dos meses antes. Escribirlo de memoria habría
  enseñado normativa falsa.
- **2026-07-31** — La materialidad se escala **contra la media** y no de
  mínimo a máximo. Con la escala anterior, la filial que mejor opera se
  quedaba sin asuntos materiales, lo cual confunde materialidad con
  desempeño. Y se añadió un suelo de cuatro asuntos por filial.
- **2026-07-31** — Las cinco tentaciones de greenwashing son **todas
  literalmente ciertas**. Ninguna opción del ejercicio es falsa: si lo fueran,
  la sesión enseñaría a detectar mentiras, que es fácil, en vez de a detectar
  verdades que engañan, que es el problema real.
- **2026-07-31** — La memoria descargable lleva **la revisión dentro**, con
  las salvedades impresas. Que el grupo se lleve su propio documento con la
  opinión desfavorable escrita debajo es la mitad de la lección.
- **2026-07-31** — `core.datos.registrar_cache`: las cachés de otros módulos
  se apuntan en un registro en vez de importarse. `core.datos` no debe
  conocer a nadie, porque cualquier módulo nuevo crearía una importación
  circular.
- **2026-07-31** — **Levantada la restricción sobre las sesiones 5 a 7.**
  Tercera reversión expresa de Tomás, para cubrir Dirección de Proyectos:
  Agile y Scrum en la 5, Kanban e híbridos en la 6 y gestión del cambio en
  la 7. Ya no queda nada bloqueado del alcance original.
- **2026-07-31** — El backlog de la Sesión 5 se **genera desde el caso** y no
  lo reintroduce el alumno. Un backlog con historial de sprints no se copia a
  mano entre clases: era la primera vez que la ausencia de persistencia hacía
  daño de verdad, y generarlo la evita sin añadir Supabase.
- **2026-07-31** — Las iniciativas grandes **progresan entre sprints** en vez
  de entregarse o no. Sin eso, cualquier iniciativa mayor que un sprint era
  inejecutable, y son justamente las que enseñan el coste de empezar por lo
  grande.
- **2026-07-31** — Los contratiempos son **fijos por filial** y no
  aleatorios. Con aleatoriedad dos grupos viven clases distintas y la puesta
  en común se descoloca; además el guion del profesor no podría anticiparlos.
- **2026-07-31** — La clasificación predictivo/iterativo está **escrita y
  razonada**, no deducida de los datos. Es el contenido de la sesión: una obra
  es predictiva aunque la haga una empresa muy ágil.
- **2026-07-31** — La Sesión 6 **reutiliza el backlog de la Sesión 5** en vez
  de crear uno propio. Es el mismo proyecto con otra lente, y eso permite
  comparar las dos formas de gestionarlo sin que el alumno tenga que
  aprenderse un caso nuevo a mitad de curso.
- **2026-07-31** — El bloqueo de las tareas se dispara **al abrirlas** y no
  al llegar a un porcentaje de avance. Con la primera versión las tareas
  pequeñas terminaban antes de bloquearse, el equipo nunca se quedaba parado
  y el óptimo de WIP caía en 1 en dos filiales, que es justo la
  simplificación falsa que la sesión quiere desmontar.
- **2026-07-31** — El óptimo de WIP **no puede caer en los extremos**, y hay
  prueba que lo vigila en las cinco filiales. Si cayera en el mínimo, la
  lección sería «haz una cosa cada vez», que es falso y además inaplicable.
- **2026-07-31** — La ley de Little se presenta **con su desviación a la
  vista** en lugar de forzar el modelo para que cuadre. Que no encaje del
  todo es información: el sistema no está estable, y decirlo enseña más que
  ocultarlo.
- **2026-08-07** — **El tutor pasa de un modo a tres**, tras la queja de los
  alumnos en la primera prueba. Se abre a explicar conceptos y a decir dónde
  está el dato, y se mantiene cerrado sobre el hallazgo de la filial. La
  decisión del 29 de julio no se revoca: se acota a lo que de verdad había
  que proteger.
- **2026-08-07** — Las explicaciones van en un **banco escrito a mano** y no
  generadas. No pueden filtrar nada, no gastan cuota, no fallan sin red y
  están mejor redactadas. La IA es el respaldo, no la fuente.
- **2026-08-07** — La protección del hallazgo en el modo explicar es
  **estructural**: la función no recibe el grupo. Una prohibición en el
  prompt se puede sortear; la ausencia de datos, no.
- **2026-08-07** — La Sesión 7 mide **adopción y no entrega**, que es lo que
  la distingue de la 5 y de la 6. Sin esa distinción sería una tercera
  sesión de gestión de proyectos y el curso se quedaría sin cierre.
- **2026-08-07** — La dependencia conductual de cada iniciativa está
  **escrita y razonada**, como la clasificación predictivo/iterativo de la
  Sesión 5. Es el contenido de la sesión, no un parámetro.
- **2026-08-07** — El plan de cambio y la memoria del curso van en **un solo
  documento**. Un alumno enseña un documento en una entrevista, no siete, y
  las siete decisiones puestas en fila cuentan algo que por separado no se ve.
- **2026-08-07** — El panel del tutor pasa a estar **compartido** en
  `modulos/ayuda.py` en vez de copiado en cada sesión. Con un solo modo la
  duplicación era tolerable; con tres, no.
