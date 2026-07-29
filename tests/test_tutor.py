"""Pruebas del tutor de guardia.

Aquí no se comprueba que el tutor sea listo, sino dos cosas que sí importan:
que **nunca deja tirada a la clase** y que **nunca regala el hallazgo**.

Todo se prueba con un transporte falso: no hace falta clave ni conexión.
"""

import pytest

from core import tutor

GRUPOS = ["A", "B", "C", "D", "E"]
PASOS = list(tutor.RESERVA)

SECRETOS = {"gemini": {"api_key": "clave-de-prueba"}}


def _respuesta(texto: str) -> dict:
    """Imita la forma de la respuesta real de la API."""
    return {"steps": [{"content": [{"type": "text", "text": texto}]}]}


def _transporte_que_devuelve(texto: str):
    def transporte(url, cabeceras, cuerpo, tiempo):
        return _respuesta(texto)
    return transporte


def _transporte_que_falla(excepcion=RuntimeError("boom")):
    def transporte(url, cabeceras, cuerpo, tiempo):
        raise excepcion
    return transporte


# --------------------------------------------------------------------------
# Nunca deja tirada a la clase
# --------------------------------------------------------------------------

@pytest.mark.parametrize("paso", PASOS)
def test_sin_clave_siempre_hay_pregunta(paso):
    texto, del_tutor = tutor.preguntar("A", paso, "lo que sea", secretos=None)
    assert texto.strip()
    assert texto.strip().endswith("?")
    assert del_tutor is False


@pytest.mark.parametrize("secretos", [
    None, {}, {"gemini": {}}, {"gemini": {"api_key": ""}},
    {"gemini": {"api_key": "   "}}, {"otra_cosa": 1},
])
def test_una_configuracion_incompleta_no_rompe_nada(secretos):
    texto, del_tutor = tutor.preguntar("B", "paso3", "texto", secretos=secretos)
    assert texto.strip()
    assert del_tutor is False


@pytest.mark.parametrize("fallo", [
    RuntimeError("cuota agotada"),
    TimeoutError("Google no contesta"),
    ValueError("respuesta ilegible"),
    KeyError("formato inesperado"),
])
def test_si_google_falla_la_clase_continua(fallo):
    """El peor caso debe ser exactamente la aplicación de siempre."""
    texto, del_tutor = tutor.preguntar(
        "C", "paso4", "algo", SECRETOS, transporte=_transporte_que_falla(fallo)
    )
    assert texto in tutor.RESERVA["paso4"]
    assert del_tutor is False


def test_una_respuesta_vacia_cae_en_la_reserva():
    texto, del_tutor = tutor.preguntar(
        "A", "paso2", "algo", SECRETOS, transporte=_transporte_que_devuelve("")
    )
    assert texto in tutor.RESERVA["paso2"]
    assert del_tutor is False


def test_preguntar_nunca_lanza_excepcion():
    class Explosivo:
        def __getitem__(self, clave):
            raise RuntimeError("los secretos también pueden fallar")

    texto, _ = tutor.preguntar("A", "paso2", "x", Explosivo())
    assert texto.strip()


@pytest.mark.parametrize("grupo", GRUPOS)
@pytest.mark.parametrize("paso", PASOS)
def test_hay_reserva_para_toda_combinacion(grupo, paso):
    texto, _ = tutor.preguntar(grupo, paso, "", secretos=None)
    assert len(texto) > 20


def test_la_reserva_rota_para_no_repetir_la_misma_pregunta():
    vistas = {tutor.pregunta_de_reserva("paso3", i) for i in range(3)}
    assert len(vistas) == len(tutor.RESERVA["paso3"])


# --------------------------------------------------------------------------
# Nunca regala el hallazgo
# --------------------------------------------------------------------------

@pytest.mark.parametrize("paso", PASOS)
def test_todas_las_preguntas_de_reserva_son_preguntas(paso):
    """Si una afirma en vez de preguntar, está dando la respuesta."""
    for pregunta in tutor.RESERVA[paso]:
        assert pregunta.strip().endswith("?"), pregunta


@pytest.mark.parametrize("paso", PASOS)
def test_la_reserva_no_nombra_ningun_hallazgo(paso):
    """El banco de preguntas no puede contener el diagnóstico de nadie."""
    prohibidas = ["kilómetros en vacío", "entregas fallidas", "R-404A",
                  "refrigerante", "cadena de frío", "última milla"]
    for pregunta in tutor.RESERVA[paso]:
        minuscula = pregunta.lower()
        for palabra in prohibidas:
            assert palabra.lower() not in minuscula, (paso, pregunta, palabra)


@pytest.mark.parametrize("basura", [
    "El problema de vuestra filial son los kilómetros en vacío.",
    "Deberíais cambiar el refrigerante R-404A por CO2.",
    "Sí, habéis acertado.",
])
def test_una_respuesta_que_afirma_se_descarta(basura):
    """El filtro exige una pregunta. Una afirmación no pasa."""
    texto, del_tutor = tutor.preguntar(
        "D", "diagnostico", "algo", SECRETOS,
        transporte=_transporte_que_devuelve(basura),
    )
    assert del_tutor is False
    assert texto in tutor.RESERVA["diagnostico"]


