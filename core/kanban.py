"""Seguimiento del proyecto · Sesión 6.

La Sesión 5 repartía el trabajo en cajas de tiempo. Esta lo deja fluir y se
ocupa de otra cosa: **cómo se sigue un proyecto que ya está en marcha**.

**La idea que sostiene la sesión, y es contraintuitiva.** Empezar más cosas
no termina más cosas. Un equipo con seis tareas abiertas a la vez tarda más
en terminar la primera que el mismo equipo con dos, porque la capacidad se
reparte y porque cambiar de tarea cuesta. Limitar el trabajo en curso —el
WIP— parece que frena y en realidad acelera.

**Pero el mínimo tampoco es la respuesta.** Con una sola tarea abierta, en
cuanto esa tarea se bloquea el equipo entero se para. Y en este proyecto las
tareas se bloquean: las obras esperan al proveedor y los programas esperan a
que alguien responda. **El óptimo está en medio**, es distinto en cada filial
y hay que encontrarlo. Eso es lo que un tablero enseña y una hoja de cálculo
no.

**La ley de Little.** Tiempo de ciclo = trabajo en curso ÷ ritmo de entrega.
No es una metáfora: se cumple sobre los propios datos del ejercicio, y el
módulo la comprueba. Si quieres entregar antes y no puedes trabajar más
rápido, solo te queda empezar menos cosas a la vez.

**El sistema híbrido.** Las iniciativas predictivas no se gestionan con
flujo: tienen proveedor, permiso y fecha, y lo que hay que seguir en ellas es
si llegan a tiempo. Las iterativas sí. Un tablero con las dos mezcladas miente
en las dos direcciones, y por eso la sesión obliga a separarlas.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from core import datos, proyecto

#: Semanas que dura el seguimiento. Doce da para ver la curva y cabe en clase.
SEMANAS = 12

#: La capacidad semanal es la mitad de la de un sprint de la Sesión 5, que
#: duraba dos semanas. Es el mismo equipo mirado con otra lente.
SEMANAS_POR_SPRINT = 2

#: Lo que cuesta la multitarea. Cada tarea abierta de más resta eficiencia al
#: equipo entero: reuniones, cambios de contexto y trabajo a medio hacer que
#: hay que recordar. No es una penalización inventada para que salga la
#: lección: es lo que mide cualquier equipo que lo ha probado.
PENALIZACION_MULTITAREA = 0.07

#: Por debajo de esto no cae la eficiencia por mucho que se abran tareas.
EFICIENCIA_MINIMA = 0.40

#: Cuánto espera cada tipo de iniciativa **desde que se abre**. Es la espera
#: que no depende del equipo: el proveedor que tiene que presupuestar, el
#: permiso que tiene que salir, el proveedor al que hay que pedirle un dato.
#: Determinista, para que los cinco grupos sean comparables.
#:
#: Aquí está el motivo de que el mínimo no sea la respuesta: **mientras una
#: tarea espera, ocupa un hueco del tablero y el equipo no puede avanzarla**.
#: Con una sola tarea abierta, el equipo se queda parado.
BLOQUEO = {
    "Predictivo": {"semanas": 2},
    "Iterativo": {"semanas": 1},
}

#: Límites de WIP que se ofrecen en clase.
LIMITES_OFRECIDOS = [1, 2, 3, 4, 5, 6, 8, 10]


@dataclass(frozen=True)
class Columna:
    codigo: str
    nombre: str
    explicacion: str


COLUMNAS = [
    Columna("pendiente", "Pendiente",
            "Trabajo comprometido que todavía no ha empezado. No consume "
            "nada y no vale nada."),
    Columna("en_curso", "En curso",
            "Lo que el equipo tiene abierto. Aquí es donde se decide todo: "
            "cuantas más cosas haya, más lento avanza cada una."),
    Columna("bloqueado", "Bloqueado",
            "Empezado y detenido por algo que no depende del equipo. Ocupa "
            "sitio en el tablero y no avanza."),
    Columna("hecho", "Hecho",
            "Terminado y entregando valor. Lo único que cuenta de verdad."),
]


def capacidad_semanal(grupo: str) -> float:
    """Puntos que el equipo puede acometer en una semana."""
    return round(proyecto.capacidad(grupo) / SEMANAS_POR_SPRINT, 2)


def eficiencia(wip: int) -> float:
    """Cuánto rinde el equipo con `wip` tareas abiertas a la vez."""
    if wip <= 1:
        return 1.0
    return max(EFICIENCIA_MINIMA, 1.0 - PENALIZACION_MULTITAREA * (wip - 1))


# --------------------------------------------------------------------------
# La simulación de flujo
# --------------------------------------------------------------------------

def simular_flujo(grupo: str, limite_wip: int,
                  orden: list[str] | None = None) -> dict:
    """Deja fluir el trabajo semana a semana con un límite de WIP.

    El tablero tira del trabajo: en cuanto hay hueco, entra la siguiente
    iniciativa de la lista. La capacidad se reparte entre todo lo que está en
    curso y se penaliza por multitarea. Lo bloqueado ocupa sitio y no avanza.

    Nunca lanza excepción por una entrada rara.
    """
    catalogo = proyecto.por_codigo(grupo)
    if orden is None:
        orden = [
            i.codigo for i in sorted(
                catalogo.values(),
                key=lambda x: (-x.valor_por_punto, x.esfuerzo),
            )
        ]
    orden = [c for c in orden if c in catalogo]
    limite = max(1, int(limite_wip or 1))
    capacidad = capacidad_semanal(grupo)

    pendientes = list(orden)
    en_curso: list[str] = []
    progreso: dict[str, float] = {}
    bloqueado_hasta: dict[str, int] = {}
    entrada: dict[str, int] = {}
    salida: dict[str, int] = {}
    historia = []

    for semana in range(1, SEMANAS + 1):
        # 1 · Se tira de trabajo nuevo hasta llenar el límite.
        while len(en_curso) < limite and pendientes:
            codigo = pendientes.pop(0)
            if any(d not in salida for d in catalogo[codigo].depende_de):
                # No se puede empezar todavía: vuelve al final de la cola.
                pendientes.append(codigo)
                if all(any(d not in salida for d in catalogo[c].depende_de)
                       for c in pendientes):
                    break
                continue
            en_curso.append(codigo)
            entrada[codigo] = semana
            # Al abrirla se descubre que hay que esperar a alguien.
            bloqueado_hasta[codigo] = semana + BLOQUEO[
                catalogo[codigo].enfoque
            ]["semanas"]

        # 2 · Se reparte la capacidad entre lo que puede avanzar.
        activas = [c for c in en_curso if bloqueado_hasta.get(c, 0) < semana]
        bloqueadas = [c for c in en_curso if c not in activas]

        if activas:
            disponible = capacidad * eficiencia(len(en_curso))
            por_tarea = disponible / len(activas)
            for codigo in list(activas):
                iniciativa = catalogo[codigo]
                progreso[codigo] = progreso.get(codigo, 0.0) + por_tarea
                if progreso[codigo] >= iniciativa.esfuerzo:
                    en_curso.remove(codigo)
                    salida[codigo] = semana

        historia.append({
            "semana": semana,
            "pendiente": len(pendientes),
            "en_curso": len([c for c in en_curso
                             if bloqueado_hasta.get(c, 0) < semana]),
            "bloqueado": len(bloqueadas),
            "hecho": len(salida),
            "wip": len(en_curso),
            "valor_acumulado": sum(catalogo[c].valor for c in salida),
            "eficiencia": round(eficiencia(len(en_curso)), 3),
        })

    ciclos = [salida[c] - entrada[c] + 1 for c in salida]
    terminadas = len(salida)
    return {
        "limite_wip": limite,
        "historia": historia,
        "terminadas": sorted(salida, key=lambda c: salida[c]),
        "sin_terminar": [c for c in catalogo if c not in salida],
        "en_curso_al_final": list(en_curso),
        "valor_entregado": sum(catalogo[c].valor for c in salida),
        "valor_total": sum(i.valor for i in catalogo.values()),
        "tiempo_de_ciclo": round(sum(ciclos) / len(ciclos), 2) if ciclos else 0.0,
        "throughput": round(terminadas / SEMANAS, 3),
        "wip_medio": round(
            sum(h["wip"] for h in historia) / len(historia), 2
        ),
        "eficiencia_media": round(
            sum(h["eficiencia"] for h in historia) / len(historia), 3
        ),
        "capacidad_semanal": capacidad,
        "progreso": progreso,
        "entrada": entrada,
        "salida": salida,
    }


def ley_de_little(resultado: dict) -> dict:
    """Comprueba la ley de Little sobre el propio resultado.

    Tiempo de ciclo = trabajo en curso ÷ ritmo de entrega. No es una
    metáfora ni una regla aproximada: es una identidad que se cumple en
    cualquier sistema estable, y verlo salir de sus propios números es lo
    que convence a un alumno de que limitar el WIP no es una moda.
    """
    throughput = resultado["throughput"]
    previsto = resultado["wip_medio"] / throughput if throughput else 0.0
    real = resultado["tiempo_de_ciclo"]
    return {
        "wip_medio": resultado["wip_medio"],
        "throughput": throughput,
        "ciclo_previsto": round(previsto, 2),
        "ciclo_real": real,
        "desviacion": round(abs(previsto - real) / real, 3) if real else 0.0,
    }


@lru_cache(maxsize=None)
def _barrido(grupo: str) -> tuple[dict, ...]:
    filas = []
    for limite in LIMITES_OFRECIDOS:
        resultado = simular_flujo(grupo, limite)
        filas.append({
            "limite_wip": limite,
            "terminadas": len(resultado["terminadas"]),
            "valor_entregado": resultado["valor_entregado"],
            "tiempo_de_ciclo": resultado["tiempo_de_ciclo"],
            "throughput": resultado["throughput"],
            "eficiencia_media": resultado["eficiencia_media"],
        })
    return tuple(filas)


def barrido_wip(grupo: str) -> pd.DataFrame:
    """El resultado con cada límite de WIP posible.

    Es la tabla que descubre la sesión: ni uno ni diez, sino un número de en
    medio que además no es el mismo en las cinco filiales.
    """
    return pd.DataFrame(list(_barrido(grupo)))


def wip_optimo(grupo: str) -> int:
    """El límite que más valor entrega. En caso de empate, el más bajo."""
    tabla = _barrido(grupo)
    mejor = max(f["valor_entregado"] for f in tabla)
    return min(f["limite_wip"] for f in tabla if f["valor_entregado"] == mejor)


def limpiar_cache() -> None:
    _barrido.cache_clear()


datos.registrar_cache(limpiar_cache)


# --------------------------------------------------------------------------
# El sistema híbrido
# --------------------------------------------------------------------------

#: Cuántas semanas de margen se conceden a una iniciativa predictiva sobre lo
#: que tardaría sin bloqueos. Es el colchón que se compromete con el comité.
MARGEN_HITO = 3


def compromiso(grupo: str, codigo: str) -> int:
    """Semana en la que una iniciativa predictiva se compromete a terminar.

    Se calcula sobre su esfuerzo y la capacidad del equipo, más el bloqueo
    que ya se sabe que va a sufrir y un margen. Es lo que un jefe de proyecto
    pone en un cronograma, y es una promesa que alguien va a comprobar.
    """
    iniciativa = proyecto.por_codigo(grupo)[codigo]
    capacidad = capacidad_semanal(grupo)
    semanas = iniciativa.esfuerzo / capacidad if capacidad else 0.0
    semanas += BLOQUEO[iniciativa.enfoque]["semanas"]
    return int(round(semanas + MARGEN_HITO))


def evaluar_hibrido(grupo: str, en_flujo: list[str],
                    limite_wip: int) -> dict:
    """Mide el sistema híbrido con dos varas distintas, que es el punto.

    Lo que va a flujo se juzga por tiempo de ciclo y por lo que entrega. Lo
    que va con fecha se juzga por si llega a tiempo. Usar el mismo indicador
    para las dos mitades es lo que hace que los cuadros de mando de proyecto
    no sirvan para nada.
    """
    catalogo = proyecto.por_codigo(grupo)
    en_flujo = [c for c in (en_flujo or []) if c in catalogo]
    con_fecha = [c for c in catalogo if c not in en_flujo]

    resultado = simular_flujo(grupo, limite_wip, orden=en_flujo)

    # Las iniciativas con fecha se ejecutan con la capacidad que sobra.
    capacidad_libre = max(
        0.0,
        capacidad_semanal(grupo) * SEMANAS
        - sum(catalogo[c].esfuerzo for c in resultado["terminadas"]),
    )
    cumplidos, incumplidos = [], []
    gastado = 0.0
    for codigo in sorted(con_fecha, key=lambda c: catalogo[c].esfuerzo):
        iniciativa = catalogo[codigo]
        gastado += iniciativa.esfuerzo
        if gastado <= capacidad_libre:
            cumplidos.append(codigo)
        else:
            incumplidos.append(codigo)

    # Un error frecuente: meter obras en el tablero de flujo. Las obras no
    # fluyen, esperan, y ocupan un hueco de WIP mientras esperan.
    obras_en_flujo = [c for c in en_flujo
                      if catalogo[c].enfoque == "Predictivo"]
    iterativas_con_fecha = [c for c in con_fecha
                            if catalogo[c].enfoque == "Iterativo"]

    total_hitos = len(con_fecha)
    return {
        "en_flujo": en_flujo,
        "con_fecha": con_fecha,
        "flujo": resultado,
        "hitos_cumplidos": cumplidos,
        "hitos_incumplidos": incumplidos,
        "puntualidad": len(cumplidos) / total_hitos if total_hitos else 1.0,
        "obras_en_flujo": obras_en_flujo,
        "iterativas_con_fecha": iterativas_con_fecha,
        "valor_total_entregado": (
            resultado["valor_entregado"]
            + sum(catalogo[c].valor for c in cumplidos)
        ),
        "valor_posible": sum(i.valor for i in catalogo.values()),
    }


def reparto_recomendado(grupo: str) -> list[str]:
    """Lo que haría un buen jefe de proyecto: a flujo, lo iterativo."""
    catalogo = proyecto.por_codigo(grupo)
    return [c for c, i in catalogo.items() if i.enfoque == "Iterativo"]


def tabla_tablero(grupo: str, resultado: dict) -> pd.DataFrame:
    """El estado final de cada iniciativa, para pintar el tablero."""
    catalogo = proyecto.por_codigo(grupo)
    filas = []
    for codigo, iniciativa in catalogo.items():
        if codigo in resultado["salida"]:
            estado = "Hecho"
            semana = resultado["salida"][codigo]
        elif codigo in resultado["entrada"]:
            estado = "En curso"
            semana = resultado["entrada"][codigo]
        else:
            estado = "Pendiente"
            semana = 0
        avance = min(1.0, resultado["progreso"].get(codigo, 0.0)
                     / iniciativa.esfuerzo)
        filas.append({
            "codigo": codigo,
            "nombre": iniciativa.nombre,
            "enfoque": iniciativa.enfoque,
            "esfuerzo": iniciativa.esfuerzo,
            "valor": iniciativa.valor,
            "estado": estado,
            "semana": semana,
            "avance": round(avance, 2),
            "ciclo": (resultado["salida"][codigo]
                      - resultado["entrada"][codigo] + 1)
            if codigo in resultado["salida"] else None,
        })
    return pd.DataFrame(filas)
