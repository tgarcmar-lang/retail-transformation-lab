# Hoja de magnitudes de RetailNova Europa

> **Qué es esto.** Los números de partida de las cinco filiales. El generador
> (`generador.py`) no inventa nada: lee esta hoja y construye a partir de ella los
> dos años de datos diarios. Si un número de aquí cambia, cambian todos los datos
> derivados de forma coherente.
>
> **Versión 2** (29 jul 2026), tras la revisión de Tomás. Cambios respecto a la v1
> en la sección 9.

## 0. Qué es RetailNova

Operador de **grandes almacenes polivalentes**, no una cadena de supermercados.
Su núcleo económico es el textil y los bienes duraderos; la alimentación es una
línea importante pero no dominante.

| Categoría | Peso sobre ventas del grupo |
|---|---|
| Moda y Belleza | 40 % |
| Hogar, Electrónica y Electrodomésticos | 36 % |
| Alimentación y Hostelería | 24 % |

Esto tiene una consecuencia estructural: **cada filial explota cuatro formatos de
punto de venta distintos**, y casi todo (energía, refrigerantes, logística) depende
del formato, no de la filial.

| Formato | Superficie típica | Papel |
|---|---|---|
| Gran almacén | 14.000 – 19.000 m² | Buque insignia. Varias plantas, climatización masiva, food hall |
| Hipermercado / Gourmet | 2.500 – 3.000 m² | Alimentación y hostelería. Frío industrial intensivo |
| Tienda especializada | 800 – 900 m² | Moda y belleza en calle o centro comercial |
| Conveniencia | 380 – 400 m² | Proximidad urbana, surtido corto |

## 1. Dimensión de cada filial

### Parque de tiendas

| Formato | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao | Grupo |
|---|---|---|---|---|---|---|
| Grandes almacenes | 3 | 2 | 1 | 1 | 1 | **8** |
| Hipermercado / Gourmet | 5 | 4 | 7 | 4 | 2 | **22** |
| Especializadas | 20 | 14 | 10 | 12 | 7 | **63** |
| Conveniencia | 10 | 8 | 9 | 10 | 4 | **41** |
| **Puntos de venta** | **38** | **28** | **27** | **27** | **14** | **134** |

### Magnitudes principales

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao | **Grupo** |
|---|---|---|---|---|---|---|
| Superficie de venta (m²) | 91.800 | 61.340 | 48.600 | 39.200 | 26.550 | **267.490** |
| Ventas por m² (€/m²·año) | 4.700 | 4.600 | 3.900 | 3.300 | 4.400 | — |
| **Ventas anuales (M€)** | **431** | **282** | **190** | **129** | **117** | **1.149** |
| Plantilla | 2.005 | 1.343 | 974 | 697 | 520 | **5.539** |
| Ventas por empleado (k€) | 215 | 210 | 195 | 185 | 225 | 207 |
| Centros logísticos | 3 | 2 | 2 | 1 | 1 | **9** |
| Superficie por centro (m²) | 8.000 | 9.000 | 7.000 | 6.500 | 5.500 | — |
| Puntos de venta por centro | 13 | 14 | 14 | 27 | 14 | — |

Lecturas intencionadas: Madrid es el buque insignia con tres grandes almacenes.
Valencia está sobreponderada en alimentación (7 hipermercados sobre 27 puntos de
venta). Sevilla sirve 27 puntos de venta desde un único centro, el doble de carga
que cualquier otra filial. Bilbao es la más pequeña pero la mejor en ventas por
empleado.

## 2. Mix de categorías y comercio electrónico

El porcentaje de comercio electrónico **no se fija a mano: se deriva**. Cada filial
tiene su mix de categorías, y cada categoría su penetración online. La cuota de la
filial es la media ponderada. Así es imposible que salga un número inverosímil.

### Mix de categorías por filial (% de ventas)

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| Moda y Belleza | 45 | 42 | 30 | 38 | 40 |
| Hogar y Electrónica | 35 | 36 | 25 | 34 | 36 |
| Alimentación y Hostelería | 20 | 22 | 45 | 28 | 24 |

### Penetración del canal online por categoría (%)

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| Moda y Belleza | 28 | 26 | 22 | 16 | 24 |
| Hogar y Electrónica | 33 | 30 | 26 | 19 | 29 |
| **Alimentación y Hostelería** | **5,0** | **4,5** | **4,0** | **3,0** | **4,0** |

La alimentación se mantiene siempre en la horquilla real del mercado español
(3-5 %). Los porcentajes altos quedan reservados a moda y electrónica, y solo
Madrid y Barcelona llegan a los niveles de los grandes operadores digitales.

### Resultado: cuota de comercio electrónico sobre el total

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| **Cuota online (%)** | **25,2** | **22,7** | **14,9** | **13,4** | **21,0** |
| Ventas online (M€) | 109 | 64 | 28 | 17 | 25 |
| Valor anterior (v1) | 38 | 31 | 19 | 14 | 27 |

