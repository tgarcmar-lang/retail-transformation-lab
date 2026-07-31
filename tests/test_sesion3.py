"""Recorrido completo de la Sesión 3, con la aplicación de verdad."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import circular, filiales, plan_circular

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
GRUPOS = ["A", "B", "C", "D", "E"]
ESPERA = 120


def _entrar(grupo: str, paso: int = 0, plan_inicial: dict | None = None) -> AppTest:
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    filial = filiales.obtener(grupo)
    prueba.sidebar.selectbox[0].set_value(f"Grupo {grupo} — {filial.nombre}").run()
    prueba.session_state["vista"] = "sesion3"
    prueba.session_state["paso3"] = paso
    if plan_inicial is not None:
        prueba.session_state["plan3c"] = plan_inicial
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


def test_la_sesion_tres_esta_desbloqueada():
    from core import sesiones
    assert sesiones.SESIONES[2].disponible


def test_se_entra_desde_la_portada():
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    boton = [b for b in prueba.button if "Sesión 3" in b.label]
    assert boton
    boton[0].click().run()
    assert not prueba.exception
    assert prueba.session_state["vista"] == "sesion3"


# --------------------------------------------------------------------------
# La jerarquía se explica antes de decidir
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_explica_la_jerarquia(grupo):
    prueba = _entrar(grupo, 0)
    textos = " ".join(
        [m.value for m in prueba.markdown]
        + [s.value for s in prueba.success]
        + [w.value for w in prueba.warning]
        + [i.value for i in prueba.info]
        + [e.value for e in prueba.error]
    )
    for escalon in ("Prevenir", "Reutilizar", "Reciclar", "Verter"):
        assert escalon in textos, escalon


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_avisa_de_que_reciclar_pierde_material(grupo):
    """Es la idea que sostiene la sesión entera."""
    prueba = _entrar(grupo, 0)
    avisos = " ".join(w.value for w in prueba.warning)
    assert "no es una tonelada salvada" in avisos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_muestra_el_balance(grupo):
    prueba = _entrar(grupo, 0)
    etiquetas = [m.label for m in prueba.metric]
    assert "Material que generáis" in etiquetas
    assert "Se pierde" in etiquetas
    assert "Tenéis que recuperar" in etiquetas


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
    mejor = circular.mejor_plan_posible(grupo)["plan"]
    prueba = _entrar(grupo, 2, plan_inicial=mejor)
    assert not prueba.exception
    assert any("Objetivo cumplido" in s.value for s in prueba.success)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_pasarse_de_presupuesto_se_avisa(grupo):
    prueba = _entrar(grupo, 2, plan_inicial=circular.plan_maximo(grupo))
    assert any("presupuesto" in e.value.lower() for e in prueba.error)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_un_plan_solo_de_reciclaje_se_reprocha(grupo):
    """La trampa de la sesión: gestionar mejor un residuo que se sigue
    generando igual. Se avisa, pero solo después de que lo intenten."""
    prueba = _entrar(
        grupo, 2, plan_inicial={"segregacion": circular.topes(grupo)["segregacion"]}
    )
    assert any("escalones de abajo" in e.value for e in prueba.error)


# --------------------------------------------------------------------------
# El paso 4 · la otra unidad de medida
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_cuarto_paso_ensena_la_cuenta_en_euros(grupo):
    prueba = _entrar(grupo, 3)
    assert not prueba.exception
    etiquetas = [m.label for m in prueba.metric]
    assert "Os cuesta gestionar devoluciones" in etiquetas
    assert "Merma" in etiquetas


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_cuarto_paso_senala_la_contradiccion(grupo):
    prueba = _entrar(grupo, 3)
    assert any("En euros no lo es en absoluto" in e.value for e in prueba.error)


def test_el_cuarto_paso_admite_no_haber_hecho_el_plan():
    prueba = _entrar("A", 3)
    assert not prueba.exception


# --------------------------------------------------------------------------
# El plan que se llevan
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_plan_se_puede_descargar(grupo):
    prueba = _entrar(grupo, 2)
    assert prueba.get("download_button")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_plan_lleva_el_nombre_de_la_filial(grupo):
    resultado = circular.simular(grupo, circular.mejor_plan_posible(grupo)["plan"])
    documento = plan_circular.generar(grupo, resultado, {}, "Equipo de prueba")
    assert filiales.obtener(grupo).nombre in documento
    assert "Equipo de prueba" in documento


def test_el_plan_marca_lo_que_no_se_ha_respondido():
    resultado = circular.simular("A", {})
    documento = plan_circular.generar("A", resultado, {})
    assert documento.count("Sin responder.") == len(plan_circular.PREGUNTAS)


def test_el_plan_recoge_lo_respondido():
    respuestas = {c: f"Respuesta a {c}" for c in plan_circular.PREGUNTAS}
    resultado = circular.simular("C", {"merma": 0.4})
    documento = plan_circular.generar("C", resultado, respuestas)
    assert "Sin responder." not in documento
    for clave in plan_circular.PREGUNTAS:
        assert f"Respuesta a {clave}" in documento


def test_el_plan_dice_la_verdad_sobre_si_cumple():
    flojo = plan_circular.generar("A", circular.simular("A", {}), {})
    assert "todavía no cumple" in flojo
    bueno = plan_circular.generar(
        "A", circular.simular("A", circular.mejor_plan_posible("A")["plan"]), {}
    )
    assert "alcanza el objetivo" in bueno


def test_el_plan_escapa_el_html_del_alumno():
    documento = plan_circular.generar(
        "A", circular.simular("A", {}), {"euros": "<script>malo()</script>"}
    )
    assert "<script>malo()</script>" not in documento
    assert "&lt;script&gt;" in documento


def test_el_plan_reparte_por_escalones():
    """Sin esta tabla el grupo no ve dónde ha actuado de verdad."""
    resultado = circular.simular("D", circular.mejor_plan_posible("D")["plan"])
    documento = plan_circular.generar("D", resultado, {})
    assert "jerarquía" in documento
    for nivel in circular.NIVELES:
        assert nivel in documento


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
    comprobador.feed(
        plan_circular.generar("D", circular.simular("D", {"retornable": 0.3}), {})
    )
    assert not comprobador.pila
    assert not comprobador.desajustes


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_nombre_del_fichero_identifica_al_grupo(grupo):
    nombre = plan_circular.nombre_de_fichero(grupo)
    assert nombre.endswith(".html")
    assert f"grupo{grupo}" in nombre
    assert "circular" in nombre


# --------------------------------------------------------------------------
# Convivencia con las otras dos sesiones
# --------------------------------------------------------------------------

def test_cambiar_de_grupo_descarta_tambien_este_plan():
    prueba = _entrar("D", 2, plan_inicial={"retornable": 0.4})
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    assert prueba.session_state["plan3c"] == {}
    assert prueba.session_state["paso3"] == 0


def test_las_respuestas_de_las_tres_sesiones_no_se_mezclan():
    prueba = _entrar("C", 0)
    prueba.text_area[0].set_value("Cambiamos el refrigerante.").run()
    assert prueba.session_state["respuestas3"]["plan_previo"] == \
        "Cambiamos el refrigerante."
    assert "plan_previo" not in prueba.session_state["respuestas"]
    assert "plan_previo" not in prueba.session_state["respuestas2"]


def test_el_tutor_tambien_esta_en_la_sesion_tres():
    prueba = _entrar("A", 0)
    botones = [b for b in prueba.button if b.label == "Preguntar al tutor"]
    assert botones
    botones[0].click().run()
    assert not prueba.exception
    assert any("El tutor os pregunta" in i.value for i in prueba.info)
