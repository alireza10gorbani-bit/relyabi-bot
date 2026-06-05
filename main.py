import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = "8837276103:AAFhMbiFNGgoh6z5Hb_pyrSGY4K5ejP-K_8"
ADMIN_ID = 8678262416
CHANNELS = ["@LoLo_funny2", "@LoLo_funny", "@LoLo_LoLo_Lo_Lo"]
CARD_NUMBER = "6037701210299613"
CARD_NAME = "بنیامین"

PLATFORM, AMOUNT, LINK = range(3)
CHARGE_AMOUNT, CHARGE_RECEIPT = range(3, 5)

wallets = {}
orders = {}

def get_wallet(user_id):
    if user_id not in wallets:
        wallets[user_id] = 0
    return wallets[user_id]

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
            "🚫 *دسترسی محدود!*\n\nبرای استفاده از ربات باید عضو کانال‌های زیر بشی 👇",
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
    user_id = update.effective_user.id
    balance = get_wallet(user_id)
    keyboard = [
        [InlineKeyboardButton("📦 ثبت سفارش", callback_data="new_order")],
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")],
        [InlineKeyboardButton("👛 موجودی من", callback_data="my_wallet")],
        [InlineKeyboardButton("📋 قوانین", callback_data="rules")],
        [InlineKeyboardButton("👨‍💻 پشتیبانی", callback_data="support")]
    ]
    await update.message.reply_text(
        f"💎 *به ربات فروش ممبر خوش اومدی!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👛 موجودی شما: *{balance} تومن*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 *خدمات ما:*\n"
        f"├ 📱 ممبر فیک تلگرام\n"
        f"└ 📲 ممبر فیک روبیکا\n\n"
        f"⚡️ تحویل سریع | 24 ساعته\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"یه گزینه انتخاب کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_main_menu_query(query, context):
    user_id = query.from_user.id
    balance = get_wallet(user_id)
    keyboard = [
        [InlineKeyboardButton("📦 ثبت سفارش", callback_data="new_order")],
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")],
        [InlineKeyboardButton("👛 موجودی من", callback_data="my_wallet")],
        [InlineKeyboardButton("📋 قوانین", callback_data="rules")],
        [InlineKeyboardButton("👨‍💻 پشتیبانی", callback_data="support")]
    ]
    await query.message.reply_text(
        f"💎 *به ربات فروش ممبر خوش اومدی!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👛 موجودی شما: *{balance} تومن*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 *خدمات ما:*\n"
        f"├ 📱 ممبر فیک تلگرام\n"
        f"└ 📲 ممبر فیک روبیکا\n\n"
        f"⚡️ تحویل سریع | 24 ساعته\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"یه گزینه انتخاب کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def my_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    balance = get_wallet(user_id)
    keyboard = [
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await query.message.reply_text(
        f"👛 *کیف پول شما:*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 موجودی: *{balance} تومن*\n"
        f"━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def charge_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        f"💰 *افزایش موجودی*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💳 شماره کارت: `{CARD_NUMBER}`\n"
        f"👤 به نام: *{CARD_NAME}*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"مبلغ مورد نظر رو بنویس 👇\n"
        f"_(مثلاً: 50000)_",
        parse_mode="Markdown"
    )
    return CHARGE_AMOUNT

async def charge_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("❌ فقط عدد بنویس!")
        return CHARGE_AMOUNT
    context.user_data['charge_amount'] = int(text)
    await update.message.reply_text(
        f"✅ *مبلغ: {text} تومن*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"حالا تصویر رسید پرداخت رو بفرست 👇",
        parse_mode="Markdown"
    )
    return CHARGE_RECEIPT

async def charge_receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    amount = context.user_data['charge_amount']

    await update.message.reply_text(
        "⏳ *رسیدت دریافت شد!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "منتظر تایید ادمین باش 🙏\n"
        "━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ تایید شارژ", callback_data=f"charge_confirm_{user.id}_{amount}"),
            InlineKeyboardButton("❌ رد", callback_data=f"charge_reject_{user.id}")
        ]
    ]

    caption = (
        f"💰 *درخواست شارژ کیف پول:*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 آیدی: `{user.id}`\n"
        f"🔗 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"💵 مبلغ: {amount} تومن\n"
        f"━━━━━━━━━━━━━━━"
    )

    if update.message.photo:
        await context.bot.send_photo(
            ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            ADMIN_ID,
            caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    return ConversationHandler.END

async def charge_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    user_id = int(parts[2])
    amount = int(parts[3])

    wallets[user_id] = get_wallet(user_id) + amount

    await context.bot.send_message(
        user_id,
        f"✅ *موجودی شما شارژ شد!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 مبلغ افزوده شده: *{amount} تومن*\n"
        f"👛 موجودی فعلی: *{wallets[user_id]} تومن*\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ {amount} تومن به کیف پول کاربر اضافه شد!")

async def charge_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[2])

    await context.bot.send_message(
        user_id,
        "❌ *شارژ کیف پول تایید نشد!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "رسید پرداخت تایید نشد.\n"
        "لطفاً دوباره تلاش کن.\n"
        "━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("❌ شارژ رد شد!")

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    balance = get_wallet(user_id)

    keyboard = [
        [InlineKeyboardButton("📱 ممبر تلگرام", callback_data="platform_telegram")],
        [InlineKeyboardButton("📲 ممبر روبیکا", callback_data="platform_rubika")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await query.message.reply_text(
        f"📦 *ثبت سفارش جدید*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👛 موجودی شما: *{balance} تومن*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 *قیمت‌ها:*\n"
        f"├ 📱 تلگرام: هر ۱۰۰ ممبر = ۱۵ تومن\n"
        f"└ 📲 روبیکا: هر ۱۰۰ ممبر = ۳۰ تومن\n\n"
        f"⚠️ حداقل سفارش: ۲۰۰۰ ممبر\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"پلتفرم رو انتخاب کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return PLATFORM

async def platform_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    platform = "تلگرام" if query.data == "platform_telegram" else "روبیکا"
    price = 15 if query.data == "platform_telegram" else 30
    context.user_data['platform'] = platform
    context.user_data['price_per_100'] = price

    await query.message.reply_text(
        f"📦 *پلتفرم: {platform}*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 قیمت: هر ۱۰۰ ممبر = {price} تومن\n"
        f"⚠️ حداقل: ۲۰۰۰ ممبر\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"تعداد ممبر مورد نظرت رو بنویس 👇",
        parse_mode="Markdown"
    )
    return AMOUNT

async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    if not text.isdigit():
        await update.message.reply_text("❌ فقط عدد بنویس!")
        return AMOUNT
    amount = int(text)
    if amount < 2000:
        await update.message.reply_text("❌ حداقل سفارش ۲۰۰۰ ممبره!")
        return AMOUNT

    price_per_100 = context.user_data['price_per_100']
    total = (amount // 100) * price_per_100
    balance = get_wallet(user_id)

    if balance < total:
        await update.message.reply_text(
            f"❌ *موجودی کافی نیست!*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 مبلغ سفارش: {total} تومن\n"
            f"👛 موجودی شما: {balance} تومن\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"لطفاً اول موجودیت رو شارژ کن!",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    context.user_data['amount'] = amount
    context.user_data['total'] = total

    await update.message.reply_text(
        f"✅ *تعداد: {amount} ممبر*\n"
        f"💰 *مبلغ کل: {total} تومن*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"لینک کانال یا گروهت رو بفرست 👇",
        parse_mode="Markdown"
    )
    return LINK

async def link_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    platform = context.user_data['platform']
    amount = context.user_data['amount']
    total = context.user_data['total']
    link = update.message.text

    wallets[user.id] = get_wallet(user.id) - total

    await update.message.reply_text(
        f"✅ *سفارش ثبت شد!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 پلتفرم: {platform}\n"
        f"👥 تعداد: {amount} ممبر\n"
        f"💰 مبلغ: {total} تومن\n"
        f"👛 موجودی باقیمانده: {wallets[user.id]} تومن\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"⏳ سفارشت در حال انجامه!",
        parse_mode="Markdown"
    )

    await context.bot.send_message(
        ADMIN_ID,
        f"🛒 *سفارش جدید!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 آیدی: `{user.id}`\n"
        f"🔗 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"📱 پلتفرم: {platform}\n"
        f"👥 تعداد: {amount} ممبر\n"
        f"💰 مبلغ: {total} تومن\n"
        f"🔗 لینک: {link}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(
        "📋 *قوانین و مقررات:*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "✅ حداقل سفارش: ۲۰۰۰ ممبر\n"
        "✅ پرداخت از کیف پول\n"
        "✅ بعد از ثبت سفارش انجام میشه\n"
        "❌ کنسلی نداریم\n"
        "❌ استرداد وجه نداریم\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💰 *قیمت‌ها:*\n"
        "├ تلگرام: هر ۱۰۰ ممبر = ۱۵ تومن\n"
        "└ روبیکا: هر ۱۰۰ ممبر = ۳۰ تومن",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(
        "👨‍💻 *پشتیبانی:*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "برای ارتباط با پشتیبانی پیام بده 👇\n"
        "━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu_query(query, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_order, pattern="^new_order$")],
        states={
            PLATFORM: [CallbackQueryHandler(platform_chosen, pattern="^platform_")],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_received)],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")]
    )

    charge_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(charge_wallet, pattern="^charge_wallet$")],
        states={
            CHARGE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, charge_amount_received)],
            CHARGE_RECEIPT: [
                MessageHandler(filters.PHOTO, charge_receipt_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, charge_receipt_received)
            ],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(my_wallet, pattern="^my_wallet$"))
    app.add_handler(CallbackQueryHandler(charge_confirm, pattern="^charge_confirm_"))
    app.add_handler(CallbackQueryHandler(charge_reject, pattern="^charge_reject_"))
    app.add_handler(order_conv)
    app.add_handler(charge_conv)

    print("✅ ربات شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
