from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from urllib.parse import parse_qs
import html
import sqlite3

HOST = "0.0.0.0"
PORT = 8080
DB_PATH = "demo_users.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                display_name TEXT NOT NULL,
                address TEXT NOT NULL,
                credit_card TEXT NOT NULL
            )
            """
        )
        conn.execute("DELETE FROM users")
        conn.executemany(
            "INSERT INTO users (username, password, display_name, address, credit_card) VALUES (?, ?, ?, ?, ?)",
            [
                ("admin", "musclewaf", "システム管理者", "東京都千代田区1-1-1", "1234-5678-9012-3456"),
                ("yamada", "taro123", "山田 太郎", "東京都渋谷区神南1-2-3", "9876-5432-1098-7654"),
                ("sato", "hanako123", "佐藤 花子", "大阪府大阪市北区梅田2-4-6", "1111-2222-3333-4444"),
                ("zawa", "zawa123", "黒澤 亮太", "神奈川県横浜市西区みなとみらい3-5", "5555-6666-7777-8888"),
            ],
        )
        conn.commit()
    finally:
        conn.close()

def page(message="", username="", status=""):
    escaped_message = html.escape(message)
    escaped_username = html.escape(username)
    status_class = html.escape(status or "neutral")
    
    # メッセージ（エラー時など）の表示ブロック
    message_html = ""
    if escaped_message:
        message_html = f'<div class="message {status_class}">{escaped_message}</div>'

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ログイン - MuscleMart (プロテイン・筋トレ器具専門店)</title>
  <style>
    :root {{
      --primary: #ea580c; /* フィットネスらしいオレンジに変更 */
      --primary-hover: #c2410c;
      --bg: #f3f4f6;
      --text: #1f2937;
      --border: #e5e7eb;
      --danger: #ef4444;
      --danger-bg: #fef2f2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    header {{
      background: #111827; /* 力強いダークなヘッダー */
      padding: 1.2rem 0;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .container {{
      max-width: 1000px;
      margin: 0 auto;
      padding: 0 1rem;
    }}
    .header-inner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo {{
      font-size: 1.8rem;
      font-weight: 900;
      color: #ffffff;
      text-decoration: none;
      letter-spacing: 1px;
      text-transform: uppercase;
      font-style: italic;
    }}
    .logo span {{
      color: var(--primary);
    }}
    main {{
      padding: 4rem 1rem;
      display: flex;
      justify-content: center;
      min-height: calc(100vh - 160px);
    }}
    .login-box {{
      background: #ffffff;
      padding: 2.5rem;
      border-radius: 8px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      width: 100%;
      max-width: 420px;
      border-top: 5px solid var(--primary);
    }}
    h1 {{
      margin: 0 0 1.5rem;
      font-size: 1.4rem;
      text-align: center;
      color: #111827;
      font-weight: 800;
    }}
    .form-group {{
      margin-bottom: 1.2rem;
    }}
    label {{
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      font-weight: 700;
      color: #374151;
    }}
    input[type="text"], input[type="password"] {{
      width: 100%;
      padding: 0.75rem;
      border: 2px solid #e5e7eb;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s;
    }}
    input:focus {{
      outline: none;
      border-color: var(--primary);
    }}
    button {{
      width: 100%;
      padding: 0.85rem;
      margin-top: 1rem;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1.1rem;
      font-weight: 800;
      cursor: pointer;
      transition: background-color 0.2s;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    button:hover {{
      background: var(--primary-hover);
    }}
    .message {{
      padding: 0.75rem 1rem;
      border-radius: 6px;
      margin-bottom: 1.5rem;
      font-size: 0.9rem;
      line-height: 1.5;
      font-weight: 600;
    }}
    .message.error {{
      background: var(--danger-bg);
      color: var(--danger);
      border: 1px solid #fecaca;
    }}
    .message.neutral {{
      background: #f8fafc;
      color: #475569;
      border: 1px solid #e2e8f0;
    }}
    footer {{
      text-align: center;
      padding: 2rem;
      color: #9ca3af;
      font-size: 0.875rem;
      background: #111827;
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a href="/" class="logo">Muscle<span>Mart</span></a>
    </div>
  </header>
  <main>
    <div class="login-box">
      <h1>メンバーログイン</h1>
      {message_html}
      <form method="post" action="/login">
        <div class="form-group">
          <label for="username">ユーザー名 または メールアドレス</label>
          <input type="text" id="username" name="username" value="{escaped_username}" required>
        </div>
        <div class="form-group">
          <label for="password">パスワード</label>
          <input type="password" id="password" name="password" required>
        </div>
        <button type="submit">ログイン</button>
      </form>
    </div>
  </main>
  <footer>
    &copy; 2026 MuscleMart Inc. All rights reserved.
  </footer>
</body>
</html>"""

