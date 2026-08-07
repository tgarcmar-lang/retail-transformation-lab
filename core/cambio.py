"""Gestión del cambio · Sesión 7.

Durante seis sesiones los grupos han optimizado, presupuestado, priorizado y
medido. Todo racional y todo correcto. Esta sesión introduce lo único que las
seis anteriores no tenían: **gente**.

**La verdad incómoda del curso.** Su plan aterriza sobre personas concretas
que tienen sus propias razones para no querer. Y el patrón se repite: **quien
tiene que cambiar casi nunca es quien se lleva el beneficio**. Se le pide al
personal de tienda que prepare paquetes para que bajen las emisiones de
reparto; al conductor, que cambie su ruta para que mejore un indicador de la
central. La resistencia rara vez es irracional: es que el esfuerzo y el
beneficio caen en manos distintas.

**La brecha que cierra el curso.** En la Sesión 5 midieron valor *entregado*.
Aquí se mide valor *adoptado*, que no es lo mismo. Una instalación nueva
funciona la quiera la gente o no: es una máquina. Un cambio de hábito solo
funciona si lo adoptan. Por eso **se puede entregar un proyecto al 100 % y no
cambiar nada**, y por eso las filiales cuyo plan se apoya en el comportamiento
están mucho más expuestas que las que compraron equipos.

**Por qué el mandato no es la respuesta.** Ordenarlo desde arriba sube la
adopción muy deprisa y después se cae, porque nadie ha cambiado de opinión:
solo ha dejado de discutir. Participar es lento y se sostiene. El modelo lo
refleja, y descubrirlo con su propio plan delante vale más que leerlo.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from core import datos, proyecto

#: Meses que dura el seguimiento de la adopción.
MESES = 12

#: Adopción que alcanza un cambio si no se hace nada por gestionarlo. No es
#: cero: siempre hay quien se apunta solo. Tampoco es alta.
ADOPCION_INERCIAL = 0.25


@dataclass(frozen=True)
class Rol:
    codigo: str
    nombre: str
    descripcion: str
    #: Cuánta gente de la filial pertenece a este rol, en proporción.
    peso: float
    #: Poder para parar o impulsar el cambio, de 1 a 5.
    poder: int


ROLES: list[Rol] = [
    Rol("direccion", "Dirección de la filial",
        "Aprueba el presupuesto y responde ante la central. Quiere que el "
        "plan salga porque lo ha firmado.", 0.01, 5),
    Rol("jefes_tienda", "Jefes de tienda",
        "Responden de las ventas de su tienda. Cualquier cosa que quite "
        "tiempo a vender les cuesta su propio objetivo.", 0.04, 4),
    Rol("personal_tienda", "Personal de tienda",
        "Quien acaba haciendo el trabajo nuevo. Casi nunca se le pregunta y "
        "casi siempre es quien sabe por qué algo no va a funcionar.", 0.55, 2),
    Rol("conductores", "Conductores y reparto",
        "Rutas, horarios y a menudo una parte del sueldo ligada al número de "
        "servicios. Un cambio de ruta les toca el bolsillo.", 0.12, 3),
    Rol("almacen", "Personal de almacén",
        "Preparación, carga y devoluciones. Lo que cambia aguas arriba les "
        "llega a ellos convertido en más manipulación.", 0.18, 2),
    Rol("compras", "Equipo de compras",
        "Su bonus se mide en precio y en plazo. Pedirles criterios "
        "ambientales es pedirles que compliquen su propio objetivo.", 0.03, 4),
    Rol("mantenimiento", "Mantenimiento e instalaciones",
        "Ejecuta las obras. Suele estar a favor del proyecto y en contra del "
        "calendario, porque además tiene que apagar los fuegos del día.",
        0.07, 3),
]

POR_ROL = {rol.codigo: rol for rol in ROLES}


#: Para cada iniciativa: cuánto depende de que la gente cambie de conducta y
#: a qué roles toca. **Es el contenido de la sesión**, así que está escrito y
#: razonado, no deducido de los datos.
#:
#: La dependencia va de 0 a 1. Un 0,05 es una máquina que funciona sola en
#: cuanto se instala; un 0,90 es un cambio que solo existe si miles de gestos
#: diarios cambian.
CONDUCTA = {
    "c_refrigerante": (0.05, ("mantenimiento",),
                       "Es una máquina. Una vez instalada funciona aunque a "
                       "nadie le guste, y nadie tiene que hacer nada distinto "
                       "cada mañana."),
    "c_energia": (0.10, ("mantenimiento", "jefes_tienda"),
                  "Iluminación y equipos funcionan solos. Lo poco que "
                  "depende de la gente es que no se desactiven los "
                  "automatismos por comodidad."),
    "c_electrificacion": (0.25, ("conductores", "mantenimiento"),
                          "La furgoneta eléctrica emite menos por sí sola, "
                          "pero hay que planificar la recarga y eso cambia "
                          "la rutina del conductor."),
    "c_vacio": (0.50, ("conductores", "almacen"),
                "Buscar cargas de retorno exige que alguien las busque, las "
                "negocie y las encaje. No hay ninguna máquina que lo haga."),
    "c_carga": (0.60, ("conductores", "almacen", "jefes_tienda"),
                "Cambiar la frecuencia de reparto a las tiendas altera el "
                "trabajo de todos los eslabones, y cada tienda tiene su "
                "manera de recibir."),
    "c_consolidacion": (0.85, ("personal_tienda", "jefes_tienda"),
                        "Solo funciona si el personal de tienda prepara los "
                        "pedidos y los entrega bien, y si el jefe de tienda "
                        "no lo considera una molestia que le quita ventas."),
    "m_segregacion": (0.90, ("personal_tienda", "almacen"),
                      "Depende de miles de gestos diarios de mucha gente. "
                      "Es el cambio más conductual de todo el proyecto."),
    "m_embalaje": (0.50, ("almacen", "compras"),
                   "El rediseño se hace una vez, pero hay que usarlo bien y "
                   "exigírselo a los proveedores cada pedido."),
    "m_merma": (0.70, ("jefes_tienda", "personal_tienda"),
                "Previsión, rebaja a tiempo y control diario. Y además "
                "obliga a registrar una cifra que hoy conviene disimular."),
    "m_devoluciones": (0.40, ("personal_tienda",),
                       "Las fichas de producto se mejoran una vez; mantener "
                       "la calidad después ya depende de la gente."),
    "m_retornable": (0.50, ("almacen", "conductores", "personal_tienda"),
                     "El circuito se compra, pero si las cajas no vuelven, "
                     "no hay circuito. Y devolverlas es trabajo de alguien."),
    "m_reacondicionado": (0.40, ("almacen",),
                          "El taller se monta y luego hay que operarlo con "
                          "criterio: qué se repara y qué no."),
    "r_medicion": (0.40, ("jefes_tienda", "almacen", "compras"),
                   "El sistema se instala, pero los datos los meten "
                   "personas, y un dato mal metido es peor que no tenerlo."),
    "r_proveedores_esg": (0.70, ("compras",),
                          "Exige que el equipo de compras cambie sus "
                          "criterios de decisión, que es justo lo que se les "
                          "premia por no hacer."),
}


# --------------------------------------------------------------------------
# Las palancas de gestión del cambio
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class PalancaCambio:
    codigo: str
    nombre: str
    descripcion: str
    #: Cuánto sube la adopción a largo plazo.
    techo: float
    #: Cómo de rápido llega. Alto = rápido.
    velocidad: float
    #: Cuánto se desinfla con el tiempo. Alto = se cae.
    decaimiento: float
    coste_relativo: float
    ayuda: str


PALANCAS: list[PalancaCambio] = [
    PalancaCambio(
        "mandato", "Ordenarlo desde dirección",
        "Una instrucción de la dirección: esto se hace, y punto. Es "
        "gratis, es inmediato y no requiere convencer a nadie.",
        techo=0.26, velocidad=0.90, decaimiento=0.55, coste_relativo=0.05,
        ayuda="Sube muy deprisa y se cae. Nadie ha cambiado de opinión: solo "
              "ha dejado de discutir mientras alguien mira.",
    ),
    PalancaCambio(
        "comunicacion", "Explicar el porqué",
        "Contar para qué sirve el cambio, qué problema resuelve y qué pasa "
        "si no se hace. No convence solo, pero sin esto nada más funciona.",
        techo=0.13, velocidad=0.60, decaimiento=0.25, coste_relativo=0.10,
        ayuda="Barata y necesaria. Por sí sola cambia poco: saber por qué "
              "hay que hacer algo no es lo mismo que saber hacerlo.",
    ),
    PalancaCambio(
        "formacion", "Formar a quien tiene que hacerlo",
        "Enseñar el procedimiento nuevo a quien va a ejecutarlo, con tiempo "
        "y en su puesto.",
        techo=0.21, velocidad=0.45, decaimiento=0.15, coste_relativo=0.25,
        ayuda="Quita el «no sé hacerlo», que es la mitad de la resistencia "
              "que se confunde con mala voluntad.",
    ),
    PalancaCambio(
        "incentivos", "Alinear los objetivos",
        "Cambiar lo que se mide y lo que se premia para que el esfuerzo y "
        "el beneficio caigan en la misma persona.",
        techo=0.26, velocidad=0.55, decaimiento=0.20, coste_relativo=0.30,
        ayuda="Es la palanca que ataca la causa: nadie trabaja de más para "
              "el indicador de otro. También la más incómoda de negociar.",
    ),
    PalancaCambio(
        "participacion", "Diseñarlo con ellos",
        "Sentar a quien va a ejecutar el cambio a decidir cómo se hace, "
        "antes de decidirlo.",
        techo=0.32, velocidad=0.25, decaimiento=0.05, coste_relativo=0.35,
        ayuda="Lo más lento de arrancar y lo único que aguanta. Además "
              "suele mejorar el plan, porque quien hace el trabajo sabe "
              "cosas que no están en ninguna hoja de cálculo.",
    ),
    PalancaCambio(
        "piloto", "Empezar por una tienda",
        "Probarlo en un sitio, medirlo y enseñar el resultado al resto en "
        "vez de anunciarlo.",
        techo=0.19, velocidad=0.35, decaimiento=0.10, coste_relativo=0.20,
        ayuda="Convierte una promesa en una prueba. Y si sale mal, sale mal "
              "en una tienda y no en treinta.",
    ),
]

POR_CODIGO = {p.codigo: p for p in PALANCAS}

#: Presupuesto de gestión del cambio, sobre el esfuerzo del proyecto de la
#: Sesión 5. Es pequeño a propósito: en los proyectos reales también lo es, y
#: por eso fracasan tantos. Calibrado para que el plan completo cueste algo
#: más del doble de lo disponible: hay que elegir.
PRESUPUESTO_SOBRE_PROYECTO = 0.12

#: Escala de los costes. Con esto, comprarlo todo cuesta unas 2,3 veces el
#: presupuesto en las cinco filiales.
COSTE_UNITARIO = 0.22


# --------------------------------------------------------------------------
# La adopción
# --------------------------------------------------------------------------

def curva(plan: dict[str, float], mes: int) -> float:
    """Adopción alcanzada en un mes dado, de 0 a 1.

    Cada palanca aporta su techo, llega a su ritmo y se desinfla a su
    velocidad. El mandato sube casi del todo el primer mes y se cae; la
    participación tarda medio año y se queda.
    """
    total = ADOPCION_INERCIAL
    for palanca in PALANCAS:
        intensidad = max(0.0, min(1.0, float(plan.get(palanca.codigo, 0.0) or 0.0)))
        if intensidad <= 0:
            continue
        # Cuánto ha llegado ya de lo que esta palanca puede dar.
        llegada = 1 - (1 - palanca.velocidad) ** mes
        # Cuánto se ha desinflado de lo que había llegado.
        caida = palanca.decaimiento * (1 - (1 - 0.35) ** max(0, mes - 2))
        total += palanca.techo * intensidad * llegada * (1 - caida)
    return max(0.0, min(1.0, total))


def coste(plan: dict[str, float], grupo: str) -> float:
    """Lo que cuesta el plan de cambio, en puntos de esfuerzo del proyecto."""
    base = proyecto.resumen(grupo)["esfuerzo_total"] * COSTE_UNITARIO
    return sum(
        base * p.coste_relativo
        * max(0.0, min(1.0, float(plan.get(p.codigo, 0.0) or 0.0)))
        for p in PALANCAS
    )


def presupuesto(grupo: str) -> float:
    return round(
        proyecto.resumen(grupo)["esfuerzo_total"] * PRESUPUESTO_SOBRE_PROYECTO, 1
    )


@lru_cache(maxsize=None)
def _entregado(grupo: str) -> tuple[str, ...]:
    """Las iniciativas del plan de la filial.

    Se toma el backlog completo y no solo lo que dio tiempo a entregar en la
    Sesión 5: lo que se juzga aquí es el plan, y el plan es entero. Además,
    así la exposición refleja el mix real de cada filial —quien apostó por
    máquinas frente a quien apostó por comportamiento— en vez de depender de
    en qué orden se ejecutó.
    """
    return tuple(i.codigo for i in proyecto.backlog(grupo))


def exposicion(grupo: str) -> dict:
    """Cuánto del valor entregado depende de que la gente cambie.

    Es la cifra que diferencia a las cinco filiales: quien compró máquinas
    está a salvo y quien apostó por el comportamiento, no.
    """
    catalogo = proyecto.por_codigo(grupo)
    entregadas = _entregado(grupo)
    automatico = conductual = 0.0
    for codigo in entregadas:
        valor = catalogo[codigo].valor
        dependencia = CONDUCTA.get(codigo, (0.5, (), ""))[0]
        conductual += valor * dependencia
        automatico += valor * (1 - dependencia)
    total = automatico + conductual
    return {
        "entregadas": list(entregadas),
        "valor_entregado": round(total, 1),
        "valor_automatico": round(automatico, 1),
        "valor_conductual": round(conductual, 1),
        "pct_conductual": conductual / total if total else 0.0,
    }


def simular(grupo: str, plan: dict[str, float]) -> dict:
    """Qué parte del valor entregado se adopta de verdad.

    Nunca lanza excepción por una entrada rara.
    """
    catalogo = proyecto.por_codigo(grupo)
    entregadas = _entregado(grupo)
    exp = exposicion(grupo)

    historia = []
    for mes in range(1, MESES + 1):
        adopcion = curva(plan, mes)
        realizado = sum(
            catalogo[c].valor * (
                (1 - CONDUCTA.get(c, (0.5, (), ""))[0])
                + CONDUCTA.get(c, (0.5, (), ""))[0] * adopcion
            )
            for c in entregadas
        )
        historia.append({
            "mes": mes,
            "adopcion": round(adopcion, 3),
            "valor_realizado": round(realizado, 1),
        })

    final = historia[-1]
    detalle = []
    for codigo in entregadas:
        dependencia, roles, porque = CONDUCTA.get(codigo, (0.5, (), ""))
        valor = catalogo[codigo].valor
        realizado = valor * ((1 - dependencia) + dependencia * final["adopcion"])
        detalle.append({
            "codigo": codigo,
            "nombre": catalogo[codigo].nombre,
            "valor": valor,
            "dependencia": dependencia,
            "roles": list(roles),
            "porque": porque,
            "realizado": round(realizado, 2),
            "perdido": round(valor - realizado, 2),
        })
    detalle.sort(key=lambda f: -f["perdido"])

    gastado = coste(plan, grupo)
    disponible = presupuesto(grupo)
    return {
        "historia": historia,
        "detalle": detalle,
        "adopcion_final": final["adopcion"],
        "adopcion_maxima": max(h["adopcion"] for h in historia),
        "mes_del_maximo": max(historia, key=lambda h: h["adopcion"])["mes"],
        "valor_entregado": exp["valor_entregado"],
        "valor_realizado": final["valor_realizado"],
        "valor_perdido": round(exp["valor_entregado"] - final["valor_realizado"], 1),
        "brecha": (1 - final["valor_realizado"] / exp["valor_entregado"]
                   if exp["valor_entregado"] else 0.0),
        "pct_conductual": exp["pct_conductual"],
        "coste": round(gastado, 1),
        "presupuesto": disponible,
        "dentro_de_presupuesto": gastado <= disponible + 1e-6,
        "se_desinfla": final["adopcion"] < max(h["adopcion"] for h in historia) - 0.02,
    }


def mapa_de_actores(grupo: str) -> pd.DataFrame:
    """Cuánto le toca a cada rol y cuánto poder tiene para pararlo.

    El eje de impacto se calcula con el valor de las iniciativas entregadas
    que caen sobre ese rol, así que sale distinto en cada filial.
    """
    catalogo = proyecto.por_codigo(grupo)
    entregadas = _entregado(grupo)

    carga = {rol.codigo: 0.0 for rol in ROLES}
    afectan = {rol.codigo: [] for rol in ROLES}
    for codigo in entregadas:
        dependencia, roles, _ = CONDUCTA.get(codigo, (0.5, (), ""))
        if not roles:
            continue
        reparto = catalogo[codigo].valor * dependencia / len(roles)
        for rol in roles:
            carga[rol] += reparto
            afectan[rol].append(catalogo[codigo].nombre)

    maximo = max(carga.values()) or 1.0
    filas = []
    for rol in ROLES:
        filas.append({
            "rol": rol.codigo,
            "nombre": rol.nombre,
            "descripcion": rol.descripcion,
            "poder": rol.poder,
            "impacto": round(1 + 4 * carga[rol.codigo] / maximo, 2),
            "carga": round(carga[rol.codigo], 2),
            "iniciativas": afectan[rol.codigo],
            "empleados": int(round(proyecto.resumen(grupo)["empleados"] * rol.peso)),
        })
    return pd.DataFrame(filas).sort_values(
        "impacto", ascending=False, ignore_index=True
    )


def plan_recomendado() -> dict[str, float]:
    """Lo que haría alguien que ha hecho esto antes: nada de mandato."""
    return {"comunicacion": 1.0, "formacion": 0.6, "participacion": 1.0,
            "piloto": 0.6, "incentivos": 0.4}


def plan_de_mandato() -> dict[str, float]:
    """La tentación: ordenarlo y comunicarlo. Barato, rápido y se cae."""
    return {"mandato": 1.0, "comunicacion": 1.0}


def limpiar_cache() -> None:
    _entregado.cache_clear()


datos.registrar_cache(limpiar_cache)
