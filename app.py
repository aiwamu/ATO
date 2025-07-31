from flask import Flask, render_template, request
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Allow: /
Sitemap: https://ato-ayg2.onrender.com/sitemap.xml
""", mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://ato-ayg2.onrender.com/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://ato-ayg2.onrender.com/about</loc>
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

