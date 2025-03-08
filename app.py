from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# データベースの初期化
def init_db():
    conn = sqlite3.connect('reservation.db')
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
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time_slots TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
    ''')
    
    # サンプルデータの挿入
    sample_users = [('山田太郎',), ('佐藤花子',), ('鈴木一郎',)]
    sample_items = [('プロジェクター',), ('会議室A',), ('ノートPC',), ('タブレット',)]
    
    for user in sample_users:
        try:
            cursor.execute('INSERT INTO users (name) VALUES (?)', user)
        except sqlite3.IntegrityError:
            pass
    
    for item in sample_items:
        try:
            cursor.execute('INSERT INTO items (name) VALUES (?)', item)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# ルート
@app.route('/')
def index():
    return render_template('index.html')

# 利用者一覧を取得
@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('reservation.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY name')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

# 備品一覧を取得
@app.route('/api/items')
def get_items():
    conn = sqlite3.connect('reservation.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items ORDER BY name')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

# 予約を取得
@app.route('/api/reservations')
def get_reservations():
    date = request.args.get('date')
    
    conn = sqlite3.connect('reservation.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if date:
        cursor.execute('''
        SELECT r.*, u.name as user_name, i.name as item_name 
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN items i ON r.item_id = i.id
        WHERE r.date = ?
        ''', (date,))
    else:
        cursor.execute('''
        SELECT r.*, u.name as user_name, i.name as item_name 
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN items i ON r.item_id = i.id
        ''')
    
    reservations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(reservations)

# 予約を作成
@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.json
    user_id = data.get('user_id')
    item_id = data.get('item_id')
    date = data.get('date')
    time_slots = data.get('time_slots')
    
    # 時間枠が連続しているか確認
    time_slots_list = time_slots.split(',')
    time_slots_list = [int(slot) for slot in time_slots_list]
    time_slots_list.sort()
    
    for i in range(len(time_slots_list) - 1):
        if time_slots_list[i + 1] - time_slots_list[i] != 1:
            return jsonify({'error': '連続していない時間枠は選択できません'}), 400
    
    # 予約の重複チェック
    conn = sqlite3.connect('reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT time_slots FROM reservations 
    WHERE date = ? AND item_id = ?
    ''', (date, item_id))
    
    existing_reservations = cursor.fetchall()
    
    for reservation in existing_reservations:
        existing_slots = reservation[0].split(',')
        existing_slots = [int(slot) for slot in existing_slots]
        
        # 重複チェック
        if any(slot in existing_slots for slot in time_slots_list):
            conn.close()
            return jsonify({'error': '選択した時間枠は既に予約されています'}), 400
    
    # 予約を作成
    cursor.execute('''
    INSERT INTO reservations (user_id, item_id, date, time_slots)
    VALUES (?, ?, ?, ?)
    ''', (user_id, item_id, date, time_slots))
    
    conn.commit()
    reservation_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': reservation_id, 'message': '予約が完了しました'})

# 予約を削除
@app.route('/api/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    conn = sqlite3.connect('reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM reservations WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '予約を削除しました'})

# 管理者ページ
@app.route('/admin')
def admin():
    return render_template('admin.html')

# 全予約を削除
@app.route('/api/reservations/all', methods=['DELETE'])
def delete_all_reservations():
    conn = sqlite3.connect('reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM reservations')
    conn.commit()
    conn.close()
    
    return jsonify({'message': '全ての予約を削除しました'})

# 新しい利用者を追加
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': '利用者名を入力してください'}), 400
    
    conn = sqlite3.connect('reservation.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': user_id, 'name': name})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'この利用者名は既に登録されています'}), 400

# 新しい備品を追加
@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': '備品名を入力してください'}), 400
    
    conn = sqlite3.connect('reservation.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO items (name) VALUES (?)', (name,))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': item_id, 'name': name})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'この備品名は既に登録されています'}), 400

@app.route('/api/reservations/all')
def get_all_reservations():
    conn = sqlite3.connect('reservation.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # すべての予約を取得
    c.execute('''
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
    
    reservations = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({'reservations': reservations})

if __name__ == '__main__':
    if not os.path.exists('reservation.db'):
        init_db()
    app.run(debug=True, port=5003) 