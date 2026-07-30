"""Parámetros de partida de RetailNova Europa.

Este fichero es la traducción a código de `magnitudes.md`, validada con el
responsable del proyecto. El generador no inventa ninguna cifra: todo lo que
produce sale de aquí.

Si hay que cambiar un número del caso, se cambia AQUÍ y se vuelve a generar.
Nunca se tocan los CSV a mano: dejarían de ser reproducibles.
"""

from datetime import date

# --------------------------------------------------------------------------
# Periodo cubierto
# --------------------------------------------------------------------------

FECHA_INICIO = date(2024, 1, 1)
FECHA_FIN = date(2025, 12, 31)

#: Semilla fija: dos ejecuciones distintas producen exactamente los mismos datos.
SEMILLA = 20260908

GRUPOS = ["A", "B", "C", "D", "E"]

# --------------------------------------------------------------------------
# Formatos de punto de venta
# --------------------------------------------------------------------------

FORMATOS = ["gran_almacen", "hipermercado", "especializada", "conveniencia"]

NOMBRE_FORMATO = {
    "gran_almacen": "Gran almacén",
    "hipermercado": "Hipermercado / Gourmet",
    "especializada": "Tienda especializada",
    "conveniencia": "Conveniencia",
}

#: Parque de tiendas: (número de centros, superficie media en m²).
PARQUE = {
    "A": {"gran_almacen": (3, 19_000), "hipermercado": (5, 2_800),
          "especializada": (20, 850), "conveniencia": (10, 380)},
    "B": {"gran_almacen": (2, 18_000), "hipermercado": (4, 2_600),
          "especializada": (14, 850), "conveniencia": (8, 380)},
    "C": {"gran_almacen": (1, 16_000), "hipermercado": (7, 3_000),
          "especializada": (10, 800), "conveniencia": (9, 400)},
    "D": {"gran_almacen": (1, 15_000), "hipermercado": (4, 2_700),
          "especializada": (12, 800), "conveniencia": (10, 380)},
    "E": {"gran_almacen": (1, 14_000), "hipermercado": (2, 2_500),
          "especializada": (7, 850), "conveniencia": (4, 400)},
}

#: Centros logísticos: (número, superficie media en m²).
CENTROS_LOGISTICOS = {
    "A": (3, 8_000), "B": (2, 9_000), "C": (2, 7_000),
    "D": (1, 6_500), "E": (1, 5_500),
}

# --------------------------------------------------------------------------
# Ventas
# --------------------------------------------------------------------------

#: Ventas totales (tienda + online) por m² de superficie de venta, en €/año.
#: Es el ratio de control validado. El año de referencia es 2025.
VENTAS_POR_M2 = {"A": 4_700, "B": 4_600, "C": 3_900, "D": 3_300, "E": 4_400}

#: Productividad relativa de cada formato. Una tienda de conveniencia vende
#: muchos más euros por m² que un gran almacén, aunque venda menos en total.
#: El generador renormaliza estos pesos para que el total de la filial cuadre
#: exactamente con VENTAS_POR_M2.
PRODUCTIVIDAD_FORMATO = {
    "gran_almacen": 0.95, "hipermercado": 1.15,
    "especializada": 1.35, "conveniencia": 1.60,
}

#: Ventas anuales por empleado, en miles de euros.
VENTAS_POR_EMPLEADO_KEUR = {"A": 215, "B": 210, "C": 195, "D": 185, "E": 225}

#: Crecimiento de 2024 a 2025. Sevilla casi plana, Bilbao la que más crece.
CRECIMIENTO_ANUAL = {"A": 0.045, "B": 0.038, "C": 0.019, "D": 0.006, "E": 0.051}

#: Ticket medio por formato, en euros.
TICKET_MEDIO = {
    "gran_almacen": 78.0, "hipermercado": 42.0,
    "especializada": 55.0, "conveniencia": 18.0,
}

# --------------------------------------------------------------------------
# Categorías de producto y canal online
# --------------------------------------------------------------------------

