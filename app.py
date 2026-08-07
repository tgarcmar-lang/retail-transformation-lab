"""Retail Transformation Lab — punto de entrada.

Escuela Politécnica · Universidad Camilo José Cela
"""

import streamlit as st

from core import datos, filiales, kpis, marca, sesiones
from modulos import (sesion1_diagnostico, sesion2_descarbonizacion,
                     sesion3_circular, sesion4_reporting, sesion5_ejecucion,
                     sesion6_kanban, sesion7_cambio)

st.set_page_config(
    page_title="Retail Transformation Lab",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

ESTILOS = """
<style>
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
    .abierta   { background: #F7E8EE; color: #872046; }
    .bloqueada { background: #E2E8F0; color: #64748B; }
</style>
"""
st.markdown(ESTILOS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def cifras_de_portada() -> list[tuple[str, str]]:
    """Las cifras del grupo, leídas de los datos y cacheadas.

    Si los datos no estuvieran donde deben, la portada se dibuja sin cifras
    en lugar de romperse: el alumno vería una pantalla en blanco y no
    entendería por qué.
    """
    try:
        r = kpis.resumen_corporativo()
    except Exception:
        return []
    return [
        (f'{r["ventas_eur"] / 1e6:,.0f} M€'.replace(",", "."), "Ventas anuales"),
        (f'{r["puntos_de_venta"]}', "Puntos de venta"),
        (f'{r["vehiculos"]}', "Vehículos"),
        (f'{r["co2e_t"]:,.0f} t'.replace(",", "."), "CO₂e al año"),
        (f'{r["filiales"]}', "Filiales"),
    ]


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
            st.session_state["respuestas2"] = {}
            st.session_state["plan"] = {}
            st.session_state["plan3"] = {}
            st.session_state["plan3c"] = {}
            st.session_state["respuestas3"] = {}
            st.session_state["respuestas4"] = {}
            st.session_state["seleccion4"] = []
            st.session_state["declaraciones4"] = {}
            st.session_state["respuestas5"] = {}
            st.session_state["plan5"] = {}
            st.session_state["paso3"] = 0
            st.session_state["paso4"] = 0
            st.session_state["paso5"] = 0
            st.session_state["respuestas6"] = {}
            st.session_state["paso6"] = 0
            st.session_state["respuestas7"] = {}
            st.session_state["plan7"] = {}
            st.session_state["paso7"] = 0
            st.session_state.pop("resultado7", None)
            st.session_state["consultas_tutor"] = 0
            st.session_state.pop("wip6", None)
            st.session_state.pop("flujo6", None)
            st.session_state.pop("resultado6", None)
            st.session_state.pop("hibrido6", None)
            st.session_state.pop("resultado5", None)
            st.session_state.pop("resultado5_sin", None)
            st.session_state.pop("resultado3c", None)
            st.session_state.pop("evaluacion4", None)
            st.session_state.pop("resultado", None)
            st.session_state.pop("resultado3", None)
            st.session_state["tutor_respuestas"] = {}
            st.session_state["paso"] = 0
            st.session_state["paso2"] = 0
        st.session_state["grupo"] = grupo

    if st.session_state.get("vista") in ("sesion1", "sesion2", "sesion3", "sesion4", "sesion5",
     "sesion6", "sesion7"):
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

if st.session_state.get("vista") in ("sesion1", "sesion2", "sesion3", "sesion4", "sesion5",
     "sesion6", "sesion7") and grupo:
    filial_actual = filiales.obtener(grupo)
    st.markdown(
        marca.cabecera_compacta(f"{filial_actual.nombre} · Grupo {grupo}"),
        unsafe_allow_html=True,
    )
else:
    st.markdown(marca.cabecera(cifras_de_portada()), unsafe_allow_html=True)

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
    sesion1_diagnostico.mostrar(grupo)
    st.stop()

if st.session_state.get("vista") == "sesion2":
    sesion2_descarbonizacion.mostrar(grupo)
    st.stop()

if st.session_state.get("vista") == "sesion3":
    sesion3_circular.mostrar(grupo)
    st.stop()

if st.session_state.get("vista") == "sesion4":
    sesion4_reporting.mostrar(grupo)
    st.stop()

if st.session_state.get("vista") == "sesion5":
    sesion5_ejecucion.mostrar(grupo)
    st.stop()

if st.session_state.get("vista") == "sesion6":
    sesion6_kanban.mostrar(grupo)
    st.stop()

if st.session_state.get("vista") == "sesion7":
    sesion7_cambio.mostrar(grupo)
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

entrada1, entrada2, entrada3 = st.columns(3)
entrada4, entrada5, entrada6 = st.columns(3)
entrada7, _, _ = st.columns(3)
if entrada1.button("Entrar en la Sesión 1 · Diagnóstico",
                   type="primary", use_container_width=True):
    st.session_state["vista"] = "sesion1"
    st.rerun()
if entrada2.button("Entrar en la Sesión 2 · Descarbonización",
                   use_container_width=True):
    st.session_state["vista"] = "sesion2"
    st.rerun()
if entrada3.button("Entrar en la Sesión 3 · Economía circular",
                   use_container_width=True):
    st.session_state["vista"] = "sesion3"
    st.rerun()
if entrada4.button("Entrar en la Sesión 4 · Reporting ESG",
                   use_container_width=True):
    st.session_state["vista"] = "sesion4"
    st.rerun()
if entrada5.button("Entrar en la Sesión 5 · Ejecución",
                   use_container_width=True):
    st.session_state["vista"] = "sesion5"
    st.rerun()
if entrada6.button("Entrar en la Sesión 6 · Seguimiento",
                   use_container_width=True):
    st.session_state["vista"] = "sesion6"
    st.rerun()
if entrada7.button("Entrar en la Sesión 7 · Gestión del cambio",
                   use_container_width=True):
    st.session_state["vista"] = "sesion7"
    st.rerun()
