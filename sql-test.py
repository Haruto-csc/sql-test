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
          <input type="text" id="password" name="password" required autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
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
            <a href="/admin/sales" class="btn btn-outline">詳細レポートを開く</a>
          </div>
          <div class="card admin-card">
            <h3>👥 メンバーデータベース</h3>
            <p>全トレーニーの個人情報、配送先、クレジットカード情報へのアクセスと管理を行います。</p>
            <a href="/admin/db" class="btn btn-outline" style="color: #b91c1c; border-color: #b91c1c;">DBへアクセス</a>
          </div>
          <div class="card admin-card">
            <h3>📦 在庫管理アラート</h3>
            <p style="color: #ea580c; font-weight: bold;">⚠️ アジャスタブルダンベル 32kg の在庫が残り3セットです。</p>
            <a href="/admin/inventory" class="btn btn-outline">在庫アラートを開く</a>
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
            <a href="/cart?item=%E3%83%9B%E3%82%A8%E3%82%A4%E3%83%97%E3%83%AD%E3%83%86%E3%82%A4%E3%83%B3+WPI+1kg+%28%E3%83%80%E3%83%96%E3%83%AB%E3%83%AA%E3%83%83%E3%83%81%E3%83%81%E3%83%A7%E3%82%B3%E3%83%AC%E3%83%BC%E3%83%88%E5%91%B3%29&price=%C2%A54%2C980" class="btn-primary" style="display:block;text-decoration:none;text-align:center;">カートに入れる</a>
          </div>

          <!-- ダンベル -->
          <div class="card product-card">
            <div class="emoji-img">🏋️‍♂️</div>
            <h3>アジャスタブルダンベル 32kg × 2個セット</h3>
            <p>ダイヤルを回すだけで2kg〜32kgまで簡単に重量変更が可能。ホームジムの必須アイテム。</p>
            <div class="price">¥34,800</div>
            <a href="/cart?item=%E3%82%A2%E3%82%B8%E3%83%A3%E3%82%B9%E3%82%BF%E3%83%96%E3%83%AB%E3%83%80%E3%83%B3%E3%83%99%E3%83%AB+32kg+%C3%97+2%E5%80%8B%E3%82%BB%E3%83%83%E3%83%88&price=%C2%A534%2C800" class="btn-primary" style="display:block;text-decoration:none;text-align:center;">カートに入れる</a>
          </div>

          <!-- マシン/ラック -->
          <div class="card product-card">
            <div class="emoji-img">🏗️</div>
            <h3>ハーフラック スタンダードモデル (耐荷重300kg)</h3>
            <p>スクワット、ベンチプレスなどビッグ3に完全対応。極太フレームで安定感抜群のラックです。</p>
            <div class="price">¥89,000</div>
            <a href="/cart?item=%E3%83%8F%E3%83%BC%E3%83%95%E3%83%A9%E3%83%83%E3%82%AF+%E3%82%B9%E3%82%BF%E3%83%B3%E3%83%80%E3%83%BC%E3%83%89%E3%83%A2%E3%83%87%E3%83%AB+%28%E8%80%90%E8%8D%B7%E9%87%8D300kg%29&price=%C2%A589%2C000" class="btn-primary" style="display:block;text-decoration:none;text-align:center;">大型配送・カートに入れる</a>
          </div>

          <!-- アクセサリー -->
          <div class="card product-card">
            <div class="emoji-img">🧤</div>
            <h3>本革パワーグリップ PRO</h3>
            <p>デッドリフトや懸垂時の握力サポートに。背中トレの質を劇的に向上させるマストアイテム。</p>
            <div class="price">¥6,500</div>
            <a href="/cart?item=%E6%9C%AC%E9%9D%B4%E3%83%91%E3%83%AF%E3%83%BC%E3%82%B0%E3%83%AA%E3%83%83%E3%83%97+PRO&price=%C2%A56%2C500" class="btn-primary" style="display:block;text-decoration:none;text-align:center;">カートに入れる</a>
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


