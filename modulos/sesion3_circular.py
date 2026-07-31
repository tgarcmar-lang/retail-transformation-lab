"""Sesión 3 · Logística verde y economía circular.

Cuatro pasos, misma mecánica que la Sesión 2: ya conocen la herramienta y
repetir la explicación les resultaría infantil.

1. **Qué material movéis** — el balance de materiales de la filial y la
   jerarquía de residuos. Aquí aparece la cifra que manda: cuánto material
   se pierde de verdad.
2. **Vuestras palancas** — las seis, ordenadas por lo que cuesta recuperar
   una tonelada con cada una. La sorpresa está servida: lo más barato es lo
   más bajo de la jerarquía.
3. **Vuestro plan** — simulador con presupuesto y plan descargable.
4. **La cuenta en euros** — lo mismo mirado con la otra unidad. Hay palancas
   que son pésimas en toneladas y excelentes en dinero, y al revés. Un
   director de operaciones tiene que ver las dos.

**Por qué el paso 4 va al final.** Igual que el alcance 3 en la Sesión 2:
primero deciden con una sola unidad de medida y se comprometen, y después
descubren que la otra unidad ordena las cosas de otra manera. Puesto antes,
sería una columna más de una tabla.

Este módulo es solo interfaz. El modelo vive en `core/circular.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import circular, datos, filiales, kpis, plan_circular, tutor

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"

COLOR_NIVEL = {"Prevenir": VERDE, "Reutilizar": AMBAR, "Reciclar": GRIS}

PASOS = [
    ("Qué material movéis", "Vuestro balance de materiales y dónde se pierde"),
    ("Vuestras palancas", "Qué cuesta recuperar una tonelada con cada medida"),
    ("Vuestro plan", "Decidid, comprobad y llevaos el plan"),
    ("La cuenta en euros", "Lo mismo, con la otra unidad de medida"),
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
    st.session_state.setdefault("respuestas3", {})
    valor = st.text_area(
        etiqueta,
        value=st.session_state["respuestas3"].get(clave, ""),
        key=f"s3_{clave}", height=alto, help=ayuda or None,
        placeholder="Escribid aquí…",
    )
    st.session_state["respuestas3"][clave] = valor
    _tutor(clave, grupo)


def _tutor(clave: str, grupo: str) -> None:
    """El mismo tutor de guardia de las otras dos sesiones."""
    from modulos.sesion1_diagnostico import LIMITE_TUTOR

    st.session_state.setdefault("tutor_usos", 0)
    st.session_state.setdefault("tutor_respuestas", {})
    usos = st.session_state["tutor_usos"]
    agotado = usos >= LIMITE_TUTOR

    izquierda, derecha = st.columns([1, 3])
    pulsado = izquierda.button(
        "Preguntar al tutor", key=f"s3_tutor_{clave}", disabled=agotado,
        help="Lee lo que habéis escrito y os devuelve una pregunta. "
             "No os va a dar la respuesta.",
    )
    if agotado:
        derecha.caption("Habéis gastado las consultas. Preguntad al profesor.")

    if pulsado:
        escrito = st.session_state["respuestas3"].get(clave, "")
        try:
            secretos = st.secrets
        except Exception:
            secretos = None
        with st.spinner("El tutor está leyendo lo que habéis escrito…"):
            texto, del_tutor = tutor.preguntar(
                grupo, f"s3_{clave}", escrito, secretos, semilla=usos
            )
        st.session_state["tutor_respuestas"][f"s3_{clave}"] = (texto, del_tutor)
        st.session_state["tutor_usos"] = usos + 1

    guardada = st.session_state["tutor_respuestas"].get(f"s3_{clave}")
    if guardada:
        texto, del_tutor = guardada
        st.info(f"**El tutor os pregunta:** {texto}")
        if not del_tutor:
            st.caption("Pregunta del banco de la asignatura.")


# --------------------------------------------------------------------------
# Paso 1 · Qué material movéis
# --------------------------------------------------------------------------

def _la_jerarquia() -> None:
    with st.expander("Antes de empezar: la jerarquía de residuos", expanded=True):
        st.markdown(
            "En descarbonización todas las toneladas de CO₂ valen lo mismo: "
            "una tonelada evitada es una tonelada evitada, la evites como la "
            "evites. **Con el material no funciona así.** Importa muchísimo "
            "cómo se evita, y hay un orden establecido."
        )
        uno, dos, tres, cuatro = st.columns(4)
        uno.success("**1. Prevenir**\n\nNo generar el residuo. Lo que no "
                    "existe no hay que gestionarlo, ni pagarlo, ni tirarlo.")
        dos.warning("**2. Reutilizar**\n\nQue el material vuelva a usarse tal "
                    "cual, sin transformarlo. Se recupera casi todo.")
        tres.info("**3. Reciclar**\n\nTransformarlo para hacer otra cosa. Se "
                  "pierde material y se pierde calidad en cada vuelta.")
        cuatro.error("**4. Verter**\n\nEl final del camino. El material sale "
                     "de la economía y no vuelve.")
        st.caption(
            "Este orden no es una preferencia moral: es de dónde sale más "
            "material recuperado por euro invertido. Y explica por qué una "
            "empresa que solo recicla puede estar haciéndolo mal."
        )


def _paso_material(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    inv = circular.inventario(grupo)

    _la_jerarquia()

    st.markdown(f"### El balance de materiales de {filial.nombre}")

    a, b, c, d = st.columns(4)
    a.metric("Material que generáis", f'{_num(inv["generado_t"], 0)} t')
    b.metric("Vuelve al ciclo", f'{_num(inv["recirculado_t"], 0)} t',
             help="Lo que se recicla, descontando lo que se pierde por el "
                  "camino y la calidad que baja.")
    c.metric("Se pierde", f'{_num(inv["perdida_t"], 0)} t',
             delta=f'{_pct(1 - inv["pct_circularidad"], 0)} de lo que movéis',
             delta_color="inverse")
    d.metric("Tenéis que recuperar", f'{_num(inv["objetivo_t"], 0)} t',
             help="Un tercio de lo que hoy se pierde.")

    st.warning(
        f"**Ojo a la segunda cifra.** Recicláis el "
        f"{_pct(inv['pct_reciclado'], 0)} de lo que generáis, pero solo vuelve "
        f"al ciclo el {_pct(inv['pct_circularidad'], 0)}. La diferencia se "
        f"pierde en la recogida, en la limpieza y en la propia "
        f"transformación: **una tonelada reciclada no es una tonelada "
        f"salvada.** Por eso prevenir está por encima de reciclar.",
        icon="♻️",
    )

    tabla = circular.desglose(grupo)
    figura = px.bar(
        tabla, x="generado_t", y="material", orientation="h",
        labels={"generado_t": "Toneladas al año", "material": ""},
        color_discrete_sequence=[GRANATE],
    )
    _grafico(figura, alto=280)

    st.divider()
    st.markdown("### De dónde sale ese material")
    a, b, c = st.columns(3)
    envases = circular.envases_resumen(grupo)
    devoluciones = circular.devoluciones_resumen(grupo)
    a.metric("Envase puesto en circulación", f'{_num(envases["total_t"], 0)} t',
             help="Cartón, film, relleno y palés, tanto de lo que entra como "
                  "de lo que sale hacia el cliente.")
    b.metric("Merma", f'{_num(inv["merma_t"], 0)} t',
             help="Producto que nunca llegó a venderse.")
    c.metric("Devoluciones", f'{_num(devoluciones["peso_t"], 0)} t',
             help=f'De las que {_num(devoluciones["no_revendible_t"], 0)} t '
                  f'no se pueden volver a vender.')

    st.divider()
    st.markdown("### Vuestra conclusión de la Sesión 2")
    st.caption(
        "Sacad el plan de descarbonización que descargasteis y copiad aquí lo "
        "que decidisteis. Vais a partir de ahí."
    )
    _respuesta(
        "plan_previo",
        "¿Qué palancas elegisteis en la Sesión 2 y por qué?",
        grupo, alto=90,
    )
    _respuesta(
        "material_o_carbono",
        "De esas palancas, ¿alguna cambia además la cantidad de envase o de "
        "residuo que genera vuestra filial? ¿Cuál, y por qué?",
        grupo,
        ayuda="Pensad qué le pasa a la caja de cartón cuando un pedido se "
              "recoge en la tienda en vez de repartirse a domicilio.",
        alto=90,
    )


# --------------------------------------------------------------------------
# Paso 2 · Vuestras palancas
# --------------------------------------------------------------------------

def _paso_palancas(grupo: str) -> None:
    st.markdown("### Las seis palancas, ordenadas por lo que cuestan")
    st.caption(
        "Cada una está en un escalón distinto de la jerarquía. Fijaos en qué "
        "escalón ocupa la más barata."
    )

    tabla = circular.coste_por_tonelada(grupo)
    inv = circular.inventario(grupo)

    marco = pd.DataFrame([{
        "Palanca": fila["nombre"],
        "Escalón": fila["nivel"],
        "Recupera": _num(fila["evitado_t"], 0) + " t",
        "% de lo perdido": _pct(fila["pct_de_la_perdida"]),
        "Inversión": _eur(fila["coste_eur"]),
        "Coste por tonelada": (
            "—" if fila["coste_por_t"] == float("inf")
            else _num(fila["coste_por_t"], 0) + " €"
        ),
    } for fila in tabla])
    st.dataframe(marco, hide_index=True, use_container_width=True)

    figura = px.bar(
        pd.DataFrame(tabla), x="nombre", y="pct_de_la_perdida", color="nivel",
        color_discrete_map=COLOR_NIVEL,
        labels={"nombre": "", "pct_de_la_perdida": "Recupera",
                "nivel": "Escalón"},
    )
    figura.add_hline(
        y=circular.OBJETIVO_CIRCULAR, line_dash="dash", line_color=AMBAR,
        annotation_text="Objetivo: un tercio", annotation_position="top right",
    )
    figura.update_yaxes(tickformat=".0%")
    _grafico(figura, alto=340)

    barata = tabla[0]
    st.info(
        f"**La más barata de las seis es «{barata['nombre']}», que está en el "
        f"escalón «{barata['nivel']}».** No es casualidad ni es un error del "
        f"caso: separar mejor siempre es lo más barato por tonelada, y por "
        f"eso es por donde empieza todo el mundo. Comprobad hasta dónde os "
        f"llega vosotros solos con ella.",
        icon="💡",
    )

    with st.expander("Qué hace exactamente cada palanca"):
        for palanca in circular.PALANCAS:
            st.markdown(f"**{palanca.nombre}** · _{palanca.nivel}_")
            st.write(palanca.descripcion)
            st.caption(palanca.ayuda)
            st.write("")

    st.divider()
    _respuesta(
        "escalon",
        "Mirad la tabla: ¿en qué escalón de la jerarquía están las palancas "
        "más baratas, y en cuál las que más material recuperan? ¿Coinciden?",
        grupo, alto=100,
    )


# --------------------------------------------------------------------------
# Paso 3 · Vuestro plan
# --------------------------------------------------------------------------

def _paso_plan(grupo: str) -> None:
    st.markdown("### Construid vuestro plan")
    st.caption(
        f"Objetivo: recuperar un tercio del material que hoy perdéis. "
        f"Presupuesto: {_eur(circular.presupuesto(grupo))} a tres años."
    )

    limites = circular.topes(grupo)
    st.session_state.setdefault("plan3c", {})

    izquierda, derecha = st.columns([3, 2])

    with izquierda:
        for nivel in circular.NIVELES:
            st.markdown(f"**{nivel}**")
            for palanca in circular.PALANCAS:
                if palanca.nivel != nivel:
                    continue
                tope = limites[palanca.codigo]
                if tope <= 0:
                    st.caption(f"{palanca.nombre} — sin margen en vuestra filial.")
                    st.session_state["plan3c"][palanca.codigo] = 0.0
                    continue

                guardado = st.session_state["plan3c"].get(palanca.codigo, 0.0)
                if palanca.codigo in circular.EN_PUNTOS:
                    valor = st.slider(
                        f"{palanca.nombre} ({palanca.unidad})",
                        0.0, float(round(tope, 1)),
                        float(min(guardado, tope)), step=0.5,
                        key=f"plan3c_{palanca.codigo}", help=palanca.ayuda,
                    )
                else:
                    valor = st.slider(
                        f"{palanca.nombre} ({palanca.unidad})",
                        0, int(round(tope * 100)),
                        min(int(guardado * 100), int(round(tope * 100))),
                        step=5, key=f"plan3c_{palanca.codigo}",
                        help=palanca.ayuda,
                    ) / 100
                st.session_state["plan3c"][palanca.codigo] = valor

    resultado = circular.simular(grupo, st.session_state["plan3c"])
    st.session_state["resultado3c"] = resultado

    with derecha:
        st.metric(
            "Material recuperado", _pct(resultado["reduccion"]),
            delta=f'{_num((resultado["reduccion"] - circular.OBJETIVO_CIRCULAR) * 100)} '
                  f'puntos respecto al objetivo',
        )
        st.progress(min(1.0, resultado["reduccion"] / circular.OBJETIVO_CIRCULAR))
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
            st.warning(f"Os faltan {_num(faltan, 0)} t por recuperar.", icon="⚠️")

        st.markdown("**De dónde sale lo recuperado**")
        for nivel in circular.NIVELES:
            toneladas = resultado["por_nivel"][nivel]
            if resultado["evitado_t"] > 0:
                st.caption(
                    f"{nivel}: {_num(toneladas, 0)} t "
                    f"({_pct(toneladas / resultado['evitado_t'], 0)})"
                )

    if (resultado["evitado_t"] > 0
            and resultado["por_nivel"]["Prevenir"] / resultado["evitado_t"] < 0.15):
        st.error(
            "**Casi todo vuestro plan está en los escalones de abajo.** "
            "Estáis gestionando mejor un residuo que seguís generando igual. "
            "Funciona, pero es lo primero que os van a discutir: ¿por qué no "
            "habéis evitado que se genere?",
            icon="⚠️",
        )

    detalle = pd.DataFrame([{
        "Palanca": fila["nombre"],
        "Escalón": fila["nivel"],
        "Intensidad": (
            _num(fila["intensidad"], 1) + " puntos"
            if fila["codigo"] in circular.EN_PUNTOS
            else _pct(fila["intensidad"], 0)
        ),
        "Recupera": _num(fila["evitado_t"], 0) + " t",
        "Cuesta": _eur(fila["coste_eur"]),
    } for fila in resultado["detalle"]])
    st.dataframe(detalle, hide_index=True, use_container_width=True)

    figura = go.Figure()
    figura.add_bar(
        x=["Se pierde hoy", "Después del plan"],
        y=[resultado["base_t"], resultado["final_t"]],
        marker_color=[GRIS, GRANATE],
    )
    figura.add_hline(
        y=resultado["base_t"] - resultado["objetivo_t"],
        line_dash="dash", line_color=AMBAR,
        annotation_text="Donde tenéis que llegar",
    )
    figura.update_layout(yaxis_title="Toneladas de material perdido")
    _grafico(figura, alto=300)

    st.divider()
    st.markdown("### Justificad vuestro plan")
    _respuesta(
        "justificacion",
        "¿Por qué este plan y no otro? ¿Qué habéis dejado fuera y por qué?",
        grupo, alto=120,
    )
    _respuesta(
        "prevencion",
        "¿Qué parte de vuestro plan evita que el residuo se genere, y qué "
        "parte solo lo gestiona mejor una vez generado?",
        grupo, alto=90,
    )

    st.divider()
    _descargar(grupo, resultado)


# --------------------------------------------------------------------------
# Paso 4 · La cuenta en euros
# --------------------------------------------------------------------------

def _paso_euros(grupo: str) -> None:
    st.markdown("### Lo mismo, contado en dinero")
    st.caption(
        "Hasta aquí habéis decidido mirando toneladas. Un director de "
        "operaciones no decide solo así."
    )

    devoluciones = circular.devoluciones_resumen(grupo)
    inventario_kpi = kpis.inventario_resumen(grupo)
    envases = circular.envases_resumen(grupo)

    a, b, c = st.columns(3)
    a.metric("Os cuesta gestionar devoluciones",
             _eur(devoluciones["coste_gestion_eur"]),
             help=f'{_num(devoluciones["pedidos_devueltos"], 0)} pedidos '
                  f'devueltos al año.')
    b.metric("Merma", _eur(inventario_kpi["merma_eur"]),
             help="Producto que compraste y nunca vendiste.")
    c.metric("Envase comprado", _eur(envases["coste_eur"]))

    st.error(
        f"**Mirad la primera cifra.** Evitar devoluciones es vuestra palanca "
        f"más cara por tonelada, con diferencia. Y sin embargo las "
        f"devoluciones os están costando hoy "
        f"{_eur(devoluciones['coste_gestion_eur'])} al año en pura gestión, "
        f"más "
        f"{_eur(devoluciones['valor_eur'] - devoluciones['coste_gestion_eur'])} "
        f"de mercancía que va y viene. En toneladas es la peor de las seis. "
        f"En euros no lo es en absoluto.",
        icon="💶",
    )

    tabla = circular.coste_por_tonelada(grupo)
    marco = pd.DataFrame([{
        "Palanca": fila["nombre"],
        "Escalón": fila["nivel"],
        "Puesto en toneladas": indice + 1,
        "Coste por tonelada": (
            "—" if fila["coste_por_t"] == float("inf")
            else _num(fila["coste_por_t"], 0) + " €"
        ),
        "Inversión": _eur(fila["coste_eur"]),
    } for indice, fila in enumerate(tabla)])
    st.dataframe(marco, hide_index=True, use_container_width=True)

    st.info(
        "**Ninguna de las dos unidades es la correcta.** El material mide el "
        "impacto ambiental; el dinero mide si la empresa puede permitírselo y "
        "si el Consejo lo va a aprobar. Un plan que solo se defiende en "
        "toneladas no se aprueba, y uno que solo se defiende en euros no "
        "cambia nada.",
        icon="⚖️",
    )

    st.divider()
    _respuesta(
        "euros",
        "Con la cuenta en euros delante, ¿cambiaríais vuestro plan? ¿En qué?",
        grupo, alto=110,
    )
    _respuesta(
        "consejo",
        "Tenéis tres minutos ante el Consejo para defender vuestro plan. "
        "¿Con qué cifra abrís?",
        grupo, alto=90,
    )

    st.divider()
    _descargar(grupo, st.session_state.get("resultado3c"))


def _descargar(grupo: str, resultado: dict | None) -> None:
    if resultado is None:
        st.warning(
            "Volved al paso 3 y construid vuestro plan antes de descargarlo.",
            icon="⚠️",
        )
        return

    st.markdown("### Llevaos vuestro plan")

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
        key="integrantes_s3",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = plan_circular.generar(
            grupo, resultado, st.session_state.get("respuestas3", {}), integrantes
        )
    except Exception as error:
        st.error(
            "No he podido generar el plan. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar el plan de economía circular",
        data=html.encode("utf-8"),
        file_name=plan_circular.nombre_de_fichero(grupo),
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

    st.markdown("## Sesión 3 · Logística verde y economía circular")
    st.caption(
        "Vuestra filial tiene que recuperar un tercio del material que hoy "
        "pierde, con un presupuesto cerrado. Reciclar mejor no os va a bastar."
    )

    st.session_state.setdefault("paso3", 0)
    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    elegido = st.radio(
        "Paso", etiquetas, index=st.session_state["paso3"],
        horizontal=True, label_visibility="collapsed",
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso3"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    st.divider()

    if paso == 0:
        _paso_material(grupo)
    elif paso == 1:
        _paso_palancas(grupo)
    elif paso == 2:
        _paso_plan(grupo)
    else:
        _paso_euros(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True,
                                    key="s3_anterior"):
        st.session_state["paso3"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True,
        key="s3_siguiente",
    ):
        st.session_state["paso3"] = paso + 1
        st.rerun()
