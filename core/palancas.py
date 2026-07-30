"""Palancas de descarbonización de la Sesión 2.

El grupo tiene un objetivo de reducción y un presupuesto. No le llega para
todo, así que tiene que elegir. Ese es el ejercicio: no calcular, sino
decidir.

**La misma palanca no vale para todos.** Cambiar el refrigerante es demoledor
en Valencia y no sirve de nada en Bilbao, que ya lo hizo. Electrificar la
última milla tiene sentido en Madrid, que reparte en ciudad, y muy poco en
Sevilla, que quema el gasóleo en carretera. Un grupo que copie el plan del
vecino no llegará al objetivo, y eso es exactamente lo que debe descubrir.

Sin Streamlit dentro: se puede simular y probar sin levantar la aplicación.
"""

from __future__ import annotations

from dataclasses import dataclass

from core import datos, filiales, kpis
from datos.retailnova import parametros as p

#: Reducción que se les exige, sobre las emisiones del último año cerrado.
OBJETIVO = 0.25

#: Presupuesto del **plan de inversión a tres años**, como proporción de las
#: ventas de un año. Escala con el tamaño para que las cinco filiales tengan
#: un reto parecido. Está calibrado (ver `tests/test_palancas.py`) para que
#: el 25 % sea alcanzable eligiendo bien e inalcanzable eligiendo mal.
PRESUPUESTO_SOBRE_VENTAS = 0.025

# --- Palanca 1 · Refrigerante ---------------------------------------------
#: Coste de reconvertir una instalación de frío a CO₂, por kilo de carga.
COSTE_REFRIGERANTE_EUR_KG = 620.0
#: Lo que se evita de la fuga al pasar a CO₂. No es el 100 %: el CO₂ también
#: se fuga, solo que su impacto es unas mil veces menor.
EFICACIA_REFRIGERANTE = 0.96

# --- Palanca 2 · Última milla eléctrica -----------------------------------
#: Sobrecoste de una furgoneta eléctrica frente a la diésel equivalente.
COSTE_FURGONETA_ELECTRICA = 26_000.0
#: Consumo de la furgoneta eléctrica. Emite, pero a través de la red.
CONSUMO_ELECTRICO_KWH_KM = 0.25

# --- Palanca 3 · Kilómetros en vacío --------------------------------------
#: Por debajo de este porcentaje de kilómetros en vacío no se puede bajar:
#: siempre hay retornos que no se pueden llenar.
VACIO_MINIMO = 0.12
#: Coste por cada punto porcentual de vacío eliminado.
COSTE_VACIO_POR_PUNTO = 52_000.0

# --- Palanca 4 · Factor de carga ------------------------------------------
#: Ocupación máxima realista de un vehículo de reparto. El 100 % no existe:
#: la mercancía no encaja perfectamente y las rutas no se llenan a voluntad.
OCUPACION_MAXIMA = 0.86
#: Coste por cada punto porcentual de ocupación ganado.
COSTE_CARGA_POR_PUNTO = 46_000.0

# --- Palanca 5 · Consolidación y recogida en tienda -----------------------
#: Hasta dónde puede llegar la recogida en tienda. Más de la mitad de los
#: pedidos no se puede empujar al mostrador sin perder clientes.
RECOGIDA_MAXIMA = 0.55
#: Inversión por cada punto de recogida ganado y por cada tienda que hay que
#: equipar: taquillas, espacio de preparación y sistema de avisos. Se cobra
#: por tienda y no por euro vendido porque lo que se monta es infraestructura
#: física: una taquilla cuesta lo mismo sirva pedidos caros o baratos.
COSTE_RECOGIDA_POR_PUNTO_Y_TIENDA = 700.0

# --- Palanca 6 · Energía en instalaciones ---------------------------------
#: Reducción máxima del consumo eléctrico con iluminación, frío eficiente y
#: fotovoltaica en cubierta.
REDUCCION_ENERGIA_MAXIMA = 0.40
#: Inversión por cada kWh anual que se deja de comprar a la red.
COSTE_ENERGIA_EUR_KWH = 0.62


