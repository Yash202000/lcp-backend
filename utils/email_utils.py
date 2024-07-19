import re

from pydantic import EmailStr

from security.settings import settings, conf
from fastapi_mail import MessageSchema, FastMail


def is_valid_email(email: str) -> bool:
    from constants.plain_constants import EMAIL_REGEX

    if re.fullmatch(EMAIL_REGEX, email):
        return True
    else:
        return False


async def send_email_to_reset_password(email: EmailStr, name: str, reset_token: str):
    message = MessageSchema(
        subject="Reset Password Mail",
        recipients=[email],  # List of recipients, as many as you can pass '
        template_body={
            "first_name": name,
            "activation_url": f"{settings.SEND_EMAIL_TO_RESET_PASSWORD}/{reset_token}"}
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="reset_password.html")


async def send_email_for_verification(email: EmailStr, email_domain: str, name: str, verification_id: str):
    message = MessageSchema(
        subject="Account Verification Mail",
        recipients=[email],  # List of recipients, as many as you can pass '
        template_body={
            "first_name": name,
            "activation_url": settings.SEND_EMAIL_FOR_VERIFICATION.format(
                email_domain=email_domain, verification_id=verification_id)
        }
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_verification.html")
