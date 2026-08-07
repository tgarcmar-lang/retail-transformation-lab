"""Pruebas del banco de conceptos y de los tres modos del tutor.

Lo que se vigila, en orden de importancia:

1. **Que ningún modo desvele el hallazgo de la filial.** Es la razón de ser
   del diseño y lo único que no se puede negociar. El modo explicar lo
   consigue estructuralmente: no recibe ni un dato del caso.
2. **Que el banco responda a lo que los alumnos preguntan de verdad.** La
   queja de la primera prueba con alumnos fue que el tutor no resolvía nada;
   si el banco no acierta, seguimos igual.
3. **Que nunca se pare la clase**: sin clave, sin red o con una consulta
   absurda, siempre sale algo útil y nunca un error.
"""

import pytest

from core import conceptos, tutor

#: Consultas reales del tipo que hace un alumno, con el concepto que deberían
#: encontrar. Si esta tabla deja de pasar, el tutor ha vuelto a ser inútil.
CONSULTAS = [
    ("qué es el alcance 3", "alcances"),
    ("no entiendo los alcances", "alcances"),
    ("cómo se calcula la huella de carbono", "huella"),
    ("qué es el CO2 equivalente", "huella"),
    ("por qué reciclar no es lo mismo que circularidad", "circularidad"),
    ("qué es la jerarquía de residuos", "jerarquia_residuos"),
    ("explícame la ley de Little", "little"),
    ("qué es el WIP", "kanban"),
    ("doble materialidad", "doble_materialidad"),
    ("qué es la CSRD", "csrd"),
    ("qué es el greenwashing", "greenwashing"),
    ("ISO 14083", "iso14083"),
    ("diferencia entre predictivo e iterativo", "predictivo_iterativo"),
    ("qué es un sprint", "scrum"),
    ("qué son los kilómetros en vacío", "km_vacio"),
    ("qué es el factor de carga", "factor_carga"),
    ("qué es la merma", "merma"),
    ("estimación por gasto", "estimacion_gasto"),
    ("qué es el cambio modal", "cambio_modal"),
    ("mapa de actores", "actores"),
    ("qué es la adopción", "adopcion"),
    ("logística inversa", "logistica_inversa"),
]


# --------------------------------------------------------------------------
# El banco acierta
# --------------------------------------------------------------------------

@pytest.mark.parametrize("consulta,esperado", CONSULTAS)
def test_el_banco_encuentra_el_concepto(consulta, esperado):
    concepto = conceptos.buscar(consulta)
    assert concepto is not None, consulta
    assert concepto.codigo == esperado, (consulta, concepto.codigo)


def test_el_banco_no_inventa_cuando_no_sabe():
    for absurda in ["", "   ", "hola", "no sé nada de esto", "asdfgh"]:
        assert conceptos.buscar(absurda) is None, absurda


def test_hay_conceptos_de_las_siete_sesiones():
    sesiones = {c.sesion for c in conceptos.CONCEPTOS}
    assert sesiones == set(range(1, 8))


def test_todo_concepto_esta_bien_formado():
    for concepto in conceptos.CONCEPTOS:
        assert concepto.titulo and concepto.explicacion
        assert len(concepto.explicacion) > 120, concepto.codigo
        assert 1 <= concepto.sesion <= 7


def test_los_codigos_no_se_repiten():
    codigos = [c.codigo for c in conceptos.CONCEPTOS]
    assert len(codigos) == len(set(codigos))


def test_casi_todos_dicen_donde_mirar():
    """Es lo único que este tutor puede hacer y un motor externo no."""
    con_ubicacion = [c for c in conceptos.CONCEPTOS if c.donde_mirar]
    assert len(con_ubicacion) >= len(conceptos.CONCEPTOS) - 2


# --------------------------------------------------------------------------
# Lo que no puede pasar: que se escape el hallazgo
# --------------------------------------------------------------------------

#: Las cifras y expresiones que constituyen el hallazgo de cada filial. Si
#: alguna aparece en una explicación, el ejercicio se ha destruido.
PROHIBIDO = [
    "madrid", "barcelona", "valencia", "sevilla", "bilbao", "retailnova",
    "34 %", "4,1 %", "r-404a", "84 %",
]


def test_ninguna_explicacion_del_banco_nombra_a_una_filial():
    """El banco explica conceptos, no diagnósticos.

    Un texto que dijera «en Sevilla el vacío es del 34 %» convertiría el
    tutor en la respuesta del ejercicio.
    """
    for concepto in conceptos.CONCEPTOS:
        texto = (concepto.explicacion + " " + concepto.donde_mirar).lower()
        for prohibido in PROHIBIDO:
            assert prohibido not in texto, (concepto.codigo, prohibido)


def test_el_modo_explicar_no_recibe_datos_de_la_filial():
    """La garantía es estructural, no una prohibición en el prompt.

    `explicar` no acepta el grupo como parámetro: no puede enviar datos de
    la filial ni queriendo.
    """
    import inspect
    parametros = inspect.signature(tutor.explicar).parameters
    assert "grupo" not in parametros
    assert "filial" not in parametros


