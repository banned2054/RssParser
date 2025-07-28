from gotify import AsyncGotify

from app import config


async def send_gotify(message: str) :
    gotify = AsyncGotify(
            base_url = config.get_config('gotify_url'),
            app_token = config.get_config('gotify_finish_download_token'), )
    await gotify.create_message(message)


async def send_download_gotify(message: str) :
    gotify = AsyncGotify(
            base_url = config.get_config('gotify_url'),
            app_token = config.get_config('gotify_start_download_token'), )
    await gotify.create_message(message)
