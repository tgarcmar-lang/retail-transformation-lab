"""Banco de conceptos del curso: lo que el tutor sí puede explicar.

**Por qué existe.** En la primera prueba con alumnos, la queja principal fue
que el tutor solo preguntaba y nunca resolvía nada, así que se iban a un
motor de IA externo. Tenían razón a medias: lo que hay que proteger es **el
hallazgo de su filial**, que es lo único que deben descubrir solos. Qué es
una huella de carbono, por qué reciclar pierde material o qué exige la CSRD
no son hallazgos, son conceptos, y negarse a explicarlos volvía el tutor
inútil frente a cualquier alternativa.

**Por qué escritos a mano y no generados.** Tres razones, en orden:

1. **No pueden filtrar nada.** Un texto fijo no improvisa sobre la filial.
2. **No gastan cuota ni fallan.** Responden al instante aunque no haya red,
   que es la regla que gobierna todo el proyecto: la clase no se para nunca.
3. **Están mejor escritos.** Son las explicaciones del curso, con el
   vocabulario del curso y las mismas advertencias que da cada sesión.

Cada concepto lleva además **dónde mirar**: en qué paso de qué sesión está el
dato. Eso es lo único que el tutor puede hacer y ningún motor externo puede,
porque requiere conocer la aplicación.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Concepto:
    codigo: str
    titulo: str
    sesion: int
    explicacion: str
    donde_mirar: str = ""
    sinonimos: tuple[str, ...] = field(default_factory=tuple)


CONCEPTOS: list[Concepto] = [
    # ---------------------------------------------------------- Sesión 1
    Concepto(
        "indicador", "Qué es un indicador y por qué se divide", 1,
        "Un indicador es una cifra que sirve para decidir. La mayoría de las "
        "cifras brutas no sirven: que una filial emita 9.000 toneladas no "
        "dice si lo hace bien o mal, porque depende de su tamaño. Por eso "
        "casi todos los indicadores útiles son un cociente: emisiones por "
        "millón vendido, litros por millón, euros por metro cuadrado. "
        "Dividir es lo que permite comparar cosas de tamaños distintos, y es "
        "el error que más se comete: quedarse en la cifra absoluta.",
        "Sesión 1, paso 5: la tabla comparativa ya trae los indicadores "
        "divididos, y la columna del puesto dice en qué lugar quedáis.",
        ("kpi", "ratio", "metrica", "comparar", "absoluto", "relativo"),
    ),
    Concepto(
        "km_vacio", "Kilómetros en vacío", 1,
        "Son los kilómetros que un vehículo recorre sin carga: normalmente "
        "el viaje de vuelta después de descargar. Se pagan igual —mismo "
        "gasóleo, mismo conductor, mismo desgaste— y no transportan nada. En "
        "distribución es normal tener entre un 15 % y un 25 %; por debajo "
        "del 12 % no baja casi nadie, porque siempre hay retornos que no se "
        "pueden llenar.",
        "Sesión 1, paso 3, y la columna `km_en_vacio` de la tabla de rutas.",
        ("vacio", "retorno", "viaje de vuelta", "kilometros"),
    ),
    Concepto(
        "factor_carga", "Factor de carga y por qué no es lo mismo que el vacío", 1,
        "El factor de carga es cuánto se llena el vehículo cuando sí lleva "
        "algo: si sale al 60 % de su capacidad, está desaprovechando el 40 % "
        "de cada viaje. Es distinto de los kilómetros en vacío, y confundirlo "
        "es habitual: **un camión puede ir siempre cargado y aun así ir medio "
        "vacío**. Uno mide viajes que sobran; el otro, espacio que sobra "
        "dentro de los viajes que se hacen.\n\n"
        "Y hay una cuenta que casi nadie hace bien: pasar del 60 % al 80 % "
        "de ocupación no ahorra un 20 % de viajes, ahorra un 25 %, porque lo "
        "que cambia es la proporción entre lo que mueves y los viajes que "
        "necesitas.",
        "Sesión 1, paso 3, y la columna `ocupacion_media` de la tabla de "
        "rutas.",
        ("ocupacion", "carga", "llenar", "capacidad"),
    ),
    Concepto(
        "entrega_fallida", "Entregas fallidas", 1,
        "Una entrega que no se pudo completar al primer intento: no había "
        "nadie, no se pudo aparcar, el portal estaba cerrado. Obliga a "
        "repetir el viaje entero, así que se paga dos veces en dinero y dos "
        "veces en emisiones. Es el coste oculto de la última milla urbana y "
        "casi nunca aparece en los cuadros de mando, porque el pedido acaba "
        "entregándose y figura como éxito.",
        "Sesión 1, paso 3, y la columna `entregas_fallidas` de la tabla de "
        "rutas.",
        ("fallida", "segundo intento", "ultima milla", "reparto"),
    ),
    Concepto(
        "merma", "Merma", 1,
        "Producto que se compró y nunca llegó a venderse: caducó, se rompió, "
        "se estropeó o se perdió. Se mide en euros y como porcentaje de las "
        "ventas. Es doblemente cara, porque se pagó al proveedor y además "
        "hay que gestionarla como residuo. En alimentación es donde más "
        "pesa, y en una cadena con mucho fresco puede superar el 2,5 % de "
        "las ventas.",
        "Sesión 1, paso 3, y la Sesión 3, donde se convierte en una palanca.",
        ("desperdicio", "caducado", "perdida", "shrinkage"),
    ),
    Concepto(
        "cobertura_stock", "Días de cobertura de stock", 1,
        "Cuántos días podrías seguir vendiendo si dejaras de reponer. Mucha "
        "cobertura significa dinero inmovilizado en almacén y riesgo de que "
        "el producto se quede antiguo; poca, riesgo de rotura. Va muy unida "
        "al plazo de entrega del proveedor: quien compra lejos necesita más "
        "stock por fuerza, y eso es una consecuencia de una decisión de "
        "compra, no un descuido de almacén.",
        "Sesión 1, paso 3, tabla de inventario.",
        ("stock", "inventario", "rotacion", "almacen"),
    ),

    # ---------------------------------------------------------- Sesión 2
    Concepto(
        "huella", "Huella de carbono y CO₂ equivalente", 2,
        "La huella de carbono es el total de gases de efecto invernadero "
        "asociados a una actividad durante un año. Se mide en **toneladas de "
        "CO₂ equivalente**: como el metano o los gases refrigerantes "
        "calientan mucho más que el CO₂, se convierten todos a una unidad "
        "común para poder sumarlos. Por eso un kilo de un gas refrigerante "
        "puede equivaler a casi cuatro mil kilos de CO₂.\n\n"
        "Lo difícil de una huella no es sumar: es decidir qué se cuenta. Esa "
        "decisión se llama frontera del inventario y hay que declararla "
        "siempre.",
        "Sesión 2, paso 1.",
        ("co2", "co2e", "carbono", "emisiones", "gases"),
    ),
    Concepto(
        "alcances", "Los tres alcances", 2,
        "Es la forma normalizada de repartir las emisiones de una empresa:\n\n"
        "**Alcance 1** — lo que arde en algo que es tuyo: el gasóleo de tus "
        "camiones, el gas de tus calderas, el refrigerante que se fuga de "
        "tus cámaras.\n\n"
        "**Alcance 2** — la energía que compras ya hecha, sobre todo "
        "electricidad. No emites tú, emite la central, pero emite porque tú "
        "consumes.\n\n"
        "**Alcance 3** — todo lo demás de tu cadena de valor: fabricar lo "
        "que vendes, traerlo, tratar tus residuos, los viajes de tu gente. "
        "En un minorista es, con diferencia, la parte más grande, y también "
        "la peor medida.",
        "Sesión 2: los alcances 1 y 2 en el paso 1, y el alcance 3 en el "
        "paso 4.",
        ("alcance", "scope", "scope 3", "alcance 3"),
    ),
    Concepto(
        "factor_emision", "Factor de emisión", 2,
        "El número que convierte una actividad en emisiones: kilos de CO₂e "
        "por litro de gasóleo, por kWh de electricidad, por kilo de gas "
        "refrigerante. Multiplicas tu consumo por el factor y tienes tu "
        "huella. La calidad de una huella depende casi por completo de la "
        "calidad de sus factores, y por eso se publican y se revisan cada "
        "año.",
        "La tabla `factores_emision` de los datos del caso.",
        ("factor", "conversion", "kg co2"),
    ),
    Concepto(
        "estimacion_gasto", "Estimación por gasto, y su defecto", 2,
        "Es el método más común para calcular el alcance 3 cuando se "
        "empieza: se multiplica lo que se compra en euros por un factor "
        "medio de la categoría. Es rápido y sirve para saber dónde mirar.\n\n"
        "**Tiene un defecto que hay que conocer**: si negocias un descuento "
        "del 5 % con tu proveedor, tu huella declarada baja un 5 % sin que "
        "haya cambiado absolutamente nada en ninguna fábrica. Por eso una "
        "cifra estimada por gasto no sirve para reclamar una reducción, solo "
        "para priorizar. El paso siguiente es pedir datos primarios a los "
        "proveedores que concentran el gasto.",
        "Sesión 2, paso 4.",
        ("por gasto", "spend based", "estimacion"),
    ),
    Concepto(
        "coste_tonelada", "Coste por tonelada evitada", 2,
        "Cuánto dinero cuesta evitar una tonelada de CO₂e con una medida "
        "concreta. Es el indicador que convierte la sostenibilidad en una "
        "decisión de inversión: permite ordenar medidas que no se parecen en "
        "nada —cambiar un gas, comprar furgonetas, poner placas— con una "
        "sola vara.\n\n"
        "Ojo: una medida cara en términos absolutos puede ser la más "
        "eficiente por tonelada, y una barata puede no servir de nada si en "
        "tu caso concreto reduce poco.",
        "Sesión 2, paso 2, columna de coste por tonelada.",
        ("euros por tonelada", "coste marginal", "abatimiento"),
    ),
    Concepto(
        "cambio_modal", "Cambio modal", 2,
        "Mover la misma mercancía en un medio de transporte distinto. El "
        "caso más rentable con diferencia es pasar del avión al barco: "
        "transportar una tonelada un kilómetro emite unas cuarenta veces "
        "más en avión que en barco. A cambio, el barco tarda semanas donde "
        "el avión tarda días, así que la decisión no es ambiental sino de "
        "cadena de suministro: hay que poder esperar.",
        "Sesión 2, paso 4.",
        ("modal", "avion", "barco", "maritimo", "aereo"),
    ),

    # ---------------------------------------------------------- Sesión 3
    Concepto(
        "jerarquia_residuos", "La jerarquía de residuos", 3,
        "El orden en que conviene tratar los materiales, de mejor a peor:\n\n"
        "**1. Prevenir** — no generar el residuo. Lo que no existe no hay "
        "que gestionarlo, ni pagarlo, ni tirarlo.\n"
        "**2. Reutilizar** — que el material vuelva a usarse tal cual, sin "
        "transformarlo. Se recupera casi todo.\n"
        "**3. Reciclar** — transformarlo para hacer otra cosa. Se pierde "
        "material y se pierde calidad en cada vuelta.\n"
        "**4. Verter** — el final del camino: el material sale de la "
        "economía y no vuelve.\n\n"
        "No es una preferencia moral: es de dónde sale más material "
        "recuperado por euro invertido.",
        "Sesión 3, paso 1.",
        ("jerarquia", "prevenir", "reutilizar", "reciclar", "residuos"),
    ),
    Concepto(
        "circularidad", "Tasa de reciclaje frente a circularidad", 3,
        "No son lo mismo y confundirlas es el error central de la Sesión 3.\n\n"
        "La **tasa de reciclaje** dice cuánto material mandas a reciclar. La "
        "**circularidad** dice cuánto vuelve de verdad al ciclo. Entre una y "
        "otra se pierde bastante más de la mitad: en la recogida, en la "
        "limpieza y en la propia transformación, y lo que sale suele valer "
        "para menos cosas de lo que entró.\n\n"
        "Por eso una empresa puede tener una tasa de reciclaje excelente y "
        "una circularidad mediocre, y por eso prevenir está por encima de "
        "reciclar: una tonelada reciclada no equivale a una tonelada que "
        "nunca se generó. La distancia entre las dos cifras suele ser de "
        "decenas de puntos.",
        "Sesión 3, paso 1: las dos cifras aparecen juntas a propósito.",
        ("reciclaje", "circular", "economia circular", "recirculado"),
    ),
    Concepto(
        "logistica_inversa", "Logística inversa", 3,
        "Todo el movimiento de mercancía que va en sentido contrario al "
        "habitual: devoluciones de clientes, envases retornables que vuelven "
        "a la fábrica, aparatos que se recogen al final de su vida. Es cara "
        "porque el flujo normal está optimizado y este no.\n\n"
        "Tiene un punto de encuentro con la logística verde: si tus camiones "
        "ya vuelven de vacío, el viaje de retorno **ya lo estás pagando**, y "
        "montar un circuito de envase retornable encima de esos kilómetros "
        "sale mucho más barato que crearlo desde cero.",
        "Sesión 3, paso 2, palanca de envase retornable.",
        ("inversa", "retorno", "devoluciones", "retornable"),
    ),

    # ---------------------------------------------------------- Sesión 4
    Concepto(
        "csrd", "CSRD y ESRS", 4,
        "La **CSRD** es la directiva europea que obliga a ciertas empresas a "
        "publicar información de sostenibilidad con el mismo rigor que la "
        "financiera: auditada, comparable y en un formato común, que son los "
        "**ESRS**.\n\n"
        "**Cuidado con lo que encontréis por internet**: el paquete Ómnibus, "
        "publicado en febrero de 2026, recortó las empresas obligadas de "
        "unas 50.000 a unas 5.000, simplificó los ESRS eliminando hasta la "
        "mitad de los puntos de dato y aplazó el nuevo perímetro a enero de "
        "2027. Cualquier material anterior a 2026 está desactualizado.",
        "Sesión 4, paso 1.",
        ("csrd", "esrs", "directiva", "omnibus", "reporte obligatorio"),
    ),
    Concepto(
        "doble_materialidad", "Doble materialidad", 4,
        "El criterio que decide de qué hay que informar. Un asunto es "
        "material por dos caminos distintos:\n\n"
        "**Materialidad de impacto** — el efecto que la empresa tiene sobre "
        "el entorno y las personas.\n"
        "**Materialidad financiera** — el efecto que ese asunto tiene sobre "
        "los resultados de la empresa.\n\n"
        "**Basta con uno de los dos**: es una unión, no una intersección.\n\n"
        "Y el error más común: materialidad no es desempeño. Un asunto es "
        "material si pesa, no si lo haces mal. El transporte es material en "
        "una empresa que mueve muchísima mercancía aunque la mueva bien.",
        "Sesión 4, paso 2: la matriz se calcula con los datos de vuestra "
        "propia filial.",
        ("materialidad", "material", "matriz", "doble"),
    ),
    Concepto(
        "iso14083", "ISO 14083 y el GLEC Framework", 4,
        "La norma internacional que dice cómo se calculan y se declaran las "
        "emisiones del transporte y la logística. Se publicó en 2023 sobre "
        "el trabajo previo del GLEC Framework, y hoy es el idioma común "
        "entre cargadores, operadores logísticos y verificadores.\n\n"
        "Su indicador estrella es la intensidad: gramos de CO₂e por tonelada "
        "y kilómetro. Permite comparar un camión con un barco, o tu "
        "operación con la de otra empresa, cosa que las cifras absolutas no "
        "permiten.",
        "Sesión 4, paso 3: los indicadores marcados con ISO 14083.",
        ("iso", "14083", "glec", "tkm", "tonelada kilometro"),
    ),
    Concepto(
        "greenwashing", "Greenwashing", 4,
        "Comunicar el desempeño ambiental de forma que induzca a error. Lo "
        "importante, y lo que casi nadie enseña: **no hace falta mentir**. "
        "Las formas más frecuentes son todas literalmente ciertas:\n\n"
        "— Sumar porcentajes de reducción que tienen denominadores distintos.\n"
        "— Publicar una huella sin declarar qué incluye y qué no.\n"
        "— Destacar la cifra que sale mejor entre dos que miden lo mismo.\n"
        "— Dar solo magnitudes absolutas, que bajan si vendes menos.\n"
        "— Presentar una estimación gruesa con precisión de decimales.\n\n"
        "Por eso existe la verificación externa: comprobar que una cifra es "
        "cierta es fácil; comprobar que no engaña, no.",
        "Sesión 4, paso 3: las cinco decisiones de presentación.",
        ("greenwashing", "lavado verde", "enganar", "maquillar"),
    ),
    Concepto(
        "sbti", "SBTi y los objetivos basados en la ciencia", 4,
        "La Science Based Targets initiative valida que el objetivo de "
        "reducción de una empresa es coherente con lo que haría falta para "
        "limitar el calentamiento. No es obligatorio, pero es el sello más "
        "reconocido.\n\n"
        "Su norma Corporate Net-Zero v2.0, cerrada en junio de 2026, exige "
        "algo que conviene retener: **los objetivos de alcances 1 y 2 y los "
        "de alcance 3 se fijan y se comunican por separado**. Son "
        "inventarios distintos y mezclarlos no significa nada.",
        "Sesión 4, paso 1, mapa de estándares.",
        ("sbti", "science based", "net zero", "objetivo"),
    ),
    Concepto(
        "calidad_dato", "Calidad del dato", 4,
        "No todas las cifras de una memoria valen lo mismo. Un consumo "
        "leído de un contador es un dato de calidad alta; una estimación a "
        "partir del gasto es de calidad baja. Declararlo no es una debilidad: "
        "es lo que permite a quien lee saber qué puede hacer con cada cifra.\n\n"
        "Regla práctica: un indicador de calidad baja sirve para decidir "
        "dónde mirar, nunca para reclamar una mejora.",
        "Sesión 4, paso 3: la columna de calidad del catálogo.",
        ("calidad", "trazabilidad", "fiabilidad", "dato primario"),
    ),

    # ---------------------------------------------------------- Sesión 5
    Concepto(
        "backlog", "Backlog y puntos de esfuerzo", 5,
        "El backlog es la lista de todo lo que hay que hacer, ordenada por "
        "prioridad. Cada elemento lleva un **esfuerzo** en puntos, que no son "
        "horas: son tamaño relativo. Se usan puntos y no horas porque la "
        "gente estima fatal en horas y bastante bien en comparaciones.\n\n"
        "Lo que de verdad ordena un backlog no es el esfuerzo ni el valor por "
        "separado, sino el **valor por punto**: lo que rinde cada unidad de "
        "trabajo invertida.",
        "Sesión 5, paso 1.",
        ("backlog", "puntos", "esfuerzo", "estimacion", "historia"),
    ),
    Concepto(
        "predictivo_iterativo", "Predictivo frente a iterativo", 5,
        "La distinción que decide cómo se gestiona cada parte de un "
        "proyecto.\n\n"
        "**Predictivo** — el alcance está cerrado desde el principio. Hay "
        "proveedor, permiso, precio y fecha. No hay nada que descubrir: hay "
        "que ejecutarlo bien. Cambiar una instalación de frío es esto.\n\n"
        "**Iterativo** — no se sabe qué funciona hasta probarlo. Se avanza "
        "por tandas, se mide y se corrige. Un programa con proveedores es "
        "esto.\n\n"
        "Meter una obra en sprints no la acelera, solo añade reuniones. Y "
        "planificar a doce meses lo que hay que descubrir es escribir una "
        "ficción. Gestionar las dos mitades con el mismo método es el error "
        "más caro de la dirección de proyectos, y **saber cuál es cuál es lo "
        "que se llama enfoque híbrido**.",
        "Sesión 5, paso 1: la clasificación de vuestro backlog.",
        ("predictivo", "iterativo", "agil", "cascada", "hibrido", "waterfall"),
    ),
    Concepto(
        "scrum", "Sprint y velocidad", 5,
        "Un **sprint** es una caja de tiempo fija —una o dos semanas— en la "
        "que el equipo se compromete a terminar un conjunto de trabajo. Lo "
        "importante no es la ceremonia: es que al final del sprint haya algo "
        "terminado que se pueda enseñar.\n\n"
        "La **capacidad** o velocidad es cuántos puntos cabe esperar que el "
        "equipo termine en un sprint. Se mide, no se decide.\n\n"
        "Y la idea que más cuesta: lo ágil no hace ir más rápido, hace "
        "enterarse antes. Quien tiene algo entregado en el sprint 2 puede "
        "defenderlo cuando llega el recorte; quien no ha entregado nada, no.",
        "Sesión 5, paso 2.",
        ("sprint", "scrum", "velocidad", "capacidad", "iteracion"),
    ),

    # ---------------------------------------------------------- Sesión 6
    Concepto(
        "kanban", "Kanban y el límite de trabajo en curso", 6,
        "Un tablero Kanban no reparte trabajo en cajas de tiempo: lo deja "
        "fluir. Cuando se termina algo, entra lo siguiente. La única "
        "decisión importante es el **límite de trabajo en curso** (WIP): "
        "cuántas cosas puede haber abiertas a la vez.\n\n"
        "Empezar más cosas no termina más cosas, porque la capacidad se "
        "reparte y cambiar de tarea cuesta. Pero el mínimo tampoco es la "
        "respuesta: si solo tienes una tarea abierta y se queda esperando a "
        "un proveedor, el equipo entero se para. **El óptimo está en medio y "
        "depende de tu equipo y de tu trabajo.**",
        "Sesión 6, paso 2: probad varios límites y mirad la curva.",
        ("kanban", "wip", "tablero", "trabajo en curso", "limite"),
    ),
    Concepto(
        "little", "La ley de Little", 6,
        "Tiempo de ciclo = trabajo en curso ÷ ritmo de entrega.\n\n"
        "No es una regla aproximada ni una metáfora: es una identidad que se "
        "cumple en cualquier sistema estable. Si tienes seis cosas abiertas "
        "y terminas dos por semana, cada cosa tarda tres semanas de media.\n\n"
        "Lo que implica es lo único que hay que recordar: **si quieres "
        "entregar antes y no puedes trabajar más rápido, la única palanca "
        "que te queda es empezar menos cosas a la vez.**\n\n"
        "Y una advertencia honesta: la ley describe sistemas estables. Si al "
        "final del periodo te quedan tareas a medias, no cuadrará del todo, y "
        "saber por qué vale tanto como saber aplicarla.",
        "Sesión 6, paso 2: el desplegable que la comprueba con vuestros "
        "propios números.",
        ("little", "tiempo de ciclo", "throughput", "ciclo"),
    ),
    Concepto(
        "flujo_acumulado", "Diagrama de flujo acumulado", 6,
        "El gráfico de seguimiento de un tablero: una banda por columna, "
        "apiladas a lo largo del tiempo. Lo que importa no son las bandas "
        "sino su grosor.\n\n"
        "Si la banda de «en curso» engorda, estás abriendo más de lo que "
        "cierras y el tiempo de ciclo va a subir. Si engorda la de "
        "«bloqueado», el cuello de botella no está en tu equipo sino en "
        "quien tiene que responderte. Y si la de «hecho» sube a escalones en "
        "vez de en línea, entregas a golpes en lugar de seguido.",
        "Sesión 6, paso 4.",
        ("cfd", "flujo acumulado", "diagrama", "seguimiento"),
    ),

    # ---------------------------------------------------------- Sesión 7
    Concepto(
        "gestion_cambio", "Gestión del cambio", 7,
        "La parte de un proyecto que se ocupa de las personas que tienen que "
        "trabajar distinto para que el proyecto sirva de algo.\n\n"
        "La idea central: **quien tiene que cambiar casi nunca es quien se "
        "lleva el beneficio**. Le pides a una tienda que prepare paquetes "
        "para que bajen las emisiones de reparto; le pides a un conductor "
        "que cambie su ruta para que mejore un indicador de la central. La "
        "resistencia rara vez es irracional: normalmente es que el esfuerzo "
        "y el beneficio caen en manos distintas.",
        "Sesión 7, paso 1.",
        ("cambio", "resistencia", "personas", "adopcion"),
    ),
    Concepto(
        "adopcion", "Adopción y la brecha con la entrega", 7,
        "Entregar un proyecto y que el proyecto cambie algo son dos cosas "
        "distintas. La **adopción** es qué parte del beneficio prometido se "
        "materializa de verdad una vez que la gente reacciona.\n\n"
        "No todas las medidas dependen igual de ella. Una instalación nueva "
        "funciona la quiera la gente o no: es una máquina. Un cambio de "
        "hábito —que el personal de tienda empuje la recogida, que un "
        "conductor respete una ruta nueva— solo funciona si lo adoptan.\n\n"
        "Por eso **se puede entregar un proyecto al 100 % y no cambiar "
        "nada**, y por eso un plan hecho solo de medidas de comportamiento "
        "es mucho más frágil de lo que parece en la hoja de cálculo.",
        "Sesión 7, pasos 2 y 3.",
        ("adopcion", "brecha", "beneficio real", "uso"),
    ),
    Concepto(
        "actores", "Mapa de actores", 7,
        "El inventario de quién se ve afectado por un cambio, con dos "
        "preguntas para cada uno: **cuánto le afecta** y **cuánto poder "
        "tiene** para pararlo o impulsarlo.\n\n"
        "Sirve para no gastar el mismo esfuerzo en todos. A quien tiene "
        "mucho poder y poco interés hay que mantenerlo informado; a quien "
        "tiene mucho de los dos hay que sentarlo a decidir contigo desde el "
        "principio; a quien tiene mucho interés y poco poder, escucharlo, "
        "porque suele ser quien sabe por qué el plan no va a funcionar.",
        "Sesión 7, paso 1.",
        ("actores", "stakeholder", "interesados", "poder", "interes"),
    ),
]

POR_CODIGO = {c.codigo: c for c in CONCEPTOS}


def _normalizar(texto: str) -> str:
    """Minúsculas, sin acentos y sin signos: para poder comparar."""
    limpio = unicodedata.normalize("NFKD", (texto or "").lower())
    limpio = "".join(c for c in limpio if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9ñ ]+", " ", limpio)


def _palabras(texto: str) -> set[str]:
    return {p for p in _normalizar(texto).split() if len(p) > 2}


#: Palabras tan comunes que no ayudan a distinguir un concepto de otro.
VACIAS = {
    "que", "como", "para", "por", "los", "las", "del", "una", "uno", "con",
    "cual", "cuales", "donde", "cuando", "esto", "eso", "hay", "son", "the",
    "explicame", "explica", "dime", "quiero", "saber", "entiendo", "significa",
    "puedes", "podrias", "sobre", "acerca", "mas", "nuestra", "nuestro",
    "mismo", "misma", "frente", "entre", "entiende", "diferencia", "entender",
    "sirve", "entonces", "tiene", "tienen", "ser", "esta", "estan", "muy",
    "porque", "cuanto", "cuanta", "entendemos", "significan", "quienes",
}


def buscar(consulta: str, sesion: int | None = None) -> Concepto | None:
    """El concepto del banco que mejor responde a la consulta.

    Búsqueda por palabras, sin dependencias ni modelos: compara el texto del
    alumno con el título, los sinónimos y el código de cada concepto. Si nada
    encaja razonablemente, devuelve `None` y el tutor pasa a la IA.
    """
    palabras = _palabras(consulta) - VACIAS
    if not palabras:
        return None

    mejor, mejor_puntos = None, 0.0
    for concepto in CONCEPTOS:
        # Las palabras vacías se descuentan también de las etiquetas: sin
        # esto, un título que contenga «lo mismo que» se lleva cualquier
        # consulta que use esas palabras, aunque no tenga nada que ver.
        del_titulo = _palabras(concepto.titulo) - VACIAS
        etiquetas = del_titulo | {
            p for s in concepto.sinonimos for p in _palabras(s)
        } | _palabras(concepto.codigo.replace("_", " "))
        etiquetas -= VACIAS
        comunes = palabras & etiquetas
        if not comunes:
            continue
        # Se puntúa por palabras coincidentes, dando algo de ventaja a los
        # conceptos de la sesión en la que está el alumno.
        puntos = len(comunes) + 0.5 * len(comunes & del_titulo)
        if sesion is not None and concepto.sesion == sesion:
            puntos += 0.75
        if puntos > mejor_puntos:
            mejor, mejor_puntos = concepto, puntos

    return mejor if mejor_puntos >= 1 else None


def del_curso(sesion: int | None = None) -> list[Concepto]:
    """Los conceptos, opcionalmente filtrados por sesión."""
    if sesion is None:
        return list(CONCEPTOS)
    return [c for c in CONCEPTOS if c.sesion == sesion]


def texto(concepto: Concepto) -> str:
    """La explicación completa, con el «dónde mirar» si lo tiene."""
    if not concepto.donde_mirar:
        return concepto.explicacion
    return f"{concepto.explicacion}\n\n**Dónde mirarlo:** {concepto.donde_mirar}"
