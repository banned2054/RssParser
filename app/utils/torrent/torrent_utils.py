import hashlib

import bencodepy


def get_torrent_info_hash(torrent_path) :
    with open(torrent_path, 'rb') as f :
        torrent_data = bencodepy.decode(f.read())

        # 检查是否返回了字典
        if isinstance(torrent_data, dict) and b'info' in torrent_data :
            info_data = bencodepy.encode(torrent_data[b'info'])
            info_hash = hashlib.sha1(info_data).hexdigest()
            return info_hash
        else :
            raise ValueError("The torrent file is not correctly formatted or lacks an 'info' dictionary.")