CATEGORIAS = ["moda_belleza", "hogar_electronica", "alimentacion_hosteleria"]

NOMBRE_CATEGORIA = {
    "moda_belleza": "Moda y Belleza",
    "hogar_electronica": "Hogar, Electrónica y Electrodomésticos",
    "alimentacion_hosteleria": "Alimentación y Hostelería",
}

#: Peso de cada categoría sobre las ventas de la filial. Suma 1 en cada filial.
MIX_CATEGORIAS = {
    "A": {"moda_belleza": 0.45, "hogar_electronica": 0.35, "alimentacion_hosteleria": 0.20},
    "B": {"moda_belleza": 0.42, "hogar_electronica": 0.36, "alimentacion_hosteleria": 0.22},
    "C": {"moda_belleza": 0.30, "hogar_electronica": 0.25, "alimentacion_hosteleria": 0.45},
    "D": {"moda_belleza": 0.38, "hogar_electronica": 0.34, "alimentacion_hosteleria": 0.28},
    "E": {"moda_belleza": 0.40, "hogar_electronica": 0.36, "alimentacion_hosteleria": 0.24},
}

#: Penetración del canal online dentro de cada categoría.
#: La alimentación se mantiene siempre en la horquilla real del mercado
#: español (3-5 %). Los valores altos quedan para moda y electrónica.
PENETRACION_ONLINE = {
    "A": {"moda_belleza": 0.28, "hogar_electronica": 0.33, "alimentacion_hosteleria": 0.050},
    "B": {"moda_belleza": 0.26, "hogar_electronica": 0.30, "alimentacion_hosteleria": 0.045},
    "C": {"moda_belleza": 0.22, "hogar_electronica": 0.26, "alimentacion_hosteleria": 0.040},
    "D": {"moda_belleza": 0.16, "hogar_electronica": 0.19, "alimentacion_hosteleria": 0.030},
    "E": {"moda_belleza": 0.24, "hogar_electronica": 0.29, "alimentacion_hosteleria": 0.040},
}

#: Reparto de categorías dentro de cada formato. Un gran almacén lo vende todo;
#: una tienda especializada es casi solo moda. Suma 1 en cada formato.
MIX_POR_FORMATO = {
    "gran_almacen": {"moda_belleza": 0.46, "hogar_electronica": 0.38, "alimentacion_hosteleria": 0.16},
    "hipermercado": {"moda_belleza": 0.08, "hogar_electronica": 0.14, "alimentacion_hosteleria": 0.78},
    "especializada": {"moda_belleza": 0.88, "hogar_electronica": 0.10, "alimentacion_hosteleria": 0.02},
    "conveniencia": {"moda_belleza": 0.06, "hogar_electronica": 0.09, "alimentacion_hosteleria": 0.85},
}

# --------------------------------------------------------------------------
# Estacionalidad
# --------------------------------------------------------------------------

#: Índice por día de la semana (lunes = 0). Media 1,00.
FACTOR_SEMANAL = [0.88, 0.86, 0.92, 1.00, 1.28, 1.55, 0.51]

#: Índice mensual (enero = 1). Media 1,00.
FACTOR_MENSUAL = {
    1: 0.85, 2: 0.82, 3: 0.95, 4: 1.00, 5: 0.98, 6: 1.02,
    7: 1.10, 8: 0.92, 9: 1.00, 10: 0.98, 11: 1.03, 12: 1.35,
}

#: Los grandes almacenes abren en domingos autorizados: su caída dominical es
#: mucho menor que la de una tienda de calle.
FACTOR_DOMINGO_GRAN_ALMACEN = 0.80

#: Peso del verano por filial: turismo y calor en Levante y Andalucía,
#: prácticamente plano en el norte. Se aplica a julio y agosto.
FACTOR_VERANO = {"A": 0.93, "B": 1.05, "C": 1.18, "D": 1.14, "E": 1.00}

