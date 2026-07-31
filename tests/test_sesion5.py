"""Recorrido completo de la Sesión 5, con la aplicación de verdad."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import acta, filiales, proyecto

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
GRUPOS = ["A", "B", "C", "D", "E"]
ESPERA = 120


def _entrar(grupo: str, paso: int = 0, plan: dict | None = None) -> AppTest:
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    filial = filiales.obtener(grupo)
    prueba.sidebar.selectbox[0].set_value(f"Grupo {grupo} — {filial.nombre}").run()
    prueba.session_state["vista"] = "sesion5"
    prueba.session_state["paso5"] = paso
    if plan is not None:
        prueba.session_state["plan5"] = plan
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


def test_la_sesion_cinco_esta_desbloqueada():
    from core import sesiones
    assert sesiones.SESIONES[4].disponible


def test_se_entra_desde_la_portada():
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    boton = [b for b in prueba.button if "Sesión 5" in b.label]
    assert boton
    boton[0].click().run()
    assert not prueba.exception
    assert prueba.session_state["vista"] == "sesion5"


# --------------------------------------------------------------------------
# El backlog y la clasificación
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_avisa_de_que_no_cabe_todo(grupo):
    """Es la premisa del ejercicio y tiene que quedar clara desde el minuto uno."""
    prueba = _entrar(grupo, 0)
    assert any("No cabe todo" in e.value for e in prueba.error)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_explica_predictivo_e_iterativo(grupo):
    prueba = _entrar(grupo, 0)
    textos = " ".join(m.value for m in prueba.markdown)
    assert "Predictivo" in textos
    assert "Iterativo" in textos


def test_el_primer_paso_dice_que_no_todo_se_gestiona_igual():
    prueba = _entrar("C", 0)
    textos = " ".join(m.value for m in prueba.markdown)
    assert "no se gestiona" in textos or "no se gestionan" in textos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_muestra_las_cifras_del_proyecto(grupo):
    prueba = _entrar(grupo, 0)
    etiquetas = [m.label for m in prueba.metric]
    assert "Iniciativas" in etiquetas
    assert "Esfuerzo total" in etiquetas
    assert "Capacidad por sprint" in etiquetas


# --------------------------------------------------------------------------
# El reparto en sprints
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_segundo_paso_ofrece_un_control_por_iniciativa(grupo):
    prueba = _entrar(grupo, 1)
    assert len(prueba.selectbox) >= len(proyecto.backlog(grupo))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_sin_plan_no_se_entrega_nada(grupo):
    prueba = _entrar(grupo, 1, plan={})
    assert not prueba.exception
    assert any("No entregáis nada" in w.value for w in prueba.warning)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_con_un_buen_plan_se_entrega_pronto(grupo):
    prueba = _entrar(grupo, 1, plan=proyecto.plan_por_valor(grupo))
    assert not prueba.exception
    assert not any("No entregáis nada" in w.value for w in prueba.warning)


# --------------------------------------------------------------------------
# Los contratiempos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_tercer_paso_cuenta_los_contratiempos_de_la_filial(grupo):
    prueba = _entrar(grupo, 2, plan=proyecto.plan_por_valor(grupo))
    assert not prueba.exception
    textos = " ".join(m.value for m in prueba.markdown)
    for evento in proyecto.eventos(grupo):
        assert evento.titulo in textos


def test_los_contratiempos_de_una_filial_no_salen_en_otra():
    """Cada grupo vive su propia historia."""
    prueba = _entrar("A", 2)
    textos = " ".join(m.value for m in prueba.markdown)
    for evento in proyecto.eventos("C"):
        assert evento.titulo not in textos


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_tercer_paso_compara_lo_esperado_con_lo_entregado(grupo):
    prueba = _entrar(grupo, 2, plan=proyecto.plan_por_valor(grupo))
    etiquetas = [m.label for m in prueba.metric]
    assert "Valor que esperabais" in etiquetas
    assert "Valor que entregáis" in etiquetas


# --------------------------------------------------------------------------
# La retrospectiva
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_cuarto_paso_compara_con_las_dos_referencias(grupo):
    prueba = _entrar(grupo, 3, plan=proyecto.plan_por_valor(grupo))
    assert not prueba.exception
    etiquetas = [m.label for m in prueba.metric]
    assert "Priorizando por valor" in etiquetas
    assert "Empezando por lo grande" in etiquetas


def test_el_cuarto_paso_avisa_de_las_iniciativas_a_medias():
    """Trabajo pagado que no entregó nada: la cifra que pregunta un comité."""
    grupo = "C"
    catalogo = proyecto.por_codigo(grupo)
    grande = max(catalogo.values(), key=lambda i: i.esfuerzo)
    prueba = _entrar(grupo, 3, plan={proyecto.SPRINTS: [grande.codigo]})
    assert any("a medias" in e.value for e in prueba.error)


# --------------------------------------------------------------------------
# El acta que se llevan
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_acta_se_puede_descargar(grupo):
    prueba = _entrar(grupo, 3, plan=proyecto.plan_por_valor(grupo))
    assert prueba.get("download_button")


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_acta_lleva_el_nombre_de_la_filial(grupo):
    resultado = proyecto.simular(grupo, proyecto.plan_por_valor(grupo))
    documento = acta.generar(grupo, resultado, {}, "Equipo de prueba")
    assert filiales.obtener(grupo).nombre in documento
    assert "Equipo de prueba" in documento


def test_el_acta_imprime_lo_que_quedo_a_medias():
    grupo = "C"
    catalogo = proyecto.por_codigo(grupo)
    grande = max(catalogo.values(), key=lambda i: i.esfuerzo)
    resultado = proyecto.simular(grupo, {proyecto.SPRINTS: [grande.codigo]})
    documento = acta.generar(grupo, resultado, {})
    assert "empezadas y sin" in documento


def test_el_acta_explica_lo_predictivo_y_lo_iterativo():
    resultado = proyecto.simular("D", proyecto.plan_por_valor("D"))
    documento = acta.generar("D", resultado, {})
    assert "Predictivo e iterativo" in documento


def test_el_acta_marca_lo_que_no_se_ha_respondido():
    resultado = proyecto.simular("A", {})
    documento = acta.generar("A", resultado, {})
    assert documento.count("Sin responder.") == len(acta.PREGUNTAS)


def test_el_acta_escapa_el_html_del_alumno():
    resultado = proyecto.simular("A", {})
    documento = acta.generar(
        "A", resultado, {"aprendizaje": "<script>malo()</script>"}
    )
    assert "<script>malo()</script>" not in documento
    assert "&lt;script&gt;" in documento


def test_el_acta_es_html_bien_formado():
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

    resultado = proyecto.simular("E", proyecto.plan_por_valor("E"))
    comprobador = Comprobador()
    comprobador.feed(acta.generar("E", resultado, {}))
    assert not comprobador.pila
    assert not comprobador.desajustes


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_nombre_del_fichero_identifica_al_grupo(grupo):
    nombre = acta.nombre_de_fichero(grupo)
    assert nombre.endswith(".html")
    assert f"grupo{grupo}" in nombre
    assert "acta_proyecto" in nombre


# --------------------------------------------------------------------------
# Convivencia con las otras sesiones
# --------------------------------------------------------------------------

def test_cambiar_de_grupo_descarta_el_plan():
    prueba = _entrar("D", 1, plan={1: ["c_refrigerante"]})
    prueba.sidebar.selectbox[0].set_value("Grupo A — RetailNova Madrid").run()
    assert prueba.session_state["plan5"] == {}
    assert prueba.session_state["paso5"] == 0


def test_las_respuestas_de_las_cinco_sesiones_no_se_mezclan():
    prueba = _entrar("C", 0)
    prueba.text_area[0].set_value("El refrigerante es una obra.").run()
    assert prueba.session_state["respuestas5"]["clasificacion"] == \
        "El refrigerante es una obra."
    for otras in ("respuestas", "respuestas2", "respuestas3", "respuestas4"):
        assert "clasificacion" not in prueba.session_state[otras]


def test_el_tutor_tambien_esta_en_la_sesion_cinco():
    prueba = _entrar("A", 0)
    botones = [b for b in prueba.button if b.label == "Preguntar al tutor"]
    assert botones
    botones[0].click().run()
    assert not prueba.exception
    assert any("El tutor os pregunta" in i.value for i in prueba.info)
