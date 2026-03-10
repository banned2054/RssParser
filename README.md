# RssParser

一个自动化的动漫 RSS 订阅下载工具，支持从 Mikanani 和 Bangumi.moe 等站点获取 RSS 订阅，自动解析并下载到 qBittorrent，同时支持通知推送和媒体库刷新。

## 功能特性

- **多源 RSS 支持**: 支持 Mikanani 和 Bangumi.moe 的 RSS 订阅
- **智能解析**: 使用 `pyaniparser` 智能解析番剧标题、集数、字幕组等信息
- **自动下载**: 自动将种子添加到 qBittorrent 并管理下载任务
- **智能命名**: 根据 Bangumi 信息自动重命名下载的文件和文件夹
- **通知推送**: 支持 Gotify 和 Telegram 通知
- **媒体库集成**: 支持 Jellyfin 媒体库自动刷新
- **数据库管理**: 使用 MySQL 存储番剧信息和下载记录
- **多进程架构**: RSS 抓取和种子管理独立进程运行

## 项目结构

```
RssParser/
├── app/
│   ├── config_setting.py      # 配置管理
│   ├── controllers/           # 业务控制器
│   │   ├── bangumi_controller.py   # Bangumi.moe RSS 处理
│   │   ├── mikan_controller.py     # Mikanani RSS 处理
│   │   ├── temp_controller.py      # 临时 RSS 处理
│   │   └── torrent_controller.py   # 种子下载管理
│   ├── models/                # 数据模型
│   │   ├── bangumi_subject_info.py
│   │   ├── mikan_rss_info.py
│   │   ├── subscription_data.py
│   │   └── sql/               # 数据库模型
│   │       ├── bangumi_table.py
│   │       ├── rss_item_table.py
│   │       └── database.py
│   └── utils/                 # 工具模块
│       ├── parser/            # 解析器
│       │   ├── bangumi_parser.py
│       │   ├── mikan_parser.py
│       │   └── title_parser.py
│       ├── torrent/           # 种子工具
│       │   ├── qbittorrent_utils.py
│       │   └── torrent_utils.py
│       ├── file_utils.py
│       ├── gotify_utils.py
│       ├── jellyfin_utils.py
│       ├── log_utils.py
│       ├── net_utils.py
│       ├── telegram_utils.py
│       └── time_utils.py
├── data/                      # 配置文件目录
│   ├── config.json.example    # 主配置示例
│   ├── jellyfin.json.example  # Jellyfin 配置示例
│   ├── setting.json           # 请求头配置
│   ├── sql.json.example       # 数据库配置示例
│   └── subscription.json.example  # 订阅配置示例
├── main.py                    # 程序入口
├── pyproject.toml             # 项目依赖配置
└── uv.lock                    # uv 锁定文件
```

## 安装

### 环境要求

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) 包管理器
- MySQL 数据库
- qBittorrent

### 安装步骤

1. 克隆仓库

```bash
git clone <repository-url>
cd RssParser
```

2. 使用 uv 安装依赖

```bash
uv sync
```

3. 复制配置文件模板并进行配置

```bash
cp data/config.json.example data/config.json
cp data/sql.json.example data/sql.json
cp data/subscription.json.example data/subscription.json
cp data/jellyfin.json.example data/jellyfin.json
```

## 配置说明

### config.json

```json
{
    "anime_path": "Anime",                          // 动漫保存子目录
    "tokusatsu_path": "Tokusatsu",                  // 特摄保存子目录
    "download_path": "/downloads/Media",            // 下载根目录
    "dir_name": "[/year/./month/]/cn_name/",        // 文件夹命名格式
    "file_name": "/cn_name/ E/episode/",            // 文件命名格式
    "qbittorrent_name": "[/type/]/cn_name/ E/episode/",  // qBittorrent 显示名称格式
    "mikan_rss_url": "https://mikanani.me/RSS/...", // Mikanani RSS 地址
    "qbittorrent_url": "http://localhost:8080",     // qBittorrent Web UI 地址
    "qbittorrent_username": "admin",                // qBittorrent 用户名
    "qbittorrent_password": "password",             // qBittorrent 密码
    "proxy_url": "http://127.0.0.1:7890",           // 代理地址（可选）
    "interval_time_to_rss": "300",                  // RSS 抓取间隔（秒）
    "gotify_url": "",                               // Gotify 服务器地址
    "gotify_start_download_token": "",              // Gotify 开始下载通知 Token
    "gotify_finish_download_token": "",             // Gotify 完成下载通知 Token
    "telegram_token": "",                           // Telegram Bot Token
    "telegram_chat_id": "",                         // Telegram Chat ID
    "telegram_channel_id": "",                      // Telegram Channel ID
    "timezone": "Asia/Shanghai"                     // 时区设置
}
```

