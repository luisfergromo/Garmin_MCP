# 🏃‍♂️ Garmin AI Coach & MCP Server ⌚🤖

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini 2.5/3.5/3.7](https://img.shields.io/badge/Gemini-AI%20Powered-orange.svg)](https://aistudio.google.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot%20Ready-2CA5E0.svg?logo=telegram)](https://telegram.org/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol%201.0-purple.svg)](https://modelcontextprotocol.io/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-FFDD00?logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/luisfergromo)

A complete Artificial Intelligence ecosystem for athletes of any discipline (Running, Swimming, Cycling, Triathlon, Gym, Hyrox, CrossFit, etc.) connected in real-time to **Garmin Connect**.

It includes two primary operating modes:
1. 📱 **Personal Telegram Coach (Powered by Gemini AI)**: Chat or send voice notes to your AI coach directly from your mobile phone. It monitors your daily recovery (Sleep stages/score, nocturnal HRV, Body Battery, Training Readiness), evaluates weekly load distribution, and **schedules structured workouts directly onto your Garmin watch**.
2. 🔌 **Model Context Protocol (MCP) Server**: Exposes your Garmin health, fitness, and activity metrics to **Google Gemini**, **Claude Desktop**, **Cursor**, or **Antigravity IDE** with 50+ pre-built tools.

---

## 🌟 Key Features

- 🫀 **Comprehensive Recovery & Health Diagnostics**: Sleep stages (Deep/Light/REM, sleep score, SpO2), nocturnal HRV balance, resting heart rate, stress, and Body Battery.
- 🎯 **Targeted HR Zone Workouts**: Calculates and adapts your workouts according to your configured Garmin Heart Rate Zones (Z1 through Z5) and muscular readiness.
- ⌚ **Direct Watch Workout Scheduling**: Creates structured interval or aerobic base workouts and schedules them directly onto your Garmin watch calendar via Garmin Connect.
- 🎙️ **Telegram Voice Notes Support**: Send a voice note right after finishing your session; the AI transcribes and correlates your verbal feedback against the actual workout metrics recorded by your watch.
- ⚡ **Multi-Model Failover Cascade**: Automatically fails over across Gemini models (`gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-flash-lite-latest`, `gemini-3.5-flash`, `gemini-3.7-flash`) to guarantee 100% uptime without rate-limit interruptions.
- 🛡️ **Privacy & Security First**: Local OAuth token caching, strict `.gitignore` filters, and optional Telegram User ID whitelist restrictions.

---

## 📋 Prerequisites

1. **Python 3.12+** installed on your machine.
2. **[uv](https://docs.astral.sh/uv/)** (recommended for speed) or standard `pip`.
3. **Garmin Connect Account** (Email and Password).
4. **Google Gemini API Key** (Free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey)).
5. **Telegram Bot Token** (Free via [@BotFather](https://t.me/botfather)).

---

## 🚀 Quick Start Guide (3 Minutes)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Garmin_MCP.git
cd Garmin_MCP
```

### 2. Install dependencies

With `uv` (recommended):
```bash
uv sync
```

Or with standard `pip`:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -e .
```

### 3. Configure environment variables

Copy `.env.example` to `.env`:

```bash
# On Windows:
copy .env.example .env

# On Linux / macOS:
cp .env.example .env
```

Open `.env` in your text editor and fill in the required keys:

```env
# 1. Garmin Connect
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password_here

# 2. Google Gemini AI (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# 3. Telegram Bot (https://t.me/botfather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# 4. Optional Security: restrict bot exclusively to your Telegram User ID
# TELEGRAM_ALLOWED_USER_ID=123456789
```

### 4. Authenticate Garmin Tokens (One-time step)

To authenticate your Garmin account and securely cache OAuth tokens locally:

```bash
uv run garmin-mcp-auth
```
*(If your account has Two-Factor Authentication (2FA) enabled, you will be prompted for your SMS/Email verification code in the terminal).*

---

## 🎨 Customizing Your Coach (No Code Changes Needed)

You can customize your coach's persona, schedule, sport focus, and timezone using two simple methods:

### Option 1: Via `.env` Variables

| Variable | Description | Example / Default |
|---|---|---|
| `TIMEZONE` | Timezone for accurate date and morning briefing calculations | `America/New_York`, `Europe/London`, `America/Mexico_City` |
| `ATHLETE_NAME` | Name your Coach will use to address you | `Alex`, `Sarah`, `Athlete` |
| `GARMIN_DEVICE_MODEL` | Your Garmin watch model for tailored instructions | `Forerunner 965`, `Fenix 7`, `EPIX Gen2`, `Venu 3` |
| `COACH_SPORT_FOCUS` | Main sports and athletic focus | `Marathon & Strength`, `Olympic Triathlon`, `Trail Running` |
| `COACH_CUSTOM_PROMPT` | Custom directives, current goals, or specific guidelines | `Preparing for a sub-40 min 10k race. Protect left hamstring.` |
| `TELEGRAM_ALLOWED_USER_ID` | Your Telegram User ID to lock the bot to your account | `987654321` (Get your ID via [@userinfobot](https://t.me/userinfobot)) |

### Option 2: Using an Athlete Profile File (`coach_profile.txt`)

If you have a specific weekly training schedule, injury history, or training constraints, copy the example profile:

```bash
# On Windows:
copy coach_profile.example.txt coach_profile.txt

# On Linux/macOS:
cp coach_profile.example.txt coach_profile.txt
```

Edit `coach_profile.txt` in plain English:
```text
[ATHLETE]
Name: Alex
Primary Sports: Triathlon (Running, Cycling, Swimming)
Current Goal: Half Ironman (70.3) in 6 months

[PREFERRED WEEKLY SCHEDULE]
- Monday: Technique Swimming + Mobility & Core
- Tuesday: Track Interval Running (Zone 4 / Threshold)
- Wednesday: Zone 2 Cycling + Upper Body Strength
- Thursday: Easy Aerobic Recovery Run (Zone 1/2)
- Friday: Endurance Swimming + Lower Body Strength
- Saturday: Outdoor Long Run or Long Ride
- Sunday: Full Rest & Recovery

[PREFERENCES & INJURIES]
- History: Watch left Achilles tendon when exceeding 180 spm.
- Availability: 60-75 min on weekdays (mornings), 3 hours on Saturdays.
```

The coach will automatically detect `coach_profile.txt` and seamlessly incorporate your routine into all its training advice.

---

## 📱 Using the Telegram Coach Bot

Start the bot:

```bash
uv run python telegram_bot.py
```

### Available Telegram Commands

| Command | Description |
|---|---|
| `/start` | Welcome message, connection status, and quick-action menu. |
| `/briefing` | **Morning Briefing**: Real-time diagnostic of your sleep, HRV, Body Battery, Training Readiness, and today's workout recommendation. |
| `/week` or `/semana` | **Weekly Summary**: Accumulated distance, hours, and Training Load across all logged disciplines. |
| `/status` | Connection health check and active Gemini model status. |
| `/help` | Bot command guide, workout tips, and voice notes instructions. |

### 🎙️ Voice Notes After Training
After finishing a workout, tap the microphone button in Telegram and tell your coach how you felt:
> *"Coach, I just finished the 5x1000m track intervals. My legs felt slightly heavy on the last two reps, but I kept my heart rate in Zone 4. How did the actual numbers look on my watch?"*

The AI will fetch your most recent activity from Garmin Connect, compare your real-time heart rate and pace with your verbal sensations, and provide immediate feedback.

### 📅 Scheduling Workouts onto Your Watch
Simply ask the coach in natural language:
> *"Coach, please create a 5x3 min interval session with 2 min recovery and schedule it on my watch for tomorrow morning."*

---

## 🔌 Running as an MCP Server (Gemini / Claude / Cursor)

Use this repository as a backend data provider for Model Context Protocol (MCP) clients.

### Available MCP Tools (~50 tools):

- 📊 **Activities**: `get_activities`, `get_activity_details`, `get_activity_splits`, `get_activity_hr_in_zones`, etc.
- ❤️ **Health & Wellness**: `get_stats`, `get_sleep_data`, `get_hrv_data`, `get_body_battery`, `get_stress_data`, `get_spo2_data`.
- 🏋️ **Training & Fitness**: `get_training_status`, `get_training_readiness`, `get_vo2_max`, `get_race_predictions`, `get_endurance_score`.
- 👟 **Gear**: `get_gear`, `get_gear_stats`.
- ⌚ **Devices**: `get_devices`, `get_device_settings`.
- 🏃 **Workouts**: `get_workouts`, `upload_workout`, `schedule_workout`.

### Antigravity IDE / Gemini MCP Configuration

Add the server to your MCP settings file:

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uv",
      "args": [
        "--directory",
        "/full/path/to/Garmin_MCP",
        "run",
        "garmin-mcp"
      ]
    }
  }
}
```

### Claude Desktop Configuration

In `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uv",
      "args": [
        "--directory",
        "/full/path/to/Garmin_MCP",
        "run",
        "garmin-mcp"
      ]
    }
  }
}
```

---

## ☁️ Cloud Deployment (Docker / Render / Google Cloud Run)

The project includes an optimized `Dockerfile` and an internal healthcheck HTTP server listening on port `8080` (or `$PORT`), ready for PaaS platforms and container engines.

### 1. Build Docker image locally

```bash
docker build -t garmin-coach-bot .
```

### 2. Run container with environment variables

```bash
docker run -d \
  -e GARMIN_EMAIL="your_email@example.com" \
  -e GARMIN_PASSWORD="your_password" \
  -e GEMINI_API_KEY="your_gemini_api_key" \
  -e TELEGRAM_BOT_TOKEN="your_telegram_token" \
  -e TIMEZONE="America/New_York" \
  --name garmin_coach \
  garmin-coach-bot
