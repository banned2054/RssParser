# 服务端的 URL 地址
from app.utils.log_utils import set_up_logger
from app.utils.net_utils import fetch

BASE_URL = "https://qb.YOUR_MYSQL_USERNAME.top:34152"
login_url = f"{BASE_URL}/dHJ5X2dldF9hY2Nlc3M"
send_url = f"{BASE_URL}/c2VuZF9ncm91cF9tZXNzYWdl"

logger = set_up_logger(__name__)


async def login():
    success, token_data = await fetch(login_url, method = "POST")
    if success:
        logger.info("napcat server login success")
        return token_data.get("access_token")
    else:
        logger.error("napcat get login failed")
        logger.error("Login failed")
        return None


async def send_message(token, content, target, recipient):
    headers = {"Authorization": f"Bearer {token}"}
    message_data = {"content": content, "target": target, "recipient": recipient}

    success, response_data = await fetch(send_url, method = "POST", headers = headers, json = message_data)
    if success:
        logger.info("napcat send message success")
        return response_data
    else:
        logger.error("Failed to send message")
        return None


async def send_group_message(message):
    # 第一步：获取 Token
    token = await login()

    if token:
        # 第二步：使用获取的 Token 发送消息
        await send_message(
                token, content = message, target = "612582873", recipient = "rss_parser"
        )
    else:
        print("Unable to proceed without a token.")
