"""Identidad visual de la Escuela Politécnica en la aplicación.

Devuelve HTML como texto: no importa Streamlit, así que se puede probar sin
levantar la aplicación y se reutilizará tal cual en las sesiones siguientes.

El logotipo se incrusta en el propio HTML codificado en base64. Streamlit no
sirve ficheros locales dentro de un bloque de HTML, y una etiqueta `<img>`
apuntando a `assets/ucjc.png` saldría rota en producción.
"""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

#: Dos tamaños a propósito. Streamlit reejecuta el script entero en cada clic
#: y vuelve a enviar el HTML, logotipo incluido. Dentro de una sesión hay
#: muchísima interacción, así que allí se usa el pequeño: 19 KB en vez de 41.
LOGO = RAIZ / "assets" / "ucjc.png"
LOGO_PEQUENO = RAIZ / "assets" / "ucjc_pequeno.png"

#: Granate corporativo de la Universidad Camilo José Cela.
GRANATE = "#872046"
GRANATE_CLARO = "#E9D5DD"
TINTA = "#262730"
SUAVE = "#5B6472"

ESCUELA = "Escuela Politécnica Superior de Tecnología y Ciencia"
UNIVERSIDAD = "Universidad Camilo José Cela"
RESPONSABLE = "Tomás García Martín · Director de la Escuela Politécnica UCJC"
ROTULO = "AI Sustainability &amp; Logistics Projects"
TITULO = "Retail Transformation Lab"
DESCRIPCION = "Dirige la transformación sostenible de RetailNova Europa"

#: Posición de cada filial en el esquema de la red. No es un mapa a escala:
#: es un diagrama, y colocarlas donde caen de verdad haría el dibujo ilegible.
NODOS = [
    ("E", "Bilbao", 178, 46, "arriba"),
    ("A", "Madrid", 352, 68, "arriba"),
    ("B", "Barcelona", 516, 94, "abajo"),
    ("C", "Valencia", 236, 130, "abajo"),
    ("D", "Sevilla", 300, 156, "abajo"),
]

ENLACES = [
    (352, 68, 178, 46), (352, 68, 236, 130), (352, 68, 516, 94),
    (352, 68, 300, 156), (178, 46, 236, 130), (516, 94, 300, 156),
]


@lru_cache(maxsize=2)
def logo_incrustado(pequeno: bool = False) -> str:
    """El logotipo de la universidad como URI de datos.

    Si falta el fichero devuelve cadena vacía: la aplicación se queda sin
    logotipo, pero no se cae. Una clase no se para por una imagen.
    """
    ruta = LOGO_PEQUENO if pequeno else LOGO
    if not ruta.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(ruta.read_bytes()).decode()


def _estilos() -> str:
    return f"""
<style>
.marca-caja {{
    background-image:
        linear-gradient(rgba(135,32,70,.055) 1px, transparent 1px),
        linear-gradient(90deg, rgba(135,32,70,.055) 1px, transparent 1px);
    background-size: 24px 24px;
    border: 1px solid {GRANATE_CLARO};
    border-radius: 12px;
    padding: 1.15rem 1.5rem 0;
    margin-bottom: 1.1rem;
}}
.marca-fila {{ display: flex; align-items: center; gap: 1.6rem; flex-wrap: wrap; }}
.marca-logo {{ height: 52px; width: auto; }}
.marca-escuela {{
    font-size: .98rem; font-weight: 800; color: {GRANATE};
    line-height: 1.28; margin: 0;
}}
.marca-quien {{ font-size: .8rem; color: {SUAVE}; margin: .3rem 0 0; }}
.marca-regla {{ height: 5px; background: {GRANATE}; margin: 1rem -1.5rem 0; }}
.marca-rotulo {{
    font-size: .7rem; font-weight: 800; letter-spacing: .14em;
    text-transform: uppercase; color: {GRANATE}; margin: 1rem 0 .1rem;
}}
.marca-titulo {{
    font-size: 2rem; font-weight: 800; color: {TINTA};
    letter-spacing: -.02em; margin: 0;
}}
.marca-descripcion {{ font-size: .9rem; color: {SUAVE}; margin: .35rem 0 0; }}
.marca-hero {{
    display: flex; gap: 1.6rem; align-items: center;
    flex-wrap: wrap; padding: .4rem 0 1.2rem;
}}
.marca-red {{ flex: 1 1 380px; min-width: 320px; }}
.marca-cifras {{
    flex: 0 1 250px; display: flex; flex-direction: column; gap: .5rem;
}}
.marca-cifra {{
    border: 1px solid {GRANATE_CLARO}; border-radius: 8px;
    padding: .5rem .75rem; background: rgba(255,255,255,.7);
}}
.marca-cifra-valor {{
    font-size: 1.2rem; font-weight: 800; color: {GRANATE};
    letter-spacing: -.02em; line-height: 1.1;
}}
.marca-cifra-etiqueta {{
    font-size: .66rem; color: {SUAVE}; letter-spacing: .05em;
    text-transform: uppercase; margin-top: .1rem;
}}
.marca-compacta {{
    display: flex; align-items: center; gap: 1rem;
    border-bottom: 3px solid {GRANATE}; padding-bottom: .55rem;
    margin-bottom: 1rem; flex-wrap: wrap;
}}
.marca-compacta img {{ height: 34px; width: auto; }}
.marca-compacta span {{ font-size: .78rem; color: {SUAVE}; }}
</style>"""


