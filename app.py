import math
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# Configuración de la página
st.set_page_config(
    page_title="Estaciones Policiales Cercanas", page_icon="🚨", layout="centered"
)

st.title("🚨 Estaciones Policiales Cercanas")
st.write(
    "Esta aplicación detecta tu ubicación actual automáticamente y encuentra"
    " las 3 estaciones policiales más cercanas."
)

# 1. Lista de al menos 5 estaciones policiales
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


# 2. Obtener la ubicación automática del dispositivo mediante GPS
st.subheader("📍 Tu Ubicación")
st.write("Haz clic en el botón para permitir el acceso a tu GPS:")
loc = streamlit_geolocation()

user_lat = None
user_lon = None

if loc and loc.get("latitude") and loc.get("longitude"):
  user_lat = loc["latitude"]
  user_lon = loc["longitude"]
  st.success(f"¡Ubicación detectada con éxito!")
else:
  st.info(
      "Esperando coordenadas de ubicación... (Presiona el botón del navegador"
      " si te pide permisos)."
  )

# 3 y 4. Si ya tenemos la ubicación, calcular y mostrar las más cercanas
if user_lat and user_lon:
  # Calcular distancias
  for st_info in stations:
    st_info["distancia_km"] = round(
        haversine(user_lat, user_lon, st_info["lat"], st_info["lon"]), 2
    )

  # Ordenar de menor a mayor distancia y seleccionar el Top 3
  sorted_stations = sorted(stations, key=lambda x: x["distancia_km"])
  top_3 = sorted_stations[:3]

  st.markdown("---")
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

  # 5. Mostrar un mapa interactivo con las estaciones cercanas
  st.markdown("---")
  st.subheader("🗺️ Mapa de Ubicaciones")
  # Preparamos los datos para st.map (necesita columnas 'lat' y 'lon')
  map_data = [{"lat": user_lat, "lon": user_lon}] + [
      {"lat": s["lat"], "lon": s["lon"]} for s in top_3
  ]
  st.map(map_data)
