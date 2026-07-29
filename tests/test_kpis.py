"""Pruebas de los cálculos del diagnóstico.

Aquí no se comprueba que el código funcione, sino que **dice la verdad**:
que las ventas cuadran con las de la hoja de magnitudes, que la huella suma
lo que debe y que cada filial llega a clase con el problema que le tocaba.
"""

import pytest

from core import datos, filiales, kpis
from datos.retailnova import parametros as p

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


def test_los_datos_estan_generados():
    assert datos.hay_datos(), (
        "Faltan los CSV. Genera los datos con: "
        "python -m datos.retailnova.generador"
    )


def test_hay_dos_anios():
    assert datos.anios_disponibles() == [2024, 2025]


# --------------------------------------------------------------------------
# Las cifras coinciden con lo validado
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_ventas_coinciden_con_la_hoja_de_magnitudes(grupo):
    assert kpis.ventas_totales(grupo) == pytest.approx(
        p.ventas_anuales(grupo), rel=0.01
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_cuota_online_coincide_con_la_ficha(grupo):
    assert kpis.canal(grupo)["cuota_online"] == pytest.approx(
        filiales.obtener(grupo).pct_ecommerce, abs=0.015
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_ventas_totales_superan_a_las_de_tienda(grupo):
    """El canal online no está en `ventas_diarias.csv`: es el error clásico."""
    tienda = datos.de_la_filial("ventas_diarias", grupo)
    tienda = tienda[tienda["fecha"].dt.year == 2025]["ventas_eur"].sum()
    assert kpis.ventas_totales(grupo) > tienda


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_reparto_por_formato_suma_el_total(grupo):
    tabla = kpis.ventas_por_formato(grupo)
    assert tabla["pct_ventas"].sum() == pytest.approx(1.0)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_reparto_por_categoria_suma_el_total(grupo):
    tabla = kpis.ventas_por_categoria(grupo)
    assert tabla["pct_total"].sum() == pytest.approx(1.0)
    assert tabla["total_eur"].sum() == pytest.approx(kpis.ventas_totales(grupo), rel=0.01)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_huella_suma_el_cien_por_cien(grupo):
    tabla = kpis.huella(grupo)
    assert tabla["pct"].sum() == pytest.approx(1.0)
    assert kpis.huella_total(grupo) == pytest.approx(tabla["co2e_t"].sum())


@pytest.mark.parametrize("grupo", GRUPOS)
def test_todas_las_filiales_crecen_pero_poco(grupo):
    variacion = kpis.crecimiento(grupo)["variacion"]
    assert 0 < variacion < 0.15


# --------------------------------------------------------------------------
# Cada filial llega a clase con su problema
# --------------------------------------------------------------------------

def test_madrid_es_la_peor_en_entregas_fallidas():
    """El problema del grupo A: la última milla urbana."""
    tabla = kpis.comparativa().set_index("grupo")
    assert tabla["pct_entregas_fallidas"].idxmax() == "A"


def test_barcelona_es_la_peor_en_plazo_y_en_stock():
    """El problema del grupo B: la cadena asiática y su coste financiero."""
    tabla = kpis.comparativa().set_index("grupo")
    assert tabla["plazo_medio_dias"].idxmax() == "B"
    assert tabla["dias_cobertura"].idxmax() == "B"


def test_valencia_es_la_peor_en_energia_y_en_merma():
    """El problema del grupo C: la cadena de frío."""
    tabla = kpis.comparativa().set_index("grupo")
    assert tabla["intensidad_energetica"].idxmax() == "C"
    assert tabla["pct_merma"].idxmax() == "C"


def test_sevilla_es_la_peor_en_vacio_y_en_gasoleo():
    """El problema del grupo D: rutas mal optimizadas."""
    tabla = kpis.comparativa().set_index("grupo")
    assert tabla["pct_km_en_vacio"].idxmax() == "D"
    assert tabla["litros_por_meur"].idxmax() == "D"


def test_bilbao_es_la_mejor_en_casi_todo_pero_la_mas_pequena():
    """El problema del grupo E es el contrario: no tiene escala."""
    tabla = kpis.comparativa().set_index("grupo")
    assert tabla["ventas_m_eur"].idxmin() == "E"
    assert tabla["intensidad_energetica"].idxmin() == "E"
    assert tabla["pct_km_en_vacio"].idxmin() == "E"


@pytest.mark.parametrize("grupo,esperado", [
    ("A", "Entregas fallidas"),
    ("B", "Cobertura de stock"),
    ("C", "Energía por millón vendido"),
    ("D", "CO₂e por millón vendido"),
])
def test_el_punto_debil_principal_es_el_previsto(grupo, esperado):
    """Si esto falla, un grupo llegará a clase sin nada que descubrir."""
    assert kpis.puntos_debiles(grupo)["indicador"].iloc[0] == esperado


def test_cada_filial_tiene_un_punto_debil_distinto():
    """Cinco grupos con el mismo hallazgo harían la puesta en común inútil."""
    principales = {kpis.puntos_debiles(g)["indicador"].iloc[0] for g in GRUPOS}
    assert len(principales) >= 4


# --------------------------------------------------------------------------
# La comparativa se sostiene
# --------------------------------------------------------------------------

def test_la_comparativa_tiene_las_cinco_filiales():
    tabla = kpis.comparativa()
    assert len(tabla) == 5
    assert set(tabla["grupo"]) == set(GRUPOS)


def test_la_comparativa_no_tiene_huecos():
    assert not kpis.comparativa().isna().any().any()


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_puestos_van_del_uno_al_cinco(grupo):
    tabla = kpis.posicion(grupo)
    assert tabla["puesto"].between(1, 5).all()
    assert len(tabla) == len(kpis.INDICADORES)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_cada_filial_es_primera_en_algo(grupo):
    """Nadie debe salir de clase pensando que su filial no vale para nada."""
    assert (kpis.posicion(grupo)["puesto"] == 1).any()


# --------------------------------------------------------------------------
# Los huecos deliberados siguen ahí
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_hay_huecos_que_el_alumno_debe_detectar(grupo):
    calidad = kpis.calidad_de_los_datos(grupo)
    assert calidad["lecturas_electricas_ausentes"] > 0
    assert calidad["partes_de_ruta_sin_km"] > 0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_energia_se_imputa_al_calcular_la_huella(grupo):
    """Ignorar los huecos infravaloraría el consumo: hay que rellenarlos."""
    bruto = datos.de_la_filial("energia", grupo)
    bruto = bruto[bruto["mes"].dt.year == 2025]["electricidad_kwh"].sum()
    assert kpis.energia_resumen(grupo)["electricidad_kwh"] > bruto


# --------------------------------------------------------------------------
# Errores comprensibles
# --------------------------------------------------------------------------

def test_una_tabla_inexistente_avisa_con_claridad():
    with pytest.raises(ValueError, match="Tabla desconocida"):
        datos.cargar("inventadas")


def test_un_grupo_inexistente_avisa_con_claridad():
    with pytest.raises(ValueError, match="Grupo desconocido"):
        filiales.obtener("Z")
