import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# --- SOZLAMALAR (SETTINGS) ---
# Bot tokenini shu yerga yozing (BotFather'dan olasiz)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8914319934:AAFlcNWO3_5PNKbPIp3IlFquXygpoowz4L4")

# Admin (siz)ning Telegram ID raqamingiz. CV va e'lonlar shu ID'ga yuboriladi.
# ID ni bilmasangiz, @userinfobot ga /start yozing, u sizga ID'ingizni beradi.
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "6123334036")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Suhbat holatlari (conversation states)
WAITING_LISTING = 1
WAITING_JOB_AD = 2
WAITING_CV = 3

MAIN_MENU_TEXT = (
    "👋 Assalomu alaykum!\n\n"
    "Marketplace & Ada | UAE botiga xush kelibsiz.\n"
    "Quyidagilardan birini tanlang:"
)


def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 E'lon berish / ko'rish", callback_data="marketplace")],
        [InlineKeyboardButton("💼 Ish e'lonlari", callback_data="jobs")],
        [InlineKeyboardButton("📄 CV xizmati", callback_data="cv")],
        [InlineKeyboardButton("🎓 Job Academy", callback_data="academy")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard():
    keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(keyboard)


# --- ASOSIY BUYRUQLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
    return ConversationHandler.END


# --- 1. MARKETPLACE BO'LIMI ---

async def marketplace_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("➕ Yangi e'lon berish", callback_data="new_listing")],
        [InlineKeyboardButton("📢 Kanaldagi e'lonlarni ko'rish", url="https://t.me/uzinuae")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")],
    ]
    await query.edit_message_text(
        "🛒 E'lon berish yoki mavjud e'lonlarni ko'rish uchun kanalimizga tashrif buyuring, "
        "yoki yangi e'lon joylashtiring:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def new_listing_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📝 E'loningizni yozing (nomi, narxi, tavsifi va shahar).\n"
        "Rasm qo'shmoqchi bo'lsangiz, matn bilan birga rasmni yuborishingiz mumkin.\n\n"
        "Bekor qilish uchun /cancel yozing.",
        reply_markup=back_keyboard(),
    )
    return WAITING_LISTING


async def new_listing_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.caption or update.message.text or ""
    caption = f"🆕 Yangi e'lon\n👤 @{user.username or user.first_name} (ID: {user.id})\n\n{text}"

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo, caption=caption)
    else:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=caption)

    await update.message.reply_text(
        "✅ E'loningiz qabul qilindi! Tez orada tekshirib, kanalga joylaymiz.",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


# --- 2. ISH E'LONLARI BO'LIMI ---

async def jobs_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📢 Mavjud ish o'rinlarini ko'rish", url="https://t.me/uzinuae")],
        [InlineKeyboardButton("➕ Ish e'loni joylashtirish (ish beruvchi uchun)", callback_data="new_job_ad")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")],
    ]
    await query.edit_message_text("💼 Ish e'lonlari bo'limi:", reply_markup=InlineKeyboardMarkup(keyboard))


async def new_job_ad_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📝 Ish e'loningizni yozing (lavozim, maosh, talablar, aloqa uchun raqam).\n\n"
        "Bekor qilish uchun /cancel yozing.",
        reply_markup=back_keyboard(),
    )
    return WAITING_JOB_AD


async def new_job_ad_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""
    caption = f"🆕 Yangi ish e'loni\n👤 @{user.username or user.first_name} (ID: {user.id})\n\n{text}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=caption)

    await update.message.reply_text(
        "✅ Ish e'loningiz qabul qilindi! Tekshirib, kanalga joylaymiz.",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


# --- 3. CV XIZMATI BO'LIMI ---

async def cv_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📄 CV yuborish", callback_data="send_cv")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")],
    ]
    await query.edit_message_text(
        "📄 CV xizmati.\n"
        "CV faylingizni (PDF/Word) yoki matn ko'rinishida ma'lumotlaringizni yuboring, "
        "biz ko'rib chiqib maslahat beramiz.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def send_cv_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📎 CV faylingizni (PDF/Word) yuboring, yoki ma'lumotlaringizni matn ko'rinishida yozing.\n\n"
        "Bekor qilish uchun /cancel yozing.",
        reply_markup=back_keyboard(),
    )
    return WAITING_CV


