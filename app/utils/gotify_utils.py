from gotify import AsyncGotify

gotify = AsyncGotify(
        base_url = "REDACTED_GOTIFY_URL",
        app_token = "REDACTED_GOTIFY_TOKEN_1",
)


async def send_gotify(message: str) :
    await gotify.create_message(message)
