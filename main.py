import logging
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
waiting_male = []
waiting_female = []
active_chats = {}
message_map = {}  # message_id -> user_id

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
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 سلام!\n\nبرای استفاده از ربات باید عضو کانال‌های زیر بشی:",
            reply_markup=reply_markup
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
        [InlineKeyboardButton("💘 رل‌یابی", callback_data="find_match")],
        [InlineKeyboardButton("👤 پروفایل من", callback_data="my_profile")],
        [InlineKeyboardButton("👻 ربات وحشتناک", url="https://t.me/LoaLo_ma_si_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎉 خوش اومدی!\n\nچیکار میخوای بکنی؟",
        reply_markup=reply_markup
    )

async def show_main_menu_query(query, context):
    keyboard = [
        [InlineKeyboardButton("💘 رل‌یابی", callback_data="find_match")],
        [InlineKeyboardButton("👤 پروفایل من", callback_data="my_profile")],
        [InlineKeyboardButton("👻 ربات وحشتناک", url="https://t.me/LoaLo_ma_si_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "🎉 خوش اومدی!\n\nچیکار میخوای بکنی؟",
        reply_markup=reply_markup
    )

async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("👦 پسر", callback_data="gender_male")],
        [InlineKeyboardButton("👧 دختر", callback_data="gender_female")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("جنسیتت چیه؟", reply_markup=reply_markup)
    return GENDER

async def gender_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = 'male' if query.data == 'gender_male' else 'female'
    await query.message.reply_text("چند سالته؟ (عدد بنویس)")
    return AGE

async def age_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age_text = update.message.text
    if not age_text.isdigit():
        await update.message.reply_text("❌ لطفاً فقط عدد بنویس!")
        return AGE
    context.user_data['age'] = int(age_text)
    await update.message.reply_text("از کدوم شهری؟")
    return CITY

async def city_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['city'] = update.message.text
    context.user_data['username'] = user.username or "ندارد"

    users[user.id] = {
        'gender': context.user_data['gender'],
        'age': context.user_data['age'],
        'city': context.user_data['city'],
        'username': context.user_data['username']
    }

    gender = context.user_data['gender']

    await update.message.reply_text(
        "✅ ثبت‌نامت انجام شد!\n\n"
        "🔍 داریم دنبال رل مناسب میگردیم...\n"
        "⏳ کمی صبر کن!"
    )

    msg = await context.bot.send_message(
        ADMIN_ID,
        f"💘 کاربر جدید:\n"
        f"آیدی: {user.id}\n"
        f"یوزرنیم: @{context.user_data['username']}\n"
        f"جنسیت: {'پسر' if gender == 'male' else 'دختر'}\n"
        f"سن: {context.user_data['age']}\n"
        f"شهر: {context.user_data['city']}\n\n"
        f"👆 روی این پیام Reply کن تا جواب بدی!"
    )

    message_map[msg.message_id] = user.id

    await asyncio.sleep(10)

    active_chats[user.id] = True

    await context.bot.send_message(
        user.id,
        "💘 رلت پیدا شد!\n\nحالا میتونید شروع به صحبت کنید! 😊"
    )

    return ConversationHandler.END

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # ادمین داره Reply میکنه
    if user.id == ADMIN_ID:
        if update.message.reply_to_message:
            replied_id = update.message.reply_to_message.message_id
            if replied_id in message_map:
                target_id = message_map[replied_id]
                await context.bot.send_message(
                    target_id,
                    f"💬 رلت: {text}"
                )
                await update.message.reply_text("✅ پیام فرستاده شد!")
                return

    # کاربر عادی پیام میده
    if user.id in active_chats and active_chats[user.id]:
        msg = await context.bot.send_message(
            ADMIN_ID,
            f"💬 پیام از رل:\n"
            f"آیدی: {user.id}\n"
            f"پیام: {text}"
        )
        message_map[msg.message_id] = user.id
        await update.message.reply_text("✅ پیامت فرستاده شد!")

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in users:
        await query.message.reply_text("❌ هنوز ثبت‌نام نکردی!")
        return

    u = users[user_id]
    await query.message.reply_text(
        f"👤 پروفایل تو:\n\n"
        f"جنسیت: {'پسر' if u['gender'] == 'male' else 'دختر'}\n"
        f"سن: {u['age']}\n"
        f"شهر: {u['city']}"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(find_match, pattern="^find_match$")],
        states={
            GENDER: [CallbackQueryHandler(gender_chosen, pattern="^gender_")],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_received)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_received)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(my_profile, pattern="^my_profile$"))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("✅ ربات شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
