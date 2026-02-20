import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración principal de la página
st.set_page_config(page_title="Inseguridad CDMX", layout="wide")
st.title("🗺️ Mapa Interactivo de Eventos de Seguridad en CDMX")
st.markdown("Análisis geoespacial extraído automáticamente de reportes policiales.")

# 2. Carga y limpieza de datos (con caché para que cargue rápido)
@st.cache_data
def load_data():
    # Leer el archivo que generamos
    df = pd.read_csv('eventos_con_coordenadas.csv')
    
    # Quitar los que no tienen coordenadas
    df = df.dropna(subset=['latitud', 'longitud'])
    
    # Arreglar la fecha para poder filtrar por año
    df['fecha_evento'] = pd.to_datetime(df['fecha_evento'], errors='coerce')
    df['Año'] = df['fecha_evento'].dt.year.fillna(0).astype(int)
    
    # Filtrar solo años válidos (por si se coló algún error del PDF)
    df = df[df['Año'] > 2000]
    return df

df = load_data()

# 3. Barra Lateral (Filtros interactivos)
st.sidebar.header("Filtros de Búsqueda")

# Filtro de Año
anios_disponibles = sorted(df['Año'].unique())
anio_seleccionado = st.sidebar.selectbox("Selecciona el Año:", anios_disponibles, index=len(anios_disponibles)-1)

# Filtro de Delito
delitos_disponibles = df['categoria_delito'].unique().tolist()
# Por defecto seleccionamos los 3 primeros para no saturar el mapa de inicio
delitos_seleccionados = st.sidebar.multiselect("Tipo de Delito:", delitos_disponibles, default=delitos_disponibles[:3])

# 4. Aplicar los filtros a los datos
df_filtrado = df[(df['Año'] == anio_seleccionado) & (df['categoria_delito'].isin(delitos_seleccionados))]

# 5. Dibujar el Mapa
if not df_filtrado.empty:
    st.write(f"Mostrando **{len(df_filtrado)}** eventos geolocalizados.")
    
    fig = px.scatter_mapbox(
        df_filtrado,
        lat="latitud",
        lon="longitud",
        color="categoria_delito",      # Colores distintos por delito
        hover_name="delito",           # Título al pasar el mouse
        hover_data={
            "actores_criminales": True,
            "alcaldia_inferida": True,
            "fecha_evento": True,
            "latitud": False,          # Ocultamos lat/lon en el popup para que se vea limpio
            "longitud": False,
            "Año": False
        },
        zoom=10,
        center={"lat": 19.4326, "lon": -99.1332}, # Coordenadas del Zócalo de CDMX
        mapbox_style="carto-darkmatter",          # Tema oscuro (resaltan más los puntos)
        height=650
    )
    
    # Quitar márgenes blancos alrededor del mapa
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No se encontraron eventos para los filtros seleccionados. Intenta cambiar el año o los delitos.")