def test_una_parrafada_se_descarta():
    parrafada = ("Vamos a analizarlo con calma. " * 30) + "¿Qué opináis?"
    texto, del_tutor = tutor.preguntar(
        "A", "paso3", "x", SECRETOS,
        transporte=_transporte_que_devuelve(parrafada),
    )
    assert del_tutor is False


def test_un_interrogatorio_se_descarta():
    """Queremos una pregunta, no cinco: cinco abruman y guían demasiado."""
    muchas = "¿Uno? ¿Dos? ¿Tres? ¿Cuatro?"
    _, del_tutor = tutor.preguntar(
        "A", "paso3", "x", SECRETOS, transporte=_transporte_que_devuelve(muchas)
    )
    assert del_tutor is False


def test_una_pregunta_buena_si_pasa():
    buena = "¿Por qué gastáis más gasóleo que una filial con el doble de flota?"
    texto, del_tutor = tutor.preguntar(
        "D", "paso3", "algo", SECRETOS, transporte=_transporte_que_devuelve(buena)
    )
    assert del_tutor is True
    assert texto == buena


# --------------------------------------------------------------------------
# La instrucción y el contexto
# --------------------------------------------------------------------------

def test_la_instruccion_prohibe_dar_la_respuesta():
    instruccion = tutor.INSTRUCCION.lower()
    assert "nunca digas cuál es el problema" in instruccion
    assert "una sola pregunta" in instruccion or "una pregunta" in instruccion


@pytest.mark.parametrize("grupo", GRUPOS)
@pytest.mark.parametrize("paso", ["paso2", "paso3", "paso4", "diagnostico"])
def test_el_contexto_no_contiene_el_diagnostico(grupo, paso):
    """El tutor solo ve lo que ve el alumno. Nunca el hallazgo."""
    texto = tutor.contexto(grupo, paso).lower()
    for delator in ["problema", "hallazgo", "diagnóstico", "causa", "debe descubrir"]:
        assert delator not in texto, (grupo, paso, delator)


@pytest.mark.parametrize("grupo", GRUPOS)
def test_el_contexto_lleva_cifras_de_la_filial(grupo):
    texto = tutor.contexto(grupo, "paso3")
    assert "M€" in texto
    assert "%" in texto


def test_el_contexto_no_revienta_con_un_paso_desconocido():
    assert tutor.contexto("A", "inventado").strip()


def test_lo_que_escribe_el_alumno_llega_al_modelo():
    capturado = {}

    def transporte(url, cabeceras, cuerpo, tiempo):
        capturado.update(cuerpo)
        return _respuesta("¿Y por qué creéis eso?")

    tutor.preguntar("A", "paso2", "Diciembre es el mes fuerte", SECRETOS,
                    transporte=transporte)
    assert "Diciembre es el mes fuerte" in capturado["input"]
    assert capturado["system_instruction"] == tutor.INSTRUCCION
    assert capturado["store"] is False


def test_la_clave_viaja_en_la_cabecera_y_no_en_la_url():
    """Una clave en la URL acaba en los registros del servidor."""
    capturado = {}

    def transporte(url, cabeceras, cuerpo, tiempo):
        capturado["url"] = url
        capturado["cabeceras"] = cabeceras
        return _respuesta("¿Seguro?")

    tutor.preguntar("A", "paso2", "x", SECRETOS, transporte=transporte)
    assert "clave-de-prueba" not in capturado["url"]
    assert capturado["cabeceras"]["x-goog-api-key"] == "clave-de-prueba"


# --------------------------------------------------------------------------
# Resistencia a los cambios de Google
# --------------------------------------------------------------------------

def test_si_un_modelo_esta_retirado_se_prueba_el_siguiente():
    intentos = []

    def transporte(url, cabeceras, cuerpo, tiempo):
        intentos.append(cuerpo["model"])
        if len(intentos) < len(tutor.MODELOS):
            raise RuntimeError("404 modelo no encontrado")
        return _respuesta("¿Y si lo miráis por millón vendido?")

    texto, del_tutor = tutor.preguntar("A", "paso4", "x", SECRETOS,
                                       transporte=transporte)
    assert intentos == tutor.MODELOS
    assert del_tutor is True


def test_hay_mas_de_un_modelo_de_repuesto():
    assert len(tutor.MODELOS) >= 2


@pytest.mark.parametrize("forma", [
    {"steps": [{"content": [{"type": "text", "text": "¿Por qué?"}]}]},
    {"candidates": [{"content": {"parts": [{"text": "¿Por qué?"}]}}]},
    {"output_text": "¿Por qué?", "otros": {"text": "¿Por qué?"}},
    {"a": {"b": {"c": [{"text": "¿Por qué?"}]}}},
])
def test_se_entiende_la_respuesta_aunque_cambie_el_formato(forma):
    """La API ya ha cambiado de esquema antes. No queremos caer con ella."""
    assert "¿Por qué?" in tutor._extraer_texto(forma)


def test_una_respuesta_sin_texto_no_revienta():
    assert tutor._extraer_texto({"steps": [{"content": []}]}) == ""
    assert tutor._extraer_texto({}) == ""


def test_hay_un_tiempo_limite_razonable():
    """En clase, esperar más de unos segundos es peor que no preguntar."""
    assert 5 <= tutor.TIEMPO_LIMITE <= 20
