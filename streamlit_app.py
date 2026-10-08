import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Explorador de operación",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Carga los datos que utilizará la aplicación."""
    datos = pd.read_csv("datos_ejemplo.csv")
    datos["Fecha"] = pd.to_datetime(datos["Fecha"])
    return datos


df = cargar_datos()

st.title("Explorador de operación")
st.caption(
    "Tablero ejecutivo para explorar casos, tiempos de atención y satisfacción "
    "por área y región. Usa los filtros de la barra lateral; todos los "
    "indicadores, tablas y gráficas se actualizan con tu selección."
)

st.write("**Desarrollado por:** Emiliano Lopez Aguilar")

# ================================================================
# OPCIÓN A: TABLERO EJECUTIVO
# ================================================================

# ---------- Filtros ----------
st.sidebar.header("Filtros")

areas_disponibles = sorted(df["Área"].unique())
areas_seleccionadas = st.sidebar.multiselect(
    "Área",
    options=areas_disponibles,
    default=areas_disponibles,
)

# Filtro adicional 1: región
regiones_disponibles = sorted(df["Región"].unique())
regiones_seleccionadas = st.sidebar.multiselect(
    "Región",
    options=regiones_disponibles,
    default=regiones_disponibles,
)

# Filtro adicional 2: rango de fechas
fecha_min = df["Fecha"].min().date()
fecha_max = df["Fecha"].max().date()
rango_fechas = st.sidebar.slider(
    "Rango de fechas",
    min_value=fecha_min,
    max_value=fecha_max,
    value=(fecha_min, fecha_max),
    format="DD/MM/YYYY",
)

df_filtrado = df[
    df["Área"].isin(areas_seleccionadas)
    & df["Región"].isin(regiones_seleccionadas)
    & df["Fecha"].dt.date.between(rango_fechas[0], rango_fechas[1])
].copy()

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados. Ajusta tu selección.")
    st.stop()

# ---------- Indicadores (st.metric) ----------
total_casos = int(df_filtrado["Casos"].sum())
tiempo_promedio = df_filtrado["Tiempo_min"].mean()
satisfaccion_promedio = df_filtrado["Satisfacción"].mean()

# Comparación contra el promedio general (sin filtros)
delta_tiempo = tiempo_promedio - df["Tiempo_min"].mean()
delta_satisfaccion = satisfaccion_promedio - df["Satisfacción"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Casos totales", f"{total_casos:,}")
col2.metric(
    "Tiempo promedio (min)",
    f"{tiempo_promedio:.1f}",
    delta=f"{delta_tiempo:+.1f} vs. general",
    delta_color="inverse",  # menos tiempo es mejor
)
col3.metric(
    "Satisfacción promedio",
    f"{satisfaccion_promedio:.1f}",
    delta=f"{delta_satisfaccion:+.1f} vs. general",
)

# ---------- Vistas (st.tabs) ----------
tab_resumen, tab_detalle = st.tabs(["📈 Resumen", "📋 Detalle"])

with tab_resumen:
    casos_por_fecha = (
        df_filtrado.groupby("Fecha", as_index=False)["Casos"]
        .sum()
        .sort_values("Fecha")
    )
    fig_linea = px.line(
        casos_por_fecha,
        x="Fecha",
        y="Casos",
        markers=True,
        title="Casos por fecha",
    )
    st.plotly_chart(fig_linea, width="stretch")

    casos_por_area = (
        df_filtrado.groupby("Área", as_index=False)["Casos"]
        .sum()
        .sort_values("Casos", ascending=False)
    )
    fig_barras = px.bar(
        casos_por_area,
        x="Área",
        y="Casos",
        title="Casos por área",
        text_auto=True,
    )
    st.plotly_chart(fig_barras, width="stretch")

with tab_detalle:
    st.subheader("Resumen por área")
    resumen_area = (
        df_filtrado.groupby("Área")
        .agg(
            Casos=("Casos", "sum"),
            Tiempo_promedio=("Tiempo_min", "mean"),
            Satisfacción_promedio=("Satisfacción", "mean"),
        )
        .round(1)
        .reset_index()
    )
    st.dataframe(resumen_area, width="stretch", hide_index=True)

    st.subheader("Datos filtrados")
    st.dataframe(df_filtrado, width="stretch", hide_index=True)
