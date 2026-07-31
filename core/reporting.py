"""Medición, reporting y estrategia ESG · Sesión 4.

Las tres sesiones anteriores producían decisiones. Esta produce **una
declaración**, y eso cambia la naturaleza del ejercicio: no hay un óptimo que
un deslizador pueda encontrar. Hay criterio, y hay una firma debajo.

**Las dos ideas que sostienen la sesión.**

1. **Doble materialidad.** No se cuenta todo: se cuenta lo material. Y algo
   es material por dos caminos distintos —por el efecto que la empresa tiene
   sobre el mundo (materialidad de impacto) y por el efecto que el asunto
   tiene sobre la empresa (materialidad financiera)—. Basta con uno de los
   dos. La matriz de este módulo **se calcula con los datos del caso**, no
   está escrita a mano, así que cada filial tiene la suya y ningún grupo
   puede copiar la del vecino.

2. **Se puede mentir sin decir una sola cifra falsa.** Las cinco trampas que
   vigila el verificador son todas técnicamente ciertas y todas engañan. Son,
   además, exactamente las cosas contra las que se les avisó en las sesiones
   2 y 3: aquí reaparecen convertidas en tentación.

**Estándares.** El ancla de la sesión es **ISO 14083:2023** —construido sobre
el GLEC Framework v3.0—, que es el estándar propio de las emisiones del
transporte y la logística, y los **ESRS** de la CSRD como marco obligatorio.
GHG Protocol, GRI y SBTi se citan y se sitúan, pero no se desarrollan.

Sin Streamlit dentro, como el resto de `core/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable

import pandas as pd

from core import alcance3, circular, datos, filiales, kpis, palancas
from datos.retailnova import parametros as p

#: Cuántos indicadores puede llevar la memoria. El límite es el ejercicio:
#: sin él no habría que elegir, y elegir es lo que enseña la materialidad.
MAXIMO_INDICADORES = 10

#: Umbral a partir del cual un asunto se considera material. Sobre 5.
UMBRAL_MATERIALIDAD = 3.5


# --------------------------------------------------------------------------
# Los asuntos sobre los que se puede informar
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Tema:
    codigo: str
    nombre: str
    dimension: str      # Ambiental · Social · Gobernanza
    explicacion: str


TEMAS: list[Tema] = [
    Tema("emisiones_operativas", "Emisiones propias y de energía", "Ambiental",
         "Lo que emite la filial directamente y la electricidad que compra. "
         "Es sobre lo que manda de verdad."),
    Tema("transporte", "Transporte y distribución", "Ambiental",
         "El gasóleo de la flota, los kilómetros en vacío y el factor de "
         "carga. Es el asunto propio de la logística."),
    Tema("refrigerantes", "Gases fluorados", "Ambiental",
         "Las fugas de las instalaciones de frío. No aparecen en ninguna "
         "factura y pesan mucho donde queda R-404A."),
    Tema("cadena_suministro", "Emisiones de la cadena de valor", "Ambiental",
         "El alcance 3: fabricar lo que se vende y traerlo. Es la mayor "
         "parte del inventario y la peor medida."),
    Tema("residuos_envase", "Envase y residuos", "Ambiental",
         "El material que se pone en circulación y el que se pierde."),
    Tema("merma", "Merma y desperdicio", "Ambiental",
         "Producto que se compró y nunca se vendió."),
    Tema("plantilla", "Empleo y condiciones", "Social",
         "Temporalidad, rotación, formación y brecha salarial."),
    Tema("seguridad", "Seguridad y salud", "Social",
         "Accidentes con baja. En logística es el asunto social con más "
         "consecuencias."),
    Tema("trabajo_cadena", "Trabajo en la cadena de valor", "Social",
         "Condiciones laborales aguas arriba. Es donde más lejos llega la "
         "responsabilidad y menos se ve."),
    Tema("gobernanza", "Gobernanza de la sostenibilidad", "Gobernanza",
         "Cómo se controla lo que se compra y a quién se compra."),
]

POR_TEMA = {tema.codigo: tema for tema in TEMAS}


# --------------------------------------------------------------------------
# El catálogo de indicadores
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Indicador:
    codigo: str
    nombre: str
    tema: str
    estandar: str
    unidad: str
    calidad: str        # alta · media · baja
    calculo: Callable[[str], float]
    nota: str = ""


def _huella_12(grupo: str) -> float:
    return palancas.linea_base(grupo)["total_t"]


def _intensidad_12(grupo: str) -> float:
    return _huella_12(grupo) / (kpis.ventas_totales(grupo) / 1_000_000)


def _huella_3(grupo: str) -> float:
    return alcance3.inventario(grupo)["alcance3_t"]


def _emisiones_transporte(grupo: str) -> float:
    return palancas.linea_base(grupo)["flota_t"]


def _intensidad_transporte(grupo: str) -> float:
    """Gramos de CO₂e por tonelada-kilómetro, al modo de la ISO 14083.

    Es una aproximación: se reparte la emisión de la flota entre las
    toneladas-kilómetro estimadas a partir de los kilómetros recorridos y la
    ocupación media. La norma pide bastante más detalle, y decirlo forma
    parte de la lección.
    """
    log = kpis.logistica(grupo)
    flota_t = palancas.linea_base(grupo)["flota_t"]
    # Capacidad media ponderada de la flota, en toneladas por vehículo.
    furgonetas, rigidos = p.FLOTA[grupo]
    capacidad = (furgonetas * 1.2 + rigidos * 12.0) / (furgonetas + rigidos)
    t_km = log["km_totales"] * capacidad * log["ocupacion_media"]
    return flota_t * 1_000_000 / t_km if t_km else 0.0


def _km_vacio(grupo: str) -> float:
    return kpis.logistica(grupo)["pct_km_en_vacio"] * 100


def _factor_carga(grupo: str) -> float:
    return kpis.logistica(grupo)["ocupacion_media"] * 100


def _energia(grupo: str) -> float:
    return kpis.energia_resumen(grupo)["electricidad_kwh"] / 1_000


def _refrigerantes(grupo: str) -> float:
    return palancas.linea_base(grupo)["refrigerante_t"]


def _residuo_generado(grupo: str) -> float:
    return circular.inventario(grupo)["generado_t"]


def _tasa_reciclaje(grupo: str) -> float:
    return circular.inventario(grupo)["pct_reciclado"] * 100


def _circularidad(grupo: str) -> float:
    return circular.inventario(grupo)["pct_circularidad"] * 100


def _envase(grupo: str) -> float:
    return circular.envases_resumen(grupo)["total_t"]


def _merma(grupo: str) -> float:
    return kpis.inventario_resumen(grupo)["pct_merma"] * 100


def _devoluciones(grupo: str) -> float:
    return circular.devoluciones_resumen(grupo)["tasa_media"] * 100


def _plantilla(grupo: str) -> float:
    tabla = _plantilla_anual(grupo)
    return float(tabla["empleados"].mean())


def _plantilla_anual(grupo: str) -> pd.DataFrame:
    anio = datos.ultimo_anio()
    tabla = datos.de_la_filial("plantilla", grupo)
    return tabla[tabla["mes"].dt.year == anio]


def _temporalidad(grupo: str) -> float:
    return float(_plantilla_anual(grupo)["pct_temporales"].mean()) * 100


def _rotacion(grupo: str) -> float:
    return float(_plantilla_anual(grupo)["pct_rotacion"].sum()) * 100


def _accidentes(grupo: str) -> float:
    """Índice de frecuencia: accidentes con baja por millón de horas."""
    tabla = _plantilla_anual(grupo)
    horas = float(tabla["empleados"].sum()) * 150
    return float(tabla["accidentes_con_baja"].sum()) * 1_000_000 / horas if horas else 0.0


def _formacion(grupo: str) -> float:
    tabla = _plantilla_anual(grupo)
    return float(tabla["horas_formacion"].sum()) / float(tabla["empleados"].mean())


def _brecha(grupo: str) -> float:
    return float(_plantilla_anual(grupo)["brecha_salarial"].mean()) * 100


def _mujeres_direccion(grupo: str) -> float:
    return float(_plantilla_anual(grupo)["pct_mujeres_direccion"].mean()) * 100


def _compra_riesgo(grupo: str) -> float:
    """Parte de la compra que viene de países con riesgo laboral alto."""
    anio = datos.ultimo_anio()
    compras = datos.de_la_filial("compras", grupo)
    compras = compras[compras["mes"].dt.year == anio]
    total = float(compras["importe_eur"].sum())
    if total <= 0:
        return 0.0
    riesgo = float(
        compras[compras["pais_origen"].isin(p.PAISES_RIESGO_LABORAL)]
        ["importe_eur"].sum()
    )
    return riesgo / total * 100


def _proveedores_evaluados(grupo: str) -> float:
    return p.PCT_PROVEEDORES_EVALUADOS[grupo] * 100


def _puntualidad(grupo: str) -> float:
    return kpis.cadena_suministro(grupo)["pct_puntualidad"] * 100


INDICADORES: list[Indicador] = [
    # --- Ambiental · emisiones propias
    Indicador("e_huella_12", "Emisiones de alcances 1 y 2", "emisiones_operativas",
              "ESRS E1 · GHG Protocol", "t CO₂e", "alta", _huella_12,
              "Medido a partir de consumos reales de energía y combustible."),
    Indicador("e_intensidad", "Intensidad de emisiones", "emisiones_operativas",
              "ESRS E1", "t CO₂e / M€", "alta", _intensidad_12,
              "Es la cifra que permite comparar filiales de tamaños distintos."),
    Indicador("e_energia", "Consumo eléctrico", "emisiones_operativas",
              "ESRS E1", "MWh", "alta", _energia),
    Indicador("e_refrigerantes", "Fugas de gases fluorados", "refrigerantes",
              "ESRS E1", "t CO₂e", "media", _refrigerantes,
              "Estimadas a partir de la carga instalada y una tasa de fuga."),
    # --- Ambiental · transporte
    Indicador("e_transporte", "Emisiones de la flota", "transporte",
              "ESRS E1 · ISO 14083", "t CO₂e", "alta", _emisiones_transporte),
    Indicador("e_intensidad_tkm", "Intensidad del transporte", "transporte",
              "ISO 14083 · GLEC", "g CO₂e / t·km", "media", _intensidad_transporte,
              "Aproximación: la norma pide desagregar por trayecto y modo."),
    Indicador("e_vacio", "Kilómetros en vacío", "transporte",
              "ISO 14083 · GLEC", "%", "alta", _km_vacio),
    Indicador("e_carga", "Factor de carga medio", "transporte",
              "ISO 14083 · GLEC", "%", "alta", _factor_carga),
    # --- Ambiental · cadena de valor
    Indicador("e_huella_3", "Emisiones de alcance 3", "cadena_suministro",
              "ESRS E1 · GHG Protocol", "t CO₂e", "baja", _huella_3,
              "Estimación por gasto. Un descuento del proveedor la bajaría "
              "sin que cambiase nada físico."),
    # --- Ambiental · materiales
    Indicador("e_residuo", "Residuo generado", "residuos_envase",
              "ESRS E5", "t", "alta", _residuo_generado),
    Indicador("e_reciclaje", "Tasa de reciclaje", "residuos_envase",
              "ESRS E5", "%", "alta", _tasa_reciclaje,
              "Cuánto se manda a reciclar. No es lo mismo que cuánto vuelve."),
    Indicador("e_circularidad", "Material que vuelve al ciclo", "residuos_envase",
              "ESRS E5", "%", "media", _circularidad,
              "Descuenta lo que se pierde en recogida y transformación."),
    Indicador("e_envase", "Envase puesto en circulación", "residuos_envase",
              "ESRS E5", "t", "media", _envase),
    Indicador("e_merma", "Merma sobre ventas", "merma",
              "ESRS E5", "%", "alta", _merma),
    Indicador("e_devoluciones", "Tasa de devolución online", "merma",
              "ESRS E5", "%", "media", _devoluciones),
    # --- Social
    Indicador("s_plantilla", "Plantilla media", "plantilla",
              "ESRS S1 · GRI 2", "empleados", "alta", _plantilla),
    Indicador("s_temporalidad", "Contratos temporales", "plantilla",
              "ESRS S1", "%", "alta", _temporalidad),
    Indicador("s_rotacion", "Rotación anual", "plantilla",
              "ESRS S1", "%", "alta", _rotacion),
    Indicador("s_formacion", "Formación por empleado", "plantilla",
              "ESRS S1", "horas", "alta", _formacion),
    Indicador("s_brecha", "Brecha salarial de género", "plantilla",
              "ESRS S1", "%", "alta", _brecha),
    Indicador("s_mujeres_direccion", "Mujeres en dirección", "plantilla",
              "ESRS S1", "%", "alta", _mujeres_direccion),
    Indicador("s_accidentes", "Índice de accidentes con baja", "seguridad",
              "ESRS S1 · GRI 403", "por millón de horas", "alta", _accidentes),
    Indicador("s_compra_riesgo", "Compra en países de riesgo laboral",
              "trabajo_cadena", "ESRS S2", "%", "media", _compra_riesgo,
              "Indicador de exposición, no de incumplimiento: dice dónde hay "
              "que mirar, no que haya un problema."),
    # --- Gobernanza
    Indicador("g_proveedores", "Proveedores con evaluación ESG", "gobernanza",
              "ESRS G1 · GRI 308", "%", "alta", _proveedores_evaluados),
    Indicador("g_puntualidad", "Fiabilidad de proveedores", "gobernanza",
              "ESRS G1", "%", "alta", _puntualidad),
]

POR_CODIGO = {indicador.codigo: indicador for indicador in INDICADORES}


def valor(grupo: str, codigo: str) -> float:
    """El valor del indicador en esta filial."""
    return float(POR_CODIGO[codigo].calculo(grupo))


def catalogo(grupo: str) -> pd.DataFrame:
    """El catálogo completo con los valores de la filial."""
    filas = []
    for indicador in INDICADORES:
        tema = POR_TEMA[indicador.tema]
        filas.append({
            "codigo": indicador.codigo,
            "nombre": indicador.nombre,
            "tema": indicador.tema,
            "nombre_tema": tema.nombre,
            "dimension": tema.dimension,
            "estandar": indicador.estandar,
            "unidad": indicador.unidad,
            "calidad": indicador.calidad,
            "valor": valor(grupo, indicador.codigo),
            "nota": indicador.nota,
        })
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# Doble materialidad
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _crudos() -> dict[str, dict[str, tuple[float, float]]]:
    """Métricas brutas de impacto y financieras por filial y asunto.

    Se calculan con los datos del caso. La materialidad no está escrita a
    mano en ninguna parte: sale de lo que cada filial es.
    """
    salida: dict[str, dict[str, tuple[float, float]]] = {}
    for filial in filiales.listar():
        g = filial.grupo
        ventas = kpis.ventas_totales(g)
        millones = ventas / 1_000_000
        base = palancas.linea_base(g)
        log = kpis.logistica(g)
        flota = kpis.flota_resumen(g)
        energia = kpis.energia_resumen(g)
        inv_c = circular.inventario(g)
        env = circular.envases_resumen(g)
        inv_kpi = kpis.inventario_resumen(g)

        salida[g] = {
            # (impacto, financiera)
            "emisiones_operativas": (
                base["total_t"] / millones,
                (energia["coste_eur"] + flota["coste_eur"]) / ventas,
            ),
            "transporte": (
                flota["litros"] / millones,
                flota["coste_eur"] / ventas,
            ),
            "refrigerantes": (
                base["refrigerante_t"] / base["total_t"],
                base["refrigerante_t"] / millones,
            ),
            "cadena_suministro": (
                # Cuántas veces mayor es el alcance 3 que lo que la filial
                # controla. Discrimina mucho mejor que el porcentaje, que
                # sale casi igual en las cinco.
                alcance3.inventario(g)["veces_mayor"],
                kpis.cadena_suministro(g)["compras_eur"] / ventas,
            ),
            "residuos_envase": (
                # La parte del material que NO vuelve al ciclo. El envase por
                # millón vendido sale casi idéntico en las cinco y por tanto
                # no dice nada.
                1 - inv_c["pct_circularidad"],
                env["coste_eur"] / ventas,
            ),
            "merma": (
                inv_c["merma_t"] / millones,
                inv_kpi["merma_eur"] / ventas,
            ),
            "plantilla": (
                _temporalidad(g) + _rotacion(g),
                _rotacion(g) / 100,
            ),
            "seguridad": (
                _accidentes(g),
                _accidentes(g) / 100,
            ),
            "trabajo_cadena": (
                _compra_riesgo(g),
                _compra_riesgo(g) / 100,
            ),
            "gobernanza": (
                100 - _proveedores_evaluados(g),
                (100 - _proveedores_evaluados(g)) / 100,
            ),
        }
    return salida


#: Cuántos asuntos informa como mínimo cada filial, aunque ninguno pase el
#: umbral. Una memoria que dijera «no tenemos asuntos materiales» no la
#: firmaría nadie, y menos una empresa de 1.149 M€.
MINIMO_ASUNTOS = 4


def _escalar(valores: dict[str, float]) -> dict[str, float]:
    """Lleva las cinco filiales a una escala de 1 a 5.

    Se escala contra la **media** y no contra el mínimo y el máximo. La
    diferencia importa y es conceptual: con una escala de mínimo a máximo, la
    filial que mejor opera se quedaría con un 1 en todo y por tanto sin
    ningún asunto material. Y eso es falso. **La materialidad no es
    desempeño**: el transporte es material en Madrid porque Madrid mueve
    muchísima mercancía, no porque la mueva mal.

    Con esta escala, estar en la media da un 3 y destacar da un 4 o un 5.
    """
    media = sum(valores.values()) / len(valores)
    if media <= 0:
        return {g: 3.0 for g in valores}
    return {
        g: max(1.0, min(5.0, 3.0 * v / media)) for g, v in valores.items()
    }


@lru_cache(maxsize=None)
def _matriz(grupo: str) -> pd.DataFrame:
    """La matriz de doble materialidad de la filial.

    Cada asunto recibe dos notas de 1 a 5: cuánto afecta la filial al mundo
    y cuánto le afecta a ella el asunto. **Basta con que una de las dos pase
    del umbral** para que haya que informar: eso es exactamente lo que dice
    la doble materialidad, y es lo que casi todos los grupos entienden mal a
    la primera.
    """
    crudos = _crudos()
    filas = []
    for tema in TEMAS:
        impacto = _escalar({g: crudos[g][tema.codigo][0] for g in crudos})
        financiera = _escalar({g: crudos[g][tema.codigo][1] for g in crudos})
        filas.append({
            "tema": tema.codigo,
            "nombre_tema": tema.nombre,
            "dimension": tema.dimension,
            "explicacion": tema.explicacion,
            "impacto": round(impacto[grupo], 2),
            "financiera": round(financiera[grupo], 2),
        })

    tabla = pd.DataFrame(filas)
    # Basta con que una de las dos supere el umbral: eso es la doble
    # materialidad, y es lo que casi todos entienden mal a la primera.
    tabla["nota"] = tabla[["impacto", "financiera"]].max(axis=1)
    tabla["material"] = tabla["nota"] >= UMBRAL_MATERIALIDAD

    # Suelo: aunque ninguno pase el umbral, se informa de los más altos.
    if int(tabla["material"].sum()) < MINIMO_ASUNTOS:
        corte = tabla["nota"].nlargest(MINIMO_ASUNTOS).min()
        tabla["material"] = tabla["nota"] >= corte

    return tabla.sort_values(
        ["material", "nota"], ascending=[False, False], ignore_index=True
    )


def matriz_materialidad(grupo: str) -> pd.DataFrame:
    """Copia de la matriz, para que nadie pueda modificar la cacheada.

    Calcularla cuesta casi un segundo porque recorre las cinco filiales
    enteras. Sin caché, un paso de la sesión que la pidiera tres veces
    tardaría tres segundos en dibujarse.
    """
    return _matriz(grupo).copy()


def temas_materiales(grupo: str) -> list[str]:
    tabla = _matriz(grupo)
    return tabla[tabla["material"]]["tema"].tolist()


def limpiar_cache() -> None:
    """Olvida la materialidad calculada. La llama `core.datos`."""
    _crudos.cache_clear()
    _matriz.cache_clear()


datos.registrar_cache(limpiar_cache)


# --------------------------------------------------------------------------
# Las declaraciones: donde está la tentación
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Declaracion:
    codigo: str
    pregunta: str
    opciones: dict[str, str]      # clave -> texto que se publica
    correcta: str
    hallazgo: str                 # qué dice el verificador si se equivocan
    gravedad: str                 # salvedad · grave
    porque: str


DECLARACIONES: list[Declaracion] = [
    Declaracion(
        codigo="reduccion",
        pregunta="¿Cómo presentáis la reducción de emisiones comprometida?",
        opciones={
            "sumada": "«Reduciremos nuestras emisiones un 35 %», sumando el "
                      "25 % de alcances 1 y 2 y el 10 % de alcance 3.",
            "separada": "«Reduciremos un 25 % los alcances 1 y 2 y un 10 % el "
                        "alcance 3», con los dos inventarios por separado.",
            "solo_12": "«Reduciremos nuestras emisiones un 25 %», sin "
                       "mencionar el alcance 3.",
        },
        correcta="separada",
        hallazgo="La reducción se presenta de forma que induce a error sobre "
                 "el alcance real del compromiso.",
        gravedad="grave",
        porque="Son dos inventarios distintos con denominadores distintos. "
               "Sumar los porcentajes no significa nada, y el SBTi exige "
               "desde su norma v2.0 que los objetivos de alcances 1 y 2 y "
               "los de alcance 3 se fijen y se comuniquen por separado.",
    ),
    Declaracion(
        codigo="frontera",
        pregunta="¿Declaráis qué queda dentro y qué queda fuera del inventario?",
        opciones={
            "si": "Se declara la frontera: alcances 1, 2 y 3, con las "
                  "categorías de alcance 3 que se han calculado y las que no.",
            "no": "Se publica la cifra de huella sin especificar qué incluye.",
        },
        correcta="si",
        hallazgo="No se declara la frontera del inventario, de modo que la "
                 "cifra publicada no es interpretable ni comparable.",
        gravedad="grave",
        porque="Una huella sin frontera declarada no dice nada: no se sabe "
               "si es grande porque la empresa emite mucho o porque ha "
               "contado más cosas que su competidor.",
    ),
    Declaracion(
        codigo="metodo_alcance3",
        pregunta="¿Cómo presentáis la cifra de alcance 3?",
        opciones={
            "con_metodo": "Con el método y su limitación: estimación por "
                          "gasto, sensible a los precios de compra.",
            "sin_metodo": "Como una cifra más del inventario, con el mismo "
                          "rango de decimales que las demás.",
        },
        correcta="con_metodo",
        hallazgo="La cifra de alcance 3 se presenta con una precisión que el "
                 "método empleado no soporta.",
        gravedad="salvedad",
        porque="La estimación por gasto tiene un defecto conocido: negociar "
               "un descuento con el proveedor baja la huella declarada sin "
               "que cambie nada en ninguna fábrica.",
    ),
    Declaracion(
        codigo="circularidad",
        pregunta="¿Qué indicador de materiales destacáis?",
        opciones={
            "circularidad": "El material que vuelve realmente al ciclo, "
                            "descontando pérdidas de recogida y proceso.",
            "reciclaje": "La tasa de reciclaje, que es la cifra más alta y "
                         "la más reconocible.",
        },
        correcta="circularidad",
        hallazgo="Se destaca la tasa de reciclaje en lugar del material "
                 "efectivamente recirculado, lo que sobrestima el desempeño.",
        gravedad="salvedad",
        porque="Entre una cifra y otra hay más de treinta puntos en algunas "
               "filiales. La tasa de reciclaje mide una intención; la "
               "circularidad mide un resultado.",
    ),
    Declaracion(
        codigo="normalizacion",
        pregunta="¿Publicáis solo cifras absolutas o también por unidad de "
                 "negocio?",
        opciones={
            "ambas": "Ambas: toneladas totales y toneladas por millón "
                     "vendido.",
            "absoluta": "Solo absolutas, que es como se ven mejor las "
                        "reducciones.",
        },
        correcta="ambas",
        hallazgo="Solo se publican magnitudes absolutas, lo que impide "
                 "distinguir la mejora real de la variación de actividad.",
        gravedad="salvedad",
        porque="Una filial puede bajar sus emisiones absolutas simplemente "
               "porque ha vendido menos. Sin intensidad, no se sabe si ha "
               "mejorado o ha encogido.",
    ),
]

POR_DECLARACION = {d.codigo: d for d in DECLARACIONES}


# --------------------------------------------------------------------------
# La revisión del verificador
# --------------------------------------------------------------------------

def evaluar(grupo: str, seleccion: list[str],
            declaraciones: dict[str, str]) -> dict:
    """Lo que diría un verificador externo ante esta memoria.

    Sustituye al presupuesto de las sesiones 2 y 3: aquí la restricción no
    es el dinero, es que la memoria resista una revisión. Nunca lanza
    excepción por una entrada rara.
    """
    seleccion = [c for c in (seleccion or []) if c in POR_CODIGO]
    materiales = temas_materiales(grupo)
    cubiertos = {POR_CODIGO[c].tema for c in seleccion}

    hallazgos = []

    # 1 · Asuntos materiales sin ningún indicador.
    sin_cubrir = [t for t in materiales if t not in cubiertos]
    for tema in sin_cubrir:
        hallazgos.append({
            "codigo": f"cobertura_{tema}",
            "gravedad": "grave",
            "titulo": f"Asunto material sin información: "
                      f"{POR_TEMA[tema].nombre}",
            "detalle": "La matriz de materialidad de la filial señala este "
                       "asunto como material y la memoria no publica ningún "
                       "indicador sobre él.",
        })

    # 2 · Las cinco tentaciones.
    for declaracion in DECLARACIONES:
        elegida = declaraciones.get(declaracion.codigo)
        if elegida is None:
            hallazgos.append({
                "codigo": declaracion.codigo,
                "gravedad": "salvedad",
                "titulo": "Declaración pendiente",
                "detalle": f"No se ha resuelto: {declaracion.pregunta}",
            })
        elif elegida != declaracion.correcta:
            hallazgos.append({
                "codigo": declaracion.codigo,
                "gravedad": declaracion.gravedad,
                "titulo": declaracion.hallazgo,
                "detalle": declaracion.porque,
            })

    # 3 · Exceso de indicadores: informar de todo es no informar de nada.
    if len(seleccion) > MAXIMO_INDICADORES:
        hallazgos.append({
            "codigo": "exceso",
            "gravedad": "salvedad",
            "titulo": "La memoria publica más indicadores de los admitidos",
            "detalle": f"Se han seleccionado {len(seleccion)} y el máximo es "
                       f"{MAXIMO_INDICADORES}. Publicarlo todo no es "
                       f"transparencia: es enterrar lo material.",
        })

    # 4 · Memoria vacía.
    if not seleccion:
        hallazgos.append({
            "codigo": "vacia",
            "gravedad": "grave",
            "titulo": "La memoria no publica ningún indicador",
            "detalle": "No hay nada que verificar.",
        })

    graves = [h for h in hallazgos if h["gravedad"] == "grave"]
    salvedades = [h for h in hallazgos if h["gravedad"] == "salvedad"]

    if graves:
        opinion = "desfavorable"
    elif salvedades:
        opinion = "con salvedades"
    else:
        opinion = "favorable"

    return {
        "opinion": opinion,
        "hallazgos": hallazgos,
        "graves": len(graves),
        "salvedades": len(salvedades),
        "temas_materiales": materiales,
        "temas_cubiertos": sorted(cubiertos),
        "temas_sin_cubrir": sin_cubrir,
        "cobertura": (len(materiales) - len(sin_cubrir)) / len(materiales)
                     if materiales else 1.0,
        "indicadores": seleccion,
        "dentro_del_limite": len(seleccion) <= MAXIMO_INDICADORES,
    }


def memoria_ejemplar(grupo: str) -> tuple[list[str], dict[str, str]]:
    """Una memoria que pasaría la revisión sin salvedades.

    Sirve para las pruebas y para que el profesor pueda enseñar en la puesta
    en común que el ejercicio tiene solución.
    """
    seleccion = []
    for tema in temas_materiales(grupo):
        for indicador in INDICADORES:
            if indicador.tema == tema:
                seleccion.append(indicador.codigo)
                break
    seleccion = seleccion[:MAXIMO_INDICADORES]
    declaraciones = {d.codigo: d.correcta for d in DECLARACIONES}
    return seleccion, declaraciones
