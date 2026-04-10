# 🕵️ Data Cleaning Detective

Actividad interactiva de limpieza de datos para el curso de **Minería de Datos**.

## 📁 Archivos

```
data_detective/
├── app.py                # Aplicación principal Streamlit
├── generate_dataset.py   # Generador del dataset sucio
├── ventas_sucias.csv     # Dataset ya generado (listo para usar)
├── requirements.txt      # Dependencias Python
└── README.md             # Este archivo
```

---

## 🚀 Opción 1: Desplegar en Streamlit Cloud (recomendado)

> Gratis, sin instalación para los estudiantes. Solo necesitan un navegador.

### Pasos:

1. **Crear un repositorio en GitHub** (público o privado)
2. **Subir los 4 archivos** al repositorio:
   - `app.py`
   - `ventas_sucias.csv`
   - `requirements.txt`
   - (opcional) `README.md`

3. **Ir a [share.streamlit.io](https://share.streamlit.io)**
4. Conectar tu cuenta de GitHub
5. Seleccionar el repositorio y el archivo `app.py`
6. Clic en **"Deploy"** — listo en ~2 minutos

Tu app estará disponible en una URL como:
```
https://tu-usuario-data-detective.streamlit.app
```

Comparte esa URL con los estudiantes. ¡Sin instalar nada!

---

## 💻 Opción 2: Ejecutar localmente

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. (Opcional) Regenerar el dataset
python generate_dataset.py

# 3. Ejecutar la app
streamlit run app.py
```

La app abre automáticamente en `http://localhost:8501`

---

## 🎯 Flujo de la actividad (10 minutos)

| Fase | Descripción | Puntos |
|------|-------------|--------|
| 🔍 Explorar | Vista general, nulos, duplicados, distribuciones | 35 pts |
| 🧹 Limpiar | 10 problemas a resolver interactivamente | 180 pts |
| 🏆 Resultado | Score final + comparativa antes/después | — |

### Sistema de medallas

| Medalla | Puntos |
|---------|--------|
| 🥇 Detective Élite | ≥ 90% |
| 🥈 Detective Experto | ≥ 70% |
| 🥉 Detective Aprendiz | ≥ 50% |
| 🔍 Investigador Novato | < 50% |

---

## 🧪 Problemas en el dataset

El dataset `ventas_sucias.csv` tiene los siguientes problemas intencionales:

1. **Columna `notas`** — 100% vacía
2. **13 filas duplicadas** — registros repetidos exactos
3. **Nulos en `ciudad`** (~9%) — imputar con moda
4. **Nulos en `vendedor`** (~7%) — imputar con moda
5. **Nulos en `calificacion`** (~12%) — imputar con mediana
6. **Nulos en `metodo_pago`** (~6%) — imputar con 'Desconocido'
7. **Outliers en `precio_unitario`** — precios multiplicados x15-30
8. **Outliers en `cantidad`** — valores entre 500-999
9. **Totales negativos** en `total_venta`
10. **Ciudades inconsistentes** — 'BOG', 'bogota', 'Bquilla', etc.

---

## 📌 Notas para el profesor

- El dataset se **regenera** ejecutando `generate_dataset.py` (usa semillas fijas, siempre produce el mismo resultado)
- Los estudiantes **no pueden romper la app** — cada acción modifica solo la copia en sesión
- Al recargar la página, la sesión se reinicia automáticamente
- Funciona bien en móviles (layout responsivo de Streamlit)
