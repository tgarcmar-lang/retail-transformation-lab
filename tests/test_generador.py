"""Verificación de coherencia de los datos de RetailNova.

Estas pruebas son la red de seguridad del caso. Si alguien cambia un parámetro
y los datos dejan de cuadrar, salta aquí y no en clase el 8 de septiembre.

Ejecutar desde la raíz del repositorio:

    python -m pytest tests/ -q
"""

import numpy as np
import pandas as pd
import pytest

from core import filiales
from datos.retailnova import generador as gen
from datos.retailnova import parametros as p

TOLERANCIA = 0.005  # 0,5 %


@pytest.fixture(scope="module")
def tablas():
    """Genera los datos una sola vez para todas las pruebas."""
    tiendas = gen.generar_tiendas()
    centros = gen.generar_centros()
    flota = gen.generar_flota()
    ventas_diarias = gen.generar_ventas_diarias(tiendas)
    ventas_categoria = gen.generar_ventas_categoria(ventas_diarias, tiendas)
    return {
        "tiendas": tiendas,
        "centros": centros,
        "flota": flota,
        "proveedores": gen.generar_proveedores(),
        "ventas_diarias": ventas_diarias,
        "ventas_categoria": ventas_categoria,
        "pedidos_online": gen.generar_pedidos_online(tiendas),
        "rutas": gen.generar_rutas(centros),
        "consumo_flota": gen.generar_consumo_flota(flota),
        "energia": gen.generar_energia(tiendas, centros),
        "inventario": gen.generar_inventario(ventas_categoria),
        "residuos": gen.generar_residuos(tiendas, centros, ventas_categoria),
        "refrigerantes": gen.generar_refrigerantes(tiendas),
    }


# --------------------------------------------------------------------------
# Los parámetros no se contradicen entre sí
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_el_mix_de_categorias_suma_cien(grupo):
    assert sum(p.MIX_CATEGORIAS[grupo].values()) == pytest.approx(1.0)


@pytest.mark.parametrize("formato", p.FORMATOS)
def test_el_mix_por_formato_suma_cien(formato):
    assert sum(p.MIX_POR_FORMATO[formato].values()) == pytest.approx(1.0)


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_el_mix_de_origenes_suma_cien(grupo):
    assert sum(p.MIX_ORIGEN[grupo].values()) == pytest.approx(1.0)


def test_los_factores_semanales_tienen_media_uno():
    assert np.mean(p.FACTOR_SEMANAL) == pytest.approx(1.0, abs=1e-9)


def test_los_factores_mensuales_tienen_media_uno():
    assert np.mean(list(p.FACTOR_MENSUAL.values())) == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_la_flota_coincide_con_la_ficha_de_la_filial(grupo):
    """El total de vehículos debe ser el mismo que ve el alumno en la ficha."""
    assert sum(p.FLOTA[grupo]) == filiales.obtener(grupo).vehiculos


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_los_centros_coinciden_con_la_ficha_de_la_filial(grupo):
    assert p.CENTROS_LOGISTICOS[grupo][0] == filiales.obtener(grupo).centros_logisticos


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_la_cuota_online_coincide_con_la_ficha_de_la_filial(grupo):
    """La ficha y los datos deben contar lo mismo: si no, el alumno lo nota."""
    assert p.cuota_online(grupo) == pytest.approx(
        filiales.obtener(grupo).pct_ecommerce, abs=0.01
    )


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_la_alimentacion_online_es_verosimil(grupo):
    """En España la alimentación online está entre el 3 % y el 5 %.

    Es el error de partida que más distorsionaría el caso, así que queda
    blindado con una prueba.
    """
    assert 0.03 <= p.PENETRACION_ONLINE[grupo]["alimentacion_hosteleria"] <= 0.05


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_la_productividad_por_formato_reproduce_la_de_la_filial(grupo):
    productividad = p.factor_productividad(grupo)
    ventas = sum(
        n * m2 * productividad[f] for f, (n, m2) in p.PARQUE[grupo].items()
    )
    assert ventas / p.superficie_venta(grupo) == pytest.approx(
        p.VENTAS_POR_M2[grupo], rel=1e-9
    )