def dashboard_page(display_name="", username=""):
    escaped_display_name = html.escape(display_name)
    escaped_username = html.escape(username)
    
    # ユーザー名がadminなら管理者画面、それ以外なら一般のマイページを表示
    is_admin = (username == "admin")
    
    if is_admin:
        title = "管理者ダッシュボード - MuscleMart"
        main_content = f"""
        <div class="admin-banner">
          <strong>【警告】</strong> 現在システム管理者権限でログインしています。顧客情報の閲覧・編集、在庫データの変更が可能です。
        </div>
        <h2>管理者コントロールパネル</h2>
        <div class="grid">
          <div class="card admin-card">
            <h3>📊 器具・プロテイン売上レポート</h3>
            <p>本日の売上高: ¥2,450,000<br>一番売れている商品: ホエイプロテイン WPI 1kg</p>
            <a href="#" class="btn btn-outline">詳細レポートを開く</a>
          </div>
          <div class="card admin-card">
            <h3>👥 メンバーデータベース</h3>
            <p>全トレーニーの個人情報、配送先、クレジットカード情報へのアクセスと管理を行います。</p>
            <a href="/admin/db" class="btn btn-outline" style="color: #b91c1c; border-color: #b91c1c;">DBへアクセス</a>
          </div>
          <div class="card admin-card">
            <h3>📦 在庫管理アラート</h3>
            <p style="color: #ea580c; font-weight: bold;">⚠️ アジャスタブルダンベル 32kg の在庫が残り3セットです。</p>
            <a href="#" class="btn btn-outline">発注システムを開く</a>
          </div>
        </div>
        """
    else:
        title = "ショッピング・マイページ - MuscleMart"
        main_content = f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border); padding-bottom: 0.8rem;">
          <h2 style="margin: 0; border: none; padding: 0;">{escaped_display_name} 様のマイページ</h2>
          <span style="font-weight: 600; color: #ea580c;">保有マッスルポイント: 3,500 pt</span>
        </div>
        
        <h3 style="margin-bottom: 1rem; color: #111827; font-size: 1.3rem;">🔥 今週のイチオシ商品</h3>
        <div class="grid">
          <!-- プロテイン -->
          <div class="card product-card">
            <div class="emoji-img">🥤</div>
            <h3>ホエイプロテイン WPI 1kg (ダブルリッチチョコレート味)</h3>
            <p>高純度のWPIを採用。吸収速度に優れ、激しいトレーニング後のタンパク質補給に最適です。</p>
            <div class="price">¥4,980</div>
            <button class="btn-primary">カートに入れる</button>
          </div>

          <!-- ダンベル -->
          <div class="card product-card">
            <div class="emoji-img">🏋️‍♂️</div>
            <h3>アジャスタブルダンベル 32kg × 2個セット</h3>
            <p>ダイヤルを回すだけで2kg〜32kgまで簡単に重量変更が可能。ホームジムの必須アイテム。</p>
            <div class="price">¥34,800</div>
            <button class="btn-primary">カートに入れる</button>
          </div>

          <!-- マシン/ラック -->
          <div class="card product-card">
            <div class="emoji-img">🏗️</div>
            <h3>ハーフラック スタンダードモデル (耐荷重300kg)</h3>
            <p>スクワット、ベンチプレスなどビッグ3に完全対応。極太フレームで安定感抜群のラックです。</p>
            <div class="price">¥89,000</div>
            <button class="btn-primary">大型配送・カートに入れる</button>
          </div>
          
          <!-- アクセサリー -->
          <div class="card product-card">
            <div class="emoji-img">🧤</div>
            <h3>本革パワーグリップ PRO</h3>
            <p>デッドリフトや懸垂時の握力サポートに。背中トレの質を劇的に向上させるマストアイテム。</p>
            <div class="price">¥6,500</div>
            <button class="btn-primary">カートに入れる</button>
          </div>
        </div>
        """

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --primary: #ea580c;
      --primary-hover: #c2410c;
      --admin-color: #dc2626;
      --bg: #f9fafb;
      --text: #1f2937;
      --border: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    header {{
      background: #111827;
      padding: 1rem 0;
    }}
    .container {{
      max-width: 1000px;
      margin: 0 auto;
      padding: 0 1rem;
    }}
    .header-inner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo {{
      font-size: 1.5rem;
      font-weight: 900;
      color: #ffffff;
      text-decoration: none;
      letter-spacing: 1px;
      text-transform: uppercase;
      font-style: italic;
    }}
    .logo span {{ color: var(--primary); }}
    main {{ padding: 2.5rem 1rem; min-height: calc(100vh - 160px); }}
    
    .admin-banner {{
      background: #fef2f2;
      border-left: 4px solid var(--admin-color);
      color: #991b1b;
      padding: 1rem 1.2rem;
      margin-bottom: 2rem;
      border-radius: 4px;
      font-size: 0.95rem;
      font-weight: bold;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.5rem;
    }}
    .card {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      display: flex;
      flex-direction: column;
    }}
    .admin-card {{ 
      border-top: 4px solid var(--admin-color); 
    }}
    .product-card {{
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .product-card:hover {{
      transform: translateY(-5px);
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }}
    .emoji-img {{
      font-size: 3rem;
      text-align: center;
      margin-bottom: 1rem;
      background: #f3f4f6;
      border-radius: 8px;
      padding: 1rem;
    }}
    .card h3 {{ margin: 0 0 1rem; font-size: 1.1rem; color: #111827; line-height: 1.4; }}
    .card p {{ color: #4b5563; line-height: 1.6; margin-bottom: 1rem; font-size: 0.9rem; flex-grow: 1; }}
    
    .price {{
      font-size: 1.4rem;
      font-weight: 800;
      color: #b91c1c;
      margin-bottom: 1rem;
    }}
    
    .btn-primary {{
      background: var(--primary);
      color: white;
      border: none;
      padding: 0.8rem 1rem;
      border-radius: 6px;
      font-weight: 700;
      cursor: pointer;
      text-align: center;
      width: 100%;
      font-size: 1rem;
      transition: background 0.2s;
    }}
    .btn-primary:hover {{ background: var(--primary-hover); }}
    
    .btn {{
      display: inline-block;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      text-decoration: none;
      font-size: 0.9rem;
      text-align: center;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }}
    .btn-outline {{
      border: 1px solid #d1d5db;
      color: #374151;
      background: #fff;
    }}
    .btn-outline:hover {{ 
      background: #f3f4f6; 
      border-color: #9ca3af;
    }}
    
    .logout-btn {{
      background: transparent;
      border: 1px solid #4b5563;
      padding: 0.4rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      color: #d1d5db;
      font-size: 0.85rem;
      transition: all 0.2s;
    }}
    .logout-btn:hover {{ background: #374151; color: #fff; }}
    .user-menu {{ display: flex; align-items: center; gap: 1.5rem; }}
    .user-name {{ font-weight: 600; font-size: 0.95rem; color: #f9fafb; }}
    footer {{ 
      text-align: center; 
      padding: 2rem; 
      color: #9ca3af; 
      font-size: 0.875rem; 
      background: #111827; 
      border-top: 1px solid #374151; 
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a href="/dashboard" class="logo">Muscle<span>Mart</span></a>
      <div class="user-menu">
        <span class="user-name">{escaped_display_name} 様</span>
        <form method="post" action="/logout" style="margin:0;">
          <button type="submit" class="logout-btn">ログアウト</button>
        </form>
      </div>
    </div>
  </header>
  <main class="container">
    {main_content}
  </main>
  <footer>
    &copy; 2026 MuscleMart Inc. All rights reserved.
  </footer>
</body>
</html>"""