def _red_svg() -> str:
    """Esquema de las cinco filiales conectadas al centro."""
    enlaces = "".join(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
        for x1, y1, x2, y2 in ENLACES
    )
    nodos = []
    for codigo, ciudad, x, y, lado in NODOS:
        principal = codigo == "A"
        radio = 17 if principal in (True,) else 14
        relleno = GRANATE if principal else "#FFFFFF"
        texto = "#FFFFFF" if principal else GRANATE
        borde = "" if principal else f' stroke="{GRANATE}" stroke-width="2.2"'
        dy = -23 if lado == "arriba" else 27
        nodos.append(
            f'<circle cx="{x}" cy="{y}" r="{radio}" fill="{relleno}"{borde}/>'
            f'<text x="{x}" y="{y + 5}" font-size="13" font-weight="800" '
            f'fill="{texto}" text-anchor="middle">{codigo}</text>'
            f'<text x="{x}" y="{y + dy}" font-size="12.5" '
            f'font-weight="{700 if principal else 400}" fill="{TINTA}" '
            f'text-anchor="middle">{ciudad}</text>'
        )
    return f"""
<svg viewBox="0 0 620 200" style="width:100%;height:auto" role="img"
     aria-label="Las cinco filiales de RetailNova Europa conectadas entre sí">
  <title>Red de filiales de RetailNova Europa</title>
  <g stroke="{GRANATE}" stroke-opacity=".3" stroke-width="1.2"
     stroke-dasharray="5 4" fill="none">{enlaces}</g>
  <g font-family="-apple-system,'Segoe UI',Roboto,sans-serif">{''.join(nodos)}</g>
</svg>"""


def _cifra(valor: str, etiqueta: str) -> str:
    return (f'<div class="marca-cifra"><div class="marca-cifra-valor">{valor}</div>'
            f'<div class="marca-cifra-etiqueta">{etiqueta}</div></div>')


def cabecera(cifras: list[tuple[str, str]] | None = None,
             red: bool = True) -> str:
    """Cabecera institucional completa, con la red y las cifras del caso.

    `cifras` es una lista de pares (valor, etiqueta). La red de filiales se
    dibuja siempre que `red` sea cierto, incluso sin cifras: es un dibujo
    fijo y no depende de que los datos hayan cargado bien.
    """
    logo = logo_incrustado()
    marca = (f'<img class="marca-logo" src="{logo}" '
             f'alt="Universidad Camilo José Cela">') if logo else ""

    hero = ""
    if red or cifras:
        panel_red = f'<div class="marca-red">{_red_svg()}</div>' if red else ""
        panel_cifras = (
            '<div class="marca-cifras">'
            + "".join(_cifra(v, e) for v, e in cifras)
            + "</div>"
        ) if cifras else ""
        hero = f'<div class="marca-hero">{panel_red}{panel_cifras}</div>'

    return f"""{_estilos()}
<div class="marca-caja">
  <div class="marca-fila">
    {marca}
    <div>
      <p class="marca-escuela">{ESCUELA}<br>{UNIVERSIDAD}</p>
      <p class="marca-quien">{RESPONSABLE}</p>
    </div>
  </div>
  <div class="marca-regla"></div>
  <p class="marca-rotulo">{ROTULO}</p>
  <p class="marca-titulo">{TITULO}</p>
  <p class="marca-descripcion">{DESCRIPCION}</p>
  {hero if hero else '<div style="height:1.1rem"></div>'}
</div>"""


def cabecera_compacta(subtitulo: str = "") -> str:
    """Versión reducida para las pantallas de trabajo.

    Dentro de una sesión el alumno necesita el espacio para los datos, no
    para la marca. Se conserva el logotipo y la línea granate, y nada más.
    """
    logo = logo_incrustado(pequeno=True)
    marca = (f'<img src="{logo}" alt="Universidad Camilo José Cela">'
             if logo else "")
    extra = f"<span>{subtitulo}</span>" if subtitulo else ""
    return f"""{_estilos()}
<div class="marca-compacta">
  {marca}
  <span><strong style="color:{GRANATE}">{TITULO}</strong></span>
  {extra}
</div>"""
