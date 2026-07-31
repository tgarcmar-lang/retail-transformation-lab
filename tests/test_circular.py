"""Pruebas del modelo de economía circular de la Sesión 3.

Lo que se vigila aquí es que la lección se sostenga:

1. **La jerarquía de residuos tiene que rendir en ese orden.** Reciclar es lo
   más barato por tonelada y no puede bastar. Si alguien abarata la
   prevención hasta hacerla la primera opción de todos, la sesión pierde el
   sentido y salta una prueba.
2. **Cada filial tiene que liderar en algo distinto**, como en las dos
   sesiones anteriores. Si dos grupos llegan al mismo hallazgo, la puesta en
   común se hunde.
3. **El objetivo tiene que ser alcanzable eligiendo bien e imposible
   eligiendo mal.**
"""

import pytest

from core import circular as ci, datos, kpis

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# El inventario de materiales
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_inventario_cuadra(grupo):
    inv = ci.inventario(grupo)
    assert inv["perdida_t"] == pytest.approx(
        inv["generado_t"] - inv["recirculado_t"]
    )
    assert 0 < inv["recirculado_t"] < inv["generado_t"]
    assert inv["objetivo_t"] == pytest.approx(
        inv["perdida_t"] * ci.OBJETIVO_CIRCULAR
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_reciclar_no_es_recircular(grupo):
    """Una tonelada reciclada no equivale a una que nunca se generó.

    Es la cifra que justifica toda la jerarquía. Si alguien pone el factor a
    1, reciclar pasaría a ser tan bueno como prevenir y la sesión dejaría de
    enseñar lo que quiere enseñar.
    """
    inv = ci.inventario(grupo)
    assert inv["recirculado_t"] < inv["reciclado_t"]
    assert ci.FACTOR_RECICLAJE < ci.FACTOR_REUTILIZACION


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_circularidad_de_partida_es_mejorable(grupo):
    """Ninguna filial parte tan bien que no tenga nada que hacer."""
    assert 0.20 < ci.inventario(grupo)["pct_circularidad"] < 0.60


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_desglose_suma_lo_generado(grupo):
    tabla = ci.desglose(grupo)
    assert float(tabla["generado_t"].sum()) == pytest.approx(
        ci.inventario(grupo)["generado_t"]
    )


# --------------------------------------------------------------------------
# La jerarquía de residuos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_reciclar_es_lo_mas_barato_por_tonelada(grupo):
    """Y por eso es por donde empieza todo el mundo.

    Que sea lo más barato no es un fallo del modelo: es la razón por la que
    las empresas se quedan ahí. La sesión existe para enseñar que no basta.
    """
    tabla = ci.coste_por_tonelada(grupo)
    assert tabla[0]["codigo"] == "segregacion", [f["codigo"] for f in tabla]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_reciclar_solo_no_alcanza_el_objetivo(grupo):
    """La lección central de la sesión, verificada en las cinco filiales."""
    resultado = ci.simular(grupo, {"segregacion": ci.topes(grupo)["segregacion"]})
    assert not resultado["objetivo_cumplido"]
    assert resultado["reduccion"] < ci.OBJETIVO_CIRCULAR / 2


@pytest.mark.parametrize("grupo", GRUPOS)
def test_hace_falta_prevenir_para_llegar(grupo):
    """Sin ninguna palanca de prevención no se llega, ni gastándolo todo."""
    solo_abajo = {
        palanca.codigo: ci.topes(grupo)[palanca.codigo]
        for palanca in ci.PALANCAS if palanca.nivel != "Prevenir"
    }
    assert not ci.simular(grupo, solo_abajo)["objetivo_cumplido"]


def test_las_palancas_cubren_los_tres_niveles():
    niveles = {palanca.nivel for palanca in ci.PALANCAS}
    assert niveles == set(ci.NIVELES)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_plan_reparte_por_niveles(grupo):
    resultado = ci.simular(grupo, ci.plan_maximo(grupo))
    assert sum(resultado["por_nivel"].values()) == pytest.approx(
        resultado["evitado_t"]
    )
    assert all(v > 0 for v in resultado["por_nivel"].values())


# --------------------------------------------------------------------------
# El ejercicio tiene solución, y no es trivial
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_es_alcanzable(grupo):
    mejor = ci.mejor_plan_posible(grupo)
    assert mejor["reduccion"] >= ci.OBJETIVO_CIRCULAR, (
        f"{grupo} no llega ni con el mejor plan: {mejor['reduccion']:.1%}"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_no_se_alcanza_de_sobra(grupo):
    mejor = ci.mejor_plan_posible(grupo)
    assert mejor["reduccion"] < ci.OBJETIVO_CIRCULAR * 1.5, (
        f"{grupo} llega al {mejor['reduccion']:.1%}: sobra presupuesto"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_ninguna_palanca_suelta_resuelve_la_sesion(grupo):
    for palanca in ci.PALANCAS:
        resultado = ci.simular(
            grupo, {palanca.codigo: ci.topes(grupo)[palanca.codigo]}
        )
        assert not (resultado["objetivo_cumplido"]
                    and resultado["dentro_de_presupuesto"]), (
            f"{grupo} resuelve la sesión solo con {palanca.codigo}"
        )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_mejor_plan_cabe_en_el_presupuesto(grupo):
    assert ci.mejor_plan_posible(grupo)["dentro_de_presupuesto"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_hacerlo_todo_se_sale_de_presupuesto(grupo):
    assert not ci.simular(grupo, ci.plan_maximo(grupo))["dentro_de_presupuesto"]


# --------------------------------------------------------------------------
# Cada filial lidera en algo distinto
# --------------------------------------------------------------------------

def test_valencia_es_quien_mas_gana_reduciendo_merma():
    """Su problema desde la Sesión 1: alimentación, frío y 4,46 M€ de merma."""
    peso = {
        grupo: ci.simular(grupo, {"merma": ci.REDUCCION_MERMA_MAXIMA})["reduccion"]
        for grupo in GRUPOS
    }
    assert max(peso, key=peso.get) == "C", peso


def test_sevilla_tiene_el_envase_retornable_mas_barato():
    """Sus camiones ya vuelven vacíos: el circuito de retorno está pagado.

    Es donde la logística verde y la economía circular se tocan, y es el
    mejor ejemplo del curso de que un problema puede financiar otro.
    """
    precio = {
        grupo: {f["codigo"]: f["coste_por_t"]
                for f in ci.coste_por_tonelada(grupo)}["retornable"]
        for grupo in GRUPOS
    }
    assert min(precio, key=precio.get) == "D", precio


def test_barcelona_arrastra_el_mayor_sobreembalaje():
    """Compra la mitad en Asia y la mercancía llega envuelta tres veces."""
    exceso = {
        grupo: ci.envases_resumen(grupo)["factor_sobreembalaje"]
        for grupo in GRUPOS
    }
    assert max(exceso, key=exceso.get) == "B", exceso


def test_madrid_concentra_las_devoluciones():
    """Es la filial más digital: su material vuelve, y mucho."""
    devueltas = {
        grupo: ci.devoluciones_resumen(grupo)["no_revendible_t"]
        for grupo in GRUPOS
    }
    assert max(devueltas, key=devueltas.get) == "A", devueltas


def test_a_bilbao_no_le_queda_margen_reciclando():
    """Ya recicla el 84 %: la trampa de la sesión, equivalente a la del
    refrigerante en la Sesión 2. Tiene que subir en la jerarquía."""
    assert ci.topes("E")["segregacion"] < 6
    for grupo in ["A", "B", "C", "D"]:
        assert ci.topes(grupo)["segregacion"] > ci.topes("E")["segregacion"] * 2


def test_el_orden_de_las_palancas_no_es_el_mismo_en_todas():
    """Descontando el reciclaje, que es el más barato para todos."""
    segundas = {
        grupo: [f["codigo"] for f in ci.coste_por_tonelada(grupo)][1]
        for grupo in GRUPOS
    }
    assert len(set(segundas.values())) >= 2, segundas


# --------------------------------------------------------------------------
# Las devoluciones: caras en material, baratísimas en dinero
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_evitar_devoluciones_es_carisimo_por_tonelada(grupo):
    """Y aun así hay que enseñarla: en euros es otra historia."""
    precios = {f["codigo"]: f["coste_por_t"] for f in ci.coste_por_tonelada(grupo)}
    assert precios["devoluciones"] > precios["segregacion"] * 2


@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_devoluciones_cuestan_dinero_de_verdad_hoy(grupo):
    """El contrapeso: lo que ya se están gastando en gestionarlas."""
    resumen = ci.devoluciones_resumen(grupo)
    assert resumen["coste_gestion_eur"] > 0
    assert resumen["valor_eur"] > resumen["coste_gestion_eur"]


# --------------------------------------------------------------------------
# Coherencia con los datos y con las sesiones anteriores
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_se_devuelve_mas_de_lo_que_se_vende(grupo):
    resumen = ci.devoluciones_resumen(grupo)
    assert 0 < resumen["tasa_media"] < 0.45
    assert resumen["valor_eur"] < kpis.canal(grupo)["ventas_online_eur"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_envase_es_coherente_con_el_residuo_recogido(grupo):
    """Las dos tablas cuentan lo mismo desde ángulos distintos: el envase
    puesto en circulación no puede ser menor que el cartón y el plástico que
    se recogen, ni disparatadamente mayor."""
    inv = ci.inventario(grupo)
    carton_plastico = (inv["por_tipo_t"]["carton"] + inv["por_tipo_t"]["plastico"])
    assert carton_plastico < inv["envases_t"] < carton_plastico * 1.6


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_merma_en_toneladas_es_verosimil(grupo):
    assert 0 < ci.merma_t(grupo) < ci.inventario(grupo)["generado_t"]


def test_los_datos_nuevos_estan_disponibles():
    for tabla in ("devoluciones", "envases"):
        assert not datos.cargar(tabla).empty


# --------------------------------------------------------------------------
# El simulador no se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    {}, {"merma": -1}, {"segregacion": 0}, {"inventada": 1.0},
    {"embalaje": None}, {"retornable": 1e9}, {"devoluciones": 999},
])
def test_un_plan_raro_no_revienta(plan):
    resultado = ci.simular("A", plan)
    assert resultado["evitado_t"] >= 0
    assert resultado["coste_eur"] >= 0
    assert 0 <= resultado["reduccion"] <= 1


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_hacer_nada_no_recupera_nada(grupo):
    resultado = ci.simular(grupo, {})
    assert resultado["evitado_t"] == 0
    assert resultado["coste_eur"] == 0
    assert not resultado["objetivo_cumplido"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_ninguna_palanca_puede_pasarse_de_su_tope(grupo):
    limites = ci.plan_maximo(grupo)
    exagerado = ci.simular(grupo, {c: 999 for c in limites})
    maximo = ci.simular(grupo, limites)
    assert exagerado["evitado_t"] == pytest.approx(maximo["evitado_t"])
    assert exagerado["coste_eur"] == pytest.approx(maximo["coste_eur"])


@pytest.mark.parametrize("grupo", GRUPOS)
def test_mas_intensidad_nunca_recupera_menos(grupo):
    for palanca in ci.PALANCAS:
        tope = ci.topes(grupo)[palanca.codigo]
        if tope <= 0:
            continue
        mitad = ci.simular(grupo, {palanca.codigo: tope / 2})["evitado_t"]
        entero = ci.simular(grupo, {palanca.codigo: tope})["evitado_t"]
        assert entero >= mitad - 1e-6, palanca.codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_se_puede_recuperar_mas_de_lo_que_se_pierde(grupo):
    resultado = ci.simular(grupo, ci.plan_maximo(grupo))
    assert 0 < resultado["evitado_t"] < resultado["base_t"]
    assert resultado["final_t"] > 0


# --------------------------------------------------------------------------
# Contenido
# --------------------------------------------------------------------------

def test_hay_seis_palancas_con_codigo_unico():
    assert len(ci.PALANCAS) == 6
    assert len({palanca.codigo for palanca in ci.PALANCAS}) == 6


def test_cada_palanca_se_explica_en_espanol():
    for palanca in ci.PALANCAS:
        assert palanca.nombre and palanca.unidad and palanca.ayuda
        assert len(palanca.descripcion) > 40
        assert palanca.nivel in ci.NIVELES


def test_toda_palanca_tiene_calculo_y_tope():
    for palanca in ci.PALANCAS:
        assert palanca.codigo in ci.CALCULOS
        assert palanca.codigo in ci.topes("A")


def test_el_presupuesto_escala_con_el_tamano():
    for grupo in GRUPOS:
        assert ci.presupuesto(grupo) == pytest.approx(
            kpis.ventas_totales(grupo) * ci.PRESUPUESTO_SOBRE_VENTAS
        )
    assert ci.presupuesto("A") > ci.presupuesto("E")


def test_la_sesion_no_reutiliza_el_objetivo_de_la_sesion_dos():
    """Son inventarios distintos y objetivos distintos. Confundirlos sería
    exactamente el error que la Sesión 2 dedica un paso entero a desmontar."""
    from core import palancas
    assert ci.OBJETIVO_CIRCULAR != palancas.OBJETIVO
    assert ci.PRESUPUESTO_SOBRE_VENTAS != palancas.PRESUPUESTO_SOBRE_VENTAS
