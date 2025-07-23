from django.urls import path
from .views import  CreateBookingView, CreateCheckoutSessionView

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    # path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('create-booking/', CreateBookingView.as_view(), name='create-booking'),
]