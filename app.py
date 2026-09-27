from flask import Flask, render_template, request, Response, jsonify, send_from_directory
import smtplib
from email.mime.text import MIMEText
import os
import re
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'icons'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/google<token>.html')
def google_verify(token):
    """Google Search Console の所有権確認ファイル(リポジトリ直下に置いた googleXXXX.html)を返す。"""
    if not re.fullmatch(r'[0-9A-Za-z]+', token):
        return Response('Not found', status=404)
    return send_from_directory(app.root_path, f'google{token}.html', mimetype='text/html')

@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /\nSitemap: https://ato-sns.com/sitemap.xml"
    return Response(content, status=200, mimetype='text/plain; charset=utf-8')
@app.route('/en')
def index_en():
    return render_template('index.html', lang='en')
@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://ato-sns.com/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://ato-sns.com/en</loc>
    <priority>0.8</priority>
  </url>
  <!-- 必要に応じて他ページも追加 -->
</urlset>'''
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/send', methods=['POST'])
def send():
    name = request.form['name']
    company = request.form.get('company', '')
    email = request.form['email']
    phone = request.form.get('phone', '')
    inquiry = request.form['inquiry']
    source = request.form.get('source', '')

    body = f"""【お問い合わせ内容】

名前: {name}
会社名・団体名: {company}
メールアドレス: {email}
電話番号: {phone}
どこで知ったか: {source}

▼お問い合わせ内容:
{inquiry}
"""

    msg = MIMEText(body)
    msg['Subject'] = "【サイトからのお問い合わせ】"
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return "送信が完了しました。ありがとうございました！"
    except Exception as e:
        return f"送信に失敗しました：{e}"


@app.route('/apply', methods=['POST'])
def apply():
    """LPの「Webで申し込む」フォーム。内容をGmail(EMAIL_USER)に送る。"""
    data = request.get_json(silent=True) or request.form
    if data.get('botcheck'):
        return jsonify(ok=True)
    name = (data.get('name') or '').strip()[:200]
    email = (data.get('email') or '').strip()[:200]
    kind = (data.get('type') or '').strip()[:100]
    if not name or not email or '@' not in email or not kind:
        return jsonify(ok=False, error='missing'), 400
    account = (data.get('account') or '').strip()[:300]
    message = (data.get('message') or '').strip()[:5000]
    lang = (data.get('lang') or 'ja').strip()[:5]

    body = f"""【ATO LP 無料診断の申し込み】

お名前: {name}
メールアドレス: {email}
SNSアカウント: {account or '(未記入)'}
どれに近いか: {kind}
表示言語: {lang}

▼ご相談内容:
{message or '(未記入)'}
"""
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = f"【ATO LP】無料診断の申し込み：{name}"
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Reply-To'] = email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return jsonify(ok=True)
    except Exception:
        app.logger.exception('apply mail failed')
        return jsonify(ok=False, error='mail'), 500