#: Campañas: (nombre, mes_inicio, día_inicio, mes_fin, día_fin, intensidad).
#: La intensidad multiplica las ventas de las categorías afectadas.
CAMPANAS = [
    ("Rebajas de invierno", (1, 7), (2, 15), 1.22, ["moda_belleza"]),
    ("Vuelta al cole", (9, 1), (9, 15), 1.18, ["hogar_electronica", "moda_belleza"]),
    ("Rebajas de verano", (7, 1), (7, 31), 1.25, ["moda_belleza"]),
    ("Black Friday", (11, 24), (11, 30), 1.85, ["hogar_electronica", "moda_belleza"]),
    ("Campaña de Navidad", (12, 15), (12, 31), 1.30, CATEGORIAS),
]

#: Variación diaria aleatoria (desviación típica relativa).
RUIDO_DIARIO = 0.085

# --------------------------------------------------------------------------
# Flota
# --------------------------------------------------------------------------

TIPOS_VEHICULO = ["furgoneta", "rigido"]

#: (furgonetas, rígidos) por filial. Los totales coinciden con core/filiales.py.
FLOTA = {
    "A": (100, 40), "B": (58, 37), "C": (46, 42), "D": (28, 48), "E": (32, 20),
}

#: Kilómetros anuales por vehículo y tipo.
KM_ANUALES = {
    "A": {"furgoneta": 26_000, "rigido": 48_000},
    "B": {"furgoneta": 26_000, "rigido": 48_000},
    "C": {"furgoneta": 26_000, "rigido": 48_000},
    "D": {"furgoneta": 32_000, "rigido": 55_000},
    "E": {"furgoneta": 24_000, "rigido": 45_000},
}

#: Consumo en litros por cada 100 km. Valencia lleva rígidos frigoríficos
#: (+18 % por el equipo de frío); Sevilla penaliza por flota envejecida.
CONSUMO_L_100KM = {
    "A": {"furgoneta": 9.5, "rigido": 27.0},
    "B": {"furgoneta": 9.5, "rigido": 27.0},
    "C": {"furgoneta": 9.5, "rigido": 31.8},
    "D": {"furgoneta": 10.5, "rigido": 30.0},
    "E": {"furgoneta": 9.2, "rigido": 26.0},
}

#: Porcentaje de kilómetros recorridos sin carga. Es la palanca de mejora
#: más rentable del caso, y la que explica el sobreconsumo de Sevilla.
KM_EN_VACIO = {"A": 0.18, "B": 0.21, "C": 0.23, "D": 0.34, "E": 0.14}

#: Antigüedad media de la flota, en años. Coincide con core/filiales.py.
ANTIGUEDAD_FLOTA = {"A": 5.2, "B": 4.1, "C": 6.8, "D": 8.4, "E": 3.3}

#: Paradas por ruta y ocupación media del vehículo.
PARADAS_POR_RUTA = {"A": 14, "B": 13, "C": 12, "D": 8, "E": 12}
OCUPACION_MEDIA = {"A": 0.78, "B": 0.75, "C": 0.72, "D": 0.61, "E": 0.83}

#: Entregas que fallan al primer intento. Es el coste oculto de la última
#: milla urbana: congestión, imposibilidad de aparcar, portales cerrados y
#: destinatarios ausentes. Cada fallo obliga a repetir el viaje, así que
#: paga dos veces, en euros y en emisiones. Es el problema de Madrid.
TASA_ENTREGA_FALLIDA = {"A": 0.041, "B": 0.034, "C": 0.022, "D": 0.018, "E": 0.012}

# --------------------------------------------------------------------------
# Energía
# --------------------------------------------------------------------------

#: Intensidad eléctrica en kWh por m² y año, por filial y formato.
#: Sevilla penaliza por climatización (clima cálido), Valencia por cadena de
#: frío y Bilbao se beneficia de instalaciones recientes.
INTENSIDAD_ELECTRICA = {
    "A": {"gran_almacen": 260, "hipermercado": 550, "especializada": 200,
          "conveniencia": 350, "centro_logistico": 230},
    "B": {"gran_almacen": 260, "hipermercado": 550, "especializada": 200,
          "conveniencia": 350, "centro_logistico": 230},
    "C": {"gran_almacen": 260, "hipermercado": 660, "especializada": 200,
          "conveniencia": 420, "centro_logistico": 400},
    "D": {"gran_almacen": 290, "hipermercado": 580, "especializada": 215,
          "conveniencia": 370, "centro_logistico": 230},
    "E": {"gran_almacen": 205, "hipermercado": 440, "especializada": 160,
          "conveniencia": 280, "centro_logistico": 200},
}

