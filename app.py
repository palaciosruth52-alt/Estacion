import math
import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="Estaciones Policiales Cercanas", page_icon="🚨", layout="centered"
)

st.title("🚨 Estaciones Policiales Cercanas")
st.write(
    "Selecciona una opción para encontrar las 3 estaciones policiales más"
    " cercanas:"
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


# Manejo de estados para las coordenadas
if "lat" not in st.session_state:
  st.session_state.lat = None
if "lon" not in st.session_state:
  st.session_state.lon = None

# Opción 1: Botón para obtener ubicación por GPS automáticamente mediante un botón estilizado
st.subheader("Opción 1: Usar GPS del dispositivo")
geo_button_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        .btn-geo {
            background-color: #059669;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            font-family: sans-serif;
        }
        .btn-geo:hover { background-color: #047857; }
    </style>
</head>
<body>
    <button class="btn-geo" onclick="getLocation()">📍 Obtener mi ubicación actual</button>
    <p id="msg" style="font-family: sans-serif; font-size: 13px; color: #555; text-align: center; margin-top: 8px;"></p>
    <script>
        function getLocation() {
            document.getElementById("msg").innerText = "Obteniendo ubicación...";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        document.getElementById("msg").innerText = "¡Ubicación lista!";
                        const url = new URL(window.parent.location.href);
                        url.searchParams.set('lat', lat);
                        url.searchParams.set('lon', lon);
                        window.parent.location.href = url.href;
                    },
                    (error) => {
                        document.getElementById("msg").innerText = "Error al obtener ubicación. Revisa los permisos.";
                    },
                    {timeout: 10000}
                );
            } else {
                document.getElementById("msg").innerText = "Geolocalización no soportada por el navegador.";
            }
        }
    </script>
</body>
</html>
"""
components.html(geo_button_code, height=95)

# Capturar parámetros de la URL si se usó el botón de GPS
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
  st.session_state.lat = float(query_params["lat"])
  st.session_state.lon = float(query_params["lon"])

st.markdown("---")
st.subheader("O Opción 2: Ingresar coordenadas de forma manual")
col1, col2 = st.columns(2)
with col1:
  manual_lat = st.number_input(
      "Latitud", value=st.session_state.lat or 13.3032, format="%.4f"
  )
with col2:
  manual_lon = st.number_input(
      "Longitud", value=st.session_state.lon or -87.1939, format="%.4f"
  )

if st.button("🔍 Buscar Estaciones Cercanas", type="primary"):
  st.session_state.lat = manual_lat
  st.session_state.lon = manual_lon

# Mostrar resultados si ya se cuenta con coordenadas válidas
if st.session_state.lat is not None and st.session_state.lon is not None:
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
