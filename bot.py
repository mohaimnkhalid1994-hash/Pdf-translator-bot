Python
import os
import tempfile
import pdfplumber
from googletrans import Translator
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from telegram.ext import Updater, MessageHandler, Filters

translator = Translator()

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text += txt + "\n"
    return text

def translate_text(text, dest='ar'):
    try:
        translated = translator.translate(text, dest=dest)
        return translated.text
    except Exception as e:
        print("Translation Error:", e)
        return text

def create_pdf(text, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 40
    for line in text.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line)
        y -= 15
    c.save()

def handle_pdf(update, context):
    file = update.message.document
    if not file:
        update.message.reply_text("❌ حدث خطأ في الملف.")
        return

    if file.mime_type != "application/pdf":
        update.message.reply_text("❌ أرسل ملف PDF فقط.")
        return

    update.message.reply_text("📥 جاري التحميل والمعالجة...")

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        file_path = file.get_file().download(custom_path=tmp.name)

        text = extract_text_from_pdf(file_path)
        if not text:
            update.message.reply_text("⚠ لا يوجد نص يمكن ترجمته.")
            return

        translated = translate_text(text, dest='ar')

        output_pdf = "translated.pdf"
        create_pdf(translated, output_pdf)

        update.message.reply_document(open(output_pdf, "rb"))

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN غير معرف في المتغيرات البيئية!")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_pdf))

    print("🤖 Bot Started...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
