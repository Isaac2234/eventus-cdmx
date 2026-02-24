import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# 1. Configuración de Streamlit
st.set_page_config(page_title="Mapa AGEB CDMX", layout="wide")
st.title("🔥 Intensidad Criminal por AGEB (CDMX)")
st.markdown("Análisis de cruce espacial (Spatial Join) entre eventos delictivos y polígonos del INEGI.")

# 2. Función con caché para no repetir el cruce matemático pesado cada que recargas
@st.cache_data
def generar_mapa_ageb():
    # Cargar puntos
    df = pd.read_csv('eventos_con_coordenadas.csv')
    df = df.dropna(subset=['latitud', 'longitud'])
    gdf_eventos = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitud, df.latitud), crs="EPSG:4326"
    )

    # Cargar polígonos del INEGI (¡Asegúrate de que los 4 archivos 09a estén en GitHub!)
    agebs = gpd.read_file('09a.shp')
    agebs = agebs.to_crs(epsg=4326)

    # Cruce espacial
    eventos_en_ageb = gpd.sjoin(gdf_eventos, agebs, how="inner", predicate="within")
    conteo_ageb = eventos_en_ageb.groupby('CVE_AGEB').size().reset_index(name='total_delitos')

    # Unir datos y filtrar
    agebs_con_datos = agebs.merge(conteo_ageb, on='CVE_AGEB', how='left')
    agebs_con_datos['total_delitos'] = agebs_con_datos['total_delitos'].fillna(0)
    agebs_calientes = agebs_con_datos[agebs_con_datos['total_delitos'] > 0]

    return agebs_calientes

# 3. Mostrar estado de carga
with st.spinner('Realizando cruce espacial con datos del INEGI... ⚙️'):
    agebs_calientes = generar_mapa_ageb()

# 4. Dibujar el mapa
fig = px.choropleth_mapbox(
    agebs_calientes,
    geojson=agebs_calientes.geometry.__geo_interface__,
    locations=agebs_calientes.index,
    color='total_delitos',
    color_continuous_scale="Reds",
    mapbox_style="carto-darkmatter",
    zoom=10,
    center={"lat": 19.4326, "lon": -99.1332},
    opacity=0.7,
    hover_name='CVE_AGEB',
    hover_data={'total_delitos': True}
)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# 5. Imprimir en la página web
st.plotly_chart(fig, use_container_width=True)