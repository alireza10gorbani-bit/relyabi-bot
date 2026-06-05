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
        json.dump({"wallets": wallets, "referrals": referrals, "order_counter": order_counter}, f, ensure_ascii=False, indent=2)

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
            await context.bot.send_message(referrer_id, f"🎉 یه نفر با لینک معرفی شما وارد شد!\n💰 {fmt(REFERRAL_BONUS)} تومن به کیف پولت اضافه شد!\n👛 موجودی: {fmt(wallets[referrer_id])} تومن")
    is_member = await check_membership(user_id, context)
    if not is_member:
        keyboard = [
            [InlineKeyboardButton("📢 کانال ۱", url="https://t.me/LoLo_funny2")],
            [InlineKeyboardButton("📢 کانال ۲", url="https://t.me/LoLo_funny")],
            [InlineKeyboardButton("📢 کانال ۳", url="https://t.me/LoLo_LoLo_Lo_Lo")],
            [InlineKeyboardButton("عضو شدم", callback_data="check_join")]
        ]
        await update.message.reply_text("برای استفاده از ربات باید عضو کانال‌های زیر بشی", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await show_main_menu(update, context)

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await check_membership(query.from_user.id, context):
        await query.message.reply_text("هنوز عضو همه کانال‌ها نشدی!")
        return
    await show_main_menu_query(query, context)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 ثبت سفارش", callback_data="new_order")],
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet"), InlineKeyboardButton("👛 موجودی من", callback_data="my_wallet")],
        [InlineKeyboardButton("🔗 لینک معرفی", callback_data="referral"), InlineKeyboardButton("🎫 ارسال تیکت", callback_data="new_ticket")],
        [InlineKeyboardButton("📋 قوانین", callback_data="rules"), InlineKeyboardButton("پشتیبانی", callback_data="support")]
    ])

async def show_main_menu(update, context):
    balance = get_wallet(update.effective_user.id)
    await update.message.reply_text(f"به ربات فروش ممبر خوش اومدی!\nموجودی: {fmt(balance)} تومن\nتلگرام: هر 100 تا 15000 تومن\nروبیکا: هر 100 تا 30000 تومن", reply_markup=main_keyboard())