@dataclass(frozen=True)
class Palanca:
    codigo: str
    nombre: str
    descripcion: str
    unidad: str
    ayuda: str


PALANCAS: list[Palanca] = [
    Palanca(
        codigo="refrigerante",
        nombre="Sustituir el gas refrigerante",
        descripcion=(
            "Reconvertir las instalaciones de frío para que funcionen con CO₂ "
            "en lugar del gas actual."
        ),
        unidad="% de la carga instalada que se convierte",
        ayuda=(
            "El impacto depende del gas que uséis hoy. Mirad en el paso 4 de "
            "la Sesión 1 cuánto pesan las fugas en vuestra huella: si pesan "
            "poco, esta palanca os va a costar dinero y no os va a dar nada."
        ),
    ),
    Palanca(
        codigo="electrificacion",
        nombre="Electrificar la última milla",
        descripcion=(
            "Sustituir furgonetas de reparto diésel por eléctricas. Siguen "
            "emitiendo, pero a través de la red, que es mucho más limpia."
        ),
        unidad="% de furgonetas que se sustituyen",
        ayuda=(
            "Rinde donde hay muchas furgonetas haciendo muchos kilómetros "
            "urbanos. Si vuestro gasóleo se lo comen los camiones en "
            "carretera, esta palanca toca poco."
        ),
    ),
    Palanca(
        codigo="vacio",
        nombre="Eliminar kilómetros en vacío",
        descripcion=(
            "Planificar los retornos para que el vehículo no vuelva de "
            "descargar sin nada dentro: cargas de retorno, rutas circulares "
            "y coordinación con los proveedores que os traen mercancía."
        ),
        unidad="puntos porcentuales de kilómetros en vacío que se eliminan",
        ayuda=(
            "Tiene techo: por debajo del 12 % de vacío no baja nadie, porque "
            "siempre hay retornos que no se pueden llenar. Si ya estáis cerca "
            "de ese suelo, aquí no os queda margen."
        ),
    ),
    Palanca(
        codigo="carga",
        nombre="Mejorar el factor de carga",
        descripcion=(
            "Llenar mejor el vehículo que ya sale: consolidar envíos, "
            "reagrupar pedidos pequeños y replantear la frecuencia de "
            "reparto a las tiendas para mover lo mismo en menos viajes."
        ),
        unidad="puntos porcentuales de ocupación media que se ganan",
        ayuda=(
            "Es distinta del vacío. Un camión puede ir siempre cargado y aun "
            "así ir medio vacío: eso es el factor de carga. Mirad vuestra "
            "ocupación media antes de decidir cuánto margen tenéis."
        ),
    ),
    Palanca(
        codigo="consolidacion",
        nombre="Recogida en tienda",
        descripcion=(
            "Desviar pedidos del reparto a domicilio al mostrador o a una "
            "taquilla de la tienda. El pedido viaja en un camión que ya iba, "
            "en vez de en una furgoneta que sale solo para él."
        ),
        unidad="puntos porcentuales de pedidos que pasan a recogerse en tienda",
        ayuda=(
            "Rinde el doble donde fallan muchas entregas: un pedido que se "
            "recoge en tienda no puede fallar, y cada fallo obliga hoy a "
            "repetir el viaje entero."
        ),
    ),
    Palanca(
        codigo="energia",
        nombre="Iluminación, frío eficiente y fotovoltaica",
        descripcion=(
            "Reducir la electricidad que se compra a la red, con iluminación "
            "LED, equipos de frío eficientes y placas en cubierta."
        ),
        unidad="% de reducción del consumo eléctrico",
        ayuda=(
            "La electricidad es la fuente más grande de casi todas las "
            "filiales, así que aquí está el grueso. También es la inversión "
            "más cara por tonelada evitada."
        ),
    ),
]