El orden entre filiales se mantiene; bajan los niveles. **`core/filiales.py` queda
actualizado con estos valores**, para que la ficha que ve el alumno coincida con los
datos que analiza.

## 3. Flota y combustible

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| Furgonetas (última milla) | 100 | 58 | 46 | 28 | 32 |
| Rígidos (reparto a tienda) | 40 | 37 | 42 | 48 | 20 |
| **Total vehículos** | 140 | 95 | 88 | 76 | 52 |
| km/año por furgoneta | 26.000 | 26.000 | 26.000 | 32.000 | 24.000 |
| km/año por rígido | 48.000 | 48.000 | 48.000 | 55.000 | 45.000 |
| Consumo furgoneta (L/100 km) | 9,5 | 9,5 | 9,5 | 10,5 | 9,2 |
| Consumo rígido (L/100 km) | 27,0 | 27,0 | 31,8 ¹ | 30,0 | 26,0 |
| **Gasóleo anual (litros)** | 765.400 | 622.800 | 754.700 | **886.100** | 304.700 |
| Kilómetros en vacío (%) | 18 | 21 | 23 | **34** | 14 |
| Antigüedad media (años) | 5,2 | 4,1 | 6,8 | **8,4** | 3,3 |

¹ Valencia lleva rígidos frigoríficos: +18 % de consumo por el equipo de frío.

**Sevilla es la que más gasóleo quema del grupo, con la segunda flota más pequeña.**
Validado como hallazgo de auditoría, no como error. La causa está repartida en tres
factores que el generador deja rastreables por separado, para que el grupo D pueda
atribuir el sobreconsumo a cada uno:

- **Rutas radiales largas** a provincias periféricas desde un único centro, frente
  al reparto urbano denso y concentrado de Madrid.
- **Flota de 8,4 años**, con pérdida de eficiencia de combustión.
- **34 % de kilómetros en vacío** — el talón de Aquiles. Un tercio de la flota
  circulando sin carga. Es la palanca de mejora más rentable de todo el caso.

El reparto de flota lo refleja: Sevilla es la única filial con más rígidos que
furgonetas (48 frente a 28), coherente con rutas largas entre tiendas y poca
última milla.

## 4. Energía en instalaciones

Los consumos se fijan **por formato**, no por filial. Un gran almacén de varias
plantas, con climatización masiva, iluminación comercial, ascensores, escaleras
mecánicas y frío del food hall, consume en el rango de los millones de kWh anuales.

### Intensidad energética por formato (kWh/m²·año)

| Formato | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| Gran almacén | 260 | 260 | 260 | 290 ² | 205 ³ |
| Hipermercado / Gourmet | 550 | 550 | 660 ⁴ | 580 ² | 440 ³ |
| Especializada | 200 | 200 | 200 | 215 ² | 160 ³ |
| Conveniencia | 350 | 350 | 420 ⁴ | 370 ² | 280 ³ |
| Centro logístico | 230 | 230 | 400 ⁴ | 230 | 200 ³ |

² Sevilla: sobrecoste de climatización por clima cálido. ³ Bilbao: instalaciones
recientes y eficientes. ⁴ Valencia: cadena de frío intensiva.

### Consumo por edificio (kWh/año)

| Formato | Rango en el grupo |
|---|---|
| Gran almacén | 2.870.000 – 4.940.000 |
| Hipermercado / Gourmet | 1.100.000 – 1.980.000 |
| Especializada | 136.000 – 172.000 |
| Conveniencia | 112.000 – 168.000 |

Los grandes almacenes caen dentro del rango de 2 a 6 millones de kWh que marcaste.

### Totales

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| **Electricidad (GWh/año)** | 32,8 | 22,7 | 26,7 | 15,6 | 7,6 |
| Intensidad (MWh por M€ vendido) | 76 | 80 | **141** | **121** | **65** |

Este último ratio es el resultado más pedagógico de la sección: Bilbao produce un
euro de venta con menos de la mitad de energía que Valencia. Los dos extremos tienen
explicación distinta —Valencia por su peso en frío alimentario, Sevilla por
climatización y baja productividad por m²— y esa distinción es justo lo que deben
descubrir los grupos.

## 5. Refrigerantes (palanca clave de la Sesión 2)

### Carga instalada por formato (kg)

| Formato | Carga media |
|---|---|
| Gran almacén | 850 |
| Hipermercado / Gourmet | 420 |
| Especializada | 45 |
| Conveniencia | 90 |

### Por filial

