from app.models.sql.bangumi_table import BangumiTable
from app.models.sql.database import Base, create_all_tables, engine, get_session
from app.models.sql.rss_item_table import RssItemTable

# 应用启动时创建所有表
create_all_tables()
