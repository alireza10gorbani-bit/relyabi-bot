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
    context.user_data['user_id'] = user.id
    context.user_data['username'] = user.username or "ندارد"

    users[user.id] = {
        'gender': context.user_data['gender'],
        'age': context.user_data['age'],
        'city': context.user_data['city'],
        'username': context.user_data['username']
    }

    gender = context.user_data['gender']

    if gender == 'male':
        waiting_male.append(user.id)
    else:
        waiting_female.append(user.id)

    await update.message.reply_text(
        "✅ ثبت‌نامت انجام شد!\n\n"
        "🔍 داریم دنبال رل مناسب میگردیم...\n"
        "⏳ تا ۵ دقیقه صبر کن!"
    )

    await context.bot.send_message(
        ADMIN_ID,
        f"👤 کاربر جدید:\n"
        f"آیدی: {user.id}\n"
        f"یوزرنیم: @{context.user_data['username']}\n"
        f"جنسیت: {'پسر' if gender == 'male' else 'دختر'}\n"
        f"سن: {context.user_data['age']}\n"
        f"شهر: {context.user_data['city']}"
    )

    asyncio.create_task(find_partner(user.id, context))
    return ConversationHandler.END

async def find_partner(user_id, context):
    await asyncio.sleep(300)

    if user_id not in users:
        return

    user = users[user_id]
    gender = user['gender']

    if gender == 'male' and waiting_female:
        partner_id = waiting_female.pop(0)
        if user_id in waiting_male:
            waiting_male.remove(user_id)
    elif gender == 'female' and waiting_male:
        partner_id = waiting_male.pop(0)
        if user_id in waiting_female:
            waiting_female.remove(user_id)
    else:
        await context.bot.send_message(
            user_id,
            "😔 الان کسی پیدا نشد. بعداً دوباره امتحان کن!"
        )
        return

    if partner_id not in users:
        return

    partner = users[partner_id]

    msg1 = (
        f"💘 رلت پیدا شد!\n\n"
        f"جنسیت: {'پسر' if partner['gender'] == 'male' else 'دختر'}\n"
        f"سن: {partner['age']}\n"
        f"شهر: {partner['city']}\n"
        f"یوزرنیم: @{partner['username']}"
    )

    msg2 = (
        f"💘 رلت پیدا شد!\n\n"
        f"جنسیت: {'پسر' if user['gender'] == 'male' else 'دختر'}\n"
        f"سن: {user['age']}\n"
        f"شهر: {user['city']}\n"
        f"یوزرنیم: @{user['username']}"
    )

    await context.bot.send_message(user_id, msg1)
    await context.bot.send_message(partner_id, msg2)

    await context.bot.send_message(
        ADMIN_ID,
        f"✅ match انجام شد!\n"
        f"کاربر ۱: @{user['username']} ({user['city']})\n"
        f"کاربر ۲: @{partner['username']} ({partner['city']})"
    )

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

    print("✅ ربات شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
