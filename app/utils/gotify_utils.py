from gotify import AsyncGotify


async def send_gotify(message: str) :
    gotify = AsyncGotify(
            base_url = "REDACTED_GOTIFY_URL_LOCAL",
            app_token = "REDACTED_GOTIFY_TOKEN_1", )
    await gotify.create_message(message)
