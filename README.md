# 🕵️ Data Cleaning Detective

Actividad interactiva de limpieza de datos.

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

## 🚀 Opción 1: Desplegar en Streamlit Cloud

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
