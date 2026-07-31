"""Generador de los datos sintéticos de RetailNova Europa.

Lee `parametros.py` y produce los CSV de dos años que consumen los módulos de
clase. No contiene ninguna cifra de negocio: todas vienen de los parámetros.

Uso desde la raíz del repositorio:

    python -m datos.retailnova.generador

Los ficheros se escriben en `datos/retailnova/csv/`. La semilla es fija, así
que dos ejecuciones producen exactamente el mismo resultado: si un alumno
analiza los datos en septiembre y otro en octubre, ven lo mismo.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import parametros as p

DESTINO = Path(__file__).parent / "csv"

#: Precios unitarios, para poder expresar los consumos también en euros.
PRECIO_ELECTRICIDAD = 0.155   # €/kWh
PRECIO_GAS = 0.062            # €/kWh
PRECIO_GASOLEO = 1.42         # €/litro

CODIGO_FILIAL = {"A": "MAD", "B": "BCN", "C": "VLC", "D": "SEV", "E": "BIO"}

PREFIJO_FORMATO = {
    "gran_almacen": "GA", "hipermercado": "HI",
    "especializada": "ES", "conveniencia": "CV",
}

#: Emplazamientos por filial. Se usan por orden; si un formato necesita más
#: nombres de los disponibles, se numeran.
EMPLAZAMIENTOS = {
    "A": ["Castellana", "Preciados", "Goya", "Nuevos Ministerios", "Princesa",
          "Arturo Soria", "Méndez Álvaro", "Las Rozas", "Pozuelo", "Alcobendas",
          "Getafe", "Móstoles", "Alcalá", "Leganés", "Fuenlabrada", "Vallecas",
          "Tetuán", "Chamberí", "Carabanchel", "Barajas"],
    "B": ["Plaça Catalunya", "Diagonal", "Gràcia", "Sant Cugat", "Badalona",
          "Hospitalet", "Sabadell", "Terrassa", "Mataró", "Sitges",
          "Cornellà", "Granollers", "Manresa", "Vilanova"],
    "C": ["Colón", "Ruzafa", "Campanar", "Paterna", "Torrent",
          "Gandía", "Sagunto", "Alzira", "Xàtiva", "Burjassot",
          "Mislata", "Alboraya", "Manises", "Catarroja"],
    "D": ["Nervión", "Triana", "Los Remedios", "Dos Hermanas", "Alcalá de Guadaíra",
          "Utrera", "Écija", "Carmona", "Mairena", "Bormujos",
          "Coria", "Lebrija", "Osuna", "Marchena"],
    "E": ["Gran Vía", "Abando", "Deusto", "Getxo", "Barakaldo",
          "Portugalete", "Basauri", "Galdakao", "Durango", "Mungia"],
}


# ==========================================================================
# Utilidades
# ==========================================================================

def _rng(desplazamiento: int = 0) -> np.random.Generator:
    """Generador aleatorio con semilla fija y reproducible."""
    return np.random.default_rng(p.SEMILLA + desplazamiento)


def rango_de_fechas() -> pd.DatetimeIndex:
    """Todos los días del periodo cubierto."""
    return pd.date_range(p.FECHA_INICIO, p.FECHA_FIN, freq="D")


def rango_de_meses() -> list[date]:
    """Primer día de cada mes del periodo cubierto."""
    meses = []
    actual = date(p.FECHA_INICIO.year, p.FECHA_INICIO.month, 1)
    while actual <= p.FECHA_FIN:
        meses.append(actual)
        siguiente = actual.month + 1
        actual = (date(actual.year + 1, 1, 1) if siguiente > 12
                  else date(actual.year, siguiente, 1))
    return meses


def dias_del_mes(mes: date) -> int:
    return calendar.monthrange(mes.year, mes.month)[1]


def ventas_por_formato(tiendas: pd.DataFrame, grupo: str) -> dict[str, float]:
    """Ventas anuales reales de cada formato dentro de una filial.

    Se calcula sobre las tiendas ya generadas, no sobre el parque teórico.
    La diferencia importa: Sevilla y Bilbao tienen un único gran almacén, y
    el ruido de superficie de esa sola tienda desplazaría el mix de toda la
    filial si partiésemos del valor teórico.
    """
    del_grupo = tiendas[tiendas["grupo"] == grupo]
    agregado = del_grupo.groupby("formato")["ventas_anuales_eur"].sum()
    return {f: float(agregado.get(f, 0.0)) for f in p.FORMATOS}


def mix_ajustado(grupo: str, ventas_formato: dict[str, float] | None = None
                 ) -> dict[str, dict[str, float]]:
    """Reparto de categorías dentro de cada formato, ajustado a la filial.

    Partimos del reparto típico de cada formato (un gran almacén lo vende
    todo, una tienda especializada es casi solo moda) y lo ajustamos hasta
    que el total de la filial reproduce exactamente el mix de categorías
    validado. Es un ajuste proporcional iterativo: converge en pocas vueltas
    y respeta a la vez las dos restricciones (cada formato suma 100 %, y la
    filial reproduce su mix).
    """
    if ventas_formato is None:
        productividad = p.factor_productividad(grupo)
        ventas_formato = {
            f: n * m2 * productividad[f] for f, (n, m2) in p.PARQUE[grupo].items()
        }
    total = sum(ventas_formato.values())
    objetivo = {c: total * p.MIX_CATEGORIAS[grupo][c] for c in p.CATEGORIAS}

    mix = {f: dict(p.MIX_POR_FORMATO[f]) for f in p.FORMATOS}
    for _ in range(200):
        # Ajuste por columna: que las categorías cuadren con el objetivo.
        actual = {
            c: sum(ventas_formato[f] * mix[f][c] for f in p.FORMATOS)
            for c in p.CATEGORIAS
        }
        for c in p.CATEGORIAS:
            if actual[c] > 0:
                razon = objetivo[c] / actual[c]
                for f in p.FORMATOS:
                    mix[f][c] *= razon
        # Ajuste por fila: que cada formato vuelva a sumar 100 %.
        for f in p.FORMATOS:
            suma = sum(mix[f].values())
            for c in p.CATEGORIAS:
                mix[f][c] /= suma
    return mix


def mix_fisico(mix: dict[str, float], grupo: str) -> dict[str, float]:
    """Reparto de categorías dentro de las ventas de tienda física.

    No coincide con el mix total: la alimentación apenas se compra por
    internet, así que pesa más en la tienda física de lo que pesa en el
    conjunto. Ignorar esto escoraba el mix hacia la electrónica.
    """
    bruto = {c: mix[c] * (1 - p.PENETRACION_ONLINE[grupo][c]) for c in p.CATEGORIAS}
    total = sum(bruto.values())
    return {c: v / total for c, v in bruto.items()}


def factor_campana(fecha: date, mix: dict[str, float]) -> float:
    """Multiplicador de campaña comercial para un día y un mix de categorías.

    Una tienda de moda nota las rebajas mucho más que un hipermercado. El
    efecto se pondera por el peso de las categorías afectadas en esa tienda.
    """
    factor = 1.0
    for _, (mes_i, dia_i), (mes_f, dia_f), intensidad, categorias in p.CAMPANAS:
        inicio = date(fecha.year, mes_i, dia_i)
        fin = date(fecha.year, mes_f, dia_f)
        if inicio <= fecha <= fin:
            peso = sum(mix[c] for c in categorias)
            factor *= 1 + (intensidad - 1) * peso
    return factor


# ==========================================================================
# Maestros
# ==========================================================================

def generar_tiendas() -> pd.DataFrame:
    """Maestro de puntos de venta: uno por tienda de las cinco filiales."""
    rng = _rng(1)
    filas = []
    for g in p.GRUPOS:
        productividad = p.factor_productividad(g)
        emplazamientos = list(EMPLAZAMIENTOS[g])
        usados = 0
        for formato in p.FORMATOS:
            n, m2_medio = p.PARQUE[g][formato]
            for i in range(1, n + 1):
                # Cada tienda se desvía algo de la superficie media del formato.
                m2 = int(round(m2_medio * rng.normal(1.0, 0.10)))
                m2 = max(int(m2_medio * 0.7), m2)
                if usados < len(emplazamientos):
                    sitio = emplazamientos[usados]
                    usados += 1
                else:
                    sitio = f"{emplazamientos[usados % len(emplazamientos)]} {usados // len(emplazamientos) + 1}"
                    usados += 1
                filas.append({
                    "codigo_tienda": f"RN-{CODIGO_FILIAL[g]}-{PREFIJO_FORMATO[formato]}{i:02d}",
                    "grupo": g,
                    "formato": formato,
                    "nombre_formato": p.NOMBRE_FORMATO[formato],
                    "emplazamiento": sitio,
                    "superficie_m2": m2,
                    "anio_apertura": int(rng.integers(1978, 2023)),
                    "ventas_por_m2_eur": round(productividad[formato], 2),
                })
    tiendas = pd.DataFrame(filas)

    # Reescalamos para que la superficie total de cada filial sea exactamente
    # la validada, pese al ruido introducido tienda a tienda.
    for g in p.GRUPOS:
        mascara = tiendas["grupo"] == g
        objetivo = p.superficie_venta(g)
        actual = tiendas.loc[mascara, "superficie_m2"].sum()
        tiendas.loc[mascara, "superficie_m2"] = (
            tiendas.loc[mascara, "superficie_m2"] * objetivo / actual
        ).round().astype(int)

    tiendas["ventas_anuales_eur"] = (
        tiendas["superficie_m2"] * tiendas["ventas_por_m2_eur"]
    )

    # Al repartir el ruido de superficie entre formatos con productividades
    # distintas, el total de la filial se desvía un poco. Lo devolvemos a su
    # valor exacto: las ventas de la filial son un dato validado, no un
    # subproducto del sorteo de superficies.
    for g in p.GRUPOS:
        mascara = tiendas["grupo"] == g
        ajuste = p.ventas_anuales(g) / tiendas.loc[mascara, "ventas_anuales_eur"].sum()
        tiendas.loc[mascara, "ventas_anuales_eur"] *= ajuste

    tiendas["ventas_anuales_eur"] = tiendas["ventas_anuales_eur"].round(2)
    tiendas["ventas_por_m2_eur"] = (
        tiendas["ventas_anuales_eur"] / tiendas["superficie_m2"]
    ).round(2)
    return tiendas


def generar_centros() -> pd.DataFrame:
    """Maestro de centros logísticos."""
    filas = []
    for g in p.GRUPOS:
        n, m2 = p.CENTROS_LOGISTICOS[g]
        tiendas_servidas = p.puntos_de_venta(g)
        for i in range(1, n + 1):
            filas.append({
                "codigo_centro": f"CL-{CODIGO_FILIAL[g]}-{i:02d}",
                "grupo": g,
                "superficie_m2": m2,
                "tiendas_servidas": round(tiendas_servidas / n, 1),
                "automatizado": g == "E",
                "muelles": max(4, m2 // 900),
            })
    return pd.DataFrame(filas)


def generar_flota() -> pd.DataFrame:
    """Maestro de vehículos, con antigüedad y norma de emisiones."""
    rng = _rng(2)
    filas = []
    for g in p.GRUPOS:
        furgonetas, rigidos = p.FLOTA[g]
        antiguedad_media = p.ANTIGUEDAD_FLOTA[g]
        for tipo, n, prefijo in (("furgoneta", furgonetas, "F"), ("rigido", rigidos, "R")):
            for i in range(1, n + 1):
                antiguedad = max(0.5, rng.normal(antiguedad_media, 2.0))
                anio = 2025 - int(round(antiguedad))
                if anio >= 2021:
                    norma = "Euro 6d"
                elif anio >= 2016:
                    norma = "Euro 6"
                elif anio >= 2011:
                    norma = "Euro 5"
                else:
                    norma = "Euro 4"
                filas.append({
                    "matricula": f"RN-{CODIGO_FILIAL[g]}-{prefijo}{i:03d}",
                    "grupo": g,
                    "tipo": tipo,
                    "anio_matriculacion": anio,
                    "antiguedad_anios": round(2025 - anio, 1),
                    "norma_emisiones": norma,
                    "km_anuales_previstos": p.KM_ANUALES[g][tipo],
                    "consumo_l_100km": p.CONSUMO_L_100KM[g][tipo],
                    "frigorifico": g == "C" and tipo == "rigido",
                })
    return pd.DataFrame(filas)


def generar_proveedores() -> pd.DataFrame:
    """Maestro de proveedores, con plazo de entrega y fiabilidad."""
    rng = _rng(3)
    filas = []
    origenes = list(p.ORIGENES_PROVEEDOR)
    for i in range(1, p.NUM_PROVEEDORES + 1):
        # El origen se sortea con el peso medio de las cinco filiales.
        pesos = np.array([
            np.mean([p.MIX_ORIGEN[g][o] for g in p.GRUPOS]) for o in origenes
        ])
        origen = origenes[int(rng.choice(len(origenes), p=pesos / pesos.sum()))]
        base = p.ORIGENES_PROVEEDOR[origen]
        categoria = str(rng.choice(p.CATEGORIAS, p=[0.42, 0.34, 0.24]))
        filas.append({
            "codigo_proveedor": f"PRV-{i:03d}",
            "pais_origen": origen,
            "categoria": categoria,
            "nombre_categoria": p.NOMBRE_CATEGORIA[categoria],
            "plazo_entrega_dias": max(2, int(round(rng.normal(base["plazo"], base["plazo"] * 0.20)))),
            "fiabilidad_entrega": round(float(np.clip(rng.normal(base["fiabilidad"], 0.05), 0.5, 0.995)), 3),
            "pedido_minimo_eur": int(rng.choice([500, 1_000, 2_500, 5_000, 10_000])),
        })
    return pd.DataFrame(filas)


# ==========================================================================
# Ventas
# ==========================================================================

def generar_ventas_diarias(tiendas: pd.DataFrame) -> pd.DataFrame:
    """Ventas físicas por tienda y día, con estacionalidad y campañas.

    Las ventas online no están aquí: se registran aparte, en
    `pedidos_online.csv`, porque no se atribuyen a una tienda concreta.
    """
    rng = _rng(4)
    fechas = rango_de_fechas()
    dias = np.array([f.date() for f in fechas])
    dow = np.array([f.weekday() for f in fechas])
    meses = np.array([f.month for f in fechas])
    anios = np.array([f.year for f in fechas])

    mixes = {g: mix_ajustado(g, ventas_por_formato(tiendas, g)) for g in p.GRUPOS}
    bloques = []

    for _, tienda in tiendas.iterrows():
        g = tienda["grupo"]
        formato = tienda["formato"]
        mix = mixes[g][formato]

        # Parte de las ventas que va por tienda física.
        online = sum(mix[c] * p.PENETRACION_ONLINE[g][c] for c in p.CATEGORIAS)
        mix = mix_fisico(mix, g)  # la estacionalidad la marca lo que se vende en tienda
        ventas_fisicas_2025 = tienda["ventas_anuales_eur"] * (1 - online)
        ventas_fisicas_2024 = ventas_fisicas_2025 / (1 + p.CRECIMIENTO_ANUAL[g])

        peso = np.array([p.FACTOR_SEMANAL[d] for d in dow], dtype=float)
        if formato == "gran_almacen":
            # Los grandes almacenes abren en domingos autorizados.
            domingos = dow == 6
            peso[domingos] = p.FACTOR_DOMINGO_GRAN_ALMACEN
        peso *= np.array([p.FACTOR_MENSUAL[m] for m in meses])
        verano = np.isin(meses, [7, 8])
        peso[verano] *= p.FACTOR_VERANO[g]
        peso *= np.array([factor_campana(d, mix) for d in dias])
        peso *= rng.normal(1.0, p.RUIDO_DIARIO, size=len(fechas)).clip(0.55, 1.6)

        # Días atípicos: incidencias que hunden las ventas de una jornada.
        atipicos = rng.choice(len(fechas), size=p.NUM_DIAS_ATIPICOS, replace=False)
        peso[atipicos] *= rng.uniform(0.30, 0.65, size=p.NUM_DIAS_ATIPICOS)

        # Normalizamos por año para que el total anual cuadre exactamente.
        ventas = np.zeros(len(fechas))
        for anio, objetivo in ((2024, ventas_fisicas_2024), (2025, ventas_fisicas_2025)):
            sel = anios == anio
            ventas[sel] = peso[sel] / peso[sel].sum() * objetivo

        tickets = np.maximum(
            1,
            np.round(ventas / (p.TICKET_MEDIO[formato] * rng.normal(1.0, 0.05, len(fechas)))),
        ).astype(int)

        bloques.append(pd.DataFrame({
            "fecha": fechas,
            "codigo_tienda": tienda["codigo_tienda"],
            "grupo": g,
            "formato": formato,
            "ventas_eur": ventas.round(2),
            "tickets": tickets,
        }))

    ventas = pd.concat(bloques, ignore_index=True)
    ventas["ticket_medio_eur"] = (ventas["ventas_eur"] / ventas["tickets"]).round(2)
    return ventas.sort_values(["fecha", "codigo_tienda"], ignore_index=True)


def generar_ventas_categoria(ventas_diarias: pd.DataFrame,
                             tiendas: pd.DataFrame) -> pd.DataFrame:
    """Reparto mensual de las ventas físicas por categoría de producto."""
    mixes = {g: mix_ajustado(g, ventas_por_formato(tiendas, g)) for g in p.GRUPOS}
    formato_de = dict(zip(tiendas["codigo_tienda"], tiendas["formato"]))

    mensual = ventas_diarias.copy()
    mensual["mes"] = mensual["fecha"].dt.to_period("M").dt.to_timestamp()
    agregado = (mensual.groupby(["mes", "codigo_tienda", "grupo"], as_index=False)
                ["ventas_eur"].sum())

    filas = []
    for _, fila in agregado.iterrows():
        formato = formato_de[fila["codigo_tienda"]]
        mix = mix_fisico(mixes[fila["grupo"]][formato], fila["grupo"])
        for categoria in p.CATEGORIAS:
            filas.append({
                "mes": fila["mes"],
                "codigo_tienda": fila["codigo_tienda"],
                "grupo": fila["grupo"],
                "categoria": categoria,
                "nombre_categoria": p.NOMBRE_CATEGORIA[categoria],
                "ventas_eur": round(fila["ventas_eur"] * mix[categoria], 2),
            })
    return pd.DataFrame(filas)


def generar_pedidos_online(tiendas: pd.DataFrame) -> pd.DataFrame:
    """Ventas del canal online, por filial y día.

    Se registran a nivel de filial porque el pedido no pertenece a ninguna
    tienda: se prepara en el centro logístico y se entrega a domicilio o se
    recoge en tienda.
    """
    rng = _rng(5)
    fechas = rango_de_fechas()
    dow = np.array([f.weekday() for f in fechas])
    meses = np.array([f.month for f in fechas])
    anios = np.array([f.year for f in fechas])
    dias = np.array([f.date() for f in fechas])

    mixes = {g: mix_ajustado(g, ventas_por_formato(tiendas, g)) for g in p.GRUPOS}
    bloques = []

    for g in p.GRUPOS:
        del_grupo = tiendas[tiendas["grupo"] == g]
        online_por_categoria = {c: 0.0 for c in p.CATEGORIAS}
        for _, tienda in del_grupo.iterrows():
            mix = mixes[g][tienda["formato"]]
            for c in p.CATEGORIAS:
                online_por_categoria[c] += (
                    tienda["ventas_anuales_eur"] * mix[c] * p.PENETRACION_ONLINE[g][c]
                )

        mix_online = {
            c: v / sum(online_por_categoria.values()) for c, v in online_por_categoria.items()
        }
        total_2025 = sum(online_por_categoria.values())
        total_2024 = total_2025 / (1 + p.CRECIMIENTO_ANUAL[g] + 0.06)  # el canal crece más

        # El online es menos sensible al día de la semana y más a las campañas.
        peso = np.array([1.0 + 0.12 * (d < 4) for d in dow])
        peso *= np.array([p.FACTOR_MENSUAL[m] for m in meses])
        peso *= np.array([factor_campana(d, mix_online) for d in dias])
        peso *= rng.normal(1.0, 0.11, size=len(fechas)).clip(0.6, 1.8)

        ventas = np.zeros(len(fechas))
        for anio, objetivo in ((2024, total_2024), (2025, total_2025)):
            sel = anios == anio
            ventas[sel] = peso[sel] / peso[sel].sum() * objetivo

        ticket = 62.0
        pedidos = np.maximum(1, np.round(ventas / (ticket * rng.normal(1.0, 0.06, len(fechas))))).astype(int)

        bloque = pd.DataFrame({
            "fecha": fechas,
            "grupo": g,
            "pedidos": pedidos,
            "ventas_eur": ventas.round(2),
        })
        for c in p.CATEGORIAS:
            bloque[f"ventas_{c}_eur"] = (ventas * mix_online[c]).round(2)
        bloque["ticket_medio_eur"] = (bloque["ventas_eur"] / bloque["pedidos"]).round(2)
        # La recogida en tienda evita el trayecto de última milla: es una de
        # las palancas de reducción de la Sesión 2.
        bloque["pct_recogida_en_tienda"] = np.round(
            rng.normal(0.28 if g != "E" else 0.41, 0.03, len(fechas)).clip(0.10, 0.60), 3
        )
        bloques.append(bloque)

    return pd.concat(bloques, ignore_index=True).sort_values(
        ["fecha", "grupo"], ignore_index=True
    )


# ==========================================================================
# Logística
# ==========================================================================

def generar_rutas(centros: pd.DataFrame) -> pd.DataFrame:
    """Rutas diarias de reparto por centro logístico."""
    rng = _rng(6)
    fechas = rango_de_fechas()
    dow = np.array([f.weekday() for f in fechas])
    meses = np.array([f.month for f in fechas])
    bloques = []

    for _, centro in centros.iterrows():
        g = centro["grupo"]
        n_centros = p.CENTROS_LOGISTICOS[g][0]
        km_anuales_filial = sum(
            n * p.KM_ANUALES[g][tipo]
            for tipo, n in zip(p.TIPOS_VEHICULO, p.FLOTA[g])
        )
        km_dia_centro = km_anuales_filial / n_centros / 365

        peso = np.array([1.15 if d < 5 else (0.85 if d == 5 else 0.35) for d in dow])
        peso *= np.array([p.FACTOR_MENSUAL[m] for m in meses])
        peso *= rng.normal(1.0, 0.09, len(fechas)).clip(0.6, 1.5)
        peso = peso / peso.mean()

        km = km_dia_centro * peso
        vacio = km * np.clip(rng.normal(p.KM_EN_VACIO[g], 0.03, len(fechas)), 0.02, 0.6)
        rutas = np.maximum(1, np.round(km / (km_dia_centro / 8 + 1e-9) / 8 * 9)).astype(int)
        paradas = np.maximum(
            1, np.round(rutas * rng.normal(p.PARADAS_POR_RUTA[g], 1.5, len(fechas)))
        ).astype(int)

        bloque = pd.DataFrame({
            "fecha": fechas,
            "codigo_centro": centro["codigo_centro"],
            "grupo": g,
            "num_rutas": rutas,
            "km_totales": km.round(1),
            "km_en_vacio": vacio.round(1),
            "paradas": paradas,
            "ocupacion_media": np.round(
                np.clip(rng.normal(p.OCUPACION_MEDIA[g], 0.06, len(fechas)), 0.25, 0.99), 3
            ),
        })
        bloque["pct_km_en_vacio"] = (bloque["km_en_vacio"] / bloque["km_totales"]).round(3)
        bloque["entregas_fallidas"] = rng.binomial(
            bloque["paradas"].values, p.TASA_ENTREGA_FALLIDA[g]
        )
        bloques.append(bloque)

    rutas = pd.concat(bloques, ignore_index=True)

    # Imperfección deliberada: algunos partes de ruta llegan sin kilometraje.
    sin_km = rng.random(len(rutas)) < p.PCT_RUTAS_SIN_KM
    rutas.loc[sin_km, ["km_totales", "km_en_vacio", "pct_km_en_vacio"]] = np.nan

    return rutas.sort_values(["fecha", "codigo_centro"], ignore_index=True)


def generar_consumo_flota(flota: pd.DataFrame) -> pd.DataFrame:
    """Combustible y kilómetros por vehículo y mes."""
    rng = _rng(7)
    meses = rango_de_meses()
    filas = []

    for _, vehiculo in flota.iterrows():
        g = vehiculo["grupo"]
        km_mes_base = vehiculo["km_anuales_previstos"] / 12
        # Un vehículo viejo consume más que el valor nominal de su ficha.
        penalizacion = 1 + 0.011 * max(0.0, vehiculo["antiguedad_anios"] - 4)
        for mes in meses:
            estacional = p.FACTOR_MENSUAL[mes.month] * 0.55 + 0.45
            km = km_mes_base * estacional * rng.normal(1.0, 0.07)
            km = max(0.0, km)
            litros = km * vehiculo["consumo_l_100km"] / 100 * penalizacion
            filas.append({
                "mes": pd.Timestamp(mes),
                "matricula": vehiculo["matricula"],
                "grupo": g,
                "tipo": vehiculo["tipo"],
                "km": round(km, 1),
                "km_en_vacio": round(km * p.KM_EN_VACIO[g], 1),
                "litros": round(litros, 1),
                "coste_eur": round(litros * PRECIO_GASOLEO, 2),
                "co2e_kg": round(litros * p.FACTOR_GASOLEO, 1),
            })
    return pd.DataFrame(filas)


# ==========================================================================
# Energía, residuos y refrigerantes
# ==========================================================================

def _instalaciones(tiendas: pd.DataFrame, centros: pd.DataFrame) -> pd.DataFrame:
    """Tiendas y centros logísticos en una sola tabla."""
    a = tiendas[["codigo_tienda", "grupo", "formato", "superficie_m2"]].rename(
        columns={"codigo_tienda": "codigo_instalacion"}
    )
    b = centros[["codigo_centro", "grupo", "superficie_m2"]].rename(
        columns={"codigo_centro": "codigo_instalacion"}
    )
    b["formato"] = "centro_logistico"
    return pd.concat([a, b[a.columns]], ignore_index=True)


def generar_energia(tiendas: pd.DataFrame, centros: pd.DataFrame) -> pd.DataFrame:
    """Electricidad y gas natural por instalación y mes."""
    rng = _rng(8)
    meses = rango_de_meses()
    instalaciones = _instalaciones(tiendas, centros)
    filas = []

    for _, inst in instalaciones.iterrows():
        g = inst["grupo"]
        formato = inst["formato"]
        electricidad_anual = inst["superficie_m2"] * p.INTENSIDAD_ELECTRICA[g][formato]
        gas_anual = inst["superficie_m2"] * p.INTENSIDAD_GAS[formato]

        pesos_e = np.array([p.FACTOR_ELECTRICO_MENSUAL[m.month] for m in meses])
        pesos_g = np.array([p.FACTOR_GAS_MENSUAL[m.month] for m in meses])
        ruido_e = rng.normal(1.0, 0.045, len(meses)).clip(0.8, 1.25)
        ruido_g = rng.normal(1.0, 0.07, len(meses)).clip(0.7, 1.4)

        for i, mes in enumerate(meses):
            # Los pesos mensuales tienen media 1, así que dividir entre 12
            # reparte el consumo anual sin desviarlo.
            elec = electricidad_anual / 12 * pesos_e[i] * ruido_e[i]
            gas = gas_anual / 12 * pesos_g[i] * ruido_g[i]
            filas.append({
                "mes": pd.Timestamp(mes),
                "codigo_instalacion": inst["codigo_instalacion"],
                "grupo": g,
                "tipo_instalacion": formato,
                "superficie_m2": inst["superficie_m2"],
                "electricidad_kwh": round(elec, 1),
                "gas_kwh": round(gas, 1),
                "coste_eur": round(elec * PRECIO_ELECTRICIDAD + gas * PRECIO_GAS, 2),
                "co2e_kg": round(elec * p.FACTOR_ELECTRICIDAD + gas * p.FACTOR_GAS_NATURAL, 1),
            })

    energia = pd.DataFrame(filas)

    # Imperfección deliberada: contadores que no se leyeron ese mes.
    ausentes = rng.random(len(energia)) < p.PCT_LECTURAS_AUSENTES
    energia.loc[ausentes, ["electricidad_kwh", "coste_eur", "co2e_kg"]] = np.nan

    return energia


def generar_residuos(tiendas: pd.DataFrame, centros: pd.DataFrame,
                     ventas_categoria: pd.DataFrame) -> pd.DataFrame:
    """Residuos generados por instalación y mes, por tipo."""
    rng = _rng(9)
    ventas = ventas_categoria.copy()

    filas = []
    for (mes, codigo, grupo), bloque in ventas.groupby(
        ["mes", "codigo_tienda", "grupo"], sort=False
    ):
        fila = {
            "mes": mes, "codigo_instalacion": codigo,
            "grupo": grupo, "tipo_instalacion": "tienda",
        }
        for tipo in p.TIPOS_RESIDUO:
            kg = sum(
                r["ventas_eur"] / 1_000 * p.RESIDUO_POR_KEUR[r["categoria"]][tipo]
                for _, r in bloque.iterrows()
            )
            fila[f"{tipo}_kg"] = round(kg * rng.normal(1.0, 0.06), 1)
        fila["total_kg"] = round(sum(fila[f"{t}_kg"] for t in p.TIPOS_RESIDUO), 1)
        fila["pct_reciclado"] = round(
            float(np.clip(rng.normal(p.TASA_RECICLAJE[grupo], 0.04), 0.2, 0.98)), 3
        )
        filas.append(fila)

    # Los centros logísticos generan sobre todo cartón y plástico de embalaje.
    for _, centro in centros.iterrows():
        g = centro["grupo"]
        base = centro["superficie_m2"] * 0.75  # kg al mes por m²
        for mes in rango_de_meses():
            fila = {
                "mes": pd.Timestamp(mes), "codigo_instalacion": centro["codigo_centro"],
                "grupo": g, "tipo_instalacion": "centro_logistico",
            }
            reparto = {"carton": 0.58, "plastico": 0.27, "organico": 0.01,
                       "raee": 0.03, "textil": 0.02, "resto": 0.09}
            estacional = p.FACTOR_MENSUAL[mes.month]
            for tipo in p.TIPOS_RESIDUO:
                fila[f"{tipo}_kg"] = round(
                    base * reparto[tipo] * estacional * rng.normal(1.0, 0.07), 1
                )
            fila["total_kg"] = round(sum(fila[f"{t}_kg"] for t in p.TIPOS_RESIDUO), 1)
            fila["pct_reciclado"] = round(
                float(np.clip(rng.normal(p.TASA_RECICLAJE[g] + 0.09, 0.03), 0.2, 0.99)), 3
            )
            filas.append(fila)

    return pd.DataFrame(filas).sort_values(
        ["mes", "codigo_instalacion"], ignore_index=True
    )


def generar_refrigerantes(tiendas: pd.DataFrame) -> pd.DataFrame:
    """Carga y fuga de gas refrigerante por tienda y año."""
    rng = _rng(10)
    filas = []
    for _, tienda in tiendas.iterrows():
        g = tienda["grupo"]
        gas = p.GAS_REFRIGERANTE[g]
        carga = p.CARGA_REFRIGERANTE[tienda["formato"]]
        for anio in (2024, 2025):
            tasa = float(np.clip(rng.normal(p.FUGA_REFRIGERANTE[g], 0.02), 0.02, 0.35))
            fuga = carga * tasa
            filas.append({
                "anio": anio,
                "codigo_tienda": tienda["codigo_tienda"],
                "grupo": g,
                "formato": tienda["formato"],
                "gas": gas,
                "carga_kg": carga,
                "fuga_kg": round(fuga, 2),
                "tasa_fuga": round(tasa, 3),
                "gwp": p.GWP[gas],
                "co2e_kg": round(fuga * p.GWP[gas], 1),
            })
    return pd.DataFrame(filas)


# ==========================================================================
# Inventario
# ==========================================================================

def generar_inventario(ventas_categoria: pd.DataFrame) -> pd.DataFrame:
    """Stock medio, rotación y merma por tienda, categoría y mes."""
    rng = _rng(11)
    inventario = ventas_categoria.copy()

    rotacion = inventario["categoria"].map(p.ROTACION_ANUAL)
    merma_base = inventario["categoria"].map(p.MERMA_BASE)
    factor_merma = inventario["grupo"].map(p.FACTOR_MERMA)

    ruido_rot = rng.normal(1.0, 0.10, len(inventario)).clip(0.6, 1.5)
    ruido_merma = rng.normal(1.0, 0.18, len(inventario)).clip(0.4, 2.0)

    rotacion_real = rotacion * ruido_rot * inventario["grupo"].map(p.FACTOR_ROTACION)
    # Stock medio = coste de las ventas del periodo dividido por la rotación.
    inventario["stock_medio_eur"] = (
        inventario["ventas_eur"] * 12 * 0.62 / rotacion_real
    ).round(2)
    inventario["rotacion_anualizada"] = rotacion_real.round(2)
    inventario["merma_pct"] = (merma_base * factor_merma * ruido_merma).round(4)
    inventario["merma_eur"] = (
        inventario["ventas_eur"] * inventario["merma_pct"]
    ).round(2)
    inventario["dias_cobertura"] = (365 / rotacion_real).round(1)

    return inventario[[
        "mes", "codigo_tienda", "grupo", "categoria", "nombre_categoria",
        "stock_medio_eur", "rotacion_anualizada", "dias_cobertura",
        "merma_pct", "merma_eur",
    ]]


def generar_compras(proveedores: pd.DataFrame) -> pd.DataFrame:
    """Compras a proveedores por filial, proveedor y mes.

    Sin esta tabla el problema de Barcelona sería invisible: su dependencia
    asiática solo se ve si se puede cruzar cada compra con el país de origen
    y el plazo de entrega real, no el prometido.
    """
    rng = _rng(12)
    meses = rango_de_meses()
    filas = []

    for g in p.GRUPOS:
        # Cartera de proveedores de la filial, respetando su mix de origen.
        cartera = []
        for origen, peso in p.MIX_ORIGEN[g].items():
            candidatos = proveedores.index[proveedores["pais_origen"] == origen].to_numpy()
            if len(candidatos) == 0:
                continue
            cuantos = min(len(candidatos), max(1, round(peso * 26)))
            cartera.extend(rng.choice(candidatos, size=cuantos, replace=False).tolist())

        # Las compras son el coste de la mercancía. El porcentaje depende de
        # dónde compra la filial: comprar en Asia sale más barato.
        compras_2025 = p.ventas_anuales(g) * p.coste_mercancia(g)
        reparto = rng.random(len(cartera)) + 0.35
        reparto = reparto / reparto.sum()

        for indice, peso_proveedor in zip(cartera, reparto):
            proveedor = proveedores.loc[indice]
            base = p.ORIGENES_PROVEEDOR[proveedor["pais_origen"]]
            for mes in meses:
                # Se compra por delante de lo que se vende: el pico de compra
                # se adelanta dos meses al de venta.
                mes_venta = (mes.month + 1) % 12 + 1
                estacional = p.FACTOR_MENSUAL[mes_venta]
                anual = compras_2025 if mes.year == 2025 else compras_2025 / (1 + p.CRECIMIENTO_ANUAL[g])
                importe = anual * peso_proveedor / 12 * estacional * rng.normal(1.0, 0.14)
                entregas = max(1, int(round(30 / max(4, proveedor["plazo_entrega_dias"]) * rng.normal(1.0, 0.2))))
                plazo_real = float(np.clip(
                    rng.normal(proveedor["plazo_entrega_dias"], base["plazo"] * 0.28),
                    2, base["plazo"] * 2.5,
                ))
                filas.append({
                    "mes": pd.Timestamp(mes),
                    "grupo": g,
                    "codigo_proveedor": proveedor["codigo_proveedor"],
                    "pais_origen": proveedor["pais_origen"],
                    "categoria": proveedor["categoria"],
                    "importe_eur": round(max(0.0, importe), 2),
                    "entregas": entregas,
                    "entregas_a_tiempo": int(rng.binomial(entregas, proveedor["fiabilidad_entrega"])),
                    "plazo_real_dias": round(plazo_real, 1),
                })

    return pd.DataFrame(filas).sort_values(
        ["mes", "grupo", "codigo_proveedor"], ignore_index=True
    )


def generar_devoluciones(pedidos_online: pd.DataFrame) -> pd.DataFrame:
    """Devoluciones del canal online, mes a mes y por categoría.

    Se derivan de los pedidos que ya existen, no se inventan por separado:
    así es imposible que una filial devuelva más de lo que vendió. Lo que no
    es revendible se convierte en residuo, y ese residuo ya está contado
    dentro de `residuos.csv`.

    Semilla propia (20): añadir esta tabla no mueve ninguna de las anteriores.
    """
    rng = _rng(20)
    filas = []

    for g in p.GRUPOS:
        propios = pedidos_online[pedidos_online["grupo"] == g].copy()
        propios["mes"] = propios["fecha"].dt.to_period("M").dt.to_timestamp()
        mensual = propios.groupby("mes").agg(
            pedidos=("pedidos", "sum"),
            **{f"ventas_{c}_eur": (f"ventas_{c}_eur", "sum") for c in p.CATEGORIAS},
        )

        for mes, fila in mensual.iterrows():
            ventas_mes = sum(float(fila[f"ventas_{c}_eur"]) for c in p.CATEGORIAS)
            if ventas_mes <= 0:
                continue
            for categoria in p.CATEGORIAS:
                ventas_cat = float(fila[f"ventas_{categoria}_eur"])
                if ventas_cat <= 0:
                    continue
                # Los pedidos de la categoría, repartidos según lo que pesa
                # en la venta del mes.
                pedidos_cat = float(fila["pedidos"]) * ventas_cat / ventas_mes
                tasa = float(np.clip(
                    rng.normal(p.TASA_DEVOLUCION[categoria], 0.02), 0.005, 0.55
                ))
                devueltos = pedidos_cat * tasa
                revendible = float(np.clip(
                    rng.normal(p.PCT_REVENDIBLE[categoria], 0.04), 0.0, 0.95
                ))
                kg = devueltos * p.KG_POR_DEVOLUCION[categoria]

                filas.append({
                    "mes": mes.date(),
                    "grupo": g,
                    "categoria": categoria,
                    "pedidos_devueltos": int(round(devueltos)),
                    "tasa_devolucion": round(tasa, 4),
                    "valor_eur": round(ventas_cat * tasa, 2),
                    "peso_kg": round(kg, 1),
                    "pct_revendible": round(revendible, 3),
                    "peso_no_revendible_kg": round(kg * (1 - revendible), 1),
                    "coste_gestion_eur": round(
                        devueltos * p.COSTE_GESTION_DEVOLUCION_EUR, 2
                    ),
                })

    return pd.DataFrame(filas).sort_values(
        ["mes", "grupo", "categoria"], ignore_index=True
    )


def generar_envases(residuos: pd.DataFrame, compras: pd.DataFrame) -> pd.DataFrame:
    """Envases y embalajes puestos en circulación, por tipo.

    Se calibra contra el cartón y el plástico que ya recoge `residuos.csv`,
    de modo que las dos tablas cuentan lo mismo desde dos ángulos: una, lo
    que se tira; otra, lo que se compró para embalar y de dónde venía.

    El sobreembalaje de origen es lo que hace que Barcelona, que compra la
    mitad en Asia, arrastre más envase por euro vendido que nadie.

    Semilla propia (21).
    """
    rng = _rng(21)
    filas = []

    for g in p.GRUPOS:
        residuo_g = residuos[residuos["grupo"] == g].copy()
        mensual = residuo_g.groupby("mes")[["carton_kg", "plastico_kg"]].sum()

        compras_g = compras[compras["grupo"] == g]
        importe = float(compras_g["importe_eur"].sum())
        if importe > 0:
            sobre = float(sum(
                compras_g[compras_g["pais_origen"] == origen]["importe_eur"].sum()
                / importe * factor
                for origen, factor in p.SOBREEMBALAJE_ORIGEN.items()
            ))
        else:
            sobre = 1.0

        for mes, fila in mensual.iterrows():
            # El envase puesto en circulación es algo más que el residuo
            # recogido: parte se queda en casa del cliente.
            base_kg = (float(fila["carton_kg"]) + float(fila["plastico_kg"])) * 1.18
            for tipo, peso in p.MIX_ENVASE.items():
                # El sobreembalaje solo afecta a lo que entra, no a lo que
                # se prepara aquí para el cliente.
                factor = sobre if tipo in ("carton_entrada", "film_plastico",
                                           "palet_madera") else 1.0
                kg = base_kg * peso * factor * float(
                    np.clip(rng.normal(1.0, 0.05), 0.8, 1.2)
                )
                filas.append({
                    "mes": mes,
                    "grupo": g,
                    "tipo": tipo,
                    "kg": round(kg, 1),
                    "retornable": False,
                    "coste_eur": round(kg / 1_000 * p.COSTE_ENVASE_EUR_T[tipo], 2),
                })

    return pd.DataFrame(filas).sort_values(
        ["mes", "grupo", "tipo"], ignore_index=True
    )


def generar_plantilla() -> pd.DataFrame:
    """Datos de plantilla, mes a mes y por filial.

    Existe para que la memoria de sostenibilidad de la Sesión 4 pueda tener
    dimensión social y no solo ambiental. Las cifras se mueven poco a lo
    largo del año, salvo la temporalidad, que sube en campaña de Navidad:
    es el pico que hace visible el indicador.

    Semilla propia (22).
    """
    rng = _rng(22)
    filas = []

    for g in p.GRUPOS:
        base = p.PLANTILLA[g]
        for mes in rango_de_meses():
            # Refuerzo de campaña en noviembre y diciembre.
            refuerzo = 1.14 if mes.month in (11, 12) else 1.0
            empleados = int(round(base * refuerzo * rng.normal(1.0, 0.015)))
            temporal = float(np.clip(
                rng.normal(p.TEMPORALIDAD[g] * refuerzo, 0.015), 0.05, 0.65
            ))
            filas.append({
                "mes": mes,
                "grupo": g,
                "empleados": empleados,
                "pct_temporales": round(temporal, 4),
                "pct_rotacion": round(float(np.clip(
                    rng.normal(p.ROTACION[g] / 12, 0.004), 0.0, 0.2
                )), 4),
                "accidentes_con_baja": int(max(0, round(
                    p.INDICE_ACCIDENTES[g] * empleados * 150 / 1_000_000
                    * rng.normal(1.0, 0.35)
                ))),
                "horas_formacion": round(
                    p.HORAS_FORMACION[g] / 12 * empleados
                    * float(rng.normal(1.0, 0.12)), 1
                ),
                "pct_mujeres_direccion": round(float(np.clip(
                    rng.normal(p.MUJERES_DIRECCION[g], 0.02), 0.05, 0.8
                )), 4),
                "brecha_salarial": round(float(np.clip(
                    rng.normal(p.BRECHA_SALARIAL[g], 0.008), 0.0, 0.4
                )), 4),
            })

    return pd.DataFrame(filas).sort_values(["mes", "grupo"], ignore_index=True)


def generar_factores_emision() -> pd.DataFrame:
    """Tabla de referencia de factores de emisión."""
    return pd.DataFrame(
        p.FACTORES_EMISION,
        columns=["concepto", "unidad", "factor", "alcance"],
    )


# ==========================================================================
# Orquestación
# ==========================================================================

def generar_todo(destino: Path = DESTINO) -> dict[str, pd.DataFrame]:
    """Genera todas las tablas y las escribe como CSV."""
    destino.mkdir(parents=True, exist_ok=True)

    tiendas = generar_tiendas()
    centros = generar_centros()
    flota = generar_flota()
    proveedores = generar_proveedores()
    ventas_diarias = generar_ventas_diarias(tiendas)
    ventas_categoria = generar_ventas_categoria(ventas_diarias, tiendas)
    pedidos_online = generar_pedidos_online(tiendas)
    rutas = generar_rutas(centros)
    consumo_flota = generar_consumo_flota(flota)
    energia = generar_energia(tiendas, centros)
    inventario = generar_inventario(ventas_categoria)
    residuos = generar_residuos(tiendas, centros, ventas_categoria)
    refrigerantes = generar_refrigerantes(tiendas)
    compras = generar_compras(proveedores)
    devoluciones = generar_devoluciones(pedidos_online)
    envases = generar_envases(residuos, compras)
    plantilla = generar_plantilla()
    factores = generar_factores_emision()

    tablas = {
        "tiendas": tiendas,
        "centros": centros,
        "flota": flota,
        "proveedores": proveedores,
        "compras": compras,
        "ventas_diarias": ventas_diarias,
        "ventas_categoria": ventas_categoria,
        "pedidos_online": pedidos_online,
        "rutas": rutas,
        "consumo_flota": consumo_flota,
        "energia": energia,
        "inventario": inventario,
        "residuos": residuos,
        "refrigerantes": refrigerantes,
        "devoluciones": devoluciones,
        "envases": envases,
        "plantilla": plantilla,
        "factores_emision": factores,
    }

    for nombre, tabla in tablas.items():
        tabla.to_csv(destino / f"{nombre}.csv", index=False, encoding="utf-8")

    return tablas


def main() -> None:
    tablas = generar_todo()
    print(f"Datos generados en {DESTINO}\n")
    total_mb = 0.0
    for nombre, tabla in tablas.items():
        mb = (DESTINO / f"{nombre}.csv").stat().st_size / 1024 / 1024
        total_mb += mb
        print(f"  {nombre:<20} {len(tabla):>8,} filas   {mb:>6.2f} MB")
    print(f"\n  {'TOTAL':<20} {'':>8}         {total_mb:>6.2f} MB")


if __name__ == "__main__":
    main()
