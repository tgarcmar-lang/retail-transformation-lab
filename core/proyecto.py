"""Ejecución del plan · Sesión 5.

Las cuatro sesiones anteriores terminaban con una decisión. Ninguna se
ejecutó. Esta es la que convierte tres planes en trabajo con fechas, gente y
contratiempos.

**De dónde sale el trabajo.** El backlog no está escrito a mano: cada
iniciativa nace de una palanca real de las sesiones 2 y 3, y hereda sus
cifras. El esfuerzo se deriva del coste de la palanca en esa filial y el
valor, de las toneladas que evita. Así el trabajo que planifican es
exactamente el trabajo que decidieron, sin necesidad de arrastrar estado
entre clases.

**La idea que sostiene la sesión.** No todo el plan se gestiona igual.
Cambiar el refrigerante de Valencia es una obra: alcance cerrado, proveedor,
permiso, fecha. Forzarlo a sprints es teatro. El programa de proveedores, en
cambio, es iterativo de verdad: nadie sabe qué funciona hasta probarlo con un
proveedor. **Distinguir una cosa de otra es la competencia**, y es lo que
separa a quien ha entendido lo ágil de quien se ha aprendido el vocabulario.

**La segunda idea.** Lo ágil no hace ir más rápido: hace enterarse antes. El
grupo que reparte su trabajo para entregar algo en el primer sprint descubre
sus problemas cuando aún puede reaccionar. El que ordena por tamaño no
entrega nada hasta el final y se entera de todo cuando ya no hay margen.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from core import circular, datos, filiales, palancas

#: Sprints que dura el ejercicio. Con menos no se ve la curva de entrega y
#: con más la clase no da tiempo.
SPRINTS = 6

#: Un punto de esfuerzo equivale a esta inversión. Sirve para traducir el
#: coste de una palanca a tamaño de trabajo.
EUROS_POR_PUNTO = 120_000.0

#: Qué parte del backlog cabe en los seis sprints, de media. Por debajo de 1
#: a propósito: **no cabe todo, y esa es la sesión**. Si cupiera, no habría
#: que priorizar y priorizar es la competencia que se evalúa.
HOLGURA_MEDIA = 0.70

#: Banda en la que se mueve el equipo de cada filial. Una filial con muchos
#: empleados por euro invertido va más holgada; Valencia y Sevilla, que
#: arrastran una inversión grande con plantillas pequeñas, van más justas.
HOLGURA_MINIMA = 0.60
HOLGURA_MAXIMA = 0.80


@dataclass(frozen=True)
class Iniciativa:
    codigo: str
    nombre: str
    origen: str          # de qué sesión viene
    enfoque: str         # Predictivo · Iterativo
    esfuerzo: int        # puntos
    valor: int           # 1 a 10
    depende_de: tuple[str, ...] = ()
    porque: str = ""

    @property
    def valor_por_punto(self) -> float:
        return self.valor / self.esfuerzo if self.esfuerzo else 0.0


#: Cómo se clasifica cada palanca. **Es el contenido de la sesión**, así que
#: está escrito y razonado, no deducido: una obra con proveedor y permiso es
#: predictiva aunque la haga una empresa muy ágil, y un programa con
#: proveedores es iterativo aunque lo dirija un ingeniero muy metódico.
ENFOQUE_PALANCA = {
    "refrigerante": ("Predictivo",
                     "Es una obra: proveedor, permiso, parada de la "
                     "instalación y fecha. No hay nada que descubrir por el "
                     "camino, hay que ejecutarla bien."),
    "electrificacion": ("Predictivo",
                        "Se compran vehículos y se instalan puntos de "
                        "recarga. El alcance está cerrado desde el principio."),
    "energia": ("Predictivo",
                "Iluminación, equipos y fotovoltaica en cubierta. Es obra "
                "civil y compra de equipo."),
    "vacio": ("Iterativo",
              "Depende de encontrar cargas de retorno que hoy no se conocen. "
              "Se avanza probando rutas y acuerdos, y muchos no salen."),
    "carga": ("Iterativo",
              "Reagrupar pedidos y cambiar frecuencias de reparto afecta a "
              "cada tienda de forma distinta. Se aprende tienda a tienda."),
    "consolidacion": ("Iterativo",
                      "Nadie sabe qué porcentaje de clientes aceptará "
                      "recoger en tienda hasta que se prueba en una."),
    "segregacion": ("Iterativo",
                    "Depende de miles de gestos diarios. Se mejora midiendo, "
                    "corrigiendo y volviendo a medir."),
    "embalaje": ("Iterativo",
                 "Cada referencia necesita su propia caja. Se rediseña por "
                 "familias y se comprueba que no aumenten las roturas."),
    "merma": ("Iterativo",
              "La previsión de demanda se afina con datos reales, y la "
              "rebaja dinámica hay que calibrarla en tienda."),
    "retornable": ("Predictivo",
                   "Se compra un parque de cajas plegables y se monta el "
                   "circuito de lavado y retorno. Es inversión y logística."),
    "reacondicionado": ("Predictivo",
                        "Se monta un taller: espacio, equipo y personal. "
                        "Después se opera, pero montarlo es un proyecto."),
    "devoluciones": ("Iterativo",
                     "Fotos, medidas y guías de talla se prueban por "
                     "categorías y se mide si baja la devolución."),
}

#: Iniciativas que no vienen de una palanca sino de la Sesión 4. Son las que
#: hacen falta para poder publicar la memoria, y son fáciles de olvidar
#: justamente porque no reducen ni una tonelada.
INICIATIVAS_REPORTING = [
    ("medicion", "Sistema de medición y trazabilidad", "Sesión 4", "Predictivo",
     "Sin esto no hay memoria que verificar: hay que poder rastrear cada "
     "cifra hasta su origen. No reduce nada y sin ello no se puede declarar "
     "nada."),
    ("proveedores_esg", "Evaluación ESG de proveedores", "Sesión 4", "Iterativo",
     "Se empieza por los que concentran el gasto y se aprende a evaluar "
     "evaluando. Es el hueco de gobernanza que la memoria deja al aire."),
]


# --------------------------------------------------------------------------
# El backlog
# --------------------------------------------------------------------------

def _esfuerzo(coste_eur: float) -> int:
    """Traduce la inversión de una palanca a tamaño de trabajo."""
    return max(1, int(round(coste_eur / EUROS_POR_PUNTO)))


def _valor(pct_del_objetivo: float) -> int:
    """Valor de 1 a 10 según lo que la palanca aporta al objetivo."""
    return max(1, min(10, int(round(pct_del_objetivo * 30))))


@lru_cache(maxsize=None)
def _backlog(grupo: str, anio: int | None = None) -> tuple[Iniciativa, ...]:
    """La cartera de iniciativas de la filial.

    Sale de las palancas de las sesiones 2 y 3, con su coste y su impacto
    reales, más las dos iniciativas de reporting de la Sesión 4. No hay
    ninguna cifra escrita a mano.
    """
    iniciativas: list[Iniciativa] = []

    for fila in palancas.coste_por_tonelada(grupo, anio):
        if fila["coste_eur"] <= 0:
            continue
        enfoque, porque = ENFOQUE_PALANCA[fila["codigo"]]
        iniciativas.append(Iniciativa(
            codigo=f"c_{fila['codigo']}",
            nombre=fila["nombre"],
            origen="Sesión 2 · Descarbonización",
            enfoque=enfoque,
            esfuerzo=_esfuerzo(fila["coste_eur"]),
            valor=_valor(fila["pct_de_la_huella"]),
            porque=porque,
        ))

    for fila in circular.coste_por_tonelada(grupo, anio):
        if fila["coste_eur"] <= 0:
            continue
        enfoque, porque = ENFOQUE_PALANCA[fila["codigo"]]
        iniciativas.append(Iniciativa(
            codigo=f"m_{fila['codigo']}",
            nombre=fila["nombre"],
            origen="Sesión 3 · Economía circular",
            enfoque=enfoque,
            esfuerzo=_esfuerzo(fila["coste_eur"]),
            valor=_valor(fila["pct_de_la_perdida"]),
            porque=porque,
        ))

    # El sistema de medición es la única dependencia dura del caso: sin él no
    # se puede acreditar ninguna de las demás.
    medicion, proveedores = INICIATIVAS_REPORTING
    plantilla = _empleados(grupo)
    iniciativas.append(Iniciativa(
        codigo="r_medicion", nombre=medicion[1], origen=medicion[2],
        enfoque=medicion[3], esfuerzo=max(3, int(plantilla / 500)),
        valor=4, porque=medicion[4],
    ))
    iniciativas.append(Iniciativa(
        codigo="r_proveedores_esg", nombre=proveedores[1],
        origen=proveedores[2], enfoque=proveedores[3],
        esfuerzo=max(3, int(plantilla / 400)), valor=5,
        depende_de=("r_medicion",), porque=proveedores[4],
    ))

    return tuple(iniciativas)


def backlog(grupo: str, anio: int | None = None) -> list[Iniciativa]:
    """La cartera de iniciativas de la filial, recalculada solo una vez.

    Construirla obliga a recorrer las palancas de dos sesiones enteras y
    cuesta casi un segundo. Las iniciativas son inmutables, así que se puede
    cachear sin riesgo: lo único que se devuelve es una lista nueva.
    """
    return list(_backlog(grupo, anio))


@lru_cache(maxsize=None)
def _por_codigo(grupo: str) -> dict[str, Iniciativa]:
    return {i.codigo: i for i in _backlog(grupo)}


@lru_cache(maxsize=None)
def _capacidad(grupo: str) -> float:
    grupos = [f.grupo for f in filiales.listar()]
    densidad = {
        g: _empleados(g) / max(1, sum(i.esfuerzo for i in _backlog(g)))
        for g in grupos
    }
    minimo, maximo = min(densidad.values()), max(densidad.values())
    if maximo - minimo < 1e-9:
        holgura = HOLGURA_MEDIA
    else:
        posicion = (densidad[grupo] - minimo) / (maximo - minimo)
        holgura = HOLGURA_MINIMA + posicion * (HOLGURA_MAXIMA - HOLGURA_MINIMA)
    return round(sum(i.esfuerzo for i in _backlog(grupo)) * holgura / SPRINTS, 1)


def limpiar_cache() -> None:
    """Olvida el backlog calculado. La llama `core.datos`."""
    _backlog.cache_clear()
    _por_codigo.cache_clear()
    _capacidad.cache_clear()


datos.registrar_cache(limpiar_cache)


def _empleados(grupo: str) -> int:
    from core import reporting
    return int(reporting.valor(grupo, "s_plantilla"))


def por_codigo(grupo: str) -> dict[str, Iniciativa]:
    return dict(_por_codigo(grupo))


def _esfuerzo_total(grupo: str) -> int:
    return sum(i.esfuerzo for i in _backlog(grupo))


def capacidad(grupo: str) -> float:
    """Puntos que el equipo de la filial puede acometer en un sprint.

    Se calcula sobre el propio backlog para que las cinco filiales tengan un
    reto comparable, y se modula por la gente que tiene cada una por euro
    invertido: quien arrastra una inversión grande con poca plantilla va más
    justo, que es exactamente lo que le pasa a Valencia y a Sevilla.
    """
    return _capacidad(grupo)


def tabla_backlog(grupo: str) -> pd.DataFrame:
    """El backlog en forma de tabla, ordenado por valor entregado por punto."""
    filas = [{
        "codigo": i.codigo,
        "nombre": i.nombre,
        "origen": i.origen,
        "enfoque": i.enfoque,
        "esfuerzo": i.esfuerzo,
        "valor": i.valor,
        "valor_por_punto": round(i.valor_por_punto, 3),
        "depende_de": ", ".join(i.depende_de),
        "porque": i.porque,
    } for i in backlog(grupo)]
    tabla = pd.DataFrame(filas)
    return tabla.sort_values("valor_por_punto", ascending=False,
                             ignore_index=True)


# --------------------------------------------------------------------------
# Los contratiempos
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Evento:
    codigo: str
    sprint: int          # en qué sprint aparece
    titulo: str
    relato: str
    efecto: str          # bloquea · encarece · recorta_capacidad
    objetivo: str = ""   # código de iniciativa afectada, si aplica
    magnitud: float = 0.0
    leccion: str = ""


#: Un contratiempo por filial, coherente con su historia y siempre el mismo.
#: Son fijos y no aleatorios para que los cinco grupos puedan compararse en
#: la puesta en común y para que el guion del profesor pueda anticiparlos.
EVENTOS: dict[str, list[Evento]] = {
    "A": [
        Evento("a_taquillas", 2,
               "El fabricante de taquillas se retrasa",
               "El proveedor de las taquillas de recogida en tienda comunica "
               "que no puede servir hasta dentro de dos meses: tiene la "
               "producción comprometida con otro cliente.",
               "bloquea", "c_consolidacion", 2,
               "La iniciativa que cerraba el hallazgo de la Sesión 1 depende "
               "de un tercero. Quien la había dejado para el final se queda "
               "sin ella."),
        Evento("a_piloto", 4,
               "El piloto de envase sale mal",
               "Las cajas rediseñadas aumentan las roturas en el transporte "
               "un 3 %. Hay que rehacer el diseño de dos familias.",
               "encarece", "m_embalaje", 0.35,
               "Un piloto que sale mal en el sprint 4 es una buena noticia: "
               "el mismo error descubierto al final habría costado el triple."),
    ],
    "B": [
        Evento("b_proveedor", 2,
               "El proveedor asiático no contesta",
               "Los tres proveedores que concentran el 40 % de la compra no "
               "responden a la solicitud de datos de emisiones. Sin ellos no "
               "hay programa de proveedores que valga.",
               "bloquea", "r_proveedores_esg", 3,
               "Sobre la cadena de valor no se manda: se negocia. Y negociar "
               "lleva tiempo que no estaba en el plan."),
        Evento("b_aduana", 4,
               "Retención en aduana",
               "El primer envío marítimo de prueba se queda retenido tres "
               "semanas. El equipo de compras pide volver al avión «solo por "
               "esta campaña».",
               "recorta_capacidad", "", 0.25,
               "La presión para deshacer una decisión sostenible casi nunca "
               "llega como una orden: llega como una excepción razonable."),
    ],
    "C": [
        Evento("c_instalador", 2,
               "El instalador de CO₂ se retrasa",
               "La empresa que tenía que reconvertir las instalaciones de "
               "frío solo puede empezar dos meses más tarde: hay tres "
               "cadenas más haciendo lo mismo este año.",
               "bloquea", "c_refrigerante", 2,
               "Su iniciativa más rentable es también la más rígida. Es una "
               "obra, y una obra no se acelera con voluntad."),
        Evento("c_averia", 3,
               "Avería en una cámara del hipermercado de Paterna",
               "Una fuga obliga a intervenir de urgencia. El equipo de "
               "mantenimiento que estaba en el proyecto se va a apagar el "
               "fuego.",
               "recorta_capacidad", "", 0.30,
               "La operación siempre gana al proyecto. Un plan que no deja "
               "holgura para lo urgente no sobrevive al primer mes."),
    ],
    "D": [
        Evento("d_jefe_trafico", 1,
               "Se va el jefe de tráfico",
               "La persona que conocía las rutas y los acuerdos con los "
               "transportistas se marcha a la competencia. Se lleva consigo "
               "lo que no estaba escrito en ninguna parte.",
               "recorta_capacidad", "", 0.35,
               "El conocimiento que no está documentado es un riesgo de "
               "proyecto, no una anécdota de personal."),
        Evento("d_cajas", 4,
               "Sube el precio de las cajas retornables",
               "El fabricante sube un 22 % por el precio del polipropileno. "
               "El circuito de retorno sigue siendo rentable, pero menos.",
               "encarece", "m_retornable", 0.22,
               "Un plan a tres años se hace con precios de hoy. Conviene "
               "saber cuánto puede subir algo antes de dejar de tener "
               "sentido."),
    ],
    "E": [
        Evento("e_recorte", 3,
               "La corporación recorta el presupuesto",
               "Central pide un ajuste del 20 % en todos los proyectos de "
               "las filiales pequeñas. Hay que entregar lo mismo con menos.",
               "recorta_capacidad", "", 0.20,
               "El recorte llega siempre a mitad de camino. Quien ya ha "
               "entregado algo puede defenderlo; quien no ha entregado nada, "
               "no."),
        Evento("e_copia", 5,
               "Madrid quiere copiar vuestro modelo",
               "La filial grande pide que dos personas del equipo vayan a "
               "explicar el sistema de recogida en tienda. Es un "
               "reconocimiento y es una pérdida de capacidad.",
               "recorta_capacidad", "", 0.15,
               "El éxito también consume capacidad. Nadie lo pone en el plan "
               "inicial."),
    ],
}


def eventos(grupo: str) -> list[Evento]:
    return EVENTOS.get(grupo, [])


def eventos_del_sprint(grupo: str, sprint: int) -> list[Evento]:
    return [e for e in eventos(grupo) if e.sprint == sprint]


# --------------------------------------------------------------------------
# La ejecución
# --------------------------------------------------------------------------

def simular(grupo: str, plan: dict[int, list[str]],
            con_eventos: bool = True) -> dict:
    """Ejecuta el plan sprint a sprint y cuenta qué se entrega y cuándo.

    `plan` reparte códigos de iniciativa entre sprints: {1: [...], 2: [...]}.
    Nunca lanza excepción por una entrada rara.

    Una iniciativa solo se entrega si cabe en la capacidad del sprint, si sus
    dependencias ya están entregadas y si ningún evento la tiene bloqueada.
    Lo que no cabe **no desaparece**: se arrastra al sprint siguiente, que es
    lo que pasa en la realidad y lo que hace visible el coste de sobrecargar.
    """
    catalogo = por_codigo(grupo)
    base = capacidad(grupo)
    del_grupo = eventos(grupo) if con_eventos else []

    bloqueadas: dict[str, int] = {}     # código -> sprint hasta el que dura
    sobrecoste: dict[str, float] = {}
    entregadas: set[str] = set()
    progreso: dict[str, float] = {}     # puntos ya invertidos en cada una
    pendientes: list[str] = []
    detalle = []
    valor_acumulado = 0
    valor_total = sum(i.valor for i in catalogo.values())

    for sprint in range(1, SPRINTS + 1):
        capacidad_sprint = base
        sucesos = []
        for evento in [e for e in del_grupo if e.sprint == sprint]:
            sucesos.append(evento)
            if evento.efecto == "bloquea" and evento.objetivo:
                bloqueadas[evento.objetivo] = sprint + int(evento.magnitud)
            elif evento.efecto == "encarece" and evento.objetivo:
                sobrecoste[evento.objetivo] = (
                    sobrecoste.get(evento.objetivo, 0.0) + evento.magnitud
                )
            elif evento.efecto == "recorta_capacidad":
                capacidad_sprint *= (1 - evento.magnitud)

        # Lo que arrastra el sprint anterior va primero: es deuda.
        cola = pendientes + [
            c for c in plan.get(sprint, []) or []
            if c in catalogo and c not in entregadas and c not in pendientes
        ]
        pendientes = []
        restante = capacidad_sprint
        del_sprint = []

        for codigo in cola:
            iniciativa = catalogo[codigo]
            if codigo in entregadas:
                continue
            if bloqueadas.get(codigo, 0) > sprint:
                pendientes.append(codigo)
                continue
            if any(d not in entregadas for d in iniciativa.depende_de):
                pendientes.append(codigo)
                continue

            # Una iniciativa grande no cabe en un sprint: se avanza lo que se
            # puede y se continúa en el siguiente. Pero **no entrega valor
            # hasta que está terminada**, que es de lo que se quejan los
            # comités cuando llevan medio año sin ver nada.
            coste = iniciativa.esfuerzo * (1 + sobrecoste.get(codigo, 0.0))
            falta = coste - progreso.get(codigo, 0.0)
            if restante <= 1e-9:
                pendientes.append(codigo)
                continue
            avance = min(falta, restante)
            progreso[codigo] = progreso.get(codigo, 0.0) + avance
            restante -= avance
            if progreso[codigo] >= coste - 1e-9:
                entregadas.add(codigo)
                valor_acumulado += iniciativa.valor
                del_sprint.append(codigo)
            else:
                pendientes.append(codigo)

        detalle.append({
            "sprint": sprint,
            "capacidad": round(capacidad_sprint, 1),
            "usada": round(capacidad_sprint - restante, 1),
            "entregadas": del_sprint,
            "arrastradas": list(pendientes),
            "en_curso": [c for c in pendientes if progreso.get(c, 0) > 0],
            "valor_del_sprint": sum(catalogo[c].valor for c in del_sprint),
            "valor_acumulado": valor_acumulado,
            "eventos": sucesos,
        })

    return {
        "detalle": detalle,
        "entregadas": sorted(entregadas),
        "sin_entregar": sorted(set(catalogo) - entregadas),
        "valor_entregado": valor_acumulado,
        "valor_total": valor_total,
        "pct_valor": valor_acumulado / valor_total if valor_total else 0.0,
        # Cuánto valor había en la calle a mitad de camino. Es la cifra que
        # distingue un plan que entrega pronto de uno que entrega tarde.
        "valor_en_sprint_3": detalle[2]["valor_acumulado"] if len(detalle) > 2 else 0,
        "capacidad_base": base,
        "eventos": del_grupo,
        "progreso": progreso,
    }


def plan_por_valor(grupo: str) -> dict[int, list[str]]:
    """Reparte el backlog priorizando lo que más valor da por punto.

    Es la referencia «buena»: entrega pronto y llega lejos.
    """
    catalogo = por_codigo(grupo)
    orden = sorted(catalogo.values(),
                   key=lambda i: (-i.valor_por_punto, i.esfuerzo))
    return _repartir(grupo, [i.codigo for i in orden])


def plan_por_tamano(grupo: str) -> dict[int, list[str]]:
    """Reparte empezando por lo más grande, que es lo que hace casi todo el
    mundo cuando ve una lista de iniciativas: atacar primero lo gordo."""
    catalogo = por_codigo(grupo)
    orden = sorted(catalogo.values(), key=lambda i: -i.esfuerzo)
    return _repartir(grupo, [i.codigo for i in orden])


def _repartir(grupo: str, orden: list[str]) -> dict[int, list[str]]:
    """Mete iniciativas en sprints hasta llenar la capacidad de cada uno."""
    catalogo = por_codigo(grupo)
    base = capacidad(grupo)
    plan: dict[int, list[str]] = {s: [] for s in range(1, SPRINTS + 1)}
    sprint = 1
    restante = base
    for codigo in orden:
        esfuerzo = catalogo[codigo].esfuerzo
        if restante <= 1e-9 and sprint < SPRINTS:
            sprint += 1
            restante = base
        plan[sprint].append(codigo)
        # Lo que no quepa se arrastra solo durante la simulación.
        restante -= min(esfuerzo, restante)
    return plan


def resumen(grupo: str) -> dict:
    """Cifras de cabecera del proyecto de la filial."""
    catalogo = por_codigo(grupo)
    esfuerzo = _esfuerzo_total(grupo)
    base = capacidad(grupo)
    predictivas = [i for i in catalogo.values() if i.enfoque == "Predictivo"]
    return {
        "iniciativas": len(catalogo),
        "esfuerzo_total": esfuerzo,
        "capacidad_sprint": base,
        "capacidad_total": base * SPRINTS,
        "sprints_necesarios": esfuerzo / base if base else 0.0,
        "cabe_todo": esfuerzo <= base * SPRINTS,
        "esfuerzo_predictivo": sum(i.esfuerzo for i in predictivas),
        "pct_predictivo": (sum(i.esfuerzo for i in predictivas) / esfuerzo
                           if esfuerzo else 0.0),
        "filial": filiales.obtener(grupo).nombre,
        "empleados": _empleados(grupo),
    }
