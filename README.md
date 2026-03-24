# 𖤓 Akirae — Next-Gen Discord Management System

<img src="banner.jpg" width="100%" alt="Akirae Banner">

**Akirae** is a high-performance, multipurpose Discord bot built for power users and administrators. Developed with **Python 3.10+** and **discord.py**, it leverages **Supabase (PostgreSQL)** for a seamless, cloud-native data experience.

---

## Key Features

* **⚙️ Advanced Dashboard (`!st`):** A fully interactive, multi-page settings menu using Discord's latest UI components (Buttons, Select Menus).
* **🛡️ Robust Moderation:** Automated warning system with customizable limits, smart mutes, and persistent logging.
* **📜 Security Logging:** Real-time tracking of server events, administrative actions, and message history to a dedicated log channel.
* **💎 Database-Driven:** All configurations are stored in **Supabase**, allowing for instant updates and cross-platform synchronization.
* **⚡ 24/7 Uptime:** Integrated `keep_alive.py` module to prevent service suspension on PaaS providers like Render.
* **🏗️ Modular Design:** Clean architecture with specialized directories for `cogs`, `moderation`, and `utils`.

---

## Technical Stack

| Component | Technology |
| :--- | :--- |
| **Language** | [Python 3.10+](https://www.python.org/) |
| **Framework** | [Discord.py 2.3+](https://github.com/Rapptz/discord.py) |
| **Database** | [Supabase](https://supabase.com/) (PostgreSQL) |
| **Hosting Utility** | Flask (HTTP Heartbeat) |
| **Auth/Secrets** | Dotenv (.env) |

---

## Quick Start

### 1. Clone & Install
```bash
git clone [https://github.com/VentieRavelle/akiraedc.git](https://github.com/VentieRavelle/akiraedc.git)
cd akiraedc
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the root folder:
```env
DISCORD_TOKEN=your_token_here
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_service_role_key
```

### 3. Launch
```bash
python main.py
```

---

## Project Architecture

```text
├── cogs/                # Specialized modules (Shop, Errors, Events)
├── moderation/          # Core Moderation & Dashboard logic (!st)
├── utils/               # Shared helper functions
├── main.py              # Application entry point & Cog loader
├── db.py                # Supabase client & DB connection
├── keep_alive.py        # Web-server for 24/7 uptime
└── requirements.txt     # Dependency manifest
```

---

## Security & Reliability

As an infrastructure-focused project, **Akirae** prioritizes:
* **Zero-Token Leakage:** Strict `.gitignore` policy for all secret files.
* **Error Resilience:** Global exception handling via `ErrorHandler.py` to prevent silent crashes.
* **Rate Limiting:** Built-in cooldowns to protect the Supabase API from abuse.

