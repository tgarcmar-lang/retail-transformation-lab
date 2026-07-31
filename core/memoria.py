"""La memoria de sostenibilidad que publica cada grupo en la Sesión 4.

Mismo criterio que los otros tres documentos: HTML autocontenido, imprimible
a PDF y sin dependencias nuevas.

Este documento tiene una particularidad: **lleva dentro la revisión del
verificador**. No es un entregable que el grupo se lleva y ya está; es un
entregable con una opinión de auditoría escrita debajo, que puede ser
favorable, con salvedades o desfavorable. Que el grupo vea su propia memoria
con las salvedades impresas es la mitad de la lección.
"""

from __future__ import annotations

import html
from datetime import datetime

from core import filiales, informe, reporting

PREGUNTAS = {
    "quien_lee": "¿Quién va a leer esta memoria y qué decisión va a tomar "
                 "con ella?",
    "material_fuera": "¿Qué asunto habéis dejado fuera y por qué no es "
                      "material para vuestra filial?",
    "peor_cifra": "¿Cuál es la peor cifra que publicáis? ¿Por qué la "
                  "publicáis igualmente?",
    "compromiso": "¿A qué os comprometéis para el año que viene, y cómo se "
                  "comprobará si lo habéis cumplido?",
}


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _respuesta(texto: str) -> str:
    limpio = (texto or "").strip()
    if not limpio:
        return '<div class="respuesta vacia">Sin responder.</div>'
    return f'<div class="respuesta">{html.escape(limpio)}</div>'


def _tarjeta(etiqueta: str, cifra: str) -> str:
    return (f'<div class="tarjeta"><div class="etiqueta">{html.escape(etiqueta)}</div>'
            f'<div class="cifra">{html.escape(cifra)}</div></div>')


def _tabla_indicadores(grupo: str, seleccion: list[str]) -> str:
    if not seleccion:
        return "<p>La memoria no publica ningún indicador.</p>"

    filas = []
    for codigo in seleccion:
        if codigo not in reporting.POR_CODIGO:
            continue
        indicador = reporting.POR_CODIGO[codigo]
        tema = reporting.POR_TEMA[indicador.tema]
        decimales = 0 if abs(reporting.valor(grupo, codigo)) >= 100 else 2
        filas.append(
            f"<tr><td>{html.escape(indicador.nombre)}</td>"
            f"<td>{html.escape(tema.dimension)}</td>"
            f"<td>{html.escape(indicador.estandar)}</td>"
            f'<td class="num">{_num(reporting.valor(grupo, codigo), decimales)}</td>'
            f"<td>{html.escape(indicador.unidad)}</td>"
            f"<td>{html.escape(indicador.calidad)}</td></tr>"
        )
    return (
        "<table><thead><tr><th>Indicador</th><th>Dimensión</th>"
        "<th>Estándar</th><th class='num'>Valor</th><th>Unidad</th>"
        "<th>Calidad del dato</th></tr></thead><tbody>"
        + "".join(filas) + "</tbody></table>"
    )


def _tabla_materialidad(grupo: str) -> str:
    tabla = reporting.matriz_materialidad(grupo)
    filas = []
    for fila in tabla.itertuples():
        marca = "Material" if fila.material else "No material"
        clase = ' class="propia"' if fila.material else ""
        filas.append(
            f"<tr{clase}><td>{html.escape(fila.nombre_tema)}</td>"
            f"<td>{html.escape(fila.dimension)}</td>"
            f'<td class="num">{_num(fila.impacto, 1)}</td>'
            f'<td class="num">{_num(fila.financiera, 1)}</td>'
            f"<td>{marca}</td></tr>"
        )
    return (
        "<table><thead><tr><th>Asunto</th><th>Dimensión</th>"
        "<th class='num'>Impacto</th><th class='num'>Financiera</th>"
        "<th>Conclusión</th></tr></thead><tbody>"
        + "".join(filas) + "</tbody></table>"
    )