# --------------------------------------------------------------------------
# Los maestros tienen el tamaño esperado
# --------------------------------------------------------------------------

def test_hay_ciento_treinta_y_cuatro_puntos_de_venta(tablas):
    assert len(tablas["tiendas"]) == sum(p.puntos_de_venta(g) for g in p.GRUPOS) == 134


def test_hay_cuatrocientos_cincuenta_y_un_vehiculos(tablas):
    assert len(tablas["flota"]) == 451


def test_los_codigos_de_tienda_son_unicos(tablas):
    assert tablas["tiendas"]["codigo_tienda"].is_unique


def test_las_matriculas_son_unicas(tablas):
    assert tablas["flota"]["matricula"].is_unique


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_la_superficie_por_filial_es_la_validada(tablas, grupo):
    real = tablas["tiendas"].query("grupo == @grupo")["superficie_m2"].sum()
    assert real == pytest.approx(p.superficie_venta(grupo), rel=TOLERANCIA)


# --------------------------------------------------------------------------
# Las ventas cuadran
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_las_ventas_de_2025_son_las_validadas(tablas, grupo):
    """Tienda física más online debe dar la cifra de la hoja de magnitudes."""
    v = tablas["ventas_diarias"]
    o = tablas["pedidos_online"]
    fisicas = v[(v["fecha"].dt.year == 2025) & (v["grupo"] == grupo)]["ventas_eur"].sum()
    online = o[(o["fecha"].dt.year == 2025) & (o["grupo"] == grupo)]["ventas_eur"].sum()
    assert fisicas + online == pytest.approx(p.ventas_anuales(grupo), rel=TOLERANCIA)


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_la_cuota_online_generada_es_la_esperada(tablas, grupo):
    v = tablas["ventas_diarias"]
    o = tablas["pedidos_online"]
    fisicas = v[(v["fecha"].dt.year == 2025) & (v["grupo"] == grupo)]["ventas_eur"].sum()
    online = o[(o["fecha"].dt.year == 2025) & (o["grupo"] == grupo)]["ventas_eur"].sum()
    assert online / (fisicas + online) == pytest.approx(p.cuota_online(grupo), abs=0.01)


@pytest.mark.parametrize("grupo", p.GRUPOS)
def test_el_mix_de_categorias_generado_es_el_validado(tablas, grupo):
    """Sumando tienda y online, cada categoría debe pesar lo que dice la hoja."""
    vc = tablas["ventas_categoria"]
    o = tablas["pedidos_online"]
    fisicas = vc[(vc["mes"].dt.year == 2025) & (vc["grupo"] == grupo)]
    fisicas = fisicas.groupby("categoria")["ventas_eur"].sum()
    online = o[(o["fecha"].dt.year == 2025) & (o["grupo"] == grupo)]

    totales = {
        c: fisicas.get(c, 0.0) + online[f"ventas_{c}_eur"].sum() for c in p.CATEGORIAS
    }
    suma = sum(totales.values())
    for categoria in p.CATEGORIAS:
        assert totales[categoria] / suma == pytest.approx(
            p.MIX_CATEGORIAS[grupo][categoria], abs=0.015
        )


def test_las_ventas_por_categoria_cuadran_con_las_diarias(tablas):
    """Las dos tablas de ventas físicas deben contar lo mismo."""
    diarias = tablas["ventas_diarias"].groupby("grupo")["ventas_eur"].sum()
    categoria = tablas["ventas_categoria"].groupby("grupo")["ventas_eur"].sum()
    for grupo in p.GRUPOS:
        assert categoria[grupo] == pytest.approx(diarias[grupo], rel=1e-6)


def test_madrid_es_la_filial_mas_grande(tablas):
    ventas = tablas["ventas_diarias"].groupby("grupo")["ventas_eur"].sum()
    assert ventas.idxmax() == "A"


