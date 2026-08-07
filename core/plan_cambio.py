"""El documento de cierre del curso, de la Sesión 7.

Es el único documento que hace dos cosas: recoge el **plan de gestión del
cambio** de la filial y, debajo, la **memoria del curso completo**, con lo
que el grupo decidió en las siete sesiones.

Se hizo así en vez de dos ficheros por una razón práctica: un alumno enseña
un documento en una entrevista, no siete. Y por una razón pedagógica: puestas
en fila, las siete decisiones cuentan una historia que por separado no se ve.
"""

from __future__ import annotations

import html
from datetime import datetime

from core import cambio, filiales, informe, proyecto

PREGUNTAS = {
    "quien_pierde": "¿Quién trabaja más para que este plan salga, y quién se "
                    "lleva el beneficio?",
    "resistencia": "¿Cuál es la objeción más razonable que os van a poner?",
    "mandato": "¿Por qué no basta con ordenarlo desde dirección?",
    "primero": "Si solo pudierais hacer una cosa el primer mes, ¿cuál?",
    "curso": "De las siete sesiones, ¿qué os lleváis que no sabíais al "
             "empezar?",
}


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _pct(valor: float, decimales: int = 0) -> str:
    return _num(valor * 100, decimales) + " %"


def _tarjeta(etiqueta: str, cifra: str) -> str:
    return (f'<div class="tarjeta"><div class="etiqueta">{html.escape(etiqueta)}</div>'
            f'<div class="cifra">{html.escape(cifra)}</div></div>')


def _respuesta(texto: str) -> str:
    limpio = (texto or "").strip()
    if not limpio:
        return '<div class="respuesta vacia">Sin responder.</div>'
    return f'<div class="respuesta">{html.escape(limpio)}</div>'


def _tabla_riesgo(resultado: dict) -> str:
    filas = []
    for fila in resultado["detalle"][:8]:
        filas.append(
            f"<tr><td>{html.escape(fila['nombre'])}</td>"
            f'<td class="num">{_pct(fila["dependencia"])}</td>'
            f'<td class="num">{_num(fila["valor"], 0)}</td>'
            f'<td class="num">{_num(fila["realizado"], 1)}</td>'
            f'<td class="num">{_num(fila["perdido"], 1)}</td></tr>'
        )
    return (
        "<table><thead><tr><th>Iniciativa</th>"
        '<th class="num">Depende de la gente</th><th class="num">Valor</th>'
        '<th class="num">Se materializa</th><th class="num">Se pierde</th>'
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table>"
    )


def _tabla_palancas(plan: dict) -> str:
    filas = []
    for palanca in cambio.PALANCAS:
        intensidad = float(plan.get(palanca.codigo, 0.0) or 0.0)
        if intensidad <= 0:
            continue
        filas.append(
            f"<tr><td>{html.escape(palanca.nombre)}</td>"
            f'<td class="num">{_pct(intensidad)}</td>'
            f"<td>{html.escape(palanca.ayuda)}</td></tr>"
        )
    if not filas:
        return "<p>El grupo no eligió ninguna palanca de gestión del cambio.</p>"
    return (
        '<table><thead><tr><th>Palanca</th><th class="num">Intensidad</th>'
        "<th>Qué hace</th></tr></thead><tbody>"
        + "".join(filas) + "</tbody></table>"
    )


def _tabla_actores(grupo: str) -> str:
    tabla = cambio.mapa_de_actores(grupo)
    filas = []
    for fila in tabla.itertuples():
        filas.append(
            f"<tr><td>{html.escape(fila.nombre)}</td>"
            f'<td class="num">{fila.empleados}</td>'
            f'<td class="num">{_num(fila.impacto, 1)}</td>'
            f'<td class="num">{fila.poder}</td>'
            f"<td>{html.escape(', '.join(fila.iniciativas[:3]) or '—')}</td></tr>"
        )
    return (
        "<table><thead><tr><th>Actor</th><th class='num'>Personas</th>"
        "<th class='num'>Cuánto le toca</th><th class='num'>Poder</th>"
        "<th>Iniciativas que le caen</th></tr></thead><tbody>"
        + "".join(filas) + "</tbody></table>"
    )


