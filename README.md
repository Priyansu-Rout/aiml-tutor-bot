# 🤖 AIML Tutor Bot

A Telegram bot that helps B.Tech students learn AI/ML through explanations, code generation, quizzes, ArXiv paper search, concept comparisons, and personalised roadmaps.

Built with Python (async), python-telegram-bot v21+, and OpenRouter API.

---

## 🚀 Setup

### 1. Get your Telegram Bot Token

1. Open Telegram and chat with **@BotFather**
2. Send `/newbot`
3. Follow the prompts — give it a name and username
4. Copy the **Bot Token** (looks like `123456789:ABCdef...`)

### 2. Get your OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up (free credits available)
3. Go to **Keys** → Create a new key
4. Copy the key

### 3. Install dependencies

```bash
git clone <your-repo>
cd aiml-tutor-bot
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your tokens:

```env
TELEGRAM_TOKEN=123456789:ABCdef...
OPENROUTER_API_KEY=sk-or-v1-...
```

### 5. Run the bot

```bash
python bot.py
```

You should see: `Bot is running!`

---

## 📚 All Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Welcome message | `/start` |
| `/help` | Show all commands | `/help` |
| `/clear` | Clear conversation memory | `/clear` |
| `/model` | Switch between AI models | `/model` |
| `/explain` `<topic>` | Explain an AI/ML concept | `/explain backpropagation` |
| `/code` `<task>` | Generate Python ML code | `/code CNN image classifier` |
| `/quiz` | Start an MCQ quiz | `/quiz` |
| `/paper` `<topic>` | Fetch ArXiv papers | `/paper transformers` |
| `/search` `<topic>` | Search ArXiv with abstracts | `/search object detection` |
| `/compare` `<A> vs <B>` | Compare two concepts | `/compare LSTM vs GRU` |
| `/roadmap` | Personalised learning roadmap | `/roadmap` |
| `/project` | General ML project ideas | `/project` |
| `/project` `<topic>` | Topic-specific project ideas | `/project NLP` |

> 💬 You can also just **send any message** and chat freely — the bot remembers context!

---

## 🤖 Available Models

All models are **free** via OpenRouter:

| Model | Provider | Best For |
|---|---|---|
| Llama 3.1 | Meta | General purpose, good all-rounder |
| Mistral 7B | Mistral AI | Efficient, fast responses |
| DeepSeek R1 | DeepSeek | Strong reasoning & math |
| Gemma 3 | Google | Lightweight, fast |

Switch anytime with `/model`.

---

## 🗂️ Project Structure

```
aiml-tutor-bot/
├── bot.py              # Main bot (all handlers)
├── requirements.txt   # Python dependencies
├── .env.example       # Template for .env
├── Dockerfile          # Docker container
├── docker-compose.yml # Docker Compose
├── railway.json       # Railway deploy config
├── render.yaml        # Render deploy config
└── README.md          # This file
```

---

## ☁️ Cloud Deployment

### Option 1 — Railway (Recommended, free tier)

1. **Fork this repo** to your GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your fork
4. Add environment variables:
   - `TELEGRAM_TOKEN`
   - `OPENROUTER_API_KEY`
5. Railway auto-detects Python and deploys! 🚀

---

### Option 2 — Render (Free tier)

1. **Fork this repo** to your GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Add environment variables in dashboard
6. Deploy

---

### Option 3 — VPS / Linux Server (Docker)

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/aiml-tutor-bot.git
cd aiml-tutor-bot

# Add your .env file
cp .env.example .env
nano .env  # paste your keys

# Run with Docker
docker-compose up -d
```

---

### Option 4 — Raspberry Pi / Local Linux

```bash
git clone https://github.com/YOUR_USERNAME/aiml-tutor-bot.git
cd aiml-tutor-bot
pip install -r requirements.txt
python bot.py
```

To keep it running after SSH disconnect:
```bash
tmux new -s bot
python bot.py
# Press Ctrl+B then D to detach
```

---

## 🛡️ Notes

- Bot uses **per-user conversation memory** (max 20 turns)
- API calls are **async** — no blocking
- No `time.sleep()` used anywhere
- Errors are logged with timestamps
- Use `/clear` if the bot starts misbehaving

---

## 📦 Dependencies

```
python-telegram-bot  >=21.0   # Telegram bot framework
httpx                >=0.27  # Async HTTP client
python-dotenv        >=1.0   # Load .env files
```

---

Built by **Priyansu Rout** — B.Tech AI & ML, ITER Bhubaneswar 🎓