```

### 💡 Cloud Deployment Tip (Bypass Cloudflare Block / 2FA)
When deploying to Render, Fly.io, or Google Cloud Run, cloud datacenter IPs may trigger Garmin's Cloudflare captcha. You can bypass this using pre-authenticated base64 tokens:
1. Run `uv run garmin-mcp-auth` on your local machine.
2. Open the generated `.garminconnect_base64` file.
3. Copy the string and set it as the `GARMIN_TOKENS_BASE64` environment variable in your cloud platform settings. The bot will authenticate instantly without requiring login credentials or captcha.

---

## 🔒 Privacy & Security

- **Zero Credentials Committed**: The `.gitignore` file strictly excludes `.env`, session token folders (`.garminconnect/`, `.garminconnect_base64`), `coach_profile.txt`, local JSON dumps, and log files.
- **Whitelist Protection**: Configure `TELEGRAM_ALLOWED_USER_ID` in your `.env` to prevent unauthorized users from interacting with your bot.

---

## 🧪 Testing and Local Diagnostics

Verify that your Garmin Connect connection and tool integrations work properly:

```bash
# Test live Garmin connection and view today's health metrics
uv run python demo.py

# Run automated unit tests
uv run pytest
```

---

## ☕ Support

If you find this project helpful, consider supporting its development:

<a href="https://buymeacoffee.com/luisfergromo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it.
