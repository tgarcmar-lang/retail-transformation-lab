"""Sesión 1 · Diagnóstico.

Recorrido guiado de cinco pasos, pensado para unos 60-75 minutos de clase.
El alumno no elige por dónde empezar: la primera vez que se toca una
herramienta de análisis, la libertad absoluta paraliza. Al final de cada paso
hay una pregunta que se responde por escrito, y esas respuestas son las que
acaban en el informe que el grupo se lleva.

Este módulo es solo interfaz. Todo lo que calcula vive en `core/kpis.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import datos, filiales, informe, kpis, tutor

VERDE = "#0F766E"
GRIS = "#94A3B8"
ROJO = "#B91C1C"
AMBAR = "#B45309"

PASOS = [
    ("Tu filial", "Qué tamaño tiene y a qué se dedica"),
    ("Cómo vende", "Estacionalidad, formatos, categorías y canal"),
    ("Cómo opera", "Reparto, proveedores e inventario"),
    ("Qué emite", "Energía, combustible y huella de carbono"),
    ("Tu diagnóstico", "Compara, concluye y descarga el informe"),
]


# --------------------------------------------------------------------------
# Utilidades de presentación
# --------------------------------------------------------------------------

def _eur(valor: float, decimales: int = 1) -> str:
    if abs(valor) >= 1_000_000:
        return _num(valor / 1_000_000, decimales) + " M€"
    if abs(valor) >= 1_000:
        return _num(valor / 1_000, 0) + " k€"
    return _num(valor, 0) + " €"


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _pct(valor: float, decimales: int = 1) -> str:
    return _num(valor * 100, decimales) + " %"


def _grafico(figura: go.Figure, alto: int = 320) -> None:
    figura.update_layout(
        height=alto,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        showlegend=figura.layout.showlegend,
    )
    figura.update_xaxes(showgrid=False)
    figura.update_yaxes(gridcolor="#E2E8F0")
    st.plotly_chart(figura, use_container_width=True)


#: Cuántas veces puede un grupo pedir ayuda al tutor en toda la sesión.
#: No es por la cuota: es pedagógico. Si pudieran pulsar sin límite, el
#: ejercicio se convertiría en ir preguntando hasta que salga la respuesta.
LIMITE_TUTOR = 12


def _pregunta(clave: str, grupo: str | None = None) -> None:
    """Caja de respuesta. Lo escrito se guarda y acaba en el informe."""
    st.markdown("##### Vuestra respuesta")
    st.caption("Se guarda sola y aparecerá en el informe que descarguéis al final.")
    st.session_state.setdefault("respuestas", {})
    valor = st.text_area(
        informe.PREGUNTAS[clave],
        value=st.session_state["respuestas"].get(clave, ""),
        key=f"respuesta_{clave}",
        height=110,
        placeholder="Escribid aquí lo que habéis visto en los datos…",
    )
    st.session_state["respuestas"][clave] = valor
    if grupo:
        _tutor(clave, grupo)


def _tutor(clave: str, grupo: str) -> None:
    """El tutor de guardia: devuelve una pregunta, nunca una respuesta.

    Si no hay clave de Google configurada, o si Google falla, sale igual una
    pregunta escrita a mano. Desde fuera no se nota la diferencia salvo por
    la nota al pie, que dice la verdad sobre de dónde viene.
    """
    st.session_state.setdefault("tutor_usos", 0)
    st.session_state.setdefault("tutor_respuestas", {})

    usos = st.session_state["tutor_usos"]
    agotado = usos >= LIMITE_TUTOR

    izquierda, derecha = st.columns([1, 3])
    pulsado = izquierda.button(
        "Preguntar al tutor",
        key=f"tutor_{clave}",
        disabled=agotado,
        help="Lee lo que habéis escrito y os devuelve una pregunta para "
             "haceros avanzar. No os va a dar la respuesta.",
    )
    if agotado:
        derecha.caption(
            "Habéis gastado las consultas al tutor. A partir de aquí, "
            "preguntad al profesor."
        )

    if pulsado:
        escrito = st.session_state["respuestas"].get(clave, "")
        try:
            secretos = st.secrets
        except Exception:
            secretos = None
        with st.spinner("El tutor está leyendo lo que habéis escrito…"):
            texto, del_tutor = tutor.preguntar(
                grupo, clave, escrito, secretos, semilla=usos
            )
        st.session_state["tutor_respuestas"][clave] = (texto, del_tutor)
        st.session_state["tutor_usos"] = usos + 1

    guardada = st.session_state["tutor_respuestas"].get(clave)
    if guardada:
        texto, del_tutor = guardada
        st.info(f"**El tutor os pregunta:** {texto}")
        if not del_tutor:
            st.caption("Pregunta del banco de la asignatura.")


def _pista(texto: str) -> None:
    with st.expander("¿Atascados? Abrid esta pista"):
        st.markdown(texto)


# --------------------------------------------------------------------------
# Paso 1 · Tu filial
# --------------------------------------------------------------------------

def _paso_tu_filial(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    r = kpis.retrato(grupo)
    c = kpis.canal(grupo)
    cre = kpis.crecimiento(grupo)

    st.markdown(f"### Diriges {filial.nombre}")
    st.write(filial.perfil)

    a, b, c3, d = st.columns(4)
    a.metric("Ventas del año", _eur(r["ventas_eur"]),
             delta=_pct(cre["variacion"]) + f" vs {cre['anio_anterior']}")
    b.metric("Puntos de venta", r["puntos_de_venta"],
             help=f'De los cuales {r["grandes_almacenes"]} son grandes almacenes')
    c3.metric("Superficie de venta", f'{_num(r["superficie_m2"], 0)} m²')
    d.metric("Ventas por m²", f'{_num(r["ventas_por_m2"], 0)} €')

    a, b, c3, d = st.columns(4)
    a.metric("Vehículos", r["vehiculos"])
    b.metric("Antigüedad de la flota", f'{_num(r["antiguedad_flota"])} años')
    c3.metric("Centros logísticos", r["centros_logisticos"],
              help=f'{_num(r["tiendas_por_centro"])} tiendas por centro')
    d.metric("Canal online", _pct(c["cuota_online"]))

    st.divider()
    st.markdown("#### Tu parque de tiendas")
    formatos = kpis.ventas_por_formato(grupo)

    izquierda, derecha = st.columns([3, 2])
    with izquierda:
        figura = px.bar(
            formatos, x="nombre_formato", y="ventas_eur",
            title="Ventas por formato de tienda",
            labels={"nombre_formato": "", "ventas_eur": "Ventas (€)"},
            color_discrete_sequence=[VERDE],
        )
        _grafico(figura)
    with derecha:
        tabla = formatos[["nombre_formato", "tiendas", "ventas_por_m2", "pct_ventas"]].copy()
        tabla.columns = ["Formato", "Tiendas", "€/m²", "% ventas"]
        tabla["€/m²"] = tabla["€/m²"].map(lambda v: _num(v, 0))
        tabla["% ventas"] = tabla["% ventas"].map(_pct)
        st.dataframe(tabla, hide_index=True, use_container_width=True)

    st.info(
        "**Fijaos en la última columna.** Un gran almacén vende mucho en total, "
        "pero puede vender poco por cada metro cuadrado. Son dos preguntas "
        "distintas y conviene no mezclarlas."
    )


# --------------------------------------------------------------------------
# Paso 2 · Cómo vende
# --------------------------------------------------------------------------

def _paso_como_vende(grupo: str) -> None:
    st.markdown("### Cómo vende tu filial")

    serie = kpis.ventas_por_mes(grupo)
    figura = go.Figure()
    figura.add_bar(x=serie["mes"], y=serie["tienda_eur"], name="Tienda física",
                   marker_color=VERDE)
    figura.add_bar(x=serie["mes"], y=serie["online_eur"], name="Online",
                   marker_color=GRIS)
    figura.update_layout(barmode="stack", title="Ventas mes a mes",
                         showlegend=True, legend=dict(orientation="h", y=1.12))
    _grafico(figura, alto=340)

    _pista(
        "- ¿Qué mes es siempre el más alto? ¿Y el más bajo?\n"
        "- ¿Se repite el mismo patrón los dos años?\n"
        "- ¿Hay algún mes que se comporte distinto en vuestra filial "
        "que en la vecina? El clima y el turismo no afectan igual en "
        "Bilbao que en Valencia.\n"
        "- La barra gris crece más deprisa que la verde. ¿Por qué?"
    )

    st.divider()
    izquierda, derecha = st.columns(2)

    with izquierda:
        st.markdown("#### Qué vendéis")
        categorias = kpis.ventas_por_categoria(grupo)
        figura = px.pie(
            categorias, names="nombre_categoria", values="total_eur", hole=0.45,
            color_discrete_sequence=[VERDE, GRIS, AMBAR],
        )
        figura.update_traces(textposition="inside", textinfo="percent")
        figura.update_layout(legend=dict(orientation="h", y=-0.15))
        _grafico(figura, alto=300)

    with derecha:
        st.markdown("#### Cuánto de eso se compra por internet")
        categorias = kpis.ventas_por_categoria(grupo)
        figura = px.bar(
            categorias, x="pct_online", y="nombre_categoria", orientation="h",
            labels={"pct_online": "Cuota online", "nombre_categoria": ""},
            color_discrete_sequence=[VERDE],
        )
        figura.update_xaxes(tickformat=".0%")
        _grafico(figura, alto=300)
        st.caption(
            "La alimentación apenas se compra por internet en España: entre el "
            "3 % y el 5 %. La moda y la electrónica, muchísimo más."
        )

    c = kpis.canal(grupo)
    a, b, c3 = st.columns(3)
    a.metric("Pedidos online al año", _num(c["pedidos"], 0))
    b.metric("Ticket medio online", f'{_num(c["ticket_medio_online"])} €')
    c3.metric("Se recogen en tienda", _pct(c["pct_recogida_en_tienda"]),
              help="El resto se entrega a domicilio, con el coste y las "
                   "emisiones que eso supone")

    st.divider()
    _pregunta("paso2", grupo)


# --------------------------------------------------------------------------
# Paso 3 · Cómo opera
# --------------------------------------------------------------------------

def _paso_como_opera(grupo: str) -> None:
    st.markdown("### Cómo opera tu filial")

    log = kpis.logistica(grupo)
    flo = kpis.flota_resumen(grupo)
    cad = kpis.cadena_suministro(grupo)
    inv = kpis.inventario_resumen(grupo)

    st.markdown("#### Reparto")
    a, b, c3, d = st.columns(4)
    a.metric("Kilómetros al año", _num(log["km_totales"], 0))
    b.metric("Kilómetros en vacío", _pct(log["pct_km_en_vacio"]),
             help="Kilómetros recorridos sin carga. Se pagan igual y "
                  "contaminan igual, pero no entregan nada.")
    c3.metric("Ocupación media", _pct(log["ocupacion_media"]))
    d.metric("Entregas fallidas", _pct(log["pct_entregas_fallidas"]),
             help="Cada fallo obliga a repetir el viaje: se paga dos veces.")

    a, b, c3, d = st.columns(4)
    a.metric("Gasóleo al año", f'{_num(flo["litros"] / 1000, 0)} miles de litros')
    b.metric("Coste del combustible", _eur(flo["coste_eur"]))
    c3.metric("Consumo medio", f'{_num(flo["consumo_medio_l_100km"])} L/100 km')
    d.metric("Flota con norma Euro 6", _pct(flo["pct_euro6"]))

    st.divider()
    st.markdown("#### De dónde viene la mercancía")
    izquierda, derecha = st.columns([3, 2])
    origenes = kpis.compras_por_origen(grupo)
    with izquierda:
        figura = px.scatter(
            origenes, x="plazo_medio_dias", y="pct_compras",
            size="importe_eur", color="pct_puntualidad", text="pais_origen",
            labels={"plazo_medio_dias": "Plazo de entrega (días)",
                    "pct_compras": "Peso en las compras",
                    "pct_puntualidad": "Puntualidad"},
            color_continuous_scale=["#B91C1C", "#F59E0B", "#0F766E"],
        )
        figura.update_traces(textposition="top center")
        figura.update_yaxes(tickformat=".0%")
        _grafico(figura, alto=340)
    with derecha:
        a, b = st.columns(2)
        a.metric("Plazo medio", f'{_num(cad["plazo_medio_dias"])} días')
        b.metric("Compra en Asia", _pct(cad["pct_compra_asiatica"]))
        a.metric("Puntualidad", _pct(cad["pct_puntualidad"]))
        b.metric("Proveedores", cad["proveedores"])
        st.caption(
            "Cuanto más a la derecha está un país, más se tarda en recibir su "
            "mercancía. Y todo lo que tarda en llegar hay que tenerlo antes en "
            "el almacén: eso es dinero parado."
        )

    st.divider()
    st.markdown("#### Qué hay parado en el almacén")
    a, b, c3 = st.columns(3)
    a.metric("Stock medio", _eur(inv["stock_medio_eur"]))
    b.metric("Días de cobertura", _num(inv["dias_cobertura"], 0),
             help="Cuántos días se podría seguir vendiendo sin reponer nada")
    c3.metric("Merma", _pct(inv["pct_merma"], 2),
              help="Producto que se pierde, caduca o se rompe antes de venderse")

    calidad = kpis.calidad_de_los_datos(grupo)
    if calidad["partes_de_ruta_sin_km"] or calidad["lecturas_electricas_ausentes"]:
        st.warning(
            f'**Cuidado con los datos.** De vuestros '
            f'{calidad["partes_de_ruta_totales"]} partes de ruta del año, '
            f'{calidad["partes_de_ruta_sin_km"]} llegaron sin kilometraje, y '
            f'{calidad["lecturas_electricas_ausentes"]} lecturas de contador '
            f'eléctrico están en blanco. Los indicadores de arriba se calculan '
            f'con lo que hay. ¿Cambia eso vuestras conclusiones?'
        )

    st.divider()
    _pregunta("paso3", grupo)


# --------------------------------------------------------------------------
# Paso 4 · Qué emite
# --------------------------------------------------------------------------

def _paso_que_emite(grupo: str) -> None:
    st.markdown("### Qué consume y qué emite tu filial")

    hue = kpis.huella(grupo)
    ene = kpis.energia_resumen(grupo)
    res = kpis.residuos_resumen(grupo)
    total = hue["co2e_t"].sum()

    a, b, c3, d = st.columns(4)
    a.metric("Huella de carbono", f"{_num(total, 0)} t CO₂e")
    b.metric("Electricidad", f'{_num(ene["electricidad_kwh"] / 1e6, 1)} GWh')
    c3.metric("Energía por millón vendido",
              f'{_num(ene["intensidad_mwh_por_meur"], 0)} MWh')
    d.metric("Residuos reciclados", _pct(res["pct_reciclado"]))

    izquierda, derecha = st.columns([3, 2])
    with izquierda:
        figura = px.bar(
            hue, x="co2e_t", y="fuente", orientation="h",
            labels={"co2e_t": "Toneladas de CO₂ equivalente", "fuente": ""},
            color="alcance", color_discrete_map={1: AMBAR, 2: VERDE},
        )
        figura.update_layout(showlegend=True, legend_title_text="Alcance",
                             legend=dict(orientation="h", y=1.15))
        _grafico(figura, alto=300)
    with derecha:
        tabla = hue[["fuente", "co2e_t", "pct"]].copy()
        tabla.columns = ["Fuente", "t CO₂e", "% del total"]
        tabla["t CO₂e"] = tabla["t CO₂e"].map(lambda v: _num(v, 0))
        tabla["% del total"] = tabla["% del total"].map(_pct)
        st.dataframe(tabla, hide_index=True, use_container_width=True)

    st.info(
        "**Alcance 1** son las emisiones que salís vosotros: el gasóleo que "
        "quema vuestra flota y el gas que se escapa de vuestros equipos de frío. "
        "**Alcance 2** son las de la electricidad que compráis, que emite quien "
        "la produce. Las dos cuentan, y sobre las dos se puede actuar."
    )

    _pista(
        "- ¿Qué fuente pesa más? ¿Es la que esperabais?\n"
        "- Las fugas de refrigerante son un gas invisible que no cuesta dinero "
        "cuando se escapa. Mirad qué peso tienen en vuestra filial y comparad "
        "con otra que use un gas distinto.\n"
        "- Dividid las toneladas entre los millones vendidos. Una filial grande "
        "que emite mucho puede ser más eficiente que una pequeña que emite poco."
    )

    st.divider()
    _pregunta("paso4", grupo)


# --------------------------------------------------------------------------
# Paso 5 · Tu diagnóstico
# --------------------------------------------------------------------------

def _paso_diagnostico(grupo: str) -> None:
    st.markdown("### Tu filial frente a las otras cuatro")
    st.caption(
        "Un número aislado no dice nada. El 34 % solo asusta cuando se ve al "
        "lado del 14 %."
    )

    posicion = kpis.posicion(grupo)

    def _situacion(puesto: int) -> str:
        return {1: "La mejor", 2: "Por encima", 3: "En la media",
                4: "Por debajo", 5: "La peor"}[int(puesto)]

    tabla = pd.DataFrame({
        "Indicador": posicion["indicador"],
        "Tu filial": [
            _pct(v) if u == "%" else _num(v, 1 if u != "€/m²" else 0)
            for v, u in zip(posicion["valor"], posicion["unidad"])
        ],
        "Unidad": posicion["unidad"],
        "Media": [
            _pct(v) if u == "%" else _num(v, 1 if u != "€/m²" else 0)
            for v, u in zip(posicion["media"], posicion["unidad"])
        ],
        "Puesto": posicion["puesto"].map(lambda x: f"{x}º de 5"),
        "Situación": posicion["puesto"].map(_situacion),
    })
    st.dataframe(tabla, hide_index=True, use_container_width=True)

    fuertes = posicion[posicion["puesto"] == 1]["indicador"].tolist()
    debiles = kpis.puntos_debiles(grupo)

    izquierda, derecha = st.columns(2)
    with izquierda:
        st.markdown("#### En qué sois los mejores")
        if fuertes:
            for indicador in fuertes:
                st.success(indicador, icon="✔️")
        else:
            st.info("En ningún indicador sois los primeros. Eso también dice algo.")
    with derecha:
        st.markdown("#### Dónde estáis peor")
        for fila in debiles.itertuples():
            st.error(
                f"**{fila.indicador}** — puesto {fila.puesto} de 5. "
                f"La mejor filial está en "
                f"{_pct(fila.mejor) if fila.unidad == '%' else _num(fila.mejor)}"
                f"{'' if fila.unidad == '%' else ' ' + fila.unidad}.",
                icon="⚠️",
            )

    st.warning(
        "**Esto no es todavía vuestro diagnóstico.** La tabla dice *dónde* "
        "estáis peor, no *por qué*. Lo segundo lo tenéis que explicar vosotros, "
        "y para eso hay que volver a los pasos anteriores."
    )

    st.divider()
    st.markdown("### El diagnóstico de vuestro grupo")
    for clave in ("diagnostico", "evidencia", "coste", "propuesta"):
        _pregunta(clave, grupo)

    st.divider()
    _descargar_informe(grupo)


def _descargar_informe(grupo: str) -> None:
    st.markdown("### Llevaos vuestro informe")

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
    )
    st.session_state["integrantes"] = integrantes

    respuestas = st.session_state.get("respuestas", {})
    sin_responder = [
        clave for clave in informe.PREGUNTAS
        if not respuestas.get(clave, "").strip()
    ]
    if sin_responder:
        st.info(
            f"Quedan {len(sin_responder)} preguntas sin responder. Podéis "
            "descargar el informe igualmente, pero saldrán en blanco."
        )

    try:
        documento = informe.generar(grupo, respuestas, integrantes)
    except Exception as error:  # la clase no se para nunca por un fallo nuestro
        st.error(
            "No he podido generar el informe. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar el informe de diagnóstico",
        data=documento.encode("utf-8"),
        file_name=informe.nombre_de_fichero(grupo),
        mime="text/html",
        type="primary",
        use_container_width=True,
    )
    st.caption(
        "Se descarga como página web. Para convertirlo en PDF: abridlo, "
        "Ctrl+P y elegid *Guardar como PDF*."
    )


# --------------------------------------------------------------------------
# Punto de entrada del módulo
# --------------------------------------------------------------------------

def mostrar(grupo: str) -> None:
    """Dibuja la Sesión 1 completa para la filial del grupo indicado."""
    if not datos.hay_datos():
        st.error(
            "No encuentro los datos de RetailNova. Avisad al profesor: hay que "
            "generarlos con `python -m datos.retailnova.generador`."
        )
        return

    st.markdown("## Sesión 1 · Diagnóstico")
    st.caption(
        "Cinco pasos para conocer vuestra filial. No hace falta terminarlos "
        "todos para descargar el informe, pero cuanto más avancéis, mejor será."
    )

    st.session_state.setdefault("paso", 0)
    paso = st.session_state["paso"]

    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    elegido = st.radio(
        "Paso", etiquetas, index=paso, horizontal=True, label_visibility="collapsed"
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    st.divider()

    if paso == 0:
        _paso_tu_filial(grupo)
    elif paso == 1:
        _paso_como_vende(grupo)
    elif paso == 2:
        _paso_como_opera(grupo)
    elif paso == 3:
        _paso_que_emite(grupo)
    else:
        _paso_diagnostico(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True):
        st.session_state["paso"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True
    ):
        st.session_state["paso"] = paso + 1
        st.rerun()
