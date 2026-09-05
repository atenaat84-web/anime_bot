import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ====================== TOKEN ======================
TOKEN = os.getenv("BOT_TOKEN")   # تو Railway اینو به عنوان متغیر محیطی می‌ذاری

# ====================== DATA ======================

# نمونه آهنگ‌های ژاپنی (بعداً می‌تونی بیشتر اضافه کنی)
SONGS = [
    {
        "title": "Gurenge - LiSA",
        "anime": "Demon Slayer",
        "youtube": "https://www.youtube.com/watch?v=CwkzvkhN5n8",
        "spotify": "https://open.spotify.com/track/0qvsP5i3V6y0x0x0x0x0x0",  # لینک واقعی بذار
        "instagram": "https://www.instagram.com/lisa_official/"
    },
    {
        "title": "Kick Back - Kenshi Yonezu",
        "anime": "Chainsaw Man",
        "youtube": "https://www.youtube.com/watch?v=f1rQWcG-b4Y",
        "spotify": "https://open.spotify.com/track/...",
        "instagram": "https://www.instagram.com/kenshiyonezu_official/"
    },
    {
        "title": "Idol - YOASOBI",
        "anime": "Oshi no Ko",
        "youtube": "https://www.youtube.com/watch?v=ZRtdQ81jPUQ",
        "spotify": "https://open.spotify.com/track/...",
        "instagram": "https://www.instagram.com/yoasobi_staff/"
    },
]

# کانجی‌های N5 و N4 (نمونه)
KANJI_LIST = [
    {"kanji": "日", "reading": "にち / ひ", "meaning": "day / sun", "level": "N5"},
    {"kanji": "本", "reading": "ほん", "meaning": "book / origin", "level": "N5"},
    {"kanji": "人", "reading": "ひと / じん", "meaning": "person", "level": "N5"},
    {"kanji": "水", "reading": "みず / すい", "meaning": "water", "level": "N5"},
    {"kanji": "火", "reading": "ひ / か", "meaning": "fire", "level": "N5"},
    {"kanji": "車", "reading": "くるま / しゃ", "meaning": "car", "level": "N4"},
    {"kanji": "電", "reading": "でん", "meaning": "electricity", "level": "N4"},
    {"kanji": "話", "reading": "はなし / わ", "meaning": "talk / story", "level": "N4"},
    {"kanji": "食", "reading": "た / しょく", "meaning": "eat / food", "level": "N4"},
    {"kanji": "見", "reading": "み", "meaning": "see / look", "level": "N4"},
]

# ====================== FUNCTIONS ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎌 Anime Recommendation", callback_data="anime")],
        [InlineKeyboardButton("🎵 Japanese Song", callback_data="music")],
        [InlineKeyboardButton("📝 Kanji Quiz (N5/N4)", callback_data="kanji")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! I'm your Anime & Japanese helper bot.\n\nWhat would you like to do?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "anime":
        await send_anime(query)
    elif query.data == "music":
        await send_music(query)
    elif query.data == "kanji":
        await start_kanji_quiz(query, context)
    elif query.data.startswith("kanji_answer_"):
        await check_kanji_answer(query, context)

async def send_anime(query):
    try:
        # استفاده از API رایگان Jikan
        res = requests.get("https://api.jikan.moe/v4/random/anime", timeout=10)
        data = res.json()["data"]

        title = data.get("title", "Unknown")
        title_english = data.get("title_english") or title
        genres = ", ".join([g["name"] for g in data.get("genres", [])][:3]) or "Unknown"
        synopsis = data.get("synopsis") or "No synopsis available."
        if len(synopsis) > 400:
            synopsis = synopsis[:400] + "..."

        score = data.get("score") or "N/A"
        url = data.get("url", "")

        text = f"""🎌 *Anime Recommendation*

*Title:* {title_english}
*Japanese Title:* {title}
*Genres:* {genres}
*Score:* {score}

*Synopsis:*
{synopsis}

[More info on MyAnimeList]({url})
"""
        await query.edit_message_text(text, parse_mode="Markdown", disable_web_page_preview=False)
    except Exception as e:
        await query.edit_message_text("Sorry, couldn't fetch anime right now. Please try again.")

async def send_music(query):
    song = random.choice(SONGS)
    text = f"""🎵 *Japanese Song Recommendation*

*{song['title']}*
From: {song['anime']}

🔗 Links:
• [YouTube]({song['youtube']})
• [Spotify]({song['spotify']})
• [Instagram]({song['instagram']})
"""
    await query.edit_message_text(text, parse_mode="Markdown", disable_web_page_preview=True)

async def start_kanji_quiz(query, context):
    kanji = random.choice(KANJI_LIST)
    context.user_data["current_kanji"] = kanji

    # ساخت گزینه‌های غلط
    wrongs = random.sample([k for k in KANJI_LIST if k != kanji], 3)
    options = [kanji["meaning"]] + [w["meaning"] for w in wrongs]
    random.shuffle(options)

    keyboard = []
    for i, opt in enumerate(options):
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"kanji_answer_{i}_{opt}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""📝 *Kanji Quiz* ({kanji['level']})

What is the meaning of this kanji?

*{kanji['kanji']}*
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def check_kanji_answer(query, context):
    data = query.data.split("_", 2)
    selected = data[2]
    correct = context.user_data.get("current_kanji", {}).get("meaning")

    if selected == correct:
        text = f"✅ Correct!\n\n*{context.user_data['current_kanji']['kanji']}* means *{correct}*\nReading: {context.user_data['current_kanji']['reading']}"
    else:
        text = f"❌ Wrong!\n\nCorrect answer: *{correct}*\nReading: {context.user_data['current_kanji']['reading']}"

    keyboard = [[InlineKeyboardButton("Next Kanji →", callback_data="kanji")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ====================== MAIN ======================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()