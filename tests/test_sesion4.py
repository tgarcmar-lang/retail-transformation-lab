"""Recorrido completo de la Sesión 4, con la aplicación de verdad."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import filiales, memoria, reporting

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
GRUPOS = ["A", "B", "C", "D", "E"]
ESPERA = 120


def _entrar(grupo: str, paso: int = 0, seleccion: list | None = None,
            declaraciones: dict | None = None) -> AppTest:
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    filial = filiales.obtener(grupo)
    prueba.sidebar.selectbox[0].set_value(f"Grupo {grupo} — {filial.nombre}").run()
    prueba.session_state["vista"] = "sesion4"
    prueba.session_state["paso4"] = paso
    if seleccion is not None:
        prueba.session_state["seleccion4"] = seleccion
    if declaraciones is not None:
        prueba.session_state["declaraciones4"] = declaraciones
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


def test_la_sesion_cuatro_esta_desbloqueada():
    from core import sesiones
    assert sesiones.SESIONES[3].disponible


def test_se_entra_desde_la_portada():
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    boton = [b for b in prueba.button if "Sesión 4" in b.label]
    assert boton
    boton[0].click().run()
    assert not prueba.exception
    assert prueba.session_state["vista"] == "sesion4"


# --------------------------------------------------------------------------
# El marco
# --------------------------------------------------------------------------

def test_el_primer_paso_avisa_de_que_la_csrd_cambio():
    """Si un alumno busca información de 2024 se encontrará otra cosa."""
    prueba = _entrar("A", 0)
    avisos = " ".join(w.value for w in prueba.warning)
    assert "Ómnibus" in avisos
    assert "2026" in avisos


def test_el_primer_paso_dice_que_retailnova_sigue_obligada():
    prueba = _entrar("A", 0)
    textos = " ".join(i.value for i in prueba.info)
    assert "sigue obligada" in textos.lower()


def test_el_primer_paso_conecta_con_el_doble_objetivo_de_la_sesion_2():
    """El SBTi v2.0 exige justo lo que se hizo allí. Es un regalo."""
    prueba = _entrar("A", 0)
    textos = " ".join(s.value for s in prueba.success)
    assert "SBTi" in textos


# --------------------------------------------------------------------------
# Materialidad
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_segundo_paso_pinta_la_matriz(grupo):
    prueba = _entrar(grupo, 1)
    assert not prueba.exception
    textos = " ".join(i.value for i in prueba.info)
    assert "asuntos materiales" in textos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_segundo_paso_avisa_de_que_materialidad_no_es_desempeno(grupo):
    prueba = _entrar(grupo, 1)
    textos = " ".join(m.value for m in prueba.markdown)
    assert "lo que hacemos mal" in textos


# --------------------------------------------------------------------------
# La selección de indicadores
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_tercer_paso_ofrece_el_catalogo(grupo):
    prueba = _entrar(grupo, 2)
    assert len(prueba.checkbox) == len(reporting.INDICADORES)
    assert len(prueba.radio) >= len(reporting.DECLARACIONES)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_sin_indicadores_se_avisa_de_los_asuntos_sin_cubrir(grupo):
    prueba = _entrar(grupo, 2, seleccion=[])
    assert any("faltan asuntos materiales" in w.value.lower()
               for w in prueba.warning)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_pasarse_del_limite_se_avisa(grupo):
    todos = [i.codigo for i in reporting.INDICADORES]
    prueba = _entrar(grupo, 2, seleccion=todos)
    assert any("límite" in e.value.lower() for e in prueba.error)


# --------------------------------------------------------------------------
# La revisión
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_memoria_ejemplar_recibe_opinion_favorable(grupo):
    seleccion, declaraciones = reporting.memoria_ejemplar(grupo)
    prueba = _entrar(grupo, 3, seleccion=seleccion, declaraciones=declaraciones)
    assert not prueba.exception
    assert any("favorable" in s.value for s in prueba.success)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_una_memoria_vacia_recibe_opinion_desfavorable(grupo):
    prueba = _entrar(grupo, 3, seleccion=[], declaraciones={})
    assert any("desfavorable" in e.value for e in prueba.error)


def test_sumar_las_reducciones_sale_en_la_revision():
    seleccion, declaraciones = reporting.memoria_ejemplar("B")
    declaraciones["reduccion"] = "sumada"
    prueba = _entrar("B", 3, seleccion=seleccion, declaraciones=declaraciones)
    textos = " ".join(m.value for m in prueba.markdown)
    assert "induce a error" in textos


def test_la_revision_recuerda_que_ninguna_opcion_era_falsa():
    """Es el remate de la sesión y no puede faltar."""
    seleccion, declaraciones = reporting.memoria_ejemplar("A")
    prueba = _entrar("A", 3, seleccion=seleccion, declaraciones=declaraciones)
    textos = " ".join(i.value for i in prueba.info)
    assert "Engañan igual" in textos


# --------------------------------------------------------------------------
# La memoria que se llevan
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_memoria_se_puede_descargar(grupo):
    seleccion, declaraciones = reporting.memoria_ejemplar(grupo)
    prueba = _entrar(grupo, 3, seleccion=seleccion, declaraciones=declaraciones)
    assert prueba.get("download_button")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_memoria_lleva_el_nombre_de_la_filial(grupo):
    seleccion, declaraciones = reporting.memoria_ejemplar(grupo)
    evaluacion = reporting.evaluar(grupo, seleccion, declaraciones)
    documento = memoria.generar(grupo, seleccion, declaraciones, evaluacion,
                                {}, "Equipo de prueba")
    assert filiales.obtener(grupo).nombre in documento
    assert "Equipo de prueba" in documento


def test_la_memoria_lleva_dentro_la_revision():
    """Se publica con las salvedades impresas. Es media lección."""
    seleccion, declaraciones = reporting.memoria_ejemplar("C")
    declaraciones["circularidad"] = "reciclaje"
    evaluacion = reporting.evaluar("C", seleccion, declaraciones)
    documento = memoria.generar("C", seleccion, declaraciones, evaluacion, {})
    assert "Revisión independiente" in documento
    assert "Opinión con salvedades" in documento


def test_la_memoria_cita_la_norma_de_logistica():
    seleccion, declaraciones = reporting.memoria_ejemplar("D")
    evaluacion = reporting.evaluar("D", seleccion, declaraciones)
    documento = memoria.generar("D", seleccion, declaraciones, evaluacion, {})
    assert "ISO 14083" in documento


def test_la_memoria_publica_la_matriz_de_materialidad():
    seleccion, declaraciones = reporting.memoria_ejemplar("A")
    evaluacion = reporting.evaluar("A", seleccion, declaraciones)
    documento = memoria.generar("A", seleccion, declaraciones, evaluacion, {})
    assert "doble materialidad" in documento
    for tema in reporting.TEMAS:
        assert tema.nombre in documento


def test_la_memoria_marca_lo_que_no_se_ha_respondido():
    seleccion, declaraciones = reporting.memoria_ejemplar("A")
    evaluacion = reporting.evaluar("A", seleccion, declaraciones)
    documento = memoria.generar("A", seleccion, declaraciones, evaluacion, {})
    assert documento.count("Sin responder.") == len(memoria.PREGUNTAS)


def test_la_memoria_escapa_el_html_del_alumno():
    seleccion, declaraciones = reporting.memoria_ejemplar("A")
    evaluacion = reporting.evaluar("A", seleccion, declaraciones)
    documento = memoria.generar(
        "A", seleccion, declaraciones, evaluacion,
        {"peor_cifra": "<script>malo()</script>"},
    )
    assert "<script>malo()</script>" not in documento
    assert "&lt;script&gt;" in documento


def test_la_memoria_es_html_bien_formado():
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

    seleccion, declaraciones = reporting.memoria_ejemplar("E")
    evaluacion = reporting.evaluar("E", seleccion, declaraciones)
    comprobador = Comprobador()
    comprobador.feed(memoria.generar("E", seleccion, declaraciones,
                                     evaluacion, {}))
    assert not comprobador.pila
    assert not comprobador.desajustes


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_nombre_del_fichero_identifica_al_grupo(grupo):
    nombre = memoria.nombre_de_fichero(grupo)
    assert nombre.endswith(".html")
    assert f"grupo{grupo}" in nombre
    assert "memoria_esg" in nombre


# --------------------------------------------------------------------------
# Convivencia con las otras sesiones
# --------------------------------------------------------------------------

def test_cambiar_de_grupo_descarta_la_memoria():
    prueba = _entrar("D", 2, seleccion=["e_huella_12"],
                     declaraciones={"reduccion": "sumada"})
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    assert prueba.session_state["seleccion4"] == []
    assert prueba.session_state["declaraciones4"] == {}
    assert prueba.session_state["paso4"] == 0


def test_las_respuestas_de_las_cuatro_sesiones_no_se_mezclan():
    prueba = _entrar("C", 0)
    prueba.text_area[0].set_value("Reducir un 25 % y un 10 %.").run()
    assert prueba.session_state["respuestas4"]["compromisos_previos"] == \
        "Reducir un 25 % y un 10 %."
    for otras in ("respuestas", "respuestas2", "respuestas3"):
        assert "compromisos_previos" not in prueba.session_state[otras]


def test_el_tutor_tambien_esta_en_la_sesion_cuatro():
    prueba = _entrar("A", 0)
    botones = [b for b in prueba.button if b.label == "Preguntar al tutor"]
    assert botones
    botones[0].click().run()
    assert not prueba.exception
    assert any("El tutor os pregunta" in i.value for i in prueba.info)
