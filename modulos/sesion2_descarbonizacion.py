"""Sesión 2 · Descarbonización.

Estructura mixta: un arranque corto guiado y después simulador libre. Es la
segunda vez que tocan la herramienta, así que no hace falta llevarles de la
mano como en la Sesión 1.

Cuatro pasos:

1. **De dónde partís** — qué es una huella y hasta dónde llega la suya, más
   su conclusión de la Sesión 1, que vuelven a introducir a mano. No hay
   guardado en servidor a propósito: llegan con su informe impreso, igual
   que un consultor llega con el entregable de la fase anterior.
2. **Vuestras palancas** — qué cuesta cada una y cuánto da *en su filial*.
   Aquí está el hallazgo: la misma medida no vale para todos.
3. **Vuestro plan** — simulador con presupuesto, y plan descargable.
4. **Lo que no estabais mirando** — el alcance 3.

**Por qué el alcance 3 va al final y no al principio.** Va después de que el
grupo haya cerrado su plan y se haya felicitado por el 25 %. Si se enseñase
antes, sería un dato más; puesto aquí, es la corrección de una conclusión que
acaban de defender por escrito. Duele más y se olvida menos.

Este módulo es solo interfaz. El modelo vive en `core/palancas.py` y en
`core/alcance3.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modulos import ayuda
from core import (alcance3, datos, filiales, kpis, palancas,
                  plan as documento_plan, tutor)

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"

PASOS = [
    ("De dónde partís", "Vuestra huella y vuestra conclusión de la sesión anterior"),
    ("Vuestras palancas", "Qué cuesta cada medida y cuánto da en vuestra filial"),
    ("Vuestro plan", "Decidid, comprobad y llevaos el plan"),
    ("Lo que no estabais mirando", "El resto de vuestra huella"),
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
    """Delegado en el panel compartido: ver `modulos/ayuda.py`."""
    ayuda.pregunta(clave, grupo, 2, "respuestas2")


# --------------------------------------------------------------------------
# Paso 1 · De dónde partís
# --------------------------------------------------------------------------

def _que_es_una_huella() -> None:
    """La capa conceptual: qué se está midiendo y hasta dónde.

    Va antes de cualquier número. Sin esto el alumno manipula toneladas sin
    saber qué son, y la frontera del inventario —que es la idea que de
    verdad importa— pasa desapercibida.
    """
    with st.expander("Antes de empezar: qué es exactamente una huella de carbono",
                     expanded=True):
        st.markdown(
            "Una **huella de carbono** es el total de gases de efecto "
            "invernadero asociados a una actividad durante un año. Se mide "
            "en **toneladas de CO₂ equivalente**: el metano o los gases "
            "refrigerantes calientan mucho más que el CO₂, así que se "
            "convierten todos a una unidad común para poder sumarlos. Por "
            "eso un kilo de gas refrigerante puede valer casi cuatro mil "
            "kilos de CO₂e."
        )
        st.markdown(
            "Lo difícil de una huella no es sumar: es **decidir qué se "
            "cuenta**. Esa decisión tiene nombre y está normalizada en tres "
            "alcances."
        )

        uno, dos, tres = st.columns(3)
        uno.markdown(
            "**Alcance 1**\n\nLo que arde en algo que es vuestro. El gasóleo "
            "de vuestros camiones, el gas de vuestras calderas, el "
            "refrigerante que se fuga de vuestras cámaras."
        )
        dos.markdown(
            "**Alcance 2**\n\nLa energía que compráis hecha. Sobre todo "
            "electricidad: no emitís vosotros, emite la central, pero emite "
            "porque vosotros consumís."
        )
        tres.markdown(
            "**Alcance 3**\n\nTodo lo demás de vuestra cadena de valor: "
            "fabricar lo que vendéis, traerlo, tratar vuestros residuos, "
            "los viajes de vuestra gente."
        )

        st.info(
            "**La frontera de vuestro inventario, hoy.** Lo que vais a ver "
            "en esta sesión son vuestros **alcances 1 y 2**: lo que emitís "
            "vosotros y vuestra electricidad. Es donde mandáis de verdad y "
            "es sobre lo que se fija vuestro objetivo. El alcance 3 lo "
            "abriremos en el último paso, cuando ya tengáis un plan.",
            icon="📏",
        )
        st.caption(
            "Que un inventario tenga frontera no es hacer trampa: es "
            "obligatorio decir dónde está. Hacer trampa es no decirlo."
        )


def _paso_punto_de_partida(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    base = palancas.linea_base(grupo)
    presupuesto = palancas.presupuesto(grupo)

    _que_es_una_huella()

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
    st.markdown("### Las seis palancas, en vuestra filial")
    st.caption(
        "Estas cifras son las de vuestra filial y solo las de vuestra filial. "
        "El grupo de al lado tiene otras."
    )
    st.caption(
        "Tres de las seis son de transporte y hacen cosas distintas: quitar "
        "kilómetros vacíos no es lo mismo que llenar mejor el vehículo, y "
        "ninguna de las dos es lo mismo que dejar de repartir a domicilio."
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

            if palanca.codigo in palancas.EN_PUNTOS:
                valor = st.slider(
                    f"{palanca.nombre} ({palanca.unidad})",
                    0.0, float(round(tope, 1)),
                    float(min(st.session_state["plan"].get(palanca.codigo, 0.0),
                              tope)),
                    step=0.5, key=f"plan_{palanca.codigo}",
                    help=palanca.ayuda,
                )
            else:
                valor = st.slider(
                    f"{palanca.nombre} ({palanca.unidad})",
                    0, int(round(tope * 100)),
                    min(int(st.session_state["plan"].get(palanca.codigo, 0.0) * 100),
                        int(round(tope * 100))),
                    step=5, key=f"plan_{palanca.codigo}",
                    help=palanca.ayuda,
                ) / 100
            st.session_state["plan"][palanca.codigo] = valor

    resultado = palancas.simular(grupo, st.session_state["plan"])
    st.session_state["resultado"] = resultado

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
            _num(fila["intensidad"], 1) + " puntos"
            if fila["codigo"] in palancas.EN_PUNTOS
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


# --------------------------------------------------------------------------
# Paso 4 · Lo que no estabais mirando
# --------------------------------------------------------------------------

def _paso_alcance3(grupo: str) -> None:
    inv = alcance3.inventario(grupo)

    st.markdown("### Vuestra huella entera")
    st.caption(
        "Hasta aquí habéis trabajado con vuestros alcances 1 y 2. Esto es "
        "lo que aparece cuando se añade el alcance 3."
    )

    a, b, c = st.columns(3)
    a.metric("Lo que llevabais mirando", f'{_num(inv["operativo_t"], 0)} t',
             help="Alcances 1 y 2: vuestro gasóleo, vuestro gas, vuestras "
                  "fugas y vuestra electricidad.")
    b.metric("Vuestro alcance 3", f'{_num(inv["alcance3_t"], 0)} t',
             help="Fabricar lo que vendéis, traerlo y tratar los residuos.")
    c.metric("Vuestra huella real", f'{_num(inv["total_t"], 0)} t',
             delta=f'{_num(inv["veces_mayor"], 1)} veces lo que creíais',
             delta_color="inverse")

    tabla = alcance3.desglose(grupo)
    figura = px.bar(
        tabla, x="co2e_t", y="concepto", orientation="h",
        color="alcance",
        color_discrete_map={1: AMBAR, 2: VERDE, 3: GRANATE},
        labels={"co2e_t": "Toneladas de CO₂ equivalente", "concepto": "",
                "alcance": "Alcance"},
    )
    figura.update_layout(legend_title_text="Alcance")
    _grafico(figura, alto=300)

    st.error(
        f"**Vuestro plan de antes reduce sobre {_pct(inv['pct_operativo'])} "
        f"de vuestra huella.** No está mal hecho: está hecho sobre una parte. "
        f"Es exactamente lo que le pasa a cualquier minorista, porque un "
        f"distribuidor casi no fabrica nada y casi todo lo que emite lo emite "
        f"otro por encargo suyo.",
        icon="⚠️",
    )

    with st.expander("Cómo se ha calculado esto, y por qué hay que desconfiar"):
        st.markdown(
            "El alcance 3 de las compras está estimado **por gasto**: se "
            "multiplica lo que compráis por un factor medio de la categoría "
            "y por la intensidad del país donde se fabrica. Es el método con "
            "el que empieza todo el mundo, y tiene un defecto que conviene "
            "que veáis: **si mañana negociáis un descuento del 5 % con "
            "vuestro proveedor, vuestra huella baja un 5 % sin que haya "
            "cambiado absolutamente nada en la fábrica.**"
        )
        st.markdown(
            "Por eso una estimación por gasto sirve para saber **dónde "
            "mirar**, no para presumir de decimales ni para reclamar una "
            "reducción. El paso siguiente en una empresa real es pedir datos "
            "primarios a los proveedores que concentran el gasto."
        )

    st.divider()
    st.markdown("### De dónde viene, país por país")
    por_pais = alcance3.compras_por_pais(grupo)
    marco = pd.DataFrame([{
        "Origen": fila.pais_origen,
        "Compras": _eur(fila.importe_eur),
        "% de la compra": _pct(fila.pct_importe, 0),
        "Fabricar": _num(fila.bienes_t, 0) + " t",
        "Traerlo": _num(fila.transporte_t, 0) + " t",
        "kg CO₂e por € comprado": _num(fila.kg_por_euro, 2),
    } for fila in por_pais.itertuples()])
    st.dataframe(marco, hide_index=True, use_container_width=True)
    st.caption(
        "La última columna es la interesante: no todos los euros de compra "
        "emiten lo mismo. Comparad el vuestro de España con el de China."
    )

    st.divider()
    st.markdown("### Vuestras palancas de alcance 3")

    presupuesto = alcance3.presupuesto3(grupo)
    izquierda, derecha = st.columns([3, 2])
    st.session_state.setdefault("plan3", {})

    with izquierda:
        for palanca in alcance3.PALANCAS3:
            tope = alcance3.topes3(grupo)[palanca.codigo]
            if tope <= 0:
                st.caption(f"**{palanca.nombre}** — sin margen en vuestra filial.")
                st.session_state["plan3"][palanca.codigo] = 0.0
                continue
            valor = st.slider(
                f"{palanca.nombre} ({palanca.unidad})",
                0, int(round(tope * 100)),
                min(int(st.session_state["plan3"].get(palanca.codigo, 0.0) * 100),
                    int(round(tope * 100))),
                step=5, key=f"plan3_{palanca.codigo}", help=palanca.ayuda,
            ) / 100
            st.session_state["plan3"][palanca.codigo] = valor

    resultado3 = alcance3.simular3(grupo, st.session_state["plan3"])
    st.session_state["resultado3"] = resultado3

    with derecha:
        st.metric(
            "Reducción del alcance 3", _pct(resultado3["reduccion"]),
            delta=f'{_num((resultado3["reduccion"] - alcance3.OBJETIVO3) * 100)} '
                  f'puntos respecto al objetivo',
        )
        st.progress(min(1.0, resultado3["reduccion"] / alcance3.OBJETIVO3))
        st.metric("Inversión comprometida", _eur(resultado3["coste_eur"]))
        st.metric("Presupuesto de alcance 3", _eur(presupuesto),
                  help="Es aparte del que habéis gastado antes. Aquí no se "
                       "compran furgonetas: se financian programas.")
        restante = resultado3["presupuesto_restante_eur"]
        if resultado3["objetivo_cumplido"] and resultado3["dentro_de_presupuesto"]:
            st.success("Objetivo de alcance 3 cumplido.", icon="✔️")
        elif not resultado3["dentro_de_presupuesto"]:
            st.error(f"Os habéis pasado {_eur(-restante)}.", icon="⚠️")
        else:
            faltan = resultado3["objetivo_t"] - resultado3["evitado_t"]
            st.warning(f"Os faltan {_num(faltan, 0)} t.", icon="⚠️")

    detalle = pd.DataFrame([{
        "Palanca": fila["nombre"],
        "Intensidad": _pct(fila["intensidad"], 0),
        "Evita": _num(fila["evitado_t"], 0) + " t",
        "Cuesta": _eur(fila["coste_eur"]),
        "€ por tonelada": ("—" if fila["coste_por_t"] == float("inf")
                           else _num(fila["coste_por_t"], 0) + " €"),
    } for fila in resultado3["detalle"]])
    st.dataframe(detalle, hide_index=True, use_container_width=True)

    st.info(
        f"El objetivo aquí es del **{int(alcance3.OBJETIVO3 * 100)} %**, no "
        f"del {int(palancas.OBJETIVO * 100)} %. No es benevolencia: sobre el "
        f"alcance 3 no mandáis, negociáis. Se reduce convenciendo a un "
        f"proveedor, cambiando de proveedor o vendiendo otra cosa, y las "
        f"tres son lentas.",
        icon="🎯",
    )

    st.divider()
    st.markdown("### Lo que os lleváis de aquí")
    _respuesta(
        "alcance3_reaccion",
        "Con la huella entera delante, ¿el plan que acabáis de hacer sigue "
        "siendo el plan correcto? ¿Qué cambiaríais?",
        grupo, alto=110,
    )
    _respuesta(
        "alcance3_limite",
        "¿Qué parte de vuestro alcance 3 no controláis vosotros, y a quién "
        "tendríais que convencer para moverla?",
        grupo, alto=100,
    )

    st.divider()
    _descargar(grupo, st.session_state.get("resultado"), resultado3)


def _descargar(grupo: str, resultado: dict | None,
               resultado3: dict | None = None) -> None:
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
        key="integrantes_s2",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = documento_plan.generar(
            grupo, resultado, st.session_state.get("respuestas2", {}),
            integrantes, resultado3,
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
    ayuda.panel(2)
    st.divider()

    if paso == 0:
        _paso_punto_de_partida(grupo)
    elif paso == 1:
        _paso_palancas(grupo)
    elif paso == 2:
        _paso_plan(grupo)
    else:
        _paso_alcance3(grupo)

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
