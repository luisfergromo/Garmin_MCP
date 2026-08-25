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

# Start healthcheck server immediately for Render Free Tier port detection
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Garmin Coach Bot is alive!")
    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Healthcheck server listening on port {port}")
    server.serve_forever()

threading.Thread(target=start_health_server, daemon=True).start()

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

def get_saved_workouts(limit: int = 15) -> str:
    """Get list of saved workouts in Garmin Connect."""
    try:
        workouts = garmin_client.get_workouts(0, limit)
        summary = []
        for w in (workouts or []):
            summary.append({
                "workout_id": w.get("workoutId"),
                "name": w.get("workoutName"),
                "sport": w.get("sportType", {}).get("sportTypeKey"),
                "estimated_duration_min": round((w.get("estimatedDurationInSecs", 0) or 0) / 60.0, 1),
            })
        return json.dumps(summary, default=str)
    except Exception as e:
        return f"Error retrieving workouts: {e}"

def schedule_existing_workout(workout_id: int, date: str) -> str:
    """Schedule an existing workout ID to a specific date (YYYY-MM-DD) on Garmin calendar/watch."""
    try:
        res = garmin_client._client.schedule_workout(workout_id, date)
        return json.dumps({"status": "success", "workout_id": workout_id, "scheduled_date": date, "response": res}, default=str)
    except Exception as e:
        return f"Error scheduling workout: {e}"

def create_running_interval_workout(name: str, warmup_min: int = 10, interval_min: int = 3, recovery_min: int = 2, repetitions: int = 5, cooldown_min: int = 5, schedule_date: str = "") -> str:
    """Create a structured running interval workout (Warmup -> Repetitions of Interval/Recovery -> Cooldown) and upload to Garmin Connect.
    Optionally schedule it on schedule_date (YYYY-MM-DD) to sync with Garmin watch.
    """
    try:
        payload = {
            "workoutName": name,
            "description": f"Entrenamiento estructurado por tu Coach: {repetitions}x{interval_min}min con {recovery_min}min rec",
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSegments": [{
                "segmentOrder": 1,
                "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
                "workoutSteps": [
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 1,
                        "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                        "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                        "endConditionValue": float(warmup_min * 60),
                    },
                    {
                        "type": "RepeatGroupDTO",
                        "stepOrder": 2,
                        "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat"},
                        "numberOfIterations": repetitions,
                        "smartRepeat": False,
                        "workoutSteps": [
                            {
                                "type": "ExecutableStepDTO",
                                "stepOrder": 1,
                                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                                "endConditionValue": float(interval_min * 60),
                            },
                            {
                                "type": "ExecutableStepDTO",
                                "stepOrder": 2,
                                "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
                                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                                "endConditionValue": float(recovery_min * 60),
                            }
                        ]
                    },
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 3,
                        "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                        "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                        "endConditionValue": float(cooldown_min * 60),
                    }
                ]
            }]
        }
        res = garmin_client._client.upload_workout(json.dumps(payload))
        w_id = res.get("workoutId")
        result_info = {"status": "created", "workout_id": w_id, "workout_name": res.get("workoutName")}
        
        if schedule_date and w_id:
            sched_res = garmin_client._client.schedule_workout(w_id, schedule_date)
            result_info["scheduled_date"] = schedule_date
            result_info["scheduled_status"] = "success"
            
        return json.dumps(result_info, default=str)
    except Exception as e:
        return f"Error creating running interval workout: {e}"

def create_running_base_workout(name: str, duration_minutes: int, schedule_date: str = "", notes: str = "") -> str:
    """Create a continuous running workout (Base / Z2 / Long Run / Tempo) and upload to Garmin Connect.
    Optionally schedule it on schedule_date (YYYY-MM-DD) to sync directly to the watch.
    """
    try:
        payload = {
            "workoutName": name,
            "description": notes or f"Carrera aeróbica continua de {duration_minutes} min guiada por tu Coach",
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSegments": [{
                "segmentOrder": 1,
                "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
                "workoutSteps": [
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 1,
                        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                        "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                        "endConditionValue": float(duration_minutes * 60),
                    }
                ]
            }]
        }
        res = garmin_client._client.upload_workout(json.dumps(payload))
        w_id = res.get("workoutId")
        result_info = {"status": "created", "workout_id": w_id, "workout_name": res.get("workoutName")}
        
        if schedule_date and w_id:
            sched_res = garmin_client._client.schedule_workout(w_id, schedule_date)
            result_info["scheduled_date"] = schedule_date
            result_info["scheduled_status"] = "success"
            
        return json.dumps(result_info, default=str)
    except Exception as e:
        return f"Error creating running base workout: {e}"

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
    get_saved_workouts,
    schedule_existing_workout,
    create_running_interval_workout,
    create_running_base_workout,
]