def cart_page(item_name="", price="", display_name=""):
    escaped_display_name = html.escape(display_name)
    escaped_item = html.escape(item_name)
    escaped_price = html.escape(price)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>購入手続き - MuscleMart</title>
  <style>
    :root {{--primary:#ea580c;--primary-hover:#c2410c;--bg:#f9fafb;--text:#1f2937;--border:#e5e7eb;}}
    *{{box-sizing:border-box;}}
    body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;}}
    header{{background:#111827;padding:1rem 0;}}
    .container{{max-width:700px;margin:0 auto;padding:0 1rem;}}
    .header-inner{{display:flex;justify-content:space-between;align-items:center;}}
    .logo{{font-size:1.5rem;font-weight:900;color:#fff;text-decoration:none;letter-spacing:1px;text-transform:uppercase;font-style:italic;}}
    .logo span{{color:var(--primary);}}
    main{{padding:3rem 1rem;min-height:calc(100vh - 160px);}}
    .card{{background:#fff;border:1px solid var(--border);border-radius:8px;padding:2rem;box-shadow:0 2px 4px rgba(0,0,0,0.05);margin-bottom:1.5rem;}}
    h2{{margin:0 0 1.5rem;font-size:1.4rem;color:#111827;border-bottom:2px solid var(--border);padding-bottom:0.8rem;}}
    .item-row{{display:flex;justify-content:space-between;align-items:center;padding:1rem 0;border-bottom:1px solid var(--border);}}
    .item-name{{font-weight:700;font-size:1.05rem;}}
    .item-price{{font-size:1.3rem;font-weight:800;color:#b91c1c;}}
    .form-group{{margin-bottom:1.2rem;}}
    label{{display:block;margin-bottom:0.4rem;font-size:0.9rem;font-weight:700;color:#374151;}}
    input[type="text"]{{width:100%;padding:0.7rem;border:2px solid #e5e7eb;border-radius:6px;font-size:1rem;}}
    input:focus{{outline:none;border-color:var(--primary);}}
    .total-row{{display:flex;justify-content:space-between;padding:1rem 0;font-size:1.1rem;font-weight:800;}}
    .btn-submit{{width:100%;padding:1rem;background:var(--primary);color:#fff;border:none;border-radius:6px;font-size:1.1rem;font-weight:800;cursor:pointer;text-transform:uppercase;letter-spacing:1px;}}
    .btn-submit:hover{{background:var(--primary-hover);}}
    .back-link{{display:inline-block;margin-bottom:1.5rem;color:#4b5563;text-decoration:none;font-weight:600;}}
    .back-link:hover{{text-decoration:underline;}}
    .user-menu{{display:flex;align-items:center;gap:1.5rem;}}
    .user-name{{font-weight:600;font-size:0.95rem;color:#f9fafb;}}
    .logout-btn{{background:transparent;border:1px solid #4b5563;padding:0.4rem 1rem;border-radius:6px;cursor:pointer;font-weight:600;color:#d1d5db;font-size:0.85rem;}}
    .logout-btn:hover{{background:#374151;color:#fff;}}
    footer{{text-align:center;padding:2rem;color:#9ca3af;font-size:0.875rem;background:#111827;border-top:1px solid #374151;}}
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
    <a href="/dashboard" class="back-link">← ショッピングに戻る</a>
    <h2>🛒 購入手続き</h2>
    <div class="card">
      <h2>注文内容の確認</h2>
      <div class="item-row">
        <span class="item-name">{escaped_item}</span>
        <span class="item-price">{escaped_price}</span>
      </div>
      <div class="total-row">
        <span>合計（税込）</span>
        <span style="color:#b91c1c;">{escaped_price}</span>
      </div>
    </div>
    <div class="card">
      <h2>お届け先・お支払い情報</h2>
      <form method="post" action="/order">
        <input type="hidden" name="item_name" value="{escaped_item}">
        <input type="hidden" name="price" value="{escaped_price}">
        <div class="form-group">
          <label>お名前</label>
          <input type="text" name="order_name" placeholder="山田 太郎" required>
        </div>
        <div class="form-group">
          <label>お届け先住所</label>
          <input type="text" name="address" placeholder="東京都渋谷区〇〇1-2-3" required>
        </div>
        <div class="form-group">
          <label>クレジットカード番号</label>
          <input type="text" name="card_number" placeholder="1234-5678-9012-3456" required>
        </div>
        <button type="submit" class="btn-submit">注文を確定する</button>
      </form>
    </div>
  </main>
  <footer>&copy; 2026 MuscleMart Inc. All rights reserved.</footer>
</body>
</html>"""


def order_complete_page(item_name="", display_name=""):
    escaped_display_name = html.escape(display_name)
    escaped_item = html.escape(item_name)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>注文完了 - MuscleMart</title>
  <style>
    :root{{--primary:#ea580c;--bg:#f9fafb;--text:#1f2937;--border:#e5e7eb;}}
    *{{box-sizing:border-box;}}
    body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}}
    header{{background:#111827;padding:1rem 0;}}
    .container{{max-width:700px;margin:0 auto;padding:0 1rem;}}
    .header-inner{{display:flex;justify-content:space-between;align-items:center;}}
    .logo{{font-size:1.5rem;font-weight:900;color:#fff;text-decoration:none;letter-spacing:1px;text-transform:uppercase;font-style:italic;}}
    .logo span{{color:var(--primary);}}
    main{{padding:4rem 1rem;min-height:calc(100vh - 160px);display:flex;justify-content:center;}}
    .complete-box{{background:#fff;border:1px solid var(--border);border-radius:8px;padding:3rem 2rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08);max-width:500px;width:100%;border-top:5px solid #16a34a;}}
    .icon{{font-size:4rem;margin-bottom:1rem;}}
    h2{{font-size:1.6rem;color:#111827;margin:0 0 1rem;}}
    p{{color:#4b5563;line-height:1.7;margin-bottom:1.5rem;}}
    .order-item{{background:#f3f4f6;border-radius:6px;padding:1rem;margin-bottom:1.5rem;font-weight:700;color:#111827;}}
    .btn-back{{display:inline-block;background:var(--primary);color:#fff;padding:0.85rem 2rem;border-radius:6px;text-decoration:none;font-weight:800;font-size:1rem;}}
    .user-menu{{display:flex;align-items:center;gap:1.5rem;}}
    .user-name{{font-weight:600;font-size:0.95rem;color:#f9fafb;}}
    .logout-btn{{background:transparent;border:1px solid #4b5563;padding:0.4rem 1rem;border-radius:6px;cursor:pointer;font-weight:600;color:#d1d5db;font-size:0.85rem;}}
    .logout-btn:hover{{background:#374151;color:#fff;}}
    footer{{text-align:center;padding:2rem;color:#9ca3af;font-size:0.875rem;background:#111827;border-top:1px solid #374151;}}
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
    <div class="complete-box">
      <div class="icon">✅</div>
      <h2>ご注文が完了しました！</h2>
      <div class="order-item">📦 {escaped_item}</div>
      <p>ご注文ありがとうございます、{escaped_display_name} 様。<br>
      ご登録のメールアドレス宛に注文確認メールをお送りしました。<br>
      商品は3〜5営業日以内にお届けします。</p>
      <a href="/dashboard" class="btn-back">ショッピングを続ける</a>
    </div>
  </main>
  <footer>&copy; 2026 MuscleMart Inc. All rights reserved.</footer>
</body>
</html>"""


def admin_sales_page(display_name=""):
    escaped_display_name = html.escape(display_name)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>売上レポート - MuscleMart 管理者</title>
  <style>
    :root{{--primary:#ea580c;--admin-color:#dc2626;--bg:#f9fafb;--text:#1f2937;--border:#e5e7eb;}}
    *{{box-sizing:border-box;}}
    body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}}
    header{{background:#111827;padding:1rem 0;}}
    .container{{max-width:1000px;margin:0 auto;padding:0 1rem;}}
    .header-inner{{display:flex;justify-content:space-between;align-items:center;}}
    .logo{{font-size:1.5rem;font-weight:900;color:#fff;text-decoration:none;letter-spacing:1px;text-transform:uppercase;font-style:italic;}}
    .logo span{{color:var(--primary);}}
    main{{padding:2.5rem 1rem;min-height:calc(100vh - 160px);}}
    .admin-banner{{background:#fef2f2;border-left:4px solid var(--admin-color);color:#991b1b;padding:1rem 1.2rem;margin-bottom:2rem;border-radius:4px;font-size:0.95rem;font-weight:bold;}}
    .back-link{{display:inline-block;margin-bottom:1rem;color:#4b5563;text-decoration:none;font-weight:600;}}
    .back-link:hover{{text-decoration:underline;}}
    .stats-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1.2rem;margin-bottom:2rem;}}
    .stat-card{{background:#fff;border:1px solid var(--border);border-radius:8px;padding:1.2rem 1.5rem;box-shadow:0 2px 4px rgba(0,0,0,0.05);}}
    .stat-label{{font-size:0.85rem;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;}}
    .stat-value{{font-size:1.6rem;font-weight:800;color:#111827;}}
    .stat-sub{{font-size:0.8rem;color:#16a34a;font-weight:600;margin-top:0.3rem;}}
    .section-title{{font-size:1.2rem;font-weight:800;color:#111827;margin:2rem 0 1rem;}}
    .db-table-wrapper{{background:#fff;border:1px solid var(--border);border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.05);margin-bottom:2rem;}}
    table{{width:100%;border-collapse:collapse;text-align:left;}}
    th,td{{padding:0.9rem 1rem;border-bottom:1px solid var(--border);}}
    th{{background:#f3f4f6;font-weight:700;color:#374151;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;}}
    tr:last-child td{{border-bottom:none;}}
    tr:hover td{{background:#f9fafb;}}
    .badge{{display:inline-block;padding:3px 8px;border-radius:4px;font-size:0.8rem;font-weight:700;}}
    .badge-green{{background:#dcfce7;color:#15803d;}}
    .badge-orange{{background:#fff7ed;color:#c2410c;}}
    .bar-wrap{{background:#e5e7eb;border-radius:4px;height:8px;width:120px;display:inline-block;vertical-align:middle;}}
    .bar{{background:var(--primary);border-radius:4px;height:8px;}}
    .logout-btn{{background:transparent;border:1px solid #4b5563;padding:0.4rem 1rem;border-radius:6px;cursor:pointer;font-weight:600;color:#d1d5db;font-size:0.85rem;}}
    .logout-btn:hover{{background:#374151;color:#fff;}}
    .user-menu{{display:flex;align-items:center;gap:1.5rem;}}
    .user-name{{font-weight:600;font-size:0.95rem;color:#f9fafb;}}
    footer{{text-align:center;padding:2rem;color:#9ca3af;font-size:0.875rem;background:#111827;border-top:1px solid #374151;}}
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
      【管理者専用】売上レポート — 本日 2026/06/26 のデータを表示しています。
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">本日の売上高</div>
        <div class="stat-value">¥2,450,000</div>
        <div class="stat-sub">▲ 前日比 +12.4%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本日の注文数</div>
        <div class="stat-value">187 件</div>
        <div class="stat-sub">▲ 前日比 +8.1%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">月間売上高</div>
        <div class="stat-value">¥38,200,000</div>
        <div class="stat-sub">▲ 先月比 +5.2%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">新規会員数（今月）</div>
        <div class="stat-value">342 名</div>
        <div class="stat-sub">▲ 先月比 +18.9%</div>
      </div>
    </div>

    <div class="section-title">📊 カテゴリ別売上内訳</div>
    <div class="db-table-wrapper">
      <table>
        <thead>
          <tr><th>カテゴリ</th><th>売上高</th><th>注文数</th><th>構成比</th><th>売上グラフ</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>プロテイン・サプリ</td>
            <td>¥1,102,500</td>
            <td>98 件</td>
            <td><span class="badge badge-green">45.0%</span></td>
            <td><div class="bar-wrap"><div class="bar" style="width:100%;"></div></div></td>
          </tr>
          <tr>
            <td>ダンベル・バーベル</td>
            <td>¥784,000</td>
            <td>42 件</td>
            <td><span class="badge badge-green">32.0%</span></td>
            <td><div class="bar-wrap"><div class="bar" style="width:71%;"></div></div></td>
          </tr>
          <tr>
            <td>トレーニングマシン</td>
            <td>¥445,500</td>
            <td>12 件</td>
            <td><span class="badge badge-orange">18.2%</span></td>
            <td><div class="bar-wrap"><div class="bar" style="width:40%;"></div></div></td>
          </tr>
          <tr>
            <td>アクセサリー</td>
            <td>¥118,000</td>
            <td>35 件</td>
            <td><span class="badge badge-orange">4.8%</span></td>
            <td><div class="bar-wrap"><div class="bar" style="width:11%;"></div></div></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="section-title">🏆 本日の売上トップ商品</div>
    <div class="db-table-wrapper">
      <table>
        <thead>
          <tr><th>順位</th><th>商品名</th><th>単価</th><th>販売数</th><th>売上合計</th></tr>
        </thead>
        <tbody>
          <tr><td>1位</td><td>ホエイプロテイン WPI 1kg (ダブルリッチチョコレート味)</td><td>¥4,980</td><td>62 個</td><td>¥308,760</td></tr>
          <tr><td>2位</td><td>アジャスタブルダンベル 32kg × 2個セット</td><td>¥34,800</td><td>18 セット</td><td>¥626,400</td></tr>
          <tr><td>3位</td><td>本革パワーグリップ PRO</td><td>¥6,500</td><td>35 個</td><td>¥227,500</td></tr>
          <tr><td>4位</td><td>ハーフラック スタンダードモデル (耐荷重300kg)</td><td>¥89,000</td><td>8 台</td><td>¥712,000</td></tr>
          <tr><td>5位</td><td>EAAアミノ酸ドリンク 500g (レモン味)</td><td>¥3,280</td><td>55 個</td><td>¥180,400</td></tr>
        </tbody>
      </table>
    </div>
  </main>
  <footer>&copy; 2026 MuscleMart Inc. All rights reserved.</footer>
</body>
</html>"""


def admin_inventory_page(display_name=""):
    escaped_display_name = html.escape(display_name)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>在庫管理アラート - MuscleMart 管理者</title>
  <style>
    :root{{--primary:#ea580c;--admin-color:#dc2626;--bg:#f9fafb;--text:#1f2937;--border:#e5e7eb;}}
    *{{box-sizing:border-box;}}
    body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}}
    header{{background:#111827;padding:1rem 0;}}
    .container{{max-width:1000px;margin:0 auto;padding:0 1rem;}}
    .header-inner{{display:flex;justify-content:space-between;align-items:center;}}
    .logo{{font-size:1.5rem;font-weight:900;color:#fff;text-decoration:none;letter-spacing:1px;text-transform:uppercase;font-style:italic;}}
    .logo span{{color:var(--primary);}}
    main{{padding:2.5rem 1rem;min-height:calc(100vh - 160px);}}
    .admin-banner{{background:#fef2f2;border-left:4px solid var(--admin-color);color:#991b1b;padding:1rem 1.2rem;margin-bottom:2rem;border-radius:4px;font-size:0.95rem;font-weight:bold;}}
    .alert-banner{{background:#fff7ed;border-left:4px solid #ea580c;color:#9a3412;padding:1rem 1.2rem;margin-bottom:2rem;border-radius:4px;font-size:0.95rem;font-weight:bold;}}
    .back-link{{display:inline-block;margin-bottom:1rem;color:#4b5563;text-decoration:none;font-weight:600;}}
    .back-link:hover{{text-decoration:underline;}}
    .section-title{{font-size:1.2rem;font-weight:800;color:#111827;margin:2rem 0 1rem;}}
    .db-table-wrapper{{background:#fff;border:1px solid var(--border);border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.05);margin-bottom:2rem;}}
    table{{width:100%;border-collapse:collapse;text-align:left;}}
    th,td{{padding:0.9rem 1rem;border-bottom:1px solid var(--border);}}
    th{{background:#f3f4f6;font-weight:700;color:#374151;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;}}
    tr:last-child td{{border-bottom:none;}}
    tr:hover td{{background:#f9fafb;}}
    tr.row-danger{{background:#fef2f2;}}
    tr.row-warning{{background:#fff7ed;}}
    .badge{{display:inline-block;padding:3px 8px;border-radius:4px;font-size:0.8rem;font-weight:700;}}
    .badge-red{{background:#fecaca;color:#b91c1c;}}
    .badge-orange{{background:#fed7aa;color:#c2410c;}}
    .badge-green{{background:#dcfce7;color:#15803d;}}
    .stock-bar-wrap{{background:#e5e7eb;border-radius:4px;height:8px;width:100px;display:inline-block;vertical-align:middle;margin-right:8px;}}
    .stock-bar{{border-radius:4px;height:8px;}}
    .bar-red{{background:#ef4444;}}
    .bar-orange{{background:#f97316;}}
    .bar-green{{background:#22c55e;}}
    .logout-btn{{background:transparent;border:1px solid #4b5563;padding:0.4rem 1rem;border-radius:6px;cursor:pointer;font-weight:600;color:#d1d5db;font-size:0.85rem;}}
    .logout-btn:hover{{background:#374151;color:#fff;}}
    .user-menu{{display:flex;align-items:center;gap:1.5rem;}}
    .user-name{{font-weight:600;font-size:0.95rem;color:#f9fafb;}}
    footer{{text-align:center;padding:2rem;color:#9ca3af;font-size:0.875rem;background:#111827;border-top:1px solid #374151;}}
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
      【管理者専用】在庫管理アラート — 在庫数が閾値を下回った商品を強調表示しています。
    </div>
    <div class="alert-banner">
      ⚠️ 緊急アラート: 2商品が在庫切れ危険水域です。至急発注を検討してください。
    </div>

    <div class="section-title">🚨 要発注アラート商品</div>
    <div class="db-table-wrapper">
      <table>
        <thead>
          <tr><th>商品名</th><th>カテゴリ</th><th>現在庫数</th><th>発注点</th><th>状態</th></tr>
        </thead>
        <tbody>
          <tr class="row-danger">
            <td>アジャスタブルダンベル 32kg × 2個セット</td>
            <td>ダンベル・バーベル</td>
            <td><div class="stock-bar-wrap"><div class="stock-bar bar-red" style="width:9%;"></div></div>3 セット</td>
            <td>10 セット</td>
            <td><span class="badge badge-red">🔴 緊急発注</span></td>
          </tr>
          <tr class="row-danger">
            <td>ハーフラック スタンダードモデル (耐荷重300kg)</td>
            <td>トレーニングマシン</td>
            <td><div class="stock-bar-wrap"><div class="stock-bar bar-red" style="width:14%;"></div></div>1 台</td>
            <td>5 台</td>
            <td><span class="badge badge-red">🔴 緊急発注</span></td>
          </tr>
          <tr class="row-warning">
            <td>ホエイプロテイン WPI 1kg (ダブルリッチチョコレート味)</td>
            <td>プロテイン・サプリ</td>
            <td><div class="stock-bar-wrap"><div class="stock-bar bar-orange" style="width:36%;"></div></div>36 個</td>
            <td>50 個</td>
            <td><span class="badge badge-orange">🟠 発注推奨</span></td>
          </tr>
          <tr class="row-warning">
            <td>EAAアミノ酸ドリンク 500g (レモン味)</td>
            <td>プロテイン・サプリ</td>
            <td><div class="stock-bar-wrap"><div class="stock-bar bar-orange" style="width:44%;"></div></div>22 個</td>
            <td>30 個</td>
            <td><span class="badge badge-orange">🟠 発注推奨</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="section-title">📦 全商品在庫一覧</div>
    <div class="db-table-wrapper">
      <table>
        <thead>
          <tr><th>商品名</th><th>カテゴリ</th><th>在庫数</th><th>状態</th></tr>
        </thead>
        <tbody>
          <tr class="row-danger">
            <td>アジャスタブルダンベル 32kg × 2個セット</td>
            <td>ダンベル・バーベル</td>
            <td>3 セット</td>
            <td><span class="badge badge-red">🔴 緊急発注</span></td>
          </tr>
          <tr class="row-danger">
            <td>ハーフラック スタンダードモデル (耐荷重300kg)</td>
            <td>トレーニングマシン</td>
            <td>1 台</td>
            <td><span class="badge badge-red">🔴 緊急発注</span></td>
          </tr>
          <tr class="row-warning">
            <td>ホエイプロテイン WPI 1kg (ダブルリッチチョコレート味)</td>
            <td>プロテイン・サプリ</td>
            <td>36 個</td>
            <td><span class="badge badge-orange">🟠 発注推奨</span></td>
          </tr>
          <tr class="row-warning">
            <td>EAAアミノ酸ドリンク 500g (レモン味)</td>
            <td>プロテイン・サプリ</td>
            <td>22 個</td>
            <td><span class="badge badge-orange">🟠 発注推奨</span></td>
          </tr>
          <tr>
            <td>本革パワーグリップ PRO</td>
            <td>アクセサリー</td>
            <td>128 個</td>
            <td><span class="badge badge-green">🟢 在庫充足</span></td>
          </tr>
          <tr>
            <td>クレアチンモノハイドレート 500g</td>
            <td>プロテイン・サプリ</td>
            <td>94 個</td>
            <td><span class="badge badge-green">🟢 在庫充足</span></td>
          </tr>
          <tr>
            <td>ラバーコーティングダンベル 10kg ペア</td>
            <td>ダンベル・バーベル</td>
            <td>55 セット</td>
            <td><span class="badge badge-green">🟢 在庫充足</span></td>
          </tr>
          <tr>
            <td>トレーニングベルト Lサイズ</td>
            <td>アクセサリー</td>
            <td>76 個</td>
            <td><span class="badge badge-green">🟢 在庫充足</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
  <footer>&copy; 2026 MuscleMart Inc. All rights reserved.</footer>
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

        if self.path.startswith("/cart"):
            user = get_logged_in_user(self.headers)
            if not user:
                self.redirect("/")
                return
            from urllib.parse import urlparse, parse_qs as _parse_qs
            parsed = urlparse(self.path)
            params = _parse_qs(parsed.query)
            item_name = params.get("item", [""])[0]
            price = params.get("price", [""])[0]
            self.respond(cart_page(item_name, price, user["display_name"]))
            return

        if self.path == "/admin/sales":
            user = get_logged_in_user(self.headers)
            if not user or user["username"] != "admin":
                self.send_error(403, "Forbidden: 管理者権限が必要です。")
                return
            self.respond(admin_sales_page(user["display_name"]))
            return

        if self.path == "/admin/inventory":
            user = get_logged_in_user(self.headers)
            if not user or user["username"] != "admin":
                self.send_error(403, "Forbidden: 管理者権限が必要です。")
                return
            self.respond(admin_inventory_page(user["display_name"]))
            return

        if self.path != "/":
            self.send_error(404)
            return

    def do_POST(self):
        if self.path == "/logout":
            self.redirect("/", clear_cookie=True)
            return

        if self.path == "/order":
            user = get_logged_in_user(self.headers)
            if not user:
                self.redirect("/")
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8")
            form = parse_qs(raw_body)
            item_name = form.get("item_name", [""])[0]
            self.respond(order_complete_page(item_name, user["display_name"]))
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