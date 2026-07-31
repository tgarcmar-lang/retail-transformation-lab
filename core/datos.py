"""Carga de los datos de RetailNova.

Es la única puerta de entrada a los CSV. Nadie más debería leerlos
directamente: si mañana los datos vienen de una base de datos en vez de
ficheros, solo hay que cambiar este módulo.

No importa Streamlit a propósito, para poder probarlo sin levantar la
aplicación. El cacheado se aplica desde fuera, en la capa de interfaz.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_CSV = RAIZ / "datos" / "retailnova" / "csv"

#: Columnas que hay que interpretar como fechas al leer cada tabla.
COLUMNAS_FECHA = {
    "ventas_diarias": ["fecha"],
    "ventas_categoria": ["mes"],
    "pedidos_online": ["fecha"],
    "rutas": ["fecha"],
    "consumo_flota": ["mes"],
    "energia": ["mes"],
    "inventario": ["mes"],
    "residuos": ["mes"],
    "compras": ["mes"],
    "devoluciones": ["mes"],
    "envases": ["mes"],
}

TABLAS = [
    "tiendas", "centros", "flota", "proveedores", "compras",
    "ventas_diarias", "ventas_categoria", "pedidos_online",
    "rutas", "consumo_flota", "energia", "inventario",
    "residuos", "refrigerantes", "devoluciones", "envases",
    "factores_emision",
]


class DatosNoEncontrados(FileNotFoundError):
    """Los CSV no están donde deberían.

    Se lanza con un mensaje en español porque puede acabar viéndolo un
    alumno en clase, y "FileNotFoundError" no le dice nada.
    """


@lru_cache(maxsize=None)
def cargar(tabla: str) -> pd.DataFrame:
    """Lee una tabla completa, con las cinco filiales.

    El resultado se cachea: leer `ventas_diarias.csv` cuesta casi un segundo
    y no tiene sentido repetirlo en cada interacción del alumno.
    """
    if tabla not in TABLAS:
        raise ValueError(f"Tabla desconocida: {tabla!r}. Disponibles: {TABLAS}")

    ruta = CARPETA_CSV / f"{tabla}.csv"
    if not ruta.exists():
        raise DatosNoEncontrados(
            f"No encuentro los datos de RetailNova ({tabla}.csv). "
            "Genera los datos con: python -m datos.retailnova.generador"
        )

    return pd.read_csv(ruta, parse_dates=COLUMNAS_FECHA.get(tabla))


def de_la_filial(tabla: str, grupo: str) -> pd.DataFrame:
    """La misma tabla, filtrada por la filial que dirige un grupo."""
    datos = cargar(tabla)
    if "grupo" not in datos.columns:
        return datos
    return datos[datos["grupo"] == grupo].copy()


def anios_disponibles() -> list[int]:
    """Años que cubren los datos."""
    return sorted(cargar("ventas_diarias")["fecha"].dt.year.unique().tolist())


def ultimo_anio() -> int:
    """El año más reciente. Es el que se usa para todos los KPI."""
    return anios_disponibles()[-1]


def hay_datos() -> bool:
    """¿Están los CSV en su sitio?"""
    return (CARPETA_CSV / "ventas_diarias.csv").exists()


def limpiar_cache() -> None:
    """Olvida lo cargado. Útil en pruebas y tras regenerar los datos."""
    cargar.cache_clear()
