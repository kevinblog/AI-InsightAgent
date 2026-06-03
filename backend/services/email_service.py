"""
============================================
AI 行业脉搏 - 邮件服务
============================================

提供验证码发送功能

使用方法：
from services.email_service import EmailService
email_service = EmailService(config)
await email_service.send_verification_code("user@example.com", "123456")
"""

import smtplib
import random
import logging
from datetime import datetime, timedelta
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""

    def __init__(self, config):
        """初始化邮件服务"""
        self.config = config
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASSWORD
        self.smtp_from = config.SMTP_FROM or config.SMTP_USER

        # 验证码配置
        self.code_length = config.VERIFICATION_CODE_LENGTH
        self.code_expire_minutes = config.VERIFICATION_CODE_EXPIRE_MINUTES

        # 发送记录（用于限流）
        self.send_history = {}

    def generate_verification_code(self) -> str:
        """生成随机验证码"""
        digits = "0123456789"
        return "".join(random.choice(digits) for _ in range(self.code_length))

    def is_rate_limited(self, email: str) -> bool:
        """检查是否限流（同一邮箱 60 秒内只能发 1 次）"""
        now = datetime.now()
        if email in self.send_history:
            last_send = self.send_history[email]
            if (now - last_send).total_seconds() < 60:
                return True
        return False

    def record_send(self, email: str):
        """记录发送时间"""
        self.send_history[email] = datetime.now()

    async def send_verification_code(self, email: str, code: str) -> bool:
        """发送验证码邮件"""
        # 检查限流
        if self.is_rate_limited(email):
            logger.warning(f"发送太频繁: {email}")
            return False

        subject = "AI 行业脉搏 - 验证码"
        content = self._render_verification_email(code)

        try:
            self._send_email(email, subject, content)
            self.record_send(email)
            logger.info(f"验证码已发送: {email}")
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False

    def _send_email(self, to_email: str, subject: str, content: str):
        """发送邮件（同步方法，可用线程池）"""
        msg = MIMEMultipart()
        msg["From"] = self.smtp_from
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")

        # 邮件正文
        text_part = MIMEText(content, "html", "utf-8")
        msg.attach(text_part)

        # 连接 SMTP 服务器
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()  # 启用 TLS
        server.login(self.smtp_user, self.smtp_password)

        # 发送邮件
        server.sendmail(self.smtp_from, [to_email], msg.as_string())
        server.quit()

    def _render_verification_email(self, code: str) -> str:
        """渲染验证码邮件"""
        expire_minutes = self.code_expire_minutes
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>验证码</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 30px;
            color: white;
        }}
        .code-box {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }}
        .code {{
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
        }}
        .footer {{
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>AI 行业脉搏 - 验证码</h2>
        <p>您的验证码是：</p>
        <div class="code-box">
            <div class="code">{code}</div>
        </div>
        <p>验证码将在 <strong>{expire_minutes} 分钟</strong> 后过期。</p>
        <p style="opacity: 0.8; font-size: 12px;">
            如果您没有请求验证码，请忽略此邮件。
        </p>
    </div>
    <div class="footer">
        © 2026 AI 行业脉搏
    </div>
</body>
</html>
"""


class DummyEmailService(EmailService):
    """假邮件服务（用于开发/测试，不真实发送邮件）"""

    def __init__(self, config):
        super().__init__(config)
        logger.warning("使用假邮件服务，验证码将打印在控制台！")

    async def send_verification_code(self, email: str, code: str) -> bool:
        """假装发送验证码（打印在控制台）"""
        print(f"\n{'='*50}")
        print(f"📧 验证码发送到: {email}")
        print(f"🔑 验证码: {code}")
        print(f"⏰ 有效期: {self.code_expire_minutes} 分钟")
        print(f"{'='*50}\n")
        self.record_send(email)
        return True
