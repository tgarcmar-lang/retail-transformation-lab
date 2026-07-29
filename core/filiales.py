"""Definición de las cinco filiales de RetailNova Europa.

Cada grupo de alumnos dirige una filial. Comparten estrategia corporativa y
objetivos ESG, pero parten de situaciones distintas: eso es lo que hace que la
comparación final en clase tenga sentido.

Estos son los rasgos de partida. Los datos operativos detallados (pedidos,
rutas, inventario, consumos) los genera `datos/retailnova/generador.py`.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Filial:
    codigo: str
    grupo: str
    nombre: str
    ciudad: str
    perfil: str
    centros_logisticos: int
    vehiculos: int
    antiguedad_media_flota: float  # años
    pct_ecommerce: float           # proporción de ventas online
    reto_principal: str


FILIALES: dict[str, Filial] = {
    "A": Filial(
        codigo="RN-MAD",
        grupo="A",
        nombre="RetailNova Madrid",
        ciudad="Madrid",
        perfil="La filial más grande: tres grandes almacenes y mucha última milla urbana.",
        centros_logisticos=3,
        vehiculos=140,
        antiguedad_media_flota=5.2,
        pct_ecommerce=0.25,
        reto_principal="Congestión urbana y coste de la última milla",
    ),
    "B": Filial(
        codigo="RN-BCN",
        grupo="B",
        nombre="RetailNova Barcelona",
        ciudad="Barcelona",
        perfil="Fuerte peso de importaciones por puerto. Cadena de suministro larga.",
        centros_logisticos=2,
        vehiculos=95,
        antiguedad_media_flota=4.1,
        pct_ecommerce=0.23,
        reto_principal="Dependencia de proveedores asiáticos y lead times largos",
    ),
    "C": Filial(
        codigo="RN-VLC",
        grupo="C",
        nombre="RetailNova Valencia",
        ciudad="Valencia",
        perfil="Sobreponderada en alimentación. Cadena de frío intensiva en energía.",
        centros_logisticos=2,
        vehiculos=88,
        antiguedad_media_flota=6.8,
        pct_ecommerce=0.15,
        reto_principal="Consumo energético de la cadena de frío y merma de producto",
    ),
    "D": Filial(
        codigo="RN-SEV",
        grupo="D",
        nombre="RetailNova Sevilla",
        ciudad="Sevilla",
        perfil="Red dispersa, rutas largas entre tiendas. Flota envejecida.",
        centros_logisticos=1,
        vehiculos=76,
        antiguedad_media_flota=8.4,
        pct_ecommerce=0.13,
        reto_principal="Flota antigua y kilómetros en vacío muy altos",
    ),
    "E": Filial(
        codigo="RN-BIO",
        grupo="E",
        nombre="RetailNova Bilbao",
        ciudad="Bilbao",
        perfil="La más pequeña, pero la más avanzada en automatización.",
        centros_logisticos=1,
        vehiculos=52,
        antiguedad_media_flota=3.3,
        pct_ecommerce=0.21,
        reto_principal="Almacenes eficientes pero presupuesto de inversión limitado",
    ),
}


def obtener(grupo: str) -> Filial:
    """Devuelve la filial asignada a un grupo ('A' … 'E')."""
    clave = grupo.strip().upper()
    if clave not in FILIALES:
        raise ValueError(f"Grupo desconocido: {grupo!r}. Válidos: {list(FILIALES)}")
    return FILIALES[clave]


def listar() -> list[Filial]:
    """Todas las filiales, ordenadas por grupo."""
    return [FILIALES[g] for g in sorted(FILIALES)]
