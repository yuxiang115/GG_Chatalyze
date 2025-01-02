from app.configs.db_config import get_mysql_connection
from datetime import datetime



def fetch_player_with_most_recent_matches():
    """Fetch all players with their matches."""
    connection = get_mysql_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.player_id,
                p.personal_name,
                p.discord_id,
                pm.match_id,
                pm.start_time AS match_start_time
            FROM (
                SELECT 
                    player_id, 
                    match_id, 
                    start_time,
                    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY start_time DESC) AS rank
                FROM player_match
            ) pm
            JOIN players p ON pm.player_id = p.player_id
            WHERE pm.rank = 1;
        """)
        players = cursor.fetchall()
        cursor.close()
        return players
    return []

def fetch_all_players_id():
    """获取所有玩家的 player_id"""
    connection = get_mysql_connection()  # 获取数据库连接
    if connection:
        cursor = connection.cursor(dictionary=True)  # 创建游标
        try:
            cursor.execute("SELECT DISTINCT player_id FROM players")
            players = cursor.fetchall()  # 确保结果被完全读取
            cursor.close()  # 关闭游标，释放资源
            return [player['player_id'] for player in players]
        except Exception as e:
            print(f"查询玩家信息时发生错误: {e}")
            return []
        finally:
            connection.close()  # 无论是否发生异常，都确保关闭连接
    return []

def fetch_players_id_auto_analyze_enable():
    """获取所有玩家的 player_id，且自动分析结束时间早于当前时间"""
    connection = get_mysql_connection()
    now_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(f"""
                SELECT DISTINCT p.player_id
                FROM players p 
                WHERE p.auto_analyze_end_datetime > '{now_timestamp}'
            """)
            players = cursor.fetchall()
            cursor.close()
            return [player['player_id'] for player in players]
        except Exception as e:
            print(f"查询玩家信息时发生错误: {e}")
            return []
        finally:
            connection.close()
    return []

def put_player(player_id, personal_name, discord_id, auto_analyze_end_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
    """添加玩家信息"""
    connection = get_mysql_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # use upsert to avoid duplicate entries
            cursor.execute("""
                INSERT INTO players (player_id, personal_name, discord_id, auto_analyze_end_datetime) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    personal_name = %s, 
                    discord_id = %s, 
                    auto_analyze_end_datetime = %s
                """,
                (player_id, personal_name, discord_id, auto_analyze_end_datetime, personal_name, discord_id, auto_analyze_end_datetime)
            )
            connection.commit()
            return True
        except Exception as e:
            print(f"添加玩家信息时发生错误: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
    return False


def get_player(player_id):
    """获取所有玩家的 player_id"""
    connection = get_mysql_connection()  # 获取数据库连接
    if connection:
        cursor = connection.cursor(dictionary=True)  # 创建游标
        try:
            cursor.execute("""
            SELECT player_id, personal_name, discord_id, auto_analyze_end_datetime
            FROM players
            WHERE player_id = %s
            """, (player_id,))
            player = cursor.fetchall() # 确保结果被完全读取
            cursor.close()  # 关闭游标，释放资源
            return player[0] if player else None
        except Exception as e:
            print(f"查询玩家信息时发生错误: {e}")
            return []
        finally:
            connection.close()  # 无论是否发生异常，都确保关闭连接
    return []

def fetch_player_by_discord_id(discord_id):
    """根据 discord_id 获取玩家信息"""
    connection = get_mysql_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
            SELECT player_id, personal_name, discord_id, auto_analyze_end_datetime
            FROM players
            WHERE discord_id = %s
            """, (discord_id,))
            player = cursor.fetchall()
            cursor.close()
            return player[0] if player else None
        except Exception as e:
            print(f"查询玩家信息时发生错误: {e}")
            return []
        finally:
            connection.close()
    return None