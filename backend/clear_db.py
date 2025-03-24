import mysql.connector

try:
    connection = mysql.connector.connect(
        host='140.131.114.242',
        database='114-NTUBMRT',
        user='NTUB114407',
        password='Mrt11146@',
        port=3306
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # 禁用外鍵檢查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 獲取所有表名
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # 刪除所有表
        for table in tables:
            print(f"刪除表: {table[0]}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table[0]}`")
        
        # 啟用外鍵檢查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print("\n所有表已成功刪除")
        
except mysql.connector.Error as e:
    print(f"錯誤: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL連接已關閉") 