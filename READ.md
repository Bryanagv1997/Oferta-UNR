# 🧠 Análisis de Contratos Energéticos

Este repositorio contiene herramientas para la extracción y análisis de datos contractuales desde una base de datos PostgreSQL. Está diseñado para ser escalable, reutilizable y fácilmente integrable en pipelines de simulación energética.

## 📁 Estructura

- `db_utils.py`: Módulo para conexión y consulta a la base de datos.
- `notebook.ipynb`: Notebook para filtrar contratos de tipo "Compra" y calcular el promedio ponderado por año.
- `.env`: Archivo con las variables de entorno para la conexión PostgreSQL (no incluido por seguridad).

---

## ⚙️ Requisitos

Instala dependencias con:

```bash
pip install -r requirements.txt
