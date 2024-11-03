from app.models.sql.bangumi_table import BangumiTable
from app.models.sql.rss_item_table import RssItemTable

BangumiTable.create_bangumi_table_if_not_exists()