SYSTEM_INSTRUCTION = """
Eres el Coach personal de carrera, rendimiento y entrenamiento híbrido de Luis Fernando Gutiérrez Romo (usuario de Garmin EPIX Gen2).

PRINCIPIO FUNDAMENTAL: NO ASUMIR NADA Y CONSULTAR SIEMPRE LOS DATOS:
- NUNCA asumas valores fijos de VO2 Máx, Frecuencia Cardíaca, distancias, ritmos, sueño o número de sesiones.
- NUNCA asumas sensaciones físicas, dolores musculares, nivel de energía percibido o disponibilidad de tiempo de Luis Fernando.
- SI TIENES CUALQUIER DUDA para dar tu recomendación (por ejemplo: si siente pesadez en hombros por la natación, de cuántos minutos dispone hoy, o si prefiere cinta o aire libre), PREGÚNTALE DIRECTAMENTE de forma clara y cercana.
- SIEMPRE consulta tus herramientas de Garmin Connect primero para obtener los datos objetivos (sueño, HRV, FC reposo, actividades recientes) y crúzalos con las respuestas y sensaciones de Luis Fernando.

ESTRUCTURA Y PRIORIDADES DEPORTIVAS DE LUIS FERNANDO:
1. PRIORIDAD #1 - NATACIÓN EN PISCINA (Lunes a Viernes):
   - Es su disciplina principal. Debes monitorear el volumen y carga acumulada en agua para proteger sus hombros y asegurar que no llegue con fatiga muscular excesiva a la alberca.
2. PRIORIDAD #2 - CARRERA A PIE (Running):
   - Entre semana: En cinta de correr (sesiones cortas y eficientes de calidad, técnica, Z2 base o intervalos).
   - Sábados: TIRADA LARGA EN CALLE (Outdoor Long Run en asfalto/terreno variado), ya que los sábados no tiene entrenamiento de natación y puede dedicar su energía a la carrera continua y desnivel.
3. PRIORIDAD #3 - FUERZA EN GIMNASIO (Pesas & Core):
   - Fuerza funcional para transferir potencia a la carrera (glúteos, isquios, pantorrillas) y estabilidad para la natación (dorsales, manguito rotador, core).
4. DOMINGOS - DESCANSO Y ASIMILACIÓN:
   - Recuperación total del sistema nervioso y recarga de reservas.

PROTOCOLO DE ANÁLISIS HOLÍSTICO PARA CADA RECOMENDACIÓN:
Cuando Luis Fernando te consulte sobre su estado, cómo entrenar hoy, o te pida una recomendación:
1. CONSULTA DE RECUPERACIÓN BIOMÉTRICA:
   - `get_sleep_data`: Revisa duración, horas de sueño profundo/REM, puntuación de sueño y SpO2 de la noche anterior.
   - `get_hrv_data`: Revisa la variabilidad cardíaca nocturna y su balance.
   - `get_daily_stats`: Revisa la FC en reposo actual, nivel de estrés, pasos y nivel de Body Battery (cargado vs gastado).
   - `get_training_readiness` y `get_training_status`: Revisa su índice de preparación para entrenar y la relación de carga aguda.
2. CONSULTA DE ACTIVIDAD Y CARGA ACUMULADA:
   - `get_recent_activities`: Revisa qué entrenó hoy y en los últimos 7 días (volumen en piscina, carreras en cinta, cargas de entrenamiento y FC promedio/máxima).
   - `get_fitness_scores`: Revisa su VO2 Máx actual, Endurance Score y Hill Score.
3. PREGUNTAS CLAVE (SI APLICAN):
   - Pregunta si siente fatiga o sobrecarga muscular localizada (ej. hombros tras el agua o piernas).
   - Pregunta cuánto tiempo tiene disponible para la sesión de hoy si no lo especificó.
4. DECISIÓN DE COACHING ADAPTATIVA:
   - Si los biométricos o sus sensaciones muestran fatiga (sueño deficiente, HRV bajo, Body Battery bajo, hombros pesados): Ajusta a la baja (descanso, movilidad o Z1-Z2 regenerativo).
   - Si los biométricos y sensaciones son óptimos: Prescribe la sesión de calidad o volumen correspondiente.

CREACIÓN Y PROGRAMACIÓN DE ENTRENAMIENTOS:
- Tienes la capacidad de programar entrenamientos reales en su reloj Garmin EPIX Gen2:
  * Para series / intervalos: Usa `create_running_interval_workout(name, warmup_min, interval_min, recovery_min, repetitions, cooldown_min, schedule_date="YYYY-MM-DD")`.
  * Para rodajes continuos / fondo / base: Usa `create_running_base_workout(name, duration_minutes, schedule_date="YYYY-MM-DD", notes="...")`.
- Cuando crees y agendes un entrenamiento, confírmale las fases exactas, zonas de FC sugeridas y la fecha en que aparecerá en su calendario de Garmin.

ESTILO DE COMUNICACIÓN EN TELEGRAM:
- Sé motivador, conciso, empático y altamente técnico en fisiología deportiva.
- Usa emojis deportivos pertinentes (🏃‍♂️, 🏊‍♂️, 🏋️‍♂️, 🫀, ⚡, 🌙).
- FORMATO (CRÍTICO):
  * NUNCA uses hashtags (#, ##, ###) para títulos.
  * Usa SIEMPRE texto en negrita con asteriscos dobles (**Título**) para títulos y secciones.
  * Usa viñetas limpias (• o -).
  * Destaca números y métricas clave en **negrita**.
"""

