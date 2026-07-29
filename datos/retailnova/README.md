# Datos de RetailNova Europa

## Cómo funciona esto

```
magnitudes.md    ← las cifras del caso, validadas. Documento de referencia.
parametros.py    ← las mismas cifras, en código. Única fuente de verdad.
generador.py     ← construye los CSV a partir de los parámetros.
csv/             ← los datos que consume la aplicación. Se versionan en Git.
```

Para regenerar los datos, desde la raíz del repositorio:

```
python -m datos.retailnova.generador
```

Para comprobar que siguen cuadrando:

```
python -m pytest tests/ -q
```

**Regla importante:** los CSV no se editan a mano nunca. Si hay que cambiar una
cifra del caso, se cambia en `parametros.py` y se vuelve a generar. Un CSV
retocado a mano deja de ser reproducible y rompe las pruebas.

La semilla es fija, así que la generación es determinista: un alumno que analice
los datos en septiembre y otro que los analice en octubre ven exactamente la
misma empresa.

## Qué contiene cada fichero

### Maestros

| Fichero | Una fila por | Para qué sirve |
|---|---|---|
| `tiendas.csv` | Punto de venta (134) | Formato, superficie, emplazamiento, año de apertura |
| `centros.csv` | Centro logístico (9) | Superficie, muelles, tiendas servidas |
| `flota.csv` | Vehículo (451) | Tipo, antigüedad, norma Euro, consumo nominal |
| `proveedores.csv` | Proveedor (120) | País, plazo de entrega, fiabilidad |
| `factores_emision.csv` | Factor (6) | Conversión a CO₂ equivalente, por alcance |

### Ventas

| Fichero | Una fila por | Notas |
|---|---|---|
| `ventas_diarias.csv` | Tienda y día | **Solo venta física.** Ventas, tickets, ticket medio |
| `ventas_categoria.csv` | Tienda, categoría y mes | Reparto mensual de la venta física |
| `pedidos_online.csv` | Filial y día | El canal online no se atribuye a ninguna tienda |

Las ventas totales de una filial son la suma de las dos fuentes: tienda física
más online. Es un punto que conviene explicar en clase, porque el alumno que
solo mire `ventas_diarias.csv` se dejará entre el 13 % y el 25 % del negocio
según la filial.

### Operaciones y medio ambiente

| Fichero | Una fila por | Notas |
|---|---|---|
| `rutas.csv` | Centro y día | Kilómetros, kilómetros en vacío, paradas, ocupación |
| `consumo_flota.csv` | Vehículo y mes | Kilómetros, litros, coste y CO₂e |
| `energia.csv` | Instalación y mes | Electricidad y gas natural |
| `inventario.csv` | Tienda, categoría y mes | Stock medio, rotación, cobertura y merma |
| `residuos.csv` | Instalación y mes | Seis tipos de residuo y tasa de reciclaje |
| `refrigerantes.csv` | Tienda y año | Carga, fuga, gas empleado y CO₂e |

## Lo que los datos deben revelar

Cada filial tiene un problema dominante. No está escrito en ningún sitio: hay
que encontrarlo en los datos. Esto es lo que debe salir del análisis.

| Grupo | Filial | Lo que debe descubrir |
|---|---|---|
| A | Madrid | Es la mayor y la más digital, pero su última milla urbana es cara. Su tamaño esconde ineficiencias que en términos relativos no son excepcionales |
| B | Barcelona | Su cadena de suministro es la más larga del grupo: la dependencia asiática dispara los plazos y hunde la fiabilidad de entrega |
| C | Valencia | Emite más CO₂ que Madrid vendiendo un 56 % menos. Dos causas acumuladas: cadena de frío y R-404A en los equipos |
| D | Sevilla | Quema más gasóleo que ninguna otra filial con la segunda flota más pequeña. Un tercio de sus kilómetros son en vacío |
| E | Bilbao | Es la más pequeña y la mejor en casi todo ratio. Su margen de mejora no está en operaciones, sino en crecer |

## Imperfecciones deliberadas

Un dataset perfecto no enseña a nadie a trabajar con datos. Estos huecos están
puestos a propósito y detectarlos forma parte del diagnóstico:

- Alrededor del **1,5 % de las lecturas de contador eléctrico están vacías**
  (`energia.csv`). Quien calcule la media sin darse cuenta obtendrá un consumo
  ligeramente bajo.
- Alrededor del **2 % de los partes de ruta llegan sin kilometraje**
  (`rutas.csv`). Afecta al cálculo de kilómetros en vacío.
- **Seis días atípicos por filial** con ventas hundidas: cortes de suministro,
  olas de calor, huelgas de transporte. No están etiquetados como tales.

## Advertencias para quien mantenga esto

- `parametros.py` y `core/filiales.py` **tienen que contar lo mismo**. Los
  vehículos, los centros logísticos y la cuota de comercio electrónico aparecen
  en los dos sitios, y `tests/test_generador.py` comprueba que coinciden. Si
  cambias uno, cambia el otro.
- La cuota de comercio electrónico **no se fija a mano**: se deriva del mix de
  categorías por su penetración online. Si alguien intenta escribir un 38 % de
  golpe, hay una prueba que lo impide, porque la alimentación online en España
  no pasa del 5 %.
- El volumen total es de unos 9 MB. Streamlit Community Cloud da alrededor de
  1 GB de memoria, así que hay margen, pero conviene leer los CSV con
  `@st.cache_data` y no cargar `ventas_diarias.csv` entero si basta con un
  agregado.
