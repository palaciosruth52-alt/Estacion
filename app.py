import csv
import math
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Estaciones Policiales de Honduras",
    page_icon="🚨",
    layout="centered",
)

st.title("🚨 Estaciones Policiales en Honduras")
st.write(
    "Selecciona una zona rápida o ingresa tus coordenadas. El sistema"
    " analizará todo el listado nacional y mostrará estrictamente las **3"
    " estaciones más cercanas**."
)


# Cargar estaciones desde el CSV ampliado
@st.cache_data
def cargar_estaciones():
  stations = []
  try:
    with open("stations.csv", mode="r", encoding="utf-8") as archivo:
      lector = csv.DictReader(archivo)
      for fila inlector:
        stations.append({
            "nombre": fila["nombre"],
            "lat": float(fila["lat"]),
            "lon": float(fila["lon"]),
        })
  except FileNotFoundError:
    st.error("No se encontró el archivo 'stations.csv' en el repositorio.")
  return stations


stations = cargar_estaciones()


# Fórmula de Haversine para calcular distancia exacta en kilómetros
def haversine(lat1, lon1, lat2, lon2):
  R = 6371.0
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(math.radians(lat1))
      * math.cos(math.radians(lat2))
      * math.sin(dlon / 2) ** 2
  )
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R * c


# Estado inicial de coordenadas (Por defecto Choluteca)
if "lat" not in st.session_state:
  st.session_state.lat = 13.3032
if "lon" not in st.session_state:
  st.session_state.lon = -87.1939

# Botones de selección rápida
st.subheader("📍 Selección rápida por ciudad")
col1, col2, col3 = st.columns(3)

with col1:
  if st.button("🏙️ Tegucigalpa"):
    st.session_state.lat = 14.0818
    st.session_state.lon = -87.2068
with col2:
  if st.button("🏭 San Pedro Sula"):
    st.session_state.lat = 15.5036
    st.session_state.lon = -88.0250
with col3:
  if st.button("☀️ Choluteca"):
    st.session_state.lat = 13.3032
    st.session_state.lon = -87.1939

col4, col5 = st.columns(2)
with col4:
  if st.button("🌴 La Ceiba"):
    st.session_state.lat = 15.7593
    st.session_state.lon = -86.7808
with col5:
  if st.button("🏕️ Comayagua"):
    st.session_state.lat = 14.4556
    st.session_state.lon = -87.6433

st.markdown("---")

# Coordenadas manuales
st.subheader("⚙️ O ingresa tus coordenadas exactas:")
c_col1, c_col2 = st.columns(2)
with c_col1:
  manual_lat = st.number_input(
      "Latitud", value=float(st.session_state.lat), format="%.4f"
  )
with c_col2:
  manual_lon = st.number_input(
      "Longitud", value=float(st.session_state.lon), format="%.4f"
  )

if st.button("🔍 Buscar Estaciones Cercanas", type="primary"):
  st.session_state.lat = manual_lat
  st.session_state.lon = manual_lon

lat_f = st.session_state.lat
lon_f = st.session_state.lon

st.markdown("---")
st.success(f"Coordenadas activas: Lat: {lat_f:.4f}, Lon: {lon_f:.4f}")

if stations:
  for st_info in stations:
    st_info["distancia_km"] = round(
        haversine(lat_f, lon_f, st_info["lat"], st_info["lon"]), 2
    )

  # Ordenar todo el listado masivo y seleccionar estrictamente las 3 más cercanas
  sorted_stations = sorted(stations, key=lambda x: x["distancia_km"])
  top_3 = sorted_stations[:3]

  st.subheader("🏆 Top 3 Estaciones Policiales Más Cercanas")
  for i, station in enumerate(top_3):
    st.markdown(
        f"""
        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border-left: 5px solid #2563eb; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #1e3a8a;">#{i+1} - {station['nombre']}</h4>
            <p style="margin: 5px 0 0 0; color: #333;">Distancia aproximada: <b>{station['distancia_km']} km</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.subheader("🗺️ Mapa de Ubicaciones")
  map_data = [{"lat": lat_f, "lon": lon_f}] + [
      {"lat": s["lat"], "lon": s["lon"]} for s in top_3
  ]
  st.map(map_data)
