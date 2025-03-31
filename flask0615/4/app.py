#-----------------------
# 匯入flask及db模組
#-----------------------
from flask import Flask, render_template,request
import db

#-----------------------
# 產生一個Flask網站物件
#-----------------------
app = Flask(__name__)

#-----------------------
# 在網站中定義路由
#-----------------------
#主畫面
@app.route('/')
def index():
    return render_template('index.html') 

# 客戶清單
@app.route('/customer/list')
def customer_list():
    # 每頁顯示筆數
    items_per_page = 10

    # 取得目前頁數，預設為第 1 頁
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * items_per_page

    # 取得資料庫連線
    connection = db.get_connection()

    # 產生執行 SQL 命令的物件
    cursor = connection.cursor()

    # 計算總筆數
    cursor.execute('SELECT COUNT(*) FROM customer;')
    total_items = cursor.fetchone()[0]

    # 計算總頁數
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # 執行 SQL，取得分頁資料
    cursor.execute(
        'SELECT cusno, cusname, address, tel FROM customer ORDER BY cusno LIMIT %s OFFSET %s;',
        (items_per_page, offset)
    )
    data = cursor.fetchall()

    # 關閉資料庫連線
    connection.close()

    # 格式化資料
    if data:
        params = [{'cusno': d[0], 'cusname': d[1], 'address': d[2], 'tel': d[3]} for d in data]
    else:
        params = None

    # 將參數送給網頁，讓資料嵌入網頁中
    return render_template(
        '/customer/list.html',
        data=params,
        page=page,
        total_pages=total_pages
    )

#-----------------------
# 啟動Flask網站
#-----------------------
if __name__ == '__main__':
    app.run(debug=True)