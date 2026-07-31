"""Tutor de guardia: el asistente que acompaña a los grupos en clase.

El profesor no puede estar en cinco mesas a la vez. Mientras atiende a un
grupo, los otros cuatro se quedan solos. Esto hace lo que haría él si
estuviera allí: leer lo que ha escrito el grupo y devolverle **una pregunta**.

Tres reglas de diseño, en orden de importancia:

1. **Nunca da la respuesta.** Lo único valioso de la sesión es que el hallazgo
   lo encuentren ellos. Un asistente que lo suelta destruye la clase. Por eso
   el contexto que se le envía no contiene el diagnóstico de la filial, solo
   cifras que el alumno ya tiene delante en pantalla.
2. **Nunca para la clase.** Sin clave, sin cuota, sin conexión o con cualquier
   fallo de Google, se devuelve una pregunta escrita a mano. El alumno recibe
   siempre algo útil y no ve jamás un error.
3. **No añade dependencias.** Se llama a la API por HTTP con `requests`, que
   ya viene con Streamlit. Una librería nueva es un riesgo de despliegue, y
   eso ya nos costó una tarde con `pillow`.

No importa Streamlit: se puede probar entero sin levantar la aplicación.
"""

from __future__ import annotations

from typing import Callable

from core import kpis

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

#: Se prueban en orden y se usa el primero que responda. Los nombres de modelo
#: de Google cambian y se retiran; si el primero desaparece, el tutor sigue
#: funcionando con el siguiente en vez de caerse.
MODELOS = ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash"]

TIEMPO_LIMITE = 12  # segundos; en clase, esperar más que esto es peor que nada

#: Longitud máxima de la respuesta. Si el modelo se enrolla, se descarta:
#: queremos una pregunta, no un párrafo.
LARGO_MAXIMO = 320


INSTRUCCION = """\
Eres el tutor de una clase universitaria de logística y sostenibilidad.

Un grupo de alumnos dirige una filial de RetailNova Europa, una empresa
ficticia de grandes almacenes, y está haciendo su diagnóstico a partir de
datos reales de la filial. Cada filial tiene un problema dominante que el
grupo debe descubrir por su cuenta.

TU ÚNICA FUNCIÓN ES DEVOLVER UNA PREGUNTA. Reglas absolutas:

- Responde SIEMPRE con una sola pregunta, y nada más. Sin saludos, sin
  introducción, sin explicación, sin varias preguntas.
- La pregunta debe caber en dos líneas.
- NUNCA digas cuál es el problema de la filial, ni lo insinúes, ni lo
  confirmes si ellos lo aciertan. Si lo han acertado, pregúntales por la
  causa, por el coste o por la evidencia que lo demuestra.
- NUNCA propongas soluciones ni recomiendes medidas.
- NUNCA des datos nuevos que no estén en el contexto.
- Si lo que han escrito está vacío o no dice nada, pregúntales por lo que
  ven en los datos que tienen delante.
- Si lo que han escrito es una afirmación sin números, pregúntales cómo lo
  demostrarían con los datos.
- Si lo que han escrito ya tiene números, pregúntales por la causa: qué
  tendría que ser verdad de su filial para que esos números salgan así.
- Habla de usted en plural (vosotros), en español de España, con tono
  cercano y directo. Nada de tecnicismos innecesarios.
"""

