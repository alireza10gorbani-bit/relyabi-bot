import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = "8837276103:AAFhMbiFNGgoh6z5Hb_pyrSGY4K5ejP-K_8"
ADMIN_ID = 8678262416
CHANNELS = ["@LoLo_funny2", "@LoLo_funny", "@LoLo_LoLo_Lo_Lo"]

GENDER, AGE, CITY = range(3)

users = {}
active_chats = {}
message_map = {}

CITIES = [
    "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "اهواز", "قم",
    "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
    "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج", "قزوین",
    "خرم‌آباد", "گرگان", "ساری", "بوشهر", "بجنورد", "سمنان", "شهرکرد",
    "ایلام", "یاسوج", "بیرجند", "مهاباد", "خوی", "مراغه", "سبزوار",
    "نیشابور", "آمل", "بابل", "قائم‌شهر", "لاهیجان", "انزلی", "خمین",
    "نجف‌آباد", "کاشان", "دزفول", "آبادان", "خرمشهر", "بروجرد", "ملایر",
    "تویسرکان", "نهاوند", "سقز", "مریوان", "بانه", "قروه", "دیواندره",
    "پاوه", "جوانرود", "سرپل‌ذهاب", "اسلام‌آباد غرب", "بیجار", "شهریار",
    "ورامین", "پاکدشت", "دماوند", "فیروزکوه", "رباط‌کریم", "ملارد",
    "نظرآباد", "هشتگرد", "طالقان", "تنکابن", "رامسر", "چالوس", "نوشهر",
    "بهشهر", "نکا", "جویبار", "فریدونکنار", "محمودآباد", "رودسر",
    "صومعه‌سرا", "فومن", "شفت", "آستارا", "تالش", "ماسال", "رضوانشهر",
    "گنبدکاووس", "علی‌آباد", "کردکوی", "بندرترکمن", "مینودشت",
    "شاهرود", "دامغان", "گرمسار", "مهدیشهر", "میامی", "آران‌وبیدگل",
    "بهبهان", "مسجدسلیمان", "شوشتر", "شوش", "ایذه", "رامهرمز", "آغاجاری",
    "گچساران", "فسا", "جهرم", "لار", "لامرد", "داراب", "آباده", "مرودشت",
    "صدرا", "زرقان", "نی‌ریز", "استهبان", "اقلید", "ممسنی", "کازرون",
    "سیرجان", "رفسنجان", "بم", "جیرفت", "بافت", "زابل", "خاش", "ایرانشهر",
    "چابهار", "نیکشهر", "میناب", "قشم", "کیش", "لنگه", "حاجی‌آباد",
    "دیلم", "خارک", "گناوه", "دشتستان", "تنگستان", "دشتی", "جم",
    "عسلویه", "نورآباد", "پلدختر", "ازنا", "الیگودرز", "دورود", "کوهدشت",
    "سلسله", "رومشکان", "فلاورجان", "مبارکه", "خمینی‌شهر", "شاهین‌شهر",
    "گلپایگان", "خوانسار", "اردستان", "نطنز", "تیران", "لنجان", "فریدن",
    "چادگان", "دهاقان", "برخوار", "میمه", "سامان", "لردگان", "اردل",
    "کوهرنگ", "فارسان", "بروجن", "هفشجان", "ملکشاهی", "آبدانان", "دره‌شهر",
    "مهران", "دهلران", "چرداول", "شیروان", "فاروج", "مانه", "جاجرم",
    "اسفراین", "درگز", "قوچان", "چناران", "تربت‌جام", "تربت‌حیدریه",
    "کاشمر", "خلیل‌آباد", "فریمان", "طرقبه", "گناباد", "بردسکن",
    "خواف", "رشتخوار", "سرخس", "تایباد", "باخرز", "زاوه", "کلات",
    "هشترود", "میانه", "بستان‌آباد", "سراب", "هادیشهر", "جلفا",
    "اهر", "هریس", "ورزقان", "کلیبر", "چاراویماق", "شبستر", "اسکو",
    "بناب", "ملکان", "عجب‌شیر", "مراغه", "بوکان", "تکاب", "شاهین‌دژ",
    "پیرانشهر", "نقده", "سردشت", "اشنویه", "سلماس"
]

async def check_membership(user_id, context):
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id, context)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("📢 کانال ۱", url="https://t.me/LoLo_funny2")],
            [InlineKeyboardButton("📢 کانال ۲", url="https://t.me/LoLo_funny")],
            [InlineKeyboardButton("📢 کانال ۳", url="https://t.me/LoLo_LoLo_Lo_Lo")],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🚫 *دسترسی محدود!*\n\n"
            "برای استفاده از ربات باید عضو کانال‌های زیر بشی 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    await show_main_menu(update, context)

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    is_member = await check_membership(user_id, context)
    if not is_member:
        await query.message.reply_text("❌ هنوز عضو همه کانال‌ها نشدی!")
        return
    await show_main_menu_query(query, context)

