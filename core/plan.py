"""Plan de descarbonización que se lleva cada grupo de la Sesión 2.

Mismo criterio que el informe de la Sesión 1: HTML autocontenido, imprimible
a PDF con Ctrl+P y sin dependencias nuevas. Reutiliza los estilos de
`core/informe.py` para que los dos documentos se parezcan.
"""

from __future__ import annotations

import html
from datetime import datetime

from core import alcance3, filiales, informe, palancas

#: Preguntas de la sesión. La clave es la que usa el módulo para guardar la
#: respuesta; el texto es lo que sale impreso.
PREGUNTAS = {
    "diagnostico_previo": "¿Cuál dijisteis que era el problema principal de "
                          "vuestra filial en la Sesión 1?",
    "sigue_valiendo": "Viendo la huella entera, ¿ese diagnóstico sigue "
                      "valiendo o se os quedó corto?",
    "orden": "¿En qué orden vais a usar las palancas y por qué?",
    "justificacion": "¿Por qué este plan y no otro? ¿Qué habéis dejado fuera?",
    "riesgo": "¿Qué es lo que más fácilmente puede salir mal?",
    "siguiente_euro": "Si os dieran un millón más, ¿en qué lo gastaríais?",
    "alcance3_reaccion": "Con la huella entera delante, ¿sigue siendo el plan "
                         "correcto? ¿Qué cambiaríais?",
    "alcance3_limite": "¿Qué parte de vuestro alcance 3 no controláis, y a "
                       "quién habría que convencer para moverla?",
}


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _eur(valor: float) -> str:
    if abs(valor) >= 1_000_000:
        return _num(valor / 1_000_000, 2) + " M€"
    return _num(valor / 1_000, 0) + " k€"


def _pct(valor: float, decimales: int = 1) -> str:
    return _num(valor * 100, decimales) + " %"


def _tarjeta(etiqueta: str, cifra: str) -> str:
    return (f'<div class="tarjeta"><div class="etiqueta">{html.escape(etiqueta)}</div>'
            f'<div class="cifra">{html.escape(cifra)}</div></div>')


def _respuesta(texto: str) -> str:
    limpio = (texto or "").strip()
    if not limpio:
        return '<div class="respuesta vacia">Sin responder.</div>'
    return f'<div class="respuesta">{html.escape(limpio)}</div>'


def _tabla_plan(resultado: dict) -> str:
    filas = []
    for fila in resultado["detalle"]:
        if fila["intensidad"] <= 0:
            intensidad = "No se aplica"
        elif fila["codigo"] in palancas.EN_PUNTOS:
            intensidad = _num(fila["intensidad"], 1) + " puntos"
        else:
            intensidad = _pct(fila["intensidad"], 0)
        coste_t = ("—" if fila["coste_por_t"] == float("inf")
                   else _num(fila["coste_por_t"], 0) + " €")
        filas.append(
            f"<tr><td>{html.escape(fila['nombre'])}</td>"
            f'<td class="num">{intensidad}</td>'
            f'<td class="num">{_num(fila["evitado_t"], 0)} t</td>'
            f'<td class="num">{_eur(fila["coste_eur"])}</td>'
            f'<td class="num">{coste_t}</td></tr>'
        )
    filas.append(
        f'<tr class="propia"><td>Total</td><td class="num"></td>'
        f'<td class="num">{_num(resultado["evitado_t"], 0)} t</td>'
        f'<td class="num">{_eur(resultado["coste_eur"])}</td>'
        f'<td class="num"></td></tr>'
    )
    return (
        "<table><thead><tr><th>Palanca</th>"
        '<th class="num">Intensidad</th><th class="num">Evita</th>'
        '<th class="num">Inversión</th><th class="num">€ por tonelada</th>'
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table>"
    )