| | A · Madrid | B · Barcelona | C · Valencia | D · Sevilla | E · Bilbao |
|---|---|---|---|---|---|
| Carga total (kg) | 6.450 | 4.730 | 5.050 | 3.970 | 2.365 |
| Fuga anual (%) | 12 | 11 | 15 | 14 | 8 |
| Gas dominante | R-449A | R-449A | **R-404A** | **R-404A** | R-744 (CO₂) |
| **Emisiones por fuga (t CO₂e)** | 1.081 | 727 | **2.972** | **2.180** | **0,2** |

Valencia emite por fugas de refrigerante casi tres veces lo que Madrid, teniendo
menos carga instalada: la diferencia es el gas. Bilbao, ya migrada a CO₂, emite
prácticamente cero. Es la comparación más contundente de todo el caso y convierte
la sustitución de refrigerante en una decisión evidente de la Sesión 2.

## 6. Factores de emisión (comunes a las cinco filiales)

| Concepto | Factor | Alcance |
|---|---|---|
| Gasóleo | 2,68 kg CO₂e / litro | 1 |
| Gas natural | 0,182 kg CO₂e / kWh | 1 |
| R-404A | 3.922 kg CO₂e / kg | 1 |
| R-449A | 1.397 kg CO₂e / kg | 1 |
| R-744 (CO₂) | 1 kg CO₂e / kg | 1 |
| Electricidad (mix español) | 0,17 kg CO₂e / kWh | 2 |

## 7. Estacionalidad y patrones

- **Semanal:** viernes y sábado por encima de la media; domingo muy bajo salvo en
  los grandes almacenes con apertura autorizada.
- **Anual:** pico en diciembre (+35 %), valle en enero y febrero (−15 %).
- **Campañas propias de este negocio:** rebajas de enero y julio, Black Friday,
  vuelta al cole, campaña de Navidad. Moda con dos temporadas marcadas
  (primavera-verano y otoño-invierno); electrónica concentrada en el último
  trimestre; alimentación mucho más plana todo el año.
- **Diferencias territoriales:** verano fuerte en Valencia y Sevilla, plano en
  Bilbao.
- **Ruido:** variación diaria aleatoria y algún día atípico (corte de suministro,
  ola de calor, huelga de transporte).
- **Datos imperfectos a propósito:** una pequeña proporción de lecturas de contador
  ausentes y algún albarán sin kilometraje. Detectarlo forma parte del diagnóstico.

## 8. Tablas que producirá el generador

| Fichero | Contenido | Filas aprox. |
|---|---|---|
| `tiendas.csv` | Maestro: código, filial, formato, ciudad, m², apertura | 134 |
| `centros.csv` | Maestro de centros logísticos | 9 |
| `flota.csv` | Maestro de vehículos: tipo, año, norma Euro | 451 |
| `proveedores.csv` | Maestro de proveedores y plazos de entrega | 120 |
| `ventas_diarias.csv` | Ventas, tickets y canal por tienda y día | 97.800 |
| `ventas_categoria.csv` | Reparto mensual por categoría y canal | 9.650 |
| `pedidos_online.csv` | Pedidos de comercio electrónico por día y filial | 3.650 |
| `rutas.csv` | Rutas diarias por centro: km, paradas, ocupación, vacío | 6.600 |
| `consumo_flota.csv` | Combustible y km por vehículo y mes | 10.300 |
| `energia.csv` | Electricidad y gas por instalación y mes | 3.400 |
| `inventario.csv` | Stock, rotación y merma por tienda, categoría y mes | 9.650 |
| `residuos.csv` | Residuos por instalación y mes, por tipo | 3.400 |
| `refrigerantes.csv` | Recargas de gas refrigerante por tienda y año | 270 |
| `factores_emision.csv` | Tabla de referencia de la sección 6 | 6 |

Volumen estimado por debajo de 10 MB, holgadamente dentro del límite de
Streamlit Cloud.

## 9. Cambios respecto a la versión 1

| Qué | v1 | v2 | Motivo |
|---|---|---|---|
| Naturaleza del negocio | Retail mixto indefinido | Grandes almacenes polivalentes, con mix de categorías explícito | Corrección de Tomás: el núcleo es textil y bienes duraderos |
| Formato de tienda | 276 tiendas de 700-800 m² | 134 puntos de venta en cuatro formatos, de 380 a 19.000 m² | Un gran almacén no es una tienda de barrio |
| Ventas del grupo | 894 M€ | 1.149 M€ | Consecuencia de la superficie real, manteniendo los €/m² validados |
| Comercio electrónico | Fijado a mano (38 % en Madrid) | Derivado del mix de categorías (25 % en Madrid) | La alimentación online en España está en el 3-5 %, no en el 38 % |
| Energía por tienda | 288.000 – 455.000 kWh | 112.000 – 4.940.000 kWh según formato | Infravalorada entre 5 y 10 veces para grandes almacenes |
| Sevilla y el gasóleo | Marcado como duda | Confirmado y reforzado | Validado como hallazgo de auditoría, no como error |
| Ventas por m² | 3.200 – 4.800 €/m² | Sin cambios | Validado |
