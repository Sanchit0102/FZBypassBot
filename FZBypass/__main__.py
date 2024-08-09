from FZBypass import Bypass, LOGGER, Config
from pyrogram import idle
from pyrogram.filters import command, user
from os import path as ospath, execl
from asyncio import create_subprocess_exec
from sys import executable
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from threading import Thread
import pytz

RENDER_EXTERNAL_URL = "http://localhost:5000"

app = Flask(__name__)

@app.route('/alive')
def alive():
    return "I am alive!"

def ping_self():
    url = f"{RENDER_EXTERNAL_URL}/alive"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Ping successful!")
        else:
            logging.error(f"Ping failed with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Ping failed with exception: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_job(ping_self, 'interval', minutes=3)
    scheduler.start()

def run_flask():
    app.run(host='0.0.0.0', port=10000)

@Bypass.on_message(command("restart") & user(Config.OWNER_ID))
async def restart(client, message):
    restart_message = await message.reply("<i>Restarting...</i>")
    await (await create_subprocess_exec("python3", "update.py")).wait()
    with open(".restartmsg", "w") as f:
        f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    try:
        execl(executable, executable, "-m", "FZBypass")
    except Exception:
        execl(executable, executable, "-m", "FZBypassBot/FZBypass")


async def restart():
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            await Bypass.edit_message_text(
                chat_id=chat_id, message_id=msg_id, text="<i>Restarted !</i>"
            )
        except Exception as e:
            LOGGER.error(e)

Thread(target=run_flask).start()
start_scheduler()
Bypass.start()
LOGGER.info("FZ Bot Started!")
Bypass.loop.run_until_complete(restart())
idle()
Bypass.stop()
