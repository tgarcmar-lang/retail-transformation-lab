"""Pruebas del motor de flujo de la Sesión 6.

Lo que se vigila es que la lección se sostenga, y aquí la lección tiene dos
mitades que se contradicen aparentemente:

1. **Abrir muchas cosas a la vez entrega menos.** Si esto no se cumpliera,
   limitar el WIP sería una superstición.
2. **Abrir una sola tampoco es la respuesta.** Con una tarea abierta, el
   equipo se para cada vez que esa tarea espera a un tercero. Si el óptimo
   cayera en el mínimo, la sesión enseñaría una simplificación falsa.

Y una tercera: **la ley de Little tiene que cumplirse** sobre los propios
números, o el alumno tendrá razón al desconfiar de ella.
"""

import pytest

from core import datos, kanban as kb, proyecto

GRUPOS = ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="module", autouse=True)
def datos_limpios():
    datos.limpiar_cache()
    yield
    datos.limpiar_cache()


# --------------------------------------------------------------------------
# El óptimo está en medio
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_optimo_de_wip_no_esta_en_los_extremos(grupo):
    """Es la idea entera de la sesión.

    Si el óptimo fuese 1, la lección sería «haz una cosa cada vez», que es
    falso y además nadie puede aplicarlo. Si fuese el máximo, limitar el WIP
    no serviría para nada.
    """
    optimo = kb.wip_optimo(grupo)
    assert optimo > min(kb.LIMITES_OFRECIDOS), grupo
    assert optimo < max(kb.LIMITES_OFRECIDOS), grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_una_sola_tarea_abierta_el_equipo_se_para(grupo):
    """Porque cuando esa tarea espera a un tercero, no hay nada más."""
    minimo = kb.simular_flujo(grupo, 1)
    optimo = kb.simular_flujo(grupo, kb.wip_optimo(grupo))
    assert minimo["valor_entregado"] < optimo["valor_entregado"], grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_demasiadas_abiertas_no_se_termina_nada(grupo):
    maximo = kb.simular_flujo(grupo, max(kb.LIMITES_OFRECIDOS))
    optimo = kb.simular_flujo(grupo, kb.wip_optimo(grupo))
    assert maximo["valor_entregado"] < optimo["valor_entregado"], grupo


def test_el_optimo_no_es_el_mismo_en_todas_las_filiales():
    """Si lo fuera, bastaría con aprenderse un número."""
    optimos = {g: kb.wip_optimo(g) for g in GRUPOS}
    assert len(set(optimos.values())) >= 2, optimos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_barrido_cubre_todos_los_limites(grupo):
    tabla = kb.barrido_wip(grupo)
    assert list(tabla["limite_wip"]) == kb.LIMITES_OFRECIDOS
    assert (tabla["terminadas"] >= 0).all()


# --------------------------------------------------------------------------
# El tiempo de ciclo
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_mas_trabajo_en_curso_alarga_el_tiempo_de_ciclo(grupo):
    """La consecuencia directa de la ley de Little."""
    tabla = kb.barrido_wip(grupo)
    ciclos = list(tabla["tiempo_de_ciclo"])
    # Se admite un ruido pequeño: el sistema es discreto y de doce semanas.
    for anterior, siguiente in zip(ciclos, ciclos[1:]):
        assert siguiente >= anterior - 0.35, ciclos
    assert ciclos[-1] > ciclos[0] * 1.5, grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_ley_de_little_se_cumple_en_el_optimo(grupo):
    """Con el sistema razonablemente estable, la identidad se sostiene."""
    resultado = kb.simular_flujo(grupo, kb.wip_optimo(grupo))
    little = kb.ley_de_little(resultado)
    assert little["desviacion"] < 0.25, (grupo, little)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_ley_de_little_devuelve_todo_lo_que_hace_falta(grupo):
    little = kb.ley_de_little(kb.simular_flujo(grupo, 4))
    for clave in ("wip_medio", "throughput", "ciclo_previsto", "ciclo_real"):
        assert little[clave] >= 0


# --------------------------------------------------------------------------
# La multitarea
# --------------------------------------------------------------------------

def test_la_eficiencia_baja_al_abrir_mas_tareas():
    valores = [kb.eficiencia(w) for w in range(1, 12)]
    assert valores[0] == 1.0
    for anterior, siguiente in zip(valores, valores[1:]):
        assert siguiente <= anterior
    assert min(valores) >= kb.EFICIENCIA_MINIMA


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_eficiencia_media_cae_con_el_limite(grupo):
    tabla = kb.barrido_wip(grupo)
    eficiencias = list(tabla["eficiencia_media"])
    assert eficiencias[0] > eficiencias[-1]


