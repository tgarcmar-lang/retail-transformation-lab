"""Informe de diagnóstico que se lleva cada grupo al terminar la sesión.

Produce un HTML autocontenido: se abre en cualquier navegador, se imprime a
PDF con Ctrl+P y no necesita conexión salvo para las tipografías. Se eligió
HTML y no Word ni PDF a propósito, para no añadir dependencias que puedan
romper el despliegue en Streamlit Cloud.

No importa Streamlit: así se puede generar y revisar sin levantar la app.
"""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd

from core import filiales, kpis

ESTILOS = """
:root { --tinta: #0F172A; --suave: #64748B; --borde: #E2E8F0;
        --acento: #0F766E; --alerta: #B91C1C; --fondo: #F8FAFC; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, sans-serif;
       color: var(--tinta); line-height: 1.55; max-width: 900px;
       margin: 0 auto; padding: 2.5rem 2rem; }
h1 { font-size: 1.9rem; margin: 0 0 .3rem 0; }
h2 { font-size: 1.25rem; margin: 2.4rem 0 .8rem 0;
     border-bottom: 2px solid var(--acento); padding-bottom: .35rem; }
h3 { font-size: 1rem; margin: 1.6rem 0 .5rem 0; color: var(--acento); }
.cabecera { border-left: 4px solid var(--acento); padding-left: 1rem;
            margin-bottom: 2rem; }
.cabecera p { color: var(--suave); margin: .2rem 0; }
table { width: 100%; border-collapse: collapse; margin: .8rem 0 1.4rem 0;
        font-size: .9rem; }
th { text-align: left; background: var(--fondo); font-weight: 600;
     padding: .5rem .6rem; border-bottom: 2px solid var(--borde); }
td { padding: .45rem .6rem; border-bottom: 1px solid var(--borde); }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
tr.propia { background: #ECFDF5; font-weight: 600; }
.tarjetas { display: flex; flex-wrap: wrap; gap: .8rem; margin: 1rem 0; }
.tarjeta { flex: 1 1 150px; border: 1px solid var(--borde); border-radius: 8px;
           padding: .75rem .9rem; background: var(--fondo); }
.tarjeta .etiqueta { font-size: .72rem; text-transform: uppercase;
                     letter-spacing: .04em; color: var(--suave); }
.tarjeta .cifra { font-size: 1.35rem; font-weight: 650; margin-top: .15rem; }
.respuesta { background: var(--fondo); border-left: 3px solid var(--acento);
             padding: .7rem 1rem; margin: .5rem 0 1.2rem 0;
             white-space: pre-wrap; border-radius: 0 6px 6px 0; }
.vacia { color: var(--suave); font-style: italic; }
.puesto { display: inline-block; min-width: 1.6rem; text-align: center;
          border-radius: 4px; padding: .05rem .35rem; font-size: .8rem;
          font-weight: 600; }
.p1 { background: #D1FAE5; color: #065F46; }
.p5 { background: #FEE2E2; color: var(--alerta); }
.pie { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--borde);
       color: var(--suave); font-size: .82rem; }
@media print { body { padding: 0; } h2 { page-break-after: avoid; }
               table { page-break-inside: avoid; } }
"""


def _euros(valor: float) -> str:
    """Formatea un importe con separador de miles español."""
    if abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:,.1f} M€".replace(",", "·").replace(".", ",").replace("·", ".")
    return f"{valor:,.0f} €".replace(",", ".")


