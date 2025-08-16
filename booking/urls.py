from django.urls import path
from .views import  *

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    # path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('create-booking/', CreateBookingView.as_view(), name='create-booking'),
    path('user/', UserBookingsView.as_view(), name='user-bookings'),
    path('<int:pk>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('complaints/', SubmitComplaintView.as_view(), name='submit-complaint'),
]


