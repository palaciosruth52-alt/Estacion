import math
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Estaciones Policiales Cercanas", page_icon="🚨", layout="centered"
)

st.title("🚨 Estaciones Policiales Cercanas")
st.write(
    "Selecciona tu zona actual o ingresa tus coordenadas para encontrar las 3"
    " estaciones policiales más cercanas:"
)

# Lista de estaciones policiales de referencia
stations = [
    {
        "nombre": "Estación Policial Monjarás",
        "lat": 13.1320,
        "lon": -87.3850,
    },
    {
        "nombre": "Jefatura Policial Choluteca",
        "lat": 13.3032,
        "lon": -87.1939,
    },
    {
        "nombre": "Sub-Estación Marcovia",
        "lat": 13.3150,
        "lon": -87.3050,
    },
    {
        "nombre": "Puesto Policial San Lorenzo",
        "lat": 13.4150,
        "lon": -87.4420,
    },
    {
        "nombre": "Estación Policial El Triunfo",
        "lat": 13.0450,
        "lon": -87.0350,
    },
]


# Fórmula de Haversine para calcular la distancia en kilómetros
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


# Estado inicial de coordenadas
if "lat" not in st.session_state:
  st.session_state.lat = 13.3032
if "lon" not in st.session_state:
  st.session_state.lon = -87.1939

# 1. Selección rápida por zonas (Solución práctica y sin errores de GPS)
st.subheader("📍 Selección rápida por zona")
col_z1, col_z2, col_z3 = st.columns(3)

with col_z1:
  if st.button("🏙️ Choluteca"):
    st.session_state.lat = 13.3032
    st.session_state.lon = -87.1939
with col_z2:
  if st.button("🏖️ Marcovia"):
    st.session_state.lat = 13.3150
    st.session_state.lon = -87.3050
with col_z3:
  if st.button("🌊 San Lorenzo"):
    st.session_state.lat = 13.4150
    st.session_state.lon = -87.4420

col_z4, col_z5 = st.columns(2)
with col_z4:
  if st.button("🌴 Monjarás"):
    st.session_state.lat = 13.1320
    st.session_state.lon = -87.3850
with col_z5:
  if st.button("⭐ El Triunfo"):
    st.session_state.lat = 13.0450
    st.session_state.lon = -87.0350

st.markdown("---")

# 2. Opción de coordenadas manuales avanzadas
st.subheader("⚙️ O ingresa tus coordenadas exactas:")
col1, col2 = st.columns(2)
with col1:
  manual_lat = st.number_input(
      "Latitud", value=float(st.session_state.lat), format="%.4f"
  )
with col2:
  manual_lon = st.number_input(
      "Longitud", value=float(st.session_state.lon), format="%.4f"
  )

if st.button("🔍 Buscar Estaciones Cercanas", type="primary"):
  st.session_state.lat = manual_lat
  st.session_state.lon = manual_lon

# Cálculo y despliegue de resultados
lat_f = st.session_state.lat
lon_f = st.session_state.lon

st.markdown("---")
st.success(f"Coordenadas activas: Lat: {lat_f:.4f}, Lon: {lon_f:.4f}")

for st_info in stations:
  st_info["distancia_km"] = round(
      haversine(lat_f, lon_f, st_info["lat"], st_info["lon"]), 2
  )

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
