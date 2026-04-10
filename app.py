"""
╔══════════════════════════════════════════════════════╗
║        DATA CLEANING DETECTIVE  🕵️                  ║
║   Actividad interactiva de limpieza de datos         ║
║   Curso de Minería de Datos — Pregrado               ║
╚══════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import os

# ─────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Cleaning Detective 🕵️",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Fondo principal */
  .stApp { background-color: #0f172a; color: #e2e8f0; }

  /* Sidebar */
  section[data-testid="stSidebar"] { background-color: #1e293b; }
  section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  /* Tarjetas de métricas */
  .metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 10px;
    text-align: center;
  }
  .metric-card .val  { font-size: 2.2rem; font-weight: 800; }
  .metric-card .lbl  { font-size: 0.85rem; color: #94a3b8; margin-top: 2px; }

  /* Tarjeta de problema */
  .problema-card {
    background: #1e293b;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
  }
  .problema-card.ok { border-left-color: #10b981; }

  /* Badge de puntos */
  .badge {
    display: inline-block;
    background: #0ea5e9;
    color: white;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-left: 8px;
  }

  /* Barra de progreso personalizada */
  .prog-wrap {
    background: #334155;
    border-radius: 8px;
    height: 18px;
    margin: 6px 0 14px 0;
    overflow: hidden;
  }
  .prog-bar {
    height: 100%;
    border-radius: 8px;
    transition: width 0.4s ease;
  }

  /* Título de sección */
  .section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #f8fafc;
    border-bottom: 2px solid #0ea5e9;
    padding-bottom: 6px;
    margin: 24px 0 16px 0;
  }

  /* Ocultar menú hamburguesa */
  #MainMenu, footer { visibility: hidden; }

  /* Botones */
  .stButton > button {
    background: #0ea5e9;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
  }
  .stButton > button:hover { background: #0284c7; }

  /* Tablas */
  .stDataFrame { border-radius: 10px; overflow: hidden; }

  /* Headers */
  h1, h2, h3 { color: #f8fafc !important; }

  /* Alertas */
  .stAlert { border-radius: 8px; }

  /* Expander */
  .streamlit-expanderHeader { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────
PUNTOS = {
    "explorar_vista":        5,
    "explorar_nulos":       10,
    "explorar_duplicados":  10,
    "explorar_outliers":    10,
    "limpiar_col_vacia":    15,
    "limpiar_duplicados":   20,
    "limpiar_nulos_ciudad": 15,
    "limpiar_nulos_vendedor": 15,
    "limpiar_nulos_calificacion": 15,
    "limpiar_nulos_metodo": 15,
    "limpiar_outliers_precio": 25,
    "limpiar_outliers_cantidad": 25,
    "limpiar_negativos":    20,
    "limpiar_ciudad_inconsistente": 20,
}
PUNTOS_MAX = sum(PUNTOS.values())

CIUDADES_VALIDAS = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena"]
CIUDADES_MAP = {
    "BOG": "Bogotá", "bogota": "Bogotá", "bog": "Bogotá", "Bogota": "Bogotá",
    "MDE": "Medellín", "medellin": "Medellín", "Medellin": "Medellín",
    "CALI": "Cali", "cali": "Cali",
    "Bquilla": "Barranquilla", "BARRANQUILLA": "Barranquilla",
    "Ctgna": "Cartagena",
}


def init_state():
    defaults = {
        "df_trabajo": None,
        "df_original": None,
        "puntos": 0,
        "logros": [],
        "fase": "inicio",
        "acciones_realizadas": set(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sumar_puntos(clave: str):
    if clave not in st.session_state.acciones_realizadas:
        pts = PUNTOS.get(clave, 0)
        st.session_state.puntos += pts
        st.session_state.acciones_realizadas.add(clave)
        return pts
    return 0


def barra_progreso(valor, maximo, color="#0ea5e9"):
    pct = min(int(valor / maximo * 100), 100)
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-bar" style="width:{pct}%; background:{color};"></div>
    </div>
    <p style="color:#94a3b8;font-size:0.8rem;margin-top:-10px;">{valor}/{maximo} puntos ({pct}%)</p>
    """, unsafe_allow_html=True)


def medalla(puntos_totales):
    if puntos_totales >= PUNTOS_MAX * 0.9:
        return "🥇 Detective Élite", "#f59e0b"
    elif puntos_totales >= PUNTOS_MAX * 0.7:
        return "🥈 Detective Experto", "#94a3b8"
    elif puntos_totales >= PUNTOS_MAX * 0.5:
        return "🥉 Detective Aprendiz", "#b45309"
    else:
        return "🔍 Investigador Novato", "#64748b"


