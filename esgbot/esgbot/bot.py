from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN
from checker import check_all_sources
from database import init_db
from summarizer import generate_summary

from sources.gri import fetch_gri_news
from sources.issb import fetch_issb_news
from sources.eu_commission import fetch_eu_updates
from sources.kazakhstan import fetch_kz_updates

init_db()

async def send_updates(updates: list, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    if not updates:
        await context.bot.send_message(chat_id, "✅ Новых ESG-обновлений не найдено.")
        return

    await context.bot.send_message(chat_id, f"📬 Найдено новых обновлений: {len(updates)}")

    for item in updates[:5]:
        title       = item.get("title", "")
        description = item.get("description") or item.get("summary", "")
        link        = item.get("link", "")
        source      = item.get("source", "Update")
        date        = item.get("date") or item.get("published", "")

        summary = generate_summary(title, description)

        message = (
            f"🌿 <b>{source}</b>"
            + (f"  •  <i>{date}</i>" if date else "")
            + f"\n<b>{title}</b>\n\n"
            + f"{summary}\n\n"
            + f'🔗 <a href="{link}">Read full article</a>'
        )

        await context.bot.send_message(
            chat_id,
            message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        context.job_queue.run_repeating(
            scheduled_check,
            interval=60 * 60 * 24 * 7,
            first=10,
            chat_id=chat_id,
            name=str(chat_id),
        )
        scheduler_status = "🕐 Еженедельная автопроверка <b>включена</b>."
    else:
        scheduler_status = "🕐 Еженедельная автопроверка уже работает."

    await update.message.reply_text(
        "🌿 <b>ESG Regulatory Updates Bot</b>\n\n"
        "Бот отслеживает обновления ESG-стандартов:\n\n"
        f"• <a href='https://www.ifrs.org/news-and-events/news/'>ISSB (ifrs.org)</a>\n"
        f"• <a href='https://www.globalreporting.org/news/news-center/'>GRI (globalreporting.org)</a>\n"
        f"• <a href='https://ec.europa.eu/commission/presscorner/home/en'>EU Commission</a>\n"
        f"• <a href='https://aifc.kz/news/'>Kazakhstan (AIFC)</a>\n"
        f"• <a href='https://afsa.aifc.kz/news/'>Kazakhstan (AFSA)</a>\n"
        f"• <a href='https://gfc.aifc.kz/en/news'>Kazakhstan (GFC AIFC)</a>\n\n"
        f"{scheduler_status}\n\n"
        "Команды:\n"
        "/check — проверить все источники сразу\n"
        "/news issb — новости ISSB\n"
        "/news gri — новости GRI\n"
        "/news eu — новости EU Commission\n"
        "/news kz — новости Казахстан\n"
        "/start — это сообщение",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Проверяю источники, подождите...")
    new_updates = check_all_sources(str(update.effective_chat.id))
    await send_updates(new_updates, context, update.effective_chat.id)




async def scheduled_check(context: ContextTypes.DEFAULT_TYPE):
    """Запускается автоматически раз в неделю для каждого подписанного пользователя."""
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id, "🕐 Еженедельная автопроверка ESG-обновлений...")
    new_updates = check_all_sources(str(chat_id))
    await send_updates(new_updates, context, chat_id)

SOURCES_MAP = {
    "issb": ("ISSB",                fetch_issb_news),
    "gri":  ("GRI",                 fetch_gri_news),
    "eu":   ("EU Commission",       fetch_eu_updates),
    "kz":   ("Kazakhstan",          fetch_kz_updates),
}

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args:
        await update.message.reply_text(
            "ℹ️ Укажите источник:\n\n"
            "/news issb — ISSB (ifrs.org)\n"
            "/news gri — GRI\n"
            "/news eu — EU Commission\n"
            "/news kz — Kazakhstan (AIFC + AFSA)",
        )
        return

    key = args[0].lower()
    if key not in SOURCES_MAP:
        await update.message.reply_text(
            f"❌ Источник <b>{args[0]}</b> не найден.\n\n"
            "Доступные: issb, gri, eu, kz",
            parse_mode="HTML"
        )
        return

    source_name, fetch_fn = SOURCES_MAP[key]
    await update.message.reply_text(f"🔍 Загружаю новости {source_name}...")

    try:
        items = fetch_fn()
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при загрузке {source_name}: {e}")
        return

    if not items:
        await update.message.reply_text(f"📭 Новостей по {source_name} не найдено.")
        return

    await update.message.reply_text(f"📬 {source_name}: найдено {len(items)} новостей")

    for item in items[:5]:
        title       = item.get("title", "")
        description = item.get("description") or item.get("summary", "")
        link        = item.get("link", "")
        date        = item.get("date") or item.get("published", "")

        summary = generate_summary(title, description)

        message = (
            f"🌿 <b>{item.get('source', source_name)}</b>"
            + (f"  •  <i>{date}</i>" if date else "")
            + f"\n<b>{title}</b>\n\n"
            + f"{summary}\n\n"
            + f'🔗 <a href="{link}">Read full article</a>'
        )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 <b>ESG Regulatory Updates Bot — Help</b>\n\n"
        "<b>Команды:</b>\n"
        "/start — запуск бота и подписка на еженедельные обновления\n"
        "/check — проверить все источники прямо сейчас\n"
        "/news issb — новости ISSB (ifrs.org)\n"
        "/news gri — новости GRI (globalreporting.org)\n"
        "/news eu — новости EU Commission\n"
        "/news kz — новости Казахстан (AIFC + AFSA)\n"
        "/help — это сообщение\n\n"
        "<b>Источники мониторинга:</b>\n"
        "• <a href='https://www.ifrs.org/news-and-events/news/'>ISSB</a> — стандарты устойчивого развития\n"
        "• <a href='https://www.globalreporting.org/news/news-center/'>GRI</a> — глобальная отчётность\n"
        "• <a href='https://ec.europa.eu/commission/presscorner/home/en'>EU Commission</a> — ESG-регулирование ЕС\n"
        "• <a href='https://aifc.kz/news/'>AIFC</a> — Казахстан, финансовый центр\n"
        "• <a href='https://afsa.aifc.kz/news/'>AFSA</a> — регулятор AIFC\n\n"
        "• <a href='https://gfc.aifc.kz/en/news'>GFC AIFC</a> — зелёные финансы Казахстана\n\n"
        "<b>Как работает бот:</b>\n"
        "Каждую неделю бот автоматически проверяет все источники "
        "и присылает новые ESG-обновления с AI-summary.",
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# ─── Сборка и запуск ─────────────────────────────────────────────────────────

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("news", news))
app.add_handler(CommandHandler("help", help_command))
app.run_polling()
