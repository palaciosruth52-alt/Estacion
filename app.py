import streamlit as st
import math
from streamlit_geolocation import streamlit_geolocation

# Configuración
st.set_page_config(
    page_title="Estaciones Policiales Más Cercanas",
    page_icon="🚔",
    layout="centered"
)

# -----------------------------------------
# ESTACIONES POLICIALES
# -----------------------------------------

estaciones = [
    {
        "nombre": "Estación Policial Central",
        "latitud": 13.3000,
        "longitud": -87.1900
    },
    {
        "nombre": "Estación Policial Norte",
        "latitud": 13.3150,
        "longitud": -87.1800
    },
    {
        "nombre": "Estación Policial Sur",
        "latitud": 13.2850,
        "longitud": -87.2000
    },
    {
        "nombre": "Estación Policial Este",
        "latitud": 13.3050,
        "longitud": -87.1700
    },
    {
        "nombre": "Estación Policial Oeste",
        "latitud": 13.2950,
        "longitud": -87.2100
    }
]


# -----------------------------------------
# CALCULAR DISTANCIA
# -----------------------------------------

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
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(diferencia_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radio_tierra * c


# -----------------------------------------
# INTERFAZ
# -----------------------------------------

st.title("🚔 Estaciones Policiales Más Cercanas")

st.write(
    "Permite que la aplicación acceda a tu ubicación "
    "para encontrar las estaciones policiales más cercanas."
)

st.divider()

st.subheader("📍 Obtener mi ubicación")

st.write(
    "Presiona el botón y acepta el permiso de ubicación "
    "cuando tu navegador lo solicite."
)

location = streamlit_geolocation()

# -----------------------------------------
# VERIFICAR UBICACIÓN
# -----------------------------------------

if location:

    latitud = location.get("latitude")
    longitud = location.get("longitude")

    if latitud is not None and longitud is not None:

        st.success("✅ Ubicación obtenida correctamente")

        st.write(f"**Latitud:** {latitud}")
        st.write(f"**Longitud:** {longitud}")

        resultados = []

        # Calcular distancia hacia cada estación
        for estacion in estaciones:

            distancia = calcular_distancia(
                latitud,
                longitud,
                estacion["latitud"],
                estacion["longitud"]
            )

            resultados.append({
                "nombre": estacion["nombre"],
                "latitud": estacion["latitud"],
                "longitud": estacion["longitud"],
                "distancia": distancia
            })

        # Ordenar por distancia
        resultados.sort(
            key=lambda x: x["distancia"]
        )

        # Las 3 estaciones más cercanas
        estaciones_cercanas = resultados[:3]

        st.subheader(
            "🚔 Las 3 estaciones más cercanas"
        )

        for posicion, estacion in enumerate(
            estaciones_cercanas,
            start=1
        ):

            st.markdown(
                f"""
                ### {posicion}. 🚔 {estacion["nombre"]}

                📏 **Distancia:** {estacion["distancia"]:.2f} km

                📍 **Coordenadas:**  
                `{estacion["latitud"]}, {estacion["longitud"]}`
                """
            )

            st.divider()

        # -----------------------------------------
        # MAPA
        # -----------------------------------------

        st.subheader("🗺️ Ubicación")

        mapa_datos = [
            {
                "lat": latitud,
                "lon": longitud
            }
        ]

        for estacion in estaciones_cercanas:

            mapa_datos.append({
                "lat": estacion["latitud"],
                "lon": estacion["longitud"]
            })

        st.map(mapa_datos)

else:

    st.info(
        "📍 Presiona el botón de ubicación y "
        "acepta el permiso del navegador."
    )