#: Preguntas escritas a mano, una por paso. Se usan cuando no hay asistente
#: disponible, y también como red cuando el modelo devuelve algo inservible.
#: Son socráticas a propósito: señalan dónde mirar, nunca qué concluir.
RESERVA = {
    "paso2": [
        "¿Qué tendría que pasar en vuestra filial para que la curva de ventas "
        "tenga esa forma y no otra?",
        "Si tapáis diciembre con el dedo, ¿qué queda? ¿Y eso qué os dice?",
        "El canal online crece más deprisa que la tienda. ¿En qué categorías, "
        "y por qué justamente en esas?",
    ],
    "paso3": [
        "De todo lo que habéis visto, ¿qué es lo que más dinero os está "
        "costando al año? ¿Sabríais ponerle una cifra?",
        "¿Qué tendría que ser verdad de vuestra red de tiendas para que esos "
        "kilómetros salgan así?",
        "Lo que acabáis de afirmar, ¿en qué pantalla concreta se ve?",
    ],
    "paso4": [
        "Dividid vuestras toneladas entre los millones que vendéis. ¿Cambia "
        "eso quién sale peor?",
        "¿Qué fuente de emisiones os ha sorprendido más, y por qué esperabais "
        "otra cosa?",
        "Hay una fuente que no aparece en ninguna factura. ¿Cuál es y de dónde "
        "sale?",
    ],
    "diagnostico": [
        "Eso que describís, ¿es la causa o es un síntoma de algo anterior?",
        "Si tuvierais que resumirlo en una sola frase para el Consejo, "
        "¿cuál sería?",
        "¿Por qué le pasa a vuestra filial y no le pasa a las otras cuatro?",
    ],
    "evidencia": [
        "De esos datos, ¿cuántos habéis comparado con otra filial?",
        "Si alguien os dijera que ese dato está mal medido, ¿cómo lo "
        "comprobaríais?",
        "¿Vienen todos de la misma tabla, o de sitios distintos?",
    ],
    "coste": [
        "¿Qué cuenta habéis hecho para llegar a esa cifra, aunque sea "
        "aproximada?",
        "¿Ese coste es dinero que se pierde cada año, o una sola vez?",
        "¿Cuánto de ese coste creéis que se podría llegar a evitar?",
    ],
    "s2_alcance3_reaccion": [
        "Vuestro plan reduce sobre la parte pequeña del inventario. ¿Eso lo "
        "invalida, o sigue habiendo una razón para hacerlo primero?",
        "Si tuvierais que elegir entre una tonelada de alcance 1 y una de "
        "alcance 3, ¿valen lo mismo? ¿Para quién?",
        "¿Qué le diríais a un accionista que os acusara de haber medido solo "
        "lo que os convenía?",
    ],
    "s2_alcance3_limite": [
        "De lo que habéis señalado, ¿qué parte podríais cambiar vosotros "
        "solos y qué parte necesita que otro acepte cambiar?",
        "¿Qué tendría que ganar ese proveedor para querer moverse?",
        "Si el proveedor os dice que no, ¿qué os queda?",
    ],
    "s3_escalon": [
        "La palanca más barata que tenéis, ¿en qué escalón de la jerarquía "
        "está? ¿Y por qué creéis que es la más barata?",
        "Si solo hicierais lo más barato, ¿hasta dónde llegaríais?",
        "¿Qué tiene que pasar para que una tonelada reciclada valga menos que "
        "una tonelada que nunca se generó?",
    ],
    "s3_prevencion": [
        "De vuestro plan, ¿qué parte deja de generar residuo y qué parte solo "
        "lo coloca en otro contenedor?",
        "Si el año que viene os piden otro tercio, ¿desde dónde partiríais "
        "con el plan que acabáis de hacer?",
        "¿Hay algo en vuestro plan que además os ahorre dinero desde el "
        "primer día?",
    ],
    "s3_euros": [
        "Habéis ordenado por toneladas. Si ordenaseis por euros ahorrados, "
        "¿cambiaría el primer puesto?",
        "¿Qué medida defenderíais aunque no recuperase ni una tonelada?",
        "El Consejo os pregunta cuándo se recupera la inversión. ¿Qué "
        "contestáis?",
    ],
    "propuesta": [
        "Vuestra propuesta, ¿ataca la causa que habéis identificado o ataca "
        "otro problema distinto?",
        "¿Qué tendríais que dejar de hacer para poder hacer eso?",
        "Si solo pudierais hacer una cosa el año que viene, ¿sería esta?",
    ],
}

