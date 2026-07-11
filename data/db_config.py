# Neon Postgres 數據庫配置 (v3.5)
# 提供數據庫連接和數據訪問功能

import os

# Neon 數據庫連接字符串
# 優先從環境變量獲取，否則使用默認值
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_sVKUOn6P2BlW@ep-ancient-cherry-afmoe2xv-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
)

# 數據表名稱
TABLES = {
    "estates": "estates",
    "listings": "listings", 
    "sha_poi": "sha_poi",
    "estates_unified": "estates_unified",
}


def get_db_url():
    """獲取數據庫連接URL"""
    return DATABASE_URL


def get_connection_dict():
    """獲取連接參數字典（用於psycopg2）"""
    # 簡單解析連接字符串
    # 格式: postgresql://user:pass@host:port/dbname?params
    url = DATABASE_URL
    
    # 去掉 postgresql:// 前綴
    if url.startswith("postgresql://"):
        url = url[13:]
    elif url.startswith("postgres://"):
        url = url[11:]
    
    # 分離參數
    if "?" in url:
        url, params = url.split("?", 1)
    else:
        params = ""
    
    # 解析用戶名密碼和主機
    if "@" in url:
        creds, host_part = url.split("@", 1)
        if ":" in creds:
            user, password = creds.split(":", 1)
        else:
            user = creds
            password = ""
    else:
        user = ""
        password = ""
        host_part = url
    
    # 解析主機和數據庫名
    if "/" in host_part:
        host_port, dbname = host_part.split("/", 1)
    else:
        host_port = host_part
        dbname = "neondb"
    
    # 解析主機和端口
    if ":" in host_port:
        host, port = host_port.rsplit(":", 1)
        try:
            port = int(port)
        except:
            port = 5432
    else:
        host = host_port
        port = 5432
    
    return {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
        "sslmode": "require"
    }