def admin_db_page(users_data, display_name=""):
    """データベースの内容をテーブル表示する専用ページ"""
    escaped_display_name = html.escape(display_name)
    
    rows_html = ""
    for row in users_data:
        rows_html += f"""
        <tr>
          <td>{html.escape(str(row[0]))}</td>
          <td>{html.escape(row[1])}</td>
          <td><span class="password-mask">{html.escape(row[2])}</span></td>
          <td>{html.escape(row[3])}</td>
          <td>{html.escape(row[4])}</td>
          <td><span class="password-mask">{html.escape(row[5])}</span></td>
        </tr>
        """

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DBプレビュー - MuscleMart 管理者</title>
  <style>
    :root {{
      --primary: #ea580c;
      --admin-color: #dc2626;
      --bg: #f9fafb;
      --text: #1f2937;
      --border: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    header {{
      background: #111827;
      padding: 1rem 0;
    }}
    .container {{
      max-width: 1000px;
      margin: 0 auto;
      padding: 0 1rem;
    }}
    .header-inner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo {{
      font-size: 1.5rem;
      font-weight: 900;
      color: #ffffff;
      text-decoration: none;
      letter-spacing: 1px;
      text-transform: uppercase;
      font-style: italic;
    }}
    .logo span {{ color: var(--primary); }}
    main {{ padding: 2.5rem 1rem; min-height: calc(100vh - 160px); }}
    
    .admin-banner {{
      background: #fef2f2;
      border-left: 4px solid var(--admin-color);
      color: #991b1b;
      padding: 1rem 1.2rem;
      margin-bottom: 2rem;
      border-radius: 4px;
      font-size: 0.95rem;
      font-weight: bold;
    }}
    
    .back-link {{
      display: inline-block;
      margin-bottom: 1rem;
      color: #4b5563;
      text-decoration: none;
      font-weight: 600;
    }}
    .back-link:hover {{ text-decoration: underline; color: #111827; }}
    
    .db-table-wrapper {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    th, td {{
      padding: 1rem;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      background: #f3f4f6;
      font-weight: 700;
      color: #374151;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f9fafb; }}
    
    .password-mask {{
      font-family: monospace;
      background: #fef2f2;
      color: #b91c1c;
      padding: 3px 6px;
      border-radius: 4px;
      font-size: 0.9rem;
    }}
    
    .logout-btn {{
      background: transparent;
      border: 1px solid #4b5563;
      padding: 0.4rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      color: #d1d5db;
      font-size: 0.85rem;
      transition: all 0.2s;
    }}
    .logout-btn:hover {{ background: #374151; color: #fff; }}
    .user-menu {{ display: flex; align-items: center; gap: 1.5rem; }}
    .user-name {{ font-weight: 600; font-size: 0.95rem; color: #f9fafb; }}
    footer {{ 
      text-align: center; 
      padding: 2rem; 
      color: #9ca3af; 
      font-size: 0.875rem; 
      background: #111827; 
      border-top: 1px solid #374151; 
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a href="/dashboard" class="logo">Muscle<span>Mart</span></a>
      <div class="user-menu">
        <span class="user-name">{escaped_display_name} 様</span>
        <form method="post" action="/logout" style="margin:0;">
          <button type="submit" class="logout-btn">ログアウト</button>
        </form>
      </div>
    </div>
  </header>
  <main class="container">
    <a href="/dashboard" class="back-link">← ダッシュボードへ戻る</a>
    <div class="admin-banner">
      [社外秘] usersテーブルの生データを表示しています。取り扱いには十分注意してください。
    </div>
    <h2>登録ユーザー情報一覧</h2>
    <div class="db-table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Password</th>
            <th>Display Name</th>
            <th>Address</th>
            <th>Credit Card</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
  </main>
  <footer>
    &copy; 2026 MuscleMart Inc. All rights reserved.
  </footer>
</body>
</html>"""


def get_logged_in_user(headers):
    cookie_header = headers.get("Cookie", "")
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    user_id = cookie.get("demo_user_id")
    if not user_id:
        return None

    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT username, display_name FROM users WHERE id = ?",
            (user_id.value,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return {"username": row[0], "display_name": row[1]}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.respond(page())
            return

        if self.path == "/dashboard":
            user = get_logged_in_user(self.headers)
            if not user:
                self.redirect("/")
                return
            self.respond(dashboard_page(user["display_name"], user["username"]))
            return

        # 新しく追加されたDBアクセス用エンドポイント
        if self.path == "/admin/db":
            user = get_logged_in_user(self.headers)
            # 管理者(admin)以外はアクセス拒否
            if not user or user["username"] != "admin":
                self.send_error(403, "Forbidden: 管理者権限が必要です。")
                return
            
            # DBから全ユーザー情報を取得
            conn = sqlite3.connect(DB_PATH)
            try:
                cursor = conn.execute("SELECT id, username, password, display_name, address, credit_card FROM users")
                users_data = cursor.fetchall()
            finally:
                conn.close()
            
            self.respond(admin_db_page(users_data, user["display_name"]))
            return

        if self.path != "/":
            self.send_error(404)
            return

    def do_POST(self):
        if self.path == "/logout":
            self.redirect("/", clear_cookie=True)
            return

        if self.path != "/login":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(raw_body)
        username = form.get("username", [""])[0]
        password = form.get("password", [""])[0]

        # 意図的な脆弱性：直接文字列を埋め込んでいるためSQLインジェクションが可能
        query = (
            "SELECT id, username, display_name FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )

        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute(query).fetchone()
        except sqlite3.Error:
            # エラーの詳細（SQL文など）は出力せず、一般的なエラーメッセージを返す
            self.respond(page(message="システムエラーが発生しました。時間を置いて再度お試しください。", username=username, status="error"))
            return
        finally:
            conn.close()

        if row:
            self.redirect(
                "/dashboard",
                cookies={
                    "demo_user_id": str(row[0]),
                },
            )
            return

        if not row:
            self.respond(page(message="ログインに失敗しました。ユーザー名またはパスワードが違います。", username=username, status="error"))

    def redirect(self, location, cookies=None, clear_cookie=False):
        self.send_response(303)
        self.send_header("Location", location)
        if clear_cookie:
            self.send_header(
                "Set-Cookie",
                "demo_user_id=; Path=/; Max-Age=0; SameSite=Lax",
            )
        for name, value in (cookies or {}).items():
            cookie = SimpleCookie()
            cookie[name] = value
            cookie[name]["path"] = "/"
            cookie[name]["samesite"] = "Lax"
            self.send_header("Set-Cookie", cookie.output(header="").strip())
        self.end_headers()

    def respond(self, body):
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Stop with Ctrl+C")
    server.serve_forever()