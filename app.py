from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sqlite3
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')
CORS(app)  # CORSを有効化

# データベースのパス設定
DB_PATH = os.environ.get('DATABASE_URL', 'reservation.db')

# データベース接続を取得する関数
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# データベースの初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 利用者テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 備品テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 予約テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time_slots TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/users')
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(users)
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/items')
def get_items():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(items)
    except Exception as e:
        print(f"Error in get_items: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservations')
def get_reservations():
    date = request.args.get('date')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date:
            cursor.execute('''
            SELECT r.id, r.date, r.time_slots, r.user_id, r.item_id, u.name as user_name, i.name as item_name
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            JOIN items i ON r.item_id = i.id
            WHERE r.date = ?
            ''', (date,))
        else:
            cursor.execute('''
            SELECT r.id, r.date, r.time_slots, r.user_id, r.item_id, u.name as user_name, i.name as item_name
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            JOIN items i ON r.item_id = i.id
            ''')
        
        reservations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'reservations': reservations})
    except Exception as e:
        print(f"Error in get_reservations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'リクエストデータがありません'}), 400
    
    user_id = data.get('user_id')
    item_id = data.get('item_id')
    date = data.get('date')
    time_slots = data.get('time_slots')
    
    if not user_id or not item_id or not date or not time_slots:
        return jsonify({'error': '全ての項目を入力してください'}), 400
    
    # 予約の重複チェック
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM reservations
        WHERE date = ? AND item_id = ? AND (
            time_slots LIKE ? OR
            time_slots LIKE ? OR
            time_slots LIKE ?
        )
        ''', (date, item_id, f"%{time_slots}%", f"%{time_slots},%", f"%,{time_slots}%"))
        
        existing_reservation = cursor.fetchone()
        
        if existing_reservation:
            conn.close()
            return jsonify({'error': 'この時間帯は既に予約されています'}), 400
        
        # 予約を作成
        cursor.execute('''
        INSERT INTO reservations (date, time_slots, user_id, item_id)
        VALUES (?, ?, ?, ?)
        ''', (date, time_slots, user_id, item_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '予約が完了しました', 'success': True})
    except Exception as e:
        print(f"Error in create_reservation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reservations WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '予約を削除しました', 'success': True})
    except Exception as e:
        print(f"Error in delete_reservation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservations/all', methods=['DELETE'])
def delete_all_reservations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reservations')
        conn.commit()
        conn.close()
        
        return jsonify({'message': '全ての予約を削除しました', 'success': True})
    except Exception as e:
        print(f"Error in delete_all_reservations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'リクエストデータがありません'}), 400
    
    name = data.get('name')
    
    if not name:
        return jsonify({'error': '利用者名を入力してください'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 既存の利用者をチェック
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'この利用者名は既に登録されています'}), 400
        
        # 新しい利用者を追加
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        
        # 追加した利用者のIDを取得
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'id': user_id, 'name': name, 'success': True})
    except Exception as e:
        print(f"Error in add_user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'リクエストデータがありません'}), 400
    
    name = data.get('name')
    
    if not name:
        return jsonify({'error': '備品名を入力してください'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 既存の備品をチェック
        cursor.execute('SELECT * FROM items WHERE name = ?', (name,))
        existing_item = cursor.fetchone()
        
        if existing_item:
            conn.close()
            return jsonify({'error': 'この備品名は既に登録されています'}), 400
        
        # 新しい備品を追加
        cursor.execute('INSERT INTO items (name) VALUES (?)', (name,))
        conn.commit()
        
        # 追加した備品のIDを取得
        item_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'id': item_id, 'name': name, 'success': True})
    except Exception as e:
        print(f"Error in add_item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservations/all')
def get_all_reservations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # すべての予約を取得
        cursor.execute('''
            SELECT 
                r.id, r.date, r.time_slots, r.user_id, r.item_id, 
                u.name as user_name, i.name as item_name
            FROM 
                reservations r
            JOIN 
                users u ON r.user_id = u.id
            JOIN 
                items i ON r.item_id = i.id
            ORDER BY 
                r.date, r.time_slots
        ''')
        
        reservations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'reservations': reservations})
    except Exception as e:
        print(f"Error in get_all_reservations: {str(e)}")
        return jsonify({"error": str(e)}), 500

# アプリケーション起動前にデータベースを初期化
if not os.path.exists(DB_PATH):
    init_db()

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5003) 