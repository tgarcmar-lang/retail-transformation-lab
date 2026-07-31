"""Pruebas del modelo de reporting ESG de la Sesión 4.

Lo que se vigila aquí:

1. **Que la materialidad no sea desempeño.** La filial que mejor opera no
   puede quedarse sin asuntos materiales, y la matriz tiene que salir
   distinta en cada filial.
2. **Que las cinco tentaciones se detecten.** Todas son técnicamente
   ciertas; si el verificador dejase pasar alguna, la sesión enseñaría a
   maquillar.
3. **Que el ejercicio tenga solución.** Existe una memoria que pasa la
   revisión sin salvedades, en las cinco filiales.
"""

import pytest

from core import datos, reporting as rep

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# El catálogo
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_todos_los_indicadores_se_calculan(grupo):
    """Un indicador que reviente en clase deja la sesión inservible."""
    for indicador in rep.INDICADORES:
        valor = rep.valor(grupo, indicador.codigo)
        assert valor == valor, f"{indicador.codigo} devuelve NaN"
        assert valor >= 0, indicador.codigo


def test_el_catalogo_cubre_las_tres_dimensiones():
    dimensiones = {rep.POR_TEMA[i.tema].dimension for i in rep.INDICADORES}
    assert dimensiones == {"Ambiental", "Social", "Gobernanza"}


def test_cada_tema_tiene_al_menos_un_indicador():
    """Si un asunto material no tuviera indicador, sería incumplible."""
    con_indicador = {i.tema for i in rep.INDICADORES}
    for tema in rep.TEMAS:
        assert tema.codigo in con_indicador, tema.codigo


def test_los_indicadores_declaran_su_estandar_y_su_calidad():
    for indicador in rep.INDICADORES:
        assert indicador.estandar
        assert indicador.calidad in {"alta", "media", "baja"}


def test_el_alcance_3_se_marca_como_dato_de_baja_calidad():
    """Es la coherencia con lo que se enseñó en la Sesión 2."""
    assert rep.POR_CODIGO["e_huella_3"].calidad == "baja"


def test_hay_indicadores_de_la_norma_de_logistica():
    """ISO 14083 es el ancla de la sesión: sin ella sobra la mitad."""
    con_iso = [i for i in rep.INDICADORES if "14083" in i.estandar]
    assert len(con_iso) >= 3


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_catalogo_se_construye_entero(grupo):
    tabla = rep.catalogo(grupo)
    assert len(tabla) == len(rep.INDICADORES)
    assert not tabla["valor"].isna().any()


# --------------------------------------------------------------------------
# Doble materialidad
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_matriz_cubre_todos_los_asuntos(grupo):
    tabla = rep.matriz_materialidad(grupo)
    assert len(tabla) == len(rep.TEMAS)
    assert tabla["impacto"].between(1, 5).all()
    assert tabla["financiera"].between(1, 5).all()


@pytest.mark.parametrize("grupo", GRUPOS)
def test_toda_filial_tiene_asuntos_materiales(grupo):
    """Incluida la que mejor opera.

    Es el error conceptual que hay que evitar: la materialidad no mide
    desempeño. Una filial impecable sigue teniendo asuntos materiales,
    porque sigue moviendo mercancía y empleando gente.
    """
    materiales = rep.temas_materiales(grupo)
    assert len(materiales) >= rep.MINIMO_ASUNTOS, f"{grupo}: {materiales}"


@pytest.mark.parametrize("grupo", GRUPOS)
def test_ninguna_filial_tiene_todo_material(grupo):
    """Si todo fuese material no habría que elegir, y elegir es el ejercicio."""
    assert len(rep.temas_materiales(grupo)) < len(rep.TEMAS)


def test_la_materialidad_es_distinta_en_cada_filial():
    """Si dos grupos tuvieran la misma matriz, la puesta en común se hunde."""
    primeros = {g: rep.temas_materiales(g)[0] for g in GRUPOS}
    assert len(set(primeros.values())) >= 3, primeros


def test_valencia_tiene_la_merma_como_asunto_material():
    """Es su hallazgo desde la Sesión 1 y su palanca en la Sesión 3."""
    assert "merma" in rep.temas_materiales("C")


def test_sevilla_tiene_el_transporte_como_asunto_material():
    """34 % de kilómetros en vacío y la flota más vieja."""
    assert "transporte" in rep.temas_materiales("D")


