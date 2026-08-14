import math
import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="Estaciones Policiales Cercanas", page_icon="🚨", layout="centered"
)

st.title("🚨 Estaciones Policiales Cercanas")
st.write(
    "Esta aplicación detecta tu ubicación actual automáticamente mediante GPS y"
    " encuentra las 3 estaciones policiales más cercanas."
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


# Componente HTML + JS para capturar la geolocalización del navegador automáticamente
geolocation_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <div id="status" style="font-family: sans-serif; color: #555; font-size: 14px; text-align: center; padding: 10px;">
        🔄 Solicitando acceso al GPS del dispositivo...
    </div>

    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError, {timeout: 10000, enableHighAccuracy: true});
            } else {
                document.getElementById("status").innerHTML = "❌ La geolocalización no es soportada por este navegador.";
            }
        }

        function showPosition(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            document.getElementById("status").innerHTML = "✅ ¡Ubicación detectada con éxito!";
            
            // Enviar coordenadas a Streamlit mediante URL parameters o recarga con query params
            const url = new URL(window.parent.location.href);
            url.searchParams.set('lat', lat);
            url.searchParams.set('lon', lon);
            
            if (window.parent.location.href !== url.href) {
                window.parent.location.href = url.href;
            }
        }

        function showError(error) {
            let msg = "Error desconocido.";
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    msg = "❌ Permiso de ubicación denegado. Por favor actívelo en su navegador.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    msg = "❌ Información de ubicación no disponible.";
                    break;
                case error.TIMEOUT:
                    msg = "❌ Tiempo de espera agotado para obtener la ubicación.";
                    break;
            }
            document.getElementById("status").innerHTML = msg;
        }

        getLocation();
    </script>
</body>
</html>
"""

# Renderizar el componente de ubicación
components.html(geolocation_code, height=60)

# Obtener los parámetros de la URL enviados por JavaScript
query_params = st.query_params
user_lat = query_params.get("lat")
user_lon = query_params.get("lon")

if user_lat and user_lon:
  try:
    lat_f = float(user_lat)
    lon_f = float(user_lon)

    st.success(
        f"Coordenadas actuales detectadas: Lat: {lat_f:.4f}, Lon: {lon_f:.4f}"
    )

    # Calcular distancias
    for st_info in stations:
      st_info["distancia_km"] = round(
          haversine(lat_f, lon_f, st_info["lat"], st_info["lon"]), 2
      )

    # Ordenar y seleccionar el Top 3
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

    # Mostrar mapa interactivo
    st.markdown("---")
    st.subheader("🗺️ Mapa de Ubicaciones")
    map_data = [{"lat": lat_f, "lon": lon_f}] + [
        {"lat": s["lat"], "lon": s["lon"]} for s in top_3
    ]
    st.map(map_data)

  except ValueError:
    st.error("Coordenadas inválidas.")
else:
  st.info(
      "Por favor, permita el acceso a su ubicación cuando el navegador lo"
      " solicite para calcular las estaciones cercanas."
  )