#: Gas natural en kWh por m² y año (calefacción y hostelería).
#: Solo tienen consumo relevante los grandes almacenes y los hipermercados.
INTENSIDAD_GAS = {
    "gran_almacen": 45, "hipermercado": 28,
    "especializada": 0, "conveniencia": 0, "centro_logistico": 12,
}

#: Estacionalidad del consumo eléctrico: pico de refrigeración en verano y
#: de iluminación y calefacción en invierno.
FACTOR_ELECTRICO_MENSUAL = {
    1: 1.04, 2: 0.98, 3: 0.94, 4: 0.90, 5: 0.94, 6: 1.06,
    7: 1.18, 8: 1.20, 9: 1.04, 10: 0.94, 11: 0.94, 12: 0.84,
}

#: Estacionalidad del gas: al revés, casi todo en invierno.
FACTOR_GAS_MENSUAL = {
    1: 1.85, 2: 1.70, 3: 1.35, 4: 0.95, 5: 0.55, 6: 0.30,
    7: 0.22, 8: 0.22, 9: 0.40, 10: 0.85, 11: 1.35, 12: 1.26,
}

# --------------------------------------------------------------------------
# Refrigerantes
# --------------------------------------------------------------------------

#: Carga instalada de gas refrigerante, en kg por instalación.
CARGA_REFRIGERANTE = {
    "gran_almacen": 850, "hipermercado": 420,
    "especializada": 45, "conveniencia": 90,
}

#: Fuga anual como porcentaje de la carga instalada.
FUGA_REFRIGERANTE = {"A": 0.12, "B": 0.11, "C": 0.15, "D": 0.14, "E": 0.08}

#: Gas dominante en cada filial. Valencia y Sevilla siguen con R-404A, que
#: tiene casi el triple de impacto que el R-449A. Bilbao ya migró a CO₂.
GAS_REFRIGERANTE = {
    "A": "R-449A", "B": "R-449A", "C": "R-404A", "D": "R-404A", "E": "R-744",
}

# --------------------------------------------------------------------------
# Residuos
# --------------------------------------------------------------------------

TIPOS_RESIDUO = ["carton", "plastico", "organico", "raee", "textil", "resto"]

#: Kilos generados al año por cada 1.000 € vendidos, por tipo de residuo.
#: Depende del mix de categorías: la alimentación genera orgánico, la moda
#: textil y la electrónica RAEE.
RESIDUO_POR_KEUR = {
    "moda_belleza": {"carton": 4.2, "plastico": 2.8, "organico": 0.1,
                     "raee": 0.0, "textil": 3.6, "resto": 1.4},
    "hogar_electronica": {"carton": 7.5, "plastico": 4.1, "organico": 0.1,
                          "raee": 5.2, "textil": 0.1, "resto": 1.8},
    "alimentacion_hosteleria": {"carton": 6.1, "plastico": 3.9, "organico": 12.4,
                                "raee": 0.2, "textil": 0.0, "resto": 2.6},
}

#: Porcentaje que se recicla en lugar de acabar en vertedero.
TASA_RECICLAJE = {"A": 0.68, "B": 0.72, "C": 0.61, "D": 0.54, "E": 0.83}

# --------------------------------------------------------------------------
# Inventario
# --------------------------------------------------------------------------

#: Rotaciones de inventario al año, por categoría.
ROTACION_ANUAL = {
    "moda_belleza": 3.4, "hogar_electronica": 4.1, "alimentacion_hosteleria": 18.5,
}

