"""Recorrido completo de la Sesión 6, con la aplicación de verdad."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import filiales, informe_seguimiento, kanban

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
GRUPOS = ["A", "B", "C", "D", "E"]
ESPERA = 120


def _entrar(grupo: str, paso: int = 0, wip: int | None = None,
            flujo: list | None = None) -> AppTest:
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    filial = filiales.obtener(grupo)
    prueba.sidebar.selectbox[0].set_value(f"Grupo {grupo} — {filial.nombre}").run()
    prueba.session_state["vista"] = "sesion6"
    prueba.session_state["paso6"] = paso
    if wip is not None:
        prueba.session_state["wip6"] = wip
    if flujo is not None:
        prueba.session_state["flujo6"] = flujo
    prueba.run()
    return prueba


# --------------------------------------------------------------------------
# La sesión carga
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
@pytest.mark.parametrize("paso", [0, 1, 2, 3])
def test_cada_paso_carga_sin_errores(grupo, paso):
    prueba = _entrar(grupo, paso)
    assert not prueba.exception, f"Paso {paso + 1} roto en el grupo {grupo}"


def test_la_sesion_seis_esta_desbloqueada():
    from core import sesiones
    assert sesiones.SESIONES[5].disponible


def test_se_entra_desde_la_portada():
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    boton = [b for b in prueba.button if "Sesión 6" in b.label]
    assert boton
    boton[0].click().run()
    assert not prueba.exception
    assert prueba.session_state["vista"] == "sesion6"


# --------------------------------------------------------------------------
# El tablero
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_explica_las_cuatro_columnas(grupo):
    prueba = _entrar(grupo, 0)
    textos = " ".join(m.value for m in prueba.markdown)
    for columna in kanban.COLUMNAS:
        assert columna.nombre in textos


def test_el_primer_paso_avisa_de_que_lo_bloqueado_ocupa_sitio():
    """Es lo que hace que el mínimo de WIP no sea la respuesta."""
    prueba = _entrar("A", 0)
    textos = " ".join(i.value for i in prueba.info)
    assert "ocupa sitio" in textos


# --------------------------------------------------------------------------
# El límite de WIP
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_segundo_paso_ofrece_el_control_de_wip(grupo):
    prueba = _entrar(grupo, 1)
    assert prueba.get("select_slider")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_el_optimo_se_felicita(grupo):
    prueba = _entrar(grupo, 1, wip=kanban.wip_optimo(grupo))
    assert any("óptimo" in s.value for s in prueba.success)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_wip_de_uno_se_avisa_de_que_el_equipo_se_para(grupo):
    prueba = _entrar(grupo, 1, wip=1)
    assert any("se queda parado" in w.value for w in prueba.warning)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_wip_alto_se_avisa_de_la_multitarea(grupo):
    prueba = _entrar(grupo, 1, wip=10)
    assert any("no termina" in e.value for e in prueba.error)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_segundo_paso_muestra_los_indicadores(grupo):
    prueba = _entrar(grupo, 1)
    etiquetas = [m.label for m in prueba.metric]
    assert "Tiempo de ciclo medio" in etiquetas
    assert "Eficiencia del equipo" in etiquetas


# --------------------------------------------------------------------------
# El sistema híbrido
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_tercer_paso_ofrece_repartir_el_backlog(grupo):
    from core import proyecto
    prueba = _entrar(grupo, 2)
    assert len(prueba.checkbox) == len(proyecto.backlog(grupo))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_meter_todo_en_el_tablero_se_reprocha(grupo):
    from core import proyecto
    todas = [i.codigo for i in proyecto.backlog(grupo)]
    prueba = _entrar(grupo, 2, flujo=todas)
    assert any("obras en el tablero" in e.value.lower() for e in prueba.error)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_reparto_recomendado_se_aprueba(grupo):
    prueba = _entrar(grupo, 2, flujo=kanban.reparto_recomendado(grupo))
    assert any("coherente" in s.value for s in prueba.success)


# --------------------------------------------------------------------------
# El seguimiento
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_cuarto_paso_pinta_el_flujo_acumulado(grupo):
    prueba = _entrar(grupo, 3)
    assert not prueba.exception
    etiquetas = [m.label for m in prueba.metric]
    assert "Tiempo de ciclo" in etiquetas
    assert "Trabajo en curso medio" in etiquetas


def test_el_cuarto_paso_explica_como_se_lee_el_diagrama():
    prueba = _entrar("A", 3)
    textos = " ".join(i.value for i in prueba.info)
    assert "engorda" in textos


# --------------------------------------------------------------------------
# El informe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_informe_se_puede_descargar(grupo):
    prueba = _entrar(grupo, 3)
    assert prueba.get("download_button")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_informe_lleva_el_nombre_de_la_filial(grupo):
    resultado = kanban.simular_flujo(grupo, kanban.wip_optimo(grupo))
    documento = informe_seguimiento.generar(
        grupo, resultado, None, {}, "Equipo de prueba"
    )
    assert filiales.obtener(grupo).nombre in documento
    assert "Equipo de prueba" in documento


def test_el_informe_incluye_la_ley_de_little():
    resultado = kanban.simular_flujo("B", 4)
    documento = informe_seguimiento.generar("B", resultado, None, {})
    assert "ley de Little" in documento
    assert "empezar menos" in documento


def test_el_informe_mide_las_dos_mitades_del_hibrido():
    grupo = "D"
    evaluacion = kanban.evaluar_hibrido(
        grupo, kanban.reparto_recomendado(grupo), kanban.wip_optimo(grupo)
    )
    resultado = kanban.simular_flujo(grupo, kanban.wip_optimo(grupo))
    documento = informe_seguimiento.generar(grupo, resultado, evaluacion, {})
    assert "sistema híbrido" in documento
    assert "Puntualidad de hitos" in documento


def test_el_informe_dice_si_el_limite_elegido_era_el_bueno():
    grupo = "C"
    malo = kanban.simular_flujo(grupo, 10)
    documento = informe_seguimiento.generar(grupo, malo, None, {})
    assert "no es el que más" in documento


def test_el_informe_marca_lo_que_no_se_ha_respondido():
    resultado = kanban.simular_flujo("A", 4)
    documento = informe_seguimiento.generar("A", resultado, None, {})
    assert documento.count("Sin responder.") == len(
        informe_seguimiento.PREGUNTAS
    )


def test_el_informe_escapa_el_html_del_alumno():
    resultado = kanban.simular_flujo("A", 4)
    documento = informe_seguimiento.generar(
        "A", resultado, None, {"mejora": "<script>malo()</script>"}
    )
    assert "<script>malo()</script>" not in documento
    assert "&lt;script&gt;" in documento


def test_el_informe_es_html_bien_formado():
    from html.parser import HTMLParser

    class Comprobador(HTMLParser):
        vacias = {"meta", "br", "hr", "img", "input", "link"}

        def __init__(self):
            super().__init__()
            self.pila = []
            self.desajustes = []

        def handle_starttag(self, etiqueta, atributos):
            if etiqueta not in self.vacias:
                self.pila.append(etiqueta)

        def handle_endtag(self, etiqueta):
            if self.pila and self.pila[-1] == etiqueta:
                self.pila.pop()
            else:
                self.desajustes.append(etiqueta)

    grupo = "E"
    evaluacion = kanban.evaluar_hibrido(
        grupo, kanban.reparto_recomendado(grupo), 4
    )
    comprobador = Comprobador()
    comprobador.feed(informe_seguimiento.generar(
        grupo, kanban.simular_flujo(grupo, 4), evaluacion, {}
    ))
    assert not comprobador.pila
    assert not comprobador.desajustes


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_nombre_del_fichero_identifica_al_grupo(grupo):
    nombre = informe_seguimiento.nombre_de_fichero(grupo)
    assert nombre.endswith(".html")
    assert f"grupo{grupo}" in nombre
    assert "seguimiento" in nombre


# --------------------------------------------------------------------------
# Convivencia con las otras sesiones
# --------------------------------------------------------------------------

def test_cambiar_de_grupo_descarta_el_tablero():
    prueba = _entrar("D", 1, wip=8)
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    assert "wip6" not in prueba.session_state or \
        prueba.session_state["wip6"] != 8
    assert prueba.session_state["paso6"] == 0


def test_las_respuestas_de_las_seis_sesiones_no_se_mezclan():
    prueba = _entrar("C", 0)
    prueba.text_area[0].set_value("Hay demasiado en curso.").run()
    assert prueba.session_state["respuestas6"]["tablero"] == \
        "Hay demasiado en curso."
    for otras in ("respuestas", "respuestas2", "respuestas3", "respuestas4",
                  "respuestas5"):
        assert "tablero" not in prueba.session_state[otras]


def test_el_tutor_tambien_esta_en_la_sesion_seis():
    prueba = _entrar("A", 0)
    botones = [b for b in prueba.button if b.label == "Preguntar al tutor"]
    assert botones
    botones[0].click().run()
    assert not prueba.exception
    assert any("El tutor os pregunta" in i.value for i in prueba.info)