#: Qué cifras se le enseñan al tutor en cada paso. Deliberadamente son las
#: mismas que el alumno tiene delante: el tutor no sabe más que ellos.
def contexto(grupo: str, paso: str) -> str:
    """Las cifras de la filial que el tutor puede ver.

    Nunca incluye el diagnóstico ni el punto débil de la filial. Si se lo
    diéramos, acabaría filtrándolo por mucho que se lo prohibamos.
    """
    try:
        r = kpis.retrato(grupo)
        lineas = [
            f"Filial: {r['nombre']} ({r['ciudad']}).",
            f"Ventas anuales: {r['ventas_eur'] / 1e6:.0f} M€.",
            f"Puntos de venta: {r['puntos_de_venta']}.",
        ]
        if paso == "paso2":
            c = kpis.canal(grupo)
            cre = kpis.crecimiento(grupo)
            lineas += [
                f"Cuota del canal online: {c['cuota_online'] * 100:.1f} %.",
                f"Crecimiento interanual: {cre['variacion'] * 100:.1f} %.",
                f"Recogida en tienda: {c['pct_recogida_en_tienda'] * 100:.0f} %.",
            ]
        elif paso == "paso3":
            log = kpis.logistica(grupo)
            cad = kpis.cadena_suministro(grupo)
            inv = kpis.inventario_resumen(grupo)
            lineas += [
                f"Kilómetros en vacío: {log['pct_km_en_vacio'] * 100:.1f} %.",
                f"Entregas fallidas: {log['pct_entregas_fallidas'] * 100:.1f} %.",
                f"Plazo medio de proveedor: {cad['plazo_medio_dias']:.0f} días.",
                f"Compra en Asia: {cad['pct_compra_asiatica'] * 100:.0f} %.",
                f"Cobertura de stock: {inv['dias_cobertura']:.0f} días.",
                f"Merma: {inv['pct_merma'] * 100:.2f} %.",
            ]
        elif paso == "paso4":
            ene = kpis.energia_resumen(grupo)
            hue = kpis.huella(grupo)
            lineas.append(
                f"Energía por millón vendido: "
                f"{ene['intensidad_mwh_por_meur']:.0f} MWh."
            )
            lineas.append(f"Huella total: {hue['co2e_t'].sum():.0f} t CO2e.")
            for fila in hue.itertuples():
                lineas.append(f"  {fila.fuente}: {fila.pct * 100:.0f} % de la huella.")
        else:
            pos = kpis.posicion(grupo)
            lineas.append("Puesto de la filial en cada indicador (1 es el mejor):")
            for fila in pos.itertuples():
                lineas.append(f"  {fila.indicador}: {fila.puesto} de 5.")
        return "\n".join(lineas)
    except Exception:
        # Sin contexto el tutor sigue pudiendo preguntar por lo escrito.
        return "No hay cifras disponibles de esta filial."


def hay_clave(secretos) -> bool:
    """¿Está configurada la clave de Google?

    Acepta cualquier cosa que se comporte como un diccionario, para poder
    probarlo sin Streamlit.
    """
    try:
        clave = secretos["gemini"]["api_key"]
    except Exception:
        # Cualquier fallo aquí significa "no hay clave". En Streamlit Cloud
        # leer secretos mal configurados puede lanzar errores propios suyos.
        return False
    return bool(str(clave).strip())


def _extraer_texto(datos: dict) -> str:
    """Saca el texto de la respuesta, sin casarse con una forma concreta.

    La API ha cambiado de formato más de una vez. En lugar de indexar una
    ruta fija, se recorre la respuesta buscando textos: así un cambio de
    esquema no rompe la clase.
    """
    encontrados: list[str] = []

    def recorrer(nodo):
        if isinstance(nodo, dict):
            texto = nodo.get("text")
            if isinstance(texto, str) and texto.strip():
                encontrados.append(texto)
            for clave, valor in nodo.items():
                if clave != "text":
                    recorrer(valor)
        elif isinstance(nodo, list):
            for elemento in nodo:
                recorrer(elemento)

    recorrer(datos)
    return "\n".join(encontrados).strip()