async def show_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("💘 رُل‌یابی", callback_data="find_match")],
        [InlineKeyboardButton("👤 پروفایل من", callback_data="my_profile")]
    ]
    await update.message.reply_text(
        "🔥 *به ربات رُل‌یابی خوش اومدی!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💫 اینجا رُل واقعیت پیدا میشه!\n"
        "━━━━━━━━━━━━━━━\n\n"
        "چیکار میخوای بکنی؟ 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_main_menu_query(query, context):
    keyboard = [
        [InlineKeyboardButton("💘 رُل‌یابی", callback_data="find_match")],
        [InlineKeyboardButton("👤 پروفایل من", callback_data="my_profile")]
    ]
    await query.message.reply_text(
        "🔥 *به ربات رُل‌یابی خوش اومدی!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💫 اینجا رُل واقعیت پیدا میشه!\n"
        "━━━━━━━━━━━━━━━\n\n"
        "چیکار میخوای بکنی؟ 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("👦 پسر", callback_data="gender_male")],
        [InlineKeyboardButton("👧 دختر", callback_data="gender_female")]
    ]
    await query.message.reply_text(
        "💫 *مرحله ۱ از ۳*\n\n"
        "جنسیتت چیه؟ 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return GENDER

async def gender_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = 'male' if query.data == 'gender_male' else 'female'
    await query.message.reply_text(
        "💫 *مرحله ۲ از ۳*\n\n"
        "چند سالته؟\n"
        "_(بین ۱۰ تا ۵۰ سال)_",
        parse_mode="Markdown"
    )
    return AGE

async def age_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age_text = update.message.text
    if not age_text.isdigit():
        await update.message.reply_text("❌ فقط عدد بنویس!")
        return AGE
    age = int(age_text)
    if age < 10 or age > 50:
        await update.message.reply_text("❌ سن باید بین ۱۰ تا ۵۰ سال باشه!")
        return AGE
    context.user_data['age'] = age

    # ساخت کیبورد شهرها
    keyboard = []
    row = []
    for i, city in enumerate(CITIES):
        row.append(InlineKeyboardButton(city, callback_data=f"city_{city}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "💫 *مرحله ۳ از ۳*\n\n"
        "از کدوم شهری؟ 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CITY

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data.replace("city_", "")
    context.user_data['city'] = city

    user = query.from_user
    context.user_data['username'] = user.username or "ندارد"

    users[user.id] = {
        'gender': context.user_data['gender'],
        'age': context.user_data['age'],
        'city': city,
        'username': context.user_data['username']
    }

    gender = context.user_data['gender']

    await query.message.reply_text(
        "⏳ *داریم دنبال رُلت میگردیم...*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💫 کمی صبر کن، بهترین رُل رو پیدا میکنیم!\n"
        "━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

    msg = await context.bot.send_message(
        ADMIN_ID,
        f"💘 *کاربر جدید وارد رُل‌یابی شد:*\n\n"
        f"👤 آیدی: `{user.id}`\n"
        f"🔗 یوزرنیم: @{context.user_data['username']}\n"
        f"⚧ جنسیت: {'👦 پسر' if gender == 'male' else '👧 دختر'}\n"
        f"🎂 سن: {context.user_data['age']}\n"
        f"🏙 شهر: {city}\n\n"
        f"👆 *روی این پیام Reply کن تا جواب بدی!*",
        parse_mode="Markdown"
    )

    message_map[msg.message_id] = user.id

    await asyncio.sleep(10)

    active_chats[user.id] = True

    keyboard = [[InlineKeyboardButton("❌ پایان چت", callback_data="end_chat")]]
    await context.bot.send_message(
        user.id,
        "💘 *رُلت پیدا شد!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "✨ حالا میتونید شروع به صحبت کنید!\n"
        "━━━━━━━━━━━━━━━\n\n"
        "برای پایان دادن به چت دکمه زیر رو بزن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id in active_chats:
        del active_chats[user_id]

    await query.message.reply_text(
        "👋 *چت پایان یافت!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "میتونی دوباره رُل‌یابی کنی 😊\n"
        "━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

    await context.bot.send_message(
        ADMIN_ID,
        f"❌ کاربر `{user_id}` چت رو پایان داد.",
        parse_mode="Markdown"
    )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if user.id == ADMIN_ID:
        if update.message.reply_to_message:
            replied_id = update.message.reply_to_message.message_id
            if replied_id in message_map:
                target_id = message_map[replied_id]
                await context.bot.send_message(
                    target_id,
                    f"💬 *رُلت:*\n{text}",
                    parse_mode="Markdown"
                )
                await update.message.reply_text("✅ پیام فرستاده شد!")
                return

    if user.id in active_chats and active_chats[user.id]:
        msg = await context.bot.send_message(
            ADMIN_ID,
            f"💬 *پیام از رُل:*\n\n"
            f"آیدی: `{user.id}`\n"
            f"پیام: {text}\n\n"
            f"👆 Reply کن تا جواب بدی!",
            parse_mode="Markdown"
        )
        message_map[msg.message_id] = user.id
        await update.message.reply_text("✅ پیامت فرستاده شد!")

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in users:
        await query.message.reply_text(
            "❌ هنوز ثبت‌نام نکردی!\n\nبرو رُل‌یابی رو بزن 😊"
        )
        return

    u = users[user_id]
    await query.message.reply_text(
        f"👤 *پروفایل تو:*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚧ جنسیت: {'👦 پسر' if u['gender'] == 'male' else '👧 دختر'}\n"
        f"🎂 سن: {u['age']}\n"
        f"🏙 شهر: {u['city']}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(find_match, pattern="^find_match$")],
        states={
            GENDER: [CallbackQueryHandler(gender_chosen, pattern="^gender_")],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_received)],
            CITY: [CallbackQueryHandler(city_chosen, pattern="^city_")],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(my_profile, pattern="^my_profile$"))
    app.add_handler(CallbackQueryHandler(end_chat, pattern="^end_chat$"))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("✅ ربات شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