def cargar_dataset():
    ruta = os.path.join(os.path.dirname(__file__), "ventas_sucias.csv")
    df = pd.read_csv(ruta, parse_dates=["fecha"])
    return df


# ─────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🕵️ Data Detective")
        st.markdown("---")

        # Score
        pts = st.session_state.puntos
        st.markdown(f"### 🏆 Puntuación")
        barra_progreso(pts, PUNTOS_MAX,
                       "#10b981" if pts >= PUNTOS_MAX * 0.7 else "#0ea5e9")

        # Medalla actual
        nombre_medalla, color_medalla = medalla(pts)
        st.markdown(
            f'<div style="background:{color_medalla}22;border:1px solid {color_medalla};'
            f'border-radius:8px;padding:8px;text-align:center;margin:8px 0;">'
            f'<span style="color:{color_medalla};font-weight:700;">{nombre_medalla}</span>'
            f'</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Navegación de fases
        st.markdown("### 📋 Fases")
        fases = [
            ("🚀", "inicio",   "Inicio"),
            ("🔍", "explorar", "Explorar Dataset"),
            ("🧹", "limpiar",  "Limpiar Datos"),
            ("🏆", "resultado","Resultado Final"),
        ]
        for emoji, clave, nombre in fases:
            activa = st.session_state.fase == clave
            bloqueada = (clave == "limpiar" and
                         "explorar_vista" not in st.session_state.acciones_realizadas)
            bloqueada2 = (clave == "resultado" and
                          len(st.session_state.acciones_realizadas) < 5)

            if bloqueada or bloqueada2:
                st.markdown(
                    f'<div style="color:#475569;padding:6px 0;">🔒 {nombre}</div>',
                    unsafe_allow_html=True)
            elif activa:
                st.markdown(
                    f'<div style="background:#0ea5e933;border-left:3px solid #0ea5e9;'
                    f'padding:6px 10px;border-radius:4px;font-weight:700;">'
                    f'{emoji} {nombre}</div>', unsafe_allow_html=True)
            else:
                if st.button(f"{emoji} {nombre}", key=f"nav_{clave}",
                             use_container_width=True):
                    st.session_state.fase = clave
                    st.rerun()

        st.markdown("---")

        # Dataset info rápida
        if st.session_state.df_trabajo is not None:
            df = st.session_state.df_trabajo
            st.markdown("### 📊 Estado actual")
            st.markdown(f"- **Filas:** {len(df)}")
            st.markdown(f"- **Columnas:** {df.shape[1]}")
            nulos = df.isnull().sum().sum()
            dupes = df.duplicated().sum()
            col_a = "🔴" if nulos > 0 else "🟢"
            col_b = "🔴" if dupes > 0 else "🟢"
            st.markdown(f"- {col_a} **Nulos:** {nulos}")
            st.markdown(f"- {col_b} **Duplicados:** {dupes}")

        st.markdown("---")
        st.caption("Curso de Minería de Datos · 2026")


# ─────────────────────────────────────────────────────
# FASE 0: INICIO
# ─────────────────────────────────────────────────────
def fase_inicio():
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px 0;">
      <div style="font-size:5rem;">🕵️</div>
      <h1 style="font-size:2.8rem;margin:10px 0;">Data Cleaning Detective</h1>
      <p style="color:#94a3b8;font-size:1.1rem;max-width:600px;margin:0 auto;">
        Recibes un dataset de ventas contaminado con errores reales.<br>
        Tu misión: detectarlos, limpiarlos y demostrar tu dominio del procesamiento de datos.
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    tarjetas = [
        ("🔍", "Explora", "Analiza el dataset visualmente y detecta los problemas ocultos.", "#3b82f6"),
        ("🧹", "Limpia",  "Aplica técnicas reales: imputación, deduplicación, filtrado.", "#8b5cf6"),
        ("🏆", "Puntúa",  "Cada acción correcta suma puntos. ¿Llegarás a Detective Élite?", "#f59e0b"),
    ]
    for col, (icon, titulo, desc, color) in zip([col1, col2, col3], tarjetas):
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid {color}44;border-top:3px solid {color};
                        border-radius:12px;padding:24px;text-align:center;height:180px;">
              <div style="font-size:2.2rem;">{icon}</div>
              <h3 style="color:{color};margin:8px 0;">{titulo}</h3>
              <p style="color:#94a3b8;font-size:0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Info del dataset
    st.markdown('<div class="section-title">📁 Tu misión</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        Eres analista de datos en una empresa de tecnología. El equipo de ventas te entregó
        su dataset del año 2024, pero **alguien cometió errores al exportarlo**.

        El dataset contiene información de **ventas de productos tecnológicos** en varias ciudades
        de Colombia. Antes de poder usarlo para análisis o modelos predictivos, debes:

        - 🔎 Identificar todos los problemas de calidad
        - 🧹 Aplicar las técnicas de limpieza adecuadas
        - ✅ Validar que el dataset quede en buen estado
        """)
    with col_b:
        st.markdown("""
        <div class="metric-card">
          <div class="val" style="color:#0ea5e9;">315</div>
          <div class="lbl">Registros de ventas</div>
        </div>
        <div class="metric-card">
          <div class="val" style="color:#f59e0b;">12</div>
          <div class="lbl">Columnas</div>
        </div>
        <div class="metric-card">
          <div class="val" style="color:#ef4444;">7+</div>
          <div class="lbl">Tipos de problemas</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🚀 ¡Comenzar investigación!", use_container_width=True):
            df = cargar_dataset()
            st.session_state.df_original = df.copy()
            st.session_state.df_trabajo  = df.copy()
            st.session_state.fase = "explorar"
            st.rerun()


# ─────────────────────────────────────────────────────
# FASE 1: EXPLORAR
# ─────────────────────────────────────────────────────
def fase_explorar():
    df = st.session_state.df_trabajo

    sumar_puntos("explorar_vista")

    st.markdown("# 🔍 Fase 1 — Explorar el Dataset")
    st.markdown(
        "Antes de limpiar, necesitas **entender qué tienes**. "
        "Usa las herramientas de abajo para detectar los problemas.")

    # ── TAB LAYOUT ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Vista general", "🕳️ Valores nulos", "👯 Duplicados", "📈 Distribuciones"
    ])

    # ── TAB 1: VISTA GENERAL ──
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        metricas = [
            (len(df), "Total filas", "#0ea5e9"),
            (df.shape[1], "Columnas", "#8b5cf6"),
            (int(df.isnull().sum().sum()), "Valores nulos", "#ef4444"),
            (int(df.duplicated().sum()), "Filas duplicadas", "#f59e0b"),
        ]
        for col, (val, lbl, color) in zip([col1, col2, col3, col4], metricas):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="val" style="color:{color};">{val}</div>
                  <div class="lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("#### Primeras 10 filas del dataset")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("#### Estadísticas descriptivas")
        st.dataframe(df.describe(include="all").round(2), use_container_width=True)

    # ── TAB 2: NULOS ──
    with tab2:
        sumar_puntos("explorar_nulos")

        nulos = df.isnull().sum().reset_index()
        nulos.columns = ["Columna", "Nulos"]
        nulos["Porcentaje"] = (nulos["Nulos"] / len(df) * 100).round(1)
        nulos["Estado"] = nulos["Nulos"].apply(
            lambda x: "🔴 Crítico" if x/len(df) > 0.1 else ("🟡 Moderado" if x > 0 else "🟢 OK"))
        nulos = nulos.sort_values("Nulos", ascending=False)

        st.markdown("#### Mapa de valores nulos por columna")
        st.dataframe(nulos, use_container_width=True, hide_index=True)

        # Gráfico de nulos
        fig, ax = plt.subplots(figsize=(9, 3.5), facecolor="#1e293b")
        ax.set_facecolor("#1e293b")
        cols_con_nulos = nulos[nulos["Nulos"] > 0]
        bars = ax.barh(cols_con_nulos["Columna"], cols_con_nulos["Porcentaje"],
                       color=["#ef4444" if p > 10 else "#f59e0b"
                               for p in cols_con_nulos["Porcentaje"]],
                       edgecolor="none")
        ax.set_xlabel("% de valores nulos", color="#94a3b8")
        ax.tick_params(colors="#94a3b8")
        ax.spines[["top","right","bottom","left"]].set_visible(False)
        ax.set_title("Porcentaje de nulos por columna", color="#f8fafc", pad=12)
        for bar, val in zip(bars, cols_con_nulos["Porcentaje"]):
            ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                    f"{val}%", va="center", color="#e2e8f0", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        with st.expander("💡 Pista: ¿Qué debo buscar?"):
            st.markdown("""
            - ¿Hay alguna columna con el **100% de nulos**? Eso es una columna vacía inútil.
            - Columnas con >10% de nulos son **críticas** y necesitan imputación o eliminación.
            - Nulos en columnas categóricas como `ciudad` o `vendedor` pueden imputarse con la **moda**.
            - Nulos en `calificacion` (numérica) → usa la **mediana**.
            """)

    # ── TAB 3: DUPLICADOS ──
    with tab3:
        sumar_puntos("explorar_duplicados")

        dupes = df[df.duplicated(keep=False)]
        n_dupes = df.duplicated().sum()

        if n_dupes > 0:
            st.warning(f"⚠️ Se encontraron **{n_dupes} filas duplicadas** ({n_dupes/len(df)*100:.1f}% del dataset).")
            st.markdown("#### Ejemplo de filas duplicadas")
            st.dataframe(dupes.sort_values("id_venta").head(10),
                         use_container_width=True)
        else:
            st.success("✅ No hay filas duplicadas.")

        with st.expander("💡 Pista: ¿Por qué existen duplicados?"):
            st.markdown("""
            Los duplicados suelen aparecer por:
            - Exportaciones múltiples del mismo reporte
            - Errores en pipelines ETL
            - Uniones (JOINs) mal configuradas

            **Solución:** `df.drop_duplicates(inplace=True)`
            """)

    # ── TAB 4: DISTRIBUCIONES ──
    with tab4:
        sumar_puntos("explorar_outliers")

        st.markdown("#### Detecta outliers visualmente")
        col_sel = st.selectbox("Selecciona una columna numérica:",
                               ["precio_unitario", "cantidad", "total_venta", "calificacion"])

        fig, axes = plt.subplots(1, 2, figsize=(11, 4), facecolor="#1e293b")
        for ax in axes:
            ax.set_facecolor("#0f172a")
            ax.tick_params(colors="#94a3b8")
            ax.spines[["top","right","bottom","left"]].set_color("#334155")

        data = df[col_sel].dropna()

        # Histograma
        axes[0].hist(data, bins=40, color="#0ea5e9", alpha=0.85, edgecolor="none")
        axes[0].set_title(f"Distribución: {col_sel}", color="#f8fafc", pad=10)
        axes[0].set_xlabel(col_sel, color="#94a3b8")
        axes[0].set_ylabel("Frecuencia", color="#94a3b8")

        # Boxplot
        bp = axes[1].boxplot(data, vert=False, patch_artist=True,
                             medianprops=dict(color="#f59e0b", linewidth=2),
                             flierprops=dict(marker="o", color="#ef4444",
                                             markerfacecolor="#ef4444", markersize=5),
                             whiskerprops=dict(color="#94a3b8"),
                             capprops=dict(color="#94a3b8"),
                             boxprops=dict(facecolor="#0ea5e933", color="#0ea5e9"))
        axes[1].set_title(f"Boxplot: {col_sel}", color="#f8fafc", pad=10)
        axes[1].set_xlabel(col_sel, color="#94a3b8")
        axes[1].set_yticks([])

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        # Estadísticas del outlier
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        iqr = q3 - q1
        outliers = data[(data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Outliers detectados (IQR)", len(outliers))
        with c2:
            st.metric("Valor mínimo", f"{data.min():.2f}")
        with c3:
            st.metric("Valor máximo", f"{data.max():.2f}")

        with st.expander("💡 Pista: ¿Cómo identificar outliers?"):
            st.markdown("""
            El método **IQR (Rango Intercuartílico)** es el más común:
            - Límite inferior: `Q1 - 1.5 × IQR`
            - Límite superior: `Q3 + 1.5 × IQR`

            Valores fuera de estos límites son **candidatos a outliers**.
            Pregúntate: ¿tiene sentido que `precio_unitario` sea >10.000? ¿O `cantidad` sea 999?
            """)

    # Botón para avanzar
    st.markdown("---")
    pts_ganados = sum(PUNTOS[k] for k in ["explorar_vista","explorar_nulos",
                      "explorar_duplicados","explorar_outliers"]
                      if k in st.session_state.acciones_realizadas)
    st.info(f"✅ Exploración completada — **{pts_ganados} puntos ganados** en esta fase.")
    if st.button("➡️ Continuar a Limpieza de Datos", use_container_width=False):
        st.session_state.fase = "limpiar"
        st.rerun()


# ─────────────────────────────────────────────────────
# FASE 2: LIMPIAR
# ─────────────────────────────────────────────────────
def fase_limpiar():
    df = st.session_state.df_trabajo

    st.markdown("# 🧹 Fase 2 — Limpiar el Dataset")
    st.markdown(
        "Aplica las técnicas de limpieza en el orden que prefieras. "
        "**Cada acción es irreversible** sobre el dataset de trabajo, ¡elige bien!")

    # Panel de estado
    nulos_total  = int(df.isnull().sum().sum())
    dupes_total  = int(df.duplicated().sum())
    acciones_hechas = len([k for k in st.session_state.acciones_realizadas
                           if k.startswith("limpiar_")])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Filas actuales", len(df),
                  delta=f"{len(df)-len(st.session_state.df_original)}")
    with c2:
        st.metric("Nulos restantes", nulos_total,
                  delta_color="inverse")
    with c3:
        st.metric("Duplicados", dupes_total,
                  delta_color="inverse")
    with c4:
        st.metric("Acciones realizadas", acciones_hechas,
                  help="Máximo disponible: 9 acciones")

    st.markdown("---")

    # ── PROBLEMAS A RESOLVER ──
    problemas = [
        {
            "id": "limpiar_col_vacia",
            "titulo": "🗑️ Columna completamente vacía",
            "descripcion": "Existe una columna con el 100% de valores nulos. Es inútil y ocupa espacio.",
            "pistas": "Usa `df.dropna(axis=1, how='all', inplace=True)` para eliminar columnas totalmente vacías.",
            "puntos": PUNTOS["limpiar_col_vacia"],
        },
        {
            "id": "limpiar_duplicados",
            "titulo": "👯 Filas duplicadas",
            "descripcion": f"Hay {int(st.session_state.df_original.duplicated().sum())} registros exactamente repetidos.",
            "pistas": "Usa `df.drop_duplicates(inplace=True)` para conservar solo la primera ocurrencia.",
            "puntos": PUNTOS["limpiar_duplicados"],
        },
        {
            "id": "limpiar_nulos_ciudad",
            "titulo": "🕳️ Nulos en 'ciudad'",
            "descripcion": "La columna 'ciudad' tiene valores faltantes. Imputar con la moda es razonable.",
            "pistas": "Moda: `df['ciudad'].fillna(df['ciudad'].mode()[0], inplace=True)`",
            "puntos": PUNTOS["limpiar_nulos_ciudad"],
        },
        {
            "id": "limpiar_nulos_vendedor",
            "titulo": "🕳️ Nulos en 'vendedor'",
            "descripcion": "Hay ventas sin vendedor asignado.",
            "pistas": "Imputar con la moda: `df['vendedor'].fillna(df['vendedor'].mode()[0], inplace=True)`",
            "puntos": PUNTOS["limpiar_nulos_vendedor"],
        },
        {
            "id": "limpiar_nulos_calificacion",
            "titulo": "🕳️ Nulos en 'calificacion'",
            "descripcion": "Variable numérica con nulos. La mediana es más robusta que la media.",
            "pistas": "Mediana: `df['calificacion'].fillna(df['calificacion'].median(), inplace=True)`",
            "puntos": PUNTOS["limpiar_nulos_calificacion"],
        },
        {
            "id": "limpiar_nulos_metodo",
            "titulo": "🕳️ Nulos en 'metodo_pago'",
            "descripcion": "Método de pago desconocido en algunas transacciones.",
            "pistas": "Imputar con 'Desconocido' o con la moda.",
            "puntos": PUNTOS["limpiar_nulos_metodo"],
        },
        {
            "id": "limpiar_outliers_precio",
            "titulo": "📈 Outliers en 'precio_unitario'",
            "descripcion": "Algunos precios son absurdamente altos (errores de digitación).",
            "pistas": "Calcula IQR y filtra: `df = df[df['precio_unitario'] <= Q3 + 1.5*IQR]`",
            "puntos": PUNTOS["limpiar_outliers_precio"],
        },
        {
            "id": "limpiar_outliers_cantidad",
            "titulo": "📈 Outliers en 'cantidad'",
            "descripcion": "Cantidades de 500-999 unidades no tienen sentido para ventas individuales.",
            "pistas": "Filtra cantidades razonables: `df = df[df['cantidad'] <= 50]`",
            "puntos": PUNTOS["limpiar_outliers_cantidad"],
        },
        {
            "id": "limpiar_negativos",
            "titulo": "➖ Totales negativos en 'total_venta'",
            "descripcion": "Hay ventas con total negativo, lo cual es un error (no son devoluciones).",
            "pistas": "Filtra: `df = df[df['total_venta'] > 0]`",
            "puntos": PUNTOS["limpiar_negativos"],
        },
        {
            "id": "limpiar_ciudad_inconsistente",
            "titulo": "🔀 Ciudades con formatos inconsistentes",
            "descripcion": "La columna 'ciudad' tiene abreviaciones y variantes: 'BOG', 'bogota', 'Bquilla'...",
            "pistas": "Usa un diccionario de mapeo y `.replace()` para estandarizar.",
            "puntos": PUNTOS["limpiar_ciudad_inconsistente"],
        },
    ]

    # Mostrar cada problema
    for prob in problemas:
        ya_resuelto = prob["id"] in st.session_state.acciones_realizadas
        clase = "problema-card ok" if ya_resuelto else "problema-card"
        estado_icon = "✅" if ya_resuelto else "⚠️"

        st.markdown(f"""
        <div class="{clase}">
          <strong>{estado_icon} {prob['titulo']}</strong>
          <span class="badge">+{prob['puntos']} pts</span>
          <p style="color:#94a3b8;margin:6px 0 0 0;font-size:0.9rem;">{prob['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

        if not ya_resuelto:
            with st.expander(f"🔧 Resolver: {prob['titulo']}"):
                st.markdown(f"**💡 Pista:** {prob['pistas']}")
                _render_accion(prob["id"], df)

    st.markdown("---")
    completados = len([p for p in problemas
                       if p["id"] in st.session_state.acciones_realizadas])
    st.info(f"📊 **{completados}/{len(problemas)} problemas resueltos**")

    if completados >= 5:
        if st.button("🏆 Ver mi resultado final", use_container_width=False):
            st.session_state.fase = "resultado"
            st.rerun()
    else:
        st.warning("Resuelve al menos 5 problemas para ver tu resultado final.")


def _render_accion(prob_id: str, df: pd.DataFrame):
    """Renderiza el botón de acción para cada problema."""

    if prob_id == "limpiar_col_vacia":
        cols_vacias = [c for c in df.columns if df[c].isnull().all()]
        if cols_vacias:
            st.code(f"# Columnas completamente vacías: {cols_vacias}\ndf.dropna(axis=1, how='all', inplace=True)")
            if st.button("Eliminar columnas vacías", key=prob_id):
                st.session_state.df_trabajo.dropna(axis=1, how="all", inplace=True)
                pts = sumar_puntos(prob_id)
                st.success(f"✅ Columna(s) {cols_vacias} eliminada(s). +{pts} puntos 🎉")
                st.rerun()
        else:
            st.success("No hay columnas completamente vacías (ya resuelto).")

    elif prob_id == "limpiar_duplicados":
        n = df.duplicated().sum()
        st.code(f"# Duplicados actuales: {n}\ndf.drop_duplicates(inplace=True)")
        if st.button("Eliminar duplicados", key=prob_id):
            st.session_state.df_trabajo.drop_duplicates(inplace=True)
            st.session_state.df_trabajo.reset_index(drop=True, inplace=True)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n} duplicados eliminados. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_nulos_ciudad":
        n = df["ciudad"].isnull().sum()
        moda = df["ciudad"].mode()[0] if not df["ciudad"].mode().empty else "Bogotá"
        st.code(f"# Nulos en 'ciudad': {n}\n# Moda: '{moda}'\ndf['ciudad'].fillna(df['ciudad'].mode()[0], inplace=True)")
        if st.button("Imputar nulos en ciudad", key=prob_id):
            st.session_state.df_trabajo["ciudad"] = st.session_state.df_trabajo["ciudad"].fillna(moda)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n} nulos imputados con '{moda}'. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_nulos_vendedor":
        n = df["vendedor"].isnull().sum() if "vendedor" in df.columns else 0
        moda = df["vendedor"].mode()[0] if "vendedor" in df.columns and not df["vendedor"].mode().empty else "Ana García"
        st.code(f"# Nulos en 'vendedor': {n}\ndf['vendedor'].fillna(df['vendedor'].mode()[0], inplace=True)")
        if st.button("Imputar nulos en vendedor", key=prob_id):
            st.session_state.df_trabajo["vendedor"] = st.session_state.df_trabajo["vendedor"].fillna(moda)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n} nulos imputados con '{moda}'. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_nulos_calificacion":
        n = df["calificacion"].isnull().sum()
        mediana = df["calificacion"].median()
        st.code(f"# Nulos en 'calificacion': {n}\n# Mediana: {mediana}\ndf['calificacion'].fillna(df['calificacion'].median(), inplace=True)")
        if st.button("Imputar calificación con mediana", key=prob_id):
            st.session_state.df_trabajo["calificacion"] = st.session_state.df_trabajo["calificacion"].fillna(mediana)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n} nulos imputados con mediana={mediana}. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_nulos_metodo":
        n = df["metodo_pago"].isnull().sum() if "metodo_pago" in df.columns else 0
        st.code(f"# Nulos en 'metodo_pago': {n}\ndf['metodo_pago'].fillna('Desconocido', inplace=True)")
        if st.button("Imputar método de pago", key=prob_id):
            st.session_state.df_trabajo["metodo_pago"] = st.session_state.df_trabajo["metodo_pago"].fillna("Desconocido")
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n} nulos reemplazados con 'Desconocido'. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_outliers_precio":
        col = "precio_unitario"
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        limite = q3 + 1.5 * iqr
        n_out = int((df[col] > limite).sum())
        st.code(f"# Outliers en precio_unitario: {n_out}\n# Límite superior IQR: {limite:.2f}\ndf = df[df['precio_unitario'] <= {limite:.2f}]")
        if st.button("Eliminar outliers de precio", key=prob_id):
            st.session_state.df_trabajo = \
                st.session_state.df_trabajo[
                    st.session_state.df_trabajo[col] <= limite
                ].reset_index(drop=True)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n_out} outliers de precio eliminados. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_outliers_cantidad":
        col = "cantidad"
        limite = 50
        n_out = int((df[col] > limite).sum())
        st.code(f"# Cantidades anómalas (> {limite}): {n_out}\ndf = df[df['cantidad'] <= {limite}]")
        if st.button("Filtrar cantidades anómalas", key=prob_id):
            st.session_state.df_trabajo = \
                st.session_state.df_trabajo[
                    st.session_state.df_trabajo[col] <= limite
                ].reset_index(drop=True)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n_out} filas con cantidad anómala eliminadas. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_negativos":
        col = "total_venta"
        n_neg = int((df[col] < 0).sum())
        st.code(f"# Totales negativos: {n_neg}\ndf = df[df['total_venta'] > 0]")
        if st.button("Eliminar totales negativos", key=prob_id):
            st.session_state.df_trabajo = \
                st.session_state.df_trabajo[
                    st.session_state.df_trabajo[col] > 0
                ].reset_index(drop=True)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n_neg} filas con total negativo eliminadas. +{pts} puntos 🎉")
            st.rerun()

    elif prob_id == "limpiar_ciudad_inconsistente":
        ciudades_map = CIUDADES_MAP
        ciudades_raras = [c for c in df["ciudad"].dropna().unique()
                          if c not in CIUDADES_VALIDAS]
        n_afectadas = df["ciudad"].isin(ciudades_raras).sum()
        st.code(f"# Ciudades no estándar detectadas: {ciudades_raras[:5]}...\n"
                f"# Filas afectadas: {n_afectadas}\n"
                f"ciudades_map = {ciudades_map}\n"
                f"df['ciudad'] = df['ciudad'].replace(ciudades_map)")
        if st.button("Estandarizar ciudades", key=prob_id):
            st.session_state.df_trabajo["ciudad"] = \
                st.session_state.df_trabajo["ciudad"].replace(ciudades_map)
            pts = sumar_puntos(prob_id)
            st.success(f"✅ {n_afectadas} ciudades estandarizadas. +{pts} puntos 🎉")
            st.rerun()


# ─────────────────────────────────────────────────────
# FASE 3: RESULTADO FINAL
# ─────────────────────────────────────────────────────
def fase_resultado():
    df_original = st.session_state.df_original
    df_limpio   = st.session_state.df_trabajo
    puntos_total = st.session_state.puntos
    nombre_medalla, color_medalla = medalla(puntos_total)

    # ── HERO ──
    st.markdown(f"""
    <div style="text-align:center;padding:32px 0 20px;">
      <div style="font-size:4rem;">{nombre_medalla.split()[0]}</div>
      <h1 style="font-size:2.4rem;">{nombre_medalla}</h1>
      <div style="font-size:3rem;font-weight:800;color:{color_medalla};">
        {puntos_total} / {PUNTOS_MAX} pts
      </div>
    </div>
    """, unsafe_allow_html=True)

    barra_progreso(puntos_total, PUNTOS_MAX, color_medalla)

    st.markdown("---")

    # ── COMPARATIVA ──
    st.markdown('<div class="section-title">📊 Dataset: Antes vs Después</div>',
                unsafe_allow_html=True)

    metricas_comp = [
        ("Total filas",      len(df_original), len(df_limpio),   False),
        ("Columnas",         df_original.shape[1], df_limpio.shape[1], False),
        ("Valores nulos",    int(df_original.isnull().sum().sum()),
                             int(df_limpio.isnull().sum().sum()), True),
        ("Duplicados",       int(df_original.duplicated().sum()),
                             int(df_limpio.duplicated().sum()), True),
        ("Outliers precio",  int((df_original["precio_unitario"] >
                                  df_original["precio_unitario"].quantile(0.75) +
                                  1.5*(df_original["precio_unitario"].quantile(0.75) -
                                       df_original["precio_unitario"].quantile(0.25))).sum()),
                             int((df_limpio["precio_unitario"] >
                                  df_limpio["precio_unitario"].quantile(0.75) +
                                  1.5*(df_limpio["precio_unitario"].quantile(0.75) -
                                       df_limpio["precio_unitario"].quantile(0.25))).sum()),
                             True),
    ]

    cols = st.columns(len(metricas_comp))
    for col, (label, antes, despues, menor_es_mejor) in zip(cols, metricas_comp):
        with col:
            delta = despues - antes
            if menor_es_mejor:
                color = "#10b981" if delta < 0 else ("#ef4444" if delta > 0 else "#94a3b8")
                signo = "▼" if delta < 0 else ("▲" if delta > 0 else "=")
            else:
                color = "#94a3b8"
                signo = ""
            st.markdown(f"""
            <div class="metric-card">
              <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;">{label}</div>
              <div style="display:flex;justify-content:center;gap:14px;margin:8px 0;">
                <div>
                  <div style="font-size:1.4rem;font-weight:700;color:#ef4444;">{antes}</div>
                  <div style="font-size:0.7rem;color:#94a3b8;">Antes</div>
                </div>
                <div style="font-size:1.4rem;color:#475569;align-self:center;">→</div>
                <div>
                  <div style="font-size:1.4rem;font-weight:700;color:#10b981;">{despues}</div>
                  <div style="font-size:0.7rem;color:#94a3b8;">Después</div>
                </div>
              </div>
              <div style="color:{color};font-weight:700;font-size:0.9rem;">{signo} {abs(delta)}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── GRÁFICA COMPARATIVA ──
    st.markdown("#### Distribución de precio_unitario: Antes vs Después")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), facecolor="#1e293b")
    for ax in axes:
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors="#94a3b8")
        ax.spines[["top","right","left","bottom"]].set_color("#334155")

    axes[0].hist(df_original["precio_unitario"].dropna(), bins=50,
                 color="#ef4444", alpha=0.8, edgecolor="none")
    axes[0].set_title("ANTES (con outliers)", color="#f8fafc", pad=10)
    axes[0].set_xlabel("Precio Unitario", color="#94a3b8")

    axes[1].hist(df_limpio["precio_unitario"].dropna(), bins=50,
                 color="#10b981", alpha=0.8, edgecolor="none")
    axes[1].set_title("DESPUÉS (limpio)", color="#f8fafc", pad=10)
    axes[1].set_xlabel("Precio Unitario", color="#94a3b8")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── ACCIONES REALIZADAS ──
    st.markdown('<div class="section-title">✅ Acciones realizadas</div>',
                unsafe_allow_html=True)
    acciones_limpiar = [k for k in st.session_state.acciones_realizadas
                        if k.startswith("limpiar_")]
    todas = [k for k in PUNTOS if k.startswith("limpiar_")]

    col_a, col_b = st.columns(2)
    for i, k in enumerate(todas):
        hecho = k in acciones_limpiar
        nombre_legible = k.replace("limpiar_", "").replace("_", " ").title()
        icon = "✅" if hecho else "❌"
        pts = PUNTOS[k]
        target = col_a if i % 2 == 0 else col_b
        with target:
            st.markdown(
                f'<div style="background:#1e293b;border-radius:8px;padding:10px 14px;'
                f'margin:4px 0;border-left:3px solid {"#10b981" if hecho else "#334155"};">'
                f'{icon} <strong>{nombre_legible}</strong> '
                f'<span style="color:{"#10b981" if hecho else "#64748b"};">+{pts if hecho else 0} pts</span>'
                f'</div>', unsafe_allow_html=True)

    # ── DESCARGA ──
    st.markdown('<div class="section-title">📥 Descargar dataset limpio</div>',
                unsafe_allow_html=True)

    csv_buffer = io.StringIO()
    df_limpio.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()

    col_dl, _, _ = st.columns([1, 2, 1])
    with col_dl:
        st.download_button(
            label="⬇️ Descargar ventas_limpias.csv",
            data=csv_str,
            file_name="ventas_limpias.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── VOLVER A INTENTAR ──
    st.markdown("---")
    if st.button("🔄 Reiniciar actividad", use_container_width=False):
        for key in ["df_trabajo", "df_original", "puntos",
                    "logros", "fase", "acciones_realizadas"]:
            del st.session_state[key]
        st.rerun()


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────
def main():
    init_state()
    render_sidebar()

    fase = st.session_state.fase

    if fase == "inicio":
        fase_inicio()
    elif fase == "explorar":
        fase_explorar()
    elif fase == "limpiar":
        fase_limpiar()
    elif fase == "resultado":
        fase_resultado()


if __name__ == "__main__":
    main()
