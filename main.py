import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

ADMIN_ID = 8678262416
REQUIRED_CHANNELS = ["@LoLo_LoLo_Lo_Lo", "@LoLo_funny2", "@LoLo_funny"]
PRIVATE_CHANNEL_ID = -1004299938337
PUBLIC_CHANNEL = "@LoLo_funny2"
DELETE_AFTER_SECONDS = 7

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# نگه داشتن فیلم فوروارد شده ادمین
admin_pending = {}  # admin_id -> msg_id کانال خصوصی

async def check_membership(user_id, context):
    not_joined = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked", "banned"]:
                not_joined.append(channel)
        except TelegramError:
            not_joined.append(channel)
    return not_joined

def build_join_keyboard(not_joined, msg_id=None):
    keyboard = [
        [InlineKeyboardButton(f"📢 عضویت در {c}", url=f"https://t.me/{c.replace('@', '')}")]
        for c in not_joined
    ]
    callback = f"check_join_{msg_id}" if msg_id else "check_join"
    keyboard.append([InlineKeyboardButton("✅ عضو شدم", callback_data=callback)])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # اومده از دکمه مشاهده کانال
    if args and args[0].startswith("film_"):
        msg_id = args[0].split("_")[1]
        not_joined = await check_membership(user.id, context)
        if not_joined:
            await update.message.reply_text(
                "🔒 برای دیدن محتوا اول عضو کانال‌ها شو 👇",
                reply_markup=build_join_keyboard(not_joined, msg_id)
            )
            return
        await send_film(update.message, context, user.id, int(msg_id))
        return

    # استارت معمولی
    not_joined = await check_membership(user.id, context)
    if not_joined:
        await update.message.reply_text(
            "🔒 برای استفاده از ربات اول عضو کانال‌ها شو 👇",
            reply_markup=build_join_keyboard(not_joined)
        )
        return

    await update.message.reply_text(
        f"👋 سلام {user.first_name} عزیز!\n\n"
        f"برای دیدن محتوا، از کانال روی دکمه «مشاهده» بزن 👇\n\n"
        f"📢 {PUBLIC_CHANNEL}"
    )

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    parts = data.split("_")
    msg_id = parts[2] if len(parts) > 2 else None

    not_joined = await check_membership(user_id, context)
    if not_joined:
        await query.edit_message_text(
            "❌ هنوز عضو همه کانال‌ها نشدی 👇",
            reply_markup=build_join_keyboard(not_joined, msg_id)
        )
        return

    if msg_id:
        await query.edit_message_text("✅ عضویت تایید شد! در حال ارسال...")
        await send_film(query.message, context, user_id, int(msg_id))
    else:
        await query.edit_message_text(
            f"✅ عضویت تایید شد!\n\n"
            f"برای دیدن محتوا از کانال روی دکمه «مشاهده» بزن 👇\n\n"
            f"📢 {PUBLIC_CHANNEL}"
        )

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return

    # ادمین فیلم فوروارد کرد
    if update.message.forward_origin or update.message.video or update.message.photo or update.message.document:
        # ذخیره پیام
        admin_pending[ADMIN_ID] = {
            "message_id": update.message.message_id,
            "chat_id": update.message.chat_id
        }
        await update.message.reply_text(
            "✅ فیلم دریافت شد!\n\n"
            "حالا متن پست رو بنویس 👇\n"
            "_(این متن بالای دکمه مشاهده نشون داده میشه)_",
            parse_mode="Markdown"
        )
        return

    # ادمین متن پست رو فرستاد
    if ADMIN_ID in admin_pending and isinstance(admin_pending[ADMIN_ID], dict) and "message_id" in admin_pending[ADMIN_ID]:
        caption_text = update.message.text
        stored = admin_pending[ADMIN_ID]

        try:
            # فوروارد فیلم به کانال خصوصی تا msg_id بگیریم
            forwarded = await context.bot.forward_message(
                chat_id=PRIVATE_CHANNEL_ID,
                from_chat_id=stored["chat_id"],
                message_id=stored["message_id"]
            )
            film_msg_id = forwarded.message_id

            # لینک دکمه مشاهده
            bot_username = (await context.bot.get_me()).username
            view_url = f"https://t.me/{bot_username}?start=film_{film_msg_id}"

            keyboard = [[InlineKeyboardButton("مشاهده 👁", url=view_url)]]

            # پست توی کانال عمومی
            await context.bot.send_message(
                chat_id=PUBLIC_CHANNEL,
                text=caption_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            del admin_pending[ADMIN_ID]
            await update.message.reply_text("✅ پست با موفقیت توی کانال گذاشته شد!")

        except TelegramError as e:
            logger.error(f"خطا: {e}")
            await update.message.reply_text(f"❌ خطا: {e}")

async def send_film(message, context, user_id, msg_id):
    try:
        sent = await context.bot.forward_message(
            chat_id=user_id,
            from_chat_id=PRIVATE_CHANNEL_ID,
            message_id=msg_id
        )
        notice = await context.bot.send_message(
            chat_id=user_id,
            text=f"⏳ این محتوا بعد از {DELETE_AFTER_SECONDS} ثانیه حذف میشه!"
        )

        async def delete_later():
            await asyncio.sleep(DELETE_AFTER_SECONDS)
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=sent.message_id)
                await context.bot.delete_message(chat_id=user_id, message_id=notice.message_id)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🗑 محتوا حذف شد.\n\n📢 برای محتوای بیشتر کانال رو دنبال کن:\n{PUBLIC_CHANNEL}"
                )
            except:
                pass

        asyncio.create_task(delete_later())

    except TelegramError as e:
        logger.error(f"خطا در ارسال فیلم: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ خطا در ارسال محتوا. دوباره امتحان کن."
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join"))
    app.add_handler(MessageHandler(
        filters.User(ADMIN_ID) & (filters.VIDEO | filters.PHOTO | filters.Document.ALL | filters.FORWARDED | filters.TEXT & ~filters.COMMAND),
        handle_admin_message
    ))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
