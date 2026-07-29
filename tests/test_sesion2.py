"""Recorrido completo de la Sesión 2, con la aplicación de verdad."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import filiales, palancas, plan

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
GRUPOS = ["A", "B", "C", "D", "E"]
ESPERA = 120


def _entrar(grupo: str, paso: int = 0, plan_inicial: dict | None = None) -> AppTest:
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    filial = filiales.obtener(grupo)
    prueba.sidebar.selectbox[0].set_value(f"Grupo {grupo} — {filial.nombre}").run()
    prueba.session_state["vista"] = "sesion2"
    prueba.session_state["paso2"] = paso
    if plan_inicial is not None:
        prueba.session_state["plan"] = plan_inicial
    prueba.run()
    return prueba


# --------------------------------------------------------------------------
# La sesión carga
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
@pytest.mark.parametrize("paso", [0, 1, 2])
def test_cada_paso_carga_sin_errores(grupo, paso):
    prueba = _entrar(grupo, paso)
    assert not prueba.exception, f"Paso {paso + 1} roto en el grupo {grupo}"


def test_la_sesion_dos_esta_desbloqueada():
    from core import sesiones
    assert sesiones.SESIONES[1].disponible


def test_se_entra_desde_la_portada():
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    boton = [b for b in prueba.button if "Sesión 2" in b.label]
    assert boton
    boton[0].click().run()
    assert not prueba.exception
    assert prueba.session_state["vista"] == "sesion2"


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_muestra_la_huella_y_el_presupuesto(grupo):
    prueba = _entrar(grupo, 0)
    etiquetas = [m.label for m in prueba.metric]
    assert "Huella actual" in etiquetas
    assert "Objetivo de reducción" in etiquetas
    assert "Presupuesto a tres años" in etiquetas


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_pide_la_conclusion_de_la_sesion_uno(grupo):
    """Es lo que sustituye al guardado en servidor: llegan con su informe."""
    prueba = _entrar(grupo, 0)
    preguntas = " ".join(t.label for t in prueba.text_area)
    assert "problema principal" in preguntas


# --------------------------------------------------------------------------
# El simulador
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_simulador_ofrece_controles(grupo):
    prueba = _entrar(grupo, 2)
    assert prueba.slider, f"El grupo {grupo} no tiene ningún control"


def test_sin_plan_no_se_cumple_el_objetivo():
    prueba = _entrar("A", 2, plan_inicial={})
    assert any("faltan" in w.value.lower() for w in prueba.warning)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_el_mejor_plan_se_cumple_el_objetivo(grupo):
    mejor = palancas.mejor_plan_posible(grupo)["plan"]
    prueba = _entrar(grupo, 2, plan_inicial=mejor)
    assert not prueba.exception
    assert any("Objetivo cumplido" in s.value for s in prueba.success)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_pasarse_de_presupuesto_se_avisa(grupo):
    prueba = _entrar(grupo, 2, plan_inicial=palancas.plan_maximo(grupo))
    assert any("presupuesto" in e.value.lower() for e in prueba.error)


def test_a_bilbao_se_le_avisa_de_que_el_refrigerante_no_le_sirve():
    """La trampa del caso: copiar el plan de Valencia le costaría 1,4 M€."""
    prueba = _entrar("E", 1)
    assert any("no os sirve de nada" in e.value for e in prueba.error)


@pytest.mark.parametrize("grupo", ["A", "B", "C", "D"])
def test_a_las_demas_no_se_les_avisa_de_nada_inutil(grupo):
    prueba = _entrar(grupo, 1)
    assert not prueba.error


# --------------------------------------------------------------------------
# El plan que se llevan
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_plan_se_puede_descargar(grupo):
    prueba = _entrar(grupo, 2)
    assert prueba.get("download_button")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_plan_lleva_el_nombre_de_la_filial(grupo):
    resultado = palancas.simular(grupo, palancas.mejor_plan_posible(grupo)["plan"])
    documento = plan.generar(grupo, resultado, {}, "Equipo de prueba")
    assert filiales.obtener(grupo).nombre in documento
    assert "Equipo de prueba" in documento


def test_el_plan_marca_lo_que_no_se_ha_respondido():
    resultado = palancas.simular("A", {})
    documento = plan.generar("A", resultado, {})
    assert documento.count("Sin responder.") == len(plan.PREGUNTAS)


def test_el_plan_recoge_lo_respondido():
    respuestas = {clave: f"Respuesta a {clave}" for clave in plan.PREGUNTAS}
    resultado = palancas.simular("C", {"refrigerante": 1.0})
    documento = plan.generar("C", resultado, respuestas)
    assert "Sin responder." not in documento
    for clave in plan.PREGUNTAS:
        assert f"Respuesta a {clave}" in documento


def test_el_plan_dice_la_verdad_sobre_si_cumple():
    flojo = plan.generar("A", palancas.simular("A", {}), {})
    assert "todavía no cumple" in flojo

    bueno = plan.generar(
        "A", palancas.simular("A", palancas.mejor_plan_posible("A")["plan"]), {}
    )
    assert "alcanza el objetivo" in bueno


def test_el_plan_escapa_el_html_del_alumno():
    documento = plan.generar(
        "A", palancas.simular("A", {}), {"riesgo": "<script>malo()</script>"}
    )
    assert "<script>malo()</script>" not in documento
    assert "&lt;script&gt;" in documento


def test_el_plan_es_html_bien_formado():
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

    comprobador = Comprobador()
    comprobador.feed(plan.generar("D", palancas.simular("D", {"rutas": 5}), {}))
    assert not comprobador.pila
    assert not comprobador.desajustes


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_nombre_del_fichero_identifica_al_grupo(grupo):
    nombre = plan.nombre_de_fichero(grupo)
    assert nombre.endswith(".html")
    assert f"grupo{grupo}" in nombre
    assert "descarbonizacion" in nombre


# --------------------------------------------------------------------------
# Convivencia con la Sesión 1
# --------------------------------------------------------------------------

def test_cambiar_de_grupo_descarta_tambien_el_plan():
    """Un plan hecho para Sevilla no vale para Madrid: se empieza de cero."""
    prueba = _entrar("D", 2, plan_inicial={"rutas": 10.0})
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    assert prueba.session_state["plan"] == {}
    # Las cajas de texto se vuelven a dibujar vacías, no con lo de antes.
    assert all(not v for v in prueba.session_state["respuestas2"].values())
    assert prueba.session_state["paso2"] == 0


def test_cambiar_de_grupo_devuelve_al_primer_paso():
    prueba = _entrar("D", 2)
    prueba.sidebar.selectbox[0].set_value("Grupo B — RetailNova Barcelona").run()
    assert prueba.session_state["paso2"] == 0
    assert not prueba.exception


def test_las_respuestas_de_las_dos_sesiones_no_se_mezclan():
    """El informe de la Sesión 1 y el plan de la Sesión 2 son documentos
    distintos: sus respuestas viven en sitios distintos."""
    prueba = _entrar("C", 0)
    prueba.text_area[0].set_value("La cadena de frío.").run()
    assert prueba.session_state["respuestas2"]["diagnostico_previo"] == "La cadena de frío."
    respuestas_sesion1 = prueba.session_state["respuestas"]
    assert "diagnostico_previo" not in respuestas_sesion1


def test_el_tutor_tambien_esta_en_la_sesion_dos():
    prueba = _entrar("A", 0)
    botones = [b for b in prueba.button if b.label == "Preguntar al tutor"]
    assert botones
    botones[0].click().run()
    assert not prueba.exception
    assert any("El tutor os pregunta" in i.value for i in prueba.info)
