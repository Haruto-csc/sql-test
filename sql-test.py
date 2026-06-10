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
                ("admin", "admin123", "管理者"),
                ("alice", "wonderland", "Alice"),
                ("bob", "builder", "Bob"),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def page(message="", query="", username="", status=""):
    escaped_message = html.escape(message)
    escaped_query = html.escape(query)
    escaped_username = html.escape(username)
    status_class = html.escape(status or "neutral")

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SQL Injection Demo Login</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --panel: #ffffff;
      --ink: #18202a;
      --muted: #667085;
      --line: #d7dde4;
      --accent: #2364aa;
      --danger: #b42318;
      --ok: #027a48;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(920px, calc(100vw - 32px));
      display: grid;
      grid-template-columns: minmax(280px, 380px) 1fr;
      gap: 24px;
      align-items: start;
    }}
    section, aside {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 16px 40px rgba(24, 32, 42, 0.08);
    }}
    section {{ padding: 28px; }}
    aside {{ padding: 22px; }}
    h1 {{
      margin: 0 0 8px;
      font-size: 26px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    p {{ margin: 0 0 18px; color: var(--muted); line-height: 1.6; }}
    label {{
      display: block;
      margin: 18px 0 8px;
      font-weight: 650;
      font-size: 14px;
    }}
    input {{
      width: 100%;
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 16px;
    }}
    button {{
      width: 100%;
      min-height: 44px;
      margin-top: 22px;
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: #fff;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
    }}
    .notice {{
      border-left: 4px solid var(--danger);
      background: #fff1f0;
      color: #7a271a;
      padding: 12px 14px;
      border-radius: 6px;
      margin-bottom: 20px;
      line-height: 1.55;
    }}
    .result {{
      margin-top: 18px;
      padding: 12px 14px;
      border-radius: 6px;
      border: 1px solid var(--line);
      line-height: 1.5;
    }}
    .success {{ color: var(--ok); background: #ecfdf3; border-color: #abefc6; }}
    .error {{ color: var(--danger); background: #fef3f2; border-color: #fecdca; }}
    .neutral {{ color: var(--muted); background: #f8fafc; }}
    code, pre {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #111827;
      color: #e5e7eb;
      padding: 14px;
      border-radius: 6px;
      margin: 12px 0 0;
      min-height: 64px;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
      color: var(--muted);
      line-height: 1.7;
    }}
    @media (max-width: 760px) {{
      body {{ place-items: start center; padding: 20px 0; }}
      main {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <section>
      <div class="notice">
        この画面はSQLインジェクション学習用です。ログイン処理に意図的な脆弱性があります。
      </div>
      <h1>脆弱なログイン画面</h1>
      <p>通常ログイン: <code>admin</code> / <code>admin123</code></p>
      <form method="post" action="/login">
        <label for="username">ユーザー名</label>
        <input id="username" name="username" autocomplete="username" value="{escaped_username}">
        <label for="password">パスワード</label>
        <input id="password" name="password" type="password" autocomplete="current-password">
        <button type="submit">ログイン</button>
      </form>
      <div class="result {status_class}">{escaped_message}</div>
    </section>
    <aside>
      <h2>内部で実行されたSQL</h2>
      <p>入力値を直接SQL文字列に埋め込んでいるため、認証条件を書き換えられます。</p>
      <pre>{escaped_query or "まだログイン試行はありません。"}</pre>
      <h2 style="margin-top: 24px;">教材メモ</h2>
      <ul>
        <li>この実装は実運用禁止です。</li>
        <li>本来はプレースホルダ付きクエリを使います。</li>
        <li>このサーバーはローカルホスト専用で起動します。</li>
      </ul>
    </aside>
  </main>
</body>
</html>"""


def dashboard_page(display_name="", username=""):
    escaped_display_name = html.escape(display_name)
    escaped_username = html.escape(username)

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Login Complete</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --panel: #ffffff;
      --ink: #18202a;
      --muted: #667085;
      --line: #d7dde4;
      --accent: #2364aa;
      --ok: #027a48;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(720px, calc(100vw - 32px));
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 16px 40px rgba(24, 32, 42, 0.08);
      padding: 32px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    p {{
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.65;
    }}
    .badge {{
      display: inline-block;
      margin-bottom: 18px;
      padding: 8px 10px;
      border-radius: 6px;
      background: #ecfdf3;
      color: var(--ok);
      font-weight: 700;
    }}
    dl {{
      display: grid;
      grid-template-columns: 120px 1fr;
      gap: 10px 16px;
      margin: 24px 0;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fafc;
    }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; font-weight: 700; }}
    a, button {{
      min-height: 42px;
      border-radius: 6px;
      font-size: 15px;
      font-weight: 700;
    }}
    a {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      color: #fff;
      background: var(--accent);
      text-decoration: none;
    }}
    form {{ display: inline; margin-left: 8px; }}
    button {{
      border: 1px solid var(--line);
      padding: 0 16px;
      background: #fff;
      color: var(--ink);
      cursor: pointer;
    }}
    @media (max-width: 560px) {{
      body {{ place-items: start center; padding: 20px 0; }}
      main {{ padding: 24px; }}
      dl {{ grid-template-columns: 1fr; }}
      form {{ display: block; margin: 10px 0 0; }}
      a, button {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <main>
    <div class="badge">ログイン済み</div>
    <h1>ログイン後の画面</h1>
    <p>認証に成功したため、ログインページからこの画面へ遷移しました。</p>
    <dl>
      <dt>表示名</dt>
      <dd>{escaped_display_name}</dd>
      <dt>ユーザー名</dt>
      <dd>{escaped_username}</dd>
    </dl>
    <a href="/">ログイン画面へ戻る</a>
    <form method="post" action="/logout">
      <button type="submit">ログアウト</button>
    </form>
  </main>
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
            self.respond(page(message="ログイン情報を入力してください。", status="neutral"))
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

        # Intentionally vulnerable: direct string interpolation allows SQL injection.
        query = (
            "SELECT id, username, display_name FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )

        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute(query).fetchone()
        except sqlite3.Error as exc:
            message = f"SQLエラー: {exc}"
            self.respond(page(message=message, query=query, username=username, status="error"))
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
            message = "ログイン失敗: ユーザー名またはパスワードが違います。"
            status = "error"

        self.respond(page(message=message, query=query, username=username, status=status))

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
    print(f"SQL injection demo running at http://{HOST}:{PORT}")
    print("Stop with Ctrl+C")
    server.serve_forever()