def test_bilbao_es_la_filial_mas_pequena(tablas):
    ventas = tablas["ventas_diarias"].groupby("grupo")["ventas_eur"].sum()
    assert ventas.idxmin() == "E"


# --------------------------------------------------------------------------
# Estacionalidad: los patrones que debe encontrar el alumno están ahí
# --------------------------------------------------------------------------

def test_diciembre_es_el_mes_mas_fuerte(tablas):
    v = tablas["ventas_diarias"]
    por_mes = v.groupby(v["fecha"].dt.month)["ventas_eur"].sum()
    assert por_mes.idxmax() == 12


def test_el_sabado_vende_mas_que_el_lunes(tablas):
    v = tablas["ventas_diarias"]
    por_dia = v.groupby(v["fecha"].dt.weekday)["ventas_eur"].mean()
    assert por_dia[5] > por_dia[0]


def test_hay_crecimiento_de_2024_a_2025(tablas):
    v = tablas["ventas_diarias"]
    por_anio = v.groupby(v["fecha"].dt.year)["ventas_eur"].sum()
    assert por_anio[2025] > por_anio[2024]


def test_black_friday_dispara_las_ventas(tablas):
    """El pico de noviembre debe ser visible sin necesidad de estadística."""
    v = tablas["ventas_diarias"]
    noviembre = v[(v["fecha"].dt.month == 11) & (v["fecha"].dt.year == 2025)]
    diario = noviembre.groupby("fecha")["ventas_eur"].sum()
    ultima_semana = diario[diario.index.day >= 24].mean()
    resto = diario[diario.index.day < 24].mean()
    assert ultima_semana > resto * 1.3


# --------------------------------------------------------------------------
# Los hallazgos del caso: cada filial tiene su problema y debe verse
# --------------------------------------------------------------------------

def test_sevilla_consume_mas_gasoleo_que_madrid(tablas):
    """El hallazgo del grupo D: menos flota, más gasóleo."""
    litros = tablas["consumo_flota"].groupby("grupo")["litros"].sum()
    assert litros["D"] > litros["A"]
    assert p.FLOTA["D"][0] + p.FLOTA["D"][1] < p.FLOTA["A"][0] + p.FLOTA["A"][1]


def test_sevilla_tiene_los_peores_kilometros_en_vacio(tablas):
    rutas = tablas["rutas"].dropna(subset=["pct_km_en_vacio"])
    vacio = rutas.groupby("grupo")["pct_km_en_vacio"].mean()
    assert vacio.idxmax() == "D"


def test_valencia_es_la_mas_intensiva_en_energia(tablas):
    """El hallazgo del grupo C: mucha energía por euro vendido."""
    energia = tablas["energia"].groupby("grupo")["electricidad_kwh"].sum()
    ventas = tablas["ventas_diarias"].groupby("grupo")["ventas_eur"].sum()
    intensidad = energia / ventas
    assert intensidad.idxmax() == "C"


def test_valencia_emite_mas_por_refrigerantes_que_madrid(tablas):
    """Teniendo menos carga instalada: la diferencia es el gas empleado."""
    emisiones = tablas["refrigerantes"].groupby("grupo")["co2e_kg"].sum()
    carga = tablas["refrigerantes"].query("anio == 2025").groupby("grupo")["carga_kg"].sum()
    assert emisiones["C"] > emisiones["A"] * 2
    assert carga["C"] < carga["A"]


def test_bilbao_casi_no_emite_por_refrigerantes(tablas):
    """Ya migrada a CO₂: la comparación más contundente del caso."""
    emisiones = tablas["refrigerantes"].groupby("grupo")["co2e_kg"].sum()
    assert emisiones["E"] < emisiones["A"] / 100


def test_bilbao_es_la_mas_eficiente_en_energia(tablas):
    energia = tablas["energia"].groupby("grupo")["electricidad_kwh"].sum()
    ventas = tablas["ventas_diarias"].groupby("grupo")["ventas_eur"].sum()
    assert (energia / ventas).idxmin() == "E"


