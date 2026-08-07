"""Recorrido completo de la Sesión 1, tal como lo hará un alumno.

Ejecuta la aplicación de verdad con el banco de pruebas de Streamlit: los
cinco grupos, los cinco pasos, escribiendo respuestas y descargando el
informe. Si algo revienta el 8 de septiembre, debería reventar aquí antes.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from core import filiales, informe

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
GRUPOS = ["A", "B", "C", "D", "E"]
ESPERA = 120


def _arrancar() -> AppTest:
    prueba = AppTest.from_file(APP, default_timeout=ESPERA)
    prueba.run()
    return prueba


def _elegir_grupo(prueba: AppTest, grupo: str) -> AppTest:
    filial = filiales.obtener(grupo)
    prueba.sidebar.selectbox[0].set_value(f"Grupo {grupo} — {filial.nombre}").run()
    return prueba


def _entrar_en_sesion1(grupo: str, paso: int = 0) -> AppTest:
    prueba = _elegir_grupo(_arrancar(), grupo)
    prueba.session_state["vista"] = "sesion1"
    prueba.session_state["paso"] = paso
    prueba.run()
    return prueba


# --------------------------------------------------------------------------
# La portada sigue funcionando
# --------------------------------------------------------------------------

def test_la_aplicacion_arranca_sin_errores():
    prueba = _arrancar()
    assert not prueba.exception
    assert any("Retail Transformation Lab" in m.value for m in prueba.markdown)


def test_sin_grupo_elegido_pide_elegir_uno():
    prueba = _arrancar()
    assert prueba.info, "Debería invitar a elegir grupo antes de nada"


@pytest.mark.parametrize("grupo", GRUPOS)
def test_la_portada_de_cada_filial_carga(grupo):
    prueba = _elegir_grupo(_arrancar(), grupo)
    assert not prueba.exception
    assert any(filiales.obtener(grupo).nombre in s.value for s in prueba.success)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_boton_lleva_a_la_sesion_uno(grupo):
    prueba = _elegir_grupo(_arrancar(), grupo)
    boton = [b for b in prueba.button if "Sesión 1" in b.label]
    assert boton, "Falta el botón de entrada a la Sesión 1"
    boton[0].click().run()
    assert not prueba.exception
    assert prueba.session_state["vista"] == "sesion1"


# --------------------------------------------------------------------------
# Los cinco pasos, para las cinco filiales
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
@pytest.mark.parametrize("paso", [0, 1, 2, 3, 4])
def test_cada_paso_carga_sin_errores(grupo, paso):
    prueba = _entrar_en_sesion1(grupo, paso)
    assert not prueba.exception, (
        f"El paso {paso + 1} revienta para el grupo {grupo}"
    )


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_primer_paso_muestra_las_cifras_de_la_filial(grupo):
    prueba = _entrar_en_sesion1(grupo, 0)
    etiquetas = [m.label for m in prueba.metric]
    assert "Ventas del año" in etiquetas
    assert "Puntos de venta" in etiquetas
    assert "Canal online" in etiquetas


@pytest.mark.parametrize("paso,clave", [(1, "paso2"), (2, "paso3"), (3, "paso4")])
def test_cada_paso_termina_con_su_pregunta(paso, clave):
    prueba = _entrar_en_sesion1("A", paso)
    preguntas = [t.label for t in prueba.text_area]
    assert informe.PREGUNTAS[clave] in preguntas


def test_el_ultimo_paso_pide_las_cuatro_conclusiones():
    prueba = _entrar_en_sesion1("A", 4)
    preguntas = [t.label for t in prueba.text_area]
    for clave in ("diagnostico", "evidencia", "coste", "propuesta"):
        assert informe.PREGUNTAS[clave] in preguntas


# --------------------------------------------------------------------------
# Las respuestas se guardan y llegan al informe
# --------------------------------------------------------------------------

def test_lo_que_escribe_el_alumno_se_guarda():
    prueba = _entrar_en_sesion1("D", 1)
    prueba.text_area[0].set_value("Diciembre por Navidad y julio por rebajas.").run()
    assert not prueba.exception
    assert "Navidad" in prueba.session_state["respuestas"]["paso2"]


def test_las_respuestas_sobreviven_al_cambio_de_paso():
    prueba = _entrar_en_sesion1("D", 1)
    prueba.text_area[0].set_value("Una respuesta que no se debe perder.").run()
    prueba.session_state["paso"] = 3
    prueba.run()
    assert prueba.session_state["respuestas"]["paso2"] == (
        "Una respuesta que no se debe perder."
    )


def test_cambiar_de_grupo_descarta_las_respuestas():
    """Mezclar respuestas de dos filiales produciría un informe incoherente."""
    prueba = _entrar_en_sesion1("D", 1)
    prueba.text_area[0].set_value("Conclusiones sobre Sevilla.").run()
    _elegir_grupo(prueba, "A")
    assert prueba.session_state["respuestas"] == {}


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_informe_se_puede_descargar(grupo):
    prueba = _entrar_en_sesion1(grupo, 4)
    descargas = [d for d in prueba.get("download_button")]
    assert descargas, f"Falta el botón de descarga para el grupo {grupo}"


# --------------------------------------------------------------------------
# El informe dice lo que debe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_informe_lleva_el_nombre_de_la_filial(grupo):
    documento = informe.generar(grupo, {}, "Equipo de prueba")
    assert filiales.obtener(grupo).nombre in documento
    assert "Equipo de prueba" in documento


def test_el_informe_marca_lo_que_no_se_ha_respondido():
    documento = informe.generar("A", {})
    assert documento.count("Sin responder.") == len(informe.PREGUNTAS)


def test_el_informe_recoge_lo_respondido():
    respuestas = {clave: f"Respuesta a {clave}" for clave in informe.PREGUNTAS}
    documento = informe.generar("B", respuestas)
    assert "Sin responder." not in documento
    for clave in informe.PREGUNTAS:
        assert f"Respuesta a {clave}" in documento


def test_el_informe_escapa_el_html_que_escriba_el_alumno():
    """Nadie va a atacar esto, pero un `<` mal puesto no debe romper la página."""
    documento = informe.generar("A", {"diagnostico": "<script>fallo()</script>"})
    assert "<script>fallo()</script>" not in documento
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

    comprobador = Comprobador()
    comprobador.feed(informe.generar("C", {"paso2": "Texto de prueba"}))
    assert not comprobador.pila
    assert not comprobador.desajustes


# --------------------------------------------------------------------------
# El tutor de guardia, dentro de la aplicación de verdad
# --------------------------------------------------------------------------

def _botones_de_tutor(prueba):
    return [b for b in prueba.button if b.label == "Preguntar al tutor"]


@pytest.mark.parametrize("paso", [1, 2, 3, 4])
def test_cada_paso_con_pregunta_ofrece_el_tutor(paso):
    prueba = _entrar_en_sesion1("A", paso)
    assert _botones_de_tutor(prueba), f"Falta el tutor en el paso {paso + 1}"


def test_el_primer_paso_no_tiene_tutor():
    """El paso 1 es solo lectura: no hay nada escrito sobre lo que preguntar."""
    assert not _botones_de_tutor(_entrar_en_sesion1("A", 0))


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_tutor_responde_sin_clave_configurada(grupo):
    """Así estará el 8 de septiembre si Google falla: tiene que funcionar."""
    prueba = _entrar_en_sesion1(grupo, 1)
    prueba.text_area[0].set_value("Diciembre es el mes más fuerte.").run()
    _botones_de_tutor(prueba)[0].click().run()

    assert not prueba.exception
    avisos = [i.value for i in prueba.info]
    assert any("El tutor os pregunta" in a for a in avisos)
    assert any(a.strip().endswith("?") for a in avisos)


def test_el_tutor_no_ensena_nunca_un_error_al_alumno():
    prueba = _entrar_en_sesion1("D", 2)
    _botones_de_tutor(prueba)[0].click().run()
    assert not prueba.exception
    assert not prueba.error, "El alumno no puede ver un error del tutor"


def test_el_tutor_funciona_con_la_caja_vacia():
    """Un grupo atascado pulsará el botón sin haber escrito nada."""
    prueba = _entrar_en_sesion1("E", 3)
    _botones_de_tutor(prueba)[0].click().run()
    assert not prueba.exception
    assert any("El tutor os pregunta" in i.value for i in prueba.info)


def test_el_tutor_tiene_un_limite_de_consultas():
    from modulos import sesion1_diagnostico as sesion

    prueba = _entrar_en_sesion1("A", 1)
    prueba.session_state["tutor_usos"] = sesion.LIMITE_TUTOR
    prueba.run()
    assert _botones_de_tutor(prueba)[0].disabled


def test_la_pregunta_del_tutor_no_va_al_informe():
    """El informe recoge lo que piensa el grupo, no lo que sugirió la máquina."""
    prueba = _entrar_en_sesion1("C", 1)
    prueba.text_area[0].set_value("Nuestra conclusión.").run()
    _botones_de_tutor(prueba)[0].click().run()

    documento = informe.generar("C", prueba.session_state["respuestas"])
    # La clave lleva prefijo de sesión desde que el panel del tutor es
    # compartido por las siete: ver `modulos/ayuda.py`.
    pregunta = prueba.session_state["tutor_respuestas"]["s1_paso2"][0]
    assert "Nuestra conclusión." in documento
    assert pregunta not in documento


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_nombre_del_fichero_identifica_al_grupo(grupo):
    nombre = informe.nombre_de_fichero(grupo)
    assert nombre.endswith(".html")
    assert f"grupo{grupo}" in nombre
    assert filiales.obtener(grupo).ciudad.lower() in nombre