#: Penalización de rotación por filial. Un plazo de entrega largo obliga a
#: mantener más stock: Barcelona rota peor porque compra en Asia. Es la
#: consecuencia económica de su problema, y lo que lo hace visible en el
#: balance además de en la cadena de suministro.
FACTOR_ROTACION = {"A": 1.00, "B": 0.84, "C": 1.06, "D": 1.10, "E": 1.12}

#: Merma como porcentaje de las ventas de la categoría.
MERMA_BASE = {
    "moda_belleza": 0.012, "hogar_electronica": 0.006, "alimentacion_hosteleria": 0.028,
}

#: Penalización de merma por filial. Valencia sufre más por producto fresco.
FACTOR_MERMA = {"A": 1.00, "B": 0.95, "C": 1.45, "D": 1.20, "E": 0.80}

# --------------------------------------------------------------------------
# Proveedores
# --------------------------------------------------------------------------

NUM_PROVEEDORES = 120

#: Plazo de entrega medio en días y fiabilidad, por origen.
#: Barcelona depende mucho más de proveedores asiáticos: cadena larga.
ORIGENES_PROVEEDOR = {
    "España": {"plazo": 6, "fiabilidad": 0.96},
    "Portugal": {"plazo": 9, "fiabilidad": 0.94},
    "Italia": {"plazo": 12, "fiabilidad": 0.93},
    "Turquía": {"plazo": 21, "fiabilidad": 0.88},
    "China": {"plazo": 48, "fiabilidad": 0.79},
    "Bangladés": {"plazo": 55, "fiabilidad": 0.74},
    "Vietnam": {"plazo": 52, "fiabilidad": 0.77},
}

#: Coste relativo de comprar en cada origen. Comprar en Asia sale más barato:
#: es la contrapartida del plazo largo. Sin esto, Barcelona sería solo una
#: filial con un problema, cuando en realidad tiene un dilema — que es mucho
#: más interesante de discutir en clase.
COSTE_RELATIVO_ORIGEN = {
    "España": 1.00, "Portugal": 0.97, "Italia": 1.02, "Turquía": 0.90,
    "China": 0.78, "Bangladés": 0.74, "Vietnam": 0.76,
}

#: Coste de la mercancía sobre ventas, antes de ajustar por origen.
COSTE_MERCANCIA_BASE = 0.63

#: Peso de cada origen en las compras de cada filial.
MIX_ORIGEN = {
    "A": {"España": 0.42, "Portugal": 0.10, "Italia": 0.09, "Turquía": 0.09,
          "China": 0.18, "Bangladés": 0.06, "Vietnam": 0.06},
    "B": {"España": 0.26, "Portugal": 0.07, "Italia": 0.10, "Turquía": 0.11,
          "China": 0.28, "Bangladés": 0.09, "Vietnam": 0.09},
    "C": {"España": 0.58, "Portugal": 0.09, "Italia": 0.07, "Turquía": 0.06,
          "China": 0.12, "Bangladés": 0.04, "Vietnam": 0.04},
    "D": {"España": 0.55, "Portugal": 0.13, "Italia": 0.05, "Turquía": 0.07,
          "China": 0.12, "Bangladés": 0.04, "Vietnam": 0.04},
    "E": {"España": 0.48, "Portugal": 0.08, "Italia": 0.10, "Turquía": 0.08,
          "China": 0.16, "Bangladés": 0.05, "Vietnam": 0.05},
}

# --------------------------------------------------------------------------
# Factores de emisión
# --------------------------------------------------------------------------

