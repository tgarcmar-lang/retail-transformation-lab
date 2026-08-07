"""Sesión 7 · Gestión del cambio. El cierre del curso.

Cuatro pasos. Las seis sesiones anteriores eran racionales: había datos, un
objetivo y una respuesta mejor que las demás. Esta introduce lo único que no
tenían, que es gente.

1. **A quién le toca** — el mapa de actores del propio plan, y el patrón que
   lo explica todo: quien cambia no es quien se beneficia.
2. **Qué depende de las personas** — qué parte del plan es una máquina y qué
   parte es un hábito.
3. **Vuestro plan de cambio** — seis palancas con presupuesto, y la curva de
   adopción a doce meses.
4. **El cierre** — la brecha entre entregar y cambiar, y el documento final
   del curso.

Este módulo es solo interfaz. El modelo vive en `core/cambio.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modulos import ayuda
from core import cambio, datos, filiales, plan_cambio, proyecto

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"
ROJO = "#B91C1C"

PASOS = [
    ("A quién le toca", "El mapa de actores de vuestro plan"),
    ("Qué depende de las personas", "Máquinas frente a hábitos"),
    ("Vuestro plan de cambio", "Seis palancas y una curva de adopción"),
    ("El cierre", "La brecha entre entregar y cambiar"),
]


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _pct(valor: float, decimales: int = 0) -> str:
    return _num(valor * 100, decimales) + " %"


def _grafico(figura: go.Figure, alto: int = 340) -> None:
    figura.update_layout(
        height=alto, margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    figura.update_xaxes(showgrid=False)
    figura.update_yaxes(gridcolor="#E2E8F0")
    st.plotly_chart(figura, use_container_width=True)


def _respuesta(clave: str, etiqueta: str, grupo: str,
               pista: str = "", alto: int = 100) -> None:
    st.session_state.setdefault("respuestas7", {})
    valor = st.text_area(
        etiqueta,
        value=st.session_state["respuestas7"].get(clave, ""),
        key=f"s7_{clave}", height=alto, help=pista or None,
        placeholder="Escribid aquí…",
    )
    st.session_state["respuestas7"][clave] = valor
    ayuda.pregunta(clave, grupo, 7, "respuestas7")


def _plan(grupo: str) -> dict[str, float]:
    st.session_state.setdefault("plan7", {})
    return dict(st.session_state["plan7"])


# --------------------------------------------------------------------------
# Paso 1 · A quién le toca
# --------------------------------------------------------------------------

def _paso_actores(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    tabla = cambio.mapa_de_actores(grupo)

    st.markdown(f"### El plan de {filial.nombre} aterriza sobre gente")
    st.markdown(
        "Durante seis sesiones habéis optimizado, presupuestado, priorizado y "
        "medido. Todo correcto. Falta lo único que las hojas de cálculo no "
        "traen: **las personas que van a tener que trabajar de otra manera "
        "para que vuestro plan sirva de algo**."
    )

    figura = px.scatter(
        tabla, x="poder", y="impacto", text="nombre", size="empleados",
        size_max=55, color="impacto",
        color_continuous_scale=[[0, GRIS], [0.5, AMBAR], [1, GRANATE]],
        labels={"poder": "Poder para pararlo o impulsarlo →",
                "impacto": "Cuánto le toca de vuestro plan →"},
        range_x=[0.5, 5.5], range_y=[0.5, 5.5],
    )
    figura.update_traces(textposition="top center")
    figura.update_layout(coloraxis_showscale=False)
    figura.add_hline(y=3, line_dash="dash", line_color=GRIS)
    figura.add_vline(x=3, line_dash="dash", line_color=GRIS)
    _grafico(figura, alto=460)

    st.error(
        "**El patrón que hay que ver en ese gráfico.** Mirad quién está "
        "arriba —a quien más le toca— y comparadlo con quién está a la "
        "derecha —quien tiene poder para pararlo—. Casi nunca son los "
        "mismos. **Quien tiene que cambiar no es quien se lleva el "
        "beneficio**, y por eso la resistencia rara vez es irracional: le "
        "estáis pidiendo a alguien que trabaje más para el indicador de "
        "otro.",
        icon="⚖️",
    )

    for fila in tabla.head(4).itertuples():
        with st.container(border=True):
            izquierda, derecha = st.columns([3, 1])
            izquierda.markdown(f"**{fila.nombre}**")
            izquierda.caption(fila.descripcion)
            if fila.iniciativas:
                izquierda.caption(
                    "Le caen: " + ", ".join(fila.iniciativas[:4])
                )
            derecha.metric("Personas", fila.empleados)
            derecha.caption(f"Poder {fila.poder}/5 · le toca "
                            f"{_num(fila.impacto, 1)}/5")

    st.divider()
    _respuesta(
        "quien_pierde",
        "¿Quién trabaja más para que este plan salga, y quién se lleva el "
        "beneficio? ¿Coinciden?",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 2 · Qué depende de las personas
# --------------------------------------------------------------------------

def _paso_dependencia(grupo: str) -> None:
    exposicion = cambio.exposicion(grupo)
    catalogo = proyecto.por_codigo(grupo)

    st.markdown("### Máquinas y hábitos")
    st.markdown(
        "No todas vuestras iniciativas dependen igual de la gente. Una "
        "instalación nueva funciona la quiera alguien o no. Un cambio de "
        "hábito solo existe si miles de gestos diarios cambian."
    )

    a, b, c = st.columns(3)
    a.metric("Valor total del plan", _num(exposicion["valor_entregado"], 0))
    b.metric("Funciona solo", _num(exposicion["valor_automatico"], 0),
             help="Máquinas: se instalan y ya está.")
    c.metric("Depende de las personas",
             _num(exposicion["valor_conductual"], 0),
             delta=_pct(exposicion["pct_conductual"]) + " del plan",
             delta_color="inverse")

    filas = []
    for codigo in exposicion["entregadas"]:
        dependencia, roles, porque = cambio.CONDUCTA.get(codigo, (0.5, (), ""))
        filas.append({
            "nombre": catalogo[codigo].nombre,
            "dependencia": dependencia,
            "valor": catalogo[codigo].valor,
            "tipo": "Depende de la gente" if dependencia >= 0.5 else "Funciona sola",
            "porque": porque,
        })
    marco = pd.DataFrame(filas).sort_values("dependencia", ascending=True)

    figura = px.bar(
        marco, x="dependencia", y="nombre", orientation="h", color="tipo",
        color_discrete_map={"Funciona sola": VERDE,
                            "Depende de la gente": GRANATE},
        labels={"dependencia": "Cuánto depende de que la gente cambie",
                "nombre": "", "tipo": ""},
        hover_data=["valor"],
    )
    figura.update_xaxes(tickformat=".0%")
    _grafico(figura, alto=440)

    st.info(
        f"**El {_pct(exposicion['pct_conductual'])} del valor de vuestro plan "
        f"está en manos de otros.** Esa es vuestra exposición, y es distinta "
        f"en cada filial: quien apostó por comprar equipos está mucho más a "
        f"salvo que quien apostó por cambiar la forma de trabajar.",
        icon="🎯",
    )

    with st.expander("Por qué cada iniciativa depende lo que depende"):
        for fila in marco.sort_values("dependencia", ascending=False).itertuples():
            st.markdown(f"**{fila.nombre}** — {_pct(fila.dependencia)}")
            st.caption(fila.porque)

    st.divider()
    _respuesta(
        "resistencia",
        "Coged vuestra iniciativa más dependiente de las personas. ¿Cuál es "
        "la objeción más razonable que os va a poner quien tiene que "
        "ejecutarla?",
        grupo,
        pista="Razonable, no absurda. Si no se os ocurre ninguna buena, es "
              "que no habéis entendido su trabajo.",
        alto=110,
    )


# --------------------------------------------------------------------------
# Paso 3 · Vuestro plan de cambio
# --------------------------------------------------------------------------

def _paso_plan(grupo: str) -> None:
    st.markdown("### Seis palancas para que esto se adopte")
    st.caption(
        f"Presupuesto: {_num(cambio.presupuesto(grupo), 1)} puntos. "
        f"Comprarlo todo cuesta más del doble, así que hay que elegir."
    )

    st.session_state.setdefault("plan7", {})
    plan = {}

    izquierda, derecha = st.columns([3, 2])
    with izquierda:
        for palanca in cambio.PALANCAS:
            valor = st.slider(
                f"{palanca.nombre}",
                0, 100,
                int(st.session_state["plan7"].get(palanca.codigo, 0.0) * 100),
                step=10, key=f"s7_pal_{palanca.codigo}",
                help=palanca.descripcion,
            ) / 100
            plan[palanca.codigo] = valor
            if valor > 0:
                st.caption(palanca.ayuda)

    st.session_state["plan7"] = plan
    resultado = cambio.simular(grupo, plan)
    st.session_state["resultado7"] = resultado

    with derecha:
        st.metric("Adopción al cabo de un año",
                  _pct(resultado["adopcion_final"]))
        st.progress(resultado["adopcion_final"])
        st.metric("Coste", f'{_num(resultado["coste"], 1)} de '
                           f'{_num(resultado["presupuesto"], 1)}')
        if not resultado["dentro_de_presupuesto"]:
            st.error("Os habéis pasado del presupuesto.", icon="⚠️")
        elif resultado["adopcion_final"] < 0.5:
            st.warning(
                "Menos de la mitad de la gente adopta el cambio.", icon="⚠️"
            )
        else:
            st.success("Plan sostenible y dentro de presupuesto.", icon="✔️")

    historia = pd.DataFrame(resultado["historia"])
    referencia = pd.DataFrame(
        cambio.simular(grupo, cambio.plan_de_mandato())["historia"]
    )
    figura = go.Figure()
    figura.add_scatter(
        x=historia["mes"], y=historia["adopcion"], name="Vuestro plan",
        line=dict(color=GRANATE, width=3), mode="lines+markers",
    )
    figura.add_scatter(
        x=referencia["mes"], y=referencia["adopcion"],
        name="Solo ordenarlo desde dirección",
        line=dict(color=GRIS, width=2, dash="dash"), mode="lines",
    )
    figura.update_yaxes(tickformat=".0%", title="Adopción")
    figura.update_xaxes(title="Mes")
    figura.update_layout(legend=dict(orientation="h", y=1.12))
    _grafico(figura, alto=380)

    if resultado["se_desinfla"]:
        st.error(
            f"**Vuestra adopción se desinfla.** Llegó al "
            f"{_pct(resultado['adopcion_maxima'])} en el mes "
            f"{resultado['mes_del_maximo']} y va bajando. Es lo que pasa "
            f"cuando el cambio se sostiene sobre una orden: nadie ha "
            f"cambiado de opinión, solo ha dejado de discutir mientras "
            f"alguien miraba.",
            icon="📉",
        )

    st.info(
        "**Mirad la línea gris.** Ordenarlo desde dirección es lo más barato "
        "y lo más rápido, y por eso es lo que se hace casi siempre. También "
        "es lo único que se cae solo. Lo que aguanta es lento: participar, "
        "formar y cambiar lo que se premia.",
        icon="📈",
    )

    st.divider()
    _respuesta(
        "mandato",
        "¿Por qué no basta con que la dirección lo ordene? Contestad como si "
        "se lo tuvierais que explicar a un director que os pregunta «¿y para "
        "qué necesitamos todo esto?».",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 4 · El cierre
# --------------------------------------------------------------------------

def _paso_cierre(grupo: str) -> None:
    plan = _plan(grupo)
    resultado = cambio.simular(grupo, plan)
    st.session_state["resultado7"] = resultado

    st.markdown("### Entregar no es cambiar")

    a, b, c = st.columns(3)
    a.metric("Valor del plan", _num(resultado["valor_entregado"], 0))
    b.metric("Valor que se materializa",
             _num(resultado["valor_realizado"], 0))
    c.metric("Se queda por el camino", _num(resultado["valor_perdido"], 0),
             delta=f'{_pct(resultado["brecha"])} de brecha',
             delta_color="inverse")

    figura = go.Figure()
    figura.add_bar(
        x=["Entregado", "Adoptado"],
        y=[resultado["valor_entregado"], resultado["valor_realizado"]],
        marker_color=[GRIS, GRANATE],
        text=[_num(resultado["valor_entregado"], 0),
              _num(resultado["valor_realizado"], 0)],
        textposition="outside",
    )
    figura.update_layout(yaxis_title="Valor")
    _grafico(figura, alto=320)

    st.error(
        f"**Se puede entregar un proyecto al 100 % y no cambiar nada.** "
        f"Vuestro plan valía {_num(resultado['valor_entregado'], 0)} y se "
        f"materializa {_num(resultado['valor_realizado'], 0)}. La diferencia "
        f"no está en lo que no os dio tiempo a hacer: está en lo que "
        f"hicisteis y nadie usó.",
        icon="🔚",
    )

    st.markdown("#### Dónde se pierde")
    marco = pd.DataFrame([{
        "Iniciativa": f["nombre"],
        "Depende de la gente": _pct(f["dependencia"]),
        "Valor": _num(f["valor"], 0),
        "Se materializa": _num(f["realizado"], 1),
        "Se pierde": _num(f["perdido"], 1),
    } for f in resultado["detalle"][:8]])
    st.dataframe(marco, hide_index=True, use_container_width=True)

    st.divider()
    _respuesta(
        "primero",
        "Si solo pudierais hacer una cosa el primer mes, ¿cuál sería y por "
        "qué esa?",
        grupo, alto=90,
    )
    _respuesta(
        "curso",
        "Última pregunta del curso: de las siete sesiones, ¿qué os lleváis "
        "que no sabíais al empezar?",
        grupo, alto=110,
    )

    st.divider()
    _descargar(grupo, resultado, plan)


def _descargar(grupo: str, resultado: dict, plan: dict) -> None:
    st.markdown("### Llevaos el documento de cierre")
    st.caption(
        "Lleva vuestro plan de gestión del cambio y, debajo, la memoria de "
        "las siete sesiones. Es el documento del curso."
    )

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
        key="integrantes_s7",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = plan_cambio.generar(
            grupo, resultado, plan,
            st.session_state.get("respuestas7", {}), integrantes,
        )
    except Exception as error:
        st.error(
            "No he podido generar el documento. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar el plan de cambio y la memoria del curso",
        data=html.encode("utf-8"),
        file_name=plan_cambio.nombre_de_fichero(grupo),
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

    st.markdown("## Sesión 7 · Gestión del cambio")
    st.caption(
        "Vuestro plan está decidido, presupuestado, priorizado y medido. "
        "Falta lo más difícil: que alguien lo haga."
    )

    st.session_state.setdefault("paso7", 0)
    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    elegido = st.radio(
        "Paso", etiquetas, index=st.session_state["paso7"],
        horizontal=True, label_visibility="collapsed",
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso7"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    ayuda.panel(7)
    st.divider()

    if paso == 0:
        _paso_actores(grupo)
    elif paso == 1:
        _paso_dependencia(grupo)
    elif paso == 2:
        _paso_plan(grupo)
    else:
        _paso_cierre(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True,
                                    key="s7_anterior"):
        st.session_state["paso7"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True,
        key="s7_siguiente",
    ):
        st.session_state["paso7"] = paso + 1
        st.rerun()
