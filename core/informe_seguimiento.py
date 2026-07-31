"""Informe de seguimiento que se lleva cada grupo de la Sesión 6.

Mismo criterio que los demás documentos: HTML autocontenido, imprimible a PDF
y sin dependencias nuevas.

Este documento tiene un propósito distinto de los anteriores: los otros
resumían una decisión, y este **rinde cuentas de un proyecto en marcha**. Por
eso lleva las dos mitades del sistema híbrido medidas con indicadores
distintos, que es exactamente lo que un comité de seguimiento debería exigir
y casi nunca exige.
"""

from __future__ import annotations

import html
from datetime import datetime

from core import filiales, informe, kanban, proyecto

PREGUNTAS = {
    "tablero": "¿Qué dice lo que está en curso al final de las doce semanas?",
    "wip": "¿Cuál es vuestro límite óptimo y por qué ese?",
    "hibrido": "¿Qué va con fecha y qué contestáis a quien pide una fecha "
               "para lo que está en el tablero?",
    "seguimiento": "¿Qué le diríais al comité en cinco minutos?",
    "mejora": "¿Qué cambiaríais la semana que viene?",
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


def _tabla_flujo(resultado: dict) -> str:
    filas = []
    for semana in resultado["historia"]:
        filas.append(
            f'<tr><td class="num">{semana["semana"]}</td>'
            f'<td class="num">{semana["pendiente"]}</td>'
            f'<td class="num">{semana["en_curso"]}</td>'
            f'<td class="num">{semana["bloqueado"]}</td>'
            f'<td class="num">{semana["hecho"]}</td>'
            f'<td class="num">{_pct(semana["eficiencia"])}</td></tr>'
        )
    return (
        '<table><thead><tr><th class="num">Semana</th>'
        '<th class="num">Pendiente</th><th class="num">En curso</th>'
        '<th class="num">Bloqueado</th><th class="num">Hecho</th>'
        '<th class="num">Eficiencia</th></tr></thead><tbody>'
        + "".join(filas) + "</tbody></table>"
    )


def _tabla_entregas(grupo: str, resultado: dict) -> str:
    catalogo = proyecto.por_codigo(grupo)
    if not resultado["terminadas"]:
        return "<p>No se terminó ninguna iniciativa.</p>"
    filas = []
    for codigo in resultado["terminadas"]:
        iniciativa = catalogo[codigo]
        ciclo = resultado["salida"][codigo] - resultado["entrada"][codigo] + 1
        filas.append(
            f"<tr><td>{html.escape(iniciativa.nombre)}</td>"
            f"<td>{html.escape(iniciativa.enfoque)}</td>"
            f'<td class="num">{resultado["entrada"][codigo]}</td>'
            f'<td class="num">{resultado["salida"][codigo]}</td>'
            f'<td class="num">{ciclo}</td></tr>'
        )
    return (
        "<table><thead><tr><th>Iniciativa</th><th>Cómo se gestiona</th>"
        '<th class="num">Se abrió</th><th class="num">Se cerró</th>'
        '<th class="num">Semanas</th></tr></thead><tbody>'
        + "".join(filas) + "</tbody></table>"
    )


def _seccion_hibrido(grupo: str, evaluacion: dict | None) -> str:
    if not evaluacion:
        return (
            "<h2>4 · El sistema híbrido</h2>"
            "<p>El grupo no llegó a repartir el backlog entre flujo y "
            "compromiso de fecha.</p>"
        )
    catalogo = proyecto.por_codigo(grupo)
    avisos = []
    if evaluacion["obras_en_flujo"]:
        nombres = ", ".join(catalogo[c].nombre
                            for c in evaluacion["obras_en_flujo"])
        avisos.append(
            f"<p><strong>Obras en el tablero de flujo:</strong> {html.escape(nombres)}. "
            f"Una obra no fluye: espera al proveedor mientras ocupa un hueco "
            f"del límite de trabajo en curso.</p>"
        )
    if evaluacion["iterativas_con_fecha"]:
        nombres = ", ".join(catalogo[c].nombre
                            for c in evaluacion["iterativas_con_fecha"])
        avisos.append(
            f"<p><strong>Fecha comprometida sobre lo que hay que descubrir:</strong> "
            f"{html.escape(nombres)}. La cifra resultante no se la cree nadie "
            f"y todos la repiten en el comité.</p>"
        )
    if not avisos:
        avisos.append(
            "<p>El reparto es coherente: al tablero lo que se descubre "
            "trabajando y con fecha lo que ya está cerrado.</p>"
        )

    return f"""
<h2>4 · El sistema híbrido</h2>
<p>Las dos mitades del proyecto se siguen con indicadores distintos, y esa es
la idea entera. Lo que fluye se mide por tiempo de ciclo; lo que lleva fecha,
por puntualidad. Usar el mismo indicador para las dos es lo que vacía de
contenido la mayoría de los cuadros de mando de proyecto.</p>
<div class="tarjetas">
  {_tarjeta("Al tablero", str(len(evaluacion["en_flujo"])))}
  {_tarjeta("Con fecha", str(len(evaluacion["con_fecha"])))}
  {_tarjeta("Tiempo de ciclo",
            _num(evaluacion["flujo"]["tiempo_de_ciclo"], 1) + " sem")}
  {_tarjeta("Puntualidad de hitos", _pct(evaluacion["puntualidad"]))}
</div>
{"".join(avisos)}
"""


def generar(grupo: str, resultado: dict, hibrido: dict | None,
            respuestas: dict[str, str], integrantes: str = "") -> str:
    """Construye el informe de seguimiento completo en HTML."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%d/%m/%Y")
    little = kanban.ley_de_little(resultado)
    optimo = kanban.wip_optimo(grupo)

    tarjetas = "".join([
        _tarjeta("Límite de trabajo en curso", str(resultado["limite_wip"])),
        _tarjeta("Iniciativas terminadas", str(len(resultado["terminadas"]))),
        _tarjeta("Valor entregado",
                 f'{resultado["valor_entregado"]} de {resultado["valor_total"]}'),
        _tarjeta("Tiempo de ciclo",
                 _num(resultado["tiempo_de_ciclo"], 1) + " semanas"),
        _tarjeta("Entregas por semana", _num(resultado["throughput"], 2)),
        _tarjeta("Eficiencia del equipo", _pct(resultado["eficiencia_media"])),
    ])

    secciones = "".join(
        f"<h3>{html.escape(PREGUNTAS[clave])}</h3>"
        f"{_respuesta(respuestas.get(clave, ''))}"
        for clave in PREGUNTAS
    )

    juicio = (
        f"El límite elegido ({resultado['limite_wip']}) coincide con el que "
        f"más valor entrega en esta filial."
        if resultado["limite_wip"] == optimo else
        f"El límite elegido ({resultado['limite_wip']}) no es el que más "
        f"valor entrega en esta filial: ese es {optimo}."
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Informe de seguimiento · {html.escape(filial.nombre)}</title>
<style>{informe.ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Informe de seguimiento del proyecto</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} ·
     Sesión 6</p>
  <p>{html.escape(integrantes) if integrantes.strip()
      else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · Resultado de {kanban.SEMANAS} semanas</h2>
<div class="tarjetas">{tarjetas}</div>
<p><strong>{html.escape(juicio)}</strong> Ni el mínimo ni el máximo: con una
sola tarea abierta el equipo se para cada vez que algo espera a un tercero, y
con demasiadas la capacidad se reparte y la multitarea se come el resto.</p>

<h2>2 · La ley de Little</h2>
<p>Tiempo de ciclo = trabajo en curso ÷ ritmo de entrega. Con
{_num(little["wip_medio"], 2)} tareas abiertas de media y
{_num(little["throughput"], 2)} entregas por semana, la ley predice
{_num(little["ciclo_previsto"], 1)} semanas de ciclo y el real fue
{_num(little["ciclo_real"], 1)}: una desviación del
{_pct(little["desviacion"])}, atribuible a que el sistema no está en régimen
estable porque al terminar quedan tareas abiertas.</p>
<p>Lo que implica es lo importante: si se quiere entregar antes y no se puede
trabajar más rápido, la única palanca que queda es <strong>empezar menos
cosas a la vez</strong>.</p>

<h2>3 · Lo que se entregó y cuándo</h2>
{_tabla_entregas(grupo, resultado)}

{_seccion_hibrido(grupo, hibrido)}

<h2>5 · El flujo, semana a semana</h2>
{_tabla_flujo(resultado)}
<p>Si la columna «En curso» engorda, se está abriendo más de lo que se cierra.
Si engorda la de «Bloqueado», el cuello de botella no está en el equipo sino
en quien tiene que responder.</p>

<h2>6 · El razonamiento del grupo</h2>
{secciones}

<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia. El backlog procede de las palancas analizadas en las
  sesiones 2 y 3.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"seguimiento_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
