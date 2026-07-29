"""Pruebas del simulador de descarbonización.

Lo que se vigila aquí no es la aritmética, sino que **el ejercicio siga
teniendo sentido**: que el objetivo sea alcanzable eligiendo bien, imposible
eligiendo mal, y distinto en cada filial. Si alguien toca un coste o el
presupuesto y rompe ese equilibrio, salta aquí.
"""

import pytest

from core import datos, palancas as pl

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# El ejercicio tiene solución
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_es_alcanzable(grupo):
    """Si una filial no puede llegar al 25 %, su grupo sale de clase frustrado."""
    mejor = pl.mejor_plan_posible(grupo)
    assert mejor["reduccion"] >= pl.OBJETIVO, (
        f"{grupo} no puede llegar al objetivo ni con el mejor plan: "
        f"{mejor['reduccion']:.1%}"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_no_se_alcanza_de_sobra(grupo):
    """Con demasiado margen no habría que elegir, y elegir es el ejercicio."""
    mejor = pl.mejor_plan_posible(grupo)
    assert mejor["reduccion"] < pl.OBJETIVO * 1.6, (
        f"{grupo} llega al {mejor['reduccion']:.1%}: sobra presupuesto"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_un_mal_plan_no_llega(grupo):
    """Gastarlo todo en la palanca equivocada tiene que fracasar."""
    resultado = pl.simular(grupo, {"electrificacion": 1.0})
    assert not resultado["objetivo_cumplido"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_hacer_nada_no_reduce_nada(grupo):
    resultado = pl.simular(grupo, {})
    assert resultado["evitado_t"] == 0
    assert resultado["coste_eur"] == 0
    assert not resultado["objetivo_cumplido"]


@pytest.mark.parametrize("grupo", ["A", "B", "E"])
def test_estas_filiales_necesitan_combinar_palancas(grupo):
    """Ninguna palanca suelta les llega: tienen que construir un plan."""
    for palanca in pl.PALANCAS:
        tope = pl.topes(grupo)[palanca.codigo]
        resultado = pl.simular(grupo, {palanca.codigo: tope})
        assert not resultado["objetivo_cumplido"], (
            f"{grupo} llega al objetivo solo con {palanca.codigo}"
        )


@pytest.mark.parametrize("grupo", ["C", "D"])
def test_quien_identifico_su_problema_tiene_premio(grupo):
    """Valencia y Sevilla arrastran R-404A: cambiarlo casi les basta.

    Es deliberado. Su grupo descubrió el problema en la Sesión 1 y aquí ve
    que la solución es barata y enorme. Eso cierra el círculo.
    """
    tope = pl.topes(grupo)["refrigerante"]
    resultado = pl.simular(grupo, {"refrigerante": tope})
    assert resultado["objetivo_cumplido"]
    assert resultado["dentro_de_presupuesto"]


# --------------------------------------------------------------------------
# La misma palanca no vale para todos
# --------------------------------------------------------------------------

def test_a_bilbao_el_refrigerante_no_le_sirve_de_nada():
    """Ya migró a CO₂. Si copia el plan de Valencia, tira el dinero.

    Es la trampa más instructiva de la sesión: cuesta 1,4 M€ y reduce cero.
    """
    resultado = pl.simular("E", {"refrigerante": 1.0})
    assert resultado["evitado_t"] < 5
    assert resultado["coste_eur"] > 500_000


def test_el_orden_de_las_palancas_cambia_segun_la_filial():
    """Si el orden fuese el mismo para todos, no habría nada que decidir."""
    primeras = {
        grupo: pl.coste_por_tonelada(grupo)[0]["codigo"] for grupo in GRUPOS
    }
    assert len(set(primeras.values())) >= 2, primeras


def test_sevilla_tiene_mas_margen_en_rutas_que_bilbao():
    """Sevilla va al 34 % de vacío y Bilbao al 13,8 %: no es comparable."""
    assert pl.topes("D")["rutas"] > pl.topes("E")["rutas"] * 5


@pytest.mark.parametrize("grupo", GRUPOS)
def test_ninguna_palanca_puede_pasarse_de_su_tope(grupo):
    limites = pl.topes(grupo)
    exagerado = pl.simular(grupo, {c: 999 for c in limites})
    maximo = pl.simular(grupo, limites)
    assert exagerado["evitado_t"] == pytest.approx(maximo["evitado_t"])
    assert exagerado["coste_eur"] == pytest.approx(maximo["coste_eur"])


# --------------------------------------------------------------------------
# El simulador no se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    {}, {"refrigerante": -1}, {"energia": 0}, {"inventada": 1.0},
    {"rutas": None}, {"electrificacion": 1e9},
])
def test_un_plan_raro_no_revienta(plan):
    """El alumno mueve controles: no puede ver un error por eso."""
    resultado = pl.simular("A", plan)
    assert resultado["evitado_t"] >= 0
    assert resultado["coste_eur"] >= 0
    assert 0 <= resultado["reduccion"] <= 1


@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_emisiones_finales_cuadran(grupo):
    resultado = pl.simular(grupo, pl.plan_maximo(grupo))
    assert resultado["final_t"] == pytest.approx(
        resultado["base_t"] - resultado["evitado_t"]
    )
    assert resultado["final_t"] > 0, "Nadie puede llegar a cero con esto"


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_se_puede_reducir_mas_de_lo_que_se_emite(grupo):
    resultado = pl.simular(grupo, pl.plan_maximo(grupo))
    assert resultado["evitado_t"] < resultado["base_t"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_linea_base_coincide_con_la_huella_de_la_sesion_uno(grupo):
    """La Sesión 2 arranca justo donde terminó la Sesión 1."""
    from core import kpis
    assert pl.linea_base(grupo)["total_t"] == pytest.approx(
        kpis.huella_total(grupo)
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_desglose_suma_el_total(grupo):
    base = pl.linea_base(grupo)
    partes = (base["electricidad_t"] + base["flota_t"]
              + base["refrigerante_t"] + base["gas_t"])
    assert partes == pytest.approx(base["total_t"])


@pytest.mark.parametrize("grupo", GRUPOS)
def test_mas_intensidad_nunca_reduce_menos(grupo):
    """Monotonía: subir un control no puede empeorar el resultado."""
    for palanca in pl.PALANCAS:
        tope = pl.topes(grupo)[palanca.codigo]
        if tope <= 0:
            continue
        mitad = pl.simular(grupo, {palanca.codigo: tope / 2})["evitado_t"]
        entero = pl.simular(grupo, {palanca.codigo: tope})["evitado_t"]
        assert entero >= mitad - 1e-6, palanca.codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_electrificar_reduce_pero_no_a_cero(grupo):
    """La furgoneta eléctrica también emite: por la red, pero emite."""
    resultado = pl.simular(grupo, {"electrificacion": 1.0})
    base = pl.linea_base(grupo)
    assert 0 < resultado["evitado_t"] < base["flota_t"]


# --------------------------------------------------------------------------
# Presupuesto
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_presupuesto_escala_con_el_tamano(grupo):
    from core import kpis
    assert pl.presupuesto(grupo) == pytest.approx(
        kpis.ventas_totales(grupo) * pl.PRESUPUESTO_SOBRE_VENTAS
    )


def test_madrid_tiene_mas_presupuesto_que_bilbao():
    assert pl.presupuesto("A") > pl.presupuesto("E")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_pasarse_de_presupuesto_se_detecta(grupo):
    resultado = pl.simular(grupo, pl.plan_maximo(grupo))
    assert not resultado["dentro_de_presupuesto"], (
        "Todo al máximo debería salirse del presupuesto en todas las filiales"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_mejor_plan_cabe_en_el_presupuesto(grupo):
    assert pl.mejor_plan_posible(grupo)["dentro_de_presupuesto"]


# --------------------------------------------------------------------------
# Contenido
# --------------------------------------------------------------------------

def test_hay_cuatro_palancas_con_codigo_unico():
    assert len(pl.PALANCAS) == 4
    assert len({palanca.codigo for palanca in pl.PALANCAS}) == 4


def test_cada_palanca_se_explica_en_espanol():
    for palanca in pl.PALANCAS:
        assert palanca.nombre and palanca.descripcion and palanca.unidad
        assert palanca.ayuda
        assert len(palanca.descripcion) > 40


def test_el_objetivo_es_el_del_alcance_del_curso():
    assert pl.OBJETIVO == 0.25
