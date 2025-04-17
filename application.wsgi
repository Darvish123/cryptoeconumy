import sys
import os

# مسیر به پوشه پروژه را به sys.path اضافه کنید
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from bot import app as application  # فرض کنید که کد شما در فایل bot.py است و اپلیکیشن Flask یا مشابه آن در آنجا تعریف شده است

if __name__ == "__main__":
    application.run()