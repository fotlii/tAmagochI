"""
Desktop AI Lifeform — Configuration
====================================
All tunable parameters in one place. Edit freely.
"""

# ── WebSocket ─────────────────────────────────────────────────────────────────
WS_HOST = "localhost"
WS_PORT = 8765

# ── Timing ────────────────────────────────────────────────────────────────────
TICK_INTERVAL_S   = 2.0     # Advancing emotions faster
SENSOR_INTERVAL_S = 1.0     # Sampling windows faster
BROADCAST_INTERVAL_S = 1.0  # Pushing to Godot faster

# ── Idle detection ────────────────────────────────────────────────────────────
IDLE_SLEEP_THRESHOLD_S  = 1800   # 30 min idle → sleeping
IDLE_LONELY_THRESHOLD_S = 600    # 10 min idle → lonely
NIGHT_START_HOUR = 23            # Hour (24h) when night begins
NIGHT_END_HOUR   = 7             # Hour (24h) when night ends

# ── Emotional variable decay rates (per tick) ─────────────────────────────────
# Values between 0 and 1. Positive = rises toward 1, negative = decays toward 0
DECAY = {
    "stress":        -0.05,   # stress fades faster
    "curiosity":     -0.08,   # curiosity fades quickly
    "social_energy": -0.04,   # social energy drains faster
    "fatigue":        0.01,   # fatigue builds faster
    "attachment":     0.001,  # attachment stays slow
    "focus":         -0.05,   # focus fades faster
}

# ── Emotional variable impact on stimuli ──────────────────────────────────────
STIMULI_STRENGTH = {
    "coding_session":      {"focus": +0.15, "curiosity": +0.05, "fatigue": +0.02},
    "build_failure":       {"stress": +0.25, "focus": -0.10},
    "many_tabs":           {"stress": +0.10, "curiosity": +0.05},
    "new_app":             {"curiosity": +0.20},
    "music":               {"stress": -0.10, "social_energy": +0.10},
    "game":                {"stress": -0.15, "curiosity": +0.05},
    "idle_short":          {"fatigue": +0.01},
    "idle_long":           {"social_energy": -0.05, "fatigue": +0.03},
    "long_ai_chat":        {"social_energy": +0.20, "curiosity": +0.10},
    "system_crash":        {"stress": +0.40},
    "varied_activity":     {"social_energy": +0.05},
    "positive_event":      {"social_energy": +0.15, "stress": -0.05, "curiosity": +0.05},
}

# ── State thresholds ──────────────────────────────────────────────────────────
# Priority order matters: first match wins
STATE_RULES = [
    # (state_name, condition_fn_description)  — evaluated in creature.py
    ("sleeping",  "idle > IDLE_SLEEP_THRESHOLD_S or night hours with fatigue > 0.6"),
    ("stressed",  "stress > 0.6"),
    ("focused",   "focus > 0.6"),
    ("gaming",    "active_window_class == 'game'"),
    ("watching",  "active_window_class == 'watching'"),
    ("happy",     "social_energy > 0.75 and stress < 0.3"),
    ("curious",   "curiosity > 0.5"),
    ("lonely",    "social_energy < 0.2 and idle > IDLE_LONELY_THRESHOLD_S"),
    ("idle",      "default fallback"),
]

# ── App / window classification ───────────────────────────────────────────────
WINDOW_CLASSES = {
    "code": [
        "code", "visual studio", "pycharm", "intellij", "vim", "neovim",
        "emacs", "sublime", "atom", "notepad++", "cursor", "windsurf",
        "fleet", "rider", "clion", "goland", "webstorm", "godot",
        "tamagochi", "antigravity", "walkthrough", "github", "gitlab",
    ],
    "music": [
        "spotify", "foobar", "winamp", "vlc", "musicbee", "aimp",
        "youtube music", "deezer", "tidal", "soundcloud", "bandcamp",
        "playlist", "lofi", "hiphop", "chillhop", "ambient", "mix",
    ],
    "game": [
        "steam", "epic games", "gog", "battle.net", "origin", "ubisoft",
        "isaac", "repentance", "elden ring", "cyberpunk", "minecraft",
        "fortnite", "roblox", "overwatch", "league", "valorant", "csgo",
        "cs2", "stardew", "hades", "launcher",
    ],
    "ai_chat": [
        "claude", "chatgpt", "gemini", "copilot", "ollama", "lm studio",
        "jan", "open webui",
    ],
    "productivity": [
        "notion", "obsidian", "excel", "word", "onenote", "todoist",
        "trello", "slack", "discord", "teams", "zoom",
    ],
    "terminal": [
        "cmd", "powershell", "windows terminal", "wt", "bash", "zsh",
        "alacritty", "wezterm", "hyper",
    ],
    "watching": [
        "youtube", "netflix", "twitch", "prime video", "hbo", "disney+",
        "plex", "vlc", "mpv", "media player", "video", "cinema", "movie",
        "anime", "crunchyroll", "stremio",
    ],
    "browser": [
        "chrome", "firefox", "edge", "brave", "opera", "safari", "vivaldi",
    ],
}

# ── LLM (optional) ────────────────────────────────────────────────────────────
LLM_ENABLED       = True
LLM_MODEL         = "llama3.2:1b"
LLM_OLLAMA_URL    = "http://localhost:11434"
LLM_PHRASE_CHANCE = 0.05   # probability per tick of generating a thought

# ── Memory ────────────────────────────────────────────────────────────────────
DB_PATH = "data/lifeform.db"

# ── Display ───────────────────────────────────────────────────────────────────
DISPLAY_WIDTH  = 480
DISPLAY_HEIGHT = 320
