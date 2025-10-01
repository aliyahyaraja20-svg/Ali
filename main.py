import os
import requests
from user_agent import generate_user_agent
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def send_instagram_reset(email: str) -> str:
    try:
        user_agent_str = str(generate_user_agent())
        cookies = {
            'mid': 'Zx5LcgABAAFieRsXSAUirmjPV4cO',
            'csrftoken': '7gUfe6hxE57UPTM1VfyKBvVxzX6gWMQm',
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'i.instagram.com',
            'Connection': 'Keep-Alive',
            'User-Agent': user_agent_str,
            'Cookie2': os.getenv('Version', '') + '=1',
            'Accept-Language': 'ar-EG, en-US',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Capabilities': 'AQ==',
        }
        data = {
            'ig_sig_key_version': '4',
            'signed_body': f'1cc3d514cd3f612bd1bee78bf8a81f13b49b95847879f7a6c53bf03ea542fbd3.{{"user_email":"{email}","device_id":"android-f3e94b5ecd948ea2","guid":"a26844c0-a663-4f2e-992b-7702ea61bc49","_csrftoken":"7gUfe6hxE57UPTM1VfyKBvVxzX6gWMQm"}}',
        }
        response = requests.post(
            'https://i.instagram.com/api/v1/accounts/send_password_reset/',
            cookies=cookies,
            headers=headers,
            data=data,
        ).text
        if 'obfuscated_email' in response:
            return f"✅ تم إرسال رابط إعادة التعيين إلى البريد: {email}"
        else:
            logging.error(f"Failed response for {email}: {response}")
            return f"❌ خطأ، لم يتم العثور على حساب مرتبط بالبريد: {email}"
    except Exception as e:
        logging.error(f"An exception occurred: {e}")
        return "حدث خطأ غير متوقع أثناء محاولة الإرسال."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً بك! 👋\nأرسل لي أي بريد إلكتروني لأتحقق منه وأرسل طلب إعادة تعيين كلمة المرور له على انستغرام.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHANNEL_ID = "@TTTT4Q"
    user_id = update.effective_user.id

    try:
        member_status = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        if member_status.status in ['left', 'kicked']:
            await update.message.reply_text(
                f"عذراً ✋، يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.\n\n"
                f"اشترك هنا: {CHANNEL_ID}\n\n"
                f"ثم حاول مرة أخرى."
            )
            return

    except BadRequest as e:
        logging.error(f"Error checking chat member: {e}")
        await update.message.reply_text("حدث خطأ إداري. يرجى التأكد من أن البوت مشرف في القناة الإجبارية.")
        return
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text("حدث خطأ غير متوقع. يرجى المحاولة لاحقاً.")
        return

    user_email = update.message.text
    processing_message = await update.message.reply_text(f"⏳ جاري التحقق من البريد: {user_email}...")
    
    result = send_instagram_reset(user_email)
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=processing_message.message_id,
        text=result
    )

def main():
    TOKEN = "8377672935:AAEikEnCSF4nlXR5-L1PzWJaZi1OBL9t8oQ"
    
    print("Bot is starting with forced subscription...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
