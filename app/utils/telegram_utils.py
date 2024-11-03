from telegram import Bot
from telegram.error import TelegramError
from telegram.request import HTTPXRequest

from app import config
from app.utils.log_utils import set_up_logger

logger = set_up_logger(__name__)


async def send_message(message) :
    proxy = config.get_config("proxy_url")
    request = HTTPXRequest(proxy_url = proxy)
    bot = Bot(token = config.get_config('telegram_token'), request = request)
    try :
        await bot.send_message(chat_id = config.get_config('telegram_chat_id'), text = message)
        return True, ''
    except TelegramError as e :
        return False, str(e)


async def send_message_to_channel(message) :
    proxy = config.get_config("proxy_url")
    request = HTTPXRequest(proxy_url = proxy)
    bot = Bot(token = config.get_config('telegram_token'), request = request)
    try :
        await bot.send_message(chat_id = 'YOUR_TELEGRAM_CHANNEL_ID', text = message)
        return True, ''
    except TelegramError as e :
        return False, str(e)
