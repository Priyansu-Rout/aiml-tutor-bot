"""
AIML Tutor Bot — Telegram bot for AI/ML learning
Author: Priyansu Rout
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Optional

import httpx
from dotenv import load_dotenv
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction, ParseMode

import os

load_dotenv()

# ─── Config ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

# Free models
FREE_MODELS = {
    "Gemma 3 (Google)": "google/gemma-3-4b-it:free",
    "Dolphin 24B": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "Qwen3 80B": "qwen/qwen3-next-80b-a3b-instruct:free",
    "Nemotron 120B": "nvidia/nemotron-3-super-120b-a12b:free",
}

MODEL_DISPLAY = {
    "google/gemma-3-4b-it:free": "Gemma 3 (Google)",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free": "Dolphin 24B",
    "qwen/qwen3-next-80b-a3b-instruct:free": "Qwen3 80B",
    "nvidia/nemotron-3-super-120b-a12b:free": "Nemotron 120B",
}

DEFAULT_MODEL = "google/gemma-3-4b-it:free"

# ─── Memory ───────────────────────────────────────────────────────────────────
MAX_TURNS = 20

user_sessions: dict[int, dict] = {}

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("aiml_tutor_bot")


# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_system_prompt() -> str:
    return (
        "You are an expert AI/ML tutor bot for college students. "
        "You teach AI, ML, DL, NLP, CV, reinforcement learning, and related topics.\n"
        "Rules:\n"
        "- Be clear, concise, and friendly\n"
        "- Use code blocks for Python code\n"
        "- Use bullet points for explanations\n"
        "- Keep responses under 600 words\n"
        "- When generating code, use Python with comments\n"
        "- Prefer examples and real-world analogies\n"
        "- Temperature 0.4 for factual, 0.7 for creative tasks\n"
        "- Use markdown formatting: *bold*, `code`, bullet lists\n"
    )


def get_user_memory(user_id: int) -> list[dict]:
    if user_id not in user_sessions:
        user_sessions[user_id] = {"history": [], "model": DEFAULT_MODEL}
    return user_sessions[user_id]["history"]


def add_user_message(user_id: int, role: str, content: str):
    memory = get_user_memory(user_id)
    memory.append({"role": role, "content": content})
    if len(memory) > MAX_TURNS:
        memory.pop(0)


def get_user_model(user_id: int) -> str:
    return user_sessions.get(user_id, {}).get("model", DEFAULT_MODEL)


async def call_openrouter(
    messages: list[dict],
    model: str,
    max_tokens: int = 1024,
    temperature: float = 0.4,
) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://aiml-tutor-bot",
        "X-Title": "AIML Tutor Bot",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_BASE, headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return None


async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )


def model_keyboard():
    keyboard = []
    for name, model_id in FREE_MODELS.items():
        keyboard.append(
            [InlineKeyboardButton(name, callback_data=f"model:{model_id}")]
        )
    return InlineKeyboardMarkup(keyboard)


# ─── Command Handlers ──────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hey *{user}*! I'm your *AI/ML Tutor Bot*.\n\n"
        "I can help you learn AI/ML with explanations, code, quizzes, and more.\n\n"
        "*Commands:*\n"
        "/help — Show all commands\n"
        "/explain <topic> — Explain an AI/ML concept\n"
        "/code <task> — Generate ML code\n"
        "/quiz — Start a MCQ quiz\n"
        "/paper <topic> — Fetch ArXiv papers\n"
        "/search <topic> — Search ArXiv with abstracts\n"
        "/compare <A> vs <B> — Compare two concepts\n"
        "/roadmap — Personalised learning roadmap\n"
        "/project — ML project ideas\n"
        "/model — Switch AI model\n"
        "/clear — Clear conversation memory\n\n"
        "Or just chat with me freely! 🚀",
        parse_mode=ParseMode.MARKDOWN,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing(update, context)
    await update.message.reply_text(
        "*📚 AIML Tutor Bot — Commands*\n\n"
        "*Core Commands*\n"
        "`/start` — Welcome message\n"
        "`/help` — Show this help\n"
        "`/clear` — Clear your chat memory\n"
        "`/model` — Switch between free models\n\n"
        "*Learning Commands*\n"
        "`/explain <topic>` — Explain any AI/ML concept\n"
        "`  e.g. /explain backpropagation`\n\n"
        "`/code <task>` — Generate Python ML code\n"
        "`  e.g. /code CNN image classifier`\n\n"
        "`/quiz` — Start an MCQ quiz on AI/ML\n"
        "`  Send /quiz again for next question`\n\n"
        "`/paper <topic>` — Fetch latest ArXiv papers\n"
        "`  e.g. /paper transformers`\n\n"
        "`/search <topic>` — Search ArXiv with abstracts\n"
        "`  e.g. /search object detection`\n\n"
        "`/compare <A> vs <B>` — Compare two concepts\n"
        "`  e.g. /compare LSTM vs GRU`\n\n"
        "`/roadmap` — Get a personalised learning roadmap\n\n"
        "`/project` — General ML project ideas\n"
        "`/project <topic>` — Topic-specific project ideas\n"
        "`  e.g. /project NLP`\n\n"
        "*Free Models Available*\n"
        "• Gemma 3 (Google) — lightweight & fast\n"
        "• Dolphin 24B — strong reasoning\n"
        "• Qwen3 80B — powerful, larger model\n"
        "• Nemotron 120B — top-tier free model",
        parse_mode=ParseMode.MARKDOWN,
    )


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_sessions:
        user_sessions[user_id]["history"] = []
    await update.message.reply_text("🧹 Memory cleared! Fresh start. 👍")


async def model_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current = get_user_model(user_id)
    current_name = MODEL_DISPLAY.get(current, current)
    await update.message.reply_text(
        f"*🤖 Select an AI Model*\n\n"
        f"Current: *{current_name}*\n\n"
        "All models are free. Choose one:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=model_keyboard(),
    )


async def model_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("model:"):
        return
    model_id = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"history": [], "model": model_id}
    else:
        user_sessions[user_id]["model"] = model_id
    name = MODEL_DISPLAY.get(model_id, model_id)
    await query.edit_message_text(
        f"✅ Model switched to *{name}*!", parse_mode=ParseMode.MARKDOWN
    )


async def explain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "*📖 /explain Usage*\n\n"
            "`/explain <topic>`\n\n"
            "*Example:* `/explain backpropagation`\n"
            "`/explain transformer architecture`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    topic = " ".join(context.args)
    user_id = update.effective_user.id
    await send_typing(update, context)

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {
            "role": "user",
            "content": f"Explain the AI/ML concept of '{topic}' in a clear, "
            "educational way. Use bullet points, examples, and code snippets "
            "where appropriate. Keep it beginner-friendly but technically accurate.",
        }
    )

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.4)
    if response:
        add_user_message(user_id, "user", f"/explain {topic}")
        add_user_message(user_id, "assistant", response)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Failed to get explanation. Check your API key or try again.",
        )


async def code_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "*💻 /code Usage*\n\n"
            "`/code <task>`\n\n"
            "*Example:* `/code CNN image classifier`\n"
            "`/code sentiment analysis with LSTM`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    task = " ".join(context.args)
    user_id = update.effective_user.id
    await send_typing(update, context)

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {
            "role": "user",
            "content": f"Generate clean, well-commented Python code for the "
            f"following ML task: '{task}'. Use popular libraries like NumPy, "
            f"Pandas, scikit-learn, TensorFlow, or PyTorch. Include a brief "
            f"explanation before the code.",
        }
    )

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.4, max_tokens=1024)
    if response:
        add_user_message(user_id, "user", f"/code {task}")
        add_user_message(user_id, "assistant", response)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Failed to generate code. Try again.",
        )


async def compare_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "*⚖️ /compare Usage*\n\n"
            "`/compare <A> vs <B>`\n\n"
            "*Example:* `/compare LSTM vs GRU`\n"
            "`/compare CNN vs Transformer`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    query = " ".join(context.args)
    user_id = update.effective_user.id
    await send_typing(update, context)

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {
            "role": "user",
            "content": f"Compare the following AI/ML concepts in a clear, "
            f"structured way: '{query}'. Use a comparison table format with "
            f"bullet points. Cover differences, similarities, strengths, "
            f"weaknesses, and use cases.",
        }
    )

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.4)
    if response:
        add_user_message(user_id, "user", f"/compare {query}")
        add_user_message(user_id, "assistant", response)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Failed to compare. Try again.",
        )


async def roadmap_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await send_typing(update, context)

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {
            "role": "user",
            "content": "Create a personalised AI/ML learning roadmap for a "
            "B.Tech student (2nd year, familiar with Python and basic ML). "
            "Cover 4 phases: Foundation, Core ML, Deep Learning, Specialisation. "
            "Use a clear timeline (weeks/months), include resources (free ones), "
            "and suggest projects per phase. Format with headers and bullet points.",
        }
    )

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.7)
    if response:
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Failed to generate roadmap. Try again.",
        )


# ─── Quiz State ────────────────────────────────────────────────────────────────
user_quiz: dict[int, dict] = {}


async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await send_typing(update, context)

    # If already in a quiz, show next question
    if user_id in user_quiz and user_quiz[user_id].get("question"):
        await send_question(update, user_id, context)
        return

    # Start fresh quiz
    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {
            "role": "user",
            "content": "Generate one AI/ML multiple choice quiz question with "
            "4 options (A, B, C, D). Include the correct answer at the end "
            "marked as 'Answer: X'. Topic: random fundamental AI/ML concept.",
        }
    )

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.5)
    if response:
        user_quiz[user_id] = {"question": response, "answered": False}
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ Failed to generate quiz. Try again.")


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_quiz:
        return

    quiz = user_quiz[user_id]
    if not quiz.get("question"):
        return

    user_answer = update.message.text.strip().upper()
    if user_answer not in ["A", "B", "C", "D"]:
        await update.message.reply_text(
            "Please answer with A, B, C, or D.", parse_mode=ParseMode.MARKDOWN
        )
        return

    await send_typing(update, context)
    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {"role": "user", "content": quiz["question"]},
    )
    messages.append(
        {
            "role": "user",
            "content": f"The user answered: {user_answer}. "
            f"Tell them if they were correct and explain the answer briefly.",
        }
    )

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.4)

    quiz["question"] = None  # mark as answered
    quiz["answered"] = True

    if response:
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_text(
        "Send /quiz again for the next question! 🚀", parse_mode=ParseMode.MARKDOWN
    )


# ─── ArXiv Fetcher ─────────────────────────────────────────────────────────────
async def paper_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "*📄 /paper Usage*\n\n"
            "`/paper <topic>`\n\n"
            "*Example:* `/paper transformers`\n"
            "`/paper reinforcement learning`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    topic = " ".join(context.args)
    await send_typing(update, context)

    # Fetch from ArXiv API
    import urllib.parse

    query = urllib.parse.quote(topic)
    arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(arxiv_url)

        if response.status_code != 200:
            raise Exception("ArXiv API error")

        from xml.etree import ElementTree as ET

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        entries = root.findall("atom:entry", ns)
        if not entries:
            await update.message.reply_text(
                f"No ArXiv papers found for '{topic}'. Try a different term.",
            )
            return

        lines = [f"*📄 ArXiv Papers — {topic}*\n"]
        for i, entry in enumerate(entries, 1):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            link = entry.find("atom:id", ns)
            authors = entry.findall("atom:author/atom:name", ns)

            title_text = title.text.strip().replace("\n", " ") if title is not None else "N/A"
            summary_text = summary.text.strip().replace("\n", " ")[:300] if summary is not None else ""
            pub_text = published.text[:10] if published is not None else "N/A"
            link_text = link.text if link is not None else ""
            author_text = ", ".join(a.text for a in authors[:3]) if authors else "N/A"
            if len(authors) > 3:
                author_text += " et al."

            lines.append(f"*{i}. {title_text}*")
            lines.append(f"👤 {author_text}")
            lines.append(f"📅 {pub_text}")
            lines.append(f"__Abstract: {summary_text}...__")
            lines.append(f"🔗 {link_text}")
            lines.append("")

        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"ArXiv fetch error: {e}")
        # Fallback to OpenRouter
        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.append(
            {
                "role": "user",
                "content": f"Find information about the latest ArXiv papers on "
                f"'{topic}'. Give a summary of 3-5 recent papers with their titles, "
                f"authors, and key contributions.",
            }
        )
        user_id = update.effective_user.id
        model = get_user_model(user_id)
        response = await call_openrouter(messages, model=model, temperature=0.4)
        if response:
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(
                "❌ Could not fetch papers. Try again later.",
            )


# ─── ArXiv Search (enhanced with better formatting) ──────────────────────────
async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search ArXiv with abstracts and author info"""
    if not context.args:
        await update.message.reply_text(
            "*🔍 /search Usage*\n\n"
            "`/search <topic>`\n\n"
            "*Example:* `/search object detection`\n"
            "`/search graph neural networks`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    topic = " ".join(context.args)
    await send_typing(update, context)

    import urllib.parse

    query = urllib.parse.quote(topic)
    # Search in title and abstract fields
    arxiv_url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=ti:{query}+OR+abs:{query}"
        f"&start=0&max_results=8"
        f"&sortBy=submittedDate"
        f"&sortOrder=descending"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(arxiv_url)

        if response.status_code != 200:
            raise Exception("ArXiv API error")

        from xml.etree import ElementTree as ET

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        entries = root.findall("atom:entry", ns)
        if not entries:
            await update.message.reply_text(
                f"No papers found for '{topic}'. Try different keywords.",
            )
            return

        header = f"*🔍 ArXiv Search — \"{topic}\"*\n__{len(entries)} results__\n"
        await update.message.reply_text(header, parse_mode=ParseMode.MARKDOWN)

        for i, entry in enumerate(entries, 1):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            link = entry.find("atom:id", ns)
            authors = entry.findall("atom:author/atom:name", ns)
            categories = entry.findall("atom:category", ns)

            title_text = title.text.strip().replace("\n", " ") if title is not None else "N/A"
            summary_text = summary.text.strip().replace("\n", " ")[:400] if summary is not None else ""
            pub_text = published.text[:10] if published is not None else "N/A"
            link_text = link.text if link is not None else ""
            author_text = ", ".join(a.text for a in authors[:4]) if authors else "N/A"
            if len(authors) > 4:
                author_text += " et al."
            cats = ", ".join(c.get("term", "") for c in categories[:3])

            msg = (
                f"*{i}. {title_text}*\n"
                f"👤 {author_text}  |  📅 {pub_text}\n"
                f"🏷️ {cats}\n"
                f"__{summary_text}...__\n"
                f"🔗 {link_text}\n"
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(0.3)  # brief pause between messages

    except Exception as e:
        logger.error(f"ArXiv search error: {e}")
        await update.message.reply_text(
            "❌ Could not search ArXiv. Try again later.",
        )


# ─── Project Ideas Generator ─────────────────────────────────────────────────
async def project_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate ML/DL project ideas tailored to user's skill level"""
    if not context.args:
        # General project ideas
        await send_typing(update, context)
        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.append(
            {
                "role": "user",
                "content": "Generate 6 interesting AI/ML project ideas for a B.Tech "
                "student who knows Python, NumPy, Pandas, scikit-learn, and "
                "basic deep learning (TensorFlow/PyTorch). Include a brief "
                "description and suggested datasets for each. "
                "Categorise by difficulty: Beginner, Intermediate, Advanced.",
            }
        )
        user_id = update.effective_user.id
        model = get_user_model(user_id)
        response = await call_openrouter(messages, model=model, temperature=0.7)
        if response:
            await update.message.reply_text(
                f"*💡 AI/ML Project Ideas*\n\n{response}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text("❌ Could not generate ideas. Try again.")
        return

    # Topic-specific project ideas
    topic = " ".join(context.args)
    await send_typing(update, context)

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.append(
        {
            "role": "user",
            "content": f"Generate 5 hands-on AI/ML project ideas focused on: '{topic}'. "
            f"For each project include: name, brief description, tech stack "
            f"(Python libraries), dataset source, and estimated difficulty. "
            f"Make them practical and impressive for a B.Tech portfolio.",
        }
    )

    user_id = update.effective_user.id
    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.7)

    if response:
        await update.message.reply_text(
            f"*💡 Project Ideas — {topic}*\n\n{response}",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.message.reply_text("❌ Could not generate ideas. Try again.")


# ─── Free Chat ─────────────────────────────────────────────────────────────────
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Ignore commands
    if text.startswith("/"):
        return

    await send_typing(update, context)

    messages = [{"role": "system", "content": get_system_prompt()}]
    history = get_user_memory(user_id)
    messages.extend(history)
    messages.append({"role": "user", "content": text})

    model = get_user_model(user_id)
    response = await call_openrouter(messages, model=model, temperature=0.7)

    if response:
        add_user_message(user_id, "user", text)
        add_user_message(user_id, "assistant", response)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Something went wrong. Try again or use /clear to reset.",
        )


# ─── Error Handler ─────────────────────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")


# ─── Main ──────────────────────────────────────────────────────────────────────
async def post_init(application: ApplicationBuilder):
    commands = [
        BotCommand("start", "Welcome & start"),
        BotCommand("help", "Show all commands"),
        BotCommand("clear", "Clear chat memory"),
        BotCommand("model", "Switch AI model"),
        BotCommand("explain", "Explain an AI/ML concept"),
        BotCommand("code", "Generate ML code"),
        BotCommand("quiz", "Start MCQ quiz"),
        BotCommand("paper", "Fetch ArXiv papers"),
        BotCommand("search", "Search ArXiv with abstracts"),
        BotCommand("compare", "Compare two concepts"),
        BotCommand("roadmap", "Personalised learning roadmap"),
        BotCommand("project", "ML project ideas"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands registered.")


def main():
    logger.info("AIML Tutor Bot starting...")

    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        logger.error("TELEGRAM_TOKEN or OPENROUTER_API_KEY not set in .env")
        print("❌ Missing environment variables. Check your .env file.")
        return

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CommandHandler("model", model_cmd))
    app.add_handler(CommandHandler("explain", explain_cmd))
    app.add_handler(CommandHandler("code", code_cmd))
    app.add_handler(CommandHandler("quiz", quiz_cmd))
    app.add_handler(CommandHandler("paper", paper_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("compare", compare_cmd))
    app.add_handler(CommandHandler("roadmap", roadmap_cmd))
    app.add_handler(CommandHandler("project", project_cmd))

    # Callback for model selection
    app.add_handler(CallbackQueryHandler(model_callback, pattern="^model:"))

    # Quiz answer handler (A/B/C/D text messages during quiz)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat,
        )
    )

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("Bot is running!")
    app.run_polling()


if __name__ == "__main__":
    main()