POR_CODIGO = {palanca.codigo: palanca for palanca in PALANCAS}


# --------------------------------------------------------------------------
# Punto de partida
# --------------------------------------------------------------------------

def presupuesto(grupo: str, anio: int | None = None) -> float:
    """Dinero disponible para invertir, en euros."""
    return kpis.ventas_totales(grupo, anio) * PRESUPUESTO_SOBRE_VENTAS


def linea_base(grupo: str, anio: int | None = None) -> dict:
    """Las emisiones de partida, desglosadas por fuente, en toneladas."""
    anio = anio or datos.ultimo_anio()
    huella = kpis.huella(grupo, anio).set_index("fuente")["co2e_t"]
    return {
        "total_t": float(huella.sum()),
        "electricidad_t": float(huella.get("Electricidad", 0.0)),
        "flota_t": float(huella.get("Gasóleo de la flota", 0.0)),
        "refrigerante_t": float(huella.get("Fugas de refrigerante", 0.0)),
        "gas_t": float(huella.get("Gas natural", 0.0)),
        "objetivo_t": float(huella.sum()) * OBJETIVO,
    }


def ultima_milla_t(grupo: str, anio: int | None = None) -> float:
    """Emisiones de las furgonetas, en toneladas.

    Es lo que se juega en la última milla. Separarlo de los rígidos importa:
    en Madrid las furgonetas son un tercio de las emisiones de la flota y en
    Sevilla apenas un décimo, así que la misma medida vale cosas muy
    distintas en cada sitio.
    """
    anio = anio or datos.ultimo_anio()
    consumo = datos.de_la_filial("consumo_flota", grupo)
    consumo = consumo[(consumo["mes"].dt.year == anio)
                      & (consumo["tipo"] == "furgoneta")]
    return float(consumo["co2e_kg"].sum()) / 1_000


def topes(grupo: str, anio: int | None = None) -> dict[str, float]:
    """Hasta dónde puede llegar cada palanca en esta filial.

    No todas dan lo mismo en todas partes. Sevilla tiene mucho margen en
    vacío y en factor de carga; Bilbao casi ninguno, porque ya está en el
    13,8 % de vacío y en el 83 % de ocupación.
    """
    anio = anio or datos.ultimo_anio()
    log = kpis.logistica(grupo, anio)
    canal = kpis.canal(grupo, anio)
    return {
        "refrigerante": 1.0,
        "electrificacion": 1.0,
        "vacio": max(0.0, (log["pct_km_en_vacio"] - VACIO_MINIMO) * 100),
        "carga": max(0.0, (OCUPACION_MAXIMA - log["ocupacion_media"]) * 100),
        "consolidacion": max(
            0.0, (RECOGIDA_MAXIMA - canal["pct_recogida_en_tienda"]) * 100
        ),
        "energia": REDUCCION_ENERGIA_MAXIMA,
    }


# --------------------------------------------------------------------------
# Efecto y coste de cada palanca
# --------------------------------------------------------------------------

def _refrigerante(grupo: str, intensidad: float, base: dict) -> tuple[float, float]:
    refrigerantes = datos.de_la_filial("refrigerantes", grupo)
    carga = float(refrigerantes[refrigerantes["anio"] == datos.ultimo_anio()]
                  ["carga_kg"].sum())
    coste = carga * intensidad * COSTE_REFRIGERANTE_EUR_KG
    evitado = base["refrigerante_t"] * intensidad * EFICACIA_REFRIGERANTE
    return evitado, coste


def _electrificacion(grupo: str, intensidad: float, base: dict) -> tuple[float, float]:
    furgonetas, _ = p.FLOTA[grupo]
    km = p.KM_ANUALES[grupo]["furgoneta"]
    litros_100 = p.CONSUMO_L_100KM[grupo]["furgoneta"]

    sustituidas = furgonetas * intensidad
    coste = sustituidas * COSTE_FURGONETA_ELECTRICA

    gasoleo_evitado = sustituidas * km * litros_100 / 100 * p.FACTOR_GASOLEO / 1_000
    electricidad_anadida = (
        sustituidas * km * CONSUMO_ELECTRICO_KWH_KM * p.FACTOR_ELECTRICIDAD / 1_000
    )
    return gasoleo_evitado - electricidad_anadida, coste