### sql.json

```json
{
    "mysql_url": "localhost",
    "mysql_username": "root",
    "mysql_password": "password"
}
```

### subscription.json

```json
{
    "bangumi_moe": [
        {
            "rss_url": "https://bangumi.moe/rss/...",
            "subject_id": 123456
        }
    ],
    "temp_mikan": []
}
```

### jellyfin.json

```json
{
    "jellyfin_url": "http://localhost:8096",
    "jellyfin_token": "your-api-token",
    "anime_library_id": "your-library-id"
}
```

## 使用方法

### 启动程序

```bash
uv run python main.py
```

程序启动后会创建两个独立进程：

- **RSSWorker**: 定期抓取 RSS 订阅并添加下载任务
- **TorrentWorker**: 监控下载状态并发送完成通知

### 停止程序

按 `Ctrl+C` 即可优雅地停止程序。再次按 `Ctrl+C` 可强制退出。

## 命名格式变量

在 `dir_name`、`file_name` 和 `qbittorrent_name` 中可以使用以下变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `/cn_name/` | 中文名称 | 葬送的芙莉莲 |
| `/jp_name/` | 日文名称 | 葬送のフリーレン |
| `/romaji_name/` | 罗马音名称 | Sousou no Frieren |
| `/year/` | 年份 | 2023 |
| `/month/` | 月份 | 10 |
| `/type/` | 类型 | tv / movie / ova |
| `/episode/` | 集数 | 01 |

## 支持的 RSS 源

### Mikanani

- 支持个人订阅 RSS
- 自动解析番剧信息并关联 Bangumi
- 支持 1080p 筛选
- 优先下载 ANi、LoliHouse、简中字幕组作品

### Bangumi.moe

- 支持自定义 RSS 订阅
- 需要手动配置 `subject_id` 关联 Bangumi

## 数据库表结构

### bangumi_table

存储番剧基本信息：

- `id`: Bangumi Subject ID
- `cn_name`: 中文名称
- `jp_name`: 日文名称
- `romaji_name`: 罗马音名称
- `year`: 年份
- `month`: 月份
- `type`: 类型 (TV/Movie/OVA)
- `image_url`: 封面图片 URL

### rss_item_table

存储 RSS 条目和下载记录：

- `id`: 自增 ID
- `item_name`: 项目名称
- `origin_name`: 原始 RSS 标题
- `item_title`: RSS 条目标题
- `mikan_url`: Mikan 页面 URL
- `bangumi_id`: 关联的 Bangumi ID
- `episode`: 集数
- `pub_date`: 发布时间
- `hash`: 种子 Hash
- `downloaded`: 是否已下载
- `version`: 版本号

## 开发

### 代码风格

- 使用 `uv` 管理依赖
- 函数定义包含 Type Hints
- 遵循 PEP 8 规范

### 提交规范

- 格式: `type: <描述>` (例如 feat, fix, refactor, docs)
- 原子化提交，不同功能拆分为独立 Commit
- 使用简体中文描述（项目环境为英文时切换为英文）

## 依赖列表

- `aiohttp`: 异步 HTTP 客户端
- `beautifulsoup4`: HTML 解析
- `bencodepy`: BT 种子解析
- `cryptography`: 加密功能
- `feedparser`: RSS 解析
- `gotify`: Gotify 通知
- `pyaniparser`: 番剧标题解析
- `pymysql`: MySQL 连接
- `python-telegram-bot`: Telegram Bot
- `pytz`: 时区处理
- `qbittorrent-api`: qBittorrent API
- `requests`: HTTP 请求
- `sqlalchemy`: ORM 框架

## License

[MIT License](LICENSE)