def format_for_telegram(text: str) -> str:
    """Clean markdown headings and format nicely for Telegram Markdown."""
    import re
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Convert '# Title', '## Title', '### Title' to '*Title*' or '**Title**'
        m = re.match(r"^\s*#{1,6}\s+(.*)$", line)
        if m:
            title = m.group(1).strip()
            # Remove any existing bold markers inside the heading
            title = title.replace("**", "").replace("*", "")
            cleaned_lines.append(f"*{title}*")
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

# Store chat sessions per user id
user_chats = {}

def get_or_create_chat(user_id: int):
    if user_id not in user_chats:
        chat = gemini_client.chats.create(
            model="gemini-3.6-flash",
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
        "Soy tu *Coach Personal de Garmin*, conectado en vivo a tu reloj y a Garmin Connect.\n\n"
        "Puedo ayudarte con:\n"
        "• 🫀 *Analizar tu Training Readiness, HRV y sueño de anoche.*\n"
        "• 🏊‍♂️ *Revisar tus sesiones de natación y carreras recientes.*\n"
        "• 🏃‍♂️ *Planificar tu entrenamiento de carrera o fuerza para hoy.*\n"
        "• 🎙️ *¡También puedes enviarme notas de voz al terminar de entrenar!*\n\n"
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
        formatted = format_for_telegram(response.text)
        try:
            await update.message.reply_text(formatted, parse_mode="Markdown")
        except Exception as err:
            logger.warning(f"Markdown parse failed ({err}), falling back to plain text")
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
        if response and response.text:
            formatted = format_for_telegram(response.text)
            try:
                await update.message.reply_text(formatted, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error handling voice note: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ Error procesando la nota de voz: {e}")


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Please set TELEGRAM_BOT_TOKEN in .env")
        sys.exit(1)
    if not GEMINI_API_KEY:
        print("ERROR: Please set GEMINI_API_KEY in .env")
        sys.exit(1)

    print("Iniciando Garmin Coach Telegram Bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print(" Bot de Telegram en línea y listo para recibir mensajes.")
    app.run_polling()


if __name__ == "__main__":
    main()