def test_barcelona_tiene_el_trabajo_de_la_cadena_como_asunto_material():
    """El 48 % de su compra viene de países de riesgo laboral alto.

    Es la tercera cara del mismo dilema: margen en la Sesión 1, carbono en
    la 2, condiciones laborales en la 4.
    """
    assert "trabajo_cadena" in rep.temas_materiales("B")


def test_bilbao_tiene_material_la_cadena_de_valor():
    """La filial más limpia es la que menos manda sobre lo que emite."""
    assert "cadena_suministro" in rep.temas_materiales("E")


def test_madrid_no_se_queda_sin_asuntos_por_ser_eficiente():
    """Es la más eficiente por millón vendido y aun así informa."""
    assert len(rep.temas_materiales("A")) >= rep.MINIMO_ASUNTOS


def test_basta_con_una_de_las_dos_materialidades():
    """La doble materialidad es una unión, no una intersección."""
    encontrado = False
    for grupo in GRUPOS:
        tabla = rep.matriz_materialidad(grupo)
        solo_una = tabla[
            tabla["material"]
            & ((tabla["impacto"] < rep.UMBRAL_MATERIALIDAD)
               | (tabla["financiera"] < rep.UMBRAL_MATERIALIDAD))
        ]
        encontrado = encontrado or not solo_una.empty
    assert encontrado, "Ningún asunto es material por una sola vía"


# --------------------------------------------------------------------------
# Las cinco tentaciones
# --------------------------------------------------------------------------

def test_hay_cinco_declaraciones_con_codigo_unico():
    assert len(rep.DECLARACIONES) == 5
    assert len({d.codigo for d in rep.DECLARACIONES}) == 5


def test_toda_declaracion_tiene_una_opcion_correcta_entre_las_suyas():
    for declaracion in rep.DECLARACIONES:
        assert declaracion.correcta in declaracion.opciones
        assert len(declaracion.opciones) >= 2
        assert declaracion.gravedad in {"grave", "salvedad"}
        assert len(declaracion.porque) > 40


@pytest.mark.parametrize("declaracion", rep.DECLARACIONES, ids=lambda d: d.codigo)
def test_cada_tentacion_se_detecta(declaracion):
    """Se parte de una memoria perfecta y se estropea solo esa decisión."""
    seleccion, declaraciones = rep.memoria_ejemplar("A")
    incorrecta = next(
        c for c in declaracion.opciones if c != declaracion.correcta
    )
    declaraciones[declaracion.codigo] = incorrecta
    evaluacion = rep.evaluar("A", seleccion, declaraciones)
    assert declaracion.codigo in [h["codigo"] for h in evaluacion["hallazgos"]]
    assert evaluacion["opinion"] != "favorable"


def test_sumar_las_dos_reducciones_es_hallazgo_grave():
    """Es el error que la Sesión 2 dedica un paso entero a desmontar."""
    seleccion, declaraciones = rep.memoria_ejemplar("B")
    declaraciones["reduccion"] = "sumada"
    evaluacion = rep.evaluar("B", seleccion, declaraciones)
    assert evaluacion["opinion"] == "desfavorable"


def test_omitir_la_frontera_es_hallazgo_grave():
    seleccion, declaraciones = rep.memoria_ejemplar("C")
    declaraciones["frontera"] = "no"
    evaluacion = rep.evaluar("C", seleccion, declaraciones)
    assert evaluacion["opinion"] == "desfavorable"


def test_dar_la_tasa_de_reciclaje_es_salvedad():
    """La lección de la Sesión 3, convertida aquí en tentación."""
    seleccion, declaraciones = rep.memoria_ejemplar("E")
    declaraciones["circularidad"] = "reciclaje"
    evaluacion = rep.evaluar("E", seleccion, declaraciones)
    assert evaluacion["opinion"] == "con salvedades"


def test_ninguna_opcion_incorrecta_es_una_mentira_literal():
    """Todas las opciones describen algo que la filial podría publicar sin
    faltar a la verdad. Es la idea entera de la sesión, y por eso el texto
    de cada opción tiene que ser una afirmación, no una trampa evidente."""
    for declaracion in rep.DECLARACIONES:
        for texto in declaracion.opciones.values():
            assert len(texto) > 30
            assert "falso" not in texto.lower()
            assert "mentira" not in texto.lower()


