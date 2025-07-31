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
@app.route('/google458ff35c9a528e27.html')
def google_verification():
    return 'google-site-verification: google458ff35c9a528e27.html'

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
