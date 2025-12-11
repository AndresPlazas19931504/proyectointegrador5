# Importamos las librerías necesarias.
import streamlit as st       # Librería principal para crear la aplicación web interactiva.
import pandas as pd          # Para el manejo de datos.
import plotly.express as px  # Para crear gráficos interactivos y visualizaciones.
import os                    # Para operaciones del sistema operativo, como manejo de rutas.

# Define la ruta donde se espera encontrar el archivo de datos procesado ('dataset_enriquecido.csv').
# La lógica 'os.path.dirname(__file__)' permite encontrar la ruta relativa desde la ubicación del script.
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset_enriquecido.csv')

# --- 1. Configuración de la Aplicación y Carga de Datos ---

# Configuración inicial de la página de Streamlit.
st.set_page_config(
    page_title="Dashboard de Riesgos Laborales", # Título de la pestaña del navegador
    layout="wide",                              # Usa todo el ancho disponible de la pantalla
    initial_sidebar_state="expanded"            # Mantiene el panel lateral abierto al inicio
)

# Usa caché de Streamlit (@st.cache_data) para que la función se ejecute una sola vez,
# a menos que la ruta del archivo cambie. Esto optimiza el rendimiento.
@st.cache_data
def load_data(path):
    # Carga y prepara el dataset enriquecido.
    if not os.path.exists(path):
        # Muestra un error si el archivo de datos no existe.
        st.error(f"Error: No se encontró el archivo de datos en {path}. Asegúrese de ejecutar '02_enriquecimiento_eda.ipynb' primero.")
        return pd.DataFrame()
        
    df = pd.read_csv(path)
    # Convierte la columna 'fecha' al tipo de dato correcto (datetime).
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['anio'] = df['fecha'].dt.year
    df['mes_num'] = df['fecha'].dt.month
    
    # Crea una columna con los nombres de los meses en español para usarlos en los filtros.
    meses_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df['mes_nombre'] = df['mes_num'].apply(lambda x: meses_es[x-1] if 1 <= x <= 12 else 'Desconocido')
    
    return df

# Carga el DataFrame principal.
df_original = load_data(DATA_PATH)

# Detiene la ejecución si los datos no se cargaron correctamente.
if df_original.empty:
    st.stop()
    
# --- 2. Sidebar (Filtros) ---

st.sidebar.header("Filtros de Análisis")

# Filtro 1: Permite seleccionar uno o varios años.
all_years = sorted(df_original['anio'].unique(), reverse=True)
selected_years = st.sidebar.multiselect(
    "Seleccionar Año", 
    options=all_years, 
    default=all_years # Por defecto, selecciona todos los años.
)

# Filtro 2: Permite seleccionar uno o varios meses.
# Se ordena la lista de meses para que aparezcan en orden cronológico.
all_months = sorted(df_original['mes_nombre'].unique(), key=lambda x: [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
].index(x) if x in ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'] else 99)

selected_months = st.sidebar.multiselect(
    "Seleccionar Mes", 
    options=all_months,
    default=all_months # Por defecto, selecciona todos los meses.
)

# Filtro 3: Permite seleccionar una o varias actividades económicas.
all_activec = sorted(df_original['activec'].unique())
selected_activec = st.sidebar.multiselect(
    "Seleccionar Actividad Económica", 
    options=all_activec,
    default=all_activec # Por defecto, selecciona todas las actividades.
)

# Aplicar los filtros al DataFrame.
df_filtrado = df_original[
    (df_original['anio'].isin(selected_years)) & 
    (df_original['mes_nombre'].isin(selected_months)) &
    (df_original['activec'].isin(selected_activec))
]

# Mensaje de advertencia si el filtrado no devuelve datos.
if df_filtrado.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada. Ajuste los filtros.")
    st.stop()


# --- 3. Título Principal y Encabezado ---

st.title("Análisis Integral de Riesgos Laborales")
st.markdown("Dashboard de Monitoreo de Accidentalidad, Fatalidad y Cobertura (Variables Clave)")
st.markdown("---")

# --- 4. Panel A: Indicadores Clave (KPIs) ---

# Calcula las métricas principales (suma total para el periodo y filtros seleccionados).
total_dep = df_filtrado['dep'].sum()         # Suma de Trabajadores Dependientes
total_inc_at = df_filtrado['inc_at'].sum()   # Suma de Incidentes de Trabajo
total_muertes = df_filtrado['muertes'].sum() # Suma de Muertes por Riesgo Laboral

# Divide el espacio en tres columnas para mostrar los KPIs.
col1, col2, col3 = st.columns(3)

# Muestra el valor de cada KPI con formato de miles.
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

# --- 5. Paneles B, C, D y E (Gráficos) ---

# Primera fila de gráficos.
col_graph1, col_graph2 = st.columns(2)


# Panel B: Top 10 Actividades de Mayor Incidencia ---
with col_graph1:
    st.subheader("Top 10 Actividades con Mayor Incidencia (VR3 vs. VR1)")
    
    # Agrupa por actividad y suma los incidentes (VR3), seleccionando el top 10.
    df_top_incidencia = df_filtrado.groupby('activec')['inc_at'].sum().nlargest(10).reset_index()
    df_top_incidencia = df_top_incidencia.sort_values('inc_at', ascending=True)
    
    # Crea un gráfico de barras horizontales interactivo con Plotly.
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
    # 


# Panel C: Evolución Anual de Incidencia y Muertes (Tendencia Temporal) ---
with col_graph2:
    st.subheader("Evolución Anual: Incidencia (VR3) y Muertes (VR4)")
    
    # Agrupa por año y suma los incidentes y las muertes.
    df_tendencia = df_filtrado.groupby('anio')[['inc_at', 'muertes']].sum().reset_index()
    
    # Crea un gráfico de líneas para mostrar la tendencia a lo largo de los años.
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
    # 

# Nueva Fila de Gráficos.
st.markdown("---")
col_graph3, col_graph4 = st.columns(2)


# Panel D: Cobertura (VR5) y Fatalidad (VR4) por Departamento (VR2) ---
with col_graph3:
    st.subheader("Cobertura (VR5) y Fatalidad (VR4) por Departamento (VR2)")
    
    # Agrupa por departamento y suma las muertes (VR4) y la cobertura (VR5).
    df_dpto = df_filtrado.groupby('dpto')[['muertes', 'dep']].sum().reset_index()
    df_dpto = df_dpto.sort_values('muertes', ascending=False).head(10) # Top 10 por muertes.

    # Gráfico de barras que usa el color para representar la cobertura (dep).
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
    # 

# Panel E: Distribución de la Cobertura (VR5) por Actividad ---
with col_graph4:
    st.subheader("Distribución de la Cobertura (VR5) por Actividad (VR1)")
    
    # Agrupa por actividad y suma la cobertura (VR5), seleccionando el top 10.
    df_cobertura = df_filtrado.groupby('activec')['dep'].sum().nlargest(10).reset_index()
    df_cobertura = df_cobertura.sort_values('dep', ascending=True)

    # Gráfico de barras horizontales de la cobertura.
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
    