# --------------------------------------------------------------------------
# La revisión
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_memoria_ejemplar_pasa_la_revision(grupo):
    """El ejercicio tiene solución en las cinco filiales."""
    seleccion, declaraciones = rep.memoria_ejemplar(grupo)
    evaluacion = rep.evaluar(grupo, seleccion, declaraciones)
    assert evaluacion["opinion"] == "favorable", evaluacion["hallazgos"]
    assert evaluacion["cobertura"] == 1.0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_memoria_ejemplar_cabe_en_el_limite(grupo):
    seleccion, _ = rep.memoria_ejemplar(grupo)
    assert len(seleccion) <= rep.MAXIMO_INDICADORES


@pytest.mark.parametrize("grupo", GRUPOS)
def test_una_memoria_vacia_es_desfavorable(grupo):
    evaluacion = rep.evaluar(grupo, [], {})
    assert evaluacion["opinion"] == "desfavorable"
    assert evaluacion["cobertura"] == 0.0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_omitir_un_asunto_material_es_grave(grupo):
    seleccion, declaraciones = rep.memoria_ejemplar(grupo)
    evaluacion = rep.evaluar(grupo, seleccion[1:], declaraciones)
    assert evaluacion["opinion"] == "desfavorable"
    assert evaluacion["cobertura"] < 1.0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_publicarlo_todo_no_sale_gratis(grupo):
    """Informar de todo es enterrar lo material, y se avisa."""
    todos = [i.codigo for i in rep.INDICADORES]
    _, declaraciones = rep.memoria_ejemplar(grupo)
    evaluacion = rep.evaluar(grupo, todos, declaraciones)
    assert not evaluacion["dentro_del_limite"]
    assert "exceso" in [h["codigo"] for h in evaluacion["hallazgos"]]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_decidir_las_declaraciones_deja_salvedades(grupo):
    seleccion, _ = rep.memoria_ejemplar(grupo)
    evaluacion = rep.evaluar(grupo, seleccion, {})
    assert evaluacion["salvedades"] >= len(rep.DECLARACIONES)


# --------------------------------------------------------------------------
# La revisión no se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("entrada", [
    ([], {}), (None, None), (["inventado"], {"inventada": "x"}),
    (["e_huella_12", "e_huella_12"], {"reduccion": None}),
])
def test_una_entrada_rara_no_revienta(entrada):
    seleccion, declaraciones = entrada
    evaluacion = rep.evaluar("A", seleccion or [], declaraciones or {})
    assert evaluacion["opinion"] in {"favorable", "con salvedades",
                                     "desfavorable"}
    assert 0.0 <= evaluacion["cobertura"] <= 1.0


def test_los_indicadores_inventados_se_ignoran():
    seleccion, declaraciones = rep.memoria_ejemplar("A")
    evaluacion = rep.evaluar("A", seleccion + ["no_existe"], declaraciones)
    assert "no_existe" not in evaluacion["indicadores"]
    assert evaluacion["opinion"] == "favorable"


# --------------------------------------------------------------------------
# Coherencia con las sesiones anteriores
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_cifras_publicadas_coinciden_con_las_de_su_sesion(grupo):
    """La memoria no puede contradecir lo que vieron en las sesiones 2 y 3."""
    from core import alcance3, circular, palancas
    assert rep.valor(grupo, "e_huella_12") == pytest.approx(
        palancas.linea_base(grupo)["total_t"]
    )
    assert rep.valor(grupo, "e_huella_3") == pytest.approx(
        alcance3.inventario(grupo)["alcance3_t"]
    )
    assert rep.valor(grupo, "e_circularidad") == pytest.approx(
        circular.inventario(grupo)["pct_circularidad"] * 100
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_tasa_de_reciclaje_y_la_circularidad_no_coinciden(grupo):
    """Si coincidieran, la tentación de la Sesión 4 no existiría."""
    assert (rep.valor(grupo, "e_reciclaje")
            > rep.valor(grupo, "e_circularidad") + 10)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_datos_sociales_existen(grupo):
    assert rep.valor(grupo, "s_plantilla") > 0
    assert 0 < rep.valor(grupo, "s_temporalidad") < 100
    assert rep.valor(grupo, "s_accidentes") > 0
