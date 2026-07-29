"""Cálculos del diagnóstico de una filial.

Todo lo que la Sesión 1 muestra al alumno se calcula aquí. Sin Streamlit
dentro: así se puede probar sin levantar la aplicación, y las sesiones
siguientes podrán reutilizarlo sin arrastrar la interfaz.

Convención: salvo que se diga otra cosa, los importes van en euros, las
emisiones en toneladas de CO₂ equivalente y el año por defecto es el último
del que hay datos.
"""

from __future__ import annotations

import pandas as pd

from core import datos, filiales

ASIA = ["China", "Bangladés", "Vietnam"]

#: Nombre legible de cada formato de punto de venta.
NOMBRE_FORMATO = {
    "gran_almacen": "Gran almacén",
    "hipermercado": "Hipermercado / Gourmet",
    "especializada": "Tienda especializada",
    "conveniencia": "Conveniencia",
}


# --------------------------------------------------------------------------
# Paso 1 · El retrato de la filial
# --------------------------------------------------------------------------

def retrato(grupo: str, anio: int | None = None) -> dict:
    """Las cifras de cabecera: qué tamaño tiene la filial que diriges."""
    anio = anio or datos.ultimo_anio()
    filial = filiales.obtener(grupo)

    tiendas = datos.de_la_filial("tiendas", grupo)
    flota = datos.de_la_filial("flota", grupo)
    ventas = ventas_totales(grupo, anio)

    return {
        "nombre": filial.nombre,
        "codigo": filial.codigo,
        "ciudad": filial.ciudad,
        "ventas_eur": ventas,
        "puntos_de_venta": len(tiendas),
        "superficie_m2": int(tiendas["superficie_m2"].sum()),
        "ventas_por_m2": ventas / tiendas["superficie_m2"].sum(),
        "vehiculos": len(flota),
        "antiguedad_flota": float(flota["antiguedad_anios"].mean()),
        "centros_logisticos": filial.centros_logisticos,
        "tiendas_por_centro": len(tiendas) / filial.centros_logisticos,
        "grandes_almacenes": int((tiendas["formato"] == "gran_almacen").sum()),
    }


def ventas_totales(grupo: str, anio: int | None = None) -> float:
    """Ventas de la filial: tienda física más canal online.

    Es fácil equivocarse aquí. Quien sume solo `ventas_diarias.csv` se deja
    fuera entre el 13 % y el 25 % del negocio según la filial.
    """
    anio = anio or datos.ultimo_anio()
    fisicas = datos.de_la_filial("ventas_diarias", grupo)
    online = datos.de_la_filial("pedidos_online", grupo)
    return float(
        fisicas.loc[fisicas["fecha"].dt.year == anio, "ventas_eur"].sum()
        + online.loc[online["fecha"].dt.year == anio, "ventas_eur"].sum()
    )


# --------------------------------------------------------------------------
# Paso 2 · Cómo vende
# --------------------------------------------------------------------------

def ventas_por_mes(grupo: str) -> pd.DataFrame:
    """Serie mensual de ventas físicas y online, para ver la estacionalidad."""
    fisicas = datos.de_la_filial("ventas_diarias", grupo)
    online = datos.de_la_filial("pedidos_online", grupo)

    f = (fisicas.assign(mes=fisicas["fecha"].dt.to_period("M").dt.to_timestamp())
         .groupby("mes", as_index=False)["ventas_eur"].sum()
         .rename(columns={"ventas_eur": "tienda_eur"}))
    o = (online.assign(mes=online["fecha"].dt.to_period("M").dt.to_timestamp())
         .groupby("mes", as_index=False)["ventas_eur"].sum()
         .rename(columns={"ventas_eur": "online_eur"}))

    serie = f.merge(o, on="mes", how="outer").fillna(0.0)
    serie["total_eur"] = serie["tienda_eur"] + serie["online_eur"]
    return serie.sort_values("mes", ignore_index=True)