def test_la_instruccion_de_explicar_prohibe_hablar_de_la_empresa():
    assert "NO hables de ninguna empresa concreta" in tutor.INSTRUCCION_EXPLICAR
    assert "NO inventes cifras" in tutor.INSTRUCCION_EXPLICAR


def test_orientar_dice_donde_pero_no_que():
    texto, acertado = tutor.orientar("kilómetros en vacío")
    assert acertado
    assert "Sesión 1" in texto
    assert "no lo que dice" in texto


# --------------------------------------------------------------------------
# El modo explicar
# --------------------------------------------------------------------------

@pytest.mark.parametrize("consulta,esperado", CONSULTAS)
def test_explicar_responde_desde_el_banco(consulta, esperado):
    """Sin clave, sin red y sin cuota: el banco basta para lo que preguntan."""
    texto, origen = tutor.explicar(consulta)
    assert origen == "banco"
    assert conceptos.POR_CODIGO[esperado].explicacion[:40] in texto


def test_explicar_incluye_donde_mirar():
    texto, _ = tutor.explicar("qué es el factor de carga")
    assert "Dónde mirarlo" in texto


def test_explicar_sin_consulta_no_falla():
    texto, origen = tutor.explicar("")
    assert texto
    assert origen == "banco"


def test_explicar_sin_clave_y_sin_concepto_no_deja_tirado_al_alumno():
    texto, origen = tutor.explicar("cuéntame un chiste")
    assert origen == "sin_respuesta"
    assert "profesor" in texto
    assert "error" not in texto.lower()


def test_explicar_usa_la_ia_solo_cuando_el_banco_no_llega():
    """Y cuando la usa, valida lo que devuelve."""
    llamadas = []

    def transporte(url, cabeceras, cuerpo, tiempo):
        llamadas.append(cuerpo["input"])
        return {"candidates": [{"content": {"parts": [
            {"text": "El teorema de Bayes permite actualizar una "
                     "probabilidad cuando aparece información nueva."}]}}]}

    secretos = {"gemini": {"api_key": "prueba"}}

    # Con un concepto del banco, la IA ni se toca.
    _, origen = tutor.explicar("qué es el alcance 3", secretos,
                               transporte=transporte)
    assert origen == "banco"
    assert not llamadas

    # Con algo que no está en el banco, sí.
    texto, origen = tutor.explicar("qué es el teorema de Bayes", secretos,
                                   transporte=transporte)
    assert origen == "tutor"
    assert "bayes" in texto.lower()
    assert len(llamadas) == 1


def test_una_explicacion_kilometrica_se_descarta():
    def transporte(url, cabeceras, cuerpo, tiempo):
        return {"candidates": [{"content": {"parts": [
            {"text": "bla " * 2_000}]}}]}

    texto, origen = tutor.explicar(
        "qué es el teorema de Bayes", {"gemini": {"api_key": "x"}},
        transporte=transporte,
    )
    assert origen == "sin_respuesta"
    assert "bla" not in texto


def test_si_la_ia_falla_no_se_para_la_clase():
    def transporte(url, cabeceras, cuerpo, tiempo):
        raise RuntimeError("sin cuota")

    texto, origen = tutor.explicar(
        "qué es el teorema de Bayes", {"gemini": {"api_key": "x"}},
        transporte=transporte,
    )
    assert origen == "sin_respuesta"
    assert texto


# --------------------------------------------------------------------------
# La sesión desempata
# --------------------------------------------------------------------------

def test_la_sesion_ayuda_a_desempatar():
    """La misma palabra puede significar cosas distintas según la sesión."""
    en_tres = conceptos.buscar("merma", sesion=3)
    en_uno = conceptos.buscar("merma", sesion=1)
    assert en_tres is not None and en_uno is not None


def test_del_curso_filtra_por_sesion():
    for sesion in range(1, 8):
        for concepto in conceptos.del_curso(sesion):
            assert concepto.sesion == sesion
    assert len(conceptos.del_curso()) == len(conceptos.CONCEPTOS)


# --------------------------------------------------------------------------
# El modo preguntar sigue intacto
# --------------------------------------------------------------------------

def test_el_modo_preguntar_sigue_devolviendo_preguntas():
    texto, del_tutor = tutor.preguntar("A", "diagnostico", "Gastamos mucho")
    assert "?" in texto
    assert not del_tutor


def test_el_contexto_del_tutor_no_lleva_el_diagnostico():
    """Prueba heredada del diseño original: sigue valiendo."""
    for grupo in "ABCDE":
        contexto = tutor.contexto(grupo, "paso3").lower()
        for palabra in ["problema", "diagnóstico", "debería", "recomend"]:
            assert palabra not in contexto, (grupo, palabra)
