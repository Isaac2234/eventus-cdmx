import pandas as pd
import geopandas as gpd
import plotly.express as px

# --- 1. CARGAR TUS DELITOS (PUNTOS) ---
print("📍 Cargando eventos delictivos...")
df = pd.read_csv('eventos_con_coordenadas.csv')
df = df.dropna(subset=['latitud', 'longitud'])

# Convertir tu Excel/CSV a un formato Geoespacial
gdf_eventos = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df.longitud, df.latitud), 
    crs="EPSG:4326" # EPSG:4326 significa Latitud/Longitud de GPS estándar
)

# --- 2. CARGAR EL MAPA DEL INEGI (POLÍGONOS) ---
print("🗺️ Cargando AGEBs del INEGI...")
# Asegúrate de que los archivos 09a.shp, .shx, .dbf y .prj estén en la misma carpeta
agebs = gpd.read_file('09a.shp')

# Homologamos el mapa del INEGI a las mismas coordenadas de Google Maps
agebs = agebs.to_crs(epsg=4326) 

# --- 3. EL CRUCE MATEMÁTICO (SPATIAL JOIN) ---
print("⚙️ Cruzando delitos con polígonos del INEGI...")
# Esto verifica en qué AGEB cayó cada uno de los delitos
eventos_en_ageb = gpd.sjoin(gdf_eventos, agebs, how="inner", predicate="within")

# Contamos cuántos delitos hubo en cada AGEB
conteo_ageb = eventos_en_ageb.groupby('CVE_AGEB').size().reset_index(name='total_delitos')

# Unimos el conteo de vuelta al mapa de polígonos
agebs_con_datos = agebs.merge(conteo_ageb, on='CVE_AGEB', how='left')
agebs_con_datos['total_delitos'] = agebs_con_datos['total_delitos'].fillna(0)

# Para no saturar el navegador, graficamos solo los AGEBs que tuvieron al menos 1 delito
agebs_calientes = agebs_con_datos[agebs_con_datos['total_delitos'] > 0]

# --- 4. DIBUJAR EL MAPA ---
print("🎨 Generando mapa coroplético...")
fig = px.choropleth_mapbox(
    agebs_calientes,
    geojson=agebs_calientes.geometry.__geo_interface__,
    locations=agebs_calientes.index,
    color='total_delitos',
    color_continuous_scale="Reds",     # De blanco a rojo oscuro
    mapbox_style="carto-darkmatter",
    zoom=10,
    center={"lat": 19.4326, "lon": -99.1332},
    opacity=0.7,
    hover_name='CVE_AGEB',
    hover_data={'total_delitos': True},
    title="Intensidad Criminal por AGEB (CDMX)"
)

fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

# Guardar
fig.write_html("Mapa_AGEB_Calor.html")
print("✅ ¡LISTO! Abre el archivo 'Mapa_AGEB_Calor.html' en tu navegador.")