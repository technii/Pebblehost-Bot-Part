import threading
from bot import run_bot
from waitress import serve
from flaskapp import app

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

serve(app, host="0.0.0.0", port=8054) 