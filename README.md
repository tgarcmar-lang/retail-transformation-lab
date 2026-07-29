# Retail Transformation Lab

Plataforma docente de la Escuela Politécnica (UCJC). Cinco grupos de alumnos
dirigen cinco filiales de RetailNova Europa, una empresa ficticia de retail, y
toman decisiones sobre sostenibilidad, logística y operaciones.

Los alumnos solo necesitan un navegador y la URL. No instalan nada.

## Para el profesor

- **URL de clase:** https://retailnova-lab.streamlit.app/
- **Primera clase:** 8 de septiembre de 2026
- Abre la aplicación 10 minutos antes de clase: si lleva días sin usarse, tarda
  un poco en despertar.
- Un ordenador por grupo, no uno por alumno.

## Para desarrollar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
core/      Lógica de negocio (sin Streamlit dentro)
modulos/   Una interfaz por sesión de clase
datos/     Generador y datasets de las cinco filiales
tests/     Pruebas: datos, cálculos y recorrido completo de la sesión
```

El estado del proyecto y las decisiones tomadas están en `CLAUDE.md`.

## Aviso

**Este repositorio es público.** El material del profesor —guiones de clase,
que llevan escrito el hallazgo de cada filial— se guarda fuera, y `.gitignore`
bloquea `docs/`, `guion*` y `*.docx` para que no entre por descuido.
