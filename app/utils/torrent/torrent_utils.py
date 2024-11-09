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


def get_torrent_file_len(torrent_path) :
    with open(torrent_path, "rb") as f :
        # 解码torrent文件
        decoded_data = bencodepy.decode(f.read())

        # 断言解码后的数据是一个字典
        assert isinstance(decoded_data, dict), "Decoded data is not a dictionary"
        torrent_data = dict(decoded_data)

        # 获取info字段
        info = torrent_data.get(b"info")

        if not info :
            raise ValueError("Invalid torrent file: 'info' field not found.")

        # 检查是否是单文件还是多文件torrent
        if b"files" in info :
            # 多文件torrent
            return len(info[b"files"])
        else :
            # 单文件torrents
            return 1
