"""Retail Transformation Lab — punto de entrada.

Escuela Politécnica · Universidad Camilo José Cela
"""

import streamlit as st

from core import filiales, sesiones
from modulos import sesion1_diagnostico

st.set_page_config(
    page_title="Retail Transformation Lab",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

ESTILOS = """
<style>
    .bloque-titulo {
        border-left: 4px solid #0F766E;
        padding-left: 1rem;
        margin-bottom: 1.5rem;
    }
    .bloque-titulo h1 { margin-bottom: 0.2rem; font-size: 2.1rem; }
    .bloque-titulo p  { color: #64748B; margin: 0; }
    .tarjeta {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        height: 100%;
    }
    .tarjeta-bloqueada { opacity: 0.5; }
    .tarjeta h4 { margin: 0 0 0.4rem 0; font-size: 1.05rem; }
    .tarjeta p  { margin: 0; color: #475569; font-size: 0.9rem; }
    .etiqueta {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        margin-bottom: 0.6rem;
    }
    .abierta   { background: #CCFBF1; color: #0F766E; }
    .bloqueada { background: #E2E8F0; color: #64748B; }
</style>
"""
st.markdown(ESTILOS, unsafe_allow_html=True)


# ── Barra lateral ────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Retail Transformation Lab")
    st.caption("Escuela Politécnica · UCJC")
    st.divider()

    opciones = {f"Grupo {f.grupo} — {f.nombre}": f.grupo for f in filiales.listar()}
    elegido = st.selectbox(
        "¿Qué filial diriges?",
        options=list(opciones),
        index=None,
        placeholder="Selecciona tu grupo",
    )
    grupo = opciones.get(elegido)

    if grupo:
        # Si el grupo cambia, se descarta lo escrito: son respuestas de otra
        # filial y mezclarlas produciría un informe incoherente.
        if st.session_state.get("grupo") != grupo:
            st.session_state["respuestas"] = {}
            st.session_state["paso"] = 0
        st.session_state["grupo"] = grupo

    if st.session_state.get("vista") == "sesion1":
        st.divider()
        if st.button("← Volver al inicio", use_container_width=True):
            st.session_state["vista"] = "inicio"
            st.rerun()

    st.divider()
    st.caption(
        "Trabaja con un ordenador por grupo. "
        "Todo lo que hagas se exporta al final de la sesión."
    )


# ── Contenido principal ──────────────────────────────────────────────────────

st.markdown(
    """
    <div class="bloque-titulo">
        <h1>Retail Transformation Lab</h1>
        <p>Dirige la transformación sostenible de RetailNova Europa</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not grupo:
    st.info(
        "**Selecciona tu grupo en el panel de la izquierda para empezar.**\n\n"
        "Cada grupo dirige una filial distinta de RetailNova Europa. "
        "Todas comparten los mismos objetivos corporativos, pero parten de "
        "situaciones diferentes: distinta flota, distintos almacenes, distinto "
        "mix de producto. Las decisiones que toméis condicionarán las sesiones "
        "siguientes."
    )
    st.stop()

filial = filiales.obtener(grupo)

# ── Sesión 1 ─────────────────────────────────────────────────────────────────

if st.session_state.get("vista") == "sesion1":
    st.caption(f"{filial.nombre} · Grupo {grupo}")
    sesion1_diagnostico.mostrar(grupo)
    st.stop()


# ── Portada de la filial ─────────────────────────────────────────────────────

st.success(f"Diriges **{filial.nombre}** ({filial.codigo})")

izquierda, derecha = st.columns([2, 1])

with izquierda:
    st.markdown("#### Tu filial")
    st.write(filial.perfil)
    st.markdown(f"**Reto principal:** {filial.reto_principal}")

with derecha:
    st.metric("Centros logísticos", filial.centros_logisticos)
    st.metric("Vehículos", filial.vehiculos)
    st.metric("Antigüedad media de la flota", f"{filial.antiguedad_media_flota:.1f} años")
    st.metric("Ventas online", f"{filial.pct_ecommerce:.0%}")

st.divider()
st.markdown("#### El curso")
st.caption(
    "Siete sesiones. Cada una desbloquea un módulo nuevo y parte de donde "
    "terminó la anterior."
)

columnas = st.columns(4)
for indice, sesion in enumerate(sesiones.SESIONES):
    with columnas[indice % 4]:
        clase = "tarjeta" if sesion.disponible else "tarjeta tarjeta-bloqueada"
        etiqueta = (
            '<span class="etiqueta abierta">Disponible</span>'
            if sesion.disponible
            else '<span class="etiqueta bloqueada">Próximamente</span>'
        )
        st.markdown(
            f"""
            <div class="{clase}">
                {etiqueta}
                <h4>{sesion.numero}. {sesion.titulo}</h4>
                <p>{sesion.objetivo}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

st.divider()

if st.button("Entrar en la Sesión 1 · Diagnóstico", type="primary"):
    st.session_state["vista"] = "sesion1"
    st.rerun()
