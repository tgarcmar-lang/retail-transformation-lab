"""Pruebas del motor de ejecución de la Sesión 5.

Lo que se vigila:

1. **Que el backlog salga de los datos** y no esté escrito a mano. Si alguien
   recalibra una palanca, el esfuerzo de la iniciativa tiene que moverse con
   ella.
2. **Que priorizar bien se note.** Si ordenar por valor y ordenar por tamaño
   dieran lo mismo, la sesión no enseñaría nada.
3. **Que no quepa todo.** Es la premisa del ejercicio: si cupiera, no habría
   que elegir.
4. **Que los contratiempos duelan**, y que cada filial tenga el suyo.
"""

import pytest

from core import circular, datos, palancas, proyecto as pj

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# El backlog sale de las sesiones anteriores
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_backlog_viene_de_las_palancas(grupo):
    """Ninguna cifra escrita a mano: es la regla dura del proyecto."""
    codigos = {i.codigo for i in pj.backlog(grupo)}
    for fila in palancas.coste_por_tonelada(grupo):
        if fila["coste_eur"] > 0:
            assert f"c_{fila['codigo']}" in codigos
    for fila in circular.coste_por_tonelada(grupo):
        if fila["coste_eur"] > 0:
            assert f"m_{fila['codigo']}" in codigos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_esfuerzo_sigue_al_coste_de_la_palanca(grupo):
    catalogo = pj.por_codigo(grupo)
    for fila in palancas.coste_por_tonelada(grupo):
        if fila["coste_eur"] <= 0:
            continue
        iniciativa = catalogo[f"c_{fila['codigo']}"]
        assert iniciativa.esfuerzo == max(
            1, round(fila["coste_eur"] / pj.EUROS_POR_PUNTO)
        )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_toda_iniciativa_tiene_esfuerzo_y_valor(grupo):
    for iniciativa in pj.backlog(grupo):
        assert iniciativa.esfuerzo >= 1
        assert 1 <= iniciativa.valor <= 10
        assert iniciativa.enfoque in {"Predictivo", "Iterativo"}
        assert len(iniciativa.porque) > 30


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_backlog_incluye_lo_que_no_reduce_nada(grupo):
    """El sistema de medición no evita una tonelada y sin él no hay memoria.

    Es la iniciativa que todos los grupos quieren quitar, y la que hace que
    la Sesión 4 sea posible.
    """
    codigos = {i.codigo for i in pj.backlog(grupo)}
    assert "r_medicion" in codigos
    assert "r_proveedores_esg" in codigos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_hay_una_dependencia_de_verdad(grupo):
    catalogo = pj.por_codigo(grupo)
    assert catalogo["r_proveedores_esg"].depende_de == ("r_medicion",)


# --------------------------------------------------------------------------
# Predictivo e iterativo
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_backlog_mezcla_los_dos_enfoques(grupo):
    """Si todo fuera de un tipo, la sesión no tendría nada que enseñar."""
    enfoques = {i.enfoque for i in pj.backlog(grupo)}
    assert enfoques == {"Predictivo", "Iterativo"}


@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_obras_son_predictivas(grupo):
    """Cambiar un refrigerante o poner placas es una obra, no un sprint."""
    catalogo = pj.por_codigo(grupo)
    for codigo in ("c_refrigerante", "c_energia", "c_electrificacion"):
        if codigo in catalogo:
            assert catalogo[codigo].enfoque == "Predictivo", codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_programas_con_terceros_son_iterativos(grupo):
    catalogo = pj.por_codigo(grupo)
    for codigo in ("c_consolidacion", "m_segregacion", "m_embalaje",
                   "r_proveedores_esg"):
        if codigo in catalogo:
            assert catalogo[codigo].enfoque == "Iterativo", codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_lo_predictivo_pesa_pero_no_lo_es_todo(grupo):
    resumen = pj.resumen(grupo)
    assert 0.3 < resumen["pct_predictivo"] < 0.95


