import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = "smtp.yandex.ru"
SMTP_PORT = 587
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)


def send_reset_email(to_email: str, reset_token: str, base_url: str = "http://localhost:5173"):
    reset_link = f"{base_url}/reset-password?token={reset_token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Восстановление пароля — NutriCalc"
    msg["From"] = MAIL_FROM
    msg["To"] = to_email

    text = f"Для сброса пароля перейдите по ссылке:\n{reset_link}\n\nСсылка действительна 1 час."
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;">
      <h2 style="color:#2d6a4f;">NutriCalc</h2>
      <p>Вы запросили сброс пароля. Нажмите кнопку ниже:</p>
      <a href="{reset_link}"
         style="display:inline-block;margin:16px 0;padding:12px 24px;
                background:#2d6a4f;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;">
        Сбросить пароль
      </a>
      <p style="color:#888;font-size:13px;">Ссылка действительна 1 час. Если вы не запрашивали сброс — просто проигнорируйте это письмо.</p>
    </div>
    """

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, to_email, msg.as_string())