def _numero(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _pct(valor: float, decimales: int = 1) -> str:
    return _numero(valor * 100, decimales) + " %"


def _formatear(valor: float, unidad: str) -> str:
    if unidad == "%":
        return _pct(valor)
    if unidad == "M€":
        return _numero(valor, 1) + " M€"
    if unidad == "€/m²":
        return _numero(valor, 0) + " €/m²"
    return f"{_numero(valor, 1)} {unidad}"


def _tarjeta(etiqueta: str, cifra: str) -> str:
    return (f'<div class="tarjeta"><div class="etiqueta">{html.escape(etiqueta)}</div>'
            f'<div class="cifra">{html.escape(cifra)}</div></div>')


def _respuesta(texto: str) -> str:
    limpio = (texto or "").strip()
    if not limpio:
        return '<div class="respuesta vacia">Sin responder.</div>'
    return f'<div class="respuesta">{html.escape(limpio)}</div>'


def _tabla_posicion(grupo: str, anio: int) -> str:
    tabla = kpis.posicion(grupo, anio)
    filas = []
    for fila in tabla.itertuples():
        clase = "p1" if fila.puesto == 1 else ("p5" if fila.puesto == 5 else "")
        filas.append(
            f"<tr><td>{html.escape(fila.indicador)}</td>"
            f'<td class="num">{_formatear(fila.valor, fila.unidad)}</td>'
            f'<td class="num">{_formatear(fila.media, fila.unidad)}</td>'
            f'<td class="num"><span class="puesto {clase}">{fila.puesto}º</span></td></tr>'
        )
    return (
        "<table><thead><tr><th>Indicador</th>"
        '<th class="num">Tu filial</th><th class="num">Media del grupo</th>'
        '<th class="num">Puesto</th></tr></thead><tbody>'
        + "".join(filas) + "</tbody></table>"
    )


def _tabla_comparativa(grupo: str, anio: int) -> str:
    tabla = kpis.comparativa(anio)
    columnas = [
        ("filial", "Filial", None),
        ("ventas_m_eur", "Ventas", "M€"),
        ("ventas_por_m2", "€/m²", "€/m²"),
        ("cuota_online", "Online", "%"),
        ("pct_km_en_vacio", "Km en vacío", "%"),
        ("intensidad_energetica", "Energía", "MWh/M€"),
        ("co2e_por_meur", "CO₂e", "t/M€"),
    ]
    cabecera = "".join(
        "<th{}>{}</th>".format(
            ' class="num"' if unidad else "", html.escape(titulo)
        )
        for _, titulo, unidad in columnas
    )
    filas = []
    for fila in tabla.itertuples():
        celdas = []
        for clave, _, unidad in columnas:
            valor = getattr(fila, clave)
            if unidad is None:
                celdas.append(f"<td>{html.escape(str(valor))}</td>")
            else:
                celdas.append(f'<td class="num">{_formatear(valor, unidad)}</td>')
        clase = ' class="propia"' if fila.grupo == grupo else ""
        filas.append(f"<tr{clase}>" + "".join(celdas) + "</tr>")
    return (f"<table><thead><tr>{cabecera}</tr></thead><tbody>"
            + "".join(filas) + "</tbody></table>")


def _tabla_huella(grupo: str, anio: int) -> str:
    tabla = kpis.huella(grupo, anio)
    filas = [
        f"<tr><td>{html.escape(fila.fuente)}</td>"
        f'<td class="num">Alcance {fila.alcance}</td>'
        f'<td class="num">{_numero(fila.co2e_t, 0)} t</td>'
        f'<td class="num">{_pct(fila.pct)}</td></tr>'
        for fila in tabla.itertuples()
    ]
    total = tabla["co2e_t"].sum()
    filas.append(
        f'<tr class="propia"><td>Total</td><td class="num"></td>'
        f'<td class="num">{_numero(total, 0)} t</td><td class="num">100,0 %</td></tr>'
    )
    return ("<table><thead><tr><th>Fuente</th><th class='num'>Alcance</th>"
            "<th class='num'>t CO₂e</th><th class='num'>Peso</th></tr></thead>"
            "<tbody>" + "".join(filas) + "</tbody></table>")


#: Preguntas del recorrido. La clave es la que usa el módulo para guardar la
#: respuesta en la sesión; el texto es el que ve el alumno y el que sale
#: impreso en el informe.
PREGUNTAS = {
    "paso2": (
        "¿Qué explica la forma de la curva de ventas de tu filial? "
        "Señala al menos dos causas."
    ),
    "paso3": (
        "¿Dónde está la mayor ineficiencia operativa de tu filial "
        "y cuánto te cuesta al año?"
    ),
    "paso4": (
        "¿De dónde salen realmente las emisiones de tu filial? "
        "¿Coincide con lo que esperabas antes de mirar los datos?"
    ),
    "diagnostico": (
        "En una frase: ¿cuál es el problema principal de tu filial?"
    ),
    "evidencia": (
        "¿Con qué tres datos concretos lo demuestras?"
    ),
    "coste": (
        "¿Cuánto le cuesta ese problema a la filial al año, en euros "
        "o en toneladas de CO₂?"
    ),
    "propuesta": (
        "¿Por dónde empezarías a resolverlo y por qué por ahí?"
    ),
}


def generar(grupo: str, respuestas: dict[str, str],
            integrantes: str = "", anio: int | None = None) -> str:
    """Construye el informe completo en HTML.

    `respuestas` son las que ha escrito el grupo durante la sesión, con las
    claves de PREGUNTAS. Las que falten salen marcadas como sin responder:
    el informe no miente sobre lo que el grupo hizo.
    """
    anio = anio or kpis.datos.ultimo_anio()
    filial = filiales.obtener(grupo)
    r = kpis.retrato(grupo, anio)
    c = kpis.canal(grupo, anio)
    log = kpis.logistica(grupo, anio)
    ene = kpis.energia_resumen(grupo, anio)
    cad = kpis.cadena_suministro(grupo, anio)
    inv = kpis.inventario_resumen(grupo, anio)
    cre = kpis.crecimiento(grupo)
    debiles = kpis.puntos_debiles(grupo, anio)
    fecha = datetime.now().strftime("%d/%m/%Y")

    tarjetas_retrato = "".join([
        _tarjeta("Ventas", _euros(r["ventas_eur"])),
        _tarjeta("Puntos de venta", str(r["puntos_de_venta"])),
        _tarjeta("Superficie", f'{_numero(r["superficie_m2"], 0)} m²'),
        _tarjeta("Ventas por m²", f'{_numero(r["ventas_por_m2"], 0)} €'),
        _tarjeta("Vehículos", str(r["vehiculos"])),
        _tarjeta("Centros logísticos", str(r["centros_logisticos"])),
    ])

    tarjetas_operacion = "".join([
        _tarjeta("Kilómetros en vacío", _pct(log["pct_km_en_vacio"])),
        _tarjeta("Entregas fallidas", _pct(log["pct_entregas_fallidas"])),
        _tarjeta("Plazo de proveedor", f'{_numero(cad["plazo_medio_dias"])} días'),
        _tarjeta("Cobertura de stock", f'{_numero(inv["dias_cobertura"])} días'),
        _tarjeta("Merma", _pct(inv["pct_merma"], 2)),
        _tarjeta("Energía por M€", f'{_numero(ene["intensidad_mwh_por_meur"], 0)} MWh'),
    ])

    lista_debiles = "".join(
        f"<li><strong>{html.escape(fila.indicador)}</strong>: "
        f"{_formatear(fila.valor, fila.unidad)} — puesto {fila.puesto} de 5 "
        f"(la mejor filial está en {_formatear(fila.mejor, fila.unidad)})</li>"
        for fila in debiles.itertuples()
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Diagnóstico · {html.escape(filial.nombre)}</title>
<style>{ESTILOS}</style></head><body>

<div class="cabecera">
  <h1>Informe de diagnóstico</h1>
  <p><strong>{html.escape(filial.nombre)}</strong> · Grupo {grupo} · Ejercicio {anio}</p>
  <p>{html.escape(integrantes) if integrantes.strip() else "Sin integrantes indicados"}</p>
  <p>Retail Transformation Lab · Escuela Politécnica · UCJC · {fecha}</p>
</div>

<h2>1 · Tu filial</h2>
<p>{html.escape(filial.perfil)}</p>
<div class="tarjetas">{tarjetas_retrato}</div>
<p>La filial creció un <strong>{_pct(cre["variacion"])}</strong> entre
{cre["anio_anterior"]} y {cre["anio_actual"]}. El canal online supone el
<strong>{_pct(c["cuota_online"])}</strong> de las ventas, con
{_numero(c["pedidos"], 0)} pedidos y un ticket medio de
{_numero(c["ticket_medio_online"])} €.</p>

<h2>2 · Cómo vende</h2>
<h3>{html.escape(PREGUNTAS["paso2"])}</h3>
{_respuesta(respuestas.get("paso2", ""))}

<h2>3 · Cómo opera</h2>
<div class="tarjetas">{tarjetas_operacion}</div>
<h3>{html.escape(PREGUNTAS["paso3"])}</h3>
{_respuesta(respuestas.get("paso3", ""))}

<h2>4 · Qué consume y qué emite</h2>
{_tabla_huella(grupo, anio)}
<h3>{html.escape(PREGUNTAS["paso4"])}</h3>
{_respuesta(respuestas.get("paso4", ""))}

<h2>5 · Tu filial frente a las demás</h2>
{_tabla_posicion(grupo, anio)}
<h3>Dónde queda peor tu filial</h3>
<ul>{lista_debiles}</ul>
<h3>Las cinco filiales, lado a lado</h3>
{_tabla_comparativa(grupo, anio)}

<h2>6 · Diagnóstico del grupo</h2>
<h3>{html.escape(PREGUNTAS["diagnostico"])}</h3>
{_respuesta(respuestas.get("diagnostico", ""))}
<h3>{html.escape(PREGUNTAS["evidencia"])}</h3>
{_respuesta(respuestas.get("evidencia", ""))}
<h3>{html.escape(PREGUNTAS["coste"])}</h3>
{_respuesta(respuestas.get("coste", ""))}
<h3>{html.escape(PREGUNTAS["propuesta"])}</h3>
{_respuesta(respuestas.get("propuesta", ""))}

<div class="pie">
  <p>Datos sintéticos generados para uso docente. RetailNova Europa es una
  empresa ficticia. Los datos cubren {cre["anio_anterior"]} y
  {cre["anio_actual"]}; todos los indicadores de este informe se refieren
  a {anio}.</p>
  <p>Para guardar como PDF: Archivo → Imprimir → Destino: Guardar como PDF.</p>
</div>

</body></html>"""


def nombre_de_fichero(grupo: str) -> str:
    """Nombre con el que se descarga el informe."""
    filial = filiales.obtener(grupo)
    fecha = datetime.now().strftime("%Y%m%d")
    return f"diagnostico_{filial.ciudad.lower()}_grupo{grupo}_{fecha}.html"