def _declaraciones(declaraciones: dict[str, str]) -> str:
    filas = []
    for declaracion in reporting.DECLARACIONES:
        elegida = declaraciones.get(declaracion.codigo)
        texto = declaracion.opciones.get(elegida, "Sin decidir.")
        filas.append(
            f"<h3>{html.escape(declaracion.pregunta)}</h3>"
            f'<div class="respuesta">{html.escape(texto)}</div>'
        )
    return "".join(filas)


def _revision(evaluacion: dict) -> str:
    etiqueta = {
        "favorable": "Opinión favorable",
        "con salvedades": "Opinión con salvedades",
        "desfavorable": "Opinión desfavorable",
    }[evaluacion["opinion"]]

    if not evaluacion["hallazgos"]:
        cuerpo = (
            "<p>No se han identificado hallazgos. La memoria cubre todos los "
            "asuntos materiales de la filial y las declaraciones no inducen "
            "a error.</p>"
        )
    else:
        elementos = "".join(
            f"<li><strong>{html.escape(h['titulo'])}</strong> "
            f"({html.escape(h['gravedad'])}). {html.escape(h['detalle'])}</li>"
            for h in evaluacion["hallazgos"]
        )
        cuerpo = f"<ul>{elementos}</ul>"

    return f"""
<h2>5 · Revisión independiente</h2>
<p><strong>{html.escape(etiqueta)}</strong> — {evaluacion['graves']} hallazgos
graves y {evaluacion['salvedades']} salvedades. Cobertura de los asuntos
materiales: {_num(evaluacion['cobertura'] * 100, 0)} %.</p>
{cuerpo}
<p>Esta revisión es automática y forma parte del ejercicio. Una verificación
real comprobaría además la trazabilidad de cada cifra hasta su fuente, que es
la parte más costosa y la que más suele fallar.</p>
"""


def generar(grupo: str, seleccion: list[str], declaraciones: dict[str, str],
            evaluacion: dict, respuestas: dict[str, str],
            integrantes: str = "") -> str:
    """Construye la memoria completa en HTML."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%d/%m/%Y")
    materiales = evaluacion["temas_materiales"]

    tarjetas = "".join([
        _tarjeta("Asuntos materiales", str(len(materiales))),
        _tarjeta("Indicadores publicados", str(len(evaluacion["indicadores"]))),
        _tarjeta("Cobertura", _num(evaluacion["cobertura"] * 100, 0) + " %"),
        _tarjeta("Opinión", evaluacion["opinion"].capitalize()),
    ])

    secciones = "".join(
        f"<h3>{html.escape(PREGUNTAS[clave])}</h3>"
        f"{_respuesta(respuestas.get(clave, ''))}"
        for clave in PREGUNTAS
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Memoria de sostenibilidad · {html.escape(filial.nombre)}</title>
<style>{informe.ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Memoria de sostenibilidad</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} ·
     Sesión 4</p>
  <p>{html.escape(integrantes) if integrantes.strip()
      else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · Resumen</h2>
<div class="tarjetas">{tarjetas}</div>
<p>Esta memoria se ha elaborado siguiendo la lógica de los ESRS: se informa de
lo que resulta material para la filial, determinado por doble materialidad, y
se declara la calidad de cada dato. Los indicadores de transporte siguen el
enfoque de la norma <strong>ISO 14083:2023</strong>, construida sobre el GLEC
Framework, que es el estándar propio de las emisiones de la logística.</p>

<h2>2 · Análisis de doble materialidad</h2>
<p>Un asunto es material si lo es por impacto —lo que la filial provoca en el
entorno— o por sus consecuencias financieras. Basta con uno de los dos
caminos. Las notas van de 1 a 5 y se han calculado con los datos de
operación de la filial.</p>
{_tabla_materialidad(grupo)}

<h2>3 · Indicadores publicados</h2>
{_tabla_indicadores(grupo, evaluacion["indicadores"])}
<p>La columna de calidad del dato no es un adorno: un indicador de calidad
baja no debe usarse para reclamar una mejora, solo para saber dónde mirar.</p>

<h2>4 · Criterios de presentación</h2>
{_declaraciones(declaraciones)}

{_revision(evaluacion)}

<h2>6 · El razonamiento del grupo</h2>
{secciones}

<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia y esta memoria es un ejercicio de clase, no un documento
  con validez alguna.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"memoria_esg_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
