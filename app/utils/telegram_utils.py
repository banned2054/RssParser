from telegram import Bot
from telegram.error import TelegramError

from app import config
from app.utils.log_utils import set_up_logger
from app.utils.qq_utils import send_group_message

logger = set_up_logger(__name__)


async def send_message(message) :
    bot = Bot(token = config.get_config('telegram_token'))
    try :
        await bot.send_message(chat_id = config.get_config('telegram_chat_id'), text = message)
        return True, ''
    except TelegramError as e :
        return False, str(e)


async def send_message_to_channel(message) :
    bot = Bot(token = config.get_config('telegram_token'))
    try :
        await bot.send_message(chat_id = 'YOUR_TELEGRAM_CHANNEL_ID', text = message)
        await send_group_message(message)
        return True, ''
    except TelegramError as e :
        return False, str(e)
