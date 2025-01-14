import json

import requests

from app.utils.log_utils import set_up_logger

jellyfin_config_file = "data/jellyfin.json"
logger = set_up_logger(__name__)


def get_jellyfin_url() :
    with open(jellyfin_config_file, "r") as f :
        setting_data = json.load(f)
    return setting_data['jellyfin_url']


def get_jellyfin_token() :
    with open(jellyfin_config_file, "r") as f :
        setting_data = json.load(f)
    return setting_data['jellyfin_token']


def get_anime_library_id() :
    with open(jellyfin_config_file, "r") as f :
        setting_data = json.load(f)
    return setting_data['anime_library_id']


def fresh_anime_library() :
    try :
        base_url = get_jellyfin_url()
        library_id = get_anime_library_id()
        token = get_jellyfin_token()
        url = f"{base_url}/Library/Refresh?LibraryId={library_id}"
        headers = {
            "Authorization" : f"MediaBrowser Token={token}",
            "Content-Type"  : "application/json"
        }

        response = requests.post(url, headers = headers)

        if response.status_code == 204 :
            logger.info("媒体库刷新成功")
        elif response.status_code == 401 :
            raise Exception("Unauthorized: Check your token.")
        elif response.status_code == 403 :
            raise Exception("Forbidden: You don't have permission to perform this action.")
        else :
            raise Exception(f"Unexpected response: {response.status_code}")
    except Exception as e :
        logger.error(str(e))
