
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(email, otp):
    try:
        message = (
            f"Dear Valued User,\n\n"
            f"Thank you for choosing HomiGo. Your One-Time Password (OTP) for account registration is {otp}. "
            f"This code is valid for the next 10 minutes. Please use it to securely complete your registration process.\n\n"
            f"Should you have any questions, feel free to contact our support team \n\n"
            f"Best regards,\nThe HomiGo Team"
        )
        send_mail(
            'Your HomiGo OTP',
            message,
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