def generar(grupo: str, resultado: dict, plan: dict,
            respuestas: dict[str, str], integrantes: str = "") -> str:
    """Construye el documento de cierre completo en HTML."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%d/%m/%Y")
    resumen = proyecto.resumen(grupo)

    tarjetas = "".join([
        _tarjeta("Valor del plan", _num(resultado["valor_entregado"], 0)),
        _tarjeta("Depende de las personas", _pct(resultado["pct_conductual"])),
        _tarjeta("Adopción al año", _pct(resultado["adopcion_final"])),
        _tarjeta("Valor que se materializa",
                 _num(resultado["valor_realizado"], 0)),
        _tarjeta("Se queda por el camino", _num(resultado["valor_perdido"], 0)),
        _tarjeta("Brecha", _pct(resultado["brecha"])),
    ])

    aviso = ""
    if resultado["se_desinfla"]:
        aviso = (
            f"<p><strong>La adopción se desinfla.</strong> Alcanzó su máximo "
            f"en el mes {resultado['mes_del_maximo']} y desde entonces baja. "
            f"Es lo que ocurre cuando el cambio se sostiene sobre una orden "
            f"y no sobre una convicción: nadie ha cambiado de opinión, solo "
            f"ha dejado de discutir mientras alguien miraba.</p>"
        )

    secciones = "".join(
        f"<h3>{html.escape(PREGUNTAS[clave])}</h3>"
        f"{_respuesta(respuestas.get(clave, ''))}"
        for clave in PREGUNTAS
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Plan de gestión del cambio · {html.escape(filial.nombre)}</title>
<style>{informe.ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Plan de gestión del cambio</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} ·
     Sesión 7 · Cierre del curso</p>
  <p>{html.escape(integrantes) if integrantes.strip()
      else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · La brecha entre entregar y cambiar</h2>
<div class="tarjetas">{tarjetas}</div>
<p>El {_pct(resultado["pct_conductual"])} del valor de este plan depende de
que personas concretas trabajen de otra manera. Esa parte no se instala: se
adopta o no se adopta. El resto son máquinas, y funcionan aunque a nadie le
guste.</p>
{aviso}

<h2>2 · A quién le toca</h2>
<p>Un plan no aterriza sobre una empresa: aterriza sobre puestos concretos.
La columna que importa es la última, porque explica por qué alguien se puede
oponer con toda la razón del mundo.</p>
{_tabla_actores(grupo)}
<p>El patrón que se repite en las cinco filiales: <strong>quien tiene que
cambiar casi nunca es quien se lleva el beneficio</strong>. Se le pide al
personal de tienda que prepare paquetes para que bajen las emisiones de
reparto, y al equipo de compras que complique su propio objetivo de precio.
La resistencia rara vez es irracional.</p>

<h2>3 · Las iniciativas más expuestas</h2>
{_tabla_riesgo(resultado)}

<h2>4 · El plan de cambio del grupo</h2>
{_tabla_palancas(plan)}
<p>Coste: {_num(resultado["coste"], 1)} puntos sobre un presupuesto de
{_num(resultado["presupuesto"], 1)}.
{"Dentro de presupuesto." if resultado["dentro_de_presupuesto"]
 else "<strong>Se sale del presupuesto.</strong>"}</p>

<h2>5 · El razonamiento del grupo</h2>
{secciones}

<h2>6 · El curso, en una página</h2>
<p>Siete sesiones sobre la misma empresa, cada una con una unidad de medida
distinta:</p>
<ul>
  <li><strong>Diagnóstico</strong> — encontrar el problema dominante de la
  filial en los datos, y descubrir que una cifra absoluta no dice nada hasta
  que se divide.</li>
  <li><strong>Descarbonización</strong> — un objetivo, un presupuesto y seis
  palancas que no valen lo mismo en dos filiales. Y al final, que el
  inventario que estaban mirando era una fracción del real.</li>
  <li><strong>Economía circular</strong> — la misma empresa medida en
  material: reciclar es lo más barato y no basta, porque una tonelada
  reciclada no equivale a una que nunca se generó.</li>
  <li><strong>Reporting ESG</strong> — contarlo sin engañar, que es más
  difícil que no mentir. Doble materialidad, y cinco tentaciones que son
  todas literalmente ciertas.</li>
  <li><strong>Ejecución</strong> — convertir tres planes en trabajo con
  capacidad insuficiente, y distinguir lo que se planifica de lo que se
  descubre.</li>
  <li><strong>Seguimiento</strong> — que abrir más cosas no termina más
  cosas, y que el mínimo tampoco es la respuesta.</li>
  <li><strong>Gestión del cambio</strong> — que se puede entregar un
  proyecto al 100 % y no cambiar nada.</li>
</ul>
<p>El proyecto de esta filial sumaba {resumen["esfuerzo_total"]} puntos de
esfuerzo sobre una capacidad de {_num(resumen["capacidad_sprint"])} por
sprint. Nunca cupo todo, y esa fue la premisa desde el principio: dirigir no
es hacerlo todo, es decidir qué no se hace y saber defenderlo.</p>

<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"plan_cambio_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
