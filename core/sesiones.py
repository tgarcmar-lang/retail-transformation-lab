"""Catálogo de sesiones y control de qué está disponible.

Cada sesión de clase desbloquea un módulo. Las sesiones futuras aparecen en la
interfaz como "próximamente": el alumno ve el recorrido completo del curso desde
el primer día, aunque solo pueda entrar en lo desbloqueado.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sesion:
    numero: int
    titulo: str
    objetivo: str
    disponible: bool


SESIONES: list[Sesion] = [
    Sesion(
        numero=1,
        titulo="Diagnóstico",
        objetivo="Conocer tu filial: qué vende, cómo opera, dónde están sus problemas.",
        disponible=True,
    ),
    Sesion(
        numero=2,
        titulo="Descarbonización",
        objetivo="Medir la huella de carbono y reducirla un 25 %.",
        disponible=True,
    ),
    Sesion(
        numero=3,
        titulo="Economía circular",
        objetivo="Recuperar el material que hoy se pierde: envases, merma y "
                 "devoluciones.",
        disponible=True,
    ),
    Sesion(
        numero=4,
        titulo="Reporting ESG",
        objetivo="Medir, publicar y defender la memoria de sostenibilidad.",
        disponible=True,
    ),
    Sesion(
        numero=5,
        titulo="Ejecución del plan",
        objetivo="Convertir tres planes en trabajo: sprints, capacidad y "
                 "contratiempos.",
        disponible=True,
    ),
    Sesion(
        numero=6,
        titulo="Gestión del cambio",
        objetivo="Implantar el proyecto y gestionar los conflictos que aparecen.",
        disponible=False,
    ),
    Sesion(
        numero=7,
        titulo="Comité de Dirección",
        objetivo="Defender la estrategia y compararla con la del resto de filiales.",
        disponible=False,
    ),
]


def disponibles() -> list[Sesion]:
    return [s for s in SESIONES if s.disponible]