def _vacio(grupo: str, intensidad: float, base: dict) -> tuple[float, float]:
    """`intensidad` va en puntos porcentuales de vacío eliminados."""
    log = kpis.logistica(grupo)
    puntos = min(intensidad, max(0.0, (log["pct_km_en_vacio"] - VACIO_MINIMO) * 100))
    coste = puntos * COSTE_VACIO_POR_PUNTO
    # Menos kilómetros son menos litros, en proporción directa.
    evitado = base["flota_t"] * (puntos / 100)
    return evitado, coste


def _carga(grupo: str, intensidad: float, base: dict) -> tuple[float, float]:
    """`intensidad` va en puntos porcentuales de ocupación ganados.

    Mover la misma mercancía con el vehículo más lleno significa hacer menos
    viajes, en proporción inversa a la ocupación: pasar del 60 % al 80 % no
    ahorra un 20 % de kilómetros, ahorra un 25 %.
    """
    log = kpis.logistica(grupo)
    ocupacion = log["ocupacion_media"]
    puntos = min(intensidad, max(0.0, (OCUPACION_MAXIMA - ocupacion) * 100))
    if puntos <= 0 or ocupacion <= 0:
        return 0.0, 0.0
    nueva = ocupacion + puntos / 100
    evitado = base["flota_t"] * (1 - ocupacion / nueva)
    return evitado, puntos * COSTE_CARGA_POR_PUNTO


def _consolidacion(grupo: str, intensidad: float, base: dict) -> tuple[float, float]:
    """`intensidad` va en puntos porcentuales de pedidos que pasan a tienda.

    Solo toca la última milla: los rígidos que abastecen a las tiendas
    siguen saliendo igual. Y rinde más donde fallan más entregas, porque el
    pedido que se recoge en el mostrador no puede fallar y hoy cada fallo
    obliga a repetir el viaje.
    """
    canal = kpis.canal(grupo)
    log = kpis.logistica(grupo)
    recogida = canal["pct_recogida_en_tienda"]
    a_domicilio = 1 - recogida
    puntos = min(intensidad, max(0.0, (RECOGIDA_MAXIMA - recogida) * 100))
    if puntos <= 0 or a_domicilio <= 0:
        return 0.0, 0.0

    proporcion = (puntos / 100) / a_domicilio
    evitado = (ultima_milla_t(grupo) * proporcion
               * (1 + log["pct_entregas_fallidas"]))
    tiendas = len(datos.de_la_filial("tiendas", grupo))
    coste = puntos * tiendas * COSTE_RECOGIDA_POR_PUNTO_Y_TIENDA
    return evitado, coste


def _energia(grupo: str, intensidad: float, base: dict) -> tuple[float, float]:
    consumo = kpis.energia_resumen(grupo)["electricidad_kwh"]
    ahorro_kwh = consumo * intensidad
    coste = ahorro_kwh * COSTE_ENERGIA_EUR_KWH
    evitado = base["electricidad_t"] * intensidad
    return evitado, coste


CALCULOS = {
    "refrigerante": _refrigerante,
    "electrificacion": _electrificacion,
    "vacio": _vacio,
    "carga": _carga,
    "consolidacion": _consolidacion,
    "energia": _energia,
}

#: Palancas que se expresan en puntos porcentuales y no en porcentaje de un
#: tope. La interfaz y el informe las presentan distinto.
EN_PUNTOS = {"vacio", "carga", "consolidacion"}


# --------------------------------------------------------------------------
# Simulación
# --------------------------------------------------------------------------

