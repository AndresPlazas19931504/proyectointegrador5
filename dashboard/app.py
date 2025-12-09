import streamlit as st
import pandas as pd
import plotly.express as px
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset_enriquecido.csv')

# Título y configuración general de la app
st.set_page_config(
    page_title="Dashboard de Riesgos Laborales",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carga de datos con caché para optimizar el rendimiento de Streamlit
@st.cache_data
def load_data(path):
    """Carga y prepara el dataset enriquecido."""
    if not os.path.exists(path):
        st.error(f"Error: No se encontró el archivo de datos en {path}. Asegúrese de ejecutar '02_enriquecimiento_eda.ipynb' primero.")
        return pd.DataFrame()
        
    df = pd.read_csv(path)
    # Asegurar tipos de datos correctos para el dashboard
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['anio'] = df['fecha'].dt.year
    df['mes_num'] = df['fecha'].dt.month
    
    # Lista de nombres de meses en español para los filtros
    meses_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df['mes_nombre'] = df['mes_num'].apply(lambda x: meses_es[x-1] if 1 <= x <= 12 else 'Desconocido')
    
    return df

df_original = load_data(DATA_PATH)

if df_original.empty:
    st.stop()
    
# 2. Sidebar (Filtros) ---
st.sidebar.header("Filtros de Análisis")

# Filtro 1: Año
all_years = sorted(df_original['anio'].unique(), reverse=True)
selected_years = st.sidebar.multiselect(
    "Seleccionar Año", 
    options=all_years, 
    default=all_years
)

# Filtro 2: Mes
all_months = sorted(df_original['mes_nombre'].unique(), key=lambda x: [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
].index(x) if x in ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'] else 99)

selected_months = st.sidebar.multiselect(
    "Seleccionar Mes", 
    options=all_months,
    default=all_months
)

# Filtro 3: Actividad Económica
all_activec = sorted(df_original['activec'].unique())
selected_activec = st.sidebar.multiselect(
    "Seleccionar Actividad Económica", 
    options=all_activec,
    default=all_activec
)

# Aplicar filtros
df_filtrado = df_original[
    (df_original['anio'].isin(selected_years)) & 
    (df_original['mes_nombre'].isin(selected_months)) &
    (df_original['activec'].isin(selected_activec))
]

# Mensaje de advertencia si no hay datos
if df_filtrado.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada. Ajuste los filtros.")
    st.stop()


# 3. Título Principal ---
st.title("Análisis Integral de Riesgos Laborales")
st.markdown("Dashboard de Monitoreo de Accidentalidad, Fatalidad y Cobertura (Variables Clave)")
st.markdown("---")

# 4. Panel A: Indicadores Clave (KPIs) ---
total_dep = df_filtrado['dep'].sum()
total_inc_at = df_filtrado['inc_at'].sum()
total_muertes = df_filtrado['muertes'].sum()

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Trabajadores Dependientes (VR5)", 
    value=f"{total_dep:,.0f}"
)

col2.metric(
    label="Incidentes de Trabajo (VR3)", 
    value=f"{total_inc_at:,.0f}"
)

col3.metric(
    label="Muertes por Riesgo Laboral (VR4)", 
    value=f"{total_muertes:,.0f}"
)

st.markdown("---")

# 5. Paneles B, C y D (Gráficos)
col_graph1, col_graph2 = st.columns(2)


# Panel B: Top 10 Actividades de Mayor Incidencia (Comparativa 1)
with col_graph1:
    st.subheader("Top 10 Actividades con Mayor Incidencia (VR3 vs. VR1)")
    
    # Agregación de datos
    df_top_incidencia = df_filtrado.groupby('activec')['inc_at'].sum().nlargest(10).reset_index()
    df_top_incidencia = df_top_incidencia.sort_values('inc_at', ascending=True)
    
    # Gráfico de Barras Horizontales
    fig1 = px.bar(
        df_top_incidencia, 
        x='inc_at', 
        y='activec', 
        orientation='h',
        labels={'inc_at': 'Suma de Incidentes de Trabajo', 'activec': 'Actividad Económica'},
        color='inc_at', 
        color_continuous_scale=px.colors.sequential.Viridis,
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("Interpretación: Muestra los sectores que concentran la mayor accidentalidad, indicando dónde priorizar la prevención.")


# Panel C: Evolución Anual de Incidencia y Muertes (Tendencia Temporal) ---
with col_graph2:
    st.subheader("Evolución Anual: Incidencia (VR3) y Muertes (VR4)")
    
    # Agregación de datos
    df_tendencia = df_filtrado.groupby('anio')[['inc_at', 'muertes']].sum().reset_index()
    
    # Gráfico de Líneas
    fig2 = px.line(
        df_tendencia, 
        x='anio', 
        y=['inc_at', 'muertes'], 
        labels={'value': 'Conteo Total', 'variable': 'Métrica', 'anio': 'Año'},
        height=400
    )
    fig2.update_layout(legend_title_text='Indicador')
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Interpretación: Permite ver la tendencia de riesgo a lo largo de los años, identificando picos o reducciones.")

# Nuevo Fila de Gráficos ---
st.markdown("---")
col_graph3, col_graph4 = st.columns(2)


# Panel D: Cobertura (VR5) vs. Incidencia (VR3) por Actividad ---
with col_graph3:
    st.subheader("Cobertura (VR5) y Fatalidad (VR4) por Departamento (VR2)")
    
    # Agregación de datos
    df_dpto = df_filtrado.groupby('dpto')[['muertes', 'dep']].sum().reset_index()
    df_dpto = df_dpto.sort_values('muertes', ascending=False).head(10)

    # Gráfico de Barras agrupadas o Plotly Bar
    fig3 = px.bar(
        df_dpto, 
        x='dpto', 
        y='muertes', 
        color='dep',
        labels={'muertes': 'Suma de Muertes', 'dpto': 'Departamento', 'dep': 'Trabajadores Dependientes (Cobertura)'},
        color_continuous_scale=px.colors.sequential.Reds,
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Interpretación: Muestra dónde se concentra la fatalidad (Muertes) y lo relaciona con el nivel de cobertura (Dep) en esa región.")

# Panel de Resumen Adicional (VR1 vs VR5) ---
with col_graph4:
    st.subheader("Distribución de la Cobertura (VR5) por Actividad (VR1)")
    
    # Agregación de datos
    df_cobertura = df_filtrado.groupby('activec')['dep'].sum().nlargest(10).reset_index()
    df_cobertura = df_cobertura.sort_values('dep', ascending=True)

    # Gráfico de barras
    fig4 = px.bar(
        df_cobertura, 
        x='dep', 
        y='activec', 
        orientation='h',
        labels={'dep': 'Suma de Trabajadores Dependientes', 'activec': 'Actividad Económica'},
        height=400
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("Interpretación: Es crucial para entender el tamaño de cada sector. Ayuda a normalizar el riesgo (riesgo por cada 1,000 empleados).")