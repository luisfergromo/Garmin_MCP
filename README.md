# Garmin MCP Server

Servidor MCP (Model Context Protocol) que conecta a Garmin Connect y expone tus datos de fitness y salud a **Gemini**, **Claude**, y otros clientes MCP compatibles.

Los datos de Garmin se acceden a través de la librería [python-garminconnect](https://github.com/cyberjunky/python-garminconnect).

## Features

- 📊 **Actividades** — Listar, buscar, ver detalle, editar nombre/tipo
- ❤️ **Salud** — Estadísticas diarias, sueño, estrés, frecuencia cardíaca, SpO2, HRV, Body Battery
- 🏋️ **Entrenamiento** — Estado, readiness, VO2 max, hill/endurance scores, predicciones de carrera
- ⌚ **Dispositivos** — Lista de dispositivos, configuración, datos de solar
- 👟 **Gear** — Equipamiento y estadísticas de uso
- ⚖️ **Peso** — Registro y consulta de pesajes
- 🏃 **Workouts** — Listar, crear, programar, eliminar
- 👤 **Perfil** — Información del usuario

### Tool Coverage

~50 herramientas organizadas en 8 módulos:

| Categoría | Tools | Descripción |
|-----------|-------|-------------|
| Actividades | 10 | Listado, detalle, splits, HR zones, clima, edición |
| Salud & Bienestar | 15 | Stats, sueño, estrés, HR, HRV, SpO2, Body Battery, hidratación |
| Entrenamiento | 8 | Training status/readiness, VO2 max, predicciones, badges |
| Dispositivos | 5 | Lista, configuración, solar |
| Gear | 4 | Equipamiento y estadísticas |
| Peso | 4 | Pesajes y registro |
| Workouts | 5 | Gestión de entrenamientos |
| Perfil | 3 | Info de usuario |

## Quick Start

### Prerrequisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip
- Cuenta de Garmin Connect

### Paso 1: Pre-autenticación (una vez)

```bash
# Con uv (recomendado)
uvx --python 3.12 --from . garmin-mcp-auth

# O directamente
uv run garmin-mcp-auth

# Variables de entorno (alternativa)
GARMIN_EMAIL=tu@email.com GARMIN_PASSWORD=secreto garmin-mcp-auth
```

Los tokens OAuth se guardan en `~/.garminconnect` y son válidos ~6 meses.

### Paso 2: Verificar tokens

```bash
garmin-mcp-auth --verify
```

## Configuración para Gemini (Antigravity IDE)

Agrega la configuración MCP en tu archivo de configuración de Antigravity:

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/ruta/a/Garmin_MCP",
        "run",
        "garmin-mcp"
      ]
    }
  }
}
```

O usando uvx directamente (sin clonar el repo):

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        ".",
        "garmin-mcp"
      ]
    }
  }
}
```

## Configuración para Claude Desktop

Editar `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/ruta/a/Garmin_MCP",
        "run",
        "garmin-mcp"
      ]
    }
  }
}
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `GARMIN_EMAIL` | Email de Garmin Connect | — |
| `GARMIN_PASSWORD` | Password de Garmin Connect | — |
| `GARMIN_EMAIL_FILE` | Archivo con el email | — |
| `GARMIN_PASSWORD_FILE` | Archivo con el password | — |
| `GARMIN_IS_CN` | Usar Garmin China (garmin.cn) | `false` |
| `GARMIN_MCP_TRANSPORT` | Transporte: `stdio`, `streamable-http`, `sse` | `stdio` |
| `GARMIN_MCP_HOST` | Host para transporte HTTP | `127.0.0.1` |
| `GARMIN_MCP_PORT` | Puerto para transporte HTTP | `8000` |
| `GARMIN_ENABLED_TOOLS` | Lista de tools habilitados (CSV) | todos |
| `GARMIN_DISABLED_TOOLS` | Lista de tools deshabilitados (CSV) | ninguno |

## Tool Filtering

Puedes filtrar qué herramientas expone el servidor:

```json
{
  "env": {
    "GARMIN_ENABLED_TOOLS": "get_stats,get_activities,get_sleep_data"
  }
}
```

## Desarrollo

```bash
# Clonar e instalar
git clone <repo-url>
cd Garmin_MCP
uv sync

# Correr el servidor
uv run garmin-mcp

# Correr tests
uv run python -m pytest tests/

# Inspector MCP
npx @modelcontextprotocol/inspector uv run garmin-mcp
```

## Licencia

MIT
