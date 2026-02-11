import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ===== CONFIGURACION =====
TOKEN = "8379416814:AAHInv5f2gbwoNVoJ6SkVOBgkrtKtb2sAp4"
CANAL = "@MonitorB202bot"
URL = "https://sgonorte.bomberosperu.gob.pe/24horas/?criterio="

# Unidades que activan alerta
UNIDADES_B202 = [
    "AMB-202", "AMB202-2", "RES-202", "RESLIG-202",
    "USAC-202", "AUX-202", "AUX-36", "M202-1"
]

bot = Bot(token=TOKEN)

ultimo_parte = None

# ===== FUNCION PRINCIPAL =====
def revisar_emergencias():
    global ultimo_parte

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    filas = soup.find_all("tr")

    for fila in filas:
        texto = fila.get_text(" ", strip=True)

        # Verifica si contiene alguna unidad B202
        if any(u in texto for u in UNIDADES_B202):

            # Intentar extraer datos (ajustable si cambia la web)
            datos = texto.split()

            try:
                nro_parte = datos[0]
            except:
                continue

            # Evitar repetidos
            if nro_parte == ultimo_parte:
                return

            ultimo_parte = nro_parte

            # Extraer coordenadas
            lat = None
            lon = None
            for palabra in datos:
                if "," in palabra and "-" in palabra:
                    try:
                        lat, lon = palabra.replace("(", "").replace(")", "").split(",")
                        break
                    except:
                        pass

            # ===== LINKS =====
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

            mensaje = f"""🔥 ¡Nueva Emergencia para B-202! 🔥

📋 Nro Parte: {nro_parte}

ℹ️ Información oficial en: Bomberos Perú
🛡️ Mantente seguro.
"""

            bot.send_message(chat_id=CANAL, text=mensaje, reply_markup=botones)

            print("Publicado:", nro_parte)
            return


# ===== LOOP INFINITO =====
while True:
    try:
        revisar_emergencias()
    except Exception as e:
        print("Error:", e)

    time.sleep(5)
