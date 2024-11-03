import sqlite3


def create_table_if_not_exists(table_path, table_schema) :
    """
    假设没有数据库文件、或者没有对应的数据库的表，会执行table_schema创建对应的表格
    :param table_path: 创建对应表格的路径
    :param table_schema: 创建对应表格的参数
    """
    conn = sqlite3.connect(table_path)
    cursor = conn.cursor()
    cursor.execute(table_schema)
    conn.commit()
    conn.close()
