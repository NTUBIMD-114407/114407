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
        db_info = connection.get_server_info()
        print("成功連接到MySQL數據庫！")
        print(f"MySQL版本: {db_info}")
        
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print(f"當前數據庫: {record[0]}")
        
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("\n數據庫中的表:")
        for table in tables:
            print(f"- {table[0]}")

except mysql.connector.Error as e:
    print(f"連接錯誤: {e}")
    print("\n請確認：")
    print("1. 資料庫伺服器是否正在運行")
    print("2. 用戶名和密碼是否正確")
    print("3. 您的IP是否有權限訪問資料庫")
    print("4. 資料庫名稱是否正確")
    print(f"\n您的當前IP: {connection.server_host if 'connection' in locals() else '未知'}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL連接已關閉") 