# --------------------------------------------------------------------------
# La premisa: no cabe todo
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_cabe_todo_en_los_seis_sprints(grupo):
    """Es la premisa del ejercicio. Si cupiera, no habría que priorizar."""
    resumen = pj.resumen(grupo)
    assert not resumen["cabe_todo"], grupo
    assert resumen["sprints_necesarios"] > pj.SPRINTS


@pytest.mark.parametrize("grupo", GRUPOS)
def test_pero_falta_poco_para_que_quepa(grupo):
    """Si faltara mucho, el grupo se rendiría en vez de decidir."""
    resumen = pj.resumen(grupo)
    assert resumen["sprints_necesarios"] < pj.SPRINTS * 2


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_capacidad_es_positiva_y_razonable(grupo):
    capacidad = pj.capacidad(grupo)
    mayor = max(i.esfuerzo for i in pj.backlog(grupo))
    assert capacidad > 0
    # Ninguna iniciativa puede ser tan grande que no quepa ni en todo el
    # proyecto: sería imposible de entregar y frustrante sin enseñar nada.
    assert mayor < capacidad * pj.SPRINTS


# --------------------------------------------------------------------------
# Priorizar bien se nota
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_priorizar_por_valor_entrega_mas_que_por_tamano(grupo):
    """La lección de la sesión, verificada en las cinco filiales."""
    por_valor = pj.simular(grupo, pj.plan_por_valor(grupo))
    por_tamano = pj.simular(grupo, pj.plan_por_tamano(grupo))
    assert por_valor["valor_entregado"] > por_tamano["valor_entregado"], grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_empezar_por_lo_grande_no_entrega_nada_pronto(grupo):
    """Lo grande parece lo importante y casi nunca lo es."""
    por_tamano = pj.simular(grupo, pj.plan_por_tamano(grupo))
    por_valor = pj.simular(grupo, pj.plan_por_valor(grupo))
    assert por_tamano["valor_en_sprint_3"] < por_valor["valor_en_sprint_3"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_un_buen_plan_entrega_la_mayor_parte_del_valor(grupo):
    """Tiene que ser posible hacerlo bien, o el ejercicio desanima."""
    por_valor = pj.simular(grupo, pj.plan_por_valor(grupo))
    assert por_valor["pct_valor"] > 0.7, grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_pero_nadie_entrega_el_backlog_completo(grupo):
    por_valor = pj.simular(grupo, pj.plan_por_valor(grupo))
    assert por_valor["sin_entregar"], grupo


# --------------------------------------------------------------------------
# Las iniciativas grandes ocupan varios sprints
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_una_iniciativa_mayor_que_un_sprint_se_puede_entregar(grupo):
    """Se avanza entre sprints. Sin esto, lo grande sería inejecutable."""
    catalogo = pj.por_codigo(grupo)
    capacidad = pj.capacidad(grupo)
    grandes = [c for c, i in catalogo.items() if i.esfuerzo > capacidad]
    if not grandes:
        pytest.skip("Esta filial no tiene iniciativas mayores que un sprint")
    codigo = grandes[0]
    plan = {1: [codigo]}
    resultado = pj.simular(grupo, plan, con_eventos=False)
    assert codigo in resultado["entregadas"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_lo_empezado_y_no_terminado_no_entrega_valor(grupo):
    """Es la forma más cara de gastar un presupuesto, y hay que poder verlo."""
    catalogo = pj.por_codigo(grupo)
    capacidad = pj.capacidad(grupo)
    grandes = [c for c, i in catalogo.items() if i.esfuerzo > capacidad]
    if not grandes:
        pytest.skip("Esta filial no tiene iniciativas mayores que un sprint")
    codigo = grandes[0]
    resultado = pj.simular(grupo, {pj.SPRINTS: [codigo]}, con_eventos=False)
    assert codigo not in resultado["entregadas"]
    assert resultado["progreso"].get(codigo, 0) > 0
    assert resultado["valor_entregado"] == 0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_una_dependencia_sin_cumplir_bloquea(grupo):
    resultado = pj.simular(grupo, {1: ["r_proveedores_esg"]},
                           con_eventos=False)
    assert "r_proveedores_esg" not in resultado["entregadas"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_la_dependencia_cumplida_se_entrega(grupo):
    plan = {1: ["r_medicion"], 2: ["r_proveedores_esg"]}
    resultado = pj.simular(grupo, plan, con_eventos=False)
    assert "r_medicion" in resultado["entregadas"]
    assert "r_proveedores_esg" in resultado["entregadas"]


# --------------------------------------------------------------------------
# Los contratiempos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_cada_filial_tiene_sus_propios_contratiempos(grupo):
    eventos = pj.eventos(grupo)
    assert len(eventos) >= 2
    for evento in eventos:
        assert 1 <= evento.sprint <= pj.SPRINTS
        assert evento.efecto in {"bloquea", "encarece", "recorta_capacidad"}
        assert len(evento.relato) > 40
        assert len(evento.leccion) > 30


def test_los_contratiempos_no_se_repiten_entre_filiales():
    """Si fueran los mismos, la puesta en común perdería sentido."""
    titulos = [e.titulo for g in GRUPOS for e in pj.eventos(g)]
    assert len(titulos) == len(set(titulos))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_contratiempos_apuntan_a_iniciativas_que_existen(grupo):
    catalogo = pj.por_codigo(grupo)
    for evento in pj.eventos(grupo):
        if evento.objetivo:
            assert evento.objetivo in catalogo, evento.codigo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_los_contratiempos_hacen_dano(grupo):
    """Si no cambiaran el resultado, no habría nada que replanificar."""
    plan = pj.plan_por_valor(grupo)
    con = pj.simular(grupo, plan, con_eventos=True)
    sin = pj.simular(grupo, plan, con_eventos=False)
    assert con["valor_entregado"] <= sin["valor_entregado"]


def test_a_madrid_se_le_retrasa_la_recogida_en_tienda():
    """Es la iniciativa que cerraba su hallazgo de la Sesión 1."""
    codigos = [e.objetivo for e in pj.eventos("A")]
    assert "c_consolidacion" in codigos


def test_a_valencia_se_le_retrasa_el_refrigerante():
    """Su iniciativa más rentable es también la más rígida."""
    codigos = [e.objetivo for e in pj.eventos("C")]
    assert "c_refrigerante" in codigos


def test_a_barcelona_le_falla_la_cadena_de_proveedores():
    codigos = [e.objetivo for e in pj.eventos("B")]
    assert "r_proveedores_esg" in codigos


# --------------------------------------------------------------------------
# El simulador no se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    {}, {1: []}, {1: ["inventada"]}, {0: ["c_energia"]},
    {1: None}, {99: ["c_energia"]}, {1: ["c_energia", "c_energia"]},
])
def test_un_plan_raro_no_revienta(plan):
    resultado = pj.simular("A", plan)
    assert resultado["valor_entregado"] >= 0
    assert 0 <= resultado["pct_valor"] <= 1
    assert len(resultado["detalle"]) == pj.SPRINTS


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_hacer_nada_no_entrega_nada(grupo):
    resultado = pj.simular(grupo, {})
    assert resultado["valor_entregado"] == 0
    assert resultado["entregadas"] == []


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_valor_acumulado_no_baja_nunca(grupo):
    resultado = pj.simular(grupo, pj.plan_por_valor(grupo))
    acumulados = [s["valor_acumulado"] for s in resultado["detalle"]]
    assert acumulados == sorted(acumulados)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_se_gasta_mas_capacidad_de_la_que_hay(grupo):
    resultado = pj.simular(grupo, pj.plan_por_valor(grupo))
    for sprint in resultado["detalle"]:
        assert sprint["usada"] <= sprint["capacidad"] + 1e-6


@pytest.mark.parametrize("grupo", GRUPOS)
def test_nadie_entrega_dos_veces_lo_mismo(grupo):
    resultado = pj.simular(grupo, pj.plan_por_valor(grupo))
    entregadas = [c for s in resultado["detalle"] for c in s["entregadas"]]
    assert len(entregadas) == len(set(entregadas))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_tabla_del_backlog_se_construye(grupo):
    tabla = pj.tabla_backlog(grupo)
    assert len(tabla) == len(pj.backlog(grupo))
    assert tabla["valor_por_punto"].is_monotonic_decreasing
