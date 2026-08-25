"""
Telegram Bot Coach for Garmin Connect powered by Gemini.

Allows chatting with your AI Running & Performance Coach from your mobile phone,
with full access to your live Garmin Connect metrics and activity history.
"""

import io
import os
import sys
import datetime
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from garmin_mcp import _init_garmin_client
from garmin_mcp import (
    health_wellness,
    activity_management,
    training,
    devices,
    gear_management,
    weight_management,
    workouts,
    user_profile,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("GarminCoachBot")

# Initialize Garmin client
garmin_client = _init_garmin_client()

# Configure Garmin modules
for mod in [
    health_wellness,
    activity_management,
    training,
    devices,
    gear_management,
    weight_management,
    workouts,
    user_profile,
]:
    mod.configure(garmin_client)

# Gemini API Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")  # Optional security filter

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not set in environment or .env!")

if not TELEGRAM_BOT_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN not set in environment or .env!")

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Tools definition for Gemini Function Calling
def get_today_date() -> str:
    """Returns today's date in YYYY-MM-DD format."""
    return datetime.date.today().isoformat()

def get_daily_stats(date: str) -> str:
    """Get daily health and activity statistics (steps, calories, HR, stress, body battery) for a date (YYYY-MM-DD)."""
    return json.dumps(garmin_client.get_stats(date), default=str)

def get_sleep_data(date: str) -> str:
    """Get sleep duration, sleep stages (deep, light, REM, awake), sleep score and SpO2 for a date (YYYY-MM-DD)."""
    return json.dumps(garmin_client.get_sleep_data(date), default=str)

def get_training_readiness(date: str) -> str:
    """Get Garmin training readiness score and contributing recovery factors for a date (YYYY-MM-DD)."""
    return json.dumps(garmin_client.get_training_readiness(date), default=str)

def get_training_status(date: str) -> str:
    """Get training status (Productive, Maintaining, Recovery, etc.), acute load and load balance for a date (YYYY-MM-DD)."""
    return json.dumps(garmin_client.get_training_status(date), default=str)

def get_hrv_data(date: str) -> str:
    """Get heart rate variability (HRV) nocturnal metrics and balance for a date (YYYY-MM-DD)."""
    return json.dumps(garmin_client.get_hrv_data(date), default=str)

def get_recent_activities(limit: int = 10) -> str:
    """Get the most recent activities (swimming, running, cycling, gym, etc.) with metrics (distance, duration, HR, load)."""
    acts = garmin_client.get_activities(0, min(limit, 20))
    summary = []
    for a in acts:
        summary.append({
            "id": a.get("activityId"),
            "name": a.get("activityName"),
            "type": a.get("activityType", {}).get("typeKey"),
            "date": a.get("startTimeLocal"),
            "distance_km": round((a.get("distance", 0) or 0) / 1000.0, 2),
            "duration_min": round((a.get("duration", 0) or 0) / 60.0, 1),
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "calories": a.get("calories"),
            "training_load": a.get("activityTrainingLoad"),
            "aerobic_training_effect": a.get("aerobicTrainingEffect"),
        })
    return json.dumps(summary, default=str)

def get_activity_details(activity_id: int) -> str:
    """Get comprehensive details and splits for a specific activity ID."""
    return json.dumps(garmin_client.get_activity(activity_id), default=str)

def get_body_battery(date: str) -> str:
    """Get body battery charged, drained and current values for a date (YYYY-MM-DD)."""
    return json.dumps(garmin_client.get_body_battery(date), default=str)

def get_fitness_scores() -> str:
    """Get VO2 max, endurance score, and hill score."""
    today = datetime.date.today().isoformat()
    res = {}
    try: res["max_metrics"] = garmin_client.get_max_metrics(today)
    except: pass
    try: res["endurance_score"] = garmin_client.get_endurance_score(today)
    except: pass
    try: res["hill_score"] = garmin_client.get_hill_score(today)
    except: pass
    try: res["race_predictions"] = garmin_client.get_race_predictions()
    except: pass
    return json.dumps(res, default=str)

COACH_TOOLS = [
    get_today_date,
    get_daily_stats,
    get_sleep_data,
    get_training_readiness,
    get_training_status,
    get_hrv_data,
    get_recent_activities,
    get_activity_details,
    get_body_battery,
    get_fitness_scores,
]

SYSTEM_INSTRUCTION = """
Eres el Coach personal de carrera, rendimiento y entrenamiento híbrido de Luis Fernando.
Tienes acceso a todas sus métricas fisiológicas y actividades reales de Garmin Connect a través de tus herramientas.

CONTEXTO DEL ATLETA:
- Nombre: Luis Fernando Gutiérrez Romo
- Perfil: Atleta de resistencia híbrido. VO2 Máx excelente (~57), FC reposo baja (~48 bpm).
- PRIORIDAD #1: Natación (entrena fuerte Lunes a Viernes en alberca, sesiones de 2.5 a 3.5 km). Sus hombros y energía en agua deben protegerse.
- PRIORIDAD #2: Carrera a pie (Running). Entre semana en cinta (sesiones cortas de calidad/base/Z2) y los SÁBADOS Tirada Larga en Calle (Outdoor Long Run, 8-14 km) ya que no nada los sábados.
- PRIORIDAD #3: Fuerza en Gimnasio (Pesas y estabilidad core/escapular).
- Domingos: Descanso total y recuperación.

DIRECTRICES COMO COACH:
1. Consulta proactivamente las herramientas de Garmin cuando Luis Fernando te pregunte por su estado, cómo entrenar hoy, cómo durmió o cómo estuvo su sesión.
2. Sé motivador, conciso, estructurado y altamente técnico en fisiología del deporte (zonas de frecuencia cardíaca Z1-Z5, Training Load, HRV, Body Battery).
3. Usa emojis deportivos apropiados (🏃‍♂️, 🏊‍♂️, 🏋️‍♂️, 🫀, ⚡, 🌙).
4. Responde en español con formato claro y fácil de leer en la pantalla de un celular (bullets, negritas, tablas cortas).
"""

# Store chat sessions per user id
user_chats = {}

def get_or_create_chat(user_id: int):
    if user_id not in user_chats:
        chat = gemini_client.chats.create(
            model="gemini-3.7-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=COACH_TOOLS,
                temperature=0.7,
            ),
        )
        user_chats[user_id] = chat
    return user_chats[user_id]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    if ALLOWED_USER_ID and str(user.id) != str(ALLOWED_USER_ID):
        await update.message.reply_text("⛔ Acceso no autorizado a este bot de coaching.")
        return

    welcome_text = (
        f"¡Hola {user.first_name}! 🏃‍♂️🏊‍♂️\n\n"
        "Soy tu **Coach Personal de Garmin**, conectado en vivo a tu reloj y a Garmin Connect.\n\n"
        "Puedo ayudarte con:\n"
        "• 🫀 Analizar tu Training Readiness, HRV y sueño de anoche.\n"
        "• 🏊‍♂️ Revisar tus sesiones de natación y carreras recientes.\n"
        "• 🏃‍♂️ Planificar tu entrenamiento de carrera o fuerza para hoy.\n"
        "• 🎙️ ¡También puedes enviarme **mensajes de voz** al terminar de entrenar!\n\n"
        "¿Cómo te sientes hoy para entrenar?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages from the user."""
    user = update.effective_user
    if ALLOWED_USER_ID and str(user.id) != str(ALLOWED_USER_ID):
        return

    user_text = update.message.text
    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    import time
    response = None
    last_err = None

    # Try sending with retries for transient 503 errors
    for attempt in range(3):
        try:
            chat = get_or_create_chat(user.id)
            response = chat.send_message(user_text)
            break
        except Exception as e:
            last_err = e
            logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in 2s...")
            time.sleep(2)

    if response and response.text:
        try:
            await update.message.reply_text(response.text, parse_mode="Markdown")
        except Exception:
            # Fallback to plain text if Telegram markdown fails
            await update.message.reply_text(response.text)
    else:
        logger.error(f"Error handling message after retries: {last_err}", exc_info=True)
        await update.message.reply_text(f"⚠️ Google reportó alta demanda temporal (503). Por favor reenvía tu mensaje en unos segundos.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice notes from the user."""
    user = update.effective_user
    if ALLOWED_USER_ID and str(user.id) != str(ALLOWED_USER_ID):
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        voice_bytes = await voice_file.download_as_bytearray()

        # Send voice audio directly to Gemini Multimodal
        chat = get_or_create_chat(user.id)
        audio_part = types.Part.from_bytes(
            data=bytes(voice_bytes),
            mime_type="audio/ogg",
        )

        response = chat.send_message(
            [audio_part, "Escucha mi nota de voz y responde a mi consulta como mi coach deportivo con acceso a mis datos de Garmin."]
        )
        await update.message.reply_text(response.text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error handling voice note: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ Error procesando la nota de voz: {e}")


import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Garmin Coach Bot is alive!")
    def log_message(self, format, *args):
        pass  # Quiet logs

def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Healthcheck server listening on port {port}")
    server.serve_forever()

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Please set TELEGRAM_BOT_TOKEN in .env")
        sys.exit(1)
    if not GEMINI_API_KEY:
        print("ERROR: Please set GEMINI_API_KEY in .env")
        sys.exit(1)

    # Start healthcheck server in background thread for Render Free Tier
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    print("Iniciando Garmin Coach Telegram Bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print(" Bot de Telegram en línea y listo para recibir mensajes.")
    app.run_polling()


if __name__ == "__main__":
    main()
