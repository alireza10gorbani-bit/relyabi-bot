import asyncio
import json
import os
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

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"wallets": {}, "referrals": {}, "order_counter": 0}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "wallets": wallets,
            "referrals": referrals,
            "order_counter": order_counter
        }, f, ensure_ascii=False, indent=2)

_data = load_data()
wallets = {int(k): v for k, v in _data.get("wallets", {}).items()}
referrals = {int(k): v for k, v in _data.get("referrals", {}).items()}
order_counter = _data.get("order_counter", 0)

pending_orders = {}

def get_wallet(user_id):
    if user_id not in wallets:
        wallets[user_id] = 0
        save_data()
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
            save_data()
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
    balance = get_wallet(query.from_user.id)
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
        f"🔗 لینک عمومی کانال یا گروهت رو وارد کن\n"
        f"_(مثال: t.me/yourchannel)_\n"
        f"━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return LINK

async def link_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter
    user = update.effective_user
    platform = context.user_data['platform']
    amount = context.user_data['amount']
    total = context.user_data['total']
    link = update.message.text

    wallets[user.id] = get_wallet(user.id) - total
    save_data()

    order_counter += 1
    order_id = order_counter
    save_data()

    pending_orders[order_id] = {
        'user_id': user.id,
        'username': user.username or 'ندارد',
        'platform': platform,
        'amount': amount,
        'total': total,
        'link': link,
    }

    await update.message.reply_text(
        f"✅ *سفارش ثبت شد!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 پلتفرم: {platform}\n"
        f"👥 تعداد: {amount} ممبر\n"
        f"💰 مبلغ: {fmt(total)} تومن\n"
        f"👛 موجودی باقیمانده: {fmt(wallets[user.id])} تومن\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"⏳ سفارشت در حال بررسی توسط ادمینه، به زودی انجام میشه!",
        parse_mode="Markdown"
    )

    keyboard = [[InlineKeyboardButton("✅ انجام شد", callback_data=f"odone_{order_id}")]]
    admin_text = (
        f"🛒 *سفارش جدید!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔢 شماره سفارش: #{order_id}\n"
        f"👤 آیدی: {user.id}\n"
        f"🔗 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"📱 پلتفرم: {platform}\n"
        f"👥 تعداد: {amount} ممبر\n"
        f"💰 مبلغ: {fmt(total)} تومن\n"
        f"🔗 لینک: {link}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"⬇️ بعد از انجام سفارش دکمه رو بزن"
    )

    sent = False
    for attempt in range(3):
        try:
            await context.bot.send_message(
                ADMIN_ID, admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            sent = True
            break
        except Exception as e:
            if attempt == 2:
                print(f"خطا در ارسال سفارش به ادمین: {e}")
            await asyncio.sleep(1)

    if not sent:
        # برگشت پول
        wallets[user.id] = get_wallet(user.id) + total
        save_data()
        del pending_orders[order_id]
        await update.message.reply_text(
            f"❌ *سفارش ثبت نشد!*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"مشکل در ارتباط با ادمین\n"
            f"💰 مبلغ {fmt(total)} تومن به کیف پولت برگشت\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"دوباره امتحان کن 🙏",
            parse_mode="Markdown"
        )

    return ConversationHandler.END

async def order_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ سفارش تایید شد!")

    order_id = int(query.data.split("_")[1])
    order = pending_orders.get(order_id)

    if not order:
        await query.message.reply_text(
            "❌ اطلاعات این سفارش در حافظه نیست!\n"
            "روی پیام سفارش ریپلای بزن تا مستقیم به کاربر پیام بده.",
            parse_mode="Markdown"
        )
        return

    user_id = order['user_id']

    await context.bot.send_message(
        user_id,
        f"🎉 *سفارش شما انجام شد!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 پلتفرم: {order['platform']}\n"
        f"👥 تعداد: {order['amount']} ممبر\n"
        f"🔗 لینک کانال/گروه: {order['link']}\n"
        f"💰 مبلغ پرداختی: {fmt(order['total'])} تومن\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"✨ ممبرها به کانال یا گروهت اضافه شدن\n\n"
        f"💙 ممنون از اعتمادت!\n"
        f"هر مشکلی بود از بخش تیکت اطلاع بده 🙏",
        parse_mode="Markdown"
    )

    del pending_orders[order_id]
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        f"✅ *سفارش #{order_id} انجام شد و کاربر مطلع شد!*",
        parse_mode="Markdown"
    )

