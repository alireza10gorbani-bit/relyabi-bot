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
REFERRAL_BONUS = 500

PLATFORM, AMOUNT, LINK = range(3)
CHARGE_AMOUNT, CHARGE_RECEIPT = range(3, 5)
TICKET_MSG = 5

wallets = {}
referrals = {}
tickets = {}

def get_wallet(user_id):
    if user_id not in wallets:
        wallets[user_id] = 0
    return wallets[user_id]

def fmt(amount):
    return f"{amount:,}".replace(",", ".")

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

    if context.args and context.args[0].startswith("ref_"):
        referrer_id = int(context.args[0].split("_")[1])
        if referrer_id != user_id and user_id not in referrals:
            referrals[user_id] = referrer_id
            wallets[referrer_id] = get_wallet(referrer_id) + REFERRAL_BONUS
            await context.bot.send_message(
                referrer_id,
                f"🎉 *یه نفر با لینک معرفی شما وارد شد!*\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💰 *{fmt(REFERRAL_BONUS)} تومن* به کیف پولت اضافه شد!\n"
                f"👛 موجودی فعلی: *{fmt(wallets[referrer_id])} تومن*\n"
                f"━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )

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
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet"),
         InlineKeyboardButton("👛 موجودی من", callback_data="my_wallet")],
        [InlineKeyboardButton("🔗 لینک معرفی", callback_data="referral"),
         InlineKeyboardButton("🎫 ارسال تیکت", callback_data="new_ticket")],
        [InlineKeyboardButton("📋 قوانین", callback_data="rules"),
         InlineKeyboardButton("👨‍💻 پشتیبانی", callback_data="support")]
    ]
    await update.message.reply_text(
        f"💎 *به ربات فروش ممبر خوش اومدی!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👛 موجودی: *{fmt(balance)} تومن*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 *خدمات ما:*\n"
        f"├ 📱 ممبر فیک تلگرام — هر ۱۰۰ تا: 15.000 تومن\n"
        f"└ 📲 ممبر فیک روبیکا — هر ۱۰۰ تا: 30.000 تومن\n\n"
        f"⚡️ تحویل سریع | پشتیبانی ۲۴ ساعته\n"
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
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet"),
         InlineKeyboardButton("👛 موجودی من", callback_data="my_wallet")],
        [InlineKeyboardButton("🔗 لینک معرفی", callback_data="referral"),
         InlineKeyboardButton("🎫 ارسال تیکت", callback_data="new_ticket")],
        [InlineKeyboardButton("📋 قوانین", callback_data="rules"),
         InlineKeyboardButton("👨‍💻 پشتیبانی", callback_data="support")]
    ]
    await query.message.reply_text(
        f"💎 *به ربات فروش ممبر خوش اومدی!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👛 موجودی: *{fmt(balance)} تومن*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 *خدمات ما:*\n"
        f"├ 📱 ممبر فیک تلگرام — هر ۱۰۰ تا: 15.000 تومن\n"
        f"└ 📲 ممبر فیک روبیکا — هر ۱۰۰ تا: 30.000 تومن\n\n"
        f"⚡️ تحویل سریع | پشتیبانی ۲۴ ساعته\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"یه گزینه انتخاب کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

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
        f"👛 موجودی شما: *{fmt(balance)} تومن*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 *قیمت‌ها:*\n"
        f"├ 📱 تلگرام: هر ۱۰۰ ممبر = 15.000 تومن\n"
        f"└ 📲 روبیکا: هر ۱۰۰ ممبر = 30.000 تومن\n\n"
        f"⚠️ بین ۱۰۰ تا ۲۰۰۰ ممبر\n"
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
    price = 15000 if query.data == "platform_telegram" else 30000
    context.user_data['platform'] = platform
    context.user_data['price_per_100'] = price
    keyboard = [
        [InlineKeyboardButton("◀️ مرحله قبل", callback_data="new_order")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await query.message.reply_text(
        f"📦 *پلتفرم: {platform}*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 هر ۱۰۰ ممبر = {fmt(price)} تومن\n"
        f"⚠️ بین ۱۰۰ تا ۲۰۰۰ ممبر\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"تعداد ممبر رو بنویس 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
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
    if amount < 100 or amount > 2000:
        await update.message.reply_text("❌ تعداد باید بین ۱۰۰ تا ۲۰۰۰ ممبر باشه!")
        return AMOUNT

    price_per_100 = context.user_data['price_per_100']
    total = (amount // 100) * price_per_100
    balance = get_wallet(user_id)

    if balance < total:
        keyboard = [
            [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
        ]
        await update.message.reply_text(
            f"❌ *موجودی کافی نیست!*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 مبلغ سفارش: *{fmt(total)} تومن*\n"
            f"👛 موجودی شما: *{fmt(balance)} تومن*\n"
            f"━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    context.user_data['amount'] = amount
    context.user_data['total'] = total

    keyboard = [
        [InlineKeyboardButton("◀️ مرحله قبل", callback_data="new_order")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await update.message.reply_text(
        f"✅ *تعداد: {amount} ممبر*\n"
        f"💰 *مبلغ: {fmt(total)} تومن*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"لینک کانال یا گروهت رو بفرست 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
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
        f"💰 مبلغ: {fmt(total)} تومن\n"
        f"👛 موجودی باقیمانده: {fmt(wallets[user.id])} تومن\n"
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
        f"💰 مبلغ: {fmt(total)} تومن\n"
        f"🔗 لینک: {link}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def charge_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await query.message.reply_text(
        f"💰 *افزایش موجودی*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💳 شماره کارت: `{CARD_NUMBER}`\n"
        f"👤 به نام: *{CARD_NAME}*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"مبلغ مورد نظر رو بنویس 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CHARGE_AMOUNT

async def charge_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("❌ فقط عدد بنویس!")
        return CHARGE_AMOUNT
    context.user_data['charge_amount'] = int(text)
    keyboard = [
        [InlineKeyboardButton("◀️ مرحله قبل", callback_data="charge_wallet")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await update.message.reply_text(
        f"✅ *مبلغ: {fmt(int(text))} تومن*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"تصویر رسید پرداخت رو بفرست 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CHARGE_RECEIPT

async def charge_receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    amount = context.user_data['charge_amount']

    await update.message.reply_text(
        "⏳ *رسیدت دریافت شد!*\n\nمنتظر تایید ادمین باش 🙏",
        parse_mode="Markdown"
    )

    keyboard = [[
        InlineKeyboardButton("✅ تایید", callback_data=f"charge_confirm_{user.id}_{amount}"),
        InlineKeyboardButton("❌ رد", callback_data=f"charge_reject_{user.id}")
    ]]

    caption = (
        f"💰 *درخواست شارژ:*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 آیدی: `{user.id}`\n"
        f"🔗 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"💵 مبلغ: *{fmt(amount)} تومن*\n"
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
            ADMIN_ID, caption,
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
        f"✅ *موجودی شارژ شد!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 افزوده شده: *{fmt(amount)} تومن*\n"
        f"👛 موجودی فعلی: *{fmt(wallets[user_id])} تومن*\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ {fmt(amount)} تومن به کیف پول اضافه شد!")

async def charge_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[2])
    await context.bot.send_message(
        user_id,
        "❌ *شارژ تایید نشد!*\n\nلطفاً دوباره تلاش کن.",
        parse_mode="Markdown"
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("❌ شارژ رد شد!")

async def my_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    balance = get_wallet(user_id)
    count = sum(1 for v in referrals.values() if v == user_id)
    keyboard = [
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await query.message.reply_text(
        f"👛 *کیف پول شما:*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 موجودی: *{fmt(balance)} تومن*\n"
        f"👥 معرفی‌ها: *{count} نفر*\n"
        f"━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    count = sum(1 for v in referrals.values() if v == user_id)
    earned = count * REFERRAL_BONUS
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(
        f"🔗 *سیستم معرفی*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 تعداد معرفی‌ها: *{count} نفر*\n"
        f"💰 درآمد کل: *{fmt(earned)} تومن*\n"
        f"🎁 هر معرفی: *{fmt(REFERRAL_BONUS)} تومن*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔗 لینک معرفی تو:\n`{ref_link}`\n\n"
        f"_این لینک رو به دوستات بده!_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def new_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(
        f"🎫 *ارسال تیکت*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"مشکل یا سوالت رو بنویس 👇\n"
        f"━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return TICKET_MSG

async def ticket_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    await update.message.reply_text(
        f"✅ *تیکت ارسال شد!*\n\nبه زودی جواب میگیری 🙏",
        parse_mode="Markdown"
    )

    keyboard = [[InlineKeyboardButton("💬 جواب دادن", callback_data=f"reply_ticket_{user.id}")]]
    await context.bot.send_message(
        ADMIN_ID,
        f"🎫 *تیکت جدید!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 آیدی: `{user.id}`\n"
        f"🔗 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"📝 پیام:\n{text}\n"
        f"━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def reply_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[2])
    context.user_data['ticket_reply_to'] = user_id
    await query.message.reply_text(
        f"💬 جوابت رو بنویس 👇",
        parse_mode="Markdown"
    )

async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    if 'ticket_reply_to' in context.user_data:
        target_id = context.user_data['ticket_reply_to']
        await context.bot.send_message(
            target_id,
            f"💬 *جواب تیکت شما:*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{update.message.text}\n"
            f"━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ جواب فرستاده شد!")
        del context.user_data['ticket_reply_to']

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(
        "📋 *قوانین و مقررات:*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "✅ بین ۱۰۰ تا ۲۰۰۰ ممبر\n"
        "✅ پرداخت از کیف پول\n"
        "❌ کنسلی نداریم\n"
        "❌ استرداد وجه نداریم\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💰 *قیمت‌ها:*\n"
        "├ تلگرام: هر ۱۰۰ ممبر = 15.000 تومن\n"
        "└ روبیکا: هر ۱۰۰ ممبر = 30.000 تومن",
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
        "برای ارتباط با پشتیبانی تیکت ارسال کن 👇\n"
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
        fallbacks=[
            CallbackQueryHandler(back_main, pattern="^back_main$"),
            CallbackQueryHandler(new_order, pattern="^new_order$")
        ]
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
        fallbacks=[
            CallbackQueryHandler(back_main, pattern="^back_main$"),
            CallbackQueryHandler(charge_wallet, pattern="^charge_wallet$")
        ]
    )

    ticket_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_ticket, pattern="^new_ticket$")],
        states={
            TICKET_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_received)],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(my_wallet, pattern="^my_wallet$"))
    app.add_handler(CallbackQueryHandler(referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(charge_confirm, pattern="^charge_confirm_"))
    app.add_handler(CallbackQueryHandler(charge_reject, pattern="^charge_reject_"))
    app.add_handler(CallbackQueryHandler(reply_ticket, pattern="^reply_ticket_"))
    app.add_handler(order_conv)
    app.add_handler(charge_conv)
    app.add_handler(ticket_conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_messages))

    print("✅ ربات شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
