import streamlit as st
import requests
import math
from streamlit_geolocation import streamlit_geolocation

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="Estaciones Policiales Más Cercanas",
    page_icon="🚔",
    layout="centered"
)

st.title("🚔 Estaciones Policiales Más Cercanas")

st.write(
    "Obtén tu ubicación mediante el GPS de tu dispositivo "
    "y encuentra las estaciones policiales más cercanas."
)

st.divider()


# --------------------------------------------------
# FUNCIÓN PARA CALCULAR DISTANCIA
# --------------------------------------------------

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


# --------------------------------------------------
# BUSCAR ESTACIONES POLICIALES
# --------------------------------------------------

def buscar_estaciones(latitud, longitud):

    # Radio de búsqueda: 50 kilómetros
    radio = 50000

    consulta = f"""
    [out:json][timeout:30];

    (
      node["amenity"="police"](around:{radio},{latitud},{longitud});
      way["amenity"="police"](around:{radio},{latitud},{longitud});
      relation["amenity"="police"](around:{radio},{latitud},{longitud});
    );

    out center tags;
    """

    servidores = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]

    for servidor in servidores:

        try:

            respuesta = requests.post(
                servidor,
                data=consulta,
                timeout=40
            )

            respuesta.raise_for_status()

            datos = respuesta.json()

            estaciones = []

            for elemento in datos.get("elements", []):

                tags = elemento.get("tags", {})

                # Coordenadas para nodos
                if "lat" in elemento and "lon" in elemento:

                    lat_estacion = elemento["lat"]
                    lon_estacion = elemento["lon"]

                # Coordenadas para edificios/áreas
                elif "center" in elemento:

                    lat_estacion = elemento["center"]["lat"]
                    lon_estacion = elemento["center"]["lon"]

                else:
                    continue

                nombre = (
                    tags.get("name")
                    or tags.get("official_name")
                    or "Estación policial"
                )

                # Información adicional
                ciudad = (
                    tags.get("addr:city")
                    or tags.get("addr:town")
                    or tags.get("addr:village")
                    or "Ubicación no especificada"
                )

                departamento = (
                    tags.get("addr:state")
                    or ""
                )

                distancia = calcular_distancia(
                    latitud,
                    longitud,
                    lat_estacion,
                    lon_estacion
                )

                estaciones.append({
                    "nombre": nombre,
                    "ciudad": ciudad,
                    "departamento": departamento,
                    "latitud": lat_estacion,
                    "longitud": lon_estacion,
                    "distancia": distancia
                })

            return estaciones

        except Exception:
            continue

    return []


# --------------------------------------------------
# OBTENER GPS
# --------------------------------------------------

st.subheader("📍 Mi ubicación")

st.write(
    "Presiona el botón de ubicación y permite el acceso "
    "al GPS cuando el navegador lo solicite."
)

ubicacion = streamlit_geolocation()


# --------------------------------------------------
# MOSTRAR RESULTADOS
# --------------------------------------------------

if ubicacion:

    latitud = ubicacion.get("latitude")
    longitud = ubicacion.get("longitude")

    if latitud is not None and longitud is not None:

        st.success("✅ Ubicación obtenida correctamente")

        st.write(
            f"**Tu ubicación:** "
            f"{latitud:.6f}, {longitud:.6f}"
        )

        with st.spinner(
            "🔎 Buscando estaciones policiales cercanas..."
        ):

            estaciones = buscar_estaciones(
                latitud,
                longitud
            )

        if estaciones:

            # Ordenar de menor a mayor distancia
            estaciones.sort(
                key=lambda x: x["distancia"]
            )

            # Eliminar posibles duplicados
            estaciones_unicas = []

            for estacion in estaciones:

                duplicada = False

                for existente in estaciones_unicas:

                    distancia_entre_estaciones = calcular_distancia(
                        estacion["latitud"],
                        estacion["longitud"],
                        existente["latitud"],
                        existente["longitud"]
                    )

                    if distancia_entre_estaciones < 0.05:
                        duplicada = True
                        break

                if not duplicada:
                    estaciones_unicas.append(estacion)

            # Obtener las 3 más cercanas
            estaciones_cercanas = estaciones_unicas[:3]

            st.divider()

            st.subheader(
                "🚔 Las 3 estaciones más cercanas"
            )

            # ------------------------------------------
            # MOSTRAR ESTACIONES
            # ------------------------------------------

            for posicion, estacion in enumerate(
                estaciones_cercanas,
                start=1
            ):

                st.markdown(
                    f"## {posicion}. 🚔 {estacion['nombre']}"
                )

                st.write(
                    f"📍 **Lugar:** "
                    f"{estacion['ciudad']}"
                )

                if estacion["departamento"]:

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

                # Link para abrir ubicación
                url_mapa = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={estacion['latitud']},"
                    f"{estacion['longitud']}"
                )

                st.link_button(
                    "🗺️ Ver dónde queda",
                    url_mapa
                )

                st.divider()

            # ------------------------------------------
            # MAPA
            # ------------------------------------------

            st.subheader("🗺️ Mapa")

            puntos = []

            # Ubicación del usuario
            puntos.append({
                "lat": latitud,
                "lon": longitud
            })

            # Estaciones
            for estacion in estaciones_cercanas:

                puntos.append({
                    "lat": estacion["latitud"],
                    "lon": estacion["longitud"]
                })

            st.map(puntos)

        else:

            st.warning(
                "⚠️ No se encontraron estaciones policiales "
                "en un radio de 50 km."
            )

    else:

        st.warning(
            "No fue posible obtener las coordenadas."
        )

else:

    st.info(
        "📍 Presiona el botón de ubicación para comenzar."
    )
