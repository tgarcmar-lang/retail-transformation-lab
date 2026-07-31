"""Economía circular y logística verde · Sesión 3.

La Sesión 2 medía carbono. Esta mide **material**, y eso cambia la lógica del
ejercicio: el carbono se evita gastando dinero en tecnología, y el material se
evita, sobre todo, no llegando a usarlo.

**La jerarquía de residuos manda.** Prevenir, reutilizar, reciclar y, en
último lugar, verter. No es una lista de buenas intenciones: es el orden en
que las medidas rinden de verdad, y el modelo lo refleja con una cifra
incómoda —el factor de recirculación— que dice que una tonelada reciclada no
equivale a una tonelada que nunca se generó.

**Por qué reciclar no basta.** El reciclaje pierde material y calidad en cada
vuelta, y además no se mejora a voluntad: subir la tasa de separación es
lento y tiene techo. Una filial que intente resolver la sesión reciclando
mejor se queda a medias, y descubrirlo es el objetivo de la sesión.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from core import datos, kpis
from datos.retailnova import parametros as p

#: Reducción que se pide sobre la pérdida de material del último año. Se
#: presenta en clase como «un tercio», que se recuerda mejor que un 33 %.
OBJETIVO_CIRCULAR = 0.33

#: Presupuesto del plan, sobre las ventas de un año. Es más pequeño que el de
#: descarbonización: aquí no se compran furgonetas ni fotovoltaica, se cambian
#: procesos, envases y acuerdos.
PRESUPUESTO_SOBRE_VENTAS = 0.008

#: Cuánto material vuelve realmente al ciclo por cada tonelada que se envía a
#: reciclar. No es 1: se pierde en la recogida, en la limpieza y en la propia
#: transformación, y lo que sale suele valer para menos cosas que lo que
#: entró. Es la cifra que justifica que prevenir esté por encima de reciclar.
FACTOR_RECICLAJE = 0.55

#: Lo que se recupera de una tonelada reutilizada. Casi todo: el envase o el
#: producto vuelven a usarse tal cual, sin transformarse.
FACTOR_REUTILIZACION = 0.95

# --- Palanca 1 · Envase -----------------------------------------------------
#: Reducción del envase que se consigue con rediseño propio: cajas a medida,
#: menos hueco, menos relleno. Es lo que la filial puede hacer sola.
REDUCCION_ENVASE_PROPIA = 0.15
#: Coste por tonelada de envase que se deja de poner en circulación. El
#: rediseño propio es barato: es cambiar un troquel y una plantilla. Exigirle
#: al proveedor que deje de sobreembalar es otra cosa, porque hay que
#: auditarle, acompañarle y a veces compensarle.
COSTE_ENVASE_PROPIO_EUR_T = 700.0
COSTE_ENVASE_PROVEEDOR_EUR_T = 2_600.0

# --- Palanca 2 · Merma ------------------------------------------------------
#: Hasta dónde se puede bajar la merma con previsión de demanda, rebaja
#: dinámica y donación. No baja a cero: siempre hay producto que se pierde.
REDUCCION_MERMA_MAXIMA = 0.45
#: Coste por tonelada de merma evitada.
COSTE_MERMA_EUR_T = 1_450.0

# --- Palanca 3 · Devoluciones ----------------------------------------------
#: Puntos porcentuales de tasa de devolución que se pueden evitar con mejor
#: información de producto: fotos reales, medidas, guías de talla, opiniones.
PUNTOS_DEVOLUCION_MAXIMOS = 8.0
#: Coste por punto de devolución evitado y por millón de euros vendido
#: online: fotografía de producto, medidas reales, guías de talla y probador
#: virtual. Es la palanca más cara por tonelada de todo el caso y la que más
#: dinero ahorra: esa contradicción es su razón de estar aquí.
COSTE_DEVOLUCION_POR_PUNTO_MEUR = 900.0

# --- Palanca 4 · Envase retornable -----------------------------------------
#: Parte del envase de reparto que puede pasar a caja plegable retornable.
#: Solo aplica al circuito interno entre centro y tienda: con un proveedor a
#: 19.000 kilómetros no hay circuito que cerrar.
RETORNABLE_MAXIMO = 0.55
#: Inversión por tonelada de envase de un solo uso sustituida. Baja donde los
#: camiones ya vuelven de vacío, porque el retorno no hay que pagarlo aparte.
COSTE_RETORNABLE_EUR_T = 2_400.0

# --- Palanca 5 · Reacondicionado -------------------------------------------
#: Parte de lo devuelto no revendible que puede recuperarse y volver a
#: venderse, más la reparación de aparatos y textil.
RECUPERACION_MAXIMA = 0.60
#: Coste por tonelada recuperada. Es intensivo en mano de obra.
COSTE_REACONDICIONADO_EUR_T = 3_100.0

# --- Palanca 6 · Segregación ------------------------------------------------
#: Puntos porcentuales de tasa de reciclaje que se pueden ganar en tres años.
#: Más sería mentir: la separación depende de miles de gestos diarios.
PUNTOS_RECICLAJE_MAXIMOS = 15.0
#: Techo técnico: por encima de aquí la fracción restante no es separable.
RECICLAJE_MAXIMO = 0.88
#: Coste por punto de reciclaje ganado y por cada mil toneladas de residuo.
#: Es la palanca más barata por tonelada, y no es casualidad: por eso todo el
#: mundo empieza por aquí. Lo que casi nadie mira es que sola no llega.
COSTE_SEGREGACION_POR_PUNTO_KT = 6_000.0


@dataclass(frozen=True)
class PalancaCircular:
    codigo: str
    nombre: str
    nivel: str          # prevenir · reutilizar · reciclar
    descripcion: str
    unidad: str
    ayuda: str


PALANCAS: list[PalancaCircular] = [
    PalancaCircular(
        codigo="embalaje",
        nombre="Rediseñar el envase",
        nivel="Prevenir",
        descripcion=(
            "Cajas a la medida del pedido, menos relleno, menos film, y un "
            "estándar de embalaje exigido a los proveedores para que la "
            "mercancía no llegue envuelta tres veces."
        ),
        unidad="% del programa de rediseño que se acomete",
        ayuda=(
            "Rinde más donde la mercancía viene de lejos: un contenedor que "
            "cruza medio mundo llega mucho más protegido que un camión desde "
            "Portugal, y ese exceso lo pagáis vosotros y lo tiráis vosotros."
        ),
    ),
    PalancaCircular(
        codigo="merma",
        nombre="Reducir la merma",
        nivel="Prevenir",
        descripcion=(
            "Previsión de demanda más fina, rebaja dinámica antes de que "
            "caduque y donación de lo que ya no se puede vender. El residuo "
            "que mejor se gestiona es el que no se genera."
        ),
        unidad="% de la merma actual que se evita",
        ayuda=(
            "Mirad vuestra merma en euros antes de decidir. Si vendéis mucha "
            "alimentación, aquí tenéis la mayor bolsa de material perdido de "
            "todo vuestro negocio, y además os está costando dinero hoy."
        ),
    ),
    PalancaCircular(
        codigo="devoluciones",
        nombre="Evitar la devolución",
        nivel="Prevenir",
        descripcion=(
            "Fotografía real, medidas, guía de tallas y opiniones para que el "
            "cliente acierte a la primera. Una devolución evitada ahorra dos "
            "viajes, un embalaje y, a menudo, un producto que ya no se vende."
        ),
        unidad="puntos porcentuales de tasa de devolución que se evitan",
        ayuda=(
            "En material pesa poco y en dinero pesa muchísimo. Antes de "
            "descartarla, mirad lo que os cuesta hoy gestionar devoluciones y "
            "cuánta mercancía devuelta no vuelve a venderse."
        ),
    ),
    PalancaCircular(
        codigo="retornable",
        nombre="Envase retornable",
        nivel="Reutilizar",
        descripcion=(
            "Sustituir el cartón de un solo uso por cajas plegables que van y "
            "vuelven entre el centro logístico y la tienda. El envase deja de "
            "ser residuo y pasa a ser un activo que circula."
        ),
        unidad="% del envase de reparto que pasa a retornable",
        ayuda=(
            "Necesita un viaje de vuelta. Si vuestros camiones ya vuelven "
            "vacíos, ese viaje no hay que pagarlo: ya lo estáis pagando. "
            "Comprobad vuestros kilómetros en vacío antes de decidir."
        ),
    ),
    PalancaCircular(
        codigo="reacondicionado",
        nombre="Recuperar y revender",
        nivel="Reutilizar",
        descripcion=(
            "Revisar, limpiar, reparar y volver a poner a la venta lo que hoy "
            "se destruye: devoluciones no revendibles, aparatos averiados y "
            "textil retirado."
        ),
        unidad="% de lo recuperable que se recupera",
        ayuda=(
            "Es intensivo en mano de obra y por eso sale caro por tonelada. "
            "A cambio, es lo único que convierte un residuo en un ingreso."
        ),
    ),
    PalancaCircular(
        codigo="segregacion",
        nombre="Separar mejor",
        nivel="Reciclar",
        descripcion=(
            "Más contenedores, mejor señalización, formación en tienda y "
            "control de la calidad de la separación para que el material "
            "recogido se pueda reciclar de verdad."
        ),
        unidad="puntos porcentuales de tasa de reciclaje que se ganan",
        ayuda=(
            "Es lo más barato por tonelada y lo más bajo de la jerarquía. "
            "Tiene dos techos: no se pueden ganar más de 15 puntos en tres "
            "años, y por encima del 88 % lo que queda ya no es separable."
        ),
    ),
]

POR_CODIGO = {palanca.codigo: palanca for palanca in PALANCAS}

NIVELES = ["Prevenir", "Reutilizar", "Reciclar"]


# --------------------------------------------------------------------------
# El inventario de materiales
# --------------------------------------------------------------------------

def envases_resumen(grupo: str, anio: int | None = None) -> dict:
    """Envase puesto en circulación y cuánto de él es sobreembalaje.

    El exceso se calcula sobre lo que pesaría el mismo envase si toda la
    mercancía viniese de cerca. Es la parte que no depende del diseño propio
    sino de lo que se le exige al proveedor.
    """
    anio = anio or datos.ultimo_anio()
    envases = datos.de_la_filial("envases", grupo)
    envases = envases[envases["mes"].dt.year == anio]

    total_t = float(envases["kg"].sum()) / 1_000
    de_entrada = envases[envases["tipo"].isin(
        ["carton_entrada", "film_plastico", "palet_madera"]
    )]
    entrada_t = float(de_entrada["kg"].sum()) / 1_000

    compras = datos.de_la_filial("compras", grupo)
    compras = compras[compras["mes"].dt.year == anio]
    importe = float(compras["importe_eur"].sum())
    if importe > 0:
        sobre = sum(
            float(compras[compras["pais_origen"] == origen]["importe_eur"].sum())
            / importe * factor
            for origen, factor in p.SOBREEMBALAJE_ORIGEN.items()
        )
    else:
        sobre = 1.0

    exceso_t = entrada_t * (1 - 1 / sobre) if sobre > 0 else 0.0
    return {
        "total_t": total_t,
        "entrada_t": entrada_t,
        "salida_t": total_t - entrada_t,
        "factor_sobreembalaje": sobre,
        "exceso_t": exceso_t,
        "coste_eur": float(envases["coste_eur"].sum()),
    }


def devoluciones_resumen(grupo: str, anio: int | None = None) -> dict:
    """Devoluciones del canal online: cuántas, cuánto pesan y qué cuestan."""
    anio = anio or datos.ultimo_anio()
    devoluciones = datos.de_la_filial("devoluciones", grupo)
    devoluciones = devoluciones[devoluciones["mes"].dt.year == anio]
    canal = kpis.canal(grupo, anio)

    devueltos = int(devoluciones["pedidos_devueltos"].sum())
    return {
        "pedidos_devueltos": devueltos,
        "tasa_media": devueltos / canal["pedidos"] if canal["pedidos"] else 0.0,
        "valor_eur": float(devoluciones["valor_eur"].sum()),
        "peso_t": float(devoluciones["peso_kg"].sum()) / 1_000,
        "no_revendible_t": float(devoluciones["peso_no_revendible_kg"].sum()) / 1_000,
        "coste_gestion_eur": float(devoluciones["coste_gestion_eur"].sum()),
    }


def merma_t(grupo: str, anio: int | None = None) -> float:
    """Merma del año convertida a toneladas de material.

    Los datos la traen en euros. Se pasa a peso con la densidad de valor de
    cada categoría, ponderada por lo que vende la filial.
    """
    anio = anio or datos.ultimo_anio()
    merma_eur = kpis.inventario_resumen(grupo, anio)["merma_eur"]
    categorias = kpis.ventas_por_categoria(grupo, anio)
    peso = 0.0
    for fila in categorias.itertuples():
        valor_t = p.VALOR_POR_TONELADA[fila.categoria]
        peso += merma_eur * fila.pct_total / valor_t
    return peso


def inventario(grupo: str, anio: int | None = None) -> dict:
    """El balance de materiales de la filial.

    Es la tabla que abre la sesión: cuánto material se genera, cuánto vuelve
    de verdad al ciclo y cuánto se pierde. La cifra que importa es la última.
    """
    anio = anio or datos.ultimo_anio()
    residuos = kpis.residuos_resumen(grupo, anio)

    generado_t = residuos["total_t"]
    reciclado_t = generado_t * residuos["pct_reciclado"]
    recirculado_t = reciclado_t * FACTOR_RECICLAJE
    perdida_t = generado_t - recirculado_t

    return {
        "generado_t": generado_t,
        "pct_reciclado": residuos["pct_reciclado"],
        "reciclado_t": reciclado_t,
        "recirculado_t": recirculado_t,
        "perdida_t": perdida_t,
        "pct_circularidad": recirculado_t / generado_t if generado_t else 0.0,
        "objetivo_t": perdida_t * OBJETIVO_CIRCULAR,
        "por_tipo_t": residuos["por_tipo_t"],
        "envases_t": envases_resumen(grupo, anio)["total_t"],
        "merma_t": merma_t(grupo, anio),
        "devoluciones_t": devoluciones_resumen(grupo, anio)["peso_t"],
    }


def desglose(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """De dónde sale el material que la filial pierde."""
    residuos = kpis.residuos_resumen(grupo, anio)
    nombres = {
        "carton": "Cartón", "plastico": "Plástico", "organico": "Orgánico",
        "raee": "Aparatos eléctricos", "textil": "Textil", "resto": "Resto",
    }
    filas = [
        (nombres.get(tipo, tipo), toneladas)
        for tipo, toneladas in residuos["por_tipo_t"].items()
    ]
    tabla = pd.DataFrame(filas, columns=["material", "generado_t"])
    tabla["pct"] = tabla["generado_t"] / tabla["generado_t"].sum()
    return tabla.sort_values("generado_t", ascending=False, ignore_index=True)


# --------------------------------------------------------------------------
# Presupuesto y topes
# --------------------------------------------------------------------------

def presupuesto(grupo: str, anio: int | None = None) -> float:
    return kpis.ventas_totales(grupo, anio) * PRESUPUESTO_SOBRE_VENTAS


def topes(grupo: str, anio: int | None = None) -> dict[str, float]:
    """Hasta dónde llega cada palanca en esta filial."""
    anio = anio or datos.ultimo_anio()
    residuos = kpis.residuos_resumen(grupo, anio)
    envases = envases_resumen(grupo, anio)

    # El programa de envase suma el rediseño propio y el exceso de
    # sobreembalaje que se le puede exigir al proveedor.
    exceso_relativo = (
        envases["exceso_t"] / envases["total_t"] if envases["total_t"] else 0.0
    )
    return {
        "embalaje": 1.0,
        "merma": REDUCCION_MERMA_MAXIMA,
        "devoluciones": PUNTOS_DEVOLUCION_MAXIMOS,
        "retornable": RETORNABLE_MAXIMO,
        "reacondicionado": RECUPERACION_MAXIMA,
        "segregacion": min(
            PUNTOS_RECICLAJE_MAXIMOS,
            max(0.0, (RECICLAJE_MAXIMO - residuos["pct_reciclado"]) * 100),
        ),
        # Guardado aparte: lo usa el cálculo del envase, no es una palanca.
        "_reduccion_envase": REDUCCION_ENVASE_PROPIA + exceso_relativo,
    }


# --------------------------------------------------------------------------
# Efecto y coste de cada palanca
# --------------------------------------------------------------------------

def _perdida_por_tonelada_evitada(grupo: str, anio: int | None = None) -> float:
    """Cuánta pérdida se ahorra por cada tonelada que no se genera.

    No es una tonelada entera: parte de lo que se deja de generar se estaba
    reciclando, así que ya volvía en parte al ciclo. Cuanto mejor recicla una
    filial, menos le rinde prevenir *en esta métrica* — y aun así prevenir le
    sigue saliendo más barato, porque el material que no se compra no se paga.
    """
    residuos = kpis.residuos_resumen(grupo, anio)
    return 1 - residuos["pct_reciclado"] * FACTOR_RECICLAJE


def _embalaje(grupo: str, intensidad: float, inv: dict) -> tuple[float, float]:
    """Dos cosas a la vez, y cuestan muy distinto.

    Rediseñar la caja propia es barato. Conseguir que el proveedor asiático
    deje de envolver tres veces exige auditarle y acompañarle, y por eso la
    filial que más exceso arrastra es también la que más cara tiene esta
    palanca por tonelada.
    """
    envases = envases_resumen(grupo)
    propia_t = envases["total_t"] * REDUCCION_ENVASE_PROPIA * intensidad
    proveedor_t = envases["exceso_t"] * intensidad

    evitado_t = propia_t + proveedor_t
    coste = (propia_t * COSTE_ENVASE_PROPIO_EUR_T
             + proveedor_t * COSTE_ENVASE_PROVEEDOR_EUR_T)
    return evitado_t * _perdida_por_tonelada_evitada(grupo), coste


def _merma(grupo: str, intensidad: float, inv: dict) -> tuple[float, float]:
    evitado_t = inv["merma_t"] * intensidad
    return (evitado_t * _perdida_por_tonelada_evitada(grupo),
            evitado_t * COSTE_MERMA_EUR_T)


def _devoluciones(grupo: str, intensidad: float, inv: dict) -> tuple[float, float]:
    """`intensidad` va en puntos porcentuales de tasa de devolución."""
    resumen = devoluciones_resumen(grupo)
    canal = kpis.canal(grupo)
    tasa = resumen["tasa_media"]
    if tasa <= 0:
        return 0.0, 0.0

    puntos = min(intensidad, PUNTOS_DEVOLUCION_MAXIMOS)
    proporcion = min(1.0, (puntos / 100) / tasa)

    # Se evita el producto que no se revendía y el embalaje del envío.
    evitado_t = resumen["no_revendible_t"] * proporcion
    envases = envases_resumen(grupo)
    if canal["pedidos"] > 0:
        envase_por_pedido_t = envases["salida_t"] / canal["pedidos"]
        evitado_t += envase_por_pedido_t * resumen["pedidos_devueltos"] * proporcion

    millones = kpis.ventas_totales(grupo) * canal["cuota_online"] / 1_000_000
    coste = puntos * millones * COSTE_DEVOLUCION_POR_PUNTO_MEUR
    return evitado_t * _perdida_por_tonelada_evitada(grupo), coste


def _retornable(grupo: str, intensidad: float, inv: dict) -> tuple[float, float]:
    """El envase deja de ser residuo y pasa a circular.

    Solo toca el circuito interno entre centro y tienda. Y sale más barato
    donde los camiones ya vuelven de vacío: el viaje de retorno ya se paga.
    """
    envases = envases_resumen(grupo)
    log = kpis.logistica(grupo)

    sustituido_t = envases["salida_t"] * intensidad
    evitado_t = sustituido_t * FACTOR_REUTILIZACION

    # Con mucho retorno vacío, el circuito cerrado sale hasta la mitad de
    # barato: no hay que pagar el viaje de vuelta, ya se está haciendo. Es
    # donde la logística verde y la economía circular se tocan.
    descuento = min(0.50, log["pct_km_en_vacio"] * 1.5)
    coste = sustituido_t * COSTE_RETORNABLE_EUR_T * (1 - descuento)
    return evitado_t * _perdida_por_tonelada_evitada(grupo), coste


def _reacondicionado(grupo: str, intensidad: float, inv: dict) -> tuple[float, float]:
    resumen = devoluciones_resumen(grupo)
    por_tipo = inv["por_tipo_t"]
    recuperable_t = (
        resumen["no_revendible_t"]
        + por_tipo.get("raee", 0.0) * 0.35
        + por_tipo.get("textil", 0.0) * 0.30
    )
    recuperado_t = recuperable_t * intensidad
    evitado_t = recuperado_t * FACTOR_REUTILIZACION
    return (evitado_t * _perdida_por_tonelada_evitada(grupo),
            recuperado_t * COSTE_REACONDICIONADO_EUR_T)


def _segregacion(grupo: str, intensidad: float, inv: dict) -> tuple[float, float]:
    """`intensidad` va en puntos porcentuales de tasa de reciclaje.

    Solo cambia el destino del material, no la cantidad. Y cada tonelada que
    pasa a reciclarse solo vuelve al ciclo a medias.
    """
    limite = topes(grupo)["segregacion"]
    puntos = min(intensidad, limite)
    if puntos <= 0:
        return 0.0, 0.0

    reciclado_extra_t = inv["generado_t"] * (puntos / 100)
    evitado_t = reciclado_extra_t * FACTOR_RECICLAJE
    coste = puntos * (inv["generado_t"] / 1_000) * COSTE_SEGREGACION_POR_PUNTO_KT
    return evitado_t, coste


CALCULOS = {
    "embalaje": _embalaje,
    "merma": _merma,
    "devoluciones": _devoluciones,
    "retornable": _retornable,
    "reacondicionado": _reacondicionado,
    "segregacion": _segregacion,
}

#: Palancas que se expresan en puntos porcentuales y no en porcentaje de tope.
EN_PUNTOS = {"devoluciones", "segregacion"}


# --------------------------------------------------------------------------
# Simulación
# --------------------------------------------------------------------------

def simular(grupo: str, plan: dict[str, float],
            anio: int | None = None) -> dict:
    """Qué consigue un plan de circularidad y cuánto cuesta.

    Mismo contrato que las otras dos sesiones: nunca lanza excepción por un
    valor raro, porque al otro lado hay un alumno moviendo controles.
    """
    inv = inventario(grupo, anio)
    limites = topes(grupo, anio)

    detalle = []
    evitado_total = 0.0
    coste_total = 0.0
    por_nivel = {nivel: 0.0 for nivel in NIVELES}

    for palanca in PALANCAS:
        bruto = float(plan.get(palanca.codigo, 0.0) or 0.0)
        intensidad = max(0.0, min(bruto, limites[palanca.codigo]))
        if intensidad <= 0:
            evitado, coste = 0.0, 0.0
        else:
            evitado, coste = CALCULOS[palanca.codigo](grupo, intensidad, inv)
        evitado_total += evitado
        coste_total += coste
        por_nivel[palanca.nivel] += evitado
        detalle.append({
            "codigo": palanca.codigo,
            "nombre": palanca.nombre,
            "nivel": palanca.nivel,
            "intensidad": intensidad,
            "evitado_t": evitado,
            "coste_eur": coste,
            "coste_por_t": coste / evitado if evitado > 0.5 else float("inf"),
        })

    disponible = presupuesto(grupo, anio)
    base = inv["perdida_t"]
    return {
        "base_t": base,
        "generado_t": inv["generado_t"],
        "objetivo_t": inv["objetivo_t"],
        "evitado_t": evitado_total,
        "final_t": base - evitado_total,
        "reduccion": evitado_total / base if base else 0.0,
        "por_nivel": por_nivel,
        "coste_eur": coste_total,
        "presupuesto_eur": disponible,
        "presupuesto_restante_eur": disponible - coste_total,
        "dentro_de_presupuesto": coste_total <= disponible + 1e-6,
        "objetivo_cumplido": evitado_total >= inv["objetivo_t"] - 1e-6,
        "detalle": detalle,
    }


def plan_maximo(grupo: str, anio: int | None = None) -> dict[str, float]:
    limites = topes(grupo, anio)
    return {c: v for c, v in limites.items() if not c.startswith("_")}


def coste_por_tonelada(grupo: str, anio: int | None = None) -> list[dict]:
    """Cuánto cuesta recuperar una tonelada con cada palanca.

    Ordenada por precio, es la tabla que enfrenta a la intuición con la
    jerarquía: lo más barato casi siempre es lo que está más abajo.
    """
    inv = inventario(grupo, anio)
    limites = topes(grupo, anio)
    base = inv["perdida_t"]

    filas = []
    for palanca in PALANCAS:
        tope = limites[palanca.codigo]
        if tope <= 0:
            filas.append({
                "codigo": palanca.codigo, "nombre": palanca.nombre,
                "nivel": palanca.nivel, "evitado_t": 0.0, "coste_eur": 0.0,
                "coste_por_t": float("inf"), "pct_de_la_perdida": 0.0,
            })
            continue
        evitado, coste = CALCULOS[palanca.codigo](grupo, tope, inv)
        filas.append({
            "codigo": palanca.codigo,
            "nombre": palanca.nombre,
            "nivel": palanca.nivel,
            "evitado_t": evitado,
            "coste_eur": coste,
            "coste_por_t": coste / evitado if evitado > 0.5 else float("inf"),
            "pct_de_la_perdida": evitado / base if base else 0.0,
        })
    return sorted(filas, key=lambda f: f["coste_por_t"])


def mejor_plan_posible(grupo: str, anio: int | None = None) -> dict:
    """El mejor resultado alcanzable con el presupuesto."""
    disponible = presupuesto(grupo, anio)
    limites = topes(grupo, anio)
    plan: dict[str, float] = {}
    restante = disponible

    for fila in coste_por_tonelada(grupo, anio):
        if fila["coste_eur"] <= 0 or fila["coste_por_t"] == float("inf"):
            continue
        proporcion = min(1.0, restante / fila["coste_eur"])
        if proporcion <= 0:
            break
        plan[fila["codigo"]] = limites[fila["codigo"]] * proporcion
        restante -= fila["coste_eur"] * proporcion

    resultado = simular(grupo, plan, anio)
    resultado["plan"] = plan
    return resultado