FACTORES_EMISION = [
    ("Gasóleo", "kg CO2e/litro", 2.68, 1),
    ("Gas natural", "kg CO2e/kWh", 0.182, 1),
    ("R-404A", "kg CO2e/kg", 3922.0, 1),
    ("R-449A", "kg CO2e/kg", 1397.0, 1),
    ("R-744", "kg CO2e/kg", 1.0, 1),
    ("Electricidad (mix español)", "kg CO2e/kWh", 0.17, 2),
    # Alcance 3. Los tres primeros son factores de gasto: cuánto emite, de
    # media, un euro comprado en esa categoría. Es una estimación gruesa,
    # y decirlo forma parte de la lección.
    ("Compras · Moda y belleza", "kg CO2e/€", 0.62, 3),
    ("Compras · Hogar y electrónica", "kg CO2e/€", 0.48, 3),
    ("Compras · Alimentación y hostelería", "kg CO2e/€", 0.88, 3),
    ("Transporte por carretera", "kg CO2e/t·km", 0.105, 3),
    ("Transporte marítimo", "kg CO2e/t·km", 0.016, 3),
    ("Transporte aéreo", "kg CO2e/t·km", 0.602, 3),
    ("Residuo a vertedero", "kg CO2e/kg", 0.45, 3),
    ("Residuo reciclado", "kg CO2e/kg", 0.021, 3),
]

FACTOR_GASOLEO = 2.68
FACTOR_GAS_NATURAL = 0.182
FACTOR_ELECTRICIDAD = 0.17
GWP = {"R-404A": 3922.0, "R-449A": 1397.0, "R-744": 1.0}

# --------------------------------------------------------------------------
# Alcance 3
# --------------------------------------------------------------------------
# El inventario de alcances 1 y 2 de RetailNova ronda las 35.000 t. El de
# alcance 3 es un orden de magnitud mayor, y eso no es un defecto del caso:
# es lo que le pasa a cualquier minorista. Un distribuidor casi no fabrica
# nada, así que casi todo lo que emite lo emite otro por encargo suyo.
#
# El método es **estimación por gasto**: se multiplica lo comprado por un
# factor medio de la categoría. Es el método que usan las empresas cuando
# empiezan, y tiene un defecto que conviene que el alumno vea: si negocias
# un descuento con el proveedor, tu huella baja sin que cambie nada físico.

#: Emisiones por euro comprado, según lo que se compra.
FACTOR_GASTO_CATEGORIA = {
    "moda_belleza": 0.62,
    "hogar_electronica": 0.48,
    "alimentacion_hosteleria": 0.88,
}

#: Multiplicador por país de fabricación. Recoge lo intensivo que es el mix
#: eléctrico del país y su proceso industrial. Comprar en Asia no solo tarda
#: más y sale más barato: también emite más por euro fabricado. Es la pieza
#: que convierte el dilema de Barcelona en un problema de carbono y no solo
#: de margen y plazo.
INTENSIDAD_ORIGEN = {
    "España": 1.00, "Portugal": 0.98, "Italia": 0.96, "Turquía": 1.18,
    "China": 1.45, "Bangladés": 1.38, "Vietnam": 1.34,
}

#: Distancia media desde el origen hasta el centro logístico, en kilómetros.
DISTANCIA_ORIGEN_KM = {
    "España": 450, "Portugal": 900, "Italia": 1_800, "Turquía": 3_400,
    "China": 19_000, "Bangladés": 16_500, "Vietnam": 18_000,
}

#: Cómo viaja hoy la mercancía de cada origen. El porcentaje aéreo es
#: pequeño en volumen y enorme en emisiones: volar una tonelada emite unas
#: cuarenta veces más que llevarla en barco.
MIX_MODAL = {
    "España": {"carretera": 1.00},
    "Portugal": {"carretera": 1.00},
    "Italia": {"carretera": 0.85, "maritimo": 0.15},
    "Turquía": {"carretera": 0.55, "maritimo": 0.45},
    "China": {"maritimo": 0.88, "aereo": 0.12},
    "Bangladés": {"maritimo": 0.85, "aereo": 0.15},
    "Vietnam": {"maritimo": 0.86, "aereo": 0.14},
}

#: Emisiones por tonelada transportada y kilómetro recorrido.
FACTOR_MODO = {"carretera": 0.105, "maritimo": 0.016, "aereo": 0.602}

#: Densidad de valor: cuántos euros de compra pesan una tonelada. Hace falta
#: porque las compras están en euros y el transporte se mide en toneladas.
#: Un contenedor de camisetas vale mucho y pesa poco; uno de conservas, al
#: revés.
VALOR_POR_TONELADA = {
    "moda_belleza": 14_000.0,
    "hogar_electronica": 9_000.0,
    "alimentacion_hosteleria": 2_400.0,
}