# --------------------------------------------------------------------------
# El tablero
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_toda_iniciativa_esta_en_alguna_columna(grupo):
    resultado = kb.simular_flujo(grupo, 4)
    tabla = kb.tabla_tablero(grupo, resultado)
    assert len(tabla) == len(proyecto.backlog(grupo))
    assert set(tabla["estado"]) <= {"Pendiente", "En curso", "Hecho"}


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_flujo_acumulado_es_coherente(grupo):
    resultado = kb.simular_flujo(grupo, 4)
    total = len(proyecto.backlog(grupo))
    for semana in resultado["historia"]:
        suma = (semana["pendiente"] + semana["en_curso"]
                + semana["bloqueado"] + semana["hecho"])
        assert suma <= total
        assert semana["wip"] <= resultado["limite_wip"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_lo_hecho_nunca_disminuye(grupo):
    resultado = kb.simular_flujo(grupo, 4)
    hechas = [s["hecho"] for s in resultado["historia"]]
    assert hechas == sorted(hechas)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_hay_semanas_con_trabajo_bloqueado(grupo):
    """Si nada se bloqueara nunca, el mínimo de WIP sería siempre el óptimo."""
    resultado = kb.simular_flujo(grupo, 4)
    assert any(s["bloqueado"] > 0 for s in resultado["historia"]), grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_obras_esperan_mas_que_los_programas(grupo):
    assert (kb.BLOQUEO["Predictivo"]["semanas"]
            > kb.BLOQUEO["Iterativo"]["semanas"])


# --------------------------------------------------------------------------
# El sistema híbrido
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_reparto_recomendado_manda_lo_iterativo_al_tablero(grupo):
    catalogo = proyecto.por_codigo(grupo)
    for codigo in kb.reparto_recomendado(grupo):
        assert catalogo[codigo].enfoque == "Iterativo"


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_reparto_recomendado_no_deja_avisos(grupo):
    """Es el reparto que haría un buen jefe de proyecto: sin errores."""
    evaluacion = kb.evaluar_hibrido(
        grupo, kb.reparto_recomendado(grupo), kb.wip_optimo(grupo)
    )
    assert not evaluacion["obras_en_flujo"]
    assert not evaluacion["iterativas_con_fecha"]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_meter_obras_en_el_tablero_se_detecta(grupo):
    catalogo = proyecto.por_codigo(grupo)
    todas = list(catalogo)
    evaluacion = kb.evaluar_hibrido(grupo, todas, 4)
    assert evaluacion["obras_en_flujo"], grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_poner_fecha_a_lo_iterativo_se_detecta(grupo):
    evaluacion = kb.evaluar_hibrido(grupo, [], 4)
    assert evaluacion["iterativas_con_fecha"], grupo


@pytest.mark.parametrize("grupo", GRUPOS)
def test_las_dos_mitades_se_miden_distinto(grupo):
    """El flujo por tiempo de ciclo; los hitos, por puntualidad."""
    evaluacion = kb.evaluar_hibrido(
        grupo, kb.reparto_recomendado(grupo), kb.wip_optimo(grupo)
    )
    assert "tiempo_de_ciclo" in evaluacion["flujo"]
    assert 0.0 <= evaluacion["puntualidad"] <= 1.0
    assert (len(evaluacion["en_flujo"]) + len(evaluacion["con_fecha"])
            == len(proyecto.backlog(grupo)))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_compromiso_de_fecha_es_razonable(grupo):
    catalogo = proyecto.por_codigo(grupo)
    predictivas = [c for c, i in catalogo.items() if i.enfoque == "Predictivo"]
    for codigo in predictivas:
        semanas = kb.compromiso(grupo, codigo)
        assert semanas > 0
        assert semanas >= kb.BLOQUEO["Predictivo"]["semanas"]


# --------------------------------------------------------------------------
# El simulador no se rompe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("limite", [0, -3, None, 1, 99])
def test_un_limite_raro_no_revienta(limite):
    resultado = kb.simular_flujo("A", limite)
    assert resultado["limite_wip"] >= 1
    assert len(resultado["historia"]) == kb.SEMANAS


@pytest.mark.parametrize("orden", [[], ["inventada"], None])
def test_un_orden_raro_no_revienta(orden):
    resultado = kb.simular_flujo("A", 4, orden=orden)
    assert resultado["valor_entregado"] >= 0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_el_tablero_vacio_no_se_entrega_nada(grupo):
    resultado = kb.simular_flujo(grupo, 4, orden=[])
    assert resultado["terminadas"] == []
    assert resultado["valor_entregado"] == 0


@pytest.mark.parametrize("grupo", GRUPOS)
def test_no_se_respeta_menos_de_lo_pedido(grupo):
    """El límite de WIP es un límite: no se puede superar nunca."""
    for limite in kb.LIMITES_OFRECIDOS:
        resultado = kb.simular_flujo(grupo, limite)
        for semana in resultado["historia"]:
            assert semana["wip"] <= limite


@pytest.mark.parametrize("grupo", GRUPOS)
def test_nadie_termina_lo_que_no_ha_empezado(grupo):
    resultado = kb.simular_flujo(grupo, 4)
    for codigo in resultado["terminadas"]:
        assert codigo in resultado["entrada"]
        assert resultado["salida"][codigo] >= resultado["entrada"][codigo]


@pytest.mark.parametrize("grupo", GRUPOS)
def test_se_respetan_las_dependencias(grupo):
    resultado = kb.simular_flujo(grupo, 6)
    catalogo = proyecto.por_codigo(grupo)
    for codigo in resultado["terminadas"]:
        for dependencia in catalogo[codigo].depende_de:
            assert dependencia in resultado["salida"], codigo
            assert (resultado["salida"][dependencia]
                    <= resultado["entrada"][codigo])


# --------------------------------------------------------------------------
# Coherencia con la Sesión 5
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_es_el_mismo_proyecto_que_en_la_sesion_5(grupo):
    resultado = kb.simular_flujo(grupo, 4)
    assert resultado["valor_total"] == sum(
        i.valor for i in proyecto.backlog(grupo)
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_capacidad_semanal_es_la_mitad_de_la_del_sprint(grupo):
    assert kb.capacidad_semanal(grupo) == pytest.approx(
        proyecto.capacidad(grupo) / kb.SEMANAS_POR_SPRINT, abs=0.01
    )


def test_hay_cuatro_columnas_explicadas():
    assert len(kb.COLUMNAS) == 4
    for columna in kb.COLUMNAS:
        assert len(columna.explicacion) > 30
