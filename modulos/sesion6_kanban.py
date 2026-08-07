"""Sesión 6 · Seguimiento del proyecto con Kanban y enfoques híbridos.

Cuatro pasos. La Sesión 5 repartía el trabajo en cajas de tiempo; esta lo
deja fluir y se ocupa de seguirlo.

1. **El tablero** — las cuatro columnas y el estado real del proyecto.
2. **El límite de trabajo en curso** — el experimento que da la vuelta a la
   intuición: abrir menos cosas termina más cosas, pero abrir una sola deja
   al equipo parado.
3. **El sistema híbrido** — repartir el backlog entre lo que fluye y lo que
   se compromete con fecha, y medir cada mitad con su indicador.
4. **El seguimiento** — flujo acumulado, tiempo de ciclo e informe.

Este módulo es solo interfaz. El modelo vive en `core/kanban.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modulos import ayuda
from core import datos, filiales, informe_seguimiento, kanban, proyecto, tutor

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"
ROJO = "#B91C1C"

COLOR_ENFOQUE = {"Predictivo": GRANATE, "Iterativo": VERDE}
COLOR_COLUMNA = {"Pendiente": GRIS, "En curso": VERDE,
                 "Bloqueado": AMBAR, "Hecho": GRANATE}

PASOS = [
    ("El tablero", "Las cuatro columnas y dónde está cada cosa"),
    ("El límite de trabajo en curso", "El experimento que cambia la intuición"),
    ("El sistema híbrido", "Qué fluye y qué se compromete con fecha"),
    ("El seguimiento", "Flujo acumulado, tiempo de ciclo e informe"),
]


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _pct(valor: float, decimales: int = 0) -> str:
    return _num(valor * 100, decimales) + " %"


def _grafico(figura: go.Figure, alto: int = 320) -> None:
    figura.update_layout(
        height=alto, margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    figura.update_xaxes(showgrid=False)
    figura.update_yaxes(gridcolor="#E2E8F0")
    st.plotly_chart(figura, use_container_width=True)


def _respuesta(clave: str, etiqueta: str, grupo: str,
               ayuda: str = "", alto: int = 100) -> None:
    st.session_state.setdefault("respuestas6", {})
    valor = st.text_area(
        etiqueta,
        value=st.session_state["respuestas6"].get(clave, ""),
        key=f"s6_{clave}", height=alto, help=ayuda or None,
        placeholder="Escribid aquí…",
    )
    st.session_state["respuestas6"][clave] = valor
    _tutor(clave, grupo)


def _tutor(clave: str, grupo: str) -> None:
    """Delegado en el panel compartido: ver `modulos/ayuda.py`."""
    ayuda.pregunta(clave, grupo, 6, "respuestas6")


def _limite_elegido(grupo: str) -> int:
    return int(st.session_state.get("wip6", 4))


# --------------------------------------------------------------------------
# Paso 1 · El tablero
# --------------------------------------------------------------------------

def _paso_tablero(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    resultado = kanban.simular_flujo(grupo, _limite_elegido(grupo))

    st.markdown(f"### El tablero de {filial.nombre}")
    st.markdown(
        "En la sesión anterior repartisteis el trabajo en cajas de dos "
        "semanas. Un tablero no reparte: **tira**. Cuando se termina algo, "
        "entra lo siguiente. Y lo único que hay que decidir es cuántas cosas "
        "puede haber abiertas a la vez."
    )

    columnas = st.columns(4)
    for columna, contenedor in zip(kanban.COLUMNAS, columnas):
        with contenedor:
            st.markdown(f"**{columna.nombre}**")
            st.caption(columna.explicacion)

    st.divider()
    st.markdown("### Dónde está cada iniciativa")
    st.caption(
        f"Con un límite de {resultado['limite_wip']} tareas abiertas y "
        f"{_num(resultado['capacidad_semanal'], 2)} puntos de capacidad "
        f"semanal, después de {kanban.SEMANAS} semanas."
    )

    tabla = kanban.tabla_tablero(grupo, resultado)
    for columna in ["Hecho", "En curso", "Pendiente"]:
        del_estado = tabla[tabla["estado"] == columna]
        if del_estado.empty:
            continue
        st.markdown(f"**{columna}** — {len(del_estado)} iniciativas")
        marco = pd.DataFrame([{
            "Iniciativa": fila.nombre,
            "Cómo se gestiona": fila.enfoque,
            "Esfuerzo": fila.esfuerzo,
            "Valor": fila.valor,
            "Avance": _pct(fila.avance),
            "Semanas que tardó": (_num(fila.ciclo, 0)
                                  if fila.ciclo is not None else "—"),
        } for fila in del_estado.itertuples()])
        st.dataframe(marco, hide_index=True, use_container_width=True)

    st.info(
        "**Fijaos en la columna Bloqueado.** Toda iniciativa espera a alguien "
        "cuando se abre: el proveedor que tiene que presupuestar, el permiso "
        "que tiene que salir, el proveedor al que hay que pedirle un dato. "
        "Mientras espera **ocupa sitio en el tablero y no avanza**. Eso va a "
        "resultar decisivo en el paso siguiente.",
        icon="⏸️",
    )

    st.divider()
    _respuesta(
        "tablero",
        "Mirad lo que está en curso al final de las doce semanas. ¿Qué os "
        "dice de cómo se está trabajando?",
        grupo, alto=100,
    )


# --------------------------------------------------------------------------
# Paso 2 · El límite de trabajo en curso
# --------------------------------------------------------------------------

def _paso_wip(grupo: str) -> None:
    st.markdown("### ¿Cuántas cosas abrimos a la vez?")
    st.markdown(
        "Es la única decisión de un tablero, y casi nadie la toma en serio. "
        "Probad varios límites y mirad qué pasa."
    )

    st.session_state.setdefault("wip6", 4)
    limite = st.select_slider(
        "Límite de trabajo en curso (WIP)",
        options=kanban.LIMITES_OFRECIDOS,
        value=st.session_state["wip6"],
        key="wip6_control",
    )
    st.session_state["wip6"] = limite

    resultado = kanban.simular_flujo(grupo, limite)
    st.session_state["resultado6"] = resultado

    a, b, c, d = st.columns(4)
    a.metric("Terminadas", len(resultado["terminadas"]))
    b.metric("Valor entregado", resultado["valor_entregado"])
    c.metric("Tiempo de ciclo medio",
             f'{_num(resultado["tiempo_de_ciclo"], 1)} semanas',
             help="Desde que una tarea se abre hasta que se termina.")
    d.metric("Eficiencia del equipo",
             _pct(resultado["eficiencia_media"]),
             help="Lo que queda después de descontar la multitarea.")

    barrido = kanban.barrido_wip(grupo)
    optimo = kanban.wip_optimo(grupo)

    figura = go.Figure()
    figura.add_bar(
        x=barrido["limite_wip"], y=barrido["valor_entregado"],
        name="Valor entregado",
        marker_color=[GRANATE if w == limite else GRIS
                      for w in barrido["limite_wip"]],
    )
    figura.add_scatter(
        x=barrido["limite_wip"], y=barrido["tiempo_de_ciclo"],
        name="Tiempo de ciclo (semanas)", yaxis="y2",
        line=dict(color=AMBAR, width=3), mode="lines+markers",
    )
    figura.update_layout(
        xaxis_title="Límite de trabajo en curso",
        yaxis_title="Valor entregado",
        yaxis2=dict(title="Semanas", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", y=1.12),
    )
    _grafico(figura, alto=380)

    st.dataframe(pd.DataFrame([{
        "Límite": fila.limite_wip,
        "Terminadas": fila.terminadas,
        "Valor": fila.valor_entregado,
        "Tiempo de ciclo": _num(fila.tiempo_de_ciclo, 1) + " sem",
        "Entregas por semana": _num(fila.throughput, 2),
        "Eficiencia": _pct(fila.eficiencia_media),
    } for fila in barrido.itertuples()]), hide_index=True,
        use_container_width=True)

    if limite == optimo:
        st.success(
            f"**Habéis dado con vuestro óptimo: {optimo}.** Ni el mínimo ni "
            f"el máximo. Y no es el mismo en las cinco filiales.",
            icon="✔️",
        )
    elif limite < optimo:
        st.warning(
            f"**Con {limite} abiertas el equipo se queda parado esperando.** "
            f"Cuando la única tarea abierta está bloqueada, no hay nada más "
            f"en lo que trabajar. Probad a subir el límite.",
            icon="⏸️",
        )
    else:
        st.error(
            f"**Con {limite} abiertas todo avanza a la vez y no termina "
            f"nada.** La capacidad se reparte y la multitarea os está "
            f"costando un {_pct(1 - resultado['eficiencia_media'])} del "
            f"equipo. Probad a bajar el límite.",
            icon="⚠️",
        )

    with st.expander("La ley de Little, comprobada con vuestros números"):
        little = kanban.ley_de_little(resultado)
        st.markdown(
            "**Tiempo de ciclo = trabajo en curso ÷ ritmo de entrega.** No es "
            "una regla aproximada ni una metáfora: es una identidad que se "
            "cumple en cualquier sistema estable."
        )
        a, b, c = st.columns(3)
        a.metric("Trabajo en curso medio", _num(little["wip_medio"], 2))
        b.metric("Entregas por semana", _num(little["throughput"], 2))
        c.metric("Tiempo de ciclo previsto",
                 f'{_num(little["ciclo_previsto"], 1)} sem',
                 delta=f'Real: {_num(little["ciclo_real"], 1)}')
        st.caption(
            f"Desviación: {_pct(little['desviacion'])}. Donde más se desvía "
            f"es porque el sistema no está en régimen estable: al terminar "
            f"las doce semanas quedan tareas abiertas. La ley describe "
            f"sistemas estables, y saber cuándo no se aplica una herramienta "
            f"vale tanto como saber usarla."
        )
        st.info(
            "**Lo importante es lo que implica.** Si queréis entregar antes "
            "y no podéis trabajar más rápido, solo os queda una palanca: "
            "empezar menos cosas a la vez.",
            icon="🔑",
        )

    st.divider()
    _respuesta(
        "wip",
        "¿Cuál es vuestro límite óptimo y por qué ese? ¿Qué pasa por debajo "
        "y qué pasa por encima?",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 3 · El sistema híbrido
# --------------------------------------------------------------------------

def _paso_hibrido(grupo: str) -> None:
    catalogo = proyecto.por_codigo(grupo)

    st.markdown("### No todo va al tablero")
    st.markdown(
        "En la sesión anterior separasteis lo predictivo de lo iterativo. "
        "Ahora hay que hacer algo con esa distinción: **decidir qué se "
        "gestiona con flujo y qué se gestiona con fecha**, y seguir cada "
        "mitad con un indicador distinto."
    )

    izquierda, derecha = st.columns(2)
    izquierda.markdown(
        "**Lo que va al tablero**\n\nSe sigue por tiempo de ciclo y por lo "
        "que entrega. No tiene fecha comprometida porque no se sabe cuánto "
        "va a costar hasta que se prueba. Preguntar «¿para cuándo?» aquí es "
        "pedir una cifra inventada."
    )
    derecha.markdown(
        "**Lo que va con fecha**\n\nTiene proveedor, presupuesto y un hito "
        "comprometido. Se sigue por puntualidad: llega o no llega. Meterlo "
        "en un tablero de flujo no lo acelera, y además ocupa un hueco "
        "mientras espera al proveedor."
    )

    st.divider()
    st.markdown("### Repartid vuestro backlog")

    st.session_state.setdefault("flujo6", kanban.reparto_recomendado(grupo))
    en_flujo = list(st.session_state["flujo6"])

    for iniciativa in sorted(catalogo.values(), key=lambda i: i.nombre):
        etiqueta = (
            f"{iniciativa.nombre} — {iniciativa.esfuerzo} puntos · "
            f"{iniciativa.enfoque}"
        )
        marcado = st.checkbox(
            etiqueta, value=iniciativa.codigo in en_flujo,
            key=f"s6_flujo_{iniciativa.codigo}",
            help=iniciativa.porque,
        )
        if marcado and iniciativa.codigo not in en_flujo:
            en_flujo.append(iniciativa.codigo)
        if not marcado and iniciativa.codigo in en_flujo:
            en_flujo.remove(iniciativa.codigo)
    st.caption("Marcado = va al tablero de flujo. Sin marcar = va con fecha.")

    st.session_state["flujo6"] = en_flujo

    evaluacion = kanban.evaluar_hibrido(grupo, en_flujo, _limite_elegido(grupo))
    st.session_state["hibrido6"] = evaluacion

    st.divider()
    a, b, c = st.columns(3)
    a.metric("Al tablero", len(evaluacion["en_flujo"]))
    b.metric("Con fecha comprometida", len(evaluacion["con_fecha"]))
    c.metric("Hitos cumplidos", _pct(evaluacion["puntualidad"]))

    izquierda, derecha = st.columns(2)
    with izquierda:
        st.markdown("**Indicadores del tablero**")
        st.metric("Tiempo de ciclo",
                  f'{_num(evaluacion["flujo"]["tiempo_de_ciclo"], 1)} sem')
        st.metric("Entregadas", len(evaluacion["flujo"]["terminadas"]))
    with derecha:
        st.markdown("**Indicadores de los hitos**")
        st.metric("Puntualidad", _pct(evaluacion["puntualidad"]))
        st.metric("Hitos incumplidos", len(evaluacion["hitos_incumplidos"]))

    if evaluacion["obras_en_flujo"]:
        nombres = ", ".join(catalogo[c].nombre
                            for c in evaluacion["obras_en_flujo"])
        st.error(
            f"**Habéis metido obras en el tablero:** {nombres}. Una obra no "
            f"fluye: espera al proveedor mientras ocupa un hueco de vuestro "
            f"límite de WIP. Y a cambio no ganáis nada, porque su fecha ya "
            f"estaba comprometida con un tercero.",
            icon="⚠️",
        )
    if evaluacion["iterativas_con_fecha"]:
        nombres = ", ".join(catalogo[c].nombre
                            for c in evaluacion["iterativas_con_fecha"])
        st.warning(
            f"**Habéis puesto fecha a lo que no se puede saber:** {nombres}. "
            f"Comprometer una fecha para algo que hay que descubrir "
            f"probando produce una cifra que nadie se cree y que todos "
            f"repiten en el comité.",
            icon="⚠️",
        )
    if (not evaluacion["obras_en_flujo"]
            and not evaluacion["iterativas_con_fecha"]):
        st.success(
            "**El reparto es coherente:** al tablero lo que se descubre "
            "trabajando, con fecha lo que ya está cerrado. Eso es un sistema "
            "híbrido, y no consiste en usar las dos cosas a la vez sino en "
            "saber cuál va dónde.",
            icon="✔️",
        )

    st.divider()
    _respuesta(
        "hibrido",
        "¿Qué habéis puesto con fecha y por qué? ¿Qué le contestaríais a un "
        "director que os pide una fecha para lo que está en el tablero?",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 4 · El seguimiento
# --------------------------------------------------------------------------

def _paso_seguimiento(grupo: str) -> None:
    limite = _limite_elegido(grupo)
    resultado = kanban.simular_flujo(grupo, limite)
    st.session_state["resultado6"] = resultado

    st.markdown("### El diagrama de flujo acumulado")
    st.caption(
        "Es el gráfico de seguimiento de un tablero. Cada banda es una "
        "columna, y lo que importa no son las bandas: es su grosor."
    )

    historia = pd.DataFrame(resultado["historia"])
    largo = historia.melt(
        id_vars="semana",
        value_vars=["hecho", "en_curso", "bloqueado", "pendiente"],
        var_name="Columna", value_name="Iniciativas",
    )
    nombres = {"hecho": "Hecho", "en_curso": "En curso",
               "bloqueado": "Bloqueado", "pendiente": "Pendiente"}
    largo["Columna"] = largo["Columna"].map(nombres)

    figura = px.area(
        largo, x="semana", y="Iniciativas", color="Columna",
        color_discrete_map=COLOR_COLUMNA,
        labels={"semana": "Semana"},
        category_orders={"Columna": ["Hecho", "En curso", "Bloqueado",
                                     "Pendiente"]},
    )
    _grafico(figura, alto=380)

    st.info(
        "**Cómo se lee.** Si la banda de «En curso» engorda con el tiempo, "
        "estáis abriendo más de lo que cerráis y el tiempo de ciclo va a "
        "subir. Si la de «Bloqueado» engorda, el problema no es vuestro "
        "equipo: es de quien tiene que contestaros. Y si la de «Hecho» sube "
        "a escalones y no en línea, es que entregáis a golpes en vez de "
        "seguido.",
        icon="📈",
    )

    st.divider()
    st.markdown("### Vuestros indicadores de seguimiento")
    a, b, c, d = st.columns(4)
    a.metric("Tiempo de ciclo",
             f'{_num(resultado["tiempo_de_ciclo"], 1)} sem')
    b.metric("Entregas por semana", _num(resultado["throughput"], 2))
    c.metric("Trabajo en curso medio", _num(resultado["wip_medio"], 1))
    d.metric("Sin terminar", len(resultado["sin_terminar"]))

    tabla = kanban.tabla_tablero(grupo, resultado)
    hechas = tabla[tabla["estado"] == "Hecho"].sort_values("ciclo")
    if not hechas.empty:
        figura = px.bar(
            hechas, x="ciclo", y="nombre", orientation="h", color="enfoque",
            color_discrete_map=COLOR_ENFOQUE,
            labels={"ciclo": "Semanas desde que se abrió", "nombre": "",
                    "enfoque": "Cómo se gestiona"},
        )
        _grafico(figura, alto=340)
        st.caption(
            "Las barras largas no siempre son las tareas grandes: a menudo "
            "son las que se abrieron pronto y se quedaron esperando."
        )

    st.divider()
    _respuesta(
        "seguimiento",
        "Con este diagrama delante, ¿qué le diríais al comité en una "
        "reunión de seguimiento de cinco minutos?",
        grupo, alto=110,
    )
    _respuesta(
        "mejora",
        "¿Qué cambiaríais la semana que viene para que el tiempo de ciclo "
        "baje?",
        grupo, alto=90,
    )

    st.divider()
    _descargar(grupo, resultado)


def _descargar(grupo: str, resultado: dict) -> None:
    st.markdown("### Llevaos el informe de seguimiento")

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
        key="integrantes_s6",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = informe_seguimiento.generar(
            grupo, resultado, st.session_state.get("hibrido6"),
            st.session_state.get("respuestas6", {}), integrantes,
        )
    except Exception as error:
        st.error(
            "No he podido generar el informe. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar el informe de seguimiento",
        data=html.encode("utf-8"),
        file_name=informe_seguimiento.nombre_de_fichero(grupo),
        mime="text/html", type="primary", use_container_width=True,
    )
    st.caption("Descargadlo antes de cerrar la pestaña: no se guarda solo.")


# --------------------------------------------------------------------------
# Punto de entrada
# --------------------------------------------------------------------------

def mostrar(grupo: str) -> None:
    if not datos.hay_datos():
        st.error(
            "No encuentro los datos de RetailNova. Avisad al profesor: hay que "
            "generarlos con `python -m datos.retailnova.generador`."
        )
        return

    st.markdown("## Sesión 6 · Seguimiento con Kanban y enfoques híbridos")
    st.caption(
        "El proyecto ya está en marcha. Hoy toca seguirlo: cuántas cosas "
        "abrir a la vez, qué fluye, qué lleva fecha y cómo se cuenta."
    )

    st.session_state.setdefault("paso6", 0)
    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    elegido = st.radio(
        "Paso", etiquetas, index=st.session_state["paso6"],
        horizontal=True, label_visibility="collapsed",
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso6"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    ayuda.panel(6)
    st.divider()

    if paso == 0:
        _paso_tablero(grupo)
    elif paso == 1:
        _paso_wip(grupo)
    elif paso == 2:
        _paso_hibrido(grupo)
    else:
        _paso_seguimiento(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True,
                                    key="s6_anterior"):
        st.session_state["paso6"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True,
        key="s6_siguiente",
    ):
        st.session_state["paso6"] = paso + 1
        st.rerun()
