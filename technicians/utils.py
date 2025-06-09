from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from django.conf import settings
from .models import TechnicianToken

def generate_tokens_for_technician(technician):
    refresh = RefreshToken()
    refresh['technician_id'] = technician.id
    refresh['user_type'] = 'technician'

    access = refresh.access_token

    access_expiry = datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    refresh_expiry = datetime.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

    TechnicianToken.objects.filter(technician=technician).delete()

    TechnicianToken.objects.create(
        technician=technician,
        access_token=str(access),
        refresh_token=str(refresh),
        access_token_expires_at=access_expiry,
        refresh_token_expires_at=refresh_expiry,
    )

    return {
        'access': str(access),
        'refresh': str(refresh),
    }