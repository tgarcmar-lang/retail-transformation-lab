"""Alcance 3: el inventario que la Sesión 2 no estaba mirando.

Los alcances 1 y 2 de RetailNova rondan las 35.000 t. El alcance 3 es un
orden de magnitud mayor. No es un defecto del caso: es lo que le pasa a
cualquier minorista. Un distribuidor casi no fabrica nada, así que casi todo
lo que emite lo emite otro por encargo suyo.

**Por qué vive en un módulo aparte y con su propio objetivo.** El ejercicio
del 25 % está calibrado sobre los alcances 1 y 2, y esa calibración es lo
que hace que las cinco filiales tengan un reto equivalente. Si el alcance 3
entrase en el denominador, el 25 % pasaría de exigente a imposible de la
noche a la mañana. Así que se lleva como inventario separado, con su propio
objetivo y su propio presupuesto — que además es lo que hacen las empresas
de verdad cuando publican objetivos climáticos.

**Método: estimación por gasto.** Se multiplica lo comprado por un factor
medio de la categoría y por la intensidad del país donde se fabrica. Es lo
que hace una empresa que empieza, y tiene un defecto que conviene que el
alumno vea: si negocias un descuento con el proveedor, tu huella baja sin
que haya cambiado nada físico. El método sirve para saber dónde mirar, no
para presumir de decimales.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from core import datos, kpis
from datos.retailnova import parametros as p

#: Reducción que se les pide sobre el alcance 3. Es menos que el 25 % de los
#: alcances 1 y 2, y no por benevolencia: sobre el alcance 3 no se manda, se
#: negocia. Se reduce convenciendo a un proveedor, cambiando de proveedor o
#: comprando otra cosa, y las tres son lentas.
OBJETIVO3 = 0.10

#: Presupuesto del plan de alcance 3, sobre las ventas de un año. Es más
#: pequeño que el de los alcances 1 y 2 a propósito: aquí no se compran
#: furgonetas ni placas, se financian programas con proveedores. Está
#: calibrado en `tests/test_alcance3.py`.
PRESUPUESTO3_SOBRE_VENTAS = 0.0045

#: Países que en el caso son "cadena larga".
ASIA = kpis.ASIA

#: Origen al que se relocaliza cuando se acerca la cadena. No es España:
#: traerlo todo a casa no es realista en textil. Turquía es el destino
#: habitual del nearshoring europeo en moda.
ORIGEN_CERCANO = "Turquía"


# --------------------------------------------------------------------------
# El inventario
# --------------------------------------------------------------------------

def compras_detalladas(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """Compras del año por categoría y origen, con sus emisiones.

    Devuelve una fila por combinación de categoría y país, con las dos
    piezas del alcance 3 que dependen de las compras: lo que emite fabricar
    lo comprado (categoría 1) y lo que emite traerlo (categoría 4).
    """
    anio = anio or datos.ultimo_anio()
    compras = datos.de_la_filial("compras", grupo)
    compras = compras[compras["mes"].dt.year == anio]

    tabla = (compras.groupby(["categoria", "pais_origen"], as_index=False)
             ["importe_eur"].sum())

    tabla["factor_gasto"] = tabla["categoria"].map(p.FACTOR_GASTO_CATEGORIA)
    tabla["intensidad_origen"] = tabla["pais_origen"].map(p.INTENSIDAD_ORIGEN)
    tabla["bienes_t"] = (
        tabla["importe_eur"] * tabla["factor_gasto"]
        * tabla["intensidad_origen"] / 1_000
    )

    tabla["toneladas_mercancia"] = (
        tabla["importe_eur"] / tabla["categoria"].map(p.VALOR_POR_TONELADA)
    )
    tabla["distancia_km"] = tabla["pais_origen"].map(p.DISTANCIA_ORIGEN_KM)
    tabla["factor_modal"] = tabla["pais_origen"].map(_factor_modal_medio)
    tabla["transporte_t"] = (
        tabla["toneladas_mercancia"] * tabla["distancia_km"]
        * tabla["factor_modal"] / 1_000
    )

    tabla["pct_aereo"] = tabla["pais_origen"].map(
        lambda pais: p.MIX_MODAL[pais].get("aereo", 0.0)
    )
    tabla["total_t"] = tabla["bienes_t"] + tabla["transporte_t"]
    return tabla.sort_values("total_t", ascending=False, ignore_index=True)


def _factor_modal_medio(pais: str) -> float:
    """Emisiones por tonelada y kilómetro, mezclando los modos de ese origen."""
    return sum(
        peso * p.FACTOR_MODO[modo] for modo, peso in p.MIX_MODAL[pais].items()
    )


def residuos_t(grupo: str, anio: int | None = None) -> float:
    """Emisiones del tratamiento de residuos (categoría 5).

    Es la parte pequeña del alcance 3, y está aquí justamente por eso: el
    grupo que quiera empezar por los residuos porque es lo que suena a
    sostenibilidad tiene que poder ver que apenas mueve la aguja.
    """
    resumen = kpis.residuos_resumen(grupo, anio)
    kg = resumen["total_t"] * 1_000
    reciclado = resumen["pct_reciclado"]
    return (
        kg * reciclado * p.FACTOR_RESIDUO_RECICLADO
        + kg * (1 - reciclado) * p.FACTOR_RESIDUO_VERTEDERO
    ) / 1_000


def inventario(grupo: str, anio: int | None = None) -> dict:
    """El inventario completo de la filial, con los tres alcances.

    Es la tabla que abre el último paso de la Sesión 2, y la que cambia la
    conversación: hasta aquí el grupo creía tener una huella de unas miles
    de toneladas.
    """
    anio = anio or datos.ultimo_anio()
    huella = kpis.huella(grupo, anio)
    alcance1 = float(huella[huella["alcance"] == 1]["co2e_t"].sum())
    alcance2 = float(huella[huella["alcance"] == 2]["co2e_t"].sum())

    compras = compras_detalladas(grupo, anio)
    bienes = float(compras["bienes_t"].sum())
    transporte = float(compras["transporte_t"].sum())
    residuos = residuos_t(grupo, anio)
    alcance3 = bienes + transporte + residuos

    total = alcance1 + alcance2 + alcance3
    return {
        "alcance1_t": alcance1,
        "alcance2_t": alcance2,
        "alcance3_t": alcance3,
        "bienes_t": bienes,
        "transporte_t": transporte,
        "residuos_t": residuos,
        "total_t": total,
        "operativo_t": alcance1 + alcance2,
        "pct_operativo": (alcance1 + alcance2) / total if total else 0.0,
        "pct_alcance3": alcance3 / total if total else 0.0,
        "objetivo3_t": alcance3 * OBJETIVO3,
        "veces_mayor": alcance3 / (alcance1 + alcance2) if alcance1 + alcance2 else 0.0,
    }


def desglose(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """El inventario en forma de tabla, listo para pintar."""
    inv = inventario(grupo, anio)
    filas = [
        ("Alcance 1 · Lo que quemáis vosotros", 1, inv["alcance1_t"]),
        ("Alcance 2 · La electricidad que compráis", 2, inv["alcance2_t"]),
        ("Alcance 3 · Fabricar lo que vendéis", 3, inv["bienes_t"]),
        ("Alcance 3 · Traerlo hasta aquí", 3, inv["transporte_t"]),
        ("Alcance 3 · Tratar vuestros residuos", 3, inv["residuos_t"]),
    ]
    tabla = pd.DataFrame(filas, columns=["concepto", "alcance", "co2e_t"])
    tabla["pct"] = tabla["co2e_t"] / tabla["co2e_t"].sum()
    return tabla


def compras_por_pais(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """Emisiones del alcance 3 agrupadas por país de origen."""
    tabla = compras_detalladas(grupo, anio)
    por_pais = tabla.groupby("pais_origen", as_index=False).agg(
        importe_eur=("importe_eur", "sum"),
        bienes_t=("bienes_t", "sum"),
        transporte_t=("transporte_t", "sum"),
        toneladas_mercancia=("toneladas_mercancia", "sum"),
    )
    por_pais["total_t"] = por_pais["bienes_t"] + por_pais["transporte_t"]
    por_pais["kg_por_euro"] = por_pais["total_t"] * 1_000 / por_pais["importe_eur"]
    por_pais["pct_importe"] = por_pais["importe_eur"] / por_pais["importe_eur"].sum()
    return por_pais.sort_values("total_t", ascending=False, ignore_index=True)


# --------------------------------------------------------------------------
# Las palancas del alcance 3
# --------------------------------------------------------------------------

#: Cuánta de la mercancía que hoy vuela se puede bajar a barco. No es todo:
#: parte del avión es reposición urgente de campaña, y renunciar a ella
#: significa quedarse sin producto en tienda.
DESVIO_AEREO_MAXIMO = 0.70

#: Lo que cuesta el cambio modal, sobre el valor de la mercancía desviada.
#: El barco es más barato que el avión: lo que se paga aquí no es flete, es
#: el stock adicional que hay que financiar cuando el plazo se triplica.
COSTE_MODAL_SOBRE_VALOR = 0.062

#: Proporción de la compra asiática que se puede acercar a Turquía en tres
#: años. Más sería mentir: cambiar de proveedor en textil lleva campañas.
RELOCALIZACION_MAXIMA = 0.40

#: Reducción máxima del factor de los proveedores con los que se trabaja.
#: Un programa serio de proveedores no descarboniza una fábrica: consigue
#: que mida, que ponga objetivos y que cambie lo barato.
MEJORA_PROVEEDORES_MAXIMA = 0.12

#: Lo que cuesta ese programa, sobre el gasto con los proveedores incluidos.
COSTE_PROVEEDORES_SOBRE_GASTO = 0.0085


@dataclass(frozen=True)
class Palanca3:
    codigo: str
    nombre: str
    descripcion: str
    unidad: str
    ayuda: str


PALANCAS3: list[Palanca3] = [
    Palanca3(
        codigo="modal",
        nombre="Bajar del avión al barco",
        descripcion=(
            "Traer en barco la mercancía asiática que hoy llega en avión. "
            "El barco tarda cinco veces más y emite unas cuarenta veces menos "
            "por tonelada y kilómetro."
        ),
        unidad="% de la mercancía aérea que pasa a barco",
        ayuda=(
            "Mirad qué parte de vuestras compras viene de Asia. Si compráis "
            "poco allí, esta palanca casi no os da nada. Si compráis mucho, "
            "es la tonelada más barata de todo el caso."
        ),
    ),
    Palanca3(
        codigo="origen",
        nombre="Acercar la cadena de suministro",
        descripcion=(
            "Trasladar parte de la compra asiática a proveedores del "
            "Mediterráneo. Se acorta el viaje y se fabrica con una red "
            "eléctrica menos intensiva, pero la mercancía sale más cara."
        ),
        unidad="% de la compra asiática que se relocaliza",
        ayuda=(
            "Es la palanca que mejor suena y la que peor rinde por euro. "
            "Comprar en Turquía cuesta alrededor de un 15 % más que comprar "
            "en China: ese sobrecoste os lo come el presupuesto entero."
        ),
    ),
    Palanca3(
        codigo="proveedores",
        nombre="Programa de proveedores",
        descripcion=(
            "Exigir a los proveedores que midan su huella, fijen objetivos y "
            "acometan las mejoras baratas, acompañándoles con auditoría y "
            "una parte de la inversión."
        ),
        unidad="% del gasto de compra cubierto por el programa",
        ayuda=(
            "No es glamuroso y es donde están las toneladas: fabricar lo que "
            "vendéis es la mayor parte de vuestro inventario. Ninguna palanca "
            "de transporte puede competir con esto en volumen."
        ),
    ),
]

POR_CODIGO3 = {palanca.codigo: palanca for palanca in PALANCAS3}


def presupuesto3(grupo: str, anio: int | None = None) -> float:
    """Dinero disponible para el plan de alcance 3, en euros."""
    return kpis.ventas_totales(grupo, anio) * PRESUPUESTO3_SOBRE_VENTAS


def topes3(grupo: str, anio: int | None = None) -> dict[str, float]:
    """Hasta dónde llega cada palanca en esta filial."""
    compras = compras_detalladas(grupo, anio)
    hay_aereo = float(compras[compras["pct_aereo"] > 0]["importe_eur"].sum())
    asiatico = float(
        compras[compras["pais_origen"].isin(ASIA)]["importe_eur"].sum()
    )
    return {
        "modal": DESVIO_AEREO_MAXIMO if hay_aereo > 0 else 0.0,
        "origen": RELOCALIZACION_MAXIMA if asiatico > 0 else 0.0,
        "proveedores": 1.0,
    }


def _modal(grupo: str, intensidad: float, compras: pd.DataFrame) -> tuple[float, float]:
    """Desviar mercancía del avión al barco.

    Solo toca la categoría 4: la fábrica sigue emitiendo lo mismo, lo único
    que cambia es cómo viaja lo que fabricó.
    """
    aereas = compras[compras["pct_aereo"] > 0]
    if aereas.empty:
        return 0.0, 0.0

    toneladas_aereas = aereas["toneladas_mercancia"] * aereas["pct_aereo"]
    desviadas = toneladas_aereas * intensidad
    ahorro_por_t_km = p.FACTOR_MODO["aereo"] - p.FACTOR_MODO["maritimo"]
    evitado = float((desviadas * aereas["distancia_km"]).sum()) * ahorro_por_t_km / 1_000

    valor_desviado = float((aereas["importe_eur"] * aereas["pct_aereo"]).sum()) * intensidad
    return evitado, valor_desviado * COSTE_MODAL_SOBRE_VALOR


def _origen(grupo: str, intensidad: float, compras: pd.DataFrame) -> tuple[float, float]:
    """Mover compra asiática a Turquía.

    Cambian tres cosas a la vez: la intensidad del país donde se fabrica, la
    distancia que recorre y el modo en que viaja. Y el precio de compra.
    """
    asiaticas = compras[compras["pais_origen"].isin(ASIA)]
    if asiaticas.empty:
        return 0.0, 0.0

    importe = asiaticas["importe_eur"] * intensidad
    toneladas = asiaticas["toneladas_mercancia"] * intensidad

    intensidad_destino = p.INTENSIDAD_ORIGEN[ORIGEN_CERCANO]
    bienes_antes = float((importe * asiaticas["factor_gasto"]
                          * asiaticas["intensidad_origen"]).sum()) / 1_000
    bienes_despues = float((importe * asiaticas["factor_gasto"]).sum()) \
        * intensidad_destino / 1_000

    transporte_antes = float(
        (toneladas * asiaticas["distancia_km"] * asiaticas["factor_modal"]).sum()
    ) / 1_000
    transporte_despues = float(toneladas.sum()) \
        * p.DISTANCIA_ORIGEN_KM[ORIGEN_CERCANO] \
        * _factor_modal_medio(ORIGEN_CERCANO) / 1_000

    evitado = (bienes_antes - bienes_despues) + (transporte_antes - transporte_despues)

    # El sobrecoste es la diferencia de precio de compra, y es permanente:
    # aquí se factura el de los tres años del plan.
    sobrecoste_relativo = float((
        importe * (
            p.COSTE_RELATIVO_ORIGEN[ORIGEN_CERCANO]
            / asiaticas["pais_origen"].map(p.COSTE_RELATIVO_ORIGEN) - 1
        )
    ).sum())
    return evitado, max(0.0, sobrecoste_relativo)


def _proveedores(grupo: str, intensidad: float,
                 compras: pd.DataFrame) -> tuple[float, float]:
    """Programa de proveedores sobre una parte del gasto.

    Se aplica sobre las emisiones de fabricación, que son la mayor parte del
    inventario. Por eso, aunque la mejora relativa sea modesta, en toneladas
    es la palanca más grande.
    """
    bienes = float(compras["bienes_t"].sum())
    evitado = bienes * intensidad * MEJORA_PROVEEDORES_MAXIMA
    gasto = float(compras["importe_eur"].sum()) * intensidad
    return evitado, gasto * COSTE_PROVEEDORES_SOBRE_GASTO


CALCULOS3 = {
    "modal": _modal,
    "origen": _origen,
    "proveedores": _proveedores,
}


def simular3(grupo: str, plan: dict[str, float],
             anio: int | None = None) -> dict:
    """Qué consigue un plan de alcance 3 y cuánto cuesta.

    Mismo contrato que `palancas.simular`: nunca lanza excepción por un
    valor raro, porque al otro lado hay un alumno moviendo controles.
    """
    inv = inventario(grupo, anio)
    compras = compras_detalladas(grupo, anio)
    limites = topes3(grupo, anio)

    detalle = []
    evitado_total = 0.0
    coste_total = 0.0

    for palanca in PALANCAS3:
        bruto = float(plan.get(palanca.codigo, 0.0) or 0.0)
        intensidad = max(0.0, min(bruto, limites[palanca.codigo]))
        if intensidad <= 0:
            evitado, coste = 0.0, 0.0
        else:
            evitado, coste = CALCULOS3[palanca.codigo](grupo, intensidad, compras)
        evitado_total += evitado
        coste_total += coste
        detalle.append({
            "codigo": palanca.codigo,
            "nombre": palanca.nombre,
            "intensidad": intensidad,
            "evitado_t": evitado,
            "coste_eur": coste,
            "coste_por_t": coste / evitado if evitado > 0.5 else float("inf"),
        })

    disponible = presupuesto3(grupo, anio)
    base = inv["alcance3_t"]
    return {
        "base_t": base,
        "objetivo_t": inv["objetivo3_t"],
        "evitado_t": evitado_total,
        "final_t": base - evitado_total,
        "reduccion": evitado_total / base if base else 0.0,
        "coste_eur": coste_total,
        "presupuesto_eur": disponible,
        "presupuesto_restante_eur": disponible - coste_total,
        "dentro_de_presupuesto": coste_total <= disponible + 1e-6,
        "objetivo_cumplido": evitado_total >= inv["objetivo3_t"] - 1e-6,
        "detalle": detalle,
    }


def plan_maximo3(grupo: str, anio: int | None = None) -> dict[str, float]:
    return dict(topes3(grupo, anio))


def coste_por_tonelada3(grupo: str, anio: int | None = None) -> list[dict]:
    """Cuánto cuesta evitar una tonelada de alcance 3 con cada palanca.

    Es la tabla que desmonta la intuición: acercar la cadena suena a la
    medida más verde del catálogo y es, con diferencia, la más cara.
    """
    inv = inventario(grupo, anio)
    compras = compras_detalladas(grupo, anio)
    limites = topes3(grupo, anio)
    base = inv["alcance3_t"]

    filas = []
    for palanca in PALANCAS3:
        tope = limites[palanca.codigo]
        if tope <= 0:
            filas.append({
                "codigo": palanca.codigo, "nombre": palanca.nombre,
                "evitado_t": 0.0, "coste_eur": 0.0,
                "coste_por_t": float("inf"), "pct_del_alcance3": 0.0,
            })
            continue
        evitado, coste = CALCULOS3[palanca.codigo](grupo, tope, compras)
        filas.append({
            "codigo": palanca.codigo,
            "nombre": palanca.nombre,
            "evitado_t": evitado,
            "coste_eur": coste,
            "coste_por_t": coste / evitado if evitado > 0.5 else float("inf"),
            "pct_del_alcance3": evitado / base if base else 0.0,
        })
    return sorted(filas, key=lambda f: f["coste_por_t"])


def mejor_plan_posible3(grupo: str, anio: int | None = None) -> dict:
    """El mejor resultado alcanzable con el presupuesto de alcance 3."""
    disponible = presupuesto3(grupo, anio)
    limites = topes3(grupo, anio)
    plan: dict[str, float] = {}
    restante = disponible

    for fila in coste_por_tonelada3(grupo, anio):
        if fila["coste_eur"] <= 0 or fila["coste_por_t"] == float("inf"):
            continue
        proporcion = min(1.0, restante / fila["coste_eur"])
        if proporcion <= 0:
            break
        plan[fila["codigo"]] = limites[fila["codigo"]] * proporcion
        restante -= fila["coste_eur"] * proporcion

    resultado = simular3(grupo, plan, anio)
    resultado["plan"] = plan
    return resultado
