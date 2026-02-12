import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import os
import time

# ===== CONFIGURACION =====
TOKEN = os.environ.get("TOKEN")      # reemplaza en Railway con tu token
CANAL = os.environ.get("CANAL")      # reemplaza en Railway con tu canal (@TuCanal)

URL = "https://sgonorte.bomberosperu.gob.pe/24horas/?criterio="

# Unidades que activan alerta
UNIDADES_B202 = [
    "AMB-202", "AMB202-2", "RES-202", "RESLIG-202",
    "USAC-202", "AUX-202", "AUX-36", "M202-1"
]

bot = Bot(token=TOKEN)
ultimo_parte = None

# ===== FUNCIONES =====

async def enviar_telegram(mensaje, botones):
    """Envía mensaje al canal de forma asíncrona"""
    await bot.send_message(chat_id=CANAL, text=mensaje, reply_markup=botones)

def extraer_coordenadas(texto):
    """Busca coordenadas en el texto"""
    lat = lon = None
    partes = texto.split()
    for palabra in partes:
        if "(" in palabra and "," in palabra and ")" in palabra:
            try:
                lat, lon = palabra.replace("(", "").replace(")", "").split(",")
                break
            except:
                continue
    return lat, lon

async def revisar_emergencias():
    global ultimo_parte
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        filas = soup.find_all("tr")

        for fila in filas:
            texto = fila.get_text(" ", strip=True)

            # Verifica si contiene alguna unidad B202
            if any(u in texto for u in UNIDADES_B202):
                datos = texto.split()
                try:
                    nro_parte = datos[0]
                except:
                    continue

                # Evitar duplicados
                if nro_parte == ultimo_parte:
                    return
                ultimo_parte = nro_parte

                # Extraer coordenadas
                lat, lon = extraer_coordenadas(texto)

                # Crear links
                if lat and lon:
                    google = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                    waze = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
                    apple = f"http://maps.apple.com/?ll={lat},{lon}"
                    tg = f"https://t.me/share/url?url={lat},{lon}"
                else:
                    google = waze = apple = tg = URL

                botones = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Google Maps", url=google)],
                    [InlineKeyboardButton("Waze", url=waze)],
                    [InlineKeyboardButton("Apple Maps", url=apple)],
                    [InlineKeyboardButton("Abrir en Telegram", url=tg)],
                ])

                # Formato de mensaje
                mensaje = f"""
🔥 ¡Nueva Emergencia en B-202! 🔥

🚨 Resumen: {tipo} en {direccion} ({coordenadas})

──────────────────

📋 Detalles de la Emergencia:

🔢 Nro Parte: {nro_parte}

🏷️ Tipo: {tipo}

⏰ Hora: {hora}

📍 Dirección: {direccion}

📊 Estado: {estado}

🚒 Máquinas: 
{maquinas_formateadas}

──────────────────

ℹ️ Información oficial en: Bomberos Perú
🛡️ Mantente seguro.

──────────────────
🗺️ ABRIR UBICACIÓN EN:
"""

                # Enviar mensaje asíncrono
                await enviar_telegram(mensaje, botones)
                print("Publicado:", nro_parte)
                return

    except Exception as e:
        print("Error:", e)

# ===== LOOP PRINCIPAL =====
async def main_loop():
    while True:
        await revisar_emergencias()
        await asyncio.sleep(5)  # revisa cada 5 segundos

# ===== EJECUTAR BOT =====
if __name__ == "__main__":
    asyncio.run(main_loop())