def _es_una_pregunta_valida(texto: str) -> bool:
    """Filtro de última línea antes de enseñárselo a un alumno.

    Si el modelo se enrolla, da la respuesta en vez de preguntar, o devuelve
    un párrafo, se descarta y se usa la pregunta de reserva. Más vale una
    pregunta escrita a mano que una respuesta regalada.
    """
    limpio = texto.strip()
    if not limpio or len(limpio) > LARGO_MAXIMO:
        return False
    if "?" not in limpio:
        return False
    # Una sola pregunta: si trae varias, es que se ha puesto a explicar.
    if limpio.count("?") > 2:
        return False
    return True


def _llamar(clave: str, instruccion: str, entrada: str,
            transporte: Callable | None = None) -> str:
    """Una llamada a la API, probando los modelos en orden.

    `transporte` existe para poder probar esto sin red ni clave real.
    """
    if transporte is None:
        import requests  # viene con Streamlit; no es dependencia nueva

        def transporte(url, cabeceras, cuerpo, tiempo):
            respuesta = requests.post(
                url, headers=cabeceras, json=cuerpo, timeout=tiempo
            )
            respuesta.raise_for_status()
            return respuesta.json()

    cabeceras = {"x-goog-api-key": clave, "Content-Type": "application/json"}
    ultimo_error: Exception | None = None

    for modelo in MODELOS:
        cuerpo = {
            "model": modelo,
            "system_instruction": instruccion,
            "input": entrada,
            "store": False,
            "generation_config": {"temperature": 0.9, "thinking_level": "low"},
        }
        try:
            datos = transporte(URL, cabeceras, cuerpo, TIEMPO_LIMITE)
            texto = _extraer_texto(datos)
            if texto:
                return texto
        except Exception as error:  # modelo retirado, cuota, red, lo que sea
            ultimo_error = error
            continue

    if ultimo_error is not None:
        raise ultimo_error
    return ""


def pregunta_de_reserva(paso: str, semilla: int = 0) -> str:
    """Pregunta escrita a mano. Siempre disponible, sin clave ni conexión."""
    opciones = RESERVA.get(paso) or RESERVA["diagnostico"]
    return opciones[semilla % len(opciones)]


def preguntar(grupo: str, paso: str, escrito: str, secretos=None,
              transporte: Callable | None = None,
              semilla: int = 0) -> tuple[str, bool]:
    """Devuelve (pregunta, la_ha_generado_el_tutor).

    Nunca lanza excepción y nunca devuelve cadena vacía: si algo falla, sale
    una pregunta de reserva. El segundo valor sirve para que la interfaz
    pueda decir la verdad sobre de dónde viene lo que se está leyendo.
    """
    if secretos is None or not hay_clave(secretos):
        return pregunta_de_reserva(paso, semilla), False

    entrada = (
        f"Contexto de la filial (no se lo reveles, es solo para orientarte):\n"
        f"{contexto(grupo, paso)}\n\n"
        f"Esto es lo que ha escrito el grupo:\n"
        f"\"\"\"{escrito.strip() or '(no han escrito nada todavía)'}\"\"\"\n\n"
        f"Devuelve UNA pregunta que les haga avanzar."
    )

    try:
        texto = _llamar(
            str(secretos["gemini"]["api_key"]).strip(),
            INSTRUCCION, entrada, transporte,
        )
    except Exception:
        return pregunta_de_reserva(paso, semilla), False

    if not _es_una_pregunta_valida(texto):
        return pregunta_de_reserva(paso, semilla), False

    return texto.strip(), True
