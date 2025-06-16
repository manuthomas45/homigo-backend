
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(email, otp):
    try:
        send_mail(
            'Your HomiGo OTP',
            f'Your OTP for registration is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return f"Email sent to {email}"
    except Exception as e:
        return f"Failed to send email to {email}: {str(e)}"


@shared_task
def send_password_reset_email(email, token):
    reset_url = f"http://localhost:5173/reset-password?token={token}"
    try:
        send_mail(
            subject="HomiGo Password Reset",
            message=f"Click the link to reset your password: {reset_url}\nThis link will expire in 30 minutes.",
            from_email="HomiGo <your-email@gmail.com>",
            recipient_list=[email],
            fail_silently=False,
        )
        return f"Password reset email sent to {email}"
    except Exception as e:
        return f"Failed to send password reset email to {email}: {str(e)}"