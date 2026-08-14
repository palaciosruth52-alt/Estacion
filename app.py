import streamlit as st
import pandas as pd
import math
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(
    page_title="Estaciones Policiales Más Cercanas",
    page_icon="🚔",
    layout="centered"
)

st.title("🚔 Estaciones Policiales Más Cercanas")

st.write(
    "Obtén tu ubicación mediante el GPS de tu dispositivo "
    "y encuentra las tres estaciones policiales más cercanas."
)

st.divider()

@st.cache_data
def cargar_estaciones():

    datos = pd.read_csv("estaciones.csv")

    return datos


try:

    estaciones = cargar_estaciones()

except Exception as error:

    st.error(
        "❌ No se pudo cargar el archivo estaciones.csv"
    )

    st.stop()

def calcular_distancia(lat1, lon1, lat2, lon2):

    radio_tierra = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    diferencia_lat = lat2 - lat1
    diferencia_lon = lon2 - lon1

    a = (
        math.sin(diferencia_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(diferencia_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    distancia = radio_tierra * c

    return distancia

st.subheader("📍 Obtener mi ubicación")

st.write(
    "Presiona el botón y permite el acceso a tu ubicación "
    "cuando el navegador lo solicite."
)

ubicacion = streamlit_geolocation()

if ubicacion:

    latitud = ubicacion.get("latitude")
    longitud = ubicacion.get("longitude")

    if latitud is not None and longitud is not None:

        st.success("✅ Ubicación obtenida correctamente")

        st.write(
            f"**Tu latitud:** {latitud:.6f}"
        )

        st.write(
            f"**Tu longitud:** {longitud:.6f}"
        )

        resultados = []

        for _, estacion in estaciones.iterrows():

            distancia = calcular_distancia(
                latitud,
                longitud,
                float(estacion["latitud"]),
                float(estacion["longitud"])
            )

            resultados.append({
                "nombre": estacion["nombre"],
                "departamento": estacion["departamento"],
                "municipio": estacion["municipio"],
                "ubicacion": estacion["ubicacion"],
                "latitud": float(estacion["latitud"]),
                "longitud": float(estacion["longitud"]),
                "distancia": distancia
            })

        resultados.sort(
            key=lambda x: x["distancia"]
        )

        estaciones_cercanas = resultados[:3]

        st.divider()

        st.subheader(
            "🚔 Las 3 estaciones más cercanas"
        )

        for posicion, estacion in enumerate(
            estaciones_cercanas,
            start=1
        ):

            st.markdown(
                f"## {posicion}. 🚔 {estacion['nombre']}"
            )

            st.write(
                f"📍 **Ubicación:** "
                f"{estacion['ubicacion']}"
            )

            st.write(
                f"🏙️ **Municipio:** "
                f"{estacion['municipio']}"
            )

            st.write(
                f"🏛️ **Departamento:** "
                f"{estacion['departamento']}"
            )

            st.write(
                f"📏 **Distancia:** "
                f"{estacion['distancia']:.2f} km"
            )

            st.write(
                f"🌎 **Coordenadas:** "
                f"{estacion['latitud']:.6f}, "
                f"{estacion['longitud']:.6f}"
            )

            enlace_mapa = (
                "https://www.google.com/maps/search/?api=1"
                f"&query={estacion['latitud']},"
                f"{estacion['longitud']}"
            )

            st.link_button(
                "🗺️ Ver dónde queda",
                enlace_mapa
            )

            st.divider()

        st.subheader("🗺️ Mapa")

        puntos_mapa = []

        # Ubicación del usuario
        puntos_mapa.append({
            "lat": latitud,
            "lon": longitud
        })

        # Estaciones cercanas
        for estacion in estaciones_cercanas:

            puntos_mapa.append({
                "lat": estacion["latitud"],
                "lon": estacion["longitud"]
            })

        st.map(puntos_mapa)

    else:

        st.warning(
            "⚠️ No fue posible obtener tu ubicación."
        )

else:

    st.info(
        "📍 Presiona el botón de ubicación y "
        "acepta el permiso del navegador."
    )

