from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from app.models.subscription_data import SubscriptionData


def _load_json(path: Path) -> Dict[str, Any] :
    with path.open("r", encoding = "utf-8") as f :
        return json.load(f)


def _dump_json_atomic(path: Path, data: Dict[str, Any]) -> None :
    # 原子写，避免并发/崩溃导致的半写文件
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding = "utf-8") as f :
        json.dump(data, f, indent = 4, ensure_ascii = False)
        f.flush()
    tmp.replace(path)


@dataclass(slots = True)
class _Files :
    config: Path
    setting: Path
    subscription: Path
    sql: Path


class Config :
    """
    - 缓存 JSON 内容，避免每次 get_* 都读文件
    - set_config 原子写入，并更新缓存
    - 提供 fresh_config()/renew_temp_rss()/clear_temp_rss() 时同步缓存
    - 做了缺省值与健壮性处理
    - 对外保持原有属性与方法名：mysql_url/mysql_username/REDACTED_MYSQL_PASSWORD、
      my_domain/use_domain/mikan_*、rss_url/filters、bangumi_subscription 等
    """

    # 常量放一处
    _MIKAN_EPISODE = "https://mikanani.me/Home/Episode/"
    _MIKAN_HOME = "https://mikanani.me/Home/Bangumi/"

    def __init__(
            self,
            config_file: str | Path,
            setting_file: str | Path,
            subscription_file: str | Path,
            sql_file: str | Path = "data/sql.json",
    ) -> None :
        self._files = _Files(
                config = Path(config_file),
                setting = Path(setting_file),
                subscription = Path(subscription_file),
                sql = Path(sql_file),
        )

        # 缓存
        self._config_data: Dict[str, Any] = _load_json(self._files.config)
        self._setting_data: Dict[str, Any] = _load_json(self._files.setting)
        self._subscription_data: Dict[str, Any] = _load_json(self._files.subscription)
        self._sql_data: Dict[str, Any] = _load_json(self._files.sql)

        # 公开属性（保持命名不变）
        self.bangumi_subscription: List[SubscriptionData] = []

        self.my_domain: str = self._get_cfg_str("my_domain", "")
        self.use_domain: bool = self.my_domain != ""
        self.mikan_episode: str = self._MIKAN_EPISODE
        self.mikan_home: str = self._MIKAN_HOME
        self.rss_url: str = self._get_cfg_str("mikan_rss_url", "")

        # 读取 MySQL 配置（保持原有三个公开属性名）
        self.mysql_url: str = str(self._sql_data.get("mysql_url", ""))
        self.mysql_username: str = str(self._sql_data.get("mysql_username", ""))
        self.REDACTED_MYSQL_PASSWORD: str = str(self._sql_data.get("mysql_password", ""))

        self.get_bangumi_moe_subscription()

    # ----------------- 内部小工具 -----------------

    def _get_cfg_str(self, key: str, default: str = "") -> str :
        v = self._config_data.get(key, default)
        return str(v) if v is not None else default

    # ----------------- 公开 API（保留原方法名） -----------------

    def get_config(self, key: str) -> Any :
        """获取config文件的信息（现在直接从缓存取，避免重复 I/O）"""
        return self._config_data.get(key)

    def get_setting(self, key: str) -> Any :
        """获取setting文件的信息（从缓存取）"""
        return self._setting_data.get(key)

    def set_config(self, key: str, value: Any) -> None :
        """
        修改config文件的信息（原子写入 + 更新缓存）
        """
        self._config_data[key] = value
        _dump_json_atomic(self._files.config, self._config_data)

    def fresh_config(self) -> None :
        """
        重新加载 config/setting，并刷新派生字段
        """
        self._config_data = _load_json(self._files.config)
        self._setting_data = _load_json(self._files.setting)

        self.my_domain = self._get_cfg_str("my_domain", "")
        self.use_domain = self.my_domain != ""
        self.mikan_episode = self._MIKAN_EPISODE
        self.mikan_home = self._MIKAN_HOME
        self.rss_url = self._get_cfg_str("mikan_rss_url", "")

    def get_bangumi_moe_subscription(self) -> None :
        """
        从 subscription.json 解析 bangumi_moe 列表
        """
        # 使用内存缓存；若外部有人改了文件，可先调用 refresh_subscription()
        subs = self._subscription_data.get("bangumi_moe", []) or []
        self.bangumi_subscription.clear()
        for sub_json in subs :
            rss_url = sub_json.get("rss_url")
            subject_id = sub_json.get("subject_id")
            if not rss_url or subject_id is None :
                continue
            self.bangumi_subscription.append(
                    SubscriptionData(rss_url = rss_url, subject_id = subject_id)
            )

    def refresh_subscription(self) -> None :
        """当 subscription_file 发生外部修改时调用，刷新内存并重建列表"""
        self._subscription_data = _load_json(self._files.subscription)
        self.get_bangumi_moe_subscription()

    def get_temp_rss(self) -> List[str] :
        temp_list = self._subscription_data.get("temp_mikan", []) or []
        # 强制为 List[str]
        return [str(x) for x in temp_list]

    def renew_temp_rss(self, temp_list: List[str]) -> None :
        self._subscription_data["temp_mikan"] = list(temp_list)
        _dump_json_atomic(self._files.subscription, self._subscription_data)

    def clear_temp_rss(self) -> None :
        self._subscription_data["temp_mikan"] = []
        _dump_json_atomic(self._files.subscription, self._subscription_data)