def simular(grupo: str, plan: dict[str, float],
            anio: int | None = None) -> dict:
    """Calcula qué consigue un plan y cuánto cuesta.

    `plan` lleva la intensidad de cada palanca. Lo que no aparezca vale cero.
    Nunca lanza excepción por un valor raro: se recorta al tope permitido,
    porque el alumno no tiene que ver un error por mover un control.
    """
    base = linea_base(grupo, anio)
    limites = topes(grupo, anio)

    detalle = []
    evitado_total = 0.0
    coste_total = 0.0

    for palanca in PALANCAS:
        bruto = float(plan.get(palanca.codigo, 0.0) or 0.0)
        intensidad = max(0.0, min(bruto, limites[palanca.codigo]))
        if intensidad <= 0:
            evitado, coste = 0.0, 0.0
        else:
            evitado, coste = CALCULOS[palanca.codigo](grupo, intensidad, base)
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

    disponible = presupuesto(grupo, anio)
    return {
        "base_t": base["total_t"],
        "objetivo_t": base["objetivo_t"],
        "evitado_t": evitado_total,
        "final_t": base["total_t"] - evitado_total,
        "reduccion": evitado_total / base["total_t"] if base["total_t"] else 0.0,
        "coste_eur": coste_total,
        "presupuesto_eur": disponible,
        "presupuesto_restante_eur": disponible - coste_total,
        "dentro_de_presupuesto": coste_total <= disponible + 1e-6,
        "objetivo_cumplido": evitado_total >= base["objetivo_t"] - 1e-6,
        "detalle": detalle,
    }


def plan_maximo(grupo: str, anio: int | None = None) -> dict[str, float]:
    """Todas las palancas al máximo. Sirve para saber el techo físico."""
    return dict(topes(grupo, anio))


def coste_por_tonelada(grupo: str, anio: int | None = None) -> list[dict]:
    """Cuánto cuesta evitar una tonelada con cada palanca, por separado.

    Es la tabla que convierte la sesión en una decisión de inversión: sin
    ella el grupo elige por intuición, y la intuición aquí falla mucho.
    """
    base = linea_base(grupo, anio)
    limites = topes(grupo, anio)
    filas = []
    for palanca in PALANCAS:
        tope = limites[palanca.codigo]
        if tope <= 0:
            filas.append({
                "codigo": palanca.codigo, "nombre": palanca.nombre,
                "evitado_t": 0.0, "coste_eur": 0.0,
                "coste_por_t": float("inf"), "pct_de_la_huella": 0.0,
            })
            continue
        evitado, coste = CALCULOS[palanca.codigo](grupo, tope, base)
        filas.append({
            "codigo": palanca.codigo,
            "nombre": palanca.nombre,
            "evitado_t": evitado,
            "coste_eur": coste,
            "coste_por_t": coste / evitado if evitado > 0.5 else float("inf"),
            "pct_de_la_huella": evitado / base["total_t"] if base["total_t"] else 0.0,
        })
    return sorted(filas, key=lambda f: f["coste_por_t"])


def mejor_plan_posible(grupo: str, anio: int | None = None) -> dict:
    """El mejor resultado alcanzable dentro del presupuesto.

    Se van comprando palancas de la más barata por tonelada a la más cara,
    hasta agotar el dinero. No es óptimo en sentido estricto, pero sirve para
    comprobar que el ejercicio tiene solución y que no es trivial.
    """
    disponible = presupuesto(grupo, anio)
    limites = topes(grupo, anio)
    plan: dict[str, float] = {}
    restante = disponible

    for fila in coste_por_tonelada(grupo, anio):
        if fila["coste_eur"] <= 0 or fila["coste_por_t"] == float("inf"):
            continue
        tope = limites[fila["codigo"]]
        proporcion = min(1.0, restante / fila["coste_eur"])
        if proporcion <= 0:
            break
        plan[fila["codigo"]] = tope * proporcion
        restante -= fila["coste_eur"] * proporcion

    resultado = simular(grupo, plan, anio)
    resultado["plan"] = plan
    return resultado
