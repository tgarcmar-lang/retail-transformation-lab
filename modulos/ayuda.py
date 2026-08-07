"""El panel del tutor, compartido por las siete sesiones.

Antes cada módulo tenía su propia copia del botón «Preguntar al tutor». Al
pasar de un modo a tres, mantener siete copias iguales dejó de tener sentido.

**Los tres modos, y por qué son tres.** En la primera prueba con alumnos la
queja fue que el tutor solo preguntaba y no resolvía nada, así que acababan
en un motor de IA externo. La respuesta no es abrirlo del todo —regalar el
hallazgo destruye la sesión— sino separar lo que hay que proteger de lo que
no:

- **Explicar** — conceptos, métodos y estándares. Responde de verdad. No
  recibe ningún dato de la filial, así que no puede desvelar nada.
- **Dónde mirar** — en qué paso y en qué columna está el dato. Es lo único
  que este tutor puede hacer y ningún asistente externo puede.
- **Preguntar** — lee lo que ha escrito el grupo y le devuelve una pregunta.
  Es el modo original y sigue siendo el que más enseña.
"""

from __future__ import annotations

import streamlit as st

from core import conceptos, tutor

#: Consultas de explicación y orientación por grupo. Es más alto que el
#: límite de preguntas porque explicar un concepto no resuelve el ejercicio:
#: no hay razón para racionarlo como se raciona el modo socrático.
LIMITE_CONSULTAS = 30

#: Preguntas al tutor por grupo. Este sí es pedagógico y no de cuota: sin
#: límite, el ejercicio se convierte en pulsar hasta que salga la respuesta.
LIMITE_PREGUNTAS = 12


def _secretos():
    try:
        return st.secrets
    except Exception:
        return None


def panel(sesion: int, clave_estado: str = "consulta_tutor") -> None:
    """El panel de ayuda: explicar y orientar. Va al principio de la sesión.

    No depende de que el grupo haya escrito nada, a diferencia del modo
    pregunta: es una duda que se resuelve cuando surge.
    """
    st.session_state.setdefault("consultas_tutor", 0)
    usadas = st.session_state["consultas_tutor"]

    with st.expander("¿Alguna duda? Preguntadle al tutor", expanded=False):
        st.caption(
            "Os explica conceptos, métodos y estándares, y os dice en qué "
            "pantalla está cada dato. Lo que no os va a decir es qué le pasa "
            "a vuestra filial: eso está en los datos y es vuestro trabajo."
        )

        consulta = st.text_input(
            "¿Qué queréis saber?",
            key=f"{clave_estado}_{sesion}",
            placeholder="Por ejemplo: qué es el alcance 3, o dónde miro los "
                        "kilómetros en vacío",
        )

        izquierda, centro, derecha = st.columns([1, 1, 2])
        explicar = izquierda.button(
            "Explícamelo", key=f"expl_{sesion}",
            disabled=usadas >= LIMITE_CONSULTAS,
        )
        orientar = centro.button(
            "¿Dónde lo miro?", key=f"orient_{sesion}",
            disabled=usadas >= LIMITE_CONSULTAS,
        )
        if usadas >= LIMITE_CONSULTAS:
            derecha.caption("Habéis gastado las consultas de esta sesión.")

        if explicar and consulta.strip():
            texto, origen = tutor.explicar(consulta, _secretos(), sesion)
            st.session_state[f"resp_{sesion}"] = (texto, origen)
            st.session_state["consultas_tutor"] = usadas + 1
        elif orientar and consulta.strip():
            texto, acertado = tutor.orientar(consulta, sesion)
            st.session_state[f"resp_{sesion}"] = (
                texto, "banco" if acertado else "sin_respuesta"
            )
            st.session_state["consultas_tutor"] = usadas + 1

        guardada = st.session_state.get(f"resp_{sesion}")
        if guardada:
            texto, origen = guardada
            st.markdown(texto)
            if origen == "banco":
                st.caption("Explicación del material de la asignatura.")
            elif origen == "tutor":
                st.caption(
                    "Respuesta generada. Contrastadla: puede equivocarse."
                )

        st.divider()
        st.caption("Conceptos que os puedo explicar en esta sesión:")
        de_la_sesion = conceptos.del_curso(sesion)
        if de_la_sesion:
            st.caption(" · ".join(c.titulo for c in de_la_sesion))
        st.caption(
            "Y los de las sesiones anteriores: escribid el nombre y ya está."
        )


def pregunta(clave: str, grupo: str, sesion: int, respuestas: str) -> None:
    """El modo socrático: lee lo escrito y devuelve una pregunta.

    `respuestas` es la clave de `st.session_state` donde vive el diccionario
    de respuestas de esa sesión.
    """
    st.session_state.setdefault("tutor_usos", 0)
    st.session_state.setdefault("tutor_respuestas", {})
    usos = st.session_state["tutor_usos"]
    agotado = usos >= LIMITE_PREGUNTAS
    marca = f"s{sesion}_{clave}"

    izquierda, derecha = st.columns([1, 3])
    pulsado = izquierda.button(
        "Preguntar al tutor", key=f"btn_{marca}", disabled=agotado,
        help="Lee lo que habéis escrito y os devuelve una pregunta. "
             "No os va a dar la respuesta.",
    )
    if agotado:
        derecha.caption("Habéis gastado las preguntas. Preguntad al profesor.")

    if pulsado:
        escrito = st.session_state.get(respuestas, {}).get(clave, "")
        with st.spinner("El tutor está leyendo lo que habéis escrito…"):
            texto, del_tutor = tutor.preguntar(
                grupo, marca, escrito, _secretos(), semilla=usos
            )
        st.session_state["tutor_respuestas"][marca] = (texto, del_tutor)
        st.session_state["tutor_usos"] = usos + 1

    guardada = st.session_state["tutor_respuestas"].get(marca)
    if guardada:
        texto, del_tutor = guardada
        st.info(f"**El tutor os pregunta:** {texto}")
        if not del_tutor:
            st.caption("Pregunta del banco de la asignatura.")
