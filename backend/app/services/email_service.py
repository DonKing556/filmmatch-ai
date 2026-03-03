"""Email service using Resend for transactional emails."""

import resend

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("email")


def _init_resend() -> None:
    if settings.resend_api_key:
        resend.api_key = settings.resend_api_key


async def send_magic_link_email(email: str, token: str) -> bool:
    """Send magic link email via Resend. Returns True on success."""
    if not settings.resend_api_key:
        logger.warning("resend_not_configured", email=email)
        return False

    _init_resend()
    magic_link_url = f"{settings.frontend_url}/auth/verify?token={token}"

    try:
        resend.Emails.send(
            {
                "from": settings.resend_from_email,
                "to": [email],
                "subject": "Your FilmMatch AI login link",
                "html": _magic_link_html(magic_link_url),
            }
        )
        logger.info("magic_link_email_sent", email=email)
        return True
    except Exception as e:
        logger.error("magic_link_email_failed", email=email, error=str(e))
        return False


def _magic_link_html(magic_link_url: str) -> str:
    return f"""\
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 480px; margin: 0 auto; padding: 40px 20px;">
  <h1 style="color: #8B5CF6; font-size: 24px; margin-bottom: 8px;">FilmMatch AI</h1>
  <p style="color: #666; font-size: 14px; margin-top: 0;">Your movie night starts here</p>
  <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
  <p style="color: #333; font-size: 16px; line-height: 1.6;">
    Click the button below to sign in. This link expires in {settings.magic_link_expire_minutes} minutes.
  </p>
  <a href="{magic_link_url}"
     style="display: inline-block; background: linear-gradient(135deg, #8B5CF6, #06B6D4);
            color: white; text-decoration: none; padding: 14px 36px;
            border-radius: 8px; font-weight: 600; font-size: 16px; margin: 24px 0;">
    Sign In to FilmMatch
  </a>
  <p style="color: #999; font-size: 13px; line-height: 1.5; margin-top: 32px;">
    If you didn't request this link, you can safely ignore this email.
  </p>
  <p style="color: #ccc; font-size: 11px; margin-top: 24px;">
    Can't click the button? Copy this link:<br />
    <a href="{magic_link_url}" style="color: #8B5CF6; word-break: break-all;">{magic_link_url}</a>
  </p>
</div>"""
