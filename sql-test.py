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
                display_name TEXT NOT NULL
            )
            """
        )
        conn.execute("DELETE FROM users")
        conn.executemany(
            "INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)",
            [
                ("admin", "admin123", "システム管理者"),
                ("yamada", "taro123", "山田 太郎"),
                ("sato", "hanako123", "佐藤 花子"),
                ("zawa", "zawa123", "黒澤 亮太"),
                ("haruto", "haru123", "岡村 悠杜"),
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
  <title>ログイン - ShopEasy</title>
  <style>
    :root {{
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --bg: #f9fafb;
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
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 1.2rem 0;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
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
      font-weight: 800;
      color: var(--primary);
      text-decoration: none;
      letter-spacing: -0.5px;
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
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      width: 100%;
      max-width: 420px;
    }}
    h1 {{
      margin: 0 0 1.5rem;
      font-size: 1.4rem;
      text-align: center;
      color: #111827;
    }}
    .form-group {{
      margin-bottom: 1.2rem;
    }}
    label {{
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      font-weight: 600;
      color: #374151;
    }}
    input[type="text"], input[type="password"] {{
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s;
    }}
    input:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }}
    button {{
      width: 100%;
      padding: 0.85rem;
      margin-top: 0.5rem;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.2s;
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
      color: #6b7280;
      font-size: 0.875rem;
      background: #ffffff;
      border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a href="/" class="logo">ShopEasy</a>
    </div>
  </header>
  <main>
    <div class="login-box">
      <h1>アカウントにログイン</h1>
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
    &copy; 2026 ShopEasy Inc. All rights reserved.
  </footer>
</body>
</html>"""

def dashboard_page(display_name="", username=""):
    escaped_display_name = html.escape(display_name)
    escaped_username = html.escape(username)
    
    # ユーザー名がadminなら管理者画面、それ以外なら一般のマイページを表示
    is_admin = (username == "admin")
    
    if is_admin:
        title = "管理者ダッシュボード - ShopEasy"
        main_content = f"""
        <div class="admin-banner">
          <strong>【警告】</strong> 現在システム管理者権限でログインしています。顧客情報等の取り扱いには十分注意してください。
        </div>
        <h2>管理者コントロールパネル</h2>
        <div class="grid">
          <div class="card admin-card">
            <h3>📊 本日の売上レポート</h3>
            <p>売上高: ¥1,240,500<br>新規注文数: 154件</p>
            <a href="#" class="btn btn-outline">詳細レポートを開く</a>
          </div>
          <div class="card admin-card">
            <h3>👥 顧客データベース</h3>
            <p>全ユーザーの個人情報、配送先、クレジットカード情報へのアクセスと管理を行います。</p>
            <a href="#" class="btn btn-outline" style="color: #b91c1c; border-color: #b91c1c;">DBへアクセス</a>
          </div>
          <div class="card admin-card">
            <h3>⚙️ システム設定</h3>
            <p>サイトのメンテナンスモード切替、決済ゲートウェイの設定などを変更します。</p>
            <a href="#" class="btn btn-outline">設定を開く</a>
          </div>
        </div>
        """
    else:
        title = "マイページ - ShopEasy"
        main_content = f"""
        <h2>{escaped_display_name} 様のマイページ</h2>
        <div class="grid">
          <div class="card">
            <h3>📦 最新の注文</h3>
            <p>注文日: 先週<br>注文番号: #98234</p>
            <p>ステータス: <span style="color: #059669; font-weight: 600;">発送済み</span></p>
            <a href="#" class="btn btn-outline">配送状況を確認</a>
          </div>
          <div class="card">
            <h3>❤️ お気に入り商品</h3>
            <p>登録商品数: 5件</p>
            <br>
            <a href="#" class="btn btn-outline">リストを見る</a>
          </div>
          <div class="card">
            <h3>🎫 クーポン・ポイント</h3>
            <p>利用可能ポイント: 1,200 pt</p>
            <p>保有クーポン: 1枚</p>
            <a href="#" class="btn btn-outline">詳細を見る</a>
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
      --primary: #2563eb;
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
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 1.2rem 0;
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
      font-weight: 800;
      color: var(--primary);
      text-decoration: none;
      letter-spacing: -0.5px;
    }}
    main {{ padding: 2.5rem 1rem; min-height: calc(100vh - 160px); }}
    h2 {{ 
      margin-top: 0; 
      font-size: 1.5rem; 
      border-bottom: 2px solid var(--border); 
      padding-bottom: 0.8rem; 
      margin-bottom: 1.5rem; 
    }}
    .admin-banner {{
      background: #fef2f2;
      border-left: 4px solid var(--admin-color);
      color: #991b1b;
      padding: 1rem 1.2rem;
      margin-bottom: 2rem;
      border-radius: 4px;
      font-size: 0.95rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }}
    .card {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .admin-card {{ 
      border-top: 4px solid var(--admin-color); 
    }}
    .card h3 {{ margin: 0 0 1rem; font-size: 1.1rem; color: #111827; }}
    .card p {{ color: #4b5563; line-height: 1.6; margin-bottom: 1.5rem; font-size: 0.95rem; }}
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
      border: 1px solid #d1d5db;
      padding: 0.4rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      color: #374151;
      font-size: 0.85rem;
      transition: background 0.2s;
    }}
    .logout-btn:hover {{ background: #f3f4f6; }}
    .user-menu {{ display: flex; align-items: center; gap: 1.5rem; }}
    .user-name {{ font-weight: 600; font-size: 0.95rem; color: #374151; }}
    footer {{ 
      text-align: center; 
      padding: 2rem; 
      color: #6b7280; 
      font-size: 0.875rem; 
      background: #fff; 
      border-top: 1px solid var(--border); 
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a href="/dashboard" class="logo">ShopEasy</a>
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
    &copy; 2026 ShopEasy Inc. All rights reserved.
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