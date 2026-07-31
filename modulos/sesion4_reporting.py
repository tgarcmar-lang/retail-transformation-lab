"""Sesión 4 · Medición, reporting y estrategia ESG.

Cuatro pasos. **La mecánica cambia**: en las sesiones 2 y 3 la restricción era
el presupuesto y había un óptimo que encontrar. Aquí la restricción es que la
memoria resista una revisión externa, y no hay óptimo: hay criterio.

1. **A quién hay que contárselo** — qué es la CSRD, a quién obliga después
   del paquete Ómnibus y qué estándares existen. Capa conceptual.
2. **Qué es material** — la matriz de doble materialidad de su filial,
   calculada con sus propios datos.
3. **Qué publicáis** — eligen indicadores dentro de un límite y toman cinco
   decisiones de presentación. Ahí están las tentaciones.
4. **La revisión** — el verificador les devuelve una opinión, y la memoria
   se descarga con las salvedades impresas dentro.

Este módulo es solo interfaz. El modelo vive en `core/reporting.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import datos, filiales, memoria, reporting, tutor

GRANATE = "#872046"
VERDE = "#0F766E"
GRIS = "#94A3B8"
AMBAR = "#B45309"
ROJO = "#B91C1C"

COLOR_DIMENSION = {"Ambiental": VERDE, "Social": AMBAR, "Gobernanza": GRANATE}

PASOS = [
    ("A quién hay que contárselo", "Qué obliga la CSRD y qué estándares hay"),
    ("Qué es material", "La doble materialidad de vuestra filial"),
    ("Qué publicáis", "Elegid indicadores y decidid cómo presentarlos"),
    ("La revisión", "Lo que diría un verificador, y vuestra memoria"),
]


def _num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "·").replace(".", ",").replace("·", ".")


def _pct(valor: float, decimales: int = 1) -> str:
    return _num(valor * 100, decimales) + " %"


def _grafico(figura: go.Figure, alto: int = 320) -> None:
    figura.update_layout(
        height=alto, margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    st.plotly_chart(figura, use_container_width=True)


def _respuesta(clave: str, etiqueta: str, grupo: str,
               ayuda: str = "", alto: int = 100) -> None:
    st.session_state.setdefault("respuestas4", {})
    valor = st.text_area(
        etiqueta,
        value=st.session_state["respuestas4"].get(clave, ""),
        key=f"s4_{clave}", height=alto, help=ayuda or None,
        placeholder="Escribid aquí…",
    )
    st.session_state["respuestas4"][clave] = valor
    _tutor(clave, grupo)


def _tutor(clave: str, grupo: str) -> None:
    from modulos.sesion1_diagnostico import LIMITE_TUTOR

    st.session_state.setdefault("tutor_usos", 0)
    st.session_state.setdefault("tutor_respuestas", {})
    usos = st.session_state["tutor_usos"]
    agotado = usos >= LIMITE_TUTOR

    izquierda, derecha = st.columns([1, 3])
    pulsado = izquierda.button(
        "Preguntar al tutor", key=f"s4_tutor_{clave}", disabled=agotado,
        help="Lee lo que habéis escrito y os devuelve una pregunta.",
    )
    if agotado:
        derecha.caption("Habéis gastado las consultas. Preguntad al profesor.")

    if pulsado:
        escrito = st.session_state["respuestas4"].get(clave, "")
        try:
            secretos = st.secrets
        except Exception:
            secretos = None
        with st.spinner("El tutor está leyendo lo que habéis escrito…"):
            texto, del_tutor = tutor.preguntar(
                grupo, f"s4_{clave}", escrito, secretos, semilla=usos
            )
        st.session_state["tutor_respuestas"][f"s4_{clave}"] = (texto, del_tutor)
        st.session_state["tutor_usos"] = usos + 1

    guardada = st.session_state["tutor_respuestas"].get(f"s4_{clave}")
    if guardada:
        texto, del_tutor = guardada
        st.info(f"**El tutor os pregunta:** {texto}")
        if not del_tutor:
            st.caption("Pregunta del banco de la asignatura.")


# --------------------------------------------------------------------------
# Paso 1 · A quién hay que contárselo
# --------------------------------------------------------------------------

def _paso_marco(grupo: str) -> None:
    st.markdown("### Por qué una empresa publica esto")

    st.markdown(
        "Hasta ahora habéis **decidido**. En esta sesión vais a **declarar**, "
        "que es otra cosa: lo que se publica se audita, se compara y se usa "
        "para tomar decisiones sobre vuestra empresa. Y responde alguien con "
        "nombre y apellidos."
    )

    with st.expander("El marco obligatorio: la CSRD", expanded=True):
        st.markdown(
            "La **CSRD** es la directiva europea que obliga a publicar "
            "información de sostenibilidad con el mismo rigor que la "
            "financiera: auditada, comparable y en un formato común, los "
            "**ESRS**."
        )
        st.warning(
            "**Ojo, que esto se movió hace nada.** El paquete **Ómnibus I**, "
            "publicado en febrero de 2026, recortó el número de empresas "
            "obligadas de unas 50.000 a unas 5.000 —cerca del 90 % quedaron "
            "fuera—, simplificó los ESRS eliminando hasta la mitad de los "
            "puntos de dato y aplazó la entrada del nuevo perímetro al 1 de "
            "enero de 2027. Si buscáis información de 2024, estará "
            "desactualizada.",
            icon="📅",
        )
        st.info(
            "**RetailNova sigue obligada.** El nuevo umbral deja dentro a las "
            "grandes empresas: más de 500 empleados o más de 250 M€ de "
            "facturación. El grupo factura 1.149 M€ y emplea a 5.539 "
            "personas. Esto no es un ejercicio hipotético.",
            icon="✔️",
        )

    with st.expander("El mapa de estándares, en treinta segundos"):
        st.dataframe(pd.DataFrame([
            {"Estándar": "GHG Protocol", "Para qué sirve":
             "Cómo se cuentan las emisiones y qué son los tres alcances. Es "
             "la base de todo lo demás.", "Obligatorio": "No, pero es el uso"},
            {"Estándar": "ISO 14083:2023", "Para qué sirve":
             "Cómo se calculan y declaran las emisiones del transporte y la "
             "logística. Construida sobre el GLEC Framework.",
             "Obligatorio": "No, es el lenguaje del sector"},
            {"Estándar": "ESRS (CSRD)", "Para qué sirve":
             "Qué hay que publicar, con qué estructura y con qué "
             "verificación.", "Obligatorio": "Sí, para quien entra"},
            {"Estándar": "GRI", "Para qué sirve":
             "El estándar voluntario más extendido en el mundo. Compatible "
             "con los ESRS.", "Obligatorio": "No"},
            {"Estándar": "SBTi", "Para qué sirve":
             "Valida que un objetivo de reducción es coherente con la "
             "ciencia. Su norma v2.0 exige separar los objetivos de alcances "
             "1 y 2 de los de alcance 3.", "Obligatorio": "No"},
        ]), hide_index=True, use_container_width=True)
        st.success(
            "**Fijaos en la última línea.** En la Sesión 2 os pusimos dos "
            "objetivos separados, uno para alcances 1 y 2 y otro para el "
            "alcance 3. No fue un capricho: es exactamente lo que exige el "
            "SBTi en su norma de 2026. Vuestro plan ya tiene la estructura "
            "correcta.",
            icon="🎯",
        )

    st.divider()
    st.markdown("### Vuestros planes anteriores")
    st.caption(
        "Sacad el plan de descarbonización y el de economía circular. Vais a "
        "declarar lo que decidisteis en ellos."
    )
    _respuesta(
        "compromisos_previos",
        "¿A qué os comprometisteis en las sesiones 2 y 3? Anotad los dos "
        "objetivos y lo que os costaba cada uno.",
        grupo, alto=100,
    )
    _respuesta(
        "quien_lee",
        "¿Quién va a leer esta memoria y qué decisión va a tomar con ella?",
        grupo,
        ayuda="No es una pregunta retórica: cambia qué indicadores elegís.",
        alto=90,
    )


# --------------------------------------------------------------------------
# Paso 2 · Qué es material
# --------------------------------------------------------------------------

def _paso_materialidad(grupo: str) -> None:
    filial = filiales.obtener(grupo)
    tabla = reporting.matriz_materialidad(grupo)

    st.markdown(f"### La doble materialidad de {filial.nombre}")
    st.markdown(
        "Un asunto es material por **dos caminos distintos**, y basta con "
        "uno: por el **impacto** que vuestra filial tiene sobre el entorno, o "
        "por las **consecuencias financieras** que ese asunto tiene sobre "
        "vosotros. Confundirlo con «lo que hacemos mal» es el error más "
        "común: el transporte es material en una filial que mueve mucha "
        "mercancía aunque la mueva bien."
    )

    figura = px.scatter(
        tabla, x="financiera", y="impacto", text="nombre_tema",
        color="dimension", color_discrete_map=COLOR_DIMENSION,
        labels={"financiera": "Materialidad financiera →",
                "impacto": "Materialidad de impacto →",
                "dimension": "Dimensión"},
        range_x=[0.5, 5.5], range_y=[0.5, 5.5],
    )
    figura.update_traces(textposition="top center", marker=dict(size=14))
    figura.add_hline(y=reporting.UMBRAL_MATERIALIDAD, line_dash="dash",
                     line_color=GRIS)
    figura.add_vline(x=reporting.UMBRAL_MATERIALIDAD, line_dash="dash",
                     line_color=GRIS)
    _grafico(figura, alto=460)

    marco = pd.DataFrame([{
        "Asunto": fila.nombre_tema,
        "Dimensión": fila.dimension,
        "Impacto": _num(fila.impacto, 1),
        "Financiera": _num(fila.financiera, 1),
        "¿Material?": "Sí" if fila.material else "No",
    } for fila in tabla.itertuples()])
    st.dataframe(marco, hide_index=True, use_container_width=True)

    materiales = tabla[tabla["material"]]
    st.info(
        f"**Vuestra filial tiene {len(materiales)} asuntos materiales:** "
        f"{', '.join(materiales['nombre_tema'])}. De todos ellos tenéis que "
        f"informar. De los demás, no: publicarlo todo no es transparencia, es "
        f"enterrar lo importante.",
        icon="🎯",
    )

    with st.expander("Qué significa cada asunto"):
        for fila in tabla.itertuples():
            st.markdown(f"**{fila.nombre_tema}** · _{fila.dimension}_")
            st.caption(fila.explicacion)

    st.divider()
    _respuesta(
        "material_fuera",
        "Elegid un asunto que os haya salido NO material y explicad por qué "
        "no lo es en vuestra filial. ¿Estáis de acuerdo con el resultado?",
        grupo, alto=110,
    )


# --------------------------------------------------------------------------
# Paso 3 · Qué publicáis
# --------------------------------------------------------------------------

def _paso_publicar(grupo: str) -> None:
    catalogo = reporting.catalogo(grupo)
    materiales = reporting.temas_materiales(grupo)

    st.markdown("### Elegid los indicadores")
    st.caption(
        f"Podéis publicar como máximo {reporting.MAXIMO_INDICADORES}. "
        f"Tenéis que cubrir vuestros {len(materiales)} asuntos materiales."
    )

    st.session_state.setdefault("seleccion4", [])
    seleccion = list(st.session_state["seleccion4"])

    for dimension in ["Ambiental", "Social", "Gobernanza"]:
        del_bloque = catalogo[catalogo["dimension"] == dimension]
        if del_bloque.empty:
            continue
        st.markdown(f"**{dimension}**")
        for fila in del_bloque.itertuples():
            es_material = fila.tema in materiales
            decimales = 0 if abs(fila.valor) >= 100 else 2
            etiqueta = (
                f"{fila.nombre} — {_num(fila.valor, decimales)} {fila.unidad}"
                f"  ·  {fila.estandar}  ·  dato de calidad {fila.calidad}"
            )
            marcado = st.checkbox(
                etiqueta, value=fila.codigo in seleccion,
                key=f"ind_{fila.codigo}",
                help=fila.nota or None,
            )
            if marcado and fila.codigo not in seleccion:
                seleccion.append(fila.codigo)
            if not marcado and fila.codigo in seleccion:
                seleccion.remove(fila.codigo)
            if es_material:
                st.caption("↑ pertenece a un asunto material de vuestra filial")

    st.session_state["seleccion4"] = seleccion

    izquierda, derecha = st.columns(2)
    izquierda.metric("Indicadores elegidos",
                     f"{len(seleccion)} de {reporting.MAXIMO_INDICADORES}")
    cubiertos = {reporting.POR_CODIGO[c].tema for c in seleccion}
    faltan = [t for t in materiales if t not in cubiertos]
    derecha.metric("Asuntos materiales cubiertos",
                   f"{len(materiales) - len(faltan)} de {len(materiales)}")

    if len(seleccion) > reporting.MAXIMO_INDICADORES:
        st.error(
            f"Os habéis pasado del límite. Publicar de más no es "
            f"transparencia: obliga al lector a buscar lo importante entre "
            f"lo accesorio.", icon="⚠️",
        )
    if faltan:
        st.warning(
            "Os faltan asuntos materiales por cubrir: "
            + ", ".join(reporting.POR_TEMA[t].nombre for t in faltan),
            icon="⚠️",
        )

    st.divider()
    st.markdown("### Cómo lo contáis")
    st.caption(
        "Cinco decisiones de presentación. Todas las opciones son ciertas: "
        "ninguna miente. Elegid con cuidado."
    )

    st.session_state.setdefault("declaraciones4", {})
    for declaracion in reporting.DECLARACIONES:
        claves = list(declaracion.opciones)
        actual = st.session_state["declaraciones4"].get(declaracion.codigo)
        indice = claves.index(actual) if actual in claves else None
        elegida = st.radio(
            declaracion.pregunta,
            claves, index=indice,
            format_func=lambda c, d=declaracion: d.opciones[c],
            key=f"decl_{declaracion.codigo}",
        )
        st.session_state["declaraciones4"][declaracion.codigo] = elegida
        st.write("")

    st.divider()
    _respuesta(
        "peor_cifra",
        "¿Cuál es la peor cifra que publicáis? ¿Por qué la publicáis "
        "igualmente?",
        grupo, alto=90,
    )


# --------------------------------------------------------------------------
# Paso 4 · La revisión
# --------------------------------------------------------------------------

def _paso_revision(grupo: str) -> None:
    seleccion = st.session_state.get("seleccion4", [])
    declaraciones = st.session_state.get("declaraciones4", {})
    evaluacion = reporting.evaluar(grupo, seleccion, declaraciones)
    st.session_state["evaluacion4"] = evaluacion

    st.markdown("### La revisión del verificador")
    st.caption(
        "Una memoria de sostenibilidad se audita. Esto es lo que diría quien "
        "tuviera que firmarla."
    )

    color = {"favorable": st.success, "con salvedades": st.warning,
             "desfavorable": st.error}[evaluacion["opinion"]]
    color(
        f"**Opinión {evaluacion['opinion']}** — "
        f"{evaluacion['graves']} hallazgos graves y "
        f"{evaluacion['salvedades']} salvedades.",
        icon="🖋️",
    )

    a, b, c = st.columns(3)
    a.metric("Cobertura de asuntos materiales",
             _pct(evaluacion["cobertura"], 0))
    b.metric("Indicadores publicados", len(evaluacion["indicadores"]))
    c.metric("Hallazgos", len(evaluacion["hallazgos"]))

    if evaluacion["hallazgos"]:
        for hallazgo in evaluacion["hallazgos"]:
            icono = "🔴" if hallazgo["gravedad"] == "grave" else "🟠"
            with st.container(border=True):
                st.markdown(f"{icono} **{hallazgo['titulo']}**")
                st.caption(hallazgo["detalle"])
    else:
        st.success(
            "Sin hallazgos. La memoria cubre todos los asuntos materiales y "
            "ninguna de las decisiones de presentación induce a error.",
            icon="✔️",
        )

    st.divider()
    st.info(
        "**Ninguna de las opciones que rechazasteis era falsa.** Sumar dos "
        "porcentajes, dar la tasa de reciclaje o publicar solo cifras "
        "absolutas son cosas que se hacen todos los días y que resisten una "
        "comprobación literal. Engañan igual. Por eso existe la verificación "
        "y por eso alguien tiene que firmar.",
        icon="✍️",
    )

    st.divider()
    _respuesta(
        "compromiso",
        "¿A qué os comprometéis para el año que viene, y cómo se comprobará "
        "si lo habéis cumplido?",
        grupo,
        ayuda="Un compromiso que no se puede comprobar no es un compromiso.",
        alto=100,
    )

    st.divider()
    _descargar(grupo, seleccion, declaraciones, evaluacion)


def _descargar(grupo: str, seleccion: list[str], declaraciones: dict,
               evaluacion: dict) -> None:
    st.markdown("### Llevaos vuestra memoria")

    integrantes = st.text_input(
        "Nombres de los integrantes del grupo",
        value=st.session_state.get("integrantes", ""),
        placeholder="Ana García, Luis Pérez, Marta Ruiz",
        key="integrantes_s4",
    )
    st.session_state["integrantes"] = integrantes

    try:
        html = memoria.generar(
            grupo, seleccion, declaraciones, evaluacion,
            st.session_state.get("respuestas4", {}), integrantes,
        )
    except Exception as error:
        st.error(
            "No he podido generar la memoria. Avisad al profesor y seguid "
            f"trabajando: vuestras respuestas están guardadas. ({error})"
        )
        return

    st.download_button(
        "Descargar la memoria de sostenibilidad",
        data=html.encode("utf-8"),
        file_name=memoria.nombre_de_fichero(grupo),
        mime="text/html", type="primary", use_container_width=True,
    )
    st.caption(
        "La memoria se descarga con la revisión incluida, salvedades "
        "incluidas. Así se publica en la vida real."
    )


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

    st.markdown("## Sesión 4 · Medición, reporting y estrategia ESG")
    st.caption(
        "Vuestra filial tiene que publicar su memoria de sostenibilidad. "
        "Aquí no hay presupuesto: la restricción es que resista una revisión."
    )

    st.session_state.setdefault("paso4", 0)
    etiquetas = [f"{i + 1}. {nombre}" for i, (nombre, _) in enumerate(PASOS)]
    elegido = st.radio(
        "Paso", etiquetas, index=st.session_state["paso4"],
        horizontal=True, label_visibility="collapsed",
    )
    paso = etiquetas.index(elegido)
    st.session_state["paso4"] = paso

    st.progress((paso + 1) / len(PASOS), text=PASOS[paso][1])
    st.divider()

    if paso == 0:
        _paso_marco(grupo)
    elif paso == 1:
        _paso_materialidad(grupo)
    elif paso == 2:
        _paso_publicar(grupo)
    else:
        _paso_revision(grupo)

    st.divider()
    anterior, _, siguiente = st.columns([1, 3, 1])
    if paso > 0 and anterior.button("← Paso anterior", use_container_width=True,
                                    key="s4_anterior"):
        st.session_state["paso4"] = paso - 1
        st.rerun()
    if paso < len(PASOS) - 1 and siguiente.button(
        "Paso siguiente →", type="primary", use_container_width=True,
        key="s4_siguiente",
    ):
        st.session_state["paso4"] = paso + 1
        st.rerun()