def test_valencia_tiene_la_mayor_merma(tablas):
    """Producto fresco: más merma que ninguna otra filial."""
    merma = tablas["inventario"].groupby("grupo").apply(
        lambda d: d["merma_eur"].sum(), include_groups=False
    )
    ventas = tablas["ventas_categoria"].groupby("grupo")["ventas_eur"].sum()
    assert (merma / ventas).idxmax() == "C"


def test_barcelona_tiene_los_plazos_de_entrega_mas_largos(tablas):
    """Su dependencia asiática debe verse en el plazo medio ponderado."""
    plazos = {
        g: sum(p.MIX_ORIGEN[g][o] * p.ORIGENES_PROVEEDOR[o]["plazo"]
               for o in p.ORIGENES_PROVEEDOR)
        for g in p.GRUPOS
    }
    assert max(plazos, key=plazos.get) == "B"


# --------------------------------------------------------------------------
# Sanidad de los datos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tabla,columna", [
    ("ventas_diarias", "ventas_eur"),
    ("ventas_diarias", "tickets"),
    ("ventas_categoria", "ventas_eur"),
    ("pedidos_online", "ventas_eur"),
    ("consumo_flota", "litros"),
    ("consumo_flota", "km"),
    ("energia", "gas_kwh"),
    ("inventario", "stock_medio_eur"),
    ("residuos", "total_kg"),
    ("refrigerantes", "co2e_kg"),
])
def test_no_hay_valores_negativos(tablas, tabla, columna):
    assert (tablas[tabla][columna].dropna() >= 0).all()


def test_los_kilometros_en_vacio_no_superan_los_totales(tablas):
    rutas = tablas["rutas"].dropna(subset=["km_totales"])
    assert (rutas["km_en_vacio"] <= rutas["km_totales"]).all()


def test_la_ocupacion_esta_entre_cero_y_uno(tablas):
    ocupacion = tablas["rutas"]["ocupacion_media"]
    assert ocupacion.between(0, 1).all()


def test_el_periodo_cubierto_son_dos_anios_completos(tablas):
    fechas = tablas["ventas_diarias"]["fecha"]
    assert fechas.min().date() == p.FECHA_INICIO
    assert fechas.max().date() == p.FECHA_FIN
    assert sorted(fechas.dt.year.unique()) == [2024, 2025]


def test_cada_tienda_tiene_un_dato_por_dia(tablas):
    conteo = tablas["ventas_diarias"].groupby("codigo_tienda").size()
    assert conteo.nunique() == 1
    assert conteo.iloc[0] == 731  # 2024 es bisiesto


def test_hay_huecos_deliberados_en_las_lecturas_de_contador(tablas):
    """El dataset no es perfecto a propósito: detectarlo es parte del ejercicio."""
    ausentes = tablas["energia"]["electricidad_kwh"].isna().mean()
    assert 0.005 < ausentes < 0.04


def test_hay_rutas_sin_kilometraje(tablas):
    ausentes = tablas["rutas"]["km_totales"].isna().mean()
    assert 0.005 < ausentes < 0.05


def test_el_generador_es_reproducible():
    """Dos ejecuciones deben dar exactamente lo mismo.

    Si no, un alumno que analice los datos en septiembre y otro en octubre
    llegarían a conclusiones distintas sobre la misma empresa.
    """
    pd.testing.assert_frame_equal(gen.generar_tiendas(), gen.generar_tiendas())
    pd.testing.assert_frame_equal(gen.generar_flota(), gen.generar_flota())


def test_el_volumen_cabe_en_streamlit_cloud(tablas):
    """Streamlit Community Cloud da ~1 GB de RAM: el dataset debe ser pequeño."""
    total_mb = sum(t.memory_usage(deep=True).sum() for t in tablas.values()) / 1024**2
    assert total_mb < 200
