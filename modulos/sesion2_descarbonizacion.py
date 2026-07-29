"""Sesión 2 · Descarbonización.

Estructura mixta: un arranque corto guiado y después simulador libre. Es la
segunda vez que tocan la herramienta, así que no hace falta llevarles de la
mano como en la Sesión 1.

Tres pasos:

1. **De dónde partís** — su huella y su conclusión de la Sesión 1, que vuelven
   a introducir a mano. No hay guardado en servidor a propósito: llegan con
   su informe impreso, igual que un consultor llega con el entregable de la
   fase anterior.
2. **Vuestras palancas** — qué cuesta cada una y cuánto da *en su filial*.
   Aquí está el hallazgo: la misma medida no vale para todos.
3. **Vuestro plan** — simulador con presupuesto, y plan descargable.

Este módulo es solo interfaz. El modelo vive en `core/palancas.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import datos, filiales, kpis, palancas, plan as documento_plan, tutor

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"

PASOS = [
    ("De dónde partís", "Vuestra huella y vuestra conclusión de la sesión anterior"),
    ("Vuestras palancas", "Qué cuesta cada medida y cuánto da en vuestra filial"),
    ("Vuestro plan", "Decidid, comprobad y llevaos el plan"),
]


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _eur(valor: float) -> str:
    if abs(valor) >= 1_000_000:
        return _num(valor / 1_000_000, 2) + " M€"
    return _num(valor / 1_000, 0) + " k€"


def _pct(valor: float, decimales: int = 1) -> str:
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
    st.session_state.setdefault("respuestas2", {})
    valor = st.text_area(
        etiqueta,
        value=st.session_state["respuestas2"].get(clave, ""),
        key=f"s2_{clave}", height=alto, help=ayuda or None,
        placeholder="Escribid aquí…",
    )
    st.session_state["respuestas2"][clave] = valor
    _tutor(clave, grupo)


def _tutor(clave: str, grupo: str) -> None:
    """Mismo tutor de guardia que en la Sesión 1: pregunta, nunca responde."""
    from modulos.sesion1_diagnostico import LIMITE_TUTOR

    st.session_state.setdefault("tutor_usos", 0)
    st.session_state.setdefault("tutor_respuestas", {})
    usos = st.session_state["tutor_usos"]
    agotado = usos >= LIMITE_TUTOR

    izquierda, derecha = st.columns([1, 3])
    pulsado = izquierda.button(
        "Preguntar al tutor", key=f"s2_tutor_{clave}", disabled=agotado,
        help="Lee lo que habéis escrito y os devuelve una pregunta. "
             "No os va a dar la respuesta.",
    )
    if agotado:
        derecha.caption("Habéis gastado las consultas. Preguntad al profesor.")

    if pulsado:
        escrito = st.session_state["respuestas2"].get(clave, "")
        try:
            secretos = st.secrets
        except Exception:
            secretos = None
        with st.spinner("El tutor está leyendo lo que habéis escrito…"):
            texto, del_tutor = tutor.preguntar(
                grupo, f"s2_{clave}", escrito, secretos, semilla=usos
            )
        st.session_state["tutor_respuestas"][f"s2_{clave}"] = (texto, del_tutor)
        st.session_state["tutor_usos"] = usos + 1

    guardada = st.session_state["tutor_respuestas"].get(f"s2_{clave}")
    if guardada:
        texto, del_tutor = guardada
        st.info(f"**El tutor os pregunta:** {texto}")
        if not del_tutor:
            st.caption("Pregunta del banco de la asignatura.")


# --------------------------------------------------------------------------
# Paso 1 · De dónde partís
# --------------------------------------------------------------------------

def _paso_punto_de_partida(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    base = palancas.linea_base(grupo)
    presupuesto = palancas.presupuesto(grupo)

    st.markdown(f"### El punto de partida de {filial.nombre}")

    a, b, c, d = st.columns(4)
    a.metric("Huella actual", f'{_num(base["total_t"], 0)} t CO₂e')
    b.metric("Objetivo de reducción", _pct(palancas.OBJETIVO, 0),
             help="El mismo para las cinco filiales")
    c.metric("Tenéis que evitar", f'{_num(base["objetivo_t"], 0)} t')
    d.metric("Presupuesto a tres años", _eur(presupuesto),
             help="No os llega para todo. Ahí está el ejercicio.")

    huella = kpis.huella(grupo)
    figura = px.bar(
        huella, x="co2e_t", y="fuente", orientation="h",
        labels={"co2e_t": "Toneladas de CO₂ equivalente", "fuente": ""},
        color_discrete_sequence=[GRANATE],
    )
    _grafico(figura, alto=260)

    st.warning(
        "**Antes de tocar nada, mirad ese gráfico.** No podéis reducir lo que "
        "no emitís. Si vuestra huella es casi toda electricidad, cambiar "
        "camiones no os va a salvar."
    )

    st.divider()
    st.markdown("### Vuestra conclusión de la sesión anterior")
    st.caption(
        "Sacad el informe de diagnóstico que descargasteis en la Sesión 1 y "
        "copiad aquí lo que escribisteis. Vais a partir de ahí."
    )
    _respuesta(
        "diagnostico_previo",
        "¿Cuál dijisteis que era el problema principal de vuestra filial?",
        grupo,
        alto=90,
    )
    _respuesta(
        "sigue_valiendo",
        "Ahora que veis vuestra huella entera, ¿ese diagnóstico sigue "
        "valiendo o se os quedó corto?",
        grupo,
        ayuda="Se vale decir que os equivocasteis. Es lo que hace un "
              "consultor cuando llegan datos nuevos.",
        alto=90,
    )


# --------------------------------------------------------------------------
# Paso 2 · Vuestras palancas
# --------------------------------------------------------------------------

def _paso_palancas(grupo: str) -> None:
    st.markdown("### Las cuatro palancas, en vuestra filial")
    st.caption(
        "Estas cifras son las de vuestra filial y solo las de vuestra filial. "
        "El grupo de al lado tiene otras."
    )

    tabla = palancas.coste_por_tonelada(grupo)
    base = palancas.linea_base(grupo)

    marco = pd.DataFrame([{
        "Palanca": fila["nombre"],
        "Reduce como máximo": _pct(fila["pct_de_la_huella"]),
        "Toneladas evitadas": _num(fila["evitado_t"], 0),
        "Inversión": _eur(fila["coste_eur"]),
        "Coste por tonelada": (
            "—" if fila["coste_por_t"] == float("inf")
            else _num(fila["coste_por_t"], 0) + " €"
        ),
    } for fila in tabla])
    st.dataframe(marco, hide_index=True, use_container_width=True)

    utiles = [f for f in tabla if f["pct_de_la_huella"] > 0.001]
    if utiles:
        figura = px.bar(
            pd.DataFrame(utiles), x="nombre", y="pct_de_la_huella",
            labels={"nombre": "", "pct_de_la_huella": "Reducción máxima"},
            color_discrete_sequence=[GRANATE],
        )
        figura.add_hline(
            y=palancas.OBJETIVO, line_dash="dash", line_color=AMBAR,
            annotation_text="Objetivo: 25 %", annotation_position="top right",
        )
        figura.update_yaxes(tickformat=".0%")
        _grafico(figura, alto=320)

    inutiles = [f for f in tabla if f["pct_de_la_huella"] <= 0.001]
    for fila in inutiles:
        st.error(
            f"**{fila['nombre']}** no os sirve de nada: en vuestra filial "
            f"reduciría prácticamente cero, y aun así costaría dinero. "
            f"¿Sabéis por qué?",
            icon="⚠️",
        )

    with st.expander("Qué hace exactamente cada palanca"):
        for palanca in palancas.PALANCAS:
            st.markdown(f"**{palanca.nombre}**")
            st.write(palanca.descripcion)
            st.caption(palanca.ayuda)
            st.write("")

    st.info(
        f"Vuestra huella es de **{_num(base['total_t'], 0)} t** y tenéis que "
        f"quitar **{_num(base['objetivo_t'], 0)} t**. Mirad la columna del "
        f"coste por tonelada: es la que os dice por dónde empezar si lo que "
        f"queréis es que el dinero rinda."
    )

    st.divider()
    _respuesta(
        "orden",
        "¿En qué orden vais a usar las palancas y por qué en ese orden?",
        grupo,
        alto=100,
    )


# --------------------------------------------------------------------------
# Paso 3 · Vuestro plan
# --------------------------------------------------------------------------

def _paso_plan(grupo: str) -> None:
    st.markdown("### Construid vuestro plan")

    limites = palancas.topes(grupo)
    st.session_state.setdefault("plan", {})

    izquierda, derecha = st.columns([3, 2])

    with izquierda:
        for palanca in palancas.PALANCAS:
            tope = limites[palanca.codigo]
            if tope <= 0:
                st.caption(f"**{palanca.nombre}** — sin margen en vuestra filial.")
                st.session_state["plan"][palanca.codigo] = 0.0
                continue

            if palanca.codigo == "rutas":
                valor = st.slider(
                    f"{palanca.nombre} ({palanca.unidad})",
                    0.0, float(round(tope, 1)),
                    float(st.session_state["plan"].get(palanca.codigo, 0.0)),
                    step=0.5, key=f"plan_{palanca.codigo}",
                    help=palanca.ayuda,
                )
            else:
                valor = st.slider(
                    f"{palanca.nombre} ({palanca.unidad})",
                    0, int(round(tope * 100)),
                    int(st.session_state["plan"].get(palanca.codigo, 0.0) * 100),
                    step=5, key=f"plan_{palanca.codigo}",
                    help=palanca.ayuda,
                ) / 100
            st.session_state["plan"][palanca.codigo] = valor

    resultado = palancas.simular(grupo, st.session_state["plan"])

    with derecha:
        st.metric(
            "Reducción conseguida", _pct(resultado["reduccion"]),
            delta=f'{_num((resultado["reduccion"] - palancas.OBJETIVO) * 100)} '
                  f'puntos respecto al objetivo',
        )
        st.progress(min(1.0, resultado["reduccion"] / palancas.OBJETIVO))

        st.metric("Inversión comprometida", _eur(resultado["coste_eur"]))
        restante = resultado["presupuesto_restante_eur"]
        st.metric(
            "Presupuesto restante", _eur(restante),
            delta="Os habéis pasado" if restante < 0 else None,
            delta_color="inverse" if restante < 0 else "normal",
        )

        if resultado["objetivo_cumplido"] and resultado["dentro_de_presupuesto"]:
            st.success("Objetivo cumplido y dentro de presupuesto.", icon="✔️")
        elif not resultado["dentro_de_presupuesto"]:
            st.error("Os habéis pasado del presupuesto.", icon="⚠️")
        else:
            faltan = resultado["objetivo_t"] - resultado["evitado_t"]
            st.warning(f"Os faltan {_num(faltan, 0)} t por reducir.", icon="⚠️")

    detalle = pd.DataFrame([{
        "Palanca": fila["nombre"],
        "Intensidad": (
            _num(fila["intensidad"], 1) + " puntos" if fila["codigo"] == "rutas"
            else _pct(fila["intensidad"], 0)
        ),
        "Evita": _num(fila["evitado_t"], 0) + " t",
        "Cuesta": _eur(fila["coste_eur"]),
    } for fila in resultado["detalle"]])
    st.dataframe(detalle, hide_index=True, use_container_width=True)

    figura = go.Figure()
    figura.add_bar(
        x=["Huella actual", "Después del plan"],
        y=[resultado["base_t"], resultado["final_t"]],
        marker_color=[GRIS, GRANATE],
    )
    figura.add_hline(
        y=resultado["base_t"] - resultado["objetivo_t"],
        line_dash="dash", line_color=AMBAR,
        annotation_text="Donde tenéis que llegar",
    )
    figura.update_layout(yaxis_title="Toneladas de CO₂ equivalente")
    _grafico(figura, alto=300)

    st.divider()
    st.markdown("### Justificad vuestro plan")
    _respuesta(
        "justificacion",
        "¿Por qué este plan y no otro? Explicad qué habéis dejado fuera y "
        "por qué.",
        grupo, alto=120,
    )
    _respuesta(
        "riesgo",
        "¿Qué es lo que más fácilmente puede salir mal en vuestro plan?",
        grupo, alto=90,
    )
    _respuesta(
        "siguiente_euro",
        "Si os dieran un millón más, ¿en qué lo gastaríais?",
        grupo, alto=90,
    )

    st.divider()
    _descargar(grupo, resultado)


def _descargar(grupo: str, resultado: dict) -> None:
    st.markdown("### Llevaos vuestro plan")

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
        key="integrantes_s2",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = documento_plan.generar(
            grupo, resultado, st.session_state.get("respuestas2", {}), integrantes
        )
    except Exception as error:
        st.error(
            "No he podido generar el plan. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar el plan de descarbonización",
        data=html.encode("utf-8"),
        file_name=documento_plan.nombre_de_fichero(grupo),
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

    st.markdown("## Sesión 2 · Descarbonización")
    st.caption(
        f"Vuestra filial tiene que reducir su huella un "
        f"{int(palancas.OBJETIVO * 100)} % con un presupuesto cerrado. "
        "No os llega para todo: hay que elegir."
    )

    st.session_state.setdefault("paso2", 0)
    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    # Sin `key`: con clave propia, el control recordaría su posición y se
    # ignoraría el `index`, así que al cambiar de grupo la sesión no volvería
    # al primer paso aunque se reiniciase el estado.
    elegido = st.radio(
        "Paso", etiquetas, index=st.session_state["paso2"],
        horizontal=True, label_visibility="collapsed",
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso2"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    st.divider()

    if paso == 0:
        _paso_punto_de_partida(grupo)
    elif paso == 1:
        _paso_palancas(grupo)
    else:
        _paso_plan(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True,
                                    key="s2_anterior"):
        st.session_state["paso2"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True,
        key="s2_siguiente",
    ):
        st.session_state["paso2"] = paso + 1
        st.rerun()
