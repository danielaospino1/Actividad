"""
Genera el dataset sucio de ventas para la actividad Data Cleaning Detective.
Ejecutar una sola vez: python generate_dataset.py
"""
import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

N = 300

productos = ["Laptop", "Monitor", "Teclado", "Mouse", "Auriculares",
             "Webcam", "Hub USB", "Cable HDMI", "SSD externo", "Impresora"]
categorias = {
    "Laptop": "Computadoras", "Monitor": "Computadoras",
    "Teclado": "Periféricos",  "Mouse": "Periféricos",
    "Auriculares": "Audio",     "Webcam": "Video",
    "Hub USB": "Accesorios",   "Cable HDMI": "Accesorios",
    "SSD externo": "Almacenamiento", "Impresora": "Impresión"
}
precios_base = {
    "Laptop": 1200, "Monitor": 350, "Teclado": 80, "Mouse": 45,
    "Auriculares": 120, "Webcam": 90, "Hub USB": 35, "Cable HDMI": 20,
    "SSD externo": 110, "Impresora": 200
}
vendedores = ["Ana García", "Carlos López", "María Rodríguez",
              "Juan Martínez", "Laura Sánchez"]
ciudades = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena"]
metodos_pago = ["Tarjeta", "Efectivo", "Transferencia", "PSE"]

fechas = pd.date_range("2024-01-01", "2024-12-31", periods=N)
fechas = sorted([f + pd.Timedelta(hours=random.randint(8, 20)) for f in fechas])

prods = [random.choice(productos) for _ in range(N)]
cantidades = [random.randint(1, 10) for _ in range(N)]
precios = [round(precios_base[p] * random.uniform(0.85, 1.15), 2) for p in prods]
total = [round(c * p, 2) for c, p in zip(cantidades, precios)]

df = pd.DataFrame({
    "id_venta":      range(1001, 1001 + N),
    "fecha":         fechas,
    "vendedor":      [random.choice(vendedores) for _ in range(N)],
    "producto":      prods,
    "categoria":     [categorias[p] for p in prods],
    "cantidad":      cantidades,
    "precio_unitario": precios,
    "total_venta":   total,
    "ciudad":        [random.choice(ciudades) for _ in range(N)],
    "metodo_pago":   [random.choice(metodos_pago) for _ in range(N)],
    "calificacion":  [random.randint(1, 5) for _ in range(N)],
})

# ── INTRODUCIR PROBLEMAS ──────────────────────────────────────────────────────

# 1. Valores nulos (~10% en varias columnas)
for col, pct in [("vendedor", 0.07), ("ciudad", 0.09),
                  ("calificacion", 0.12), ("metodo_pago", 0.06)]:
    idx = df.sample(frac=pct, random_state=42).index
    df.loc[idx, col] = np.nan

# 2. Duplicados exactos (15 filas repetidas)
dupes = df.sample(15, random_state=7)
df = pd.concat([df, dupes], ignore_index=True)

# 3. Outliers en precio_unitario (precios absurdos)
bad_price_idx = df.sample(8, random_state=13).index
df.loc[bad_price_idx, "precio_unitario"] = df.loc[bad_price_idx, "precio_unitario"] * random.uniform(15, 30)

# 4. Outliers en cantidad (cantidades imposibles)
bad_qty_idx = df.sample(5, random_state=21).index
df.loc[bad_qty_idx, "cantidad"] = [500, 999, 750, 600, 850]

# 5. Valores negativos en total_venta
neg_idx = df.sample(6, random_state=33).index
df.loc[neg_idx, "total_venta"] = df.loc[neg_idx, "total_venta"] * -1

# 6. Inconsistencias en ciudad (abreviaciones y variantes)
bad_city_idx = df.sample(12, random_state=55).index
replacements = ["BOG", "MDE", "CALI", "Bquilla", "Ctgna",
                "bogota", "medellin", "BARRANQUILLA", "bog", "cali",
                "Medellin", "Bogota"]
for i, idx in enumerate(bad_city_idx):
    df.loc[idx, "ciudad"] = replacements[i % len(replacements)]

# 7. Columna extra completamente vacía (error de importación)
df["notas"] = np.nan

# Mezclar
df = df.sample(frac=1, random_state=99).reset_index(drop=True)

df.to_csv("ventas_sucias.csv", index=False)
print(f"✅ Dataset generado: {len(df)} filas, {df.shape[1]} columnas")
print(f"   Nulos por columna:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"   Duplicados: {df.duplicated().sum()}")
