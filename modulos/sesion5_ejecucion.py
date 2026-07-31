"""Sesión 5 · Ejecución del plan con métodos ágiles.

Cuatro pasos. La mecánica vuelve a cambiar: aquí no se decide **qué** hacer
—eso ya está decidido en las sesiones 2, 3 y 4— sino **en qué orden** y con
qué consecuencias.

1. **Qué hay que ejecutar** — el backlog de la filial, y la clasificación
   que sostiene la sesión: qué parte es predictiva y qué parte es iterativa.
2. **Vuestros sprints** — reparten el trabajo entre seis sprints con una
   capacidad que no da para todo.
3. **Lo que no estaba en el plan** — aparecen los contratiempos de su
   filial y hay que replanificar.
4. **La retrospectiva** — la curva de entrega, la comparación con las dos
   referencias y el acta descargable.

Este módulo es solo interfaz. El modelo vive en `core/proyecto.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import acta, datos, filiales, proyecto, tutor

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"

COLOR_ENFOQUE = {"Predictivo": GRANATE, "Iterativo": VERDE}

PASOS = [
    ("Qué hay que ejecutar", "Vuestro backlog y cómo se gestiona cada parte"),
    ("Vuestros sprints", "Repartid el trabajo: no cabe todo"),
    ("Lo que no estaba en el plan", "Los contratiempos de vuestra filial"),
    ("La retrospectiva", "Qué entregasteis, cuándo y qué aprendisteis"),
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
    st.session_state.setdefault("respuestas5", {})
    valor = st.text_area(
        etiqueta,
        value=st.session_state["respuestas5"].get(clave, ""),
        key=f"s5_{clave}", height=alto, help=ayuda or None,
        placeholder="Escribid aquí…",
    )
    st.session_state["respuestas5"][clave] = valor
    _tutor(clave, grupo)


def _tutor(clave: str, grupo: str) -> None:
    from modulos.sesion1_diagnostico import LIMITE_TUTOR

    st.session_state.setdefault("tutor_usos", 0)
    st.session_state.setdefault("tutor_respuestas", {})
    usos = st.session_state["tutor_usos"]
    agotado = usos >= LIMITE_TUTOR

    izquierda, derecha = st.columns([1, 3])
    pulsado = izquierda.button(
        "Preguntar al tutor", key=f"s5_tutor_{clave}", disabled=agotado,
        help="Lee lo que habéis escrito y os devuelve una pregunta.",
    )
    if agotado:
        derecha.caption("Habéis gastado las consultas. Preguntad al profesor.")

    if pulsado:
        escrito = st.session_state["respuestas5"].get(clave, "")
        try:
            secretos = st.secrets
        except Exception:
            secretos = None
        with st.spinner("El tutor está leyendo lo que habéis escrito…"):
            texto, del_tutor = tutor.preguntar(
                grupo, f"s5_{clave}", escrito, secretos, semilla=usos
            )
        st.session_state["tutor_respuestas"][f"s5_{clave}"] = (texto, del_tutor)
        st.session_state["tutor_usos"] = usos + 1

    guardada = st.session_state["tutor_respuestas"].get(f"s5_{clave}")
    if guardada:
        texto, del_tutor = guardada
        st.info(f"**El tutor os pregunta:** {texto}")
        if not del_tutor:
            st.caption("Pregunta del banco de la asignatura.")


def _plan_actual(grupo: str) -> dict[int, list[str]]:
    st.session_state.setdefault("plan5", {})
    plan = st.session_state["plan5"]
    return {s: list(plan.get(s, [])) for s in range(1, proyecto.SPRINTS + 1)}


# --------------------------------------------------------------------------
# Paso 1 · Qué hay que ejecutar
# --------------------------------------------------------------------------

def _paso_backlog(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    resumen = proyecto.resumen(grupo)

    st.markdown(f"### El proyecto de {filial.nombre}")
    st.markdown(
        "Durante tres sesiones habéis decidido qué hacer. Nada de eso se ha "
        "ejecutado todavía. Esto es vuestra cartera de iniciativas: sale de "
        "las palancas que analizasteis, con su coste y su impacto reales."
    )

    a, b, c, d = st.columns(4)
    a.metric("Iniciativas", resumen["iniciativas"])
    b.metric("Esfuerzo total", f'{resumen["esfuerzo_total"]} puntos')
    c.metric("Capacidad por sprint", _num(resumen["capacidad_sprint"]))
    d.metric("Sprints que harían falta",
             _num(resumen["sprints_necesarios"]),
             delta=f'Tenéis {proyecto.SPRINTS}',
             delta_color="inverse")

    st.error(
        f"**No cabe todo.** Vuestro backlog necesita "
        f"{_num(resumen['sprints_necesarios'])} sprints y tenéis "
        f"{proyecto.SPRINTS}. Ninguna metodología arregla eso: lo único que "
        f"se puede decidir es qué entra, en qué orden y qué se queda fuera.",
        icon="⚠️",
    )

    st.divider()
    st.markdown("### Lo que no todos los planes tienen en común")
    st.markdown(
        "Aquí está el contenido de la sesión. **Vuestro plan no se gestiona "
        "todo igual**, y confundirlo es el error más caro de la dirección de "
        "proyectos."
    )
    izquierda, derecha = st.columns(2)
    izquierda.markdown(
        "**Predictivo**\n\nAlcance cerrado desde el principio. Hay un "
        "proveedor, un permiso, un precio y una fecha. No hay nada que "
        "descubrir: hay que ejecutarlo bien. Meterlo en sprints y hacer una "
        "retrospectiva cada dos semanas no lo acelera, solo añade reuniones."
    )
    derecha.markdown(
        "**Iterativo**\n\nNo se sabe qué funciona hasta probarlo. Se avanza "
        "por tandas, se mide y se corrige. Planificarlo entero a doce meses "
        "es escribir una ficción: el plan quedará obsoleto en cuanto el "
        "primer piloto dé un resultado inesperado."
    )

    tabla = proyecto.tabla_backlog(grupo)
    figura = px.bar(
        tabla, x="esfuerzo", y="nombre", orientation="h", color="enfoque",
        color_discrete_map=COLOR_ENFOQUE,
        labels={"esfuerzo": "Esfuerzo (puntos)", "nombre": "",
                "enfoque": "Cómo se gestiona"},
        hover_data=["valor", "origen"],
    )
    _grafico(figura, alto=420)

    st.info(
        f"**El {_pct(resumen['pct_predictivo'])} de vuestro esfuerzo es "
        f"predictivo.** Es la parte que se compra, se instala y se pone en "
        f"marcha. El resto se descubre trabajando. Si tratáis todo como si "
        f"fuera lo mismo, os equivocaréis en las dos mitades.",
        icon="🧭",
    )

    with st.expander("Ver el backlog completo con su clasificación"):
        marco = pd.DataFrame([{
            "Iniciativa": fila.nombre,
            "Viene de": fila.origen,
            "Cómo se gestiona": fila.enfoque,
            "Esfuerzo": fila.esfuerzo,
            "Valor": fila.valor,
            "Valor por punto": _num(fila.valor_por_punto, 2),
            "Depende de": fila.depende_de or "—",
        } for fila in tabla.itertuples()])
        st.dataframe(marco, hide_index=True, use_container_width=True)
        for fila in tabla.itertuples():
            st.markdown(f"**{fila.nombre}** · _{fila.enfoque}_")
            st.caption(fila.porque)

    st.divider()
    _respuesta(
        "clasificacion",
        "Elegid una iniciativa de cada tipo y explicad por qué no se pueden "
        "gestionar igual. ¿Estáis de acuerdo con la clasificación?",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 2 · Vuestros sprints
# --------------------------------------------------------------------------

def _paso_sprints(grupo: str) -> None:
    catalogo = proyecto.por_codigo(grupo)
    tabla = proyecto.tabla_backlog(grupo)
    capacidad = proyecto.capacidad(grupo)

    st.markdown("### Repartid el trabajo entre los seis sprints")
    st.caption(
        f"Cada sprint admite {_num(capacidad)} puntos. Lo que no quepa se "
        f"arrastra al siguiente: no desaparece, os persigue."
    )

    st.session_state.setdefault("plan5", {})
    asignado: dict[str, int] = {}
    for sprint, codigos in st.session_state["plan5"].items():
        for codigo in codigos:
            asignado[codigo] = sprint

    opciones = ["No entra"] + [f"Sprint {s}" for s in range(1, proyecto.SPRINTS + 1)]
    nuevo: dict[int, list[str]] = {s: [] for s in range(1, proyecto.SPRINTS + 1)}

    for fila in tabla.itertuples():
        iniciativa = catalogo[fila.codigo]
        actual = asignado.get(fila.codigo, 0)
        etiqueta = (
            f"{iniciativa.nombre} — {iniciativa.esfuerzo} puntos, "
            f"valor {iniciativa.valor} · {iniciativa.enfoque}"
        )
        elegido = st.selectbox(
            etiqueta, opciones, index=actual,
            key=f"s5_asig_{fila.codigo}",
            help=iniciativa.porque,
        )
        if elegido != "No entra":
            nuevo[int(elegido.split()[1])].append(fila.codigo)

    st.session_state["plan5"] = nuevo

    resultado = proyecto.simular(grupo, nuevo, con_eventos=False)
    st.session_state["resultado5_sin"] = resultado

    st.divider()
    st.markdown("### Cómo queda vuestro plan, si nada sale mal")
    _pintar_sprints(resultado, catalogo)

    a, b = st.columns(2)
    a.metric("Valor entregado", f'{resultado["valor_entregado"]} de '
                                f'{resultado["valor_total"]}')
    b.metric("Entregado a mitad de camino",
             f'{resultado["valor_en_sprint_3"]} puntos de valor',
             help="Lo que ya está en la calle al terminar el sprint 3.")

    if resultado["valor_en_sprint_3"] == 0:
        st.warning(
            "**No entregáis nada hasta pasada la mitad del proyecto.** Puede "
            "estar justificado, pero tendréis que explicarlo: durante tres "
            "sprints nadie fuera del equipo verá una sola mejora.",
            icon="⚠️",
        )

    st.divider()
    _respuesta(
        "orden",
        "¿Por qué habéis elegido este orden? ¿Qué habéis dejado fuera?",
        grupo, alto=100,
    )


def _pintar_sprints(resultado: dict, catalogo: dict) -> None:
    filas = []
    for sprint in resultado["detalle"]:
        filas.append({
            "Sprint": sprint["sprint"],
            "Capacidad": _num(sprint["capacidad"]),
            "Usada": _num(sprint["usada"]),
            "Entregado": ", ".join(catalogo[c].nombre for c in sprint["entregadas"]) or "—",
            "En curso o esperando": len(sprint["arrastradas"]),
            "Valor acumulado": sprint["valor_acumulado"],
        })
    st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)


# --------------------------------------------------------------------------
# Paso 3 · Lo que no estaba en el plan
# --------------------------------------------------------------------------

def _paso_eventos(grupo: str) -> None:
    catalogo = proyecto.por_codigo(grupo)
    plan = _plan_actual(grupo)

    st.markdown("### Lo que no estaba en el plan")
    st.caption(
        "Han pasado cosas. Son las de vuestra filial y no las de las otras "
        "cuatro."
    )

    for evento in proyecto.eventos(grupo):
        with st.container(border=True):
            st.markdown(f"**Sprint {evento.sprint} · {evento.titulo}**")
            st.write(evento.relato)
            if evento.efecto == "bloquea":
                afectada = catalogo.get(evento.objetivo)
                st.caption(
                    f"Efecto: «{afectada.nombre if afectada else evento.objetivo}» "
                    f"queda bloqueada {int(evento.magnitud)} sprints."
                )
            elif evento.efecto == "encarece":
                afectada = catalogo.get(evento.objetivo)
                st.caption(
                    f"Efecto: «{afectada.nombre if afectada else evento.objetivo}» "
                    f"cuesta un {_pct(evento.magnitud)} más."
                )
            else:
                st.caption(
                    f"Efecto: perdéis un {_pct(evento.magnitud)} de capacidad "
                    f"en ese sprint."
                )

    resultado = proyecto.simular(grupo, plan, con_eventos=True)
    sin_eventos = proyecto.simular(grupo, plan, con_eventos=False)
    st.session_state["resultado5"] = resultado

    st.divider()
    st.markdown("### Qué le han hecho a vuestro plan")

    a, b, c = st.columns(3)
    a.metric("Valor que esperabais", sin_eventos["valor_entregado"])
    b.metric("Valor que entregáis", resultado["valor_entregado"],
             delta=resultado["valor_entregado"] - sin_eventos["valor_entregado"])
    c.metric("Iniciativas sin terminar", len(resultado["sin_entregar"]))

    _pintar_sprints(resultado, catalogo)

    if resultado["valor_entregado"] < sin_eventos["valor_entregado"]:
        st.warning(
            "**El plan ya no se cumple.** Podéis volver al paso 2 y "
            "reordenarlo sabiendo lo que sabéis ahora. Eso es replanificar, "
            "y no es admitir un fracaso: es la única respuesta razonable a "
            "una información nueva.",
            icon="🔁",
        )
    else:
        st.success(
            "Vuestro plan aguanta los contratiempos. O teníais holgura, o "
            "habíais puesto pronto lo que no dependía de nadie.",
            icon="✔️",
        )

    st.divider()
    _respuesta(
        "replanificacion",
        "¿Qué cambiaríais de vuestro plan ahora que conocéis los "
        "contratiempos? ¿Y qué habríais hecho distinto desde el principio "
        "para que os afectaran menos?",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 4 · La retrospectiva
# --------------------------------------------------------------------------

def _paso_retrospectiva(grupo: str) -> None:
    catalogo = proyecto.por_codigo(grupo)
    plan = _plan_actual(grupo)
    resultado = proyecto.simular(grupo, plan, con_eventos=True)
    st.session_state["resultado5"] = resultado

    por_valor = proyecto.simular(grupo, proyecto.plan_por_valor(grupo))
    por_tamano = proyecto.simular(grupo, proyecto.plan_por_tamano(grupo))

    st.markdown("### Vuestra curva de entrega")

    serie = []
    for nombre, datos_plan in [("Vuestro plan", resultado),
                               ("Priorizando por valor", por_valor),
                               ("Empezando por lo más grande", por_tamano)]:
        for sprint in datos_plan["detalle"]:
            serie.append({
                "Sprint": sprint["sprint"],
                "Valor acumulado": sprint["valor_acumulado"],
                "Plan": nombre,
            })
    figura = px.line(
        pd.DataFrame(serie), x="Sprint", y="Valor acumulado", color="Plan",
        markers=True,
        color_discrete_map={"Vuestro plan": GRANATE,
                            "Priorizando por valor": VERDE,
                            "Empezando por lo más grande": GRIS},
    )
    _grafico(figura, alto=360)

    a, b, c = st.columns(3)
    a.metric("Vuestro plan", f'{resultado["valor_entregado"]} de '
                             f'{resultado["valor_total"]}')
    b.metric("Priorizando por valor", por_valor["valor_entregado"])
    c.metric("Empezando por lo grande", por_tamano["valor_entregado"])

    st.info(
        f"**La línea gris es lo que hace casi todo el mundo:** ordenar la "
        f"cartera por tamaño y atacar primero lo gordo. Entrega "
        f"{por_tamano['valor_entregado']} de {por_tamano['valor_total']}, y "
        f"no entrega nada hasta muy tarde. No es que la gente sea torpe: es "
        f"que lo grande parece lo importante, y casi nunca lo es.",
        icon="📉",
    )

    st.divider()
    st.markdown("### Qué se quedó fuera")
    if resultado["sin_entregar"]:
        marco = pd.DataFrame([{
            "Iniciativa": catalogo[c].nombre,
            "Cómo se gestiona": catalogo[c].enfoque,
            "Esfuerzo": catalogo[c].esfuerzo,
            "Valor perdido": catalogo[c].valor,
            "Avance": _pct(
                min(1.0, resultado["progreso"].get(c, 0) / catalogo[c].esfuerzo)
            ),
        } for c in resultado["sin_entregar"]])
        st.dataframe(marco, hide_index=True, use_container_width=True)
        a_medias = [c for c in resultado["sin_entregar"]
                    if resultado["progreso"].get(c, 0) > 0]
        if a_medias:
            st.error(
                f"**Tenéis {len(a_medias)} iniciativas a medias.** Trabajo "
                f"invertido que no ha entregado nada de valor. Es la forma "
                f"más cara de terminar un proyecto: gastado y sin resultado.",
                icon="⚠️",
            )
    else:
        st.success("Habéis entregado el backlog completo.", icon="✔️")

    st.divider()
    st.markdown("### La retrospectiva")
    _respuesta(
        "aprendizaje",
        "Si empezarais mañana otra vez el mismo proyecto, ¿qué haríais "
        "distinto en el primer sprint?",
        grupo, alto=100,
    )
    _respuesta(
        "hibrido",
        "¿Qué parte de vuestro proyecto habríais llevado con sprints y qué "
        "parte con un plan cerrado y una fecha? ¿Por qué?",
        grupo,
        ayuda="Es la pregunta que más se parece a la vida real.",
        alto=110,
    )

    st.divider()
    _descargar(grupo, resultado)


def _descargar(grupo: str, resultado: dict) -> None:
    st.markdown("### Llevaos el acta")

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
        key="integrantes_s5",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = acta.generar(
            grupo, resultado, st.session_state.get("respuestas5", {}),
            integrantes,
        )
    except Exception as error:
        st.error(
            "No he podido generar el acta. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar el acta del proyecto",
        data=html.encode("utf-8"),
        file_name=acta.nombre_de_fichero(grupo),
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

    st.markdown("## Sesión 5 · Ejecución del plan")
    st.caption(
        "Tres sesiones decidiendo y ninguna ejecutando. Hoy hay que repartir "
        "el trabajo en sprints, con una capacidad que no da para todo."
    )

    st.session_state.setdefault("paso5", 0)
    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    elegido = st.radio(
        "Paso", etiquetas, index=st.session_state["paso5"],
        horizontal=True, label_visibility="collapsed",
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso5"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    st.divider()

    if paso == 0:
        _paso_backlog(grupo)
    elif paso == 1:
        _paso_sprints(grupo)
    elif paso == 2:
        _paso_eventos(grupo)
    else:
        _paso_retrospectiva(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True,
                                    key="s5_anterior"):
        st.session_state["paso5"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True,
        key="s5_siguiente",
    ):
        st.session_state["paso5"] = paso + 1
        st.rerun()
