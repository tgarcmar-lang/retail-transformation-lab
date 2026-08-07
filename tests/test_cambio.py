"""Pruebas del modelo de gestión del cambio de la Sesión 7.

Lo que se vigila:

1. **Que exista la brecha.** Si entregar y adoptar dieran lo mismo, la sesión
   no tendría nada que enseñar y el curso se quedaría sin cierre.
2. **Que el mandato se desinfle.** Es la lección: ordenarlo sube rápido y se
   cae, porque nadie ha cambiado de opinión.
3. **Que las máquinas no dependan de la gente y los hábitos sí**, que es lo
   que diferencia el riesgo de unas filiales y otras.
"""

import pytest

from core import cambio as cb, datos, proyecto

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# La brecha entre entregar y adoptar
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_sin_gestionar_el_cambio_se_pierde_valor(grupo):
    """La premisa del curso entero: entregar no es cambiar."""
    resultado = cb.simular(grupo, {})
    assert resultado["brecha"] > 0.25, grupo
    assert resultado["valor_realizado"] < resultado["valor_entregado"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_gestionar_el_cambio_recupera_valor(grupo):
    """Y tiene que compensar, o la sesión enseñaría resignación."""
    sin = cb.simular(grupo, {})
    con = cb.simular(grupo, cb.plan_recomendado())
    assert con["valor_realizado"] > sin["valor_realizado"] * 1.2, grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_nunca_se_recupera_del_todo_gratis(grupo):
    """El plan que lo arregla todo no cabe en el presupuesto."""
    assert not cb.simular(grupo, cb.plan_recomendado())["dentro_de_presupuesto"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_comprarlo_todo_cuesta_mas_del_doble(grupo):
    todo = {p.codigo: 1.0 for p in cb.PALANCAS}
    assert cb.coste(todo, grupo) > cb.presupuesto(grupo) * 2


# --------------------------------------------------------------------------
# El mandato
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_mandato_se_desinfla(grupo):
    """Sube deprisa y se cae: nadie ha cambiado de opinión."""
    resultado = cb.simular(grupo, cb.plan_de_mandato())
    assert resultado["se_desinfla"], grupo
    assert resultado["mes_del_maximo"] <= 4
    assert resultado["adopcion_final"] < resultado["adopcion_maxima"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_participacion_no_se_desinfla(grupo):
    resultado = cb.simular(grupo, {"participacion": 1.0})
    assert not resultado["se_desinfla"], grupo


def test_el_mandato_es_lo_mas_barato():
    """Por eso es lo que se hace casi siempre."""
    precios = {p.codigo: p.coste_relativo for p in cb.PALANCAS}
    assert min(precios, key=precios.get) == "mandato"


def test_la_participacion_es_la_mas_lenta_y_la_que_mas_aguanta():
    participacion = cb.POR_CODIGO["participacion"]
    mandato = cb.POR_CODIGO["mandato"]
    assert participacion.velocidad < mandato.velocidad
    assert participacion.decaimiento < mandato.decaimiento
    assert participacion.techo > mandato.techo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_a_largo_plazo_participar_gana_a_ordenar(grupo):
    """Con el mismo dinero, si se puede pagar."""
    mandato = cb.simular(grupo, cb.plan_de_mandato())
    participar = cb.simular(grupo, {"participacion": 1.0, "comunicacion": 1.0})
    assert participar["adopcion_final"] > mandato["adopcion_final"], grupo


# --------------------------------------------------------------------------
# Máquinas y hábitos
# --------------------------------------------------------------------------

def test_las_obras_no_dependen_de_la_gente():
    for codigo in ("c_refrigerante", "c_energia"):
        assert cb.CONDUCTA[codigo][0] <= 0.15, codigo


def test_los_cambios_de_habito_si():
    for codigo in ("c_consolidacion", "m_segregacion", "m_merma"):
        assert cb.CONDUCTA[codigo][0] >= 0.65, codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_toda_iniciativa_del_backlog_esta_clasificada(grupo):
    """Si falta una, el modelo la trataría con un valor por defecto."""
    for iniciativa in proyecto.backlog(grupo):
        assert iniciativa.codigo in cb.CONDUCTA, iniciativa.codigo


def test_toda_clasificacion_esta_razonada():
    for codigo, (dependencia, roles, porque) in cb.CONDUCTA.items():
        assert 0.0 <= dependencia <= 1.0, codigo
        assert roles, codigo
        assert len(porque) > 40, codigo
        for rol in roles:
            assert rol in cb.POR_ROL, (codigo, rol)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_una_parte_grande_del_plan_depende_de_las_personas(grupo):
    exposicion = cb.exposicion(grupo)
    assert 0.25 < exposicion["pct_conductual"] < 0.75, grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_lo_que_mas_se_pierde_es_lo_mas_conductual(grupo):
    resultado = cb.simular(grupo, {})
    primero = resultado["detalle"][0]
    ultimo = resultado["detalle"][-1]
    assert primero["dependencia"] >= ultimo["dependencia"], grupo


# --------------------------------------------------------------------------
# El mapa de actores
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_mapa_cubre_todos_los_roles(grupo):
    tabla = cb.mapa_de_actores(grupo)
    assert len(tabla) == len(cb.ROLES)
    assert tabla["impacto"].between(1, 5).all()
    assert tabla["poder"].between(1, 5).all()


@pytest.mark.parametrize("grupo", GRUPOS)
def test_quien_mas_carga_lleva_no_es_quien_mas_poder_tiene(grupo):
    """El patrón que sostiene la sesión."""
    tabla = cb.mapa_de_actores(grupo).sort_values("impacto", ascending=False)
    mas_afectado = tabla.iloc[0]
    mas_poderoso = tabla.sort_values("poder", ascending=False).iloc[0]
    assert mas_afectado["rol"] != mas_poderoso["rol"] or \
        mas_afectado["poder"] < 5, grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_personal_de_tienda_es_el_mas_numeroso(grupo):
    tabla = cb.mapa_de_actores(grupo).set_index("rol")
    assert tabla.loc["personal_tienda", "empleados"] == tabla["empleados"].max()


def test_todo_rol_esta_explicado():
    for rol in cb.ROLES:
        assert len(rol.descripcion) > 40, rol.codigo
        assert 0 < rol.peso <= 1
        assert 1 <= rol.poder <= 5


def test_los_pesos_de_los_roles_suman_uno():
    assert sum(rol.peso for rol in cb.ROLES) == pytest.approx(1.0, abs=0.01)


# --------------------------------------------------------------------------
# La curva
# --------------------------------------------------------------------------

def test_sin_hacer_nada_la_adopcion_es_la_inercial():
    assert cb.curva({}, 1) == pytest.approx(cb.ADOPCION_INERCIAL)
    assert cb.curva({}, cb.MESES) == pytest.approx(cb.ADOPCION_INERCIAL)


def test_la_adopcion_nunca_se_sale_de_rango():
    todo = {p.codigo: 1.0 for p in cb.PALANCAS}
    for mes in range(1, cb.MESES + 1):
        assert 0.0 <= cb.curva(todo, mes) <= 1.0
        assert 0.0 <= cb.curva({}, mes) <= 1.0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_historia_cubre_los_doce_meses(grupo):
    resultado = cb.simular(grupo, cb.plan_recomendado())
    assert len(resultado["historia"]) == cb.MESES
    assert resultado["historia"][0]["mes"] == 1


# --------------------------------------------------------------------------
# No se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    {}, {"inventada": 1.0}, {"mandato": -3}, {"participacion": 99},
    {"comunicacion": None},
])
def test_un_plan_raro_no_revienta(plan):
    resultado = cb.simular("A", plan)
    assert 0.0 <= resultado["adopcion_final"] <= 1.0
    assert resultado["valor_realizado"] >= 0
    assert 0.0 <= resultado["brecha"] <= 1.0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_mas_intensidad_nunca_adopta_menos(grupo):
    for palanca in cb.PALANCAS:
        if palanca.decaimiento > 0.3:
            continue  # el mandato sí puede terminar peor: es la lección
        media = cb.simular(grupo, {palanca.codigo: 0.5})["adopcion_final"]
        entera = cb.simular(grupo, {palanca.codigo: 1.0})["adopcion_final"]
        assert entera >= media - 1e-6, palanca.codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_documento_de_cierre_se_genera(grupo):
    from core import plan_cambio
    resultado = cb.simular(grupo, cb.plan_recomendado())
    documento = plan_cambio.generar(
        grupo, resultado, cb.plan_recomendado(), {}, "Equipo"
    )
    assert "Plan de gestión del cambio" in documento
    assert "El curso, en una página" in documento
    assert documento.count("Sin responder.") == len(plan_cambio.PREGUNTAS)


def test_el_documento_escapa_el_html_del_alumno():
    from core import plan_cambio
    resultado = cb.simular("A", {})
    documento = plan_cambio.generar(
        "A", resultado, {}, {"curso": "<script>malo()</script>"}
    )
    assert "<script>malo()</script>" not in documento
    assert "&lt;script&gt;" in documento