async def send_cv_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    caption = f"🆕 Yangi CV\n👤 @{user.username or user.first_name} (ID: {user.id})"

    if update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_CHAT_ID, document=update.message.document.file_id, caption=caption
        )
    else:
        text = update.message.text or ""
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"{caption}\n\n{text}")

    await update.message.reply_text(
        "✅ CV'ingiz qabul qilindi! Ko'rib chiqib, siz bilan bog'lanamiz.",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


# --- 4. JOB ACADEMY BO'LIMI ---

async def academy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("1-qadam: Maqsadni aniqlash", callback_data="academy_step_1")],
        [InlineKeyboardButton("2-qadam: CV tayyorlash", callback_data="academy_step_2")],
        [InlineKeyboardButton("3-qadam: Ish qidirish", callback_data="academy_step_3")],
        [InlineKeyboardButton("4-qadam: Suhbatga tayyorgarlik", callback_data="academy_step_4")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")],
    ]
    await query.edit_message_text(
        "🎓 Job Academy — ishga kirguncha bosqichma-bosqich yo'l-yo'riq.\n"
        "Qaysi bosqichni ko'rmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


ACADEMY_STEPS = {
    "academy_step_1": (
        "1️⃣ Maqsadni aniqlash\n\n"
        "Qaysi sohada ishlamoqchisiz? UAE bozorida qanday kasblar talabga ega — "
        "shularni tahlil qiling va o'zingizga mos yo'nalishni tanlang."
    ),
    "academy_step_2": (
        "2️⃣ CV tayyorlash\n\n"
        "CV'ingizni qisqa, aniq va professional qiling. "
        "Yordam kerak bo'lsa, CV xizmatimizdan foydalaning."
    ),
    "academy_step_3": (
        "3️⃣ Ish qidirish\n\n"
        "Kanalimizdagi ish e'lonlarini kuzatib boring, "
        "shuningdek LinkedIn va boshqa saytlarda ham faol bo'ling."
    ),
    "academy_step_4": (
        "4️⃣ Suhbatga tayyorgarlik\n\n"
        "Ko'p so'raladigan savollarga javob tayyorlang, "
        "o'zingiz haqingizda qisqa va ishonchli gapira olishni mashq qiling."
    ),
}


async def academy_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = ACADEMY_STEPS.get(query.data, "Ma'lumot topilmadi.")
    keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="academy_back")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def academy_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await academy_menu(update, context)


# --- BEKOR QILISH ---

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
    app.add_handler(CallbackQueryHandler(marketplace_menu, pattern="^marketplace$"))
    app.add_handler(CallbackQueryHandler(jobs_menu, pattern="^jobs$"))
    app.add_handler(CallbackQueryHandler(cv_menu, pattern="^cv$"))
    app.add_handler(CallbackQueryHandler(academy_menu, pattern="^academy$"))
    app.add_handler(CallbackQueryHandler(academy_step, pattern="^academy_step_"))
    app.add_handler(CallbackQueryHandler(academy_back, pattern="^academy_back$"))

    listing_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_listing_start, pattern="^new_listing$")],
        states={
            WAITING_LISTING: [MessageHandler(filters.TEXT | filters.PHOTO, new_listing_receive)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    job_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_job_ad_start, pattern="^new_job_ad$")],
        states={WAITING_JOB_AD: [MessageHandler(filters.TEXT, new_job_ad_receive)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    cv_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(send_cv_start, pattern="^send_cv$")],
        states={WAITING_CV: [MessageHandler(filters.TEXT | filters.Document.ALL, send_cv_receive)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(listing_conv)
    app.add_handler(job_conv)
    app.add_handler(cv_conv)

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
