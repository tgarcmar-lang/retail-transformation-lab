"""Pruebas de la identidad visual.

Una marca rota no tumba la aplicación, así que puede pasar desapercibida
hasta el día de clase. Estas pruebas la vigilan.
"""

import re
from html.parser import HTMLParser

import pytest

from core import marca

VACIAS = {"img", "br", "hr", "meta", "line", "circle", "path", "use", "rect"}


class _Comprobador(HTMLParser):
    """Verifica que las etiquetas abren y cierran en orden."""

    def __init__(self):
        super().__init__()
        self.pila = []
        self.desajustes = []

    def handle_starttag(self, etiqueta, atributos):
        if etiqueta not in VACIAS:
            self.pila.append(etiqueta)

    def handle_startendtag(self, etiqueta, atributos):
        pass  # <line/> y compañía se cierran solas

    def handle_endtag(self, etiqueta):
        if etiqueta in VACIAS:
            return
        if self.pila and self.pila[-1] == etiqueta:
            self.pila.pop()
        else:
            self.desajustes.append(etiqueta)


def _revisar(html: str) -> _Comprobador:
    sin_estilos = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    comprobador = _Comprobador()
    comprobador.feed(sin_estilos)
    return comprobador


# --------------------------------------------------------------------------
# El logotipo
# --------------------------------------------------------------------------

def test_los_dos_logotipos_estan_en_el_repositorio():
    assert marca.LOGO.exists(), "Falta assets/ucjc.png"
    assert marca.LOGO_PEQUENO.exists(), "Falta assets/ucjc_pequeno.png"


def test_el_logotipo_se_incrusta_como_uri_de_datos():
    assert marca.logo_incrustado().startswith("data:image/png;base64,")
    assert marca.logo_incrustado(pequeno=True).startswith("data:image/png;base64,")


def test_el_logotipo_pequeno_pesa_menos_que_el_grande():
    """Dentro de la sesión se reenvía en cada clic: tiene que ser el ligero."""
    assert len(marca.logo_incrustado(pequeno=True)) < len(marca.logo_incrustado())


def test_sin_logotipo_la_cabecera_no_revienta(monkeypatch, tmp_path):
    """Una imagen que falta no puede parar una clase."""
    monkeypatch.setattr(marca, "LOGO", tmp_path / "no_existe.png")
    marca.logo_incrustado.cache_clear()
    try:
        html = marca.cabecera()
        assert marca.TITULO in html
        assert "<img" not in html
    finally:
        marca.logo_incrustado.cache_clear()


# --------------------------------------------------------------------------
# La cabecera dice lo que debe
# --------------------------------------------------------------------------

def test_la_cabecera_lleva_la_identidad_de_la_escuela():
    html = marca.cabecera()
    assert marca.ESCUELA in html
    assert marca.UNIVERSIDAD in html
    assert marca.RESPONSABLE in html


def test_la_cabecera_lleva_el_rotulo_y_el_titulo():
    html = marca.cabecera()
    assert "AI Sustainability" in html
    assert marca.TITULO in html


def test_la_cabecera_usa_el_granate_corporativo():
    assert marca.GRANATE == "#872046"
    assert marca.GRANATE in marca.cabecera()


def test_la_cabecera_dibuja_las_cinco_filiales():
    html = marca.cabecera()
    for _, ciudad, *_ in marca.NODOS:
        assert ciudad in html
    assert len(marca.NODOS) == 5


def test_las_cifras_aparecen_cuando_se_pasan():
    html = marca.cabecera([("1.149 M€", "Ventas anuales"), ("134", "Puntos de venta")])
    assert "1.149 M€" in html
    assert "Puntos de venta" in html


def test_sin_cifras_la_cabecera_sigue_siendo_valida():
    """Si los datos no cargan, la portada se dibuja igual, sin cifras."""
    html = marca.cabecera([])
    assert marca.TITULO in html
    assert '<div class="marca-cifras">' not in html


def test_la_red_se_dibuja_aunque_no_haya_cifras():
    """El esquema de filiales es un dibujo fijo: no depende de los datos."""
    assert "Bilbao" in marca.cabecera([])


def test_la_red_se_puede_quitar():
    assert "Bilbao" not in marca.cabecera([], red=False)


# --------------------------------------------------------------------------
# HTML bien formado
# --------------------------------------------------------------------------

@pytest.mark.parametrize("generador", [
    lambda: marca.cabecera(),
    lambda: marca.cabecera([("1", "uno"), ("2", "dos")]),
    lambda: marca.cabecera_compacta(),
    lambda: marca.cabecera_compacta("RetailNova Madrid · Grupo A"),
])
def test_el_html_esta_bien_formado(generador):
    comprobador = _revisar(generador())
    assert not comprobador.pila, f"Etiquetas sin cerrar: {comprobador.pila}"
    assert not comprobador.desajustes, f"Desajustes: {comprobador.desajustes}"


def test_la_cabecera_compacta_es_mas_ligera_que_la_completa():
    assert len(marca.cabecera_compacta()) < len(marca.cabecera([("1", "uno")]))


def test_la_cabecera_de_sesion_no_supera_los_treinta_kilobytes():
    """Se reenvía en cada interacción del alumno: hay que vigilarla."""
    assert len(marca.cabecera_compacta("Grupo A")) < 30_000
