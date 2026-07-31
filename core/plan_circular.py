"""Plan de economía circular que se lleva cada grupo de la Sesión 3.

Mismo criterio que los otros dos documentos: HTML autocontenido, imprimible a
PDF con Ctrl+P y sin dependencias nuevas. Reutiliza los estilos de
`core/informe.py` para que los tres se parezcan.
"""

from __future__ import annotations

import html
from datetime import datetime

from core import circular, filiales, informe, kpis

PREGUNTAS = {
    "plan_previo": "¿Qué palancas elegisteis en la Sesión 2 y por qué?",
    "material_o_carbono": "¿Alguna de aquellas palancas cambia además la "
                          "cantidad de envase o de residuo que generáis?",
    "escalon": "¿En qué escalón de la jerarquía están las palancas más "
               "baratas, y en cuál las que más material recuperan?",
    "justificacion": "¿Por qué este plan y no otro? ¿Qué habéis dejado fuera?",
    "prevencion": "¿Qué parte del plan evita que el residuo se genere y qué "
                  "parte solo lo gestiona mejor?",
    "euros": "Con la cuenta en euros delante, ¿cambiaríais el plan?",
    "consejo": "Ante el Consejo, ¿con qué cifra abrís?",
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
        elif fila["codigo"] in circular.EN_PUNTOS:
            intensidad = _num(fila["intensidad"], 1) + " puntos"
        else:
            intensidad = _pct(fila["intensidad"], 0)
        coste_t = ("—" if fila["coste_por_t"] == float("inf")
                   else _num(fila["coste_por_t"], 0) + " €")
        filas.append(
            f"<tr><td>{html.escape(fila['nombre'])}</td>"
            f"<td>{html.escape(fila['nivel'])}</td>"
            f'<td class="num">{intensidad}</td>'
            f'<td class="num">{_num(fila["evitado_t"], 0)} t</td>'
            f'<td class="num">{_eur(fila["coste_eur"])}</td>'
            f'<td class="num">{coste_t}</td></tr>'
        )
    filas.append(
        f'<tr class="propia"><td>Total</td><td></td><td class="num"></td>'
        f'<td class="num">{_num(resultado["evitado_t"], 0)} t</td>'
        f'<td class="num">{_eur(resultado["coste_eur"])}</td>'
        f'<td class="num"></td></tr>'
    )
    return (
        "<table><thead><tr><th>Palanca</th><th>Escalón</th>"
        '<th class="num">Intensidad</th><th class="num">Recupera</th>'
        '<th class="num">Inversión</th><th class="num">€ por tonelada</th>'
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table>"
    )


def _tabla_jerarquia(resultado: dict) -> str:
    filas = []
    for nivel in circular.NIVELES:
        toneladas = resultado["por_nivel"][nivel]
        parte = (toneladas / resultado["evitado_t"]
                 if resultado["evitado_t"] > 0 else 0.0)
        filas.append(
            f"<tr><td>{html.escape(nivel)}</td>"
            f'<td class="num">{_num(toneladas, 0)} t</td>'
            f'<td class="num">{_pct(parte)}</td></tr>'
        )
    return (
        '<table><thead><tr><th>Escalón</th><th class="num">Material</th>'
        '<th class="num">Peso en el plan</th></tr></thead><tbody>'
        + "".join(filas) + "</tbody></table>"
    )


def generar(grupo: str, resultado: dict, respuestas: dict[str, str],
            integrantes: str = "") -> str:
    """Construye el plan completo en HTML."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%d/%m/%Y")
    inv = circular.inventario(grupo)
    devoluciones = circular.devoluciones_resumen(grupo)

    cumple = resultado["objetivo_cumplido"] and resultado["dentro_de_presupuesto"]
    veredicto = (
        "El plan alcanza el objetivo dentro del presupuesto."
        if cumple else
        "El plan todavía no cumple: "
        + ("se sale del presupuesto."
           if not resultado["dentro_de_presupuesto"]
           else f'faltan {_num(resultado["objetivo_t"] - resultado["evitado_t"], 0)} '
                f"toneladas por recuperar.")
    )

    tarjetas = "".join([
        _tarjeta("Material generado", f'{_num(inv["generado_t"], 0)} t'),
        _tarjeta("Vuelve al ciclo hoy", f'{_num(inv["recirculado_t"], 0)} t'),
        _tarjeta("Se pierde hoy", f'{_num(resultado["base_t"], 0)} t'),
        _tarjeta("Recuperado con el plan", f'{_num(resultado["evitado_t"], 0)} t'),
        _tarjeta("Reducción de la pérdida", _pct(resultado["reduccion"])),
        _tarjeta("Inversión", _eur(resultado["coste_eur"])),
    ])

    secciones = "".join(
        f"<h3>{html.escape(PREGUNTAS[clave])}</h3>"
        f"{_respuesta(respuestas.get(clave, ''))}"
        for clave in PREGUNTAS
    )

    prevenido = resultado["por_nivel"]["Prevenir"]
    parte_prevencion = (prevenido / resultado["evitado_t"]
                        if resultado["evitado_t"] > 0 else 0.0)

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Plan de economía circular · {html.escape(filial.nombre)}</title>
<style>{informe.ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Plan de economía circular</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} ·
     Sesión 3</p>
  <p>{html.escape(integrantes) if integrantes.strip()
      else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · Resultado</h2>
<div class="tarjetas">{tarjetas}</div>
<p><strong>{html.escape(veredicto)}</strong></p>
<p>La filial recicla el {_pct(inv["pct_reciclado"], 0)} de lo que genera, pero
solo vuelve realmente al ciclo el {_pct(inv["pct_circularidad"], 0)}: el resto
se pierde en la recogida, en la limpieza y en la propia transformación. Una
tonelada reciclada no equivale a una tonelada que nunca se generó, y esa
diferencia es la razón de ser de la jerarquía de residuos.</p>

<h2>2 · Las medidas</h2>
{_tabla_plan(resultado)}

<h2>3 · Dónde actúa el plan en la jerarquía</h2>
{_tabla_jerarquia(resultado)}
<p>La prevención aporta el {_pct(parte_prevencion)} del material recuperado.
Cuanto más arriba actúe un plan, menos depende de que el sistema de recogida y
reciclaje funcione bien, y menos material hay que volver a comprar.</p>

<h2>4 · La cuenta en euros</h2>
<p>Además del material, la filial se gasta hoy
{_eur(devoluciones["coste_gestion_eur"])} al año solo en gestionar
{_num(devoluciones["pedidos_devueltos"], 0)} devoluciones, y
{_eur(kpis.inventario_resumen(grupo)["merma_eur"])} en producto que compró y
nunca vendió. Hay palancas que son caras por tonelada y baratas en dinero: la
decisión correcta rara vez se ve mirando una sola de las dos unidades.</p>

<h2>5 · El razonamiento del grupo</h2>
{secciones}

<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia. El presupuesto corresponde a un plan a tres años y
  equivale al {_pct(circular.PRESUPUESTO_SOBRE_VENTAS, 1)} de las ventas
  anuales de la filial. El objetivo es recuperar un tercio del material que
  hoy se pierde.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"plan_circular_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