def _seccion_alcance3(grupo: str, resultado3: dict | None) -> str:
    """El inventario completo y el plan de alcance 3, si lo hay.

    Va al final del documento y con su propia tabla, no mezclada con la de
    alcances 1 y 2. Sumar las dos reducciones en un solo porcentaje sería
    justo el error que la sesión intenta desmontar.
    """
    inv = alcance3.inventario(grupo)

    tarjetas = "".join([
        _tarjeta("Alcances 1 y 2", f'{_num(inv["operativo_t"], 0)} t'),
        _tarjeta("Alcance 3", f'{_num(inv["alcance3_t"], 0)} t'),
        _tarjeta("Huella real", f'{_num(inv["total_t"], 0)} t'),
        _tarjeta("Lo que pesa vuestro plan operativo",
                 _pct(inv["pct_operativo"])),
    ])

    filas = "".join(
        f"<tr><td>{html.escape(fila.concepto)}</td>"
        f'<td class="num">{fila.alcance}</td>'
        f'<td class="num">{_num(fila.co2e_t, 0)} t</td>'
        f'<td class="num">{_pct(fila.pct)}</td></tr>'
        for fila in alcance3.desglose(grupo).itertuples()
    )
    inventario = (
        "<table><thead><tr><th>Concepto</th>"
        '<th class="num">Alcance</th><th class="num">Emisiones</th>'
        '<th class="num">Peso</th></tr></thead><tbody>'
        + filas + "</tbody></table>"
    )

    if resultado3 is None or resultado3["evitado_t"] <= 0:
        plan3 = (
            "<p>El grupo no llegó a construir un plan de alcance 3 en esta "
            "sesión.</p>"
        )
    else:
        detalle = "".join(
            f"<tr><td>{html.escape(fila['nombre'])}</td>"
            f'<td class="num">{_pct(fila["intensidad"], 0)}</td>'
            f'<td class="num">{_num(fila["evitado_t"], 0)} t</td>'
            f'<td class="num">{_eur(fila["coste_eur"])}</td></tr>'
            for fila in resultado3["detalle"]
        )
        plan3 = (
            "<table><thead><tr><th>Palanca</th>"
            '<th class="num">Intensidad</th><th class="num">Evita</th>'
            '<th class="num">Inversión</th></tr></thead><tbody>'
            + detalle
            + f'<tr class="propia"><td>Total</td><td class="num"></td>'
              f'<td class="num">{_num(resultado3["evitado_t"], 0)} t</td>'
              f'<td class="num">{_eur(resultado3["coste_eur"])}</td></tr>'
            + "</tbody></table>"
            + f'<p>Reducción del alcance 3: <strong>'
              f'{_pct(resultado3["reduccion"])}</strong> sobre un objetivo del '
              f'{_pct(alcance3.OBJETIVO3, 0)}, con una inversión de '
              f'{_eur(resultado3["coste_eur"])} sobre un presupuesto de '
              f'{_eur(resultado3["presupuesto_eur"])}.</p>'
        )

    return f"""
<h2>4 · La huella entera</h2>
<div class="tarjetas">{tarjetas}</div>
<p>El plan de las secciones anteriores actúa sobre los alcances 1 y 2, que
son <strong>{_pct(inv["pct_operativo"])}</strong> de la huella real de la
filial. No es un defecto del plan: es lo que le pasa a cualquier minorista,
porque un distribuidor apenas fabrica y casi todo lo que emite lo emite otro
por encargo suyo.</p>
{inventario}
<p>El alcance 3 de las compras está estimado por gasto, multiplicando el
importe comprado por un factor medio de categoría y por la intensidad del
país de fabricación. Sirve para saber dónde mirar, no para reclamar una
reducción: negociar un descuento con el proveedor bajaría esta cifra sin que
cambiase nada en la fábrica.</p>

<h2>5 · El plan de alcance 3</h2>
{plan3}
<p>Las dos reducciones no se suman en un solo porcentaje, y no es un descuido:
son inventarios distintos, con objetivos distintos y presupuestos distintos.
Así es como publican sus objetivos las empresas que lo hacen bien.</p>
"""


def generar(grupo: str, resultado: dict, respuestas: dict[str, str],
            integrantes: str = "", resultado3: dict | None = None) -> str:
    """Construye el plan completo en HTML."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%d/%m/%Y")

    cumple = resultado["objetivo_cumplido"] and resultado["dentro_de_presupuesto"]
    veredicto = (
        "El plan alcanza el objetivo dentro del presupuesto."
        if cumple else
        "El plan todavía no cumple: "
        + ("se sale del presupuesto." if not resultado["dentro_de_presupuesto"]
           else f'faltan {_num(resultado["objetivo_t"] - resultado["evitado_t"], 0)} '
                f"toneladas por reducir.")
    )

    tarjetas = "".join([
        _tarjeta("Huella de partida", f'{_num(resultado["base_t"], 0)} t'),
        _tarjeta("Huella tras el plan", f'{_num(resultado["final_t"], 0)} t'),
        _tarjeta("Reducción", _pct(resultado["reduccion"])),
        _tarjeta("Objetivo", _pct(palancas.OBJETIVO, 0)),
        _tarjeta("Inversión", _eur(resultado["coste_eur"])),
        _tarjeta("Presupuesto", _eur(resultado["presupuesto_eur"])),
    ])

    secciones = "".join(
        f"<h3>{html.escape(PREGUNTAS[clave])}</h3>"
        f"{_respuesta(respuestas.get(clave, ''))}"
        for clave in PREGUNTAS
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Plan de descarbonización · {html.escape(filial.nombre)}</title>
<style>{informe.ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Plan de descarbonización</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} ·
     Sesión 2</p>
  <p>{html.escape(integrantes) if integrantes.strip()
      else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · Resultado</h2>
<div class="tarjetas">{tarjetas}</div>
<p><strong>{html.escape(veredicto)}</strong></p>

<h2>2 · Las medidas</h2>
{_tabla_plan(resultado)}
<p>La columna de euros por tonelada es la que ordena la decisión: mide qué
rinde cada euro invertido. Una palanca cara en términos absolutos puede ser
la más eficiente, y una barata puede no servir de nada en esta filial.</p>

<h2>3 · El razonamiento del grupo</h2>
{secciones}
{_seccion_alcance3(grupo, resultado3)}
<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia. El presupuesto corresponde a un plan de inversión a tres
  años y equivale al {_pct(palancas.PRESUPUESTO_SOBRE_VENTAS, 1)} de las
  ventas anuales de la filial.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"plan_descarbonizacion_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