def ventas_por_formato(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """Cuánto aporta cada formato de tienda y con qué productividad."""
    anio = anio or datos.ultimo_anio()
    ventas = datos.de_la_filial("ventas_diarias", grupo)
    ventas = ventas[ventas["fecha"].dt.year == anio]
    tiendas = datos.de_la_filial("tiendas", grupo)

    por_formato = ventas.groupby("formato", as_index=False)["ventas_eur"].sum()
    superficie = tiendas.groupby("formato", as_index=False).agg(
        superficie_m2=("superficie_m2", "sum"), tiendas=("codigo_tienda", "count")
    )
    tabla = por_formato.merge(superficie, on="formato")
    tabla["ventas_por_m2"] = tabla["ventas_eur"] / tabla["superficie_m2"]
    tabla["pct_ventas"] = tabla["ventas_eur"] / tabla["ventas_eur"].sum()
    tabla["nombre_formato"] = tabla["formato"].map(NOMBRE_FORMATO)
    return tabla.sort_values("ventas_eur", ascending=False, ignore_index=True)


def ventas_por_categoria(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """Peso de cada categoría, separando tienda física de canal online."""
    anio = anio or datos.ultimo_anio()
    categoria = datos.de_la_filial("ventas_categoria", grupo)
    categoria = categoria[categoria["mes"].dt.year == anio]
    online = datos.de_la_filial("pedidos_online", grupo)
    online = online[online["fecha"].dt.year == anio]

    tabla = (categoria.groupby(["categoria", "nombre_categoria"], as_index=False)
             ["ventas_eur"].sum().rename(columns={"ventas_eur": "tienda_eur"}))
    tabla["online_eur"] = tabla["categoria"].map(
        lambda c: float(online[f"ventas_{c}_eur"].sum())
    )
    tabla["total_eur"] = tabla["tienda_eur"] + tabla["online_eur"]
    tabla["pct_total"] = tabla["total_eur"] / tabla["total_eur"].sum()
    tabla["pct_online"] = tabla["online_eur"] / tabla["total_eur"]
    return tabla.sort_values("total_eur", ascending=False, ignore_index=True)


def canal(grupo: str, anio: int | None = None) -> dict:
    """Peso del canal online y comportamiento del pedido."""
    anio = anio or datos.ultimo_anio()
    online = datos.de_la_filial("pedidos_online", grupo)
    online = online[online["fecha"].dt.year == anio]
    total = ventas_totales(grupo, anio)

    return {
        "ventas_online_eur": float(online["ventas_eur"].sum()),
        "cuota_online": float(online["ventas_eur"].sum()) / total,
        "pedidos": int(online["pedidos"].sum()),
        "ticket_medio_online": float(online["ventas_eur"].sum() / online["pedidos"].sum()),
        "pct_recogida_en_tienda": float(online["pct_recogida_en_tienda"].mean()),
    }


def crecimiento(grupo: str) -> dict:
    """Comparación entre los dos años disponibles."""
    anios = datos.anios_disponibles()
    anterior, actual = anios[0], anios[-1]
    v_anterior = ventas_totales(grupo, anterior)
    v_actual = ventas_totales(grupo, actual)
    return {
        "anio_anterior": anterior,
        "anio_actual": actual,
        "ventas_anterior": v_anterior,
        "ventas_actual": v_actual,
        "variacion": v_actual / v_anterior - 1,
    }


# --------------------------------------------------------------------------
# Paso 3 · Cómo opera
# --------------------------------------------------------------------------

def logistica(grupo: str, anio: int | None = None) -> dict:
    """Indicadores de reparto: kilómetros, vacío, ocupación y fallos."""
    anio = anio or datos.ultimo_anio()
    rutas = datos.de_la_filial("rutas", grupo)
    rutas = rutas[rutas["fecha"].dt.year == anio]
    validas = rutas.dropna(subset=["km_totales"])

    km = float(validas["km_totales"].sum())
    vacio = float(validas["km_en_vacio"].sum())
    return {
        "km_totales": km,
        "km_en_vacio": vacio,
        "pct_km_en_vacio": vacio / km if km else 0.0,
        "rutas": int(rutas["num_rutas"].sum()),
        "paradas": int(rutas["paradas"].sum()),
        "ocupacion_media": float(rutas["ocupacion_media"].mean()),
        "entregas_fallidas": int(rutas["entregas_fallidas"].sum()),
        "pct_entregas_fallidas": float(
            rutas["entregas_fallidas"].sum() / rutas["paradas"].sum()
        ),
        "partes_sin_km": int(rutas["km_totales"].isna().sum()),
    }


def flota_resumen(grupo: str, anio: int | None = None) -> dict:
    """Consumo de la flota y su coste."""
    anio = anio or datos.ultimo_anio()
    consumo = datos.de_la_filial("consumo_flota", grupo)
    consumo = consumo[consumo["mes"].dt.year == anio]
    flota = datos.de_la_filial("flota", grupo)

    litros = float(consumo["litros"].sum())
    km = float(consumo["km"].sum())
    return {
        "vehiculos": len(flota),
        "litros": litros,
        "km": km,
        "consumo_medio_l_100km": litros / km * 100 if km else 0.0,
        "coste_eur": float(consumo["coste_eur"].sum()),
        "antiguedad_media": float(flota["antiguedad_anios"].mean()),
        "pct_euro6": float((flota["norma_emisiones"].str.startswith("Euro 6")).mean()),
    }


def cadena_suministro(grupo: str, anio: int | None = None) -> dict:
    """Plazos, origen y fiabilidad de las compras."""
    anio = anio or datos.ultimo_anio()
    compras = datos.de_la_filial("compras", grupo)
    compras = compras[compras["mes"].dt.year == anio]

    importe = float(compras["importe_eur"].sum())
    return {
        "compras_eur": importe,
        "proveedores": int(compras["codigo_proveedor"].nunique()),
        "plazo_medio_dias": float(
            (compras["plazo_real_dias"] * compras["importe_eur"]).sum() / importe
        ),
        "pct_compra_asiatica": float(
            compras[compras["pais_origen"].isin(ASIA)]["importe_eur"].sum() / importe
        ),
        "pct_puntualidad": float(
            compras["entregas_a_tiempo"].sum() / compras["entregas"].sum()
        ),
    }


def compras_por_origen(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """Reparto de las compras por país de origen."""
    anio = anio or datos.ultimo_anio()
    compras = datos.de_la_filial("compras", grupo)
    compras = compras[compras["mes"].dt.year == anio]

    tabla = compras.groupby("pais_origen", as_index=False).agg(
        importe_eur=("importe_eur", "sum"),
        plazo_medio_dias=("plazo_real_dias", "mean"),
        entregas=("entregas", "sum"),
        entregas_a_tiempo=("entregas_a_tiempo", "sum"),
    )
    tabla["pct_compras"] = tabla["importe_eur"] / tabla["importe_eur"].sum()
    tabla["pct_puntualidad"] = tabla["entregas_a_tiempo"] / tabla["entregas"]
    return tabla.sort_values("importe_eur", ascending=False, ignore_index=True)


def inventario_resumen(grupo: str, anio: int | None = None) -> dict:
    """Capital inmovilizado en stock y pérdida por merma."""
    anio = anio or datos.ultimo_anio()
    inventario = datos.de_la_filial("inventario", grupo)
    inventario = inventario[inventario["mes"].dt.year == anio]

    merma = float(inventario["merma_eur"].sum())
    ventas_tienda = float(
        datos.de_la_filial("ventas_categoria", grupo)
        .pipe(lambda d: d[d["mes"].dt.year == anio])["ventas_eur"].sum()
    )
    return {
        "stock_medio_eur": float(inventario.groupby("mes")["stock_medio_eur"].sum().mean()),
        "dias_cobertura": float(inventario["dias_cobertura"].mean()),
        "rotacion": float(inventario["rotacion_anualizada"].mean()),
        "merma_eur": merma,
        "pct_merma": merma / ventas_tienda if ventas_tienda else 0.0,
    }


# --------------------------------------------------------------------------
# Paso 4 · Qué consume y qué emite
# --------------------------------------------------------------------------

def energia_resumen(grupo: str, anio: int | None = None) -> dict:
    """Consumo energético de tiendas y centros.

    Los huecos de lectura se imputan con la media de la propia instalación:
    ignorarlos infravaloraría el consumo. El número de huecos se devuelve
    aparte, porque detectarlos forma parte del diagnóstico.
    """
    anio = anio or datos.ultimo_anio()
    energia = datos.de_la_filial("energia", grupo)
    energia = energia[energia["mes"].dt.year == anio]

    huecos = int(energia["electricidad_kwh"].isna().sum())
    completado = energia.copy()
    completado["electricidad_kwh"] = completado.groupby("codigo_instalacion")[
        "electricidad_kwh"
    ].transform(lambda s: s.fillna(s.mean()))

    electricidad = float(completado["electricidad_kwh"].sum())
    gas = float(completado["gas_kwh"].sum())
    ventas = ventas_totales(grupo, anio)

    return {
        "electricidad_kwh": electricidad,
        "gas_kwh": gas,
        "coste_eur": float(completado["coste_eur"].sum()),
        "intensidad_mwh_por_meur": electricidad / 1_000 / (ventas / 1_000_000),
        "lecturas_ausentes": huecos,
    }


def huella(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """Emisiones de la filial por fuente, con su alcance.

    Es la tabla que abre la Sesión 2: aquí el alumno ve por primera vez de
    dónde sale realmente el CO₂ de su filial, y casi nunca es de donde
    esperaba.
    """
    anio = anio or datos.ultimo_anio()

    energia = datos.de_la_filial("energia", grupo)
    energia = energia[energia["mes"].dt.year == anio].copy()
    energia["electricidad_kwh"] = energia.groupby("codigo_instalacion")[
        "electricidad_kwh"
    ].transform(lambda s: s.fillna(s.mean()))

    consumo = datos.de_la_filial("consumo_flota", grupo)
    consumo = consumo[consumo["mes"].dt.year == anio]

    refrigerantes = datos.de_la_filial("refrigerantes", grupo)
    refrigerantes = refrigerantes[refrigerantes["anio"] == anio]

    factores = datos.cargar("factores_emision").set_index("concepto")["factor"]

    fuentes = [
        ("Electricidad", 2, float(energia["electricidad_kwh"].sum())
         * factores["Electricidad (mix español)"]),
        ("Gasóleo de la flota", 1, float(consumo["co2e_kg"].sum())),
        ("Fugas de refrigerante", 1, float(refrigerantes["co2e_kg"].sum())),
        ("Gas natural", 1, float(energia["gas_kwh"].sum()) * factores["Gas natural"]),
    ]

    tabla = pd.DataFrame(fuentes, columns=["fuente", "alcance", "co2e_kg"])
    tabla["co2e_t"] = tabla["co2e_kg"] / 1_000
    tabla["pct"] = tabla["co2e_kg"] / tabla["co2e_kg"].sum()
    return tabla.sort_values("co2e_kg", ascending=False, ignore_index=True)


def huella_total(grupo: str, anio: int | None = None) -> float:
    """Toneladas de CO₂ equivalente al año."""
    return float(huella(grupo, anio)["co2e_t"].sum())


def residuos_resumen(grupo: str, anio: int | None = None) -> dict:
    """Residuos generados y proporción que se recicla."""
    anio = anio or datos.ultimo_anio()
    residuos = datos.de_la_filial("residuos", grupo)
    residuos = residuos[residuos["mes"].dt.year == anio]
    tipos = [c for c in residuos.columns if c.endswith("_kg") and c != "total_kg"]
    return {
        "total_t": float(residuos["total_kg"].sum()) / 1_000,
        "pct_reciclado": float(residuos["pct_reciclado"].mean()),
        "por_tipo_t": {
            c.replace("_kg", ""): float(residuos[c].sum()) / 1_000 for c in tipos
        },
    }


# --------------------------------------------------------------------------
# Paso 5 · Comparación entre filiales
# --------------------------------------------------------------------------

#: Indicadores de la tabla comparativa. Para cada uno: nombre legible,
#: unidad y si conviene que sea alto (True) o bajo (False).
INDICADORES = [
    ("ventas_m_eur", "Ventas", "M€", True),
    ("ventas_por_m2", "Ventas por m²", "€/m²", True),
    ("cuota_online", "Cuota online", "%", True),
    ("pct_km_en_vacio", "Kilómetros en vacío", "%", False),
    ("pct_entregas_fallidas", "Entregas fallidas", "%", False),
    ("litros_por_meur", "Gasóleo por millón vendido", "L/M€", False),
    ("intensidad_energetica", "Energía por millón vendido", "MWh/M€", False),
    ("margen_bruto", "Margen bruto", "%", True),
    ("plazo_medio_dias", "Plazo de entrega", "días", False),
    ("pct_puntualidad", "Puntualidad de proveedores", "%", True),
    ("dias_cobertura", "Cobertura de stock", "días", False),
    ("pct_merma", "Merma", "%", False),
    ("co2e_por_meur", "CO₂e por millón vendido", "t/M€", False),
]


def comparativa(anio: int | None = None) -> pd.DataFrame:
    """Los mismos indicadores para las cinco filiales.

    Sin esta tabla el diagnóstico no funciona: un número aislado no dice si
    está bien o mal. 34 % de kilómetros en vacío solo alarma cuando se ve al
    lado del 14 % de Bilbao.
    """
    anio = anio or datos.ultimo_anio()
    filas = []
    for filial in filiales.listar():
        g = filial.grupo
        ventas = ventas_totales(g, anio)
        millones = ventas / 1_000_000
        log = logistica(g, anio)
        flota = flota_resumen(g, anio)
        energia = energia_resumen(g, anio)
        cadena = cadena_suministro(g, anio)
        inv = inventario_resumen(g, anio)

        filas.append({
            "grupo": g,
            "filial": filial.ciudad,
            "ventas_m_eur": millones,
            "ventas_por_m2": retrato(g, anio)["ventas_por_m2"],
            "cuota_online": canal(g, anio)["cuota_online"],
            "pct_km_en_vacio": log["pct_km_en_vacio"],
            "pct_entregas_fallidas": log["pct_entregas_fallidas"],
            "litros_por_meur": flota["litros"] / millones,
            "intensidad_energetica": energia["intensidad_mwh_por_meur"],
            "margen_bruto": 1 - cadena["compras_eur"] / ventas,
            "plazo_medio_dias": cadena["plazo_medio_dias"],
            "pct_puntualidad": cadena["pct_puntualidad"],
            "dias_cobertura": inv["dias_cobertura"],
            "pct_merma": inv["pct_merma"],
            "co2e_por_meur": huella_total(g, anio) / millones,
        })
    return pd.DataFrame(filas)


def posicion(grupo: str, anio: int | None = None) -> pd.DataFrame:
    """En qué puesto queda la filial en cada indicador, de 1 a 5.

    El puesto 1 es siempre el mejor, tenga el indicador que convenga alto
    (ventas) o bajo (kilómetros en vacío). Es lo que permite al alumno pasar
    de "tenemos 34 %" a "somos los peores del grupo, y por mucho".
    """
    anio = anio or datos.ultimo_anio()
    tabla = comparativa(anio).set_index("grupo")
    filas = []
    for clave, nombre, unidad, mejor_alto in INDICADORES:
        serie = tabla[clave]
        puesto = serie.rank(ascending=not mejor_alto, method="min")
        filas.append({
            "indicador": nombre,
            "unidad": unidad,
            "valor": float(serie[grupo]),
            "puesto": int(puesto[grupo]),
            "mejor": float(serie.min() if not mejor_alto else serie.max()),
            "peor": float(serie.max() if not mejor_alto else serie.min()),
            "media": float(serie.mean()),
            "mejor_alto": mejor_alto,
        })
    return pd.DataFrame(filas)


def puntos_debiles(grupo: str, anio: int | None = None, cuantos: int = 3) -> pd.DataFrame:
    """Los indicadores en los que la filial queda peor del grupo.

    No es el diagnóstico: es la pista. El alumno tiene que explicar por qué,
    y eso los datos no se lo dan hecho.
    """
    tabla = posicion(grupo, anio)
    return (tabla.sort_values(["puesto", "indicador"], ascending=[False, True])
            .head(cuantos).reset_index(drop=True))


def calidad_de_los_datos(grupo: str, anio: int | None = None) -> dict:
    """Qué le falta a los datos de esta filial.

    Los huecos están puestos a propósito. Un alumno que calcule la media sin
    mirar esto obtendrá un consumo más bajo del real y no sabrá por qué.
    """
    anio = anio or datos.ultimo_anio()
    energia = datos.de_la_filial("energia", grupo)
    energia = energia[energia["mes"].dt.year == anio]
    rutas = datos.de_la_filial("rutas", grupo)
    rutas = rutas[rutas["fecha"].dt.year == anio]

    return {
        "lecturas_electricas_ausentes": int(energia["electricidad_kwh"].isna().sum()),
        "lecturas_electricas_totales": len(energia),
        "partes_de_ruta_sin_km": int(rutas["km_totales"].isna().sum()),
        "partes_de_ruta_totales": len(rutas),
    }