async def show_main_menu_query(query, context):
    balance = get_wallet(query.from_user.id)
    await query.message.reply_text(f"به ربات فروش ممبر خوش اومدی!\nموجودی: {fmt(balance)} تومن\nتلگرام: هر 100 تا 15000 تومن\nروبیکا: هر 100 تا 30000 تومن", reply_markup=main_keyboard())

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📱 ممبر تلگرام", callback_data="platform_telegram")],
        [InlineKeyboardButton("📲 ممبر روبیکا", callback_data="platform_rubika")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    await query.message.reply_text(f"ثبت سفارش\nموجودی: {fmt(get_wallet(query.from_user.id))} تومن\nتلگرام: 100=15000 | روبیکا: 100=30000\nپلتفرم رو انتخاب کن", reply_markup=InlineKeyboardMarkup(keyboard))
    return PLATFORM

async def platform_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    platform = "تلگرام" if query.data == "platform_telegram" else "روبیکا"
    price = 15000 if query.data == "platform_telegram" else 30000
    context.user_data['platform'] = platform
    context.user_data['price_per_100'] = price
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(f"پلتفرم: {platform}\nهر 100 ممبر = {fmt(price)} تومن\nتعداد ممبر رو بنویس (100 تا 2000)", reply_markup=InlineKeyboardMarkup(keyboard))
    return AMOUNT

async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    if not text.isdigit():
        await update.message.reply_text("فقط عدد بنویس!")
        return AMOUNT
    amount = int(text)
    if amount < 100 or amount > 2000:
        await update.message.reply_text("تعداد باید بین 100 تا 2000 باشه!")
        return AMOUNT
    total = (amount // 100) * context.user_data['price_per_100']
    balance = get_wallet(user_id)
    if balance < total:
        keyboard = [[InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")], [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
        await update.message.reply_text(f"موجودی کافی نیست!\nمبلغ سفارش: {fmt(total)} تومن\nموجودی شما: {fmt(balance)} تومن", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END
    context.user_data['amount'] = amount
    context.user_data['total'] = total
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await update.message.reply_text(f"تعداد: {amount} ممبر\nمبلغ: {fmt(total)} تومن\nلینک عمومی کانال یا گروهت رو بفرست", reply_markup=InlineKeyboardMarkup(keyboard))
    return LINK

async def link_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter
    user = update.effective_user
    platform = context.user_data['platform']
    amount = context.user_data['amount']
    total = context.user_data['total']
    link = update.message.text
    wallets[user.id] = get_wallet(user.id) - total
    order_counter += 1
    order_id = order_counter
    save_data()
    pending_orders[order_id] = {'user_id': user.id, 'username': user.username or 'ندارد', 'platform': platform, 'amount': amount, 'total': total, 'link': link}
    await update.message.reply_text(f"سفارش ثبت شد!\nپلتفرم: {platform}\nتعداد: {amount}\nمبلغ: {fmt(total)} تومن\nموجودی باقی: {fmt(wallets[user.id])} تومن\nدر حال بررسی توسط ادمین...")
    keyboard = [[InlineKeyboardButton("انجام شد", callback_data=f"odone_{order_id}")]]
    admin_text = f"سفارش جدید!\nشماره: {order_id}\nآیدی: {user.id}\nیوزر: @{user.username or 'ندارد'}\nپلتفرم: {platform}\nتعداد: {amount}\nمبلغ: {fmt(total)} تومن\nلینک: {link}"
    for attempt in range(3):
        try:
            await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=InlineKeyboardMarkup(keyboard))
            break
        except:
            await asyncio.sleep(1)
    return ConversationHandler.END

async def order_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.split("_")[1])
    order = pending_orders.get(order_id)
    if not order:
        await query.message.reply_text("اطلاعات سفارش پیدا نشد!")
        return
    await context.bot.send_message(order['user_id'], f"سفارش شما انجام شد!\nپلتفرم: {order['platform']}\nتعداد: {order['amount']} ممبر\nلینک: {order['link']}\nممنون از اعتمادت!")
    del pending_orders[order_id]
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"سفارش {order_id} انجام شد!")

async def charge_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(f"افزایش موجودی\nشماره کارت: {CARD_NUMBER}\nبه نام: {CARD_NAME}\nمبلغ مورد نظر رو بنویس", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHARGE_AMOUNT

async def charge_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("فقط عدد بنویس!")
        return CHARGE_AMOUNT
    context.user_data['charge_amount'] = int(text)
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await update.message.reply_text(f"مبلغ: {fmt(int(text))} تومن\nتصویر رسید پرداخت رو بفرست", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHARGE_RECEIPT

async def charge_receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    amount = context.user_data['charge_amount']
    await update.message.reply_text("رسیدت دریافت شد! منتظر تایید ادمین باش")
    keyboard = [[InlineKeyboardButton("تایید", callback_data=f"charge_confirm_{user.id}_{amount}"), InlineKeyboardButton("رد", callback_data=f"charge_reject_{user.id}")]]
    caption = f"درخواست شارژ\nآیدی: {user.id}\nیوزر: @{user.username or 'ندارد'}\nمبلغ: {fmt(amount)} تومن"
    for attempt in range(3):
        try:
            if update.message.photo:
                await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await context.bot.send_message(ADMIN_ID, caption, reply_markup=InlineKeyboardMarkup(keyboard))
            break
        except:
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
    await context.bot.send_message(user_id, f"موجودی شارژ شد!\nافزوده شده: {fmt(amount)} تومن\nموجودی فعلی: {fmt(wallets[user_id])} تومن")
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"{fmt(amount)} تومن اضافه شد!")

async def charge_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[2])
    await context.bot.send_message(user_id, "شارژ تایید نشد! برای اطلاعات بیشتر تیکت ارسال کن")
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("شارژ رد شد!")

async def my_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    balance = get_wallet(user_id)
    count = sum(1 for v in referrals.values() if v == user_id)
    keyboard = [[InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge_wallet")], [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(f"کیف پول\nموجودی: {fmt(balance)} تومن\nمعرفی‌ها: {count} نفر", reply_markup=InlineKeyboardMarkup(keyboard))

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    count = sum(1 for v in referrals.values() if v == user_id)
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text(f"سیستم معرفی\nتعداد: {count} نفر\nدرآمد: {fmt(count*REFERRAL_BONUS)} تومن\nلینک معرفی:\n{ref_link}", reply_markup=InlineKeyboardMarkup(keyboard))

async def new_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text("مشکل یا سوالت رو بنویس", reply_markup=InlineKeyboardMarkup(keyboard))
    return TICKET_MSG

async def ticket_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or update.message.caption or "(بدون متن)"
    await update.message.reply_text("تیکت ارسال شد! به زودی پاسخ داده میشه")
    ticket_text = f"تیکت جدید\nآیدی: {user.id}\nیوزر: @{user.username or 'ندارد'}\nپیام: {text}"
    try:
        if update.message.photo:
            await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=ticket_text)
        else:
            await context.bot.send_message(ADMIN_ID, ticket_text)
    except Exception as e:
        print(f"خطا: {e}")
    return ConversationHandler.END

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text("قوانین:\n1. بعد از ثبت سفارش موجودی کسر میشه\n2. تحویل حداکثر 24 ساعته\n3. لینک باید عمومی باشه\n4. مشکل داری تیکت بزن", reply_markup=InlineKeyboardMarkup(keyboard))

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]]
    await query.message.reply_text("برای پشتیبانی از بخش تیکت استفاده کن", reply_markup=InlineKeyboardMarkup(keyboard))

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
            try:
                user_id = int(line.split(":")[1].strip())
            except:
                pass
    if user_id:
        try:
            await context.bot.send_message(user_id, f"پاسخ پشتیبانی:\n{update.message.text}")
            await update.message.reply_text("پیام ارسال شد!")
        except Exception as e:
            await update.message.reply_text(f"خطا: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_order, pattern="^new_order$")],
        states={
            PLATFORM: [CallbackQueryHandler(platform_chosen, pattern="^platform_")],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_received)],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")],
        per_message=False,
    )
    charge_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(charge_wallet, pattern="^charge_wallet$")],
        states={
            CHARGE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, charge_amount_received)],
            CHARGE_RECEIPT: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), charge_receipt_received)],
        },
        fallbacks=[CallbackQueryHandler(back_main, pattern="^back_main$")],
        per_message=False,
    )
    ticket_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_ticket, pattern="^new_ticket$")],
        states={
            TICKET_MSG: [MessageHandler(filters.TEXT | filters.PHOTO, ticket_received)],
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
    print("ربات شروع شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
