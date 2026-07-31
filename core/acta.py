"""El acta del proyecto que se lleva cada grupo de la Sesión 5.

Mismo criterio que los otros documentos: HTML autocontenido, imprimible a PDF
y sin dependencias nuevas.

Lo que distingue a este documento de los anteriores: además de lo que el
grupo consiguió, **imprime lo que dejó a medias**. El trabajo empezado y no
terminado no aparece en ningún informe de proyecto y es la forma más cara de
gastar un presupuesto.
"""

from __future__ import annotations

import html
from datetime import datetime

from core import filiales, informe, proyecto

PREGUNTAS = {
    "clasificacion": "¿Por qué esas dos iniciativas no se pueden gestionar "
                     "igual?",
    "orden": "¿Por qué este orden? ¿Qué se dejó fuera?",
    "replanificacion": "¿Qué cambiaríais tras conocer los contratiempos?",
    "aprendizaje": "Si empezarais mañana, ¿qué haríais distinto en el primer "
                   "sprint?",
    "hibrido": "¿Qué parte llevaríais con sprints y qué parte con un plan "
               "cerrado?",
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


def _tabla_sprints(grupo: str, resultado: dict) -> str:
    catalogo = proyecto.por_codigo(grupo)
    filas = []
    for sprint in resultado["detalle"]:
        entregado = ", ".join(
            catalogo[c].nombre for c in sprint["entregadas"]
        ) or "—"
        eventos = "; ".join(e.titulo for e in sprint["eventos"]) or "—"
        filas.append(
            f'<tr><td class="num">{sprint["sprint"]}</td>'
            f"<td>{html.escape(entregado)}</td>"
            f"<td>{html.escape(eventos)}</td>"
            f'<td class="num">{_num(sprint["usada"])} / '
            f'{_num(sprint["capacidad"])}</td>'
            f'<td class="num">{sprint["valor_acumulado"]}</td></tr>'
        )
    return (
        '<table><thead><tr><th class="num">Sprint</th><th>Entregado</th>'
        "<th>Incidencias</th><th class='num'>Capacidad usada</th>"
        "<th class='num'>Valor acumulado</th></tr></thead><tbody>"
        + "".join(filas) + "</tbody></table>"
    )


def _tabla_pendientes(grupo: str, resultado: dict) -> str:
    catalogo = proyecto.por_codigo(grupo)
    if not resultado["sin_entregar"]:
        return "<p>Se entregó el backlog completo.</p>"

    filas = []
    for codigo in resultado["sin_entregar"]:
        iniciativa = catalogo[codigo]
        avance = min(1.0, resultado["progreso"].get(codigo, 0) / iniciativa.esfuerzo)
        clase = ' class="propia"' if avance > 0 else ""
        filas.append(
            f"<tr{clase}><td>{html.escape(iniciativa.nombre)}</td>"
            f"<td>{html.escape(iniciativa.enfoque)}</td>"
            f'<td class="num">{iniciativa.esfuerzo}</td>'
            f'<td class="num">{iniciativa.valor}</td>'
            f'<td class="num">{_pct(avance)}</td></tr>'
        )
    return (
        "<table><thead><tr><th>Iniciativa</th><th>Cómo se gestiona</th>"
        '<th class="num">Esfuerzo</th><th class="num">Valor perdido</th>'
        '<th class="num">Avance</th></tr></thead><tbody>'
        + "".join(filas) + "</tbody></table>"
    )


def generar(grupo: str, resultado: dict, respuestas: dict[str, str],
            integrantes: str = "") -> str:
    """Construye el acta completa en HTML."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%d/%m/%Y")
    resumen = proyecto.resumen(grupo)

    a_medias = [
        c for c in resultado["sin_entregar"]
        if resultado["progreso"].get(c, 0) > 0
    ]

    tarjetas = "".join([
        _tarjeta("Iniciativas del backlog", str(resumen["iniciativas"])),
        _tarjeta("Entregadas", str(len(resultado["entregadas"]))),
        _tarjeta("A medias", str(len(a_medias))),
        _tarjeta("Valor entregado",
                 f'{resultado["valor_entregado"]} de {resultado["valor_total"]}'),
        _tarjeta("Valor al sprint 3", str(resultado["valor_en_sprint_3"])),
        _tarjeta("Capacidad por sprint", _num(resultado["capacidad_base"])),
    ])

    secciones = "".join(
        f"<h3>{html.escape(PREGUNTAS[clave])}</h3>"
        f"{_respuesta(respuestas.get(clave, ''))}"
        for clave in PREGUNTAS
    )

    aviso_medias = ""
    if a_medias:
        aviso_medias = (
            f"<p><strong>Quedaron {len(a_medias)} iniciativas empezadas y sin "
            f"terminar.</strong> Es trabajo pagado que no ha entregado ningún "
            f"resultado. En un proyecto real esa cifra es la que primero "
            f"pregunta un comité, y la que peor se defiende.</p>"
        )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Acta del proyecto · {html.escape(filial.nombre)}</title>
<style>{informe.ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Acta de ejecución del proyecto</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} ·
     Sesión 5</p>
  <p>{html.escape(integrantes) if integrantes.strip()
      else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · Resultado</h2>
<div class="tarjetas">{tarjetas}</div>
<p>El backlog de la filial necesitaba
{_num(resumen["sprints_necesarios"])} sprints y había
{proyecto.SPRINTS}. Ninguna metodología arregla esa diferencia: lo único que
se puede decidir es qué entra, en qué orden y qué se queda fuera.</p>
{aviso_medias}

<h2>2 · Los seis sprints</h2>
{_tabla_sprints(grupo, resultado)}

<h2>3 · Lo que no se entregó</h2>
{_tabla_pendientes(grupo, resultado)}

<h2>4 · Predictivo e iterativo</h2>
<p>El {_pct(resumen["pct_predictivo"])} del esfuerzo de este proyecto es
predictivo: obra, compra de equipo e instalación, con alcance cerrado y fecha.
El resto solo se puede abordar por tandas, midiendo y corrigiendo. Gestionar
las dos mitades con el mismo método es el error más caro de la dirección de
proyectos, y se comete en las dos direcciones: planificando a doce meses lo
que no se puede saber, y convocando retrospectivas quincenales sobre una obra
que solo necesita que llegue el instalador.</p>

<h2>5 · El razonamiento del grupo</h2>
{secciones}

<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia. El backlog se deriva de las palancas analizadas en las
  sesiones 2 y 3, con sus costes e impactos reales.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"acta_proyecto_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
