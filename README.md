# 備品貸出予約管理システム

備品の貸出予約を管理するためのWebアプリケーションです。カレンダーベースで備品の予約状況を視覚的に確認し、簡単に予約を作成・管理できます。

## 主な機能

- カレンダー形式での予約表示と管理
- 備品・利用者の管理
- 日付・時間帯指定での予約作成
- フィルタリング機能（備品カテゴリ別）
- 予約リスト表示
- レスポンシブデザイン（モバイル対応）

## 技術スタック

- フロントエンド: HTML, CSS, JavaScript (vanilla)
- バックエンド: Python, Flask
- データベース: SQLite

## インストール方法

### 必要条件

- Python 3.8以上
- pip

### 手順

1. リポジトリをクローン
   ```
   git clone https://github.com/sumichichi2015/equipment-reservation-system.git
   cd equipment-reservation-system
   ```

2. 仮想環境を作成し、有効化
   ```
   python3 -m venv venv
   source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
   ```

3. 依存パッケージをインストール
   ```
   pip3 install -r requirements.txt
   ```

4. アプリケーションを起動
   ```
   python3 app.py
   ```

5. ブラウザで http://localhost:5003 にアクセス

## 使い方

1. カレンダーから日付を選択
2. 「新規予約」ボタンをクリック
3. 利用者、備品、時間枠を選択
4. 「予約する」ボタンをクリック

## スクリーンショット

![カレンダー画面](docs/images/calendar_screenshot.png)
![予約フォーム](docs/images/reservation_form_screenshot.png)

## ライセンス

MITライセンス 