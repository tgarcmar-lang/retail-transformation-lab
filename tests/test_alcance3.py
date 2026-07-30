"""Pruebas del inventario y las palancas de alcance 3.

Dos cosas se vigilan aquí. La primera, que el mensaje del caso se sostenga:
en un minorista el alcance 3 manda, y quien crea que ha resuelto su huella
tocando alcances 1 y 2 se ha equivocado de problema. La segunda, que el
ejercicio de alcance 3 tenga la misma propiedad que el del 25 %: alcanzable
eligiendo bien, imposible eligiendo mal.

Y una tercera, que es la que protege todo lo demás: **el alcance 3 no puede
entrar en el denominador del objetivo del 25 %.** Si alguien lo mete, la
calibración de las cinco filiales se cae y la Sesión 2 deja de funcionar.
"""

import pytest

from core import alcance3 as a3, datos, kpis, palancas as pl

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# La lección: el alcance 3 manda
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_alcance3_es_mucho_mayor_que_el_resto(grupo):
    """Si no lo fuese, la sesión estaría enseñando algo falso."""
    inv = a3.inventario(grupo)
    assert inv["alcance3_t"] > inv["operativo_t"] * 5, (
        f"{grupo}: el alcance 3 solo es {inv['veces_mayor']:.1f} veces mayor"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_alcances_1_y_2_son_una_fraccion_pequena(grupo):
    """Es la cifra que da el susto: lo que llevaban mirando toda la sesión."""
    inv = a3.inventario(grupo)
    assert 0.02 < inv["pct_operativo"] < 0.15


@pytest.mark.parametrize("grupo", GRUPOS)
def test_fabricar_pesa_mas_que_transportar(grupo):
    """El error clásico es creer que el alcance 3 es el transporte.

    Casi nunca lo es: lo que domina es fabricar lo que se vende. Un grupo
    que solo mire camiones y barcos se deja fuera la mayor parte.
    """
    inv = a3.inventario(grupo)
    assert inv["bienes_t"] > inv["transporte_t"] * 3


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_residuos_apenas_pesan(grupo):
    """Suenan a sostenibilidad y no mueven la aguja. Conviene poder verlo."""
    inv = a3.inventario(grupo)
    assert inv["residuos_t"] < inv["alcance3_t"] * 0.02


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_inventario_suma(grupo):
    inv = a3.inventario(grupo)
    assert inv["total_t"] == pytest.approx(
        inv["alcance1_t"] + inv["alcance2_t"] + inv["alcance3_t"]
    )
    assert inv["alcance3_t"] == pytest.approx(
        inv["bienes_t"] + inv["transporte_t"] + inv["residuos_t"]
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_alcances_1_y_2_coinciden_con_la_sesion_1(grupo):
    """El inventario completo no reescribe lo anterior: lo amplía."""
    inv = a3.inventario(grupo)
    assert inv["operativo_t"] == pytest.approx(kpis.huella_total(grupo))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_desglose_suma_el_total(grupo):
    tabla = a3.desglose(grupo)
    assert float(tabla["co2e_t"].sum()) == pytest.approx(
        a3.inventario(grupo)["total_t"]
    )
    assert float(tabla["pct"].sum()) == pytest.approx(1.0)


# --------------------------------------------------------------------------
# La restricción que protege la calibración del 25 %
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_del_25_sigue_midiendose_sobre_alcances_1_y_2(grupo):
    """La línea base de las palancas no puede incluir el alcance 3.

    Es la prueba más importante del fichero. Si el alcance 3 entra en el
    denominador, el 25 % pasa de exigente a imposible y las cinco filiales
    dejan de estar equilibradas.
    """
    assert pl.linea_base(grupo)["total_t"] == pytest.approx(
        a3.inventario(grupo)["operativo_t"]
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_dos_presupuestos_son_independientes(grupo):
    """Gastar en alcance 3 no puede robar dinero del plan operativo."""
    assert a3.presupuesto3(grupo) < pl.presupuesto(grupo)
    assert a3.presupuesto3(grupo) == pytest.approx(
        kpis.ventas_totales(grupo) * a3.PRESUPUESTO3_SOBRE_VENTAS
    )


# --------------------------------------------------------------------------
# El ejercicio tiene solución, y no es trivial
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_de_alcance3_es_alcanzable(grupo):
    mejor = a3.mejor_plan_posible3(grupo)
    assert mejor["reduccion"] >= a3.OBJETIVO3, (
        f"{grupo} no llega: {mejor['reduccion']:.1%}"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_objetivo_de_alcance3_no_se_alcanza_de_sobra(grupo):
    mejor = a3.mejor_plan_posible3(grupo)
    assert mejor["reduccion"] < a3.OBJETIVO3 * 1.7, (
        f"{grupo} llega al {mejor['reduccion']:.1%}: sobra presupuesto"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_mejor_plan_de_alcance3_cabe_en_su_presupuesto(grupo):
    assert a3.mejor_plan_posible3(grupo)["dentro_de_presupuesto"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_ninguna_palanca_suelta_alcanza_el_objetivo(grupo):
    """Hay que combinar transporte y proveedores. Ese es el ejercicio."""
    for palanca in a3.PALANCAS3:
        tope = a3.topes3(grupo)[palanca.codigo]
        resultado = a3.simular3(grupo, {palanca.codigo: tope})
        cabe = resultado["dentro_de_presupuesto"]
        assert not (resultado["objetivo_cumplido"] and cabe), (
            f"{grupo} llega al objetivo solo con {palanca.codigo}"
        )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_gastarlo_todo_en_acercar_la_cadena_fracasa(grupo):
    """La trampa del alcance 3, y es la más tentadora del caso.

    Relocalizar suena a la medida más verde del catálogo. Es la más cara por
    tonelada, con diferencia, y quien se gaste ahí el presupuesto entero se
    queda muy lejos del objetivo.
    """
    presupuesto = a3.presupuesto3(grupo)
    completo = a3.simular3(grupo, {"origen": a3.topes3(grupo)["origen"]})
    proporcion = min(1.0, presupuesto / completo["coste_eur"])
    resultado = a3.simular3(
        grupo, {"origen": a3.topes3(grupo)["origen"] * proporcion}
    )
    assert not resultado["objetivo_cumplido"]
    assert resultado["reduccion"] < a3.OBJETIVO3 / 2


@pytest.mark.parametrize("grupo", GRUPOS)
def test_acercar_la_cadena_es_la_palanca_mas_cara_por_tonelada(grupo):
    tabla = {f["codigo"]: f["coste_por_t"] for f in a3.coste_por_tonelada3(grupo)}
    assert tabla["origen"] > tabla["proveedores"]
    assert tabla["origen"] > tabla["modal"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_programa_de_proveedores_es_la_palanca_mas_grande(grupo):
    """Ninguna medida de transporte puede competir en volumen con fabricar."""
    evitado = {
        f["codigo"]: f["evitado_t"] for f in a3.coste_por_tonelada3(grupo)
    }
    assert evitado["proveedores"] > evitado["modal"]


# --------------------------------------------------------------------------
# La misma palanca no vale para todos
# --------------------------------------------------------------------------

def test_barcelona_es_quien_mas_gana_bajando_del_avion():
    """Cierra el dilema que descubrió en la Sesión 1.

    Compra en Asia casi la mitad de lo que vende, y hasta ahora eso solo se
    pagaba en margen y en plazo. Aquí se paga en carbono, y por primera vez
    tiene un premio por arreglarlo.
    """
    ganancia = {
        grupo: a3.simular3(grupo, {"modal": a3.topes3(grupo)["modal"]})["reduccion"]
        for grupo in GRUPOS
    }
    assert max(ganancia, key=ganancia.get) == "B", ganancia


def test_quien_compra_en_asia_emite_mas_por_euro():
    """No es solo el viaje: la fábrica también emite más."""
    por_pais = a3.compras_por_pais("B").set_index("pais_origen")
    assert por_pais.loc["China", "kg_por_euro"] > por_pais.loc["España", "kg_por_euro"]


def test_volar_emite_muchisimo_mas_que_navegar():
    """La cifra que justifica toda la palanca de cambio modal."""
    from datos.retailnova import parametros as p
    assert p.FACTOR_MODO["aereo"] > p.FACTOR_MODO["maritimo"] * 30


# --------------------------------------------------------------------------
# El simulador no se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    {}, {"modal": -1}, {"origen": 0}, {"inventada": 1.0},
    {"proveedores": None}, {"modal": 1e9}, {"origen": 999},
])
def test_un_plan_raro_de_alcance3_no_revienta(plan):
    resultado = a3.simular3("A", plan)
    assert resultado["evitado_t"] >= 0
    assert resultado["coste_eur"] >= 0
    assert 0 <= resultado["reduccion"] <= 1


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_hacer_nada_no_reduce_nada(grupo):
    resultado = a3.simular3(grupo, {})
    assert resultado["evitado_t"] == 0
    assert resultado["coste_eur"] == 0
    assert not resultado["objetivo_cumplido"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_ninguna_palanca_puede_pasarse_de_su_tope(grupo):
    limites = a3.topes3(grupo)
    exagerado = a3.simular3(grupo, {c: 999 for c in limites})
    maximo = a3.simular3(grupo, limites)
    assert exagerado["evitado_t"] == pytest.approx(maximo["evitado_t"])
    assert exagerado["coste_eur"] == pytest.approx(maximo["coste_eur"])


@pytest.mark.parametrize("grupo", GRUPOS)
def test_mas_intensidad_nunca_reduce_menos(grupo):
    for palanca in a3.PALANCAS3:
        tope = a3.topes3(grupo)[palanca.codigo]
        if tope <= 0:
            continue
        mitad = a3.simular3(grupo, {palanca.codigo: tope / 2})["evitado_t"]
        entero = a3.simular3(grupo, {palanca.codigo: tope})["evitado_t"]
        assert entero >= mitad - 1e-6, palanca.codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_se_puede_reducir_mas_de_lo_que_se_emite(grupo):
    resultado = a3.simular3(grupo, a3.plan_maximo3(grupo))
    assert 0 < resultado["evitado_t"] < resultado["base_t"]
    assert resultado["final_t"] == pytest.approx(
        resultado["base_t"] - resultado["evitado_t"]
    )


# --------------------------------------------------------------------------
# Contenido
# --------------------------------------------------------------------------

def test_hay_tres_palancas_de_alcance3_con_codigo_unico():
    assert len(a3.PALANCAS3) == 3
    assert len({palanca.codigo for palanca in a3.PALANCAS3}) == 3


def test_cada_palanca_se_explica_en_espanol():
    for palanca in a3.PALANCAS3:
        assert palanca.nombre and palanca.unidad and palanca.ayuda
        assert len(palanca.descripcion) > 40


def test_toda_palanca_tiene_calculo_y_tope():
    for palanca in a3.PALANCAS3:
        assert palanca.codigo in a3.CALCULOS3
        assert palanca.codigo in a3.topes3("A")


def test_los_factores_de_alcance3_estan_en_los_datos():
    """Regla dura del proyecto: las cifras del caso viven en los datos."""
    factores = datos.cargar("factores_emision")
    assert (factores["alcance"] == 3).sum() >= 6