async def charge_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
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

    for attempt in range(3):
        try:
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
            break
        except Exception as e:
            if attempt == 2:
                print(f"خطا در ارسال رسید به ادمین: {e}")
            await asyncio.sleep(1)

    return ConversationHandler.END

async def charge_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    user_id = int(parts[2])
    amount = int(parts[3])
    wallets[user_id] = get_wallet(user_id) + amount
    save_data()
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
        "❌ *شارژ تایید نشد!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🚫 توسط ادمین رد شد\n\n"
        "برای اطلاعات بیشتر تیکت ارسال کنید 👇\n"
        "━━━━━━━━━━━━━━━",
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
        f"مشکل یا سوالت رو بنویس\n"
        f"_(می‌تونی عکس هم بفرستی)_ 👇\n"
        f"━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return TICKET_MSG

async def ticket_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or update.message.caption or "(بدون متن)"

    await update.message.reply_text(
        "✅ *تیکت ارسال شد!*\n\nبه زودی پاسخ داده میشه 🙏",
        parse_mode="Markdown"
    )

    ticket_text = (
        f"🎫 *تیکت جدید:*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 آیدی: `{user.id}`\n"
        f"🔗 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💬 پیام:\n{text}\n"
        f"━━━━━━━━━━━━━━━"
    )

    try:
        if update.message.photo:
            await context.bot.send_photo(
                ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption=ticket_text,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(ADMIN_ID, ticket_text, parse_mode="Markdown")
    except Exception as e:
        print(f"خطا در ارسال تیکت: {e}")

    return ConversationHandler.END

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(
        "📋 *قوانین ربات:*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "۱. پس از ثبت سفارش، موجودی کسر میشه\n"
        "۲. تحویل سفارش حداکثر ۲۴ ساعته\n"
        "۳. لینک کانال/گروه باید عمومی باشه\n"
        "۴. در صورت مشکل، تیکت ارسال کن\n"
        "━━━━━━━━━━━━━━━",
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
        "برای ارتباط با پشتیبانی از بخش تیکت استفاده کن\n"
        "━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu_query(query, context)
    return ConversationHandler.END

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.reply_to_message:
        return
    text = update.message.reply_to_message.text or ""
    user_id = None
    for line in text.split("\n"):
        if "آیدی:" in line:
            parts = line.split(":")
            if len(parts) > 1:
                try:
                    user_id = int(parts[1].strip().replace("`", ""))
                except:
                    pass
    if user_id:
        try:
            await context.bot.send_message(
                user_id,
                f"📩 *پاسخ پشتیبانی:*\n\n{update.message.text}",
                parse_mode="Markdown"
            )
            await update.message.reply_text("✅ پیام ارسال شد!")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_order, pattern="^new_order$")],
        states={
            PLATFORM: [
                CallbackQueryHandler(platform_chosen, pattern="^platform_"),
                CallbackQueryHandler(new_order, pattern="^new_order$"),
            ],
            AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received),
                CallbackQueryHandler(new_order, pattern="^new_order$"),
            ],
            LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, link_received),
                CallbackQueryHandler(new_order, pattern="^new_order$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")],
        per_message=False,
    )

    charge_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(charge_wallet, pattern="^charge_wallet$")],
        states={
            CHARGE_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, charge_amount_received),
                CallbackQueryHandler(charge_wallet, pattern="^charge_wallet$"),
            ],
            CHARGE_RECEIPT: [
                MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), charge_receipt_received),
                CallbackQueryHandler(charge_wallet, pattern="^charge_wallet$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")],
        per_message=False,
    )

    ticket_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_ticket, pattern="^new_ticket$")],
        states={
            TICKET_MSG: [
                MessageHandler(filters.TEXT | filters.PHOTO, ticket_received),
            ],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_conv)
    app.add_handler(charge_conv)
    app.add_handler(ticket_conv)
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(my_wallet, pattern="^my_wallet$"))
    app.add_handler(CallbackQueryHandler(referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(charge_confirm, pattern="^charge_confirm_"))
    app.add_handler(CallbackQueryHandler(charge_reject, pattern="^charge_reject_"))
    app.add_handler(CallbackQueryHandler(order_done, pattern="^odone_"))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, admin_reply))

    print("ربات شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