#: Tratamiento de residuos.
FACTOR_RESIDUO_VERTEDERO = 0.45
FACTOR_RESIDUO_RECICLADO = 0.021

# --------------------------------------------------------------------------
# Imperfecciones deliberadas
# --------------------------------------------------------------------------
# Un dataset perfecto no enseña nada. Detectar y tratar estos huecos forma
# parte del diagnóstico de la Sesión 1.

#: Proporción de lecturas de contador que faltan.
PCT_LECTURAS_AUSENTES = 0.015

#: Proporción de rutas registradas sin kilometraje.
PCT_RUTAS_SIN_KM = 0.02

#: Días atípicos por filial: cortes de suministro, olas de calor, huelgas.
NUM_DIAS_ATIPICOS = 6


# --------------------------------------------------------------------------
# Funciones derivadas
# --------------------------------------------------------------------------

def superficie_venta(grupo: str) -> int:
    """Superficie total de venta de una filial, en m²."""
    return sum(n * m2 for n, m2 in PARQUE[grupo].values())


def puntos_de_venta(grupo: str) -> int:
    """Número de puntos de venta de una filial."""
    return sum(n for n, _ in PARQUE[grupo].values())


def ventas_anuales(grupo: str) -> float:
    """Ventas totales de 2025 (tienda más online), en euros."""
    return superficie_venta(grupo) * VENTAS_POR_M2[grupo]


def cuota_online(grupo: str) -> float:
    """Cuota del canal online sobre el total.

    No es un dato fijado a mano: es la media del peso de cada categoría por
    su penetración online. Así resulta imposible que salga un porcentaje
    inverosímil, como un 38 % de alimentación comprada por internet.
    """
    return sum(
        MIX_CATEGORIAS[grupo][cat] * PENETRACION_ONLINE[grupo][cat]
        for cat in CATEGORIAS
    )


def coste_mercancia(grupo: str) -> float:
    """Coste de la mercancía sobre ventas.

    Depende de dónde compra la filial. Barcelona, que es la que más compra en
    Asia, es también la que compra más barato: paga ese ahorro con plazos de
    entrega el doble de largos y con el stock inmovilizado que eso obliga a
    mantener. Ese intercambio es la discusión que debe tener el grupo B.
    """
    indice = sum(
        MIX_ORIGEN[grupo][origen] * COSTE_RELATIVO_ORIGEN[origen]
        for origen in MIX_ORIGEN[grupo]
    )
    return COSTE_MERCANCIA_BASE * indice


def plantilla(grupo: str) -> int:
    """Número de empleados de la filial."""
    return round(ventas_anuales(grupo) / (VENTAS_POR_EMPLEADO_KEUR[grupo] * 1_000))


def gasoleo_anual(grupo: str) -> float:
    """Litros de gasóleo consumidos al año por la flota de la filial."""
    furgonetas, rigidos = FLOTA[grupo]
    total = 0.0
    for tipo, n in (("furgoneta", furgonetas), ("rigido", rigidos)):
        total += n * KM_ANUALES[grupo][tipo] * CONSUMO_L_100KM[grupo][tipo] / 100
    return total


def factor_productividad(grupo: str) -> dict[str, float]:
    """Euros por m² de cada formato dentro de una filial.

    Reparte la productividad entre formatos respetando sus pesos relativos,
    pero renormalizando para que el total de la filial cuadre exactamente con
    VENTAS_POR_M2. Sin esta renormalización, cambiar el parque de tiendas
    movería silenciosamente las ventas de la filial.
    """
    m2_total = superficie_venta(grupo)
    ponderado = sum(
        n * m2 * PRODUCTIVIDAD_FORMATO[f] for f, (n, m2) in PARQUE[grupo].items()
    )
    k = m2_total / ponderado
    return {
        f: VENTAS_POR_M2[grupo] * PRODUCTIVIDAD_FORMATO[f] * k for f in FORMATOS
    }
