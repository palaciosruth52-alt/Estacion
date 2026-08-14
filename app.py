import math
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Lista requerida de estaciones policiales
stations = [
    {
        "id": 1,
        "nombre": "Estación Policial Monjarás",
        "lat": 13.1320,
        "lon": -87.3850,
    },
    {
        "id": 2,
        "nombre": "Jefatura Policial Choluteca",
        "lat": 13.3032,
        "lon": -87.1939,
    },
    {
        "id": 3,
        "nombre": "Sub-Estación Marcovia",
        "lat": 13.3150,
        "lon": -87.3050,
    },
    {
        "id": 4,
        "nombre": "Puesto Policial San Lorenzo",
        "lat": 13.4150,
        "lon": -87.4420,
    },
    {
        "id": 5,
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


@app.route("/")
def index():
  return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Estaciones Policiales Cercanas</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 90vh; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 450px; text-align: center; }
            h2 { color: #1e3a8a; margin-bottom: 10px; }
            p.subtitle { color: #666; font-size: 14px; margin-bottom: 20px; }
            .results { margin-top: 20px; text-align: left; }
            .station-card { background: #f8fafc; border-left: 5px solid #2563eb; padding: 12px 15px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .station-card strong { color: #1e3a8a; }
            button { background: #059669; color: white; border: none; padding: 10px 15px; border-radius: 5px; font-size: 14px; cursor: pointer; font-weight: bold; margin-top: 10px; width: 100%; }
            button:hover { background: #047857; }
            .loader { border: 4px solid #f3f3f3; border-top: 4px solid #2563eb; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🚨 Estaciones Policiales</h2>
            <p class="subtitle">Buscando las estaciones más cercanas a tu posición actual...</p>
            <div class="results" id="results">
                <div class="loader"></div>
                <p style="text-align:center; color:#666;">Solicitando acceso al GPS...</p>
            </div>
        </div>

        <script>
            // Detectar la ubicación automáticamente al cargar la página
            window.onload = function() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            buscarEstacionesCercanas(lat, lon);
                        },
                        (error) => {
                            document.getElementById('results').innerHTML = `
                                <p style="color:red; text-align:center;">No pudimos obtener tu ubicación automáticamente. Por favor, permite el acceso a la ubicación en tu navegador y recarga la página.</p>
                                <button onclick="location.reload()">Reintentar</button>
                            `;
                        },
                        { timeout: 10000, enableHighAccuracy: true }
                    );
                } else {
                    document.getElementById('results').innerHTML = '<p style="color:red; text-align:center;">Tu navegador no soporta geolocalización.</p>';
                }
            };

            async function buscarEstacionesCercanas(lat, lon) {
                const resultsDiv = document.getElementById('results');

                try {
                    const response = await fetch(`/api/cercanas?lat=${lat}&lon=${lon}`);
                    const data = await response.json();

                    if(data.length === 0) {
                        resultsDiv.innerHTML = '<p>No se encontraron estaciones disponibles.</p>';
                        return;
                    }

                    let html = `<h3 style="color: #333; font-size: 16px; margin-bottom: 5px;">Top 3 Estaciones Más Cercanas:</h3>
                                <p style="font-size: 12px; color: #666; margin-bottom: 15px;">Ubicación detectada: (${lat.toFixed(4)}, ${lon.toFixed(4)})</p>`;
                    
                    data.forEach((st, index) => {
                        html += `<div class="station-card">
                            <strong>#${index + 1} - ${st.nombre}</strong><br>
                            Distancia: <strong>${st.distancia_km} km</strong><br>
                        </div>`;
                    });

                    html += `<button onclick="location.reload()">🔄 Actualizar Ubicación</button>`;
                    resultsDiv.innerHTML = html;

                } catch (error) {
                    resultsDiv.innerHTML = '<p style="color:red; text-align:center;">Error al conectar con el servidor.</p>';
                }
            }
        </script>
    </body>
    </html>
    """)


@app.route("/api/cercanas", methods=["GET"])
def cercanas():
  try:
    user_lat = float(request.args.get("lat"))
    user_lon = float(request.args.get("lon"))
  except (TypeError, ValueError):
    return (
        jsonify({"error": "Parámetros de latitud o longitud inválidos"}),
        400,
    )

  for st in stations:
    st["distancia_km"] = round(
        haversine(user_lat, user_lon, st["lat"], st["lon"]), 2
    )

  sorted_stations = sorted(stations, key=lambda x: x["distancia_km"])
  return jsonify(sorted_stations[:3])


if __name__ == "__main__":
  app.run(debug